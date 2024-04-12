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

""" Utility functions for the Tool project item. """
from datetime import datetime
import glob
import os.path
from pathlib import Path
import re
import json
from jupyter_client.kernelspec import find_kernel_specs
from spine_engine.utils.helpers import resolve_julia_executable


def get_julia_path_and_project(exec_settings, settings):
    """Returns path to Julia and --project=path/to/project in a list based on Tool specs execution settings.

    Args:
        exec_settings (dict): Execution settings
        settings (AppSettings): application settings

    Returns:
        list of str: e.g. ["path/to/julia", "--project=path/to/project/"] or None if kernel does not exist.
    """
    use_jupyter_console = exec_settings["use_jupyter_console"]
    if use_jupyter_console:
        kernel_name = exec_settings["kernel_spec_name"]
        resource_dir = find_kernel_specs().get(kernel_name)
        if resource_dir is None:
            return None
        filepath = os.path.join(resource_dir, "kernel.json")
        with open(filepath, "r") as fh:
            try:
                kernel_spec = json.load(fh)
            except json.decoder.JSONDecodeError:
                return None
        julia = kernel_spec["argv"].pop(0)
        project_arg = next((arg for arg in kernel_spec["argv"] if arg.startswith("--project=")), None)
        project = "" if project_arg is None else project_arg.split("--project=")[1]
        retval = [julia]
        if project:
            retval.append(f"--project={project}")
        return retval
    julia = exec_settings["executable"]
    if not julia:
        julia = resolve_julia_executable(settings)
    project = exec_settings["project"]
    retval = [julia]
    if project:
        retval.append(f"--project={project}")
    return retval


def flatten_file_path_duplicates(file_paths, logger, log_duplicates=False):
    """Flattens the extra duplicate dimension in file_paths."""
    flattened = dict()
    for required_file, paths in file_paths.items():
        if paths is not None:
            pick = paths[0]
            if len(paths) > 1 and log_duplicates:
                logger.msg_warning.emit(f"Multiple input files satisfy {required_file}; using {pick}")
            flattened[required_file] = pick
        else:
            flattened[required_file] = None
    return flattened


def file_paths_from_resources(resources):
    """
    Returns file paths from given resources.

    Args:
        resources (list): resources available

    Returns:
        a list of file paths, possibly including patterns
    """
    file_paths = []
    glob_chars = ("*", "?", "[")
    for resource in resources:
        if resource.hasfilepath:
            path = resource.path
            if any(char in path for char in glob_chars):
                file_paths += glob.glob(path)
            else:
                file_paths.append(path)
        elif resource.type_ == "file":
            file_paths.append(resource.label)
    return file_paths


def find_file(filename, resources, one_file=None):
    """
    Returns all occurrences of full paths to given file name in resources available.

    Args:
        filename (str): Searched file name (no path)
        resources (list): list of resources available from upstream items
        one_file (bool): If True, a list containing only the first found matching file is returned

    Returns:
        list: Full paths to file if found, None if not found
    """
    filename = os.path.normcase(filename)
    found_file_paths = list()
    for file_path in file_paths_from_resources(resources):
        _, file_candidate = os.path.split(file_path)
        if os.path.normcase(file_candidate) == filename:
            found_file_paths.append(file_path)
            if one_file:
                break
    return found_file_paths if found_file_paths else None


def find_last_output_files(output_files, output_dir):
    """
    Returns latest output files.

    Args:
        output_files (list): output file patterns from tool specification
        output_dir (str): path to the execution output directory

    Returns:
        dict: a mapping from a file name pattern to the path of the most recent files in the results archive.
    """
    if not os.path.exists(output_dir):
        return dict()
    recent_output_files = dict()
    file_patterns = list(output_files)
    result = _find_last_output_dir(output_dir)
    if result is None:
        return dict()
    full_archive_path = result[1]
    for pattern in list(file_patterns):
        full_path_pattern = os.path.join(full_archive_path, pattern)
        files_found = False
        for path in glob.glob(full_path_pattern):
            if os.path.exists(path):
                files_found = True
                file_list = recent_output_files.setdefault(pattern, list())
                file_list.append(os.path.normpath(path))
        if files_found:
            file_patterns.remove(pattern)
        if not file_patterns:
            return recent_output_files
    return recent_output_files


def _find_last_output_dir(output_dir, depth=0):
    """Searches for the latest output archive directory recursively.

    Args:
        output_dir (str):  path to the execution output directory
        depth (int): current recursion depth

    Returns:
        tuple: creation datetime and directory path
    """
    latest = None
    result_directory_pattern = re.compile(r"^\d\d\d\d-\d\d-\d\dT\d\d.\d\d.\d\d")
    for path in Path(output_dir).iterdir():
        if not path.is_dir() or path.name == "failed":
            continue
        if result_directory_pattern.match(path.name) is not None:
            time_stamp = datetime.fromisoformat(path.name.replace(".", ":"))
            if latest is None:
                latest = (time_stamp, path)
            elif latest[0] < time_stamp:
                latest = (time_stamp, path)
        elif depth < 1:
            subdir_latest = _find_last_output_dir(str(path), depth + 1)
            if latest is None:
                latest = subdir_latest
            elif subdir_latest is not None and latest[0] < subdir_latest[0]:
                latest = subdir_latest
    return latest


def is_pattern(file_name):
    """Returns True if file_name is actually a file pattern."""
    return "*" in file_name or "?" in file_name


def make_dir_if_necessary(d, directory):
    """Creates a directory if given dictionary contains any items.

    Args:
        d (dict): Dictionary to check
        directory (str): Absolute path to directory that shall be created if necessary

    Returns:
        bool: True if directory was created successfully or dictionary is empty,
        False if creating the directory failed.
    """
    if len(d.items()) > 0:
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError:
            return False
    return True
