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

"""Contains unit tests for Exporter's ``utils`` module."""
import os.path
import unittest
from spine_engine.project_item.project_item_resource import url_resource
from spine_items.exporter.output_channel import OutputChannel
from spine_items.exporter.utils import output_database_resources


class TestOutputDatabaseResources(unittest.TestCase):
    def test_creates_url_resources_for_channels_with_urls(self):
        item_name = "test exporter"
        channels = [
            OutputChannel("label 1", item_name, "file.csv"),
            OutputChannel(
                "label 1", item_name, "out database", {"dialect": "sqlite", "database": "/path/to/db.sqlite"}
            ),
        ]
        resources = output_database_resources(item_name, channels)
        expected_url = "sqlite:///" + os.path.abspath("/path/to/db.sqlite")
        self.assertEqual(resources, [url_resource(item_name, expected_url, "out database")])


if __name__ == "__main__":
    unittest.main()
