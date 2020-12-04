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
GdxExporter's execute kernel (do_work), as target for a multiprocess.Process

:authors: M. Marin (KTH)
:date:   6.11.2020
"""
from datetime import datetime
import os
from time import time
from spine_engine.spine_io.exporters import gdx
from spinedb_api import DatabaseMapping, SpineDBAPIError
from spinedb_api.filters.url_tools import ensure_filtering, filter_configs
from spinedb_api.filters.filter_stacks import load_filters
from spinedb_api.filters.scenario_filter import scenario_name_from_dict


def do_work(settings_pack, output_time_stamps, cancel_on_error, data_dir, gams_system_directory, databases, logger):
    successes = list()
    for url, output_file_name in databases.items():
        configs = load_filters(filter_configs(url))
        out_paths = _out_file_paths(output_file_name, data_dir, output_time_stamps, configs)
        try:
            database_map = DatabaseMapping(ensure_filtering(url, fallback_alternative="Base"))
        except SpineDBAPIError as error:
            logger.msg_error.emit(f"Failed to export <b>{url}</b> to .gdx: {error}")
            successes.append(False)
            continue
        export_logger = logger if not cancel_on_error else None
        for out_path in out_paths:
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
            finally:
                database_map.connection.close()
            logger.msg_success.emit(f"File <b>{out_path}</b> written")
            successes.append(True)
    return all(successes)


def _out_file_paths(output_file_name, data_dir, output_time_stamps, filters):
    """
    Creates output file paths.

    Args:
        output_file_name (str): file name
        data_dir (str): exporter's data directory
        filters (list): database filter stack

    Returns:
        list: list of absolute paths
    """
    out_paths = list()
    have_scenarios = False
    if output_time_stamps:
        stamp = datetime.fromtimestamp(time())
        time_stamp = "run@" + stamp.isoformat(timespec="seconds").replace(":", ".")
    else:
        time_stamp = ""
    for config in filters:
        scenario = scenario_name_from_dict(config)
        if scenario is not None:
            if time_stamp:
                path = os.path.join(data_dir, scenario + "_" + time_stamp, output_file_name)
            else:
                path = os.path.join(data_dir, scenario, output_file_name)
            out_paths.append(path)
            have_scenarios = True
    if not have_scenarios:
        out_paths.append(os.path.join(data_dir, time_stamp, output_file_name))
    return out_paths
