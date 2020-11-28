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
Contains Data transformer's executable item as well as support utilities.

:authors: A. Soininen (VTT)
:date:    2.10.2020
"""
import json
from pathlib import Path
from spinedb_api import append_filter_config
from spine_engine.project_item.executable_item_base import ExecutableItemBase
from spine_engine.project_item.project_item_resource import ProjectItemResource
from spine_engine.utils.helpers import shorten
from .filter_config_path import filter_config_path
from .item_info import ItemInfo
from .utils import make_metadata


class ExecutableItem(ExecutableItemBase):
    def __init__(self, name, specification, config_path, logger):
        """
        Args:
            name (str): item's name
            specification (DataTransformerSpecification, optional): item's specification
            config_path (str): path to the filter's configuration file
            logger (LoggerInterface): a logger
        """
        super().__init__(name, logger)
        self._db_resources = list()
        self._specification = specification
        self._filter_config_path = config_path

    @staticmethod
    def item_type():
        """Returns the data store executable's type identifier string."""
        return ItemInfo.item_type()

    def _output_resources_forward(self):
        """See base class."""
        if self._specification is None or self._specification.settings is None:
            return [
                ProjectItemResource(self, "database", url, metadata=metadata)
                for url, metadata in self._url_metadata_iterator()
            ]
        if self._specification.settings.use_shorthand():
            config = self._specification.settings.filter_config()
            return [
                ProjectItemResource(self, "database", append_filter_config(url, config), metadata=metadata)
                for url, metadata in self._url_metadata_iterator()
            ]
        with open(self._filter_config_path, "w") as filter_config_file:
            json.dump(self._specification.settings.filter_config(), filter_config_file)
        return [
            ProjectItemResource(
                self, "database", append_filter_config(url, self._filter_config_path), metadata=metadata
            )
            for url, metadata in self._url_metadata_iterator()
        ]

    def _url_metadata_iterator(self):
        for resource in self._db_resources:
            yield resource.url, make_metadata(resource, self.name)

    def execute(self, forward_resources, backward_resources):
        """See base class."""
        if not super().execute(forward_resources, backward_resources):
            return False
        self._db_resources = [r for r in forward_resources if r.type_ == "database"]
        return True

    # pylint: disable=no-self-use
    def skip_execution(self, forward_resources, backward_resources):
        """See base class."""
        self.execute(forward_resources, backward_resources)

    @classmethod
    def from_dict(cls, item_dict, name, project_dir, app_settings, specifications, logger):
        """See base class."""
        specification_name = item_dict["specification"]
        specification = ExecutableItemBase._get_specification(
            name, ItemInfo.item_type(), specification_name, specifications, logger
        )
        data_dir = str(Path(project_dir, ".spinetoolbox", "items", shorten(name)))
        path = filter_config_path(data_dir)
        return cls(name, specification, path, logger)
