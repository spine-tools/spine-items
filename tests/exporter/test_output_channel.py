######################################################################################################################
# Copyright (C) 2017-2023 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""Unit tests for the ``output_channel`` module."""
import unittest
from pathlib import Path
from spine_items.exporter.output_channel import OutputChannel


class TestOutputChannel(unittest.TestCase):
    def test_initialization_with_out_label(self):
        channel = OutputChannel("In label", "Exporter 1", "Out label")
        self.assertEqual(channel.in_label, "In label")
        self.assertEqual(channel.out_label, "Out label")

    def test_initialization_without_out_label(self):
        channel = OutputChannel("In label", "Exporter 1")
        self.assertEqual(channel.in_label, "In label")
        self.assertEqual(channel.out_label, "In label_exported@Exporter 1")

    def test_serialization(self):
        channel = OutputChannel("In label", "Exporter 1", "Out label")
        channel_dict = channel.to_dict("/project/path/")
        restored = OutputChannel.from_dict(channel_dict, "Exporter 1", "/project/path/")
        self.assertEqual(restored.in_label, "In label")
        self.assertEqual(restored.out_label, "Out label")

    def test_serialization_hides_credentials_from_url(self):
        channel = OutputChannel(
            "In label",
            "Exporter 1",
            "Out label",
            {
                "dialect": "mysql",
                "host": "dummy.test.org",
                "port": 99,
                "database": "data_leak",
                "username": "admin",
                "password": "s3cr3t",
            },
        )
        channel_dict = channel.to_dict("/project/path/")
        self.assertNotIn("username", channel_dict["out_url"])
        self.assertNotIn("password", channel_dict["out_url"])
        restored = OutputChannel.from_dict(channel_dict, "Exporter 1", "/project/path/")
        self.assertEqual(restored.in_label, "In label")
        self.assertEqual(restored.out_label, "Out label")
        self.assertEqual(
            restored.out_url, {"dialect": "mysql", "host": "dummy.test.org", "port": 99, "database": "data_leak"}
        )

    def test_database_paths_serialized_as_relative_when_inside_project_dir(self):
        initial_project_dir = Path("project_1", "dir")
        relative_database_path = Path("data", "base.sqlite")
        channel = OutputChannel(
            "In label",
            "Exporter 1",
            "Out label",
            {"dialect": "sqlite", "database": str(initial_project_dir / relative_database_path)},
        )
        channel_dict = channel.to_dict(str(initial_project_dir))
        self.assertNotIn("username", channel_dict["out_url"])
        self.assertNotIn("password", channel_dict["out_url"])
        new_project_dir = Path("project_2")
        restored = OutputChannel.from_dict(channel_dict, "Exporter 1", str(new_project_dir))
        self.assertEqual(restored.in_label, "In label")
        self.assertEqual(restored.out_label, "Out label")
        self.assertEqual(
            restored.out_url, {"dialect": "sqlite", "database": str(new_project_dir / relative_database_path)}
        )


if __name__ == "__main__":
    unittest.main()
