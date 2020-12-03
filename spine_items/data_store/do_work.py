######################################################################################################################
# Copyright (C) 2017-2020 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Combiner's execute kernel (do_work), as target for a multiprocess.Process

:authors: M. Marin (KTH)
:date:   6.11.2020
"""
import os
from spine_engine.utils.helpers import create_log_file_timestamp
from spinedb_api import (
    clear_filter_configs,
    export_data,
    import_data,
    SpineDBAPIError,
    SpineDBVersionError,
    DatabaseMapping,
)


def _get_db_map(url, logger):
    try:
        db_map = DatabaseMapping(url)
    except (SpineDBAPIError, SpineDBVersionError) as err:
        logger.msg_error.emit(f"Skipping url <b>{url}</b>: {err}")
        logger.msg_error.emit(f"Skipping url <b>{clear_filter_configs(url)}</b>: {err}")
        return None
    return db_map


def do_work(cancel_on_error, logs_dir, from_urls, to_url, logger):
    from_db_maps = [db_map for db_map in (_get_db_map(url, logger) for url in from_urls) if db_map]
    to_db_map = _get_db_map(to_url, logger)
    from_db_map_data = {from_db_map: export_data(from_db_map) for from_db_map in from_db_maps}
    all_errors = []
    for from_db_map, data in from_db_map_data.items():
        import_count, import_errors = import_data(to_db_map, **data)
        all_errors += import_errors
        if import_errors and cancel_on_error and to_db_map.has_pending_changes():
            to_db_map.rollback_session()
            continue
        if import_count:
            to_db_map.commit_session(f"Import {import_count} items from {from_db_map.db_url}")
            logger.msg_success.emit(
                "Merged {0} items with {1} errors from {2} into {3}".format(
                    import_count, len(import_errors), from_db_map.db_url, to_db_map.db_url
                )
            )
    for db_map in from_db_maps + [to_db_map]:
        db_map.connection.close()
    if all_errors:
        # Log errors in a time stamped file into the logs directory
        timestamp = create_log_file_timestamp()
        logfilepath = os.path.abspath(os.path.join(logs_dir, timestamp + "_error.log"))
        with open(logfilepath, "w") as f:
            for err in all_errors:
                f.write("{0}\n".format(err))
        # Make error log file anchor with path as tooltip
        logfile_anchor = f"<a style='color:#BB99FF;' title='{logfilepath}' href='file:///{logfilepath}'>error log</a>"
        logger.msg_error.emit("Import errors. Logfile: {0}".format(logfile_anchor))
