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

"""Merger's execute kernel (do_work), as target for a multiprocess.Process"""
import os
from spine_engine.utils.helpers import create_log_file_timestamp
from spinedb_api.helpers import remove_credentials_from_url
from spinedb_api.spine_db_client import SpineDBClient


def do_work(process, cancel_on_error, logs_dir, from_server_urls, to_server_urls, lock, logger):
    from_clients = [SpineDBClient.from_server_url(server_url) for server_url in from_server_urls]
    from_url_export_data_response = [
        (from_client.get_db_url(), from_client.export_data()) for from_client in from_clients
    ]
    from_url_data = [
        (url, response["result"]) for url, response in from_url_export_data_response if response.get("result")
    ]
    all_errors = [response["error"] for _, response in from_url_export_data_response if "error" in response]
    for server_url in to_server_urls:
        to_client = SpineDBClient.from_server_url(server_url)
        with process.maybe_idle:
            to_client.db_checkin()
        for from_url, data in from_url_data:
            lock.acquire()
            try:
                response = to_client.import_data(data, "")
                if "error" in response:
                    all_errors.append(response["error"])
                    continue
                import_count, import_errors = response["result"]
                all_errors += import_errors
                if import_errors and cancel_on_error and import_count:
                    to_client.call_method("rollback_session")
                else:
                    sanitized_from_url = remove_credentials_from_url(from_url)
                    sanitized_to_url = remove_credentials_from_url(to_client.get_db_url())
                    if data:
                        result = to_client.call_method(
                            "commit_session", f"Import {import_count} items from {sanitized_from_url}"
                        )
                        if "error" in result:
                            all_errors.append(result["error"])
                        else:
                            logger.msg_success.emit(
                                f"Merged {import_count} items with {len(import_errors)} errors "
                                f"from {sanitized_from_url} into {sanitized_to_url}"
                            )
                    else:
                        logger.msg_warning.emit(f"No new data merged from {sanitized_from_url} into {sanitized_to_url}")
            finally:
                lock.release()
        to_client.db_checkout()
    if all_errors:
        # Log errors in a time stamped file into the logs directory
        timestamp = create_log_file_timestamp()
        logfilepath = os.path.abspath(os.path.join(logs_dir, timestamp + "_error.log"))
        with open(logfilepath, "w") as f:
            for err in all_errors:
                f.write(f"{err}\n")
        # Make error log file anchor with path as tooltip
        logfile_anchor = f"<a style='color:#BB99FF;' title='{logfilepath}' href='file:///{logfilepath}'>error log</a>"
        logger.msg_error.emit(f"Import errors. Logfile: {logfile_anchor}")
    return (True,)
