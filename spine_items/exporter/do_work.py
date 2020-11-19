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
Exporter's execute kernel (do_work), as target for a multiprocess.Process

:authors: M. Marin (KTH)
:date:   6.11.2020
"""
import os
from spine_engine.spine_io.exporters import gdx
from spinedb_api import SpineDBAPIError
from .db_utils import scenario_filtered_database_map


def do_work(settings_pack, cancel_on_error, data_dir, gams_system_directory, databases, logger):
    successes = list()
    for database in databases:
        url = database.url
        out_path = os.path.join(data_dir, database.output_file_name)
        try:
            database_map = scenario_filtered_database_map(url, database.scenario)
        except SpineDBAPIError as error:
            logger.msg_error.emit(f"Failed to export <b>{url}</b> to .gdx: {error}")
            successes.append(False)
            continue
        export_logger = logger if not cancel_on_error else None
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
        finally:
            database_map.connection.close()
        logger.msg_success.emit(f"File <b>{out_path}</b> written")
        successes.append(True)
    return all(successes)
