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
Unit tests for GdxExporter project item.

:author: A. Soininen (VTT), P. Savolainen (VTT)
:date:   4.10.2019
"""

import os
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock, NonCallableMagicMock
from PySide2.QtWidgets import QApplication
from spine_engine.project_item.project_item_resource import database_resource
from spine_items.gdx_exporter.gdx_exporter import GdxExporter
from spine_items.gdx_exporter.gdx_exporter_factory import GdxExporterFactory
from spine_items.gdx_exporter.item_info import ItemInfo
from ..mock_helpers import mock_finish_project_item_construction, create_mock_project, create_mock_toolbox


class TestGdxExporter(unittest.TestCase):
    def setUp(self):
        """Set up."""
        self.toolbox = create_mock_toolbox()
        factory = GdxExporterFactory()
        item_dict = {
            "type": "GdxExporter",
            "description": "",
            "settings_packs": list(),
            "cancel_on_error": True,
            "x": 0,
            "y": 0,
        }
        self._temp_dir = TemporaryDirectory()
        self.project = create_mock_project(self._temp_dir.name)
        self.toolbox.project.return_value = self.project
        self.exporter = factory.make_item("E", item_dict, self.toolbox, self.project)
        mock_finish_project_item_construction(factory, self.exporter, self.toolbox)

    def tearDown(self):
        self._temp_dir.cleanup()

    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def test_item_type(self):
        self.assertEqual(GdxExporter.item_type(), ItemInfo.item_type())

    def test_item_category(self):
        self.assertEqual(GdxExporter.item_category(), ItemInfo.item_category())

    def test_item_dict(self):
        """Tests Item dictionary creation."""
        d = self.exporter.item_dict()
        expected_settings_pack = {
            "settings": None,
            "indexing_settings": None,
            "merging_settings": {},
            "none_export": 0,
            "none_fallback": 0,
        }
        expected = {
            "type": "GdxExporter",
            "description": "",
            "x": 0.0,
            "y": 0.0,
            "settings_pack": expected_settings_pack,
            "databases": [],
            "output_time_stamps": True,
            "cancel_on_error": True,
        }
        self.assertEqual(d, expected)

    def test_notify_destination(self):
        self.exporter.logger.msg = MagicMock()
        self.exporter.logger.msg_warning = MagicMock()
        source_item = NonCallableMagicMock()
        source_item.name = "source name"
        source_item.item_type = MagicMock(return_value="Data Connection")
        self.exporter.notify_destination(source_item)
        self.exporter.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a "
            "<b>Data Connection</b> and a <b>GdxExporter</b> has not been implemented yet."
        )
        source_item.item_type = MagicMock(return_value="Importer")
        self.exporter.notify_destination(source_item)
        self.exporter.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a "
            "<b>Importer</b> and a <b>GdxExporter</b> has not been implemented yet."
        )
        source_item.item_type = MagicMock(return_value="Data Store")
        self.exporter.notify_destination(source_item)
        self.exporter.logger.msg.emit.assert_called_with(
            "Link established. Data Store <b>source name</b> will be "
            "exported to a .gdx file by <b>E</b> when executing."
        )
        source_item.item_type = MagicMock(return_value="Tool")
        self.exporter.notify_destination(source_item)
        self.exporter.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a "
            "<b>Tool</b> and a <b>GdxExporter</b> has not been implemented yet."
        )
        source_item.item_type = MagicMock(return_value="View")
        self.exporter.notify_destination(source_item)
        self.exporter.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a "
            "<b>View</b> and a <b>GdxExporter</b> has not been implemented yet."
        )

    def test_rename(self):
        """Tests renaming a GdxExporter."""
        self.exporter.activate()
        expected_name = "ABC"
        expected_short_name = "abc"
        self.exporter.rename(expected_name, "")
        # Check name
        self.assertEqual(expected_name, self.exporter.name)  # item name
        self.assertEqual(expected_name, self.exporter._properties_ui.item_name_label.text())  # name label in props
        self.assertEqual(expected_name, self.exporter.get_icon().name_item.text())  # name item on Design View
        # Check data_dir
        expected_data_dir = os.path.join(self.project.items_dir, expected_short_name)
        self.assertEqual(expected_data_dir, self.exporter.data_dir)  # Check data dir

    def test_activation_populates_properties_tab(self):
        self.exporter._start_worker = MagicMock()
        resources = [
            database_resource("provider", "first url to database"),
            database_resource("provider", "second url to database"),
        ]
        self.exporter.upstream_resources_updated(resources)
        self.exporter.activate()
        urls_in_properties_tab = list()
        for i in range(self.exporter._properties_ui.databases_list_layout.count()):
            database_item = self.exporter._properties_ui.databases_list_layout.itemAt(i).widget()
            urls_in_properties_tab.append(database_item.url_field.text())
        self.assertEqual(len(urls_in_properties_tab), 2)
        self.assertTrue("first url to database" in urls_in_properties_tab)
        self.assertTrue("second url to database" in urls_in_properties_tab)

    def test_activating_second_exporter_with_less_database_urls_does_not_crash(self):
        self.exporter._start_worker = MagicMock()
        item_dict = {"type": "GdxExporter", "description": "", "settings_packs": None, "x": 0, "y": 0}
        factory = GdxExporterFactory()
        exporter2 = factory.make_item("2nd exporter", item_dict, self.toolbox, self.project)
        mock_finish_project_item_construction(factory, exporter2, self.toolbox)
        exporter2._start_worker = MagicMock()
        resources = [
            database_resource("provider", "first url to database"),
            database_resource("provider", "second url to database"),
        ]
        self.exporter.upstream_resources_updated(resources)
        self.exporter.activate()
        urls_in_properties_tab = list()
        for i in range(self.exporter._properties_ui.databases_list_layout.count()):
            database_item = self.exporter._properties_ui.databases_list_layout.itemAt(i).widget()
            urls_in_properties_tab.append(database_item.url_field.text())
        self.assertEqual(len(urls_in_properties_tab), 2)
        self.assertTrue("first url to database" in urls_in_properties_tab)
        self.assertTrue("second url to database" in urls_in_properties_tab)
        resources = [database_resource("provider", "url to a database in the clouds")]
        exporter2.upstream_resources_updated(resources)
        exporter2.activate()
        self.assertEqual(exporter2._properties_ui.databases_list_layout.count(), 1)
        database_item = exporter2._properties_ui.databases_list_layout.itemAt(0).widget()
        self.assertEqual(database_item.url_field.text(), "url to a database in the clouds")


if __name__ == "__main__":
    unittest.main()
