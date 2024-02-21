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

"""Contains Data Store's executable item as well as support utilities."""
from pathlib import Path
from spinedb_api import DatabaseMapping
from spinedb_api.exception import SpineDBAPIError
from spine_engine.project_item.executable_item_base import ExecutableItemBase
from spine_engine.utils.serialization import deserialize_path
from .item_info import ItemInfo
from .output_resources import scan_for_resources
from ..utils import check_database_url, convert_to_sqlalchemy_url


class ExecutableItem(ExecutableItemBase):
    def __init__(self, name, url, project_dir, logger):
        """
        Args:
            name (str): item's name
            url (URL): database's URL
            project_dir (str): absolute path to project directory
            logger (LoggerInterface): a logger
        """
        super().__init__(name, project_dir, logger)
        self._url = url
        self._validated = False

    @staticmethod
    def item_type():
        """Returns the data store executable's type identifier string."""
        return ItemInfo.item_type()

    @staticmethod
    def is_filter_terminus():
        """See base class."""
        return True

    def ready_to_execute(self, settings):
        """See base class."""
        if not super().ready_to_execute(settings) or not self._check_sqlite_file_exists():
            return False
        error = check_database_url(self._url)
        return error is None

    def _get_url(self):
        if not self._check_sqlite_file_exists():
            self._logger.msg_error.emit("SQLite file does not exist.")
            return None
        if not self._validated:
            prompt_data = DatabaseMapping.get_upgrade_db_prompt_data(self._url, create=True)
            if prompt_data is not None:
                kwargs = self._logger.prompt.emit(prompt_data)
                if kwargs is None:
                    return None
            else:
                kwargs = {}
            try:
                DatabaseMapping.create_engine(self._url, create=True, **kwargs)
                return self._url
            except SpineDBAPIError as err:
                self._logger.msg_error.emit(str(err))
                return None
            finally:
                self._validated = True
        return self._url

    def _check_sqlite_file_exists(self):
        """Checks that the database file exists for SQLite databases.

        Returns:
            bool: True if SQLite file exists or database has different dialect, False otherwise
        """
        if self._url.drivername.startswith("sqlite"):
            database_path = Path(self._url.database)
            if not database_path.exists():
                return False
            elif database_path.is_dir():
                return False
        return True

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
