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
Unit tests for View project item.

:author: A. Soininen (VTT), P. Savolainen (VTT)
:date:   4.10.2019
"""

import os
import unittest
from unittest.mock import MagicMock, NonCallableMagicMock
from PySide2.QtWidgets import QApplication
import spine_items.resources_icons_rc  # pylint: disable=unused-import
from spine_items.view.item_info import ItemInfo
from spine_items.view.view import View
from spine_items.view.view_factory import ViewFactory
from spine_items.view.executable_item import ExecutableItem
from ..mock_helpers import mock_finish_project_item_construction, create_mock_project, create_mock_toolbox


class TestView(unittest.TestCase):
    def setUp(self):
        """Set up."""
        self.toolbox = create_mock_toolbox()
        factory = ViewFactory()
        item_dict = {"type": "View", "description": "", "x": 0, "y": 0}
        self.project = create_mock_project()
        self.view = factory.make_item("V", item_dict, self.toolbox, self.project, self.toolbox)
        mock_finish_project_item_construction(factory, self.view, self.toolbox)

    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def test_item_type(self):
        self.assertEqual(View.item_type(), ItemInfo.item_type())

    def test_item_category(self):
        self.assertEqual(View.item_category(), ItemInfo.item_category())

    def test_execution_item(self):
        """Tests that the ExecutableItem counterpart is created successfully."""
        exec_item = self.view.execution_item()
        self.assertIsInstance(exec_item, ExecutableItem)

    def test_item_dict(self):
        """Tests Item dictionary creation."""
        d = self.view.item_dict()
        a = ["type", "description", "x", "y"]
        for k in a:
            self.assertTrue(k in d, f"Key '{k}' not in dict {d}")

    def test_notify_destination(self):
        source_item = NonCallableMagicMock()
        source_item.name = "source name"
        source_item.item_type = MagicMock(return_value="Data Connection")
        self.view.notify_destination(source_item)
        self.toolbox.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a <b>Data Connection</b> and"
            " a <b>View</b> has not been implemented yet."
        )
        source_item.item_type = MagicMock(return_value="Importer")
        self.view.notify_destination(source_item)
        self.toolbox.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a <b>Importer</b> and a <b>View</b> has not been implemented yet."
        )
        source_item.item_type = MagicMock(return_value="Data Store")
        self.view.notify_destination(source_item)
        self.toolbox.msg.emit.assert_called_with(
            "Link established. You can visualize Data Store <b>source name</b> in View <b>V</b>."
        )
        source_item.item_type = MagicMock(return_value="GdxExporter")
        self.view.notify_destination(source_item)
        self.toolbox.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a <b>GdxExporter</b> and a <b>View</b> has not been implemented yet."
        )
        source_item.item_type = MagicMock(return_value="Tool")
        self.view.notify_destination(source_item)
        self.toolbox.msg.emit.assert_called_with(
            "Link established. You can visualize the output from Tool <b>source name</b> in View <b>V</b>."
        )

    def test_rename(self):
        """Tests renaming a View."""
        self.view.activate()
        expected_name = "ABC"
        expected_short_name = "abc"
        ret_val = self.view.rename(expected_name)  # Do rename
        self.assertTrue(ret_val)
        # Check name
        self.assertEqual(expected_name, self.view.name)  # item name
        self.assertEqual(expected_name, self.view._properties_ui.label_view_name.text())  # name label in props
        self.assertEqual(expected_name, self.view.get_icon().name_item.text())  # name item on Design View
        # Check data_dir
        expected_data_dir = os.path.join(self.project.items_dir, expected_short_name)
        self.assertEqual(expected_data_dir, self.view.data_dir)  # Check data dir


if __name__ == "__main__":
    unittest.main()
