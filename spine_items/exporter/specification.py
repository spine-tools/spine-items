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
Contains Exporter's specifications.

:authors: A. Soininen (VTT)
:date:    11.12.2020
"""
from dataclasses import dataclass
from enum import Enum, unique
import json
from spine_engine.project_item.project_item_specification import ProjectItemSpecification
from spinedb_api.mapping import Mapping
from spinedb_api.mapping import to_dict as mapping_to_dict
from spinedb_api.export_mapping.export_mapping import from_dict as mapping_from_dict
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


@dataclass
class MappingSpecification:
    type: MappingType
    enabled: bool
    export_objects_flag: bool
    use_fixed_table_name_flag: bool
    root: Mapping


class Specification(ProjectItemSpecification):
    """Exporter's specification."""

    def __init__(self, name="", description="", mapping_specifications=None, output_format=OutputFormat.CSV):
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

    def save(self):
        """See base class."""
        specification_dict = self.to_dict()
        with open(self.definition_file_path, "w") as fp:
            json.dump(specification_dict, fp)
        return True

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
                "use_fixed_table_name": mapping_spec.use_fixed_table_name_flag,
            }
            if mapping_spec.type in (MappingType.relationships,):
                spec_dict["export_objects_flag"] = mapping_spec.export_objects_flag
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
                spec_dict.get("export_objects_flag", False),
                spec_dict.get("use_fixed_table_name", False),
                mapping_from_dict(spec_dict["mapping"]),
            )
            for name, spec_dict in specification_dict["mappings"].items()
        }
        try:
            output_format = OutputFormat(specification_dict["output_format"])
        except ValueError:
            output_format = OutputFormat.CSV
        return Specification(
            specification_dict["name"], specification_dict["description"], mapping_specifications, output_format
        )
