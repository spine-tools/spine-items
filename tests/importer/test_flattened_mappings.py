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

"""Unit tests for ``flattened_mappings`` module."""
import unittest
from spine_items.importer.flattened_mappings import FlattenedMappings, MappingType
from spinedb_api import import_mapping_from_dict
from spinedb_api.import_mapping.import_mapping import default_import_mapping
from spinedb_api.import_mapping.import_mapping_compat import parameter_mapping_from_dict


class TestFlattenedMappings(unittest.TestCase):
    def test_increasing_relationship_dimensions_keeps_import_objects_flags_consistent(self):
        mapping_dicts = [
            {"map_type": "RelationshipClass", "position": "hidden", "value": "o_to_q"},
            {"map_type": "RelationshipClassObjectClass", "position": "hidden", "value": "o"},
            {"map_type": "Relationship", "position": "hidden", "value": "relationship"},
            {"map_type": "RelationshipObject", "position": -1, "import_objects": True},
            {"map_type": "RelationshipMetadata", "position": "hidden"},
            {"map_type": "ParameterDefinition", "position": "hidden", "value": "param"},
            {"map_type": "Alternative", "position": "hidden", "value": "base"},
            {"map_type": "ParameterValueMetadata", "position": "hidden"},
            {"map_type": "ParameterValueType", "position": "hidden", "value": "map"},
            {"map_type": "IndexName", "position": "hidden", "value": "time"},
            {"map_type": "ParameterValueIndex", "position": 0},
            {"map_type": "ExpandedValue", "position": "hidden"},
        ]
        root_mapping = import_mapping_from_dict(mapping_dicts)
        flattened_mappings = FlattenedMappings(root_mapping)
        self.assertTrue(flattened_mappings.import_entities())
        flattened_mappings.set_dimension_count(2)
        self.assertTrue(flattened_mappings.import_entities())

    def test_default_entity_class_mapping(self):
        root_mapping = default_import_mapping("EntityClass")
        flattened_mappings = FlattenedMappings(root_mapping)
        self.assertEqual(flattened_mappings.map_type, MappingType.EntityClass)
        self.assertEqual(flattened_mappings.display_names, ["Entity class names", "Entity names", "Entity metadata"])
        self.assertIs(flattened_mappings.root_mapping, root_mapping)
        self.assertIsNone(flattened_mappings.value_type)
        self.assertFalse(flattened_mappings.is_time_series_value())
        self.assertFalse(flattened_mappings.is_map_value())
        self.assertEqual(flattened_mappings.map_dimension_count(), 1)
        self.assertEqual(flattened_mappings.read_start_row(), 0)
        self.assertEqual(flattened_mappings.skip_columns(), [])
        for row in range(len(flattened_mappings.display_names)):
            with self.subTest(row=row):
                self.assertEqual(flattened_mappings.display_position_type(row), "None")
                self.assertIsNone(flattened_mappings.display_position(row))
                self.assertEqual(flattened_mappings.display_row_issues(row), [])
        self.assertTrue(flattened_mappings.can_have_dimensions())
        self.assertFalse(flattened_mappings.has_dimensions())
        self.assertEqual(flattened_mappings.dimension_count(), 0)
        self.assertTrue(flattened_mappings.may_import_entity_alternatives())
        self.assertFalse(flattened_mappings.import_entity_alternatives())
        self.assertFalse(flattened_mappings.may_import_entities())
        self.assertFalse(flattened_mappings.import_entities())
        self.assertTrue(flattened_mappings.has_parameters())
        self.assertEqual(flattened_mappings.display_parameter_type(), "None")
        self.assertFalse(flattened_mappings.has_value_component())

    def test_add_dimensions_to_entity_class_mapping(self):
        root_mapping = default_import_mapping("EntityClass")
        flattened_mappings = FlattenedMappings(root_mapping)
        self.assertFalse(flattened_mappings.has_dimensions())
        self.assertEqual(flattened_mappings.dimension_count(), 0)
        flattened_mappings.set_dimension_count(1)
        self.assertTrue(flattened_mappings.has_dimensions())
        self.assertEqual(flattened_mappings.dimension_count(), 1)
        self.assertEqual(
            flattened_mappings.display_names,
            ["Entity class names", "Dimension names", "Element names", "Entity metadata"],
        )
        self.assertTrue(flattened_mappings.may_import_entities())
        self.assertFalse(flattened_mappings.import_entities())
        flattened_mappings.set_dimension_count(2)
        self.assertTrue(flattened_mappings.has_dimensions())
        self.assertEqual(flattened_mappings.dimension_count(), 2)
        self.assertEqual(
            flattened_mappings.display_names,
            [
                "Entity class names",
                "Dimension names 1",
                "Dimension names 2",
                "Element names 1",
                "Element names 2",
                "Entity metadata",
            ],
        )
        self.assertTrue(flattened_mappings.may_import_entities())
        self.assertFalse(flattened_mappings.import_entities())
        flattened_mappings.set_dimension_count(0)
        self.assertFalse(flattened_mappings.has_dimensions())
        self.assertEqual(flattened_mappings.dimension_count(), 0)
        self.assertEqual(flattened_mappings.display_names, ["Entity class names", "Entity names", "Entity metadata"])
        self.assertFalse(flattened_mappings.may_import_entities())
        self.assertFalse(flattened_mappings.import_entities())

    def test_add_parameter_definition_to_entity_class_mapping(self):
        root_mapping = default_import_mapping("EntityClass")
        flattened_mappings = FlattenedMappings(root_mapping)
        self.assertEqual(flattened_mappings.display_parameter_type(), "None")
        self.assertFalse(flattened_mappings.has_value_component())
        self.assertEqual(flattened_mappings.value_type_label(), "<no label>")
        parameter_root = parameter_mapping_from_dict({"map_type": "ParameterDefinition"})
        flattened_mappings.set_parameter_components(parameter_root)
        self.assertEqual(flattened_mappings.display_parameter_type(), "Definition")
        self.assertTrue(flattened_mappings.has_value_component())
        self.assertEqual(flattened_mappings.value_type_label(), "Default value:")
        self.assertEqual(
            flattened_mappings.display_names,
            [
                "Entity class names",
                "Entity names",
                "Entity metadata",
                "Parameter names",
                "Value list names",
                "Parameter default values",
            ],
        )

    def test_remove_parameter_definition_from_entity_class_mapping(self):
        root_mapping = default_import_mapping("EntityClass")
        flattened_mappings = FlattenedMappings(root_mapping)
        parameter_root = parameter_mapping_from_dict({"map_type": "ParameterDefinition"})
        flattened_mappings.set_parameter_components(parameter_root)
        flattened_mappings.set_parameter_components(None)
        self.assertEqual(flattened_mappings.display_parameter_type(), "None")
        self.assertFalse(flattened_mappings.has_value_component())
        self.assertEqual(flattened_mappings.value_type_label(), "<no label>")
        self.assertEqual(
            flattened_mappings.display_names,
            [
                "Entity class names",
                "Entity names",
                "Entity metadata",
            ],
        )

    def test_add_parameter_value_to_entity_class_mapping(self):
        root_mapping = default_import_mapping("EntityClass")
        flattened_mappings = FlattenedMappings(root_mapping)
        self.assertEqual(flattened_mappings.display_parameter_type(), "None")
        self.assertFalse(flattened_mappings.has_value_component())
        self.assertEqual(flattened_mappings.value_type_label(), "<no label>")
        parameter_root = parameter_mapping_from_dict({"map_type": "ParameterValue"})
        flattened_mappings.set_parameter_components(parameter_root)
        self.assertEqual(flattened_mappings.display_parameter_type(), "Value")
        self.assertTrue(flattened_mappings.has_value_component())
        self.assertEqual(flattened_mappings.value_type_label(), "Value:")
        self.assertEqual(
            flattened_mappings.display_names,
            [
                "Entity class names",
                "Entity names",
                "Entity metadata",
                "Alternative names",
                "Parameter names",
                "Parameter value metadata",
                "Parameter values",
            ],
        )

    def test_remove_parameter_value_from_entity_class_mapping(self):
        root_mapping = default_import_mapping("EntityClass")
        flattened_mappings = FlattenedMappings(root_mapping)
        parameter_root = parameter_mapping_from_dict({"map_type": "ParameterValue"})
        flattened_mappings.set_parameter_components(parameter_root)
        flattened_mappings.set_parameter_components(None)
        self.assertEqual(flattened_mappings.display_parameter_type(), "None")
        self.assertFalse(flattened_mappings.has_value_component())
        self.assertEqual(flattened_mappings.value_type_label(), "<no label>")
        self.assertEqual(
            flattened_mappings.display_names,
            [
                "Entity class names",
                "Entity names",
                "Entity metadata",
            ],
        )

    def test_add_entity_alternative_to_entity_class_mapping(self):
        root_mapping = default_import_mapping("EntityClass")
        flattened_mappings = FlattenedMappings(root_mapping)
        self.assertFalse(flattened_mappings.import_entity_alternatives())
        flattened_mappings.set_import_entity_alternatives(True)
        self.assertTrue(flattened_mappings.import_entity_alternatives())
        self.assertEqual(
            flattened_mappings.display_names,
            [
                "Entity class names",
                "Entity names",
                "Entity metadata",
                "Alternative names",
                "Entity activities",
            ],
        )

    def test_remove_entity_alternative_from_entity_class_mapping(self):
        root_mapping = default_import_mapping("EntityClass")
        flattened_mappings = FlattenedMappings(root_mapping)
        flattened_mappings.set_import_entity_alternatives(True)
        flattened_mappings.set_import_entity_alternatives(False)
        self.assertFalse(flattened_mappings.import_entity_alternatives())
        self.assertEqual(
            flattened_mappings.display_names,
            [
                "Entity class names",
                "Entity names",
                "Entity metadata",
            ],
        )

    def test_add_entity_alternative_and_parameter_value_to_entity_class_mapping(self):
        root_mapping = default_import_mapping("EntityClass")
        flattened_mappings = FlattenedMappings(root_mapping)
        flattened_mappings.set_import_entity_alternatives(True)
        parameter_root = parameter_mapping_from_dict({"map_type": "ParameterValue"})
        flattened_mappings.set_parameter_components(parameter_root)
        self.assertTrue(flattened_mappings.import_entity_alternatives())
        self.assertEqual(flattened_mappings.display_parameter_type(), "Value")
        self.assertTrue(flattened_mappings.has_value_component())
        self.assertEqual(flattened_mappings.value_type_label(), "Value:")
        self.assertEqual(
            flattened_mappings.display_names,
            [
                "Entity class names",
                "Entity names",
                "Entity metadata",
                "Alternative names",
                "Entity activities",
                "Parameter names",
                "Parameter value metadata",
                "Parameter values",
            ],
        )

    def test_add_parameter_value_and_entity_alternative_to_entity_class_mapping(self):
        root_mapping = default_import_mapping("EntityClass")
        flattened_mappings = FlattenedMappings(root_mapping)
        parameter_root = parameter_mapping_from_dict({"map_type": "ParameterValue"})
        flattened_mappings.set_parameter_components(parameter_root)
        flattened_mappings.set_import_entity_alternatives(True)
        self.assertTrue(flattened_mappings.import_entity_alternatives())
        self.assertEqual(flattened_mappings.display_parameter_type(), "Value")
        self.assertTrue(flattened_mappings.has_value_component())
        self.assertEqual(flattened_mappings.value_type_label(), "Value:")
        self.assertEqual(
            flattened_mappings.display_names,
            [
                "Entity class names",
                "Entity names",
                "Entity metadata",
                "Alternative names",
                "Entity activities",
                "Parameter names",
                "Parameter value metadata",
                "Parameter values",
            ],
        )

    def test_remove_parameter_value_from_entity_class_mapping_with_entity_alternative(self):
        root_mapping = default_import_mapping("EntityClass")
        flattened_mappings = FlattenedMappings(root_mapping)
        parameter_root = parameter_mapping_from_dict({"map_type": "ParameterValue"})
        flattened_mappings.set_parameter_components(parameter_root)
        flattened_mappings.set_import_entity_alternatives(True)
        flattened_mappings.set_parameter_components(None)
        self.assertTrue(flattened_mappings.import_entity_alternatives())
        self.assertEqual(flattened_mappings.display_parameter_type(), "None")
        self.assertFalse(flattened_mappings.has_value_component())
        self.assertEqual(flattened_mappings.value_type_label(), "<no label>")
        self.assertEqual(
            flattened_mappings.display_names,
            [
                "Entity class names",
                "Entity names",
                "Entity metadata",
                "Alternative names",
                "Entity activities",
            ],
        )

    def test_remove_entity_alternative_from_entity_class_mapping_with_parameter_value(self):
        root_mapping = default_import_mapping("EntityClass")
        flattened_mappings = FlattenedMappings(root_mapping)
        parameter_root = parameter_mapping_from_dict({"map_type": "ParameterValue"})
        flattened_mappings.set_parameter_components(parameter_root)
        flattened_mappings.set_import_entity_alternatives(True)
        flattened_mappings.set_import_entity_alternatives(False)
        self.assertFalse(flattened_mappings.import_entity_alternatives())
        self.assertEqual(flattened_mappings.display_parameter_type(), "Value")
        self.assertTrue(flattened_mappings.has_value_component())
        self.assertEqual(flattened_mappings.value_type_label(), "Value:")
        self.assertEqual(
            flattened_mappings.display_names,
            [
                "Entity class names",
                "Entity names",
                "Entity metadata",
                "Alternative names",
                "Parameter names",
                "Parameter value metadata",
                "Parameter values",
            ],
        )

    def test_remove_entity_alternative_and_parameter_value_from_entity_class_mapping(self):
        root_mapping = default_import_mapping("EntityClass")
        flattened_mappings = FlattenedMappings(root_mapping)
        parameter_root = parameter_mapping_from_dict({"map_type": "ParameterValue"})
        flattened_mappings.set_parameter_components(parameter_root)
        flattened_mappings.set_import_entity_alternatives(True)
        flattened_mappings.set_import_entity_alternatives(False)
        flattened_mappings.set_parameter_components(None)
        self.assertFalse(flattened_mappings.import_entity_alternatives())
        self.assertEqual(flattened_mappings.display_parameter_type(), "None")
        self.assertFalse(flattened_mappings.has_value_component())
        self.assertEqual(flattened_mappings.value_type_label(), "<no label>")
        self.assertEqual(
            flattened_mappings.display_names,
            [
                "Entity class names",
                "Entity names",
                "Entity metadata",
            ],
        )

    def test_remove_parameter_value_and_entity_alternative_from_entity_class_mapping(self):
        root_mapping = default_import_mapping("EntityClass")
        flattened_mappings = FlattenedMappings(root_mapping)
        parameter_root = parameter_mapping_from_dict({"map_type": "ParameterValue"})
        flattened_mappings.set_parameter_components(parameter_root)
        flattened_mappings.set_import_entity_alternatives(True)
        flattened_mappings.set_parameter_components(None)
        flattened_mappings.set_import_entity_alternatives(False)
        self.assertFalse(flattened_mappings.import_entity_alternatives())
        self.assertEqual(flattened_mappings.display_parameter_type(), "None")
        self.assertFalse(flattened_mappings.has_value_component())
        self.assertEqual(flattened_mappings.value_type_label(), "<no label>")
        self.assertEqual(
            flattened_mappings.display_names,
            [
                "Entity class names",
                "Entity names",
                "Entity metadata",
            ],
        )


if __name__ == "__main__":
    unittest.main()
