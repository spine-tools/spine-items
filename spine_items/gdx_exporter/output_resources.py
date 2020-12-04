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
Contains utilities to scan for GdxExporter's output resources.

:authors: A. Soininen (VTT)
:date:    4.12.2020
"""
import pathlib
from spine_engine.project_item.project_item_resource import ProjectItemResource


def scan_for_resources(provider, databases, directory, include_missing):
    """
    Creates transient file resources based on databases and which files can be found on disk.

    Args:
        provider (ProjectItem or ExecutableItem): resource provider item
        databases (list of Database): exporter's databases
        directory (str): directory to scan for files
        include_missing (bool): if True, include output files that have not yet been generated

    Returns:
        list of ProjectItemResource: output resources
    """
    resources = list()
    directory = pathlib.Path(directory)
    files = _scan_files(directory)
    for db in databases:
        path = files.get(db.output_file_name)
        if path is None and include_missing:
            resources.append(ProjectItemResource(provider, "transient_file", "", {"label": db.output_file_name}))
        elif path is not None:
            resources.append(
                ProjectItemResource(provider, "transient_file", path.as_uri(), {"label": db.output_file_name})
            )
    return resources


def _scan_files(directory, scanned_files=None):
    """
    Recursively scans a directory for latest versions of files.

    Args:
        directory (pathlib.Path): a directory to scan
        scanned_files (dict, optional): already scanned files

    Returns:
        dict: a mapping from file name to its full path
    """
    if scanned_files is None:
        scanned_files = dict()
    for path in directory.iterdir():
        if path.is_dir():
            _scan_files(path, scanned_files)
        else:
            existing = scanned_files.get(path.name)
            if existing is None:
                scanned_files[path.name] = path
            elif path.stat().st_mtime_ns > existing.stat().st_mtime_ns:
                scanned_files[path.name] = path
    return scanned_files
