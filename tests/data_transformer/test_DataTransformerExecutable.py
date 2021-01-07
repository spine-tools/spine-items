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
Contains unit tests for :class:`DataTransformerExecutable`.

:authors: A. Soininen (VTT)
:date:    7.1.2021
"""
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock
from spinedb_api import append_filter_config
from spine_engine.spine_engine import ExecutionDirection
from spine_engine.project_item.project_item_resource import ProjectItemResource
from spine_items.data_transformer.executable_item import ExecutableItem
from spine_items.data_transformer.data_transformer_specification import DataTransformerSpecification
from spine_items.data_transformer.settings import EntityClassRenamingSettings
from spine_items.data_transformer.filter_config_path import filter_config_path


class TestDataTransformerExecutable(unittest.TestCase):
    def test_item_type(self):
        logger = MagicMock()
        item = ExecutableItem("T", None, "", logger)
        self.assertEqual(item.item_type(), "Data Transformer")

    def test_execute(self):
        with TemporaryDirectory() as temp_dir:
            filter_file = filter_config_path(temp_dir)
            logger = MagicMock()
            item = ExecutableItem("T", None, filter_file, logger)
            provider = MagicMock()
            provider.name = "provider"
            db_resource = ProjectItemResource(provider, "database", "sqlite:///db.sqlite")
            self.assertTrue(item.execute([db_resource], []))
            expected_resource = ProjectItemResource(item, "database", "sqlite:///db.sqlite")
            self.assertEqual(item.output_resources(ExecutionDirection.FORWARD), [expected_resource])

    def test_skip_execution(self):
        with TemporaryDirectory() as temp_dir:
            filter_file = filter_config_path(temp_dir)
            logger = MagicMock()
            item = ExecutableItem("T", None, filter_file, logger)
            provider = MagicMock()
            provider.name = "provider"
            db_resource = ProjectItemResource(provider, "database", "sqlite:///db.sqlite")
            item.skip_execution([db_resource], [])
            expected_resource = ProjectItemResource(item, "database", "sqlite:///db.sqlite")
            self.assertEqual(item.output_resources(ExecutionDirection.FORWARD), [expected_resource])

    def test_execute_with_specification(self):
        with TemporaryDirectory() as temp_dir:
            settings = EntityClassRenamingSettings({})
            specification = DataTransformerSpecification("specification", settings, "test specification")
            filter_file = filter_config_path(temp_dir)
            logger = MagicMock()
            transformer = ExecutableItem("T", specification, filter_file, logger)
            provider = MagicMock()
            provider.name = "provider"
            db_resource = ProjectItemResource(provider, "database", "sqlite:///db.sqlite")
            self.assertTrue(transformer.execute([db_resource], []))
            filter_url = append_filter_config("sqlite:///db.sqlite", filter_file)
            expected_resource = ProjectItemResource(transformer, "database", filter_url)
            self.assertEqual(transformer.output_resources(ExecutionDirection.FORWARD), [expected_resource])

    def test_skip_execution_with_specification(self):
        with TemporaryDirectory() as temp_dir:
            settings = EntityClassRenamingSettings({})
            specification = DataTransformerSpecification("specification", settings, "test specification")
            filter_file = filter_config_path(temp_dir)
            logger = MagicMock()
            transformer = ExecutableItem("T", specification, filter_file, logger)
            provider = MagicMock()
            provider.name = "provider"
            db_resource = ProjectItemResource(provider, "database", "sqlite:///db.sqlite")
            transformer.skip_execution([db_resource], [])
            filter_url = append_filter_config("sqlite:///db.sqlite", filter_file)
            expected_resource = ProjectItemResource(transformer, "database", filter_url)
            self.assertEqual(transformer.output_resources(ExecutionDirection.FORWARD), [expected_resource])


if __name__ == '__main__':
    unittest.main()
