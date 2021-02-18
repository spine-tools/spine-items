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
Contains utilities to scan for Tool's output resources.

:authors: A. Soininen (VTT)
:date:    4.12.2020
"""

import pathlib
from spine_engine.project_item.project_item_resource import ProjectItemResource
from .utils import make_label, find_last_output_files, is_pattern


def scan_for_resources(provider, notebook_specification, output_dir, include_missing):
    """
    Returns a list of resources, i.e. the output files produced by the tool.

    For each pattern or path in the tool specification's output files list, we try and find matches
    in the results directory. For each match, we advertise a resource of type 'transient_file',
    meaning that this file only became available after execution.

    If no match, we advertise a resource with an empty url, where the 'label' key of the metadata
    contains the non-found pattern or path. The type of this resource is either 'file_pattern'
    or 'transient_file', depending on whether we were searching for a pattern or a path.

    Args:
        provider (ProjectItem or ExecutableItem): resource provider item
        notebook_specification (NotebookExecutorSpecification): a notebook specification
        output_dir (str): path to tool's output folder
        include_missing (bool): if True, include output files that have not yet been generated

    Returns:
        list: a list of Tool's output resources
    """
    resources = []
    if notebook_specification is None:
        return []
    last_output_files = find_last_output_files(notebook_specification.output_files, output_dir)
    for out_file_label in notebook_specification.output_files:
        latest_files = last_output_files.get(out_file_label, list())
        for out_file in latest_files:
            file_url = pathlib.Path(out_file.path).as_uri()
            metadata = {"label": make_label(out_file.label)}
            resource = ProjectItemResource(provider, "transient_file", url=file_url, metadata=metadata)
            resources.append(resource)
        if not latest_files and include_missing:
            metadata = {"label": make_label(out_file_label)}
            type_ = "file_pattern" if is_pattern(out_file_label) else "transient_file"
            resource = ProjectItemResource(provider, type_, metadata=metadata)
            resources.append(resource)
    return resources
