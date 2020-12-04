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

import json
from spine_engine.project_item.project_item_resource import ProjectItemResource
from spinedb_api import append_filter_config
from .utils import make_metadata


def scan_for_resources(provider, dt_specification, db_resources, filter_config_path):
    """
    Returns a list of resources, i.e., filtered dbs produced by the Data Transformer.

    Args:
        provider (ProjectItem or ExecutableItem): resource provider item
        dt_specification (DataTransformerSpecification): spec
        db_resources (list of ProjectItemResource): db resources available to the DT
        filter_config_path (str): path to filter config file

    Returns:
        list: a list of output resources
    """
    url_metadata = [(resource.url, make_metadata(resource, provider.name)) for resource in db_resources]
    if dt_specification is None or dt_specification.settings is None:
        return [ProjectItemResource(provider, "database", url, metadata=metadata) for url, metadata in url_metadata]
    if dt_specification.settings.use_shorthand():
        config = dt_specification.settings.filter_config()
        return [
            ProjectItemResource(provider, "database", append_filter_config(url, config), metadata=metadata)
            for url, metadata in url_metadata
        ]
    with open(filter_config_path, "w") as filter_config_file:
        json.dump(dt_specification.settings.filter_config(), filter_config_file)
    return [
        ProjectItemResource(provider, "database", append_filter_config(url, filter_config_path), metadata=metadata)
        for url, metadata in url_metadata()
    ]
