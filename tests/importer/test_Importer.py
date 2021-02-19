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
Unit tests for Importer project item.

:author: A. Soininen (VTT), P. Savolainen (VTT)
:date:   4.10.2019
"""
import collections
import os
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock, NonCallableMagicMock
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QMenu
from spine_items.importer.importer import Importer
from spine_items.importer.importer_factory import ImporterFactory
from spine_items.importer.executable_item import ExecutableItem
from spine_items.importer.item_info import ItemInfo
from spine_engine.project_item.project_item_resource import ProjectItemResource
from ..mock_helpers import mock_finish_project_item_construction, create_mock_project, create_mock_toolbox


class TestImporter(unittest.TestCase):
    def setUp(self):
        """Set up."""
        self.toolbox = create_mock_toolbox()
        mock_spec_model = self.toolbox.specification_model = MagicMock()
        Specification = collections.namedtuple('Specification', 'name mapping item_type')
        mock_spec_model.find_specification.side_effect = lambda x: Specification(
            name=x, mapping={}, item_type="Importer"
        )
        factory = ImporterFactory()
        item_dict = {
            "type": "Importer",
            "description": "",
            "specification": "importer_spec",
            "cancel_on_error": True,
            "file_selection": list(),
            "x": 0,
            "y": 0,
        }
        self._temp_dir = TemporaryDirectory()
        self.project = create_mock_project(self._temp_dir.name)
        self.toolbox.project.return_value = self.project
        self.importer = factory.make_item("I", item_dict, self.toolbox, self.project)
        mock_finish_project_item_construction(factory, self.importer, self.toolbox)

    def tearDown(self):
        self._temp_dir.cleanup()

    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def test_item_type(self):
        self.assertEqual(Importer.item_type(), ItemInfo.item_type())

    def test_item_category(self):
        self.assertEqual(Importer.item_category(), ItemInfo.item_category())

    def test_execution_item(self):
        """Tests that the ExecutableItem counterpart is created successfully."""
        exec_item = self.importer.execution_item()
        self.assertIsInstance(exec_item, ExecutableItem)

    def test_item_dict(self):
        """Tests Item dictionary creation."""
        d = self.importer.item_dict()
        a = ["type", "description", "x", "y", "specification", "cancel_on_error", "file_selection"]
        for k in a:
            self.assertTrue(k in d, f"Key '{k}' not in dict {d}")

    def test_notify_destination(self):
        self.importer.logger.msg = MagicMock()
        self.importer.logger.msg_warning = MagicMock()
        source_item = NonCallableMagicMock()
        source_item.name = "source name"
        source_item.item_type = MagicMock(return_value="Data Connection")
        self.importer.notify_destination(source_item)
        self.importer.logger.msg.emit.assert_called_with(
            "Link established. You can define mappings on data from <b>source name</b> using item <b>I</b>."
        )
        source_item.item_type = MagicMock(return_value="Data Store")
        self.importer.notify_destination(source_item)
        self.importer.logger.msg.emit.assert_called_with("Link established")
        source_item.item_type = MagicMock(return_value="GdxExporter")
        self.importer.notify_destination(source_item)
        self.importer.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a "
            "<b>GdxExporter</b> and a <b>Importer</b> has not been implemented yet."
        )
        source_item.item_type = MagicMock(return_value="Tool")
        self.importer.notify_destination(source_item)
        self.importer.logger.msg.emit.assert_called_with(
            "Link established." " You can define mappings on output files from <b>source name</b> using item <b>I</b>."
        )
        source_item.item_type = MagicMock(return_value="View")
        self.importer.notify_destination(source_item)
        self.importer.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a " "<b>View</b> and a <b>Importer</b> has not been implemented yet."
        )

    def test_rename(self):
        """Tests renaming an Importer."""
        with unittest.mock.patch("spine_items.importer.importer.ItemSpecificationMenu") as mock_spec_menu:
            mock_spec_menu.return_value = QMenu()
            self.importer.activate()
        expected_name = "ABC"
        expected_short_name = "abc"
        self.importer.rename(expected_name, "")
        # Check name
        self.assertEqual(expected_name, self.importer.name)  # item name
        self.assertEqual(expected_name, self.importer._properties_ui.label_name.text())  # name label in props
        self.assertEqual(expected_name, self.importer.get_icon().name_item.text())  # name item on Design View
        # Check data_dir
        expected_data_dir = os.path.join(self.project.items_dir, expected_short_name)
        self.assertEqual(expected_data_dir, self.importer.data_dir)  # Check data dir

    def test_handle_dag_changed(self):
        """Tests that upstream resource files are listed in the Importer view."""
        with unittest.mock.patch("spine_items.importer.importer.ItemSpecificationMenu") as mock_spec_menu:
            mock_spec_menu.return_value = QMenu()
            self.importer.activate()
        item = NonCallableMagicMock()
        expected_file_list = ["url1", "url2"]
        resources = [ProjectItemResource(item, "file", url) for url in expected_file_list]
        rank = 0
        self.importer.handle_dag_changed(rank, resources, [])
        model = self.importer._properties_ui.treeView_files.model()
        file_list = [model.index(row, 0).data(Qt.DisplayRole) for row in range(model.rowCount())]
        self.assertEqual(sorted(file_list), sorted(expected_file_list))
        checked = [model.index(row, 0).data(Qt.CheckStateRole) for row in range(model.rowCount())]
        selected = [check == Qt.Checked for check in checked]
        self.assertTrue(all(selected))

    def test_handle_dag_changed_updates_previous_list_items(self):
        with unittest.mock.patch("spine_items.importer.importer.ItemSpecificationMenu") as mock_spec_menu:
            mock_spec_menu.return_value = QMenu()
            self.importer.activate()
        item = NonCallableMagicMock()
        resources = [ProjectItemResource(item, "file", url) for url in ["url1", "url2"]]
        rank = 0
        # Add initial files
        self.importer.handle_dag_changed(rank, resources, [])
        model = self.importer._properties_ui.treeView_files.model()
        for row in range(2):
            index = model.index(row, 0)
            model.setData(index, Qt.Unchecked, Qt.CheckStateRole)
        # Update with one existing, one new file
        resources = [ProjectItemResource(item, "file", url) for url in ["url2", "url3"]]
        self.importer.handle_dag_changed(rank, resources, [])
        file_list = [model.index(row, 0).data(Qt.DisplayRole) for row in range(model.rowCount())]
        self.assertEqual(file_list, ["url2", "url3"])
        checked = [model.index(row, 0).data(Qt.CheckStateRole) for row in range(model.rowCount())]
        selected = [check == Qt.Checked for check in checked]
        self.assertEqual(selected, [False, True])


if __name__ == "__main__":
    unittest.main()
