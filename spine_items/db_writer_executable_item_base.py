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

"""Contains base classes for items that write to db."""
from spine_engine.project_item.executable_item_base import ExecutableItemBase
from spinedb_api.spine_db_client import SpineDBClient


class DBWriterExecutableItemBase(ExecutableItemBase):
    """Base class for items that might write to a Spine DB."""

    def exclude_execution(self, forward_resources, backward_resources, lock):
        """Perform the checkout on output databases so concurrent items can proceed."""
        to_resources = [r for r in backward_resources if r.type_ == "database"]
        for resource in to_resources:
            resource.quick_db_checkout()

    def update(self, forward_resources, backward_resources):
        if not super().update(forward_resources, backward_resources):
            return False
        to_resources = [r for r in backward_resources if r.type_ == "database"]
        for resource in to_resources:
            with resource.open() as server_url:
                SpineDBClient.from_server_url(server_url).cancel_db_checkout()
        return True
