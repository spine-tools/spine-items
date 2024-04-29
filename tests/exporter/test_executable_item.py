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

"""Unit tests for Exporter's ``executable_item`` module."""
import unittest
from unittest import mock
from pathlib import Path
from tempfile import TemporaryDirectory
from PySide6.QtWidgets import QApplication
from spine_engine.project_item.project_item_resource import database_resource
from spine_items.exporter.executable_item import ExecutableItem
from spine_items.exporter.exporter import Exporter
from spine_items.exporter.output_channel import OutputChannel
from spine_items.exporter.specification import Specification
from tests.mock_helpers import clean_up_toolbox, create_toolboxui_with_project


class TestExecutableItemWithToolbox(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        """Set up."""
        self._temp_dir = TemporaryDirectory()
        self._toolbox = create_toolboxui_with_project(self._temp_dir.name)

    def tearDown(self):
        clean_up_toolbox(self._toolbox)
        self._temp_dir.cleanup()

    def test_from_dict(self):
        project = self._toolbox.project()
        specification = Specification("Test spec", "Exporter specification for testing")
        project.add_specification(specification)
        database_path = str(Path(project.project_dir, "database.sqlite"))
        output_channels = [
            OutputChannel("in label", "My exporter", "out label", {"dialect": "sqlite", "database": database_path})
        ]
        exporter = Exporter(
            "My exporter",
            "",
            0.0,
            0.0,
            self._toolbox,
            project,
            "Test spec",
            output_channels,
            output_time_stamps=False,
            cancel_on_error=True,
        )
        project.add_item(exporter)
        exporter.upstream_resources_updated(
            [database_resource("My data store", "sqlite:/// " + database_path, "in label")]
        )
        item_dict = exporter.item_dict()
        logger = mock.MagicMock()
        specifications = {exporter.item_type(): {specification.name: specification}}
        executable = ExecutableItem.from_dict(
            item_dict, "My exporter", project.project_dir, self._toolbox.qsettings(), specifications, logger=logger
        )
        self.assertEqual(executable.item_type(), exporter.item_type())
        self.assertEqual(executable.name, exporter.name)


if __name__ == "__main__":
    unittest.main()
