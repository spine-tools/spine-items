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

"""Contains Data transformer's executable item as well as support utilities."""
from spine_engine.project_item.executable_item_base import ExecutableItemBase
from spine_engine.spine_engine import ItemExecutionFinishState
from .filter_config_path import filter_config_path
from .item_info import ItemInfo
from .output_resources import scan_for_resources


class ExecutableItem(ExecutableItemBase):
    def __init__(self, name, specification, project_dir, logger):
        """
        Args:
            name (str): item's name
            specification (DataTransformerSpecification, optional): item's specification
            project_dir (str): absolute path to project directory
            logger (LoggerInterface): a logger
        """
        super().__init__(name, project_dir, logger)
        self._db_resources = list()
        self._specification = specification
        self._filter_config_path = filter_config_path(self._data_dir)

    @staticmethod
    def item_type():
        """Returns the data store executable's type identifier string."""
        return ItemInfo.item_type()

    def _output_resources_forward(self):
        """See base class."""
        return scan_for_resources(self, self._specification, self._db_resources, self._filter_config_path)

    def ready_to_execute(self, settings):
        if self._specification is None:
            return True
        messages = self._specification.settings.report_inconsistencies()
        if messages:
            for message in messages:
                self._logger.msg_error.emit(message)
            return False
        return True

    def execute(self, forward_resources, backward_resources, lock):
        """See base class."""
        if not super().execute(forward_resources, backward_resources, lock):
            return ItemExecutionFinishState.FAILURE
        self._db_resources = [r for r in forward_resources if r.type_ == "database"]
        return ItemExecutionFinishState.SUCCESS

    # pylint: disable=no-self-use
    def exclude_execution(self, forward_resources, backward_resources, lock):
        """See base class."""
        self.execute(forward_resources, backward_resources, lock)

    @classmethod
    def from_dict(cls, item_dict, name, project_dir, app_settings, specifications, logger):
        """See base class."""
        specification_name = item_dict["specification"]
        specification = ExecutableItemBase._get_specification(
            name, ItemInfo.item_type(), specification_name, specifications, logger
        )
        return cls(name, specification, project_dir, logger)
