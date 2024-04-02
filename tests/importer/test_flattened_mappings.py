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
from spinedb_api import import_mapping_from_dict
from spine_items.importer.flattened_mappings import FlattenedMappings


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


if __name__ == "__main__":
    unittest.main()
