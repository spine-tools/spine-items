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

"""Contains Importer's specification."""
from spine_engine.project_item.project_item_specification import ProjectItemSpecification
from .item_info import ItemInfo


class ImporterSpecification(ProjectItemSpecification):
    """Importer's specification."""

    def __init__(self, name, mapping, description=None):
        """
        Args:
            name (str): specification's name
            mapping (dict): mapping dict
            description (str): specification's description
        """
        super().__init__(name, description, ItemInfo.item_type())
        self._mapping = mapping

    @property
    def mapping(self):
        return self._mapping

    def is_equivalent(self, other):
        """See base class."""
        return self.name == other.name and self.description == other.description and self.mapping == other.mapping

    def to_dict(self):
        """See base class."""
        return {
            "name": self.name,
            "item_type": ItemInfo.item_type(),
            "mapping": self.mapping,
            "description": self.description,
        }

    @staticmethod
    def from_dict(specification_dict, logger):
        """
        Restores :class:`ImporterSpecification` from a dictionary.

        Args:
            specification_dict (dict): serialized specification
            logger (LoggerInterface): a logger

        Returns:
            ImporterSpecification: deserialized specification
        """
        name = specification_dict["name"]
        description = specification_dict.get("description", None)
        mapping = specification_dict["mapping"]
        return ImporterSpecification(name, mapping, description)
