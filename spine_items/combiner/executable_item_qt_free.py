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
Contains Combiner's executable item as well as support utilities.

:authors: A. Soininen (VTT)
:date:   2.4.2020
"""
import os
import pathlib
from spine_engine.project_item.executable_item_base import ExecutableItemBase
from spine_engine.utils.helpers import shorten
from spine_engine.utils.returning_process import ReturningProcess
from .item_info import ItemInfo
from .do_work import do_work


class ExecutableItem(ExecutableItemBase):
    def __init__(self, name, logs_dir, cancel_on_error, logger):
        """
        Args:
            name (str): item's name
            logs_dir (str): path to the directory where logs should be stored
            cancel_on_error (bool): if True, revert changes on error and move on
            logger (LoggerInterface): a logger
        """
        super().__init__(name, logger)
        self._logs_dir = logs_dir
        self._cancel_on_error = cancel_on_error
        self._process = None

    @staticmethod
    def item_type():
        """Returns Combiner's type identifier string."""
        return ItemInfo.item_type()

    @classmethod
    def from_dict(cls, item_dict, name, project_dir, app_settings, specifications, logger):
        """See base class."""
        data_dir = pathlib.Path(project_dir, ".spinetoolbox", "items", shorten(name))
        logs_dir = os.path.join(data_dir, "logs")
        cancel_on_error = item_dict["cancel_on_error"]
        return cls(name, logs_dir, cancel_on_error, logger)

    def stop_execution(self):
        """Stops executing this Gimlet."""
        super().stop_execution()
        if self._process is not None:
            self._process.terminate()
            self._process = None

    @staticmethod
    def _urls_from_resources(resources):
        return [r.url for r in resources if r.type_ == "database"]

    def execute(self, forward_resources, backward_resources):
        """See base class."""
        if not super().execute(forward_resources, backward_resources):
            return False
        from_urls = self._urls_from_resources(forward_resources)
        to_urls = self._urls_from_resources(backward_resources)
        if not from_urls:
            self._logger.msg_warning.emit("No input database(s) available. Moving on...")
            return True
        if not to_urls:
            self._logger.msg_warning.emit("No output database available. Moving on...")
            return True
        self._process = ReturningProcess(
            target=do_work, args=(self._cancel_on_error, self._logs_dir, from_urls, to_urls, self._logger)
        )
        self._process.run_until_complete()
        self._logger.msg_success.emit(f"Executing Combiner {self.name} finished")
        self._process = None
        return True
