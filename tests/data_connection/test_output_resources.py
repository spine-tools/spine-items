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

"""Contains unit tests for ``output_resources`` module."""
import pathlib
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock
from spine_engine.project_item.project_item_resource import (
    directory_resource,
    file_resource,
    file_resource_in_pack,
    transient_file_resource,
    url_resource,
)
from spine_items.data_connection.output_resources import scan_for_resources
from spine_items.data_connection.utils import FilePattern
from spine_items.utils import UrlDict


class TestScanForResources:

    def test_file_path_in_item_data_dir(self):
        with TemporaryDirectory() as temp_dir:
            project_dir = pathlib.Path(temp_dir, "project_dir")
            data_connection = MagicMock()
            data_connection.name = "test dc"
            data_dir = project_dir / ".spinetoolbox" / "test_dc"
            data_dir.mkdir(parents=True)
            data_connection.data_dir = str(data_dir)
            data_file = data_dir / "data.csv"
            data_file.touch()
            file_paths = [str(data_file)]
            resources = scan_for_resources(data_connection, file_paths, [], [], [], str(project_dir))
            assert resources == [file_resource("test dc", str(data_file), "<test dc>/data.csv")]

    def test_file_path_in_project_dir(self):
        with TemporaryDirectory() as temp_dir:
            project_dir = pathlib.Path(temp_dir, "project_dir")
            data_connection = MagicMock()
            data_connection.name = "test dc"
            data_dir = project_dir / ".spinetoolbox" / "test_dc"
            data_dir.mkdir(parents=True)
            data_connection.data_dir = str(data_dir)
            data_file = project_dir / "data.csv"
            data_file.touch()
            file_paths = [str(data_file)]
            resources = scan_for_resources(data_connection, file_paths, [], [], [], str(project_dir))
            assert resources == [file_resource("test dc", str(data_file), "<project>/data.csv")]

    def test_non_existent_file_path_in_project_dir(self):
        with TemporaryDirectory() as temp_dir:
            project_dir = pathlib.Path(temp_dir, "project_dir")
            data_connection = MagicMock()
            data_connection.name = "test dc"
            data_dir = project_dir / ".spinetoolbox" / "test_dc"
            data_dir.mkdir(parents=True)
            data_connection.data_dir = str(data_dir)
            data_file = project_dir / "data.csv"
            file_paths = [str(data_file)]
            resources = scan_for_resources(data_connection, file_paths, [], [], [], str(project_dir))
            assert resources == [transient_file_resource("test dc", "<project>/data.csv", None)]

    def test_file_path_outside_of_project_dir(self):
        with TemporaryDirectory() as temp_dir:
            project_dir = pathlib.Path(temp_dir, "project_dir")
            data_connection = MagicMock()
            data_connection.name = "test dc"
            data_dir = project_dir / ".spinetoolbox" / "test_dc"
            data_dir.mkdir(parents=True)
            data_connection.data_dir = str(data_dir)
            other_dir = pathlib.Path(temp_dir, "other_dir")
            other_dir.mkdir()
            data_file = other_dir / "data.csv"
            data_file.touch()
            file_paths = [str(data_file)]
            resources = scan_for_resources(data_connection, file_paths, [], [], [], str(project_dir))
            assert resources == [file_resource("test dc", str(data_file), data_file.as_posix())]

    def test_non_existent_file_path_outside_of_project_dir(self):
        with TemporaryDirectory() as temp_dir:
            project_dir = pathlib.Path(temp_dir, "project_dir")
            data_connection = MagicMock()
            data_connection.name = "test dc"
            data_dir = project_dir / ".spinetoolbox" / "test_dc"
            data_dir.mkdir(parents=True)
            data_connection.data_dir = str(data_dir)
            other_dir = pathlib.Path(temp_dir, "other_dir")
            other_dir.mkdir()
            data_file = other_dir / "data.csv"
            file_paths = [str(data_file)]
            resources = scan_for_resources(data_connection, file_paths, [], [], [], str(project_dir))
            assert resources == [transient_file_resource("test dc", data_file.as_posix(), None)]

    def test_credentials_do_not_show_in_url_resource_label(self):
        data_connection = MagicMock()
        data_connection.name = "test dc"
        project_dir_path = pathlib.PurePath(__file__).parent
        data_connection.data_dir = str(project_dir_path / ".spinetoolbox" / "test_dc")
        file_paths = []
        file_patterns = []
        directories = []
        urls: list[UrlDict] = [
            {
                "dialect": "postgresql",
                "host": "long.gone.url",
                "port": 5432,
                "database": "warehouse",
                "username": "superman",
                "password": "t0p s3cr3t",
            }
        ]
        resources = scan_for_resources(
            data_connection, file_paths, file_patterns, directories, urls, str(project_dir_path)
        )
        assert resources == [
            url_resource(
                "test dc",
                "postgresql+psycopg2://superman:***@long.gone.url:5432/warehouse",
                "<test dc>postgresql+psycopg2://long.gone.url:5432/warehous",
            )
        ]

    def test_file_patterns_get_globbed_into_file_packs(self):
        with TemporaryDirectory() as temp_dir:
            data_dir = pathlib.Path(temp_dir, "data")
            data_dir.mkdir()
            empty_dir = pathlib.Path(temp_dir, "empty")
            empty_dir.mkdir()
            file1 = data_dir / "inputs.csv"
            file1.touch()
            file2 = data_dir / "definitions.csv"
            file2.touch()
            file3 = data_dir / "logs.log"
            file3.touch()
            data_connection = MagicMock()
            data_connection.name = "test dc"
            project_dir_path = pathlib.PurePath(__file__).parent
            data_connection.data_dir = str(project_dir_path / ".spinetoolbox" / "test_dc")
            file_paths = []
            file_patterns = [
                FilePattern(data_dir, "*.csv"),
                FilePattern(data_dir, "*.log"),
                FilePattern(empty_dir, "*.*"),
            ]
            directories = []
            urls = []
            resources = scan_for_resources(
                data_connection, file_paths, file_patterns, directories, urls, str(project_dir_path)
            )
            csv_label = str(data_dir / "*.csv")
            log_label = str(data_dir / "*.log")
            empty_label = str(data_dir / "*.*")
            test_case = unittest.TestCase()
            test_case.assertCountEqual(
                resources,
                [
                    file_resource_in_pack("test dc", csv_label, str(file1)),
                    file_resource_in_pack("test dc", csv_label, str(file2)),
                    file_resource_in_pack("test dc", log_label, str(file3)),
                    file_resource_in_pack("test dc", empty_label, None),
                ],
            )

    def test_directory_resources(self):
        with TemporaryDirectory() as temp_dir:
            project_dir = pathlib.Path(temp_dir, "project_dir")
            dir_in_project = project_dir / "project_data"
            dir_out_of_project = pathlib.Path(temp_dir, "data_dir")
            data_connection = MagicMock()
            data_connection.name = "test dc"
            data_connection.data_dir = str(project_dir / ".spinetoolbox" / "test_dc")
            directories = [str(dir_in_project), str(dir_out_of_project)]
            resources = scan_for_resources(data_connection, [], [], directories, [], str(project_dir))
            assert resources == [
                directory_resource("test dc", str(dir_in_project), "<project>/project_data"),
                directory_resource("test dc", str(dir_out_of_project)),
            ]
