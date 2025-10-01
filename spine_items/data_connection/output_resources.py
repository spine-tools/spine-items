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

"""Contains utilities to scan for Data Connection's output resources."""
from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING
from spine_engine.project_item.project_item_resource import (
    ProjectItemResource,
    directory_resource,
    file_resource,
    transient_file_resource,
    url_resource,
)
from spine_engine.utils.serialization import path_in_dir
from spinedb_api.helpers import remove_credentials_from_url
from ..utils import convert_to_sqlalchemy_url

if TYPE_CHECKING:
    from .data_connection import DataConnection
    from .executable_item import ExecutableItem


def scan_for_resources(
    provider: DataConnection | ExecutableItem,
    file_paths: list[str],
    directories: list[str],
    urls: list[dict],
    project_dir: str,
) -> list[ProjectItemResource]:
    """
    Creates file and URL resources based on DC's references and data.

    Args:
        provider: resource provider item
        file_paths: file paths
        directories: directory paths
        urls: urls
        project_dir: absolute path to project directory

    Returns:
        output resources
    """
    resources = []
    for fp in file_paths:
        path = Path(fp)
        try:
            if path_in_dir(fp, provider.data_dir):
                resource = file_resource(
                    provider.name, fp, label=f"<{provider.name}>/" + path.relative_to(provider.data_dir).as_posix()
                )
            elif path_in_dir(fp, project_dir):
                label = "<project>/" + path.relative_to(project_dir).as_posix()
                if path.exists():
                    resource = file_resource(provider.name, fp, label=label)
                else:
                    resource = transient_file_resource(provider.name, label)
            else:
                if path.exists():
                    resource = file_resource(provider.name, fp)
                else:
                    resource = transient_file_resource(provider.name, fp)
        except PermissionError:
            continue
        resources.append(resource)
    for directory in directories:
        if path_in_dir(directory, project_dir):
            label = "<project>/" + Path(directory).relative_to(project_dir).as_posix()
            resource = directory_resource(provider.name, directory, label=label)
        else:
            resource = directory_resource(provider.name, directory)
        resources.append(resource)
    for url in urls:
        str_url = str(convert_to_sqlalchemy_url(url))
        schema = url.get("schema")
        resource = url_resource(
            provider.name, str_url, f"<{provider.name}>" + remove_credentials_from_url(str_url), schema=schema
        )
        resources.append(resource)
    return resources
