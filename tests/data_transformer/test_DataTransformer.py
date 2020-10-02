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
Contains unit tests for :class:`DataTransformer`.

:authors: A. Soininen (VTT)
:date:    9.10.2020
"""
import os.path
import unittest
from unittest.mock import MagicMock, NonCallableMagicMock
from PySide2.QtWidgets import QApplication
from spine_items.data_transformer.data_transformer import DataTransformer
from spine_items.data_transformer.data_transformer_factory import DataTransformerFactory
from spine_items.data_transformer.executable_item import ExecutableItem
from spine_items.data_transformer.item_info import ItemInfo
from ..mock_helpers import mock_finish_project_item_construction, create_mock_project, create_mock_toolbox


class TestDataTransformer(unittest.TestCase):
    def setUp(self):
        """Set up."""
        self.toolbox = create_mock_toolbox()
        factory = DataTransformerFactory()
        item_dict = {"type": "Data Transformer", "description": "", "specification": None, "x": 0, "y": 0}
        self.project = create_mock_project()
        self.transformer = factory.make_item("T", item_dict, self.toolbox, self.project, self.toolbox)
        mock_finish_project_item_construction(factory, self.transformer, self.toolbox)

    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def test_item_type(self):
        self.assertEqual(DataTransformer.item_type(), ItemInfo.item_type())

    def test_item_category(self):
        self.assertEqual(DataTransformer.item_category(), ItemInfo.item_category())

    def test_execution_item(self):
        """Tests that the ExecutableItem counterpart is created successfully."""
        exec_item = self.transformer.execution_item()
        self.assertIsInstance(exec_item, ExecutableItem)

    def test_item_dict(self):
        """Tests Item dictionary creation."""
        d = self.transformer.item_dict()
        self.assertEqual(d, {"description": "", "type": "Data Transformer", "x": 0.0, "y": 0.0, "specification": None})

    def test_notify_destination(self):
        source_item = NonCallableMagicMock()
        source_item.name = "source name"
        source_item.item_type = MagicMock(return_value="Data Store")
        self.transformer.notify_destination(source_item)
        self.toolbox.msg.emit.assert_called_with(
            "Link established. You can now define transformations for Data Store "
            "<b>source name</b> in Data Transformer <b>T</b>."
        )

        source_item.item_type = MagicMock(return_value="Data Transformer")
        self.transformer.notify_destination(source_item)
        self.toolbox.msg.emit.assert_called_with(
            "Link established. You can now define additional transformations in Data Transformer <b>T</b>."
        )
        source_item.item_type = MagicMock(return_value="Data Connection")
        self.transformer.notify_destination(source_item)
        self.toolbox.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a "
            f"<b>{source_item.item_type()}</b> and a <b>{self.transformer.item_type()}</b> has not been "
            "implemented yet."
        )

    def test_rename(self):
        """Tests renaming a Gimlet."""
        self.transformer.activate()
        expected_name = "ABC"
        expected_short_name = "abc"
        ret_val = self.transformer.rename(expected_name)
        self.assertTrue(ret_val)
        self.assertEqual(expected_name, self.transformer.name)
        self.assertEqual(expected_name, self.transformer._properties_ui.item_name_label.text())
        self.assertEqual(expected_name, self.transformer.get_icon().name_item.text())
        expected_data_dir = os.path.join(self.project.items_dir, expected_short_name)
        self.assertEqual(expected_data_dir, self.transformer.data_dir)


if __name__ == "__main__":
    unittest.main()
