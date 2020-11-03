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
        self._forward_resources = list()
        self._specification = specification
        self._filter_config_path = config_path

    @staticmethod
    def item_type():
        """Returns the data store executable's type identifier string."""
        return ItemInfo.item_type()

    def _output_resources_forward(self):
        """See base class."""
        return self._forward_resources

    def _execute_forward(self, resources):
        """See base class."""
        database_resources = [r for r in resources if r.type_ == "database"]
        if self._specification is None or not self._specification.settings:
            self._forward_resources = database_resources
            return True
        self._forward_resources = list()
        if self._specification.settings.use_shorthand():
            for resource in database_resources:
                url = append_filter_config(resource.url, self._specification.settings.filter_config())
                filter_resource = ProjectItemResource(self, "database", url)
                self._forward_resources.append(filter_resource)
        else:
            with open(self._filter_config_path, "w") as out_file:
                json.dump(self._specification.settings.filter_config(), out_file)
            for resource in database_resources:
                url = append_filter_config(resource.url, self._filter_config_path)
                filter_resource = ProjectItemResource(self, "database", url)
                self._forward_resources.append(filter_resource)
        return True

    # pylint: disable=no-self-use
    def _skip_forward(self, resources):
        """See base class."""
        self._execute_forward(resources)

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
