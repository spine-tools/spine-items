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
Utility functions for the Tool project item.

:author: A. Soininen (VTT)
:date:   1.4.2020
"""
import glob
import os.path
import subprocess
import json
from spine_engine.config import JULIA_EXECUTABLE
from jupyter_client.kernelspec import find_kernel_specs


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
    for resource in resources:
        if resource.hasfilepath:
            file_paths += glob.glob(resource.path)
        elif resource.type_ == "transient_file":
            file_paths.append(resource.metadata["label"])
    return file_paths


def find_file(filename, resources):
    """
    Returns all occurrences of full paths to given file name in resources available.

    Args:
        filename (str): Searched file name (no path)
        resources (list): list of resources available from upstream items

    Returns:
        list: Full paths to file if found, None if not found
    """
    found_file_paths = list()
    for file_path in file_paths_from_resources(resources):
        _, file_candidate = os.path.split(file_path)
        if file_candidate == filename:
            found_file_paths.append(file_path)
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
    archive_dirs = os.listdir(output_dir)
    if "failed" in archive_dirs:
        archive_dirs.remove("failed")
    archive_dirs.sort(reverse=True)
    for archive in archive_dirs:
        for pattern in list(file_patterns):
            full_archive_path = os.path.join(output_dir, archive)
            full_path_pattern = os.path.join(full_archive_path, pattern)
            files_found = False
            for path in glob.glob(full_path_pattern):
                if os.path.exists(path):
                    files_found = True
                    file_list = recent_output_files.setdefault(pattern, list())
                    file_list.append(_LatestOutputFile.from_paths(path, full_archive_path))
            if files_found:
                file_patterns.remove(pattern)
            if not file_patterns:
                return recent_output_files
    return recent_output_files


def is_pattern(file_name):
    """Returns True if file_name is actually a file pattern."""
    return "*" in file_name or "?" in file_name


class _LatestOutputFile:
    """
    A class to hold information on a latest output file.

    Attributes:
        label (str): file label, e.g. file pattern or relative path
        path (str): absolute path to the file
    """

    def __init__(self, label, path):
        self.label = label
        self.path = path

    @staticmethod
    def from_paths(path, archive_dir):
        """Constructs a _LatestOutputFile object from an absolute path and archive directory."""
        label = os.path.relpath(path, archive_dir)
        return _LatestOutputFile(label, path)


def make_label(name):
    return "{" + name + "}"


def can_use_db_server(tool_spec):
    """Whether or not the given tool spec supports db-server url advertising as replacement of the normal db url.
    This is always True for non-julia tools, as well as for julia tools that definitely don't use SpineInterface.
    For julia tools that *might* use SpineInterface (i.e., SpineInterface is found in the project),
    we check SpineInterface version >= v"0.5.0", which is the version where we start supporting db servers.

    Args:
        tool_spec (ToolSpecification)

    Returns:
        bool
    """
    if tool_spec.tooltype != "julia":
        return True
    use_embedded_julia = tool_spec._settings.value("appSettings/useEmbeddedJulia", defaultValue="2") == "2"
    if use_embedded_julia:
        kernel_name = tool_spec._settings.value("appSettings/juliaKernel", defaultValue="")
        resource_dir = find_kernel_specs().get(kernel_name)
        if resource_dir is None:
            return True
        filepath = os.path.join(resource_dir, "kernel.json")
        with open(filepath, "r") as fh:
            try:
                kernel_spec = json.load(fh)
            except json.decoder.JSONDecodeError:
                return True
            julia = kernel_spec["argv"][0]
            option = "--project="
            project = next((arg for arg in kernel_spec["argv"] if arg.startswith(option)), None)
            if project is None:
                return True
            project = project[len(option) :]
    else:
        julia = tool_spec._settings.value("appSettings/juliaPath", defaultValue="")
        if julia == "":
            julia = JULIA_EXECUTABLE
        project = tool_spec._settings.value("appSettings/juliaProjectPath", defaultValue="")
    try:
        p = subprocess.run(
            [
                julia,
                f"--project={project}",
                "-e",
                'import Pkg;'
                'pkgs = Pkg.TOML.parsefile(joinpath(dirname(Base.active_project()), "Manifest.toml"));'
                'spine_interface = get(pkgs, "SpineInterface", nothing);'
                'if spine_interface == nothing println(true) '  # SpineInterface not found
                'else println(VersionNumber(spine_interface[1]["version"]) >= v"0.5.0") '
                'end',
            ],
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return True
    return str(p.stdout, "utf-8").strip() == "true"
