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
"""Contains unit tests for ``output_resources`` module."""
from pathlib import PurePath
import unittest
from unittest.mock import MagicMock

from spine_engine.project_item.project_item_resource import url_resource
from spine_items.data_connection.output_resources import scan_for_resources


class TestScanForResources(unittest.TestCase):
    def test_url_reference_gets_added_as_url_resource(self):
        data_connection = MagicMock()
        data_connection.name = "test dc"
        project_dir_path = PurePath(__file__).parent
        data_connection.data_dir = str(project_dir_path / ".spinetoolbox" / "test_dc")
        file_paths = []
        urls = ["gopher://long.gone.url"]
        url_credentials = {}
        resources = scan_for_resources(data_connection, file_paths, urls, url_credentials, str(project_dir_path))
        self.assertEqual(resources, [url_resource("test dc", "gopher://long.gone.url", "gopher://long.gone.url")])

    def test_credentials_do_not_show_in_url_resource_label(self):
        data_connection = MagicMock()
        data_connection.name = "test dc"
        project_dir_path = PurePath(__file__).parent
        data_connection.data_dir = str(project_dir_path / ".spinetoolbox" / "test_dc")
        file_paths = []
        urls = ["ssh://long.gone.url"]
        url_credentials = {"ssh://long.gone.url": ("superman", "t0p s3cr3t")}
        resources = scan_for_resources(data_connection, file_paths, urls, url_credentials, str(project_dir_path))
        self.assertEqual(
            resources,
            [url_resource("test dc", "ssh://superman:t0p s3cr3t@long.gone.url", "<test dc>ssh://long.gone.url")],
        )


if __name__ == '__main__':
    unittest.main()
