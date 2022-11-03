######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
GdxExporter's execute kernel (do_work), as target for a multiprocess.Process

:authors: M. Marin (KTH)
:date:    6.11.2020
"""
import os
from spinedb_api.spine_io.exporters import gdx
from spinedb_api import clear_filter_configs, DatabaseMapping, SpineDBAPIError
from spinedb_api.filters.tools import ensure_filtering
from spine_items.utils import subdirectory_for_fork


def do_work(
    process,
    settings_pack,
    output_time_stamps,
    cancel_on_error,
    data_dir,
    gams_system_directory,
    databases,
    forks,
    logger,
):
    successes = list()
    written_files = dict()
    for url, output_file_name in databases.items():
        out_path = subdirectory_for_fork(
            output_file_name, data_dir, output_time_stamps, forks[clear_filter_configs(url)]
        )
        try:
            database_map = DatabaseMapping(ensure_filtering(url, fallback_alternative="Base"))
        except SpineDBAPIError as error:
            logger.msg_error.emit(f"Failed to export <b>{url}</b> to .gdx: {error}")
            successes.append(False)
            continue
        try:
            export_logger = logger if not cancel_on_error else None
            try:
                os.mkdir(os.path.dirname(out_path))
            except FileExistsError:
                pass
            try:
                gdx.to_gdx_file(
                    database_map,
                    out_path,
                    settings_pack.settings,
                    settings_pack.indexing_settings,
                    settings_pack.merging_settings,
                    settings_pack.none_fallback,
                    settings_pack.none_export,
                    gams_system_directory,
                    export_logger,
                )
            except gdx.GdxExportException as error:
                logger.msg_error.emit(f"Failed to export <b>{url}</b> to .gdx: {error}")
                successes.append(False)
                continue
            written_files[output_file_name] = [out_path]
            logger.msg_success.emit(f"File <b>{out_path}</b> written")
            successes.append(True)
        finally:
            database_map.connection.close()
    return (all(successes), written_files)
