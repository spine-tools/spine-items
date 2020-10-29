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
Contains Data transformer's specification.

:authors: A. Soininen (VTT)
:date:    2.10.2020
"""
import json
from spinedb_api.filters.renamer import entity_class_renamer_config
from spinetoolbox.project_item.project_item_specification import ProjectItemSpecification
from .item_info import ItemInfo


class DataTransformerSpecification(ProjectItemSpecification):
    """Data transformer's specification."""

    def __init__(self, name, renaming, description=None):
        """
        Args:
            name (str): specification's name
            renaming (dict): mapping from previous to the new name
            description (str): specification's description
        """
        super().__init__(name, description, ItemInfo.item_type(), ItemInfo.item_category())
        self._name_map = renaming

    def is_equivalent(self, other):
        """
        Returns True if two specifications are essentially the same.

        Args:
            other (DataTransformerSpecification): specification to compare to

        Returns:
            bool: True if the specifications are equivalent, False otherwise
        """
        return self.name == other.name and self.description == other.description and self._name_map == other._name_map

    @property
    def entity_class_name_map(self):
        """
        Returns the map for entity class renaming.

        Returns:
            dict: map from original to new name
        """
        return self._name_map

    def entity_class_rename_config(self):
        return entity_class_renamer_config(**self._name_map)

    def to_dict(self):
        """
        Serializes specification into a dict.

        Returns:
            dict: serialized specification
        """
        return {
            "name": self.name,
            "item_type": ItemInfo.item_type(),
            "description": self.description,
            "entity_class_name_map": self._name_map,
        }

    @staticmethod
    def from_dict(specification_dict, logger):
        """
        Restores :class:`DataTransformerSpecification` from a dictionary.

        Args:
            specification_dict (dict): serialized specification
            logger (LoggerInterface): a logger

        Returns:
            DataTransformerSpecification: deserialized specification
        """
        name = specification_dict["name"]
        description = specification_dict["description"]
        renaming = specification_dict["entity_class_name_map"]
        return DataTransformerSpecification(name, renaming, description)

    def save(self):
        """See base class."""
        specification_dict = self.to_dict()
        with open(self.definition_file_path, "w") as fp:
            json.dump(specification_dict, fp)
        return True
