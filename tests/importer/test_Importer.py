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

"""Unit tests for Importer project item."""
import collections
import os
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock, NonCallableMagicMock
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMenu
from spine_items.importer.importer import Importer
from spine_items.importer.importer_factory import ImporterFactory
from spine_items.importer.importer_specification import ImporterSpecification
from spine_items.importer.item_info import ItemInfo
from spine_engine.project_item.project_item_resource import file_resource, transient_file_resource
from ..mock_helpers import mock_finish_project_item_construction, create_mock_project, create_mock_toolbox


class TestImporter(unittest.TestCase):
    def setUp(self):
        """Set up."""
        self.toolbox = create_mock_toolbox()
        mock_spec_model = self.toolbox.specification_model = MagicMock()
        Specification = collections.namedtuple("Specification", "name mapping item_type")
        mock_spec_model.find_specification.side_effect = lambda x: Specification(
            name=x, mapping={}, item_type="Importer"
        )
        factory = ImporterFactory()
        item_dict = {
            "type": "Importer",
            "description": "Very best test importer",
            "specification": "importer_spec",
            "cancel_on_error": True,
            "file_selection": [["file 99", True], ["file 01", False]],
            "x": 0,
            "y": 0,
        }
        self._temp_dir = TemporaryDirectory()
        self.project = create_mock_project(self._temp_dir.name)
        self.toolbox.project.return_value = self.project
        self.importer = factory.make_item("I", item_dict, self.toolbox, self.project)
        self._properties_widget = mock_finish_project_item_construction(factory, self.importer, self.toolbox)

    def tearDown(self):
        self._temp_dir.cleanup()

    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def test_item_type(self):
        self.assertEqual(Importer.item_type(), ItemInfo.item_type())

    def test_item_dict(self):
        """Tests Item dictionary creation."""
        specification = ImporterSpecification("import specification", {})
        self.importer.do_set_specification(specification)
        resources = [
            file_resource("source 1", "/path/file1.dat", "<source 1>/file1.dat"),
            file_resource("source 2", "/path/file2.dat", "<source 2>/file2.dat"),
        ]
        self.importer.upstream_resources_updated(resources)
        index = self.importer._file_model.index(1, 0)
        self.importer._file_model.setData(index, False, Qt.ItemDataRole.CheckStateRole)
        d = self.importer.item_dict()
        self.assertEqual(
            d,
            {
                "cancel_on_error": True,
                "description": "Very best test importer",
                "file_selection": [["<source 1>/file1.dat", True], ["<source 2>/file2.dat", False]],
                "on_conflict": "merge",
                "specification": "import specification",
                "type": "Importer",
                "x": 0.0,
                "y": 0.0,
            },
        )

    def test_notify_destination(self):
        self.importer.logger.msg = MagicMock()
        self.importer.logger.msg_warning = MagicMock()
        source_item = NonCallableMagicMock()
        source_item.name = "source name"
        source_item.item_type = MagicMock(return_value="Data Connection")
        self.importer.notify_destination(source_item)
        self.importer.logger.msg.emit.assert_called_with(
            "Link established. You can define mappings on data from <b>source name</b> using <b>I</b>."
        )
        source_item.item_type = MagicMock(return_value="Data Store")
        self.importer.notify_destination(source_item)
        self.importer.logger.msg.emit.assert_called_with("Link established")
        source_item.item_type = MagicMock(return_value="Data Transformer")
        self.importer.notify_destination(source_item)
        self.importer.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a "
            "<b>Data Transformer</b> and a <b>Importer</b> has not been implemented yet."
        )
        source_item.item_type = MagicMock(return_value="Exporter")
        self.importer.notify_destination(source_item)
        self.importer.logger.msg.emit.assert_called_with(
            "Link established. You can define mappings on data from <b>source name</b> using <b>I</b>."
        )
        source_item.item_type = MagicMock(return_value="Tool")
        self.importer.notify_destination(source_item)
        self.importer.logger.msg.emit.assert_called_with(
            "Link established. You can define mappings on data from <b>source name</b> using <b>I</b>."
        )
        source_item.item_type = MagicMock(return_value="View")
        self.importer.notify_destination(source_item)
        self.importer.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a <b>View</b> and a <b>Importer</b> has not been implemented yet."
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
        self.assertEqual(expected_name, self.importer.get_icon().name())  # name item on Design View
        # Check data_dir
        expected_data_dir = os.path.join(self.project.items_dir, expected_short_name)
        self.assertEqual(expected_data_dir, self.importer.data_dir)  # Check data dir

    def test_handle_dag_changed(self):
        """Tests that upstream resource files are listed in the Importer view."""
        with unittest.mock.patch("spine_items.importer.importer.ItemSpecificationMenu") as mock_spec_menu:
            mock_spec_menu.return_value = QMenu()
            self.importer.activate()
        expected_file_list = ["file1", "file2"]
        resources = [transient_file_resource("provider", label=file_name) for file_name in expected_file_list]
        self.importer.upstream_resources_updated(resources)
        model = self.importer._properties_ui.treeView_files.model()
        file_list = [model.index(row, 0).data(Qt.ItemDataRole.DisplayRole) for row in range(model.rowCount())]
        self.assertEqual(sorted(file_list), sorted(expected_file_list))
        checked = [model.index(row, 0).data(Qt.ItemDataRole.CheckStateRole).value for row in range(model.rowCount())]
        selected = [check == Qt.CheckState.Checked.value for check in checked]
        self.assertTrue(all(selected))

    def test_handle_dag_changed_updates_previous_list_items(self):
        with unittest.mock.patch("spine_items.importer.importer.ItemSpecificationMenu") as mock_spec_menu:
            mock_spec_menu.return_value = QMenu()
            self.importer.activate()
        resources = [transient_file_resource("provider", label=name) for name in ["file1", "file2"]]
        # Add initial files
        self.importer.upstream_resources_updated(resources)
        model = self.importer._properties_ui.treeView_files.model()
        for row in range(2):
            index = model.index(row, 0)
            model.setData(index, Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
        # Update with one existing, one new file
        resources = [transient_file_resource("provider", label=name) for name in ["file2", "file3"]]
        self.importer.upstream_resources_updated(resources)
        file_list = [model.index(row, 0).data(Qt.ItemDataRole.DisplayRole) for row in range(model.rowCount())]
        self.assertEqual(file_list, ["file2", "file3"])
        checked = [model.index(row, 0).data(Qt.ItemDataRole.CheckStateRole).value for row in range(model.rowCount())]
        selected = [check == Qt.CheckState.Checked.value for check in checked]
        self.assertEqual(selected, [False, True])


if __name__ == "__main__":
    unittest.main()
