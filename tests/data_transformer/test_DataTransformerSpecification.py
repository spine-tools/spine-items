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

"""Unit tests for Data transformer's :class:`DataTransformerSpecification`."""
import unittest
from spine_items.data_transformer.data_transformer_specification import DataTransformerSpecification
from spine_items.data_transformer.settings import EntityClassRenamingSettings


class TestDataTransformerSpecification(unittest.TestCase):
    def test_is_equivalent(self):
        dts1 = DataTransformerSpecification("DT SPEC")
        dts2 = DataTransformerSpecification("DT SPEC")
        self.assertTrue(dts1.is_equivalent(dts2))

    def test_to_dict(self):
        dts = DataTransformerSpecification("DT SPEC")
        dts_dict = dts.to_dict()
        self.assertEqual(4, len(dts_dict.keys()))
        self.assertEqual("DT SPEC", dts_dict["name"])
        self.assertEqual("Data Transformer", dts_dict["item_type"])
        self.assertIsNone(dts_dict["description"])
        self.assertIsNone(dts_dict["filter"])

    def test_from_dict(self):
        dts_dict = DataTransformerSpecification("DT SPEC").to_dict()
        dts = DataTransformerSpecification.from_dict(dts_dict, None)
        self.assertTrue(isinstance(dts, DataTransformerSpecification))
        # Make one with Settings
        rename_map = {"a": "b"}
        settings = EntityClassRenamingSettings(rename_map)
        dts2 = DataTransformerSpecification("DT WITH SETTINGS", settings=settings)
        dts2_dict = dts2.to_dict()
        dts2_reloaded = DataTransformerSpecification.from_dict(dts2_dict, None)
        self.assertTrue(isinstance(dts2_reloaded, DataTransformerSpecification))


if __name__ == "__main__":
    unittest.main()
