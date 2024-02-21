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

"""Contains settings classes for filters and manipulators."""
from spinedb_api.filters.renamer import entity_class_renamer_config, parameter_renamer_config
from spinedb_api.filters.value_transformer import value_transformer_config


class FilterSettings:
    """Base class for filter and manipulator settings."""

    def filter_config(self):
        """
        Creates filter configuration dictionary.

        Returns:
            dict: filter configuration
        """
        raise NotImplementedError()

    def report_inconsistencies(self):
        """Checks and reports errors and inconsistencies in the settings.

        Returns:
            list of str: list of warning messages
        """
        return []

    def to_dict(self):
        """
        Serializes settings to JSON compatible dictionary.

        Returns:
            dict: serialized settings
        """
        raise NotImplementedError()

    @staticmethod
    def type():
        """
        Returns a type identifier string.

        Returns:
            str: type id
        """
        raise NotImplementedError()

    @staticmethod
    def use_shorthand():
        """
        Tells if the filter config should use shorthand notation.

        Returns:
            bool: True is shorthand notation is preferred, False if config should be written on disk.
        """
        raise NotImplementedError()

    @staticmethod
    def from_dict(settings_dict):
        """
        Restores settings from dictionary.

        Args:
            settings_dict (dict): serialized settings

        Returns:
            FilterSettings: deserialized settings
        """
        raise NotImplementedError()


class RenamingSettings(FilterSettings):
    """
    Base class for renamer settings.

    Attributes:
        name_map (dict): a mapping from original name to new name
    """

    def __init__(self, name_map):
        """
        Args:
            name_map (dict): a mapping from original name to new name
        """
        self.name_map = name_map

    def __eq__(self, other):
        if not isinstance(other, RenamingSettings):
            return NotImplemented
        return self.name_map == other.name_map

    def filter_config(self):
        """See base class."""
        raise NotImplementedError()

    @staticmethod
    def type():
        """See base class."""
        raise NotImplementedError()

    @staticmethod
    def use_shorthand():
        """See base class."""
        return False

    def to_dict(self):
        """See base class."""
        return self.name_map

    @staticmethod
    def from_dict(settings_dict):
        """See base class."""
        raise NotImplementedError()


class EntityClassRenamingSettings(RenamingSettings):
    """Settings for entity class renaming manipulator."""

    def filter_config(self):
        """See base class."""
        useful = {name: rename for name, rename in self.name_map.items() if rename and name != rename}
        return entity_class_renamer_config(**useful)

    @staticmethod
    def from_dict(settings_dict):
        """See base class."""
        return EntityClassRenamingSettings(settings_dict)

    @staticmethod
    def type():
        """See base class."""
        return "entity_class_rename"


class ParameterRenamingSettings(RenamingSettings):
    """Settings for parameter renaming manipulator."""

    def filter_config(self):
        """See base class."""
        name_map = dict()
        for class_name, param_renames in self.name_map.items():
            useful = {name: rename for name, rename in param_renames.items() if rename and name != rename}
            if useful:
                name_map[class_name] = useful
        return parameter_renamer_config(name_map)

    def report_inconsistencies(self):
        messages = super().report_inconsistencies()
        if any(not klass for klass in self.name_map):
            messages.append("Class name(s) missing in specification.")
        return messages

    @staticmethod
    def from_dict(settings_dict):
        """See base class."""
        if settings_dict and isinstance(next(iter(settings_dict.values())), str):
            # Legacy settings.
            settings_dict = {"": settings_dict}
        return ParameterRenamingSettings(settings_dict)

    @staticmethod
    def type():
        """See base class."""
        return "parameter_rename"


class ValueTransformSettings(FilterSettings):
    """Settings for value transformer manipulator."""

    def __init__(self, instructions):
        """
        Args:
            instructions (dict): transform instructions
        """
        self.instructions = instructions

    def filter_config(self):
        # Remove no-op instructions.
        instructions = dict()
        for class_name, parameter_transformation in self.instructions.items():
            useful = {
                param_name: instructions
                for param_name, instructions in parameter_transformation.items()
                if instructions
            }
            if useful:
                instructions[class_name] = useful
        return value_transformer_config(instructions)

    def to_dict(self):
        return self.instructions

    @staticmethod
    def type():
        return "value_transformer"

    @staticmethod
    def use_shorthand():
        return False

    @staticmethod
    def from_dict(settings_dict):
        return ValueTransformSettings(settings_dict)


def settings_from_dict(settings_dict):
    """
    Restores filter settings.

    Args:
        settings_dict (dict): serialized filter settings

    Returns:
        FilterSettings: restored settings
    """
    restorers = {
        EntityClassRenamingSettings.type(): EntityClassRenamingSettings.from_dict,
        ParameterRenamingSettings.type(): ParameterRenamingSettings.from_dict,
        ValueTransformSettings.type(): ValueTransformSettings.from_dict,
    }
    return restorers.get(settings_dict["type"], lambda _: None)(settings_dict["settings"])
