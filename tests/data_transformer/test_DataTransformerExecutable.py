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

"""Contains unit tests for :class:`DataTransformerExecutable`."""
from multiprocessing import Lock
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock
from spinedb_api import append_filter_config
from spine_engine.utils.helpers import ExecutionDirection
from spine_engine.project_item.project_item_resource import database_resource
from spine_items.data_transformer.executable_item import ExecutableItem
from spine_items.data_transformer.data_transformer_specification import DataTransformerSpecification
from spine_items.data_transformer.settings import EntityClassRenamingSettings


class TestDataTransformerExecutable(unittest.TestCase):
    def setUp(self):
        self._temp_dir = TemporaryDirectory()

    def tearDown(self):
        self._temp_dir.cleanup()

    def test_item_type(self):
        logger = MagicMock()
        item = ExecutableItem("T", None, self._temp_dir.name, logger)
        self.assertEqual(item.item_type(), "Data Transformer")

    def test_execute(self):
        logger = MagicMock()
        item = ExecutableItem("T", None, self._temp_dir.name, logger)
        db_resource = database_resource("provider", "sqlite:///db.sqlite")
        self.assertTrue(item.execute([db_resource], [], Lock()))
        expected_resource = database_resource(item.name, "sqlite:///db.sqlite")
        self.assertEqual(item.output_resources(ExecutionDirection.FORWARD), [expected_resource])

    def test_skip_execution(self):
        logger = MagicMock()
        item = ExecutableItem("T", None, self._temp_dir.name, logger)
        db_resource = database_resource("provider", "sqlite:///db.sqlite")
        item.exclude_execution([db_resource], [], Lock())
        expected_resource = database_resource(item.name, "sqlite:///db.sqlite")
        self.assertEqual(item.output_resources(ExecutionDirection.FORWARD), [expected_resource])

    def test_execute_with_specification(self):
        settings = EntityClassRenamingSettings({})
        specification = DataTransformerSpecification("specification", settings, "test specification")
        logger = MagicMock()
        transformer = ExecutableItem("T", specification, self._temp_dir.name, logger)
        db_resource = database_resource("provider", "sqlite:///db.sqlite")
        self.assertTrue(transformer.execute([db_resource], [], Lock()))
        filter_url = append_filter_config("sqlite:///db.sqlite", transformer._filter_config_path)
        expected_resource = database_resource(transformer.name, filter_url)
        self.assertEqual(transformer.output_resources(ExecutionDirection.FORWARD), [expected_resource])

    def test_skip_execution_with_specification(self):
        settings = EntityClassRenamingSettings({})
        specification = DataTransformerSpecification("specification", settings, "test specification")
        logger = MagicMock()
        transformer = ExecutableItem("T", specification, self._temp_dir.name, logger)
        db_resource = database_resource("provider", "sqlite:///db.sqlite")
        transformer.exclude_execution([db_resource], [], Lock())
        filter_url = append_filter_config("sqlite:///db.sqlite", transformer._filter_config_path)
        expected_resource = database_resource(transformer.name, filter_url)
        self.assertEqual(transformer.output_resources(ExecutionDirection.FORWARD), [expected_resource])


if __name__ == "__main__":
    unittest.main()
