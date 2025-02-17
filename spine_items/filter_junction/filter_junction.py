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
from spinetoolbox.project_item.project_item import ProjectItem
from .item_info import ItemInfo


class FilterJunction(ProjectItem):
    def __init__(self, name, description, x, y, project):
        super().__init__(name, description, x, y, project)
        self._toolbox = project.toolbox()
        self._upstream_resources = []

    @staticmethod
    def item_type():
        """See base class."""
        return ItemInfo.item_type()

    def resources_for_direct_successors(self):
        """See base class"""
        return self._upstream_resources

    def upstream_resources_updated(self, resources):
        """See base class."""
        self._upstream_resources = [
            resource.clone_with_new_provider(self.name, filterable=False) for resource in resources
        ]
        self._resources_to_successors_changed()

    def replace_resources_from_upstream(self, old, new):
        """See base class."""
        for old_resource, new_resource in zip(old, new):
            for i, resource in self._upstream_resources:
                if resource == old_resource:
                    self._upstream_resources[i] = new_resource.clone_with_new_provider(self.name, filterable=False)
                    break
        self._resources_to_successors_changed()

    def notify_destination(self, source_item):
        """See base class."""
        if source_item.item_type() in {"Data Connection", "Data Store", "Data Transformer", "Exporter", "Tool"}:
            self._logger.msg.emit(
                f"Link established. Data from <b>{source_item.name}</b> will be provided to "
                f"downstream items from <b>{self.name}</b>."
            )
        else:
            super().notify_destination(source_item)

    @staticmethod
    def from_dict(name, item_dict, toolbox, project):
        """See base class."""
        description, x, y = ProjectItem.parse_item_dict(item_dict)
        return FilterJunction(name, description, x, y, project)
