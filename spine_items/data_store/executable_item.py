######################################################################################################################
# Copyright (C) 2017-2021 Spine project consortium
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

from spinedb_api import DatabaseMapping
from spinedb_api.exception import SpineDBAPIError, SpineDBVersionError
from spine_engine.project_item.executable_item_base import ExecutableItemBase
from spine_engine.utils.serialization import deserialize_path
from .item_info import ItemInfo
from .utils import convert_to_sqlalchemy_url
from .output_resources import scan_for_resources


class ExecutableItem(ExecutableItemBase):
    def __init__(self, name, url, project_dir, logger):
        """
        Args:
            name (str): item's name
            url (str): database's URL
            logs_dir (str): path to the directory where logs should be stored
            project_dir (str): absolute path to project directory
            logger (LoggerInterface): a logger
        """
        super().__init__(name, project_dir, logger)
        self._url = url

    @staticmethod
    def item_type():
        """Returns the data store executable's type identifier string."""
        return ItemInfo.item_type()

    def _get_url(self):
        try:
            DatabaseMapping.create_engine(self._url, create=True)
            return self._url
        except SpineDBVersionError as v_err:
            prompt = {"type": "upgrade_db", "url": self._url, "current": v_err.current, "expected": v_err.expected}
            if not self._logger.prompt.emit(prompt):
                return None
            DatabaseMapping.create_engine(self._url, upgrade=True)
            return self._url
        except SpineDBAPIError as err:
            self._logger.msg_error.emit(str(err))
            return None

    def _output_resources_backward(self):
        """See base class."""
        return self._output_resources_forward()

    def _output_resources_forward(self):
        """See base class."""
        return scan_for_resources(self, self._get_url())

    @classmethod
    def from_dict(cls, item_dict, name, project_dir, app_settings, specifications, logger):
        """See base class."""
        if item_dict["url"]["dialect"] == "sqlite":
            item_dict["url"]["database"] = deserialize_path(item_dict["url"]["database"], project_dir)
        url = convert_to_sqlalchemy_url(item_dict["url"], name, logger)
        return cls(name, url, project_dir, logger)
