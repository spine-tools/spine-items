######################################################################################################################
# Copyright (C) 2017-2021 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Merger's execute kernel (do_work), as target for a multiprocess.Process

:authors: M. Marin (KTH)
:date:   6.11.2020
"""
import os
from spine_engine.utils.helpers import create_log_file_timestamp, remove_credentials_from_url
from spinedb_api.spine_db_client import SpineDBClient


def do_work(cancel_on_error, logs_dir, from_server_urls, to_server_urls, logger):
    from_clients = [SpineDBClient.from_server_url(server_url) for server_url in from_server_urls]
    to_clients = [SpineDBClient.from_server_url(server_url) for server_url in to_server_urls]
    all_errors = []
    for from_client in from_clients:
        data = from_client.export_data()['result']
        for to_client in to_clients:
            to_client.open_connection()
            import_count, import_errors = to_client.import_data(data, "")['result']
            all_errors += import_errors
            if import_errors and cancel_on_error and import_count:
                to_client.call_method("rollback_session")
            else:
                sanitized_from_url = remove_credentials_from_url(from_client.get_db_url())
                sanitized_to_url = remove_credentials_from_url(to_client.get_db_url())
                if data:
                    to_client.call_method("commit_session", f"Import {import_count} items from {sanitized_from_url}")
                    logger.msg_success.emit(
                        "Merged {0} items with {1} errors from {2} into {3}".format(
                            import_count, len(import_errors), sanitized_from_url, sanitized_to_url
                        )
                    )
                else:
                    logger.msg_warning.emit(
                        "No new data merged from {0} into {1}".format(sanitized_from_url, sanitized_to_url)
                    )
            to_client.close_connection()
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
    return (True,)
