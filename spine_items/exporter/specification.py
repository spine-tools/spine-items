######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Contains Exporter's specifications.

:authors: A. Soininen (VTT)
:date:    11.12.2020
"""
from dataclasses import dataclass
from enum import Enum, unique
from spine_engine.project_item.project_item_specification import ProjectItemSpecification
from spinedb_api.mapping import to_dict as mapping_to_dict, Position, unflatten
from spinedb_api.export_mapping.export_mapping import (
    ExportMapping,
    from_dict as mapping_from_dict,
    ParameterValueIndexMapping,
    ParameterDefaultValueIndexMapping,
    IndexNameMapping,
    DefaultValueIndexNameMapping,
    legacy_group_fn_from_dict,
)
from .item_info import ItemInfo


@unique
class MappingType(Enum):
    alternatives = "alternatives"
    features = "features"
    objects = "objects"
    object_groups = "object_groups"
    object_group_parameter_values = "object_group_parameter_values"
    object_parameter_default_values = "object_default_parameter_values"
    object_parameter_values = "object_parameter_values"
    parameter_value_lists = "parameter_value_lists"
    relationships = "relationships"
    relationship_parameter_default_values = "relationship_default_parameter_values"
    relationship_parameter_values = "relationship_parameter_values"
    relationship_object_parameter_default_values = "relationship_object_parameter_default_values"
    relationship_object_parameter_values = "relationship_object_parameter_values"
    scenario_alternatives = "scenario_alternatives"
    scenarios = "scenarios"
    tool_features = "tool_features"
    tool_feature_methods = "tool_feature_methods"
    tools = "tools"


@unique
class OutputFormat(Enum):
    CSV = "csv"
    EXCEL = "Excel"
    GDX = "gdx"
    SQL = "SQL"

    def is_compatible_file_extension(self, extension):
        """Tests if given file extension is acceptable for current output format.

        Args:
            extension (str): file extension without the dot
        """
        if self == OutputFormat.CSV:
            return extension in ("csv", "dat", "txt")
        if self == OutputFormat.EXCEL:
            return extension == "xlsx"
        if self == OutputFormat.GDX:
            return extension == "gdx"
        if self == OutputFormat.SQL:
            return extension in ("sqlite", "sqlite3")
        return False

    def file_extension(self):
        """Returns a file extension for the output format.

        Returns:
            str: file extension without the dot
        """
        return {
            OutputFormat.CSV: "csv",
            OutputFormat.EXCEL: "xlsx",
            OutputFormat.GDX: "gdx",
            OutputFormat.SQL: "sqlite",
        }[self]

    @staticmethod
    def output_format_from_extension(extension):
        """Creates an output format from given file extension.

        Args:
            extension (str): file extension without the dot

        Returns:
            OutputFormat: output format or None if extension is unknown
        """
        try:
            return {
                "csv": OutputFormat.CSV,
                "dat": OutputFormat.CSV,
                "gdx": OutputFormat.GDX,
                "sqlite": OutputFormat.SQL,
                "txt": OutputFormat.CSV,
                "xlsx": OutputFormat.EXCEL,
            }[extension]
        except KeyError:
            return None

    @staticmethod
    def default():
        """Return the default output format.

        Returns:
            OutputFormat: default output format
        """
        return OutputFormat.CSV

    def is_multi_file_capable(self):
        """Tests if the output format is capable of having multiple output files.

        Returns:
            bool: True if multiple output files are possible, False otherwise
        """
        return self == OutputFormat.CSV


@dataclass(eq=False)
class MappingSpecification:
    type: MappingType
    enabled: bool
    always_export_header: bool
    group_fn: str
    use_fixed_table_name_flag: bool
    root: ExportMapping

    def to_dict(self):
        """Serializes specification into dictionary.

        Returns:
            dict: serialized specification
        """
        mapping_dict = dict(vars(self))
        mapping_dict["type"] = mapping_dict["type"].value
        mapping_dict["root"] = mapping_to_dict(mapping_dict["root"])
        return mapping_dict

    @staticmethod
    def from_dict(mapping_dict):
        """Deserializes specification from dictionary.

        Args:
            mapping_dict (dict): serialized specification

        Returns:
            MappingSpecifiation: deserialized specification
        """
        root = mapping_from_dict(mapping_dict.pop("root"))
        type_ = MappingType(mapping_dict.pop("type"))
        return MappingSpecification(root=root, type=type_, **mapping_dict)


class Specification(ProjectItemSpecification):
    """Exporter's specification."""

    def __init__(self, name="", description="", mapping_specifications=None, output_format=OutputFormat.default()):
        """
        Args:
            name (str): specification name
            description (str): description
            mapping_specifications (dict, optional): mapping from export mapping name to ``MappingSpecification``
            output_format (OutputFormat): output format
        """
        super().__init__(name, description, ItemInfo.item_type(), ItemInfo.item_category())
        if mapping_specifications is None:
            mapping_specifications = dict()
        self._mapping_specifications = mapping_specifications
        self.output_format = output_format

    def is_equivalent(self, other):
        """
        Checks if specifications are essentially equivalent.

        Args:
            other (Specification): another specification

        Returns:
            bool: True if specifications are equivalent, False otherwise
        """
        return (
            self.output_format == other.output_format and self._mapping_specifications == other._mapping_specifications
        )

    def mapping_specifications(self):
        """
        Returns export mapping specifications.

        Returns:
            dict: mapping specifications
        """
        return self._mapping_specifications

    def enabled_specifications(self):
        """
        Returns enabled export mapping specifications.

        Returns:
            dict: mapping specifications
        """
        return {name: spec for name, spec in self._mapping_specifications.items() if spec.enabled}

    def root_mapping(self, name):
        """
        Returns root mapping for given name.

        Args:
            name (str): mapping's name

        Returns:
            Mapping: root mapping
        """
        return self._mapping_specifications[name].root

    def mapping_type(self, name):
        """
        Returns mapping type for given name.

        Args:
            name (str): mapping's name

        Returns:
            MappingType: mapping's type
        """
        return self._mapping_specifications[name].type

    def is_exporting_multiple_files(self):
        """Tests if this specification would result in multiple files being exported.

        Returns:
            bool: True if multiple files will be exporter, False otherwise
        """
        if not self.output_format.is_multi_file_capable():
            return False
        for mapping_spec in self._mapping_specifications.values():
            if mapping_spec.use_fixed_table_name_flag or any(
                m.position == Position.table_name for m in mapping_spec.root.flatten()
            ):
                return True
        return False

    def to_dict(self):
        """
        Serializes the specification into JSON compatible dictionary.

        Returns:
            dict: serialized specification
        """
        mappings = dict()
        for name, mapping_spec in self._mapping_specifications.items():
            spec_dict = {
                "type": mapping_spec.type.value,
                "mapping": mapping_to_dict(mapping_spec.root),
                "enabled": mapping_spec.enabled,
                "always_export_header": mapping_spec.always_export_header,
                "group_fn": mapping_spec.group_fn,
                "use_fixed_table_name": mapping_spec.use_fixed_table_name_flag,
            }
            mappings[name] = spec_dict
        return {
            "item_type": ItemInfo.item_type(),
            "output_format": self.output_format.value,
            "name": self.name,
            "description": self.description,
            "mappings": mappings,
        }

    @staticmethod
    def from_dict(specification_dict):
        """
        Restores specification from dictionary.

        Args:
            specification_dict (dict): serialized specification

        Returns:
            Specification: restored specification
        """
        mapping_specifications = {
            name: MappingSpecification(
                MappingType(spec_dict["type"]),
                spec_dict.get("enabled", True),
                spec_dict.get("always_export_header", True),
                spec_dict.get("group_fn", legacy_group_fn_from_dict(spec_dict["mapping"])),
                spec_dict.get("use_fixed_table_name", False),
                _add_index_names(mapping_from_dict(spec_dict["mapping"])),
            )
            for name, spec_dict in specification_dict["mappings"].items()
        }
        try:
            output_format = OutputFormat(specification_dict["output_format"])
        except ValueError:
            output_format = OutputFormat.default()
        return Specification(
            specification_dict["name"], specification_dict["description"], mapping_specifications, output_format
        )


def _add_index_names(mapping):
    """Adds index name mappings to legacy mappings that don't have them.

    Args:
        mapping (ExportMapping): mapping to modify

    Returns:
        mapping (ExportMapping): fixed mapping
    """
    flattened = mapping.flatten()
    if any((isinstance(m, (IndexNameMapping, DefaultValueIndexNameMapping)) for m in flattened)):
        return mapping
    if any((isinstance(m, (ParameterValueIndexMapping, ParameterDefaultValueIndexMapping)) for m in flattened)):
        fixed = list()
        for m in flattened:
            if isinstance(m, ParameterValueIndexMapping):
                fixed.append(IndexNameMapping(Position.hidden))
            elif isinstance(m, ParameterDefaultValueIndexMapping):
                fixed.append(DefaultValueIndexNameMapping(Position.hidden))
            fixed.append(m)
        mapping = unflatten(fixed)
    return mapping
