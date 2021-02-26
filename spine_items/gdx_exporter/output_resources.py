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
Contains utilities to scan for GdxExporter's output resources.

:authors: A. Soininen (VTT)
:date:    4.12.2020
"""
import pathlib
from spine_engine.project_item.project_item_resource import transient_file_resource


def scan_for_resources(provider, databases, directory, forks):
    """
    Creates transient file resources based on databases and which files can be found on disk.

    Args:
        provider (ProjectItem or ExecutableItem): resource provider item
        databases (list of Database): exporter's databases
        directory (str): directory to scan for files
        forks (dict): mapping from full URL to set of scenario or tool names

    Returns:
        list of ProjectItemResource: output resources
    """
    resources = list()
    directory = pathlib.Path(directory)
    files = _scan_files(directory)
    for db in databases:
        file_forks = files.get(db.output_file_name)
        for fork in forks.get(db.url, list()):
            path = file_forks.get(fork)
            if path is not None:
                resources.append(transient_file_resource(provider.name, file_path=path))
    return resources


def _scan_files(directory, is_root=True, scanned_files=None):
    """
    Recursively scans a directory for output files.

    Args:
        directory (pathlib.Path): a directory to scan
        is_root (bool): if True, treat ``directory`` as the project item's data directory
        scanned_files (dict, optional): already scanned files

    Returns:
        dict: a mapping from file name to a mapping from fork name to file's full path
    """
    if scanned_files is None:
        scanned_files = dict()
    if not is_root:
        fork, _, stamp = directory.name.partition("run@")
        if fork and stamp:
            # Remove extra underscore between fork name and '@run'.
            fork = fork[:-1]
        elif not fork:
            # We have only time stamp, no fork.
            fork = None
    else:
        fork = None
    for path in directory.iterdir():
        if path.is_dir():
            _scan_files(path, False, scanned_files)
        else:
            existing = scanned_files.setdefault(path.name, dict()).get(fork)
            if existing is None or path.stat().st_mtime_ns > existing.stat().st_mtime_ns:
                scanned_files[path.name][fork] = path
    return scanned_files
