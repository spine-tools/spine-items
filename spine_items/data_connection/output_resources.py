######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################
"""
Contains utilities to scan for Data Connection's output resources.

"""
from pathlib import Path
from spine_engine.project_item.project_item_resource import file_resource, transient_file_resource, url_resource
from spine_engine.utils.serialization import path_in_dir
from ..utils import unsplit_url_credentials


def scan_for_resources(provider, file_paths, urls, url_credentials, project_dir):
    """
    Creates file and URL resources based on DC's references and data.

    Args:
        provider (ProjectItem or ExecutableItem): resource provider item
        file_paths (list of str): file paths
        urls (list of str): urls
        url_credentials (dict): mapping url from urls to tuple (username, password)
        project_dir (str): absolute path to project directory

    Returns:
        list of ProjectItemResource: output resources
    """
    resources = list()
    for fp in file_paths:
        try:
            if path_in_dir(fp, provider.data_dir):
                resource = file_resource(
                    provider.name, fp, label=f"<{provider.name}>/" + Path(fp).relative_to(provider.data_dir).as_posix()
                )
            elif path_in_dir(fp, project_dir):
                path = Path(fp)
                label = "<project>/" + Path(fp).relative_to(project_dir).as_posix()
                if path.exists():
                    resource = file_resource(provider.name, fp, label=label)
                else:
                    resource = transient_file_resource(provider.name, label)
            else:
                if Path(fp).exists():
                    resource = file_resource(provider.name, fp)
                else:
                    resource = transient_file_resource(provider.name, fp)
        except PermissionError:
            continue
        resources.append(resource)
    for url in urls:
        credentials = url_credentials.get(url)
        full_url = unsplit_url_credentials(url, credentials) if credentials is not None else url
        resource = url_resource(provider.name, full_url, f"<{provider.name}>" + url)
        resources.append(resource)
    return resources
