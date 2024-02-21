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

"""Contains Merger's executable item as well as support utilities."""
from contextlib import ExitStack
from spine_engine.utils.returning_process import ReturningProcess
from spine_engine.spine_engine import ItemExecutionFinishState
from ..db_writer_executable_item_base import DBWriterExecutableItemBase
from .item_info import ItemInfo
from .do_work import do_work


class ExecutableItem(DBWriterExecutableItemBase):
    def __init__(self, name, cancel_on_error, project_dir, logger):
        """
        Args:
            name (str): item's name
            cancel_on_error (bool): if True, revert changes on error and move on
            project_dir (str): absolute path to project directory
            logger (LoggerInterface): a logger
        """
        super().__init__(name, project_dir, logger)
        self._cancel_on_error = cancel_on_error
        self._process = None

    @staticmethod
    def item_type():
        """Returns the data store executable's type identifier string."""
        return ItemInfo.item_type()

    @classmethod
    def from_dict(cls, item_dict, name, project_dir, app_settings, specifications, logger):
        """See base class."""
        cancel_on_error = item_dict["cancel_on_error"]
        return cls(name, cancel_on_error, project_dir, logger)

    def execute(self, forward_resources, backward_resources, lock):
        """See base class."""
        if not super().execute(forward_resources, backward_resources, lock):
            return ItemExecutionFinishState.FAILURE
        from_resources = [r for r in forward_resources if r.type_ == "database"]
        to_resources = [r for r in backward_resources if r.type_ == "database"]
        if not from_resources or not to_resources:
            return ItemExecutionFinishState.SUCCESS
        with ExitStack() as stack:
            from_server_urls = [stack.enter_context(resource.open()) for resource in from_resources]
            to_server_urls = [stack.enter_context(resource.open()) for resource in to_resources]
            self._process = ReturningProcess(
                target=do_work,
                args=(self._cancel_on_error, self._logs_dir, from_server_urls, to_server_urls, lock, self._logger),
            )
            return_value = self._process.run_until_complete()
            self._process = None
            if return_value[0]:
                return ItemExecutionFinishState.SUCCESS
            return ItemExecutionFinishState.FAILURE

    def stop_execution(self):
        """Stops executing this DS."""
        super().stop_execution()
        if self._process is not None:
            self._process.terminate()
            self._process = None
