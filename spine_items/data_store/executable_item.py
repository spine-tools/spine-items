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
Contains Data Store's executable item as well as support utilities.

:authors: A. Soininen (VTT)
:date:   1.4.2020
"""

import os
import pathlib
from spine_engine.project_item.executable_item_base import ExecutableItemBase
from spine_engine.utils.serialization import deserialize_path
from spine_engine.utils.returning_process import ReturningProcess
from spine_engine.utils.helpers import shorten
from .item_info import ItemInfo
from .utils import convert_to_sqlalchemy_url
from .do_work import do_work
from .output_resources import scan_for_resources


class ExecutableItem(ExecutableItemBase):
    def __init__(self, name, url, logs_dir, cancel_on_error, logger):
        """
        Args:
            name (str): item's name
            url (str): database's URL
            logs_dir (str): path to the directory where logs should be stored
            cancel_on_error (bool): if True, revert changes on error and move on
            logger (LoggerInterface): a logger
        """
        super().__init__(name, logger)
        self._url = url
        self._logs_dir = logs_dir
        self._cancel_on_error = cancel_on_error
        self._process = None

    @staticmethod
    def item_type():
        """Returns the data store executable's type identifier string."""
        return ItemInfo.item_type()

    def _output_resources_backward(self):
        """See base class."""
        return self._output_resources_forward()

    def _output_resources_forward(self):
        """See base class."""
        return scan_for_resources(self, self._url)

    @classmethod
    def from_dict(cls, item_dict, name, project_dir, app_settings, specifications, logger):
        """See base class."""
        if item_dict["url"]["dialect"] == "sqlite":
            item_dict["url"]["database"] = deserialize_path(item_dict["url"]["database"], project_dir)
        url = convert_to_sqlalchemy_url(item_dict["url"], name, logger)
        data_dir = pathlib.Path(project_dir, ".spinetoolbox", "items", shorten(name))
        logs_dir = os.path.join(data_dir, "logs")
        cancel_on_error = item_dict["cancel_on_error"]
        return cls(name, url, logs_dir, cancel_on_error, logger)

    @staticmethod
    def _urls_from_resources(resources):
        return [r.url for r in resources if r.type_ == "database"]

    def execute(self, forward_resources, backward_resources):
        """See base class."""
        if not super().execute(forward_resources, backward_resources):
            return False
        from_urls = self._urls_from_resources(forward_resources)
        if not from_urls:
            return True
        self._process = ReturningProcess(
            target=do_work, args=(self._cancel_on_error, self._logs_dir, from_urls, str(self._url), self._logger)
        )
        success = self._process.run_until_complete()
        self._process = None
        return success

    def stop_execution(self):
        """Stops executing this DS."""
        super().stop_execution()
        if self._process is not None:
            self._process.terminate()
            self._process = None
