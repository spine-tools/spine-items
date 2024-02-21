######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# Copyright Spine Items contributors
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""Importer's execute kernel (do_work), as target for a multiprocess.Process"""
import os
from spine_engine.project_item.project_item_resource import get_source, get_source_extras
from spinedb_api import clear_filter_configs, InvalidMapping
from spinedb_api.helpers import remove_credentials_from_url
from spinedb_api.spine_db_client import SpineDBClient
from spinedb_api.parameter_value import to_database
from spinedb_api.import_mapping.type_conversion import value_to_convert_spec
from spine_engine.utils.helpers import create_log_file_timestamp


def do_work(
    process, mapping, cancel_on_error, on_conflict, logs_dir, source_resources, connector, to_server_urls, lock, logger
):
    all_data = []
    all_errors = []
    table_mappings = {
        name: mappings
        for name, mappings in mapping.get("table_mappings", {}).items()
        if name in mapping["selected_tables"]
    }
    table_options = {
        name: options
        for name, options in mapping.get("table_options", {}).items()
        if name in mapping["selected_tables"]
    }
    table_column_convert_specs = {
        tn: {int(col): value_to_convert_spec(spec) for col, spec in cols.items()}
        for tn, cols in mapping.get("table_types", {}).items()
    }
    table_default_column_convert_fns = {
        tn: value_to_convert_spec(spec) for tn, spec in mapping.get("table_default_column_type", {}).items()
    }
    table_row_convert_specs = {
        tn: {int(col): value_to_convert_spec(spec) for col, spec in cols.items()}
        for tn, cols in mapping.get("table_row_types", {}).items()
    }
    to_clients = [SpineDBClient.from_server_url(server_url) for server_url in to_server_urls]
    for resource in source_resources:
        src = get_source(resource)
        if resource.hasfilepath:
            source_anchor = f"<a style='color:#BB99FF;' title='{src}' href='file:///{src}'>{os.path.basename(src)}</a>"
        else:
            safe_url = remove_credentials_from_url(src)
            source_anchor = f"<p style='color:#BB99FF;'>{safe_url}</p>"
        logger.msg.emit("Importing " + source_anchor)
        extras = get_source_extras(resource)
        try:
            connector.connect_to_source(src, **extras)
        except Exception as error:  # pylint: disable=broad-except
            logger.msg_error.emit(f"Failed to connect to {source_anchor}: {error}")
            return (False,)
        for name, mappings in table_mappings.items():
            logger.msg.emit(f"Processing table <b>{name}</b>")
            for spec in mappings:
                mapping_name = next(iter(spec.keys()))
                logger.msg.emit(f"* Applying mapping <b>{mapping_name}</b>...")
                try:
                    data, errors = connector.get_mapped_data(
                        {name: [spec]},
                        table_options,
                        table_column_convert_specs,
                        table_default_column_convert_fns,
                        table_row_convert_specs,
                        unparse_value=to_database,
                    )
                except InvalidMapping as error:
                    logger.msg_error.emit(f"Failed to import: {error}")
                    if cancel_on_error:
                        logger.msg_error.emit("Cancel import on error has been set. Bailing out.")
                        return (False,)
                    logger.msg_warning.emit("Ignoring errors. Set Cancel import on error to bail out instead.")
                    continue
                if not errors:
                    logger.msg.emit(f"Successful ({sum(len(d) for d in data.values())} data to be written).")
                else:
                    logger.msg_warning.emit(
                        f"Read {sum(len(d) for d in data.values())} data with {len(errors)} errors."
                    )
                all_data.append(data)
                all_errors.extend(errors)
        connector.disconnect()
        if all_data:
            for client in to_clients:
                lock.acquire()
                try:
                    with process.maybe_idle:
                        client.db_checkin()
                    success = _import_data_to_url(cancel_on_error, on_conflict, logs_dir, all_data, client, logger)
                    client.db_checkout()
                    if not success and cancel_on_error:
                        return (False,)
                finally:
                    lock.release()
            all_data.clear()
    if all_errors:
        # Log errors in a time stamped file into the logs directory
        timestamp = create_log_file_timestamp()
        logfilepath = os.path.abspath(os.path.join(logs_dir, timestamp + "_read_error.log"))
        with open(logfilepath, "w") as f:
            for err in all_errors:
                f.write(f"{err}\n")
        # Make error log file anchor with path as tooltip
        logfile_anchor = (
            "<a style='color:#BB99FF;' title='" + logfilepath + "' href='file:///" + logfilepath + "'>Error log</a>"
        )
        logger.msg_error.emit(logfile_anchor)
        if cancel_on_error:
            logger.msg_error.emit("Cancel import on error has been set. Bailing out.")
            return (False,)
        logger.msg_warning.emit("Ignoring errors. Set Cancel import on error to bail out instead.")
    return (True,)


def _import_data_to_url(cancel_on_error, on_conflict, logs_dir, all_data, client, logger):
    all_import_errors = []
    all_import_count = 0
    for data in all_data:
        response = client.import_data({**data, "on_conflict": on_conflict}, "")
        if "error" in response:
            all_import_errors.append(response["error"])
            continue
        import_count, import_errors = response["result"]
        all_import_count += import_count
        all_import_errors += import_errors
        if import_errors:
            logger.msg_error.emit("Errors while importing a table.")
            if cancel_on_error:
                logger.msg_error.emit("Cancel import on error is set. Bailing out.")
                if all_import_count > 0:
                    logger.msg_error.emit("Rolling back changes.")
                    client.call_method("rollback_session")
                    all_import_count = 0
                break
            logger.msg_warning.emit("Ignoring errors. Set Cancel import on error to bail out instead.")
    if all_import_count > 0:
        client.call_method("commit_session", "Import data by Spine Toolbox Importer")
        clean_url = clear_filter_configs(remove_credentials_from_url(client.get_db_url()))
        logger.msg_success.emit(
            f"Inserted {all_import_count} data with {len(all_import_errors)} errors into {clean_url}"
        )
    else:
        logger.msg_warning.emit("No new data imported")
    if all_import_errors:
        # Log errors in a time stamped file into the logs directory
        timestamp = create_log_file_timestamp()
        logfilepath = os.path.abspath(os.path.join(logs_dir, timestamp + "_import_error.log"))
        with open(logfilepath, "w") as f:
            for err in all_import_errors:
                f.write(str(err) + "\n")
        # Make error log file anchor with path as tooltip
        logfile_anchor = (
            "<a style='color:#BB99FF;' title='" + logfilepath + "' href='file:///" + logfilepath + "'>Error log</a>"
        )
        logger.msg_error.emit(logfile_anchor)
        return False
    return True
