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
Contains utilities for all items.

:authors: A. Soininen (VTT)
:date:   1.4.2020
"""

from contextlib import contextmanager
from spinedb_api.spine_db_server import start_spine_db_server, shutdown_spine_db_server


def labelled_resource_filepaths(resources):
    """Returns a dict mapping resource labels to filepaths available in given resources.
    The label acts as an identifier for a 'transient_file'.
    """
    return {resource.label: resource.path for resource in resources if resource.hasfilepath}


@contextmanager
def labelled_resource_args(resources, use_db_server=False):
    result = {}
    server_urls = []
    for resource in resources:
        if resource.type_ != "database":
            result[resource.label] = resource.path
            continue
        if use_db_server:
            server_url = result[resource.label] = start_spine_db_server(resource.url)
            server_urls.append(server_url)
            continue
        result[resource.label] = resource.url
    try:
        yield result
    finally:
        for server_url in server_urls:
            shutdown_spine_db_server(server_url)


def is_label(label):
    return label[0] == "{" and label[-1] == "}"
