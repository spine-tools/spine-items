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

"""Contains utilities to scan for Data Transformer's output resources."""
from spine_engine.project_item.project_item_resource import database_resource
from spinedb_api import append_filter_config
from spinedb_api.filters.tools import store_filter
from spine_items.utils import database_label


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
    label = database_label(provider.name)
    if dt_specification is None or dt_specification.settings is None:
        return [database_resource(provider.name, r.url, label=label) for r in db_resources]
    if dt_specification.settings.use_shorthand():
        config = dt_specification.settings.filter_config()
        return [
            database_resource(provider.name, append_filter_config(r.url, config), label=label) for r in db_resources
        ]
    with open(filter_config_path, "w") as filter_config_file:
        store_filter(dt_specification.settings.filter_config(), filter_config_file)
    return [
        database_resource(provider.name, append_filter_config(r.url, filter_config_path), label=label)
        for r in db_resources
    ]
