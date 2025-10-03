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

"""Contains utilities to scan for Data Store's output resources."""
from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import URL
from spine_engine.project_item.project_item_resource import ProjectItemResource, database_resource
from spine_items.utils import database_label

if TYPE_CHECKING:
    from spine_items.data_store.data_store import DataStore
    from spine_items.data_store.executable_item import ExecutableItem


def scan_for_resources(provider: DataStore | ExecutableItem, url: URL) -> list[ProjectItemResource]:
    """
    Creates db resources based on DS url.

    Args:
        provider: resource provider item
        url: sqlalchemy url

    Returns:
        output resources
    """
    if not url:
        return []
    return [
        database_resource(
            provider.name,
            url.render_as_string(hide_password=False),
            label=database_label(provider.name),
            filterable=True,
        )
    ]
