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
from spine_engine.project_item.project_item_resource import database_resource
from spine_items.utils import database_label


def scan_for_resources(provider, url):
    """
    Creates db resources based on DS url.

    Args:
        provider (ProjectItem or ExecutableItem): resource provider item
        url (URL): sqlalchemy url

    Returns:
        list of ProjectItemResource: output resources
    """
    if not url:
        return list()
    return [database_resource(provider.name, str(url), label=database_label(provider.name), filterable=True)]
