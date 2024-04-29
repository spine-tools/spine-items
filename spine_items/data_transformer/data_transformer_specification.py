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

"""Contains Data transformer's specification."""
from spine_engine.project_item.project_item_specification import ProjectItemSpecification
from .item_info import ItemInfo
from .settings import EntityClassRenamingSettings, settings_from_dict


class DataTransformerSpecification(ProjectItemSpecification):
    """
    Data transformer's specification.

    Attributes:
        settings (FilterSettings): transformer's filter settings
    """

    def __init__(self, name, settings=None, description=None):
        """
        Args:
            name (str): specification's name
            settings (FilterSettings, optional): filter settings
            description (str, optional): specification's description
        """
        super().__init__(name, description, ItemInfo.item_type())
        self.settings = settings

    def is_equivalent(self, other):
        """See base class."""
        return self.name == other.name and self.description == other.description and self.settings == other.settings

    def to_dict(self):
        """See base class."""
        filter_dict = (
            {"type": self.settings.type(), "settings": self.settings.to_dict()} if self.settings is not None else None
        )
        return {
            "name": self.name,
            "item_type": ItemInfo.item_type(),
            "description": self.description,
            "filter": filter_dict,
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
        filter_ = specification_dict.get("filter")
        if filter_ is not None:
            settings = settings_from_dict(filter_)
        else:
            # For legacy JSON.
            renaming = specification_dict.get("entity_class_name_map")
            if renaming is not None:
                settings = EntityClassRenamingSettings(renaming)
            else:
                settings = None
        return DataTransformerSpecification(name, settings, description)
