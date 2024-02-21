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

"""Contains utilities to manage export manifest files."""
import json
from itertools import dropwhile
from pathlib import Path
from spine_engine.project_item.project_item_resource import file_resource_in_pack, transient_file_resource
from .specification import OutputFormat
from .utils import EXPORTER_EXECUTION_MANIFEST_FILE_PREFIX


def exported_files_as_resources(item_name, exported_files, data_dir, output_channels, output_format):
    """Collects exported files from 'export manifests'.

    Args:
        item_name (str): item's name
        exported_files (dict, optional): item's exported files cache
        data_dir (str): item's data directory
        output_channels (Iterable of OutputChannel): item's output channels
        output_format (OutputFormat, optional): output format

    Returns:
        tuple: output resources and updated exported files cache
    """
    manifests = _collect_execution_manifests(data_dir)
    if output_format == OutputFormat.SQL:
        output_channels = tuple(c for c in output_channels if c.out_url is None)
    if manifests is not None:
        out_labels = {c.out_label for c in output_channels}
        manifests = {
            label: files for label, files in _collect_execution_manifests(data_dir).items() if label in out_labels
        }
        exported_files = {label: [str(Path(data_dir, f)) for f in files] for label, files in manifests.items()}
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


def _collect_execution_manifests(data_dir):
    """Collects output file names from export manifest files written by exporter's executable item.

    Args:
        data_dir (str): item's data directory

    Returns:
        dict: mapping from output label to list of file paths, or None if no manifest files were found
    """
    manifests = None
    for path in Path(data_dir).iterdir():
        if path.name.startswith(EXPORTER_EXECUTION_MANIFEST_FILE_PREFIX) and path.suffix == ".json":
            with open(path) as manifest_file:
                manifest = json.load(manifest_file)
            for out_file_name, paths in manifest.items():
                relative_paths = list()
                for file_path in paths:
                    p = Path(file_path)
                    if p.is_absolute():
                        # Legacy manifests had absolute paths
                        try:
                            relative_paths.append(p.relative_to(data_dir))
                        except ValueError:
                            # Project may have been moved to another directory (or system)
                            # so data_dir is differs from manifest file content.
                            # Try resolving the relative path manually.
                            parts = tuple(dropwhile(lambda part: part != "output", p.parts))
                            relative_paths.append(str(Path(*parts)))
                    else:
                        relative_paths.append(file_path)
                if manifests is None:
                    manifests = dict()
                manifests.setdefault(out_file_name, list()).extend(paths)
    return manifests
