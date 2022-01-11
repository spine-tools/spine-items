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
Contains utilities to manage export manifest files.

:authors: A. Soininen (VTT)
:date:    5.1.2022
"""
from pathlib import Path
from spine_engine.project_item.project_item_resource import file_resource_in_pack, transient_file_resource
from spine_items.utils import (
    EXPORTED_PATHS_FILE_NAME,
    collect_execution_manifests,
    write_exported_files_file,
    read_exported_files_file,
)


def exported_files_as_resources(item_name, exported_files, data_dir, output_channels):
    """Collects exported files from 'export manifests'.

    Args:
        item_name (str): item's name
        exported_files (dict, optional): item's exported files cache
        data_dir (str): item's data directory
        output_channels (Iterable of OutputChannel): item's output channels

    Returns:
        tuple: output resources and updated exported files cache
    """
    manifests = collect_execution_manifests(data_dir)
    exported_file_path = Path(data_dir, EXPORTED_PATHS_FILE_NAME)
    if manifests is not None:
        write_exported_files_file(exported_file_path, manifests, data_dir)
        exported_files = manifests
    elif exported_files is None and exported_file_path.exists():
        exported_files = read_exported_files_file(exported_file_path, data_dir)
    resources = list()
    if exported_files is not None:
        for channel in output_channels:
            if channel.out_label:
                files = {f for f in exported_files.get(channel.out_label, []) if Path(f).exists()}
                if files:
                    resources += [file_resource_in_pack(item_name, channel.out_label, f) for f in files]
                else:
                    resources.append(transient_file_resource(item_name, channel.out_label))
    else:
        for channel in output_channels:
            if channel.out_label:
                resources.append(transient_file_resource(item_name, channel.out_label))
    return resources, exported_files
