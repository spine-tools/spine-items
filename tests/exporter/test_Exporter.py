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
Unit tests for Exporter project item.

:author: A. Soininen (VTT)
:date:   1.4.2021
"""
import os.path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock, NonCallableMagicMock
from PySide6.QtWidgets import QApplication
from spine_engine.utils.helpers import shorten
from spine_engine.project_item.project_item_resource import database_resource
from spine_items.exporter.exporter import Exporter
from spine_items.exporter.exporter_factory import ExporterFactory
from spine_items.exporter.item_info import ItemInfo
from spine_items.exporter.specification import Specification
from ..mock_helpers import mock_finish_project_item_construction, create_mock_project, create_mock_toolbox


class TestExporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        """Set up."""
        self._toolbox = create_mock_toolbox()
        mock_spec_model = self._toolbox.specification_model = MagicMock()
        mock_spec_model.find_specification.side_effect = lambda name: Specification(name, "spec description")
        factory = ExporterFactory()
        item_dict = {
            "type": "Exporter",
            "description": "item description",
            "specification": "exporter_spec",
            "cancel_on_error": True,
            "x": 0,
            "y": 0,
        }
        self._temp_dir = TemporaryDirectory()
        self._project = create_mock_project(self._temp_dir.name)
        self._toolbox.project.return_value = self._project
        self._exporter = factory.make_item("exporter", item_dict, self._toolbox, self._project)
        self._properties_widget = mock_finish_project_item_construction(factory, self._exporter, self._toolbox)

    def tearDown(self):
        self._temp_dir.cleanup()

    def test_item_type(self):
        self.assertEqual(Exporter.item_type(), ItemInfo.item_type())

    def test_item_category(self):
        self.assertEqual(Exporter.item_category(), ItemInfo.item_category())

    def test_serialization(self):
        item_dict = self._exporter.item_dict()
        deserialized = Exporter.from_dict("new exporter", item_dict, self._toolbox, self._project)
        self.assertEqual(deserialized.name, "new exporter")
        self.assertEqual(deserialized.description, "item description")

    def test_notify_destination(self):
        self._exporter._toolbox.msg = MagicMock()
        self._exporter._toolbox.msg_warning = MagicMock()
        source_item = NonCallableMagicMock()
        source_item.name = "source name"
        source_item.item_type = MagicMock(return_value="Data Connection")
        self._exporter.notify_destination(source_item)
        self._exporter.logger.msg_warning.emit.assert_called_with(
            'Link established. Interaction between a <b>Data Connection</b> and a <b>Exporter</b> has not been implemented yet.'
        )
        source_item.item_type = MagicMock(return_value="Data Store")
        self._exporter.notify_destination(source_item)
        self._exporter._toolbox.msg.emit.assert_called_with(
            "Link established. You can now export the database in <b>source name</b> in <b>exporter</b>."
        )
        source_item.item_type = MagicMock(return_value="Data Transformer")
        self._exporter.notify_destination(source_item)
        self._exporter._toolbox.msg.emit.assert_called_with(
            "Link established. You can now export the database transformed by <b>source name</b> in <b>exporter</b>."
        )
        source_item.item_type = MagicMock(return_value="Exporter")
        self._exporter.notify_destination(source_item)
        self._exporter.logger.msg_warning.emit.assert_called_with(
            'Link established. Interaction between a <b>Exporter</b> and a <b>Exporter</b> has not been implemented yet.'
        )
        source_item.item_type = MagicMock(return_value="GdxExporter")
        self._exporter.notify_destination(source_item)
        source_item.item_type = MagicMock(return_value="Gimlet")
        self._exporter.notify_destination(source_item)
        self._exporter.logger.msg_warning.emit.assert_called_with(
            'Link established. Interaction between a <b>Gimlet</b> and a <b>Exporter</b> has not been implemented yet.'
        )
        source_item.item_type = MagicMock(return_value="Importer")
        self._exporter.notify_destination(source_item)
        self._exporter.logger.msg_warning.emit.assert_called_with(
            'Link established. Interaction between a <b>Importer</b> and a <b>Exporter</b> has not been implemented yet.'
        )
        source_item.item_type = MagicMock(return_value="Tool")
        self._exporter.notify_destination(source_item)
        self._exporter.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a <b>Tool</b> and a <b>Exporter</b> has not been implemented yet."
        )
        source_item.item_type = MagicMock(return_value="View")
        self._exporter.notify_destination(source_item)
        self._exporter.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a " "<b>View</b> and a <b>Exporter</b> has not been implemented yet."
        )

    def test_rename(self):
        """Tests renaming an Importer."""
        self._exporter.activate()
        expected_name = "ABC"
        expected_short_name = shorten(expected_name)
        self.assertTrue(self._exporter.rename(expected_name, ""))
        self.assertEqual(expected_name, self._exporter.name)
        self.assertEqual(expected_name, self._exporter.get_icon().name_item.text())
        expected_data_dir = os.path.join(self._project.items_dir, expected_short_name)
        self.assertEqual(expected_data_dir, self._exporter.data_dir)

    def test_upstream_resources_updated(self):
        self._exporter.activate()
        expected_out_labels = ["db_url@Data Store 1", "db_url@Data Store 2"]
        resources = [database_resource("provider", url) for url in expected_out_labels]
        self._exporter.upstream_resources_updated(resources)
        model = self._exporter.full_url_model()
        self.assertEqual(model.rowCount(), len(expected_out_labels))
        self.assertIn(model.index(0, 0).data(), expected_out_labels)
        self.assertIn(model.index(1, 0).data(), expected_out_labels)
        self.assertEqual(self._exporter._properties_ui.outputs_list_layout.count(), len(expected_out_labels))


if __name__ == "__main__":
    unittest.main()
