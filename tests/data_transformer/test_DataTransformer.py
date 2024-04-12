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

"""Contains unit tests for :class:`DataTransformer`."""
import os.path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock, NonCallableMagicMock
from PySide6.QtWidgets import QApplication
from spinedb_api import append_filter_config
from spine_engine.project_item.project_item_resource import database_resource
from spine_items.data_transformer.data_transformer import DataTransformer
from spine_items.data_transformer.data_transformer_factory import DataTransformerFactory
from spine_items.data_transformer.data_transformer_specification import DataTransformerSpecification
from spine_items.data_transformer.filter_config_path import filter_config_path
from spine_items.data_transformer.item_info import ItemInfo
from spine_items.data_transformer.settings import EntityClassRenamingSettings
from ..mock_helpers import mock_finish_project_item_construction, create_mock_project, create_mock_toolbox


class TestDataTransformer(unittest.TestCase):
    def setUp(self):
        """Set up."""
        self.toolbox = create_mock_toolbox()
        factory = DataTransformerFactory()
        item_dict = {"type": "Data Transformer", "description": "", "specification": None, "x": 0, "y": 0}
        self._temp_dir = TemporaryDirectory()
        self.project = create_mock_project(self._temp_dir.name)
        self.toolbox.project.return_value = self.project
        self.transformer = factory.make_item("T", item_dict, self.toolbox, self.project)
        self._properties_widget = mock_finish_project_item_construction(factory, self.transformer, self.toolbox)

    def tearDown(self):
        self._temp_dir.cleanup()

    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def test_item_type(self):
        self.assertEqual(DataTransformer.item_type(), ItemInfo.item_type())

    def test_item_dict(self):
        """Tests Item dictionary creation."""
        d = self.transformer.item_dict()
        self.assertEqual(d, {"description": "", "type": "Data Transformer", "x": 0.0, "y": 0.0, "specification": ""})

    def test_notify_destination(self):
        self.transformer.logger.msg = MagicMock()
        self.transformer.logger.msg_warning = MagicMock()
        source_item = NonCallableMagicMock()
        source_item.name = "source name"
        source_item.item_type = MagicMock(return_value="Data Store")
        self.transformer.notify_destination(source_item)
        self.transformer.logger.msg.emit.assert_called_with(
            "Link established. You can now define transformations for Data Store "
            "<b>source name</b> in Data Transformer <b>T</b>."
        )

        source_item.item_type = MagicMock(return_value="Data Transformer")
        self.transformer.notify_destination(source_item)
        self.transformer.logger.msg.emit.assert_called_with(
            "Link established. You can now define additional transformations in Data Transformer <b>T</b>."
        )
        source_item.item_type = MagicMock(return_value="Data Connection")
        self.transformer.notify_destination(source_item)
        self.transformer.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a "
            f"<b>{source_item.item_type()}</b> and a <b>{self.transformer.item_type()}</b> has not been "
            "implemented yet."
        )

    def test_resources_for_direct_successors(self):
        self.assertEqual(self.transformer.resources_for_direct_successors(), [])
        provider = MagicMock()
        provider.name = "resource provider"
        db_resource = database_resource(provider.name, "sqlite:///database.sqlite")
        self.transformer.upstream_resources_updated([db_resource])
        expected_resource = database_resource(self.transformer.name, "sqlite:///database.sqlite")
        self.assertEqual(self.transformer.resources_for_direct_successors(), [expected_resource])
        settings = EntityClassRenamingSettings({})
        specification = DataTransformerSpecification("specification", settings, "test specification")
        self.transformer.do_set_specification(specification)
        config_path = filter_config_path(self.transformer.data_dir)
        filter_url = append_filter_config("sqlite:///database.sqlite", config_path)
        expected_resource = database_resource(self.transformer.name, filter_url)
        self.assertEqual(self.transformer.resources_for_direct_successors(), [expected_resource])

    def test_rename(self):
        """Tests renaming a DT."""
        self.transformer.activate()
        expected_name = "ABC"
        expected_short_name = "abc"
        self.transformer.rename(expected_name, "")
        self.assertEqual(expected_name, self.transformer.name)
        self.assertEqual(expected_name, self.transformer.get_icon().name())
        expected_data_dir = os.path.join(self.project.items_dir, expected_short_name)
        self.assertEqual(expected_data_dir, self.transformer.data_dir)


if __name__ == "__main__":
    unittest.main()
