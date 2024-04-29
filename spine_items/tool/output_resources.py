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

"""Contains utilities to scan for Tool's output resources."""
from spine_engine.project_item.project_item_resource import (
    file_resource,
    file_resource_in_pack,
    transient_file_resource,
)
from .utils import find_last_output_files, is_pattern


def scan_for_resources(provider, tool_specification, output_dir):
    """
    Returns a list of resources, i.e. the output files produced by the tool.

    For each pattern or path in the tool specification's output files list, we try and find matches
    in the results directory.

    If no match, we advertise a resource with an empty url, where the label contains the non-found
    pattern or path.

    Args:
        provider (ProjectItem or ExecutableItem): resource provider item
        tool_specification (ToolSpecification): spec
        output_dir (str): path to tool's output folder

    Returns:
        list: a list of Tool's output resources
    """
    resources = []
    if tool_specification is None:
        return []
    last_output_files = find_last_output_files(tool_specification.outputfiles, output_dir)
    for out_file_label in tool_specification.outputfiles:
        latest_files = last_output_files.get(out_file_label, list())
        make_resource = file_resource if not is_pattern(out_file_label) else file_resource_in_pack
        for out_file in latest_files:
            resources.append(make_resource(provider.name, file_path=out_file, label=out_file_label))
        if not latest_files:
            make_resource = transient_file_resource if not is_pattern(out_file_label) else file_resource_in_pack
            resources.append(make_resource(provider.name, label=out_file_label))
    return resources
