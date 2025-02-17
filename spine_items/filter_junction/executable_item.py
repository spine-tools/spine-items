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
from spine_engine import ItemExecutionFinishState
from spine_engine.project_item.executable_item_base import ExecutableItemBase
from spine_engine.project_item.project_item_resource import ProjectItemResource
from .item_info import ItemInfo


class ExecutableItem(ExecutableItemBase):
    def __init__(self, name, project_dir, logger, group_id=None):
        super().__init__(name, project_dir, logger, group_id)
        self._upstream_resources: list[ProjectItemResource] = []

    @staticmethod
    def item_type():
        """See base class."""
        return ItemInfo.item_type()

    def execute(self, forward_resources, backward_resources, lock):
        """See base class."""
        self._logger.msg.emit(f"***Gathering upstream resources in <b>{self._name}</b>***")
        self._upstream_resources = [
            resource.clone_with_new_provider(self.name, filterable=False) for resource in forward_resources
        ]
        return ItemExecutionFinishState.SUCCESS

    def _output_resources_forward(self):
        """See base class"""
        return self._upstream_resources

    @classmethod
    def from_dict(cls, item_dict, name, project_dir, app_settings, specifications, logger):
        """See base class."""
        return cls(name, project_dir, logger)
