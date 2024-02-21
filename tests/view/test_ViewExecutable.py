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

"""Unit tests for ViewExecutable."""
from multiprocessing import Lock
from tempfile import TemporaryDirectory
import unittest
from unittest import mock
from spine_engine import ExecutionDirection
from spine_items.view.executable_item import ExecutableItem


class TestViewExecutable(unittest.TestCase):
    def setUp(self):
        self._temp_dir = TemporaryDirectory()

    def tearDown(self):
        self._temp_dir.cleanup()

    def test_item_type(self):
        self.assertEqual(ExecutableItem.item_type(), "View")

    def test_from_dict(self):
        logger = mock.MagicMock()
        item_dict = {"type": "View", "description": "", "x": 0, "y": 0}
        item = ExecutableItem.from_dict(item_dict, "Viewer", self._temp_dir.name, None, dict(), logger)
        self.assertIsInstance(item, ExecutableItem)
        self.assertEqual("View", item.item_type())

    def test_stop_execution(self):
        executable = ExecutableItem(name="Viewer", project_dir=self._temp_dir.name, logger=mock.MagicMock())
        with mock.patch(
            "spine_engine.project_item.executable_item_base.ExecutableItemBase.stop_execution"
        ) as mock_stop_execution:
            executable.stop_execution()
            mock_stop_execution.assert_called_once()

    def test_execute_backward(self):
        executable = ExecutableItem("name", self._temp_dir.name, mock.MagicMock())
        self.assertTrue(executable.execute([], [], Lock()))

    def test_execute_forward(self):
        executable = ExecutableItem("name", self._temp_dir.name, mock.MagicMock())
        self.assertTrue(executable.execute([], [], Lock()))

    def test_output_resources_backward(self):
        executable = ExecutableItem("name", self._temp_dir.name, mock.MagicMock())
        self.assertEqual(executable.output_resources(ExecutionDirection.BACKWARD), [])

    def test_output_resources_forward(self):
        executable = ExecutableItem("name", self._temp_dir.name, mock.MagicMock())
        self.assertEqual(executable.output_resources(ExecutionDirection.FORWARD), [])


if __name__ == "__main__":
    unittest.main()
