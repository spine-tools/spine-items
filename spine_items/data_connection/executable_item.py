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

"""Contains Data Connection's executable item as well as support utilities."""
import os
from spine_engine.project_item.executable_item_base import ExecutableItemBase
from spine_engine.utils.serialization import deserialize_path
from .item_info import ItemInfo
from .output_resources import scan_for_resources
from .utils import restore_database_references


class ExecutableItem(ExecutableItemBase):
    """The executable parts of Data Connection."""

    def __init__(self, name, file_references, db_references, project_dir, logger):
        """
        Args:
            name (str): item's name
            file_references (list): a list of absolute paths to connected files
            db_references (list): a list of url dicts to connected dbs
            project_dir (str): absolute path to project directory
            logger (LoggerInterface): a logger
        """
        super().__init__(name, project_dir, logger)
        data_files = list()
        with os.scandir(self._data_dir) as scan_iterator:
            for entry in scan_iterator:
                if entry.is_file():
                    data_files.append(entry.path)
        self._file_paths = file_references + data_files
        self._urls = db_references

    @staticmethod
    def item_type():
        """Returns DataConnectionExecutable's type identifier string."""
        return ItemInfo.item_type()

    def _output_resources_forward(self):
        """See base class."""
        return scan_for_resources(self, self._file_paths, self._urls, self._project_dir)

    @classmethod
    def from_dict(cls, item_dict, name, project_dir, app_settings, specifications, logger):
        """See base class."""
        file_references = item_dict["file_references"]
        file_references = [deserialize_path(r, project_dir) for r in file_references]
        db_references = restore_database_references(
            item_dict.get("db_references", []), item_dict.get("db_credentials", {}), project_dir
        )
        return cls(name, file_references, db_references, project_dir, logger)
