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
import pathlib
from unittest import mock
from spine_engine.project_item.project_item_resource import file_resource, file_resource_in_pack
from spine_items.tool.executable_item import _find_optional_input_files


class TestFindOptionalInputFiles:
    def test_single_file(self, tmp_path):
        input_file_path = tmp_path / "data.csv"
        input_file_path.touch()
        resources = [file_resource("upstream item", str(input_file_path), input_file_path.name)]
        patterns = ["*.csv"]
        logger = mock.MagicMock()
        file_paths = _find_optional_input_files(resources, patterns, logger)
        assert len(file_paths) == 1
        found_paths = file_paths["*.csv"]
        assert len(found_paths) == 1
        assert input_file_path.samefile(found_paths[0])

    def test_pattern_inside_subdir(self, tmp_path):
        subdir = tmp_path / "inputs"
        subdir.mkdir()
        input_file_path1 = subdir / "data1.csv"
        input_file_path2 = subdir / "data2.csv"
        ignored_file_path = subdir / "no data.dat"
        for path in (input_file_path1, input_file_path2, ignored_file_path):
            path.touch()
        resources = [
            file_resource_in_pack("upstream item", "inputs@upstream item", str(path))
            for path in (input_file_path1, input_file_path2, ignored_file_path)
        ]
        patterns = ["*.csv"]
        logger = mock.MagicMock()
        file_paths = _find_optional_input_files(resources, patterns, logger)
        assert len(file_paths) == 1
        found_paths = file_paths["*.csv"]
        assert len(found_paths) == 2
        for expected_path in (input_file_path1, input_file_path2):
            for found_path in found_paths:
                if expected_path.samefile(found_path):
                    break
            else:
                assert False, f"expected path {expected_path} is not in found_paths"

    def test_grab_all_patterns_inside_multiple_subdirs(self, tmp_path):
        subdir1 = tmp_path / "inputs1"
        subdir1.mkdir()
        input_file_path1 = subdir1 / "data1.csv"
        subdir2 = tmp_path / "inputs2"
        subdir2.mkdir()
        input_file_path2 = subdir2 / "data2.csv"
        for path in (input_file_path1, input_file_path2):
            path.touch()
        resources = [
            file_resource_in_pack("upstream item", "inputs1@upstream item", str(input_file_path1)),
            file_resource_in_pack("upstream item", "inputs2@upstream item", str(input_file_path2)),
        ]
        patterns = ["*.csv"]
        logger = mock.MagicMock()
        file_paths = _find_optional_input_files(resources, patterns, logger)
        assert len(file_paths) == 1
        found_paths = file_paths["*.csv"]
        assert len(found_paths) == 2
        for expected_path in (input_file_path1, input_file_path2):
            for found_path in found_paths:
                if expected_path.samefile(found_path):
                    break
            else:
                assert False, f"expected path {expected_path} is not in found_paths"

    def test_warning_when_no_files_found(self, tmp_path):
        subdir = tmp_path / "inputs1"
        subdir.mkdir()
        resources = [file_resource_in_pack("upstream item", "inputs@upstream item")]
        patterns = ["*.csv"]
        logger = mock.MagicMock()
        file_paths = _find_optional_input_files(resources, patterns, logger)
        assert file_paths == {}
        logger.msg_warning.emit.assert_called_with("\tNo files matching pattern <b>*.csv</b> found")

    def test_find_optional_input_files_without_wildcards(self, tmp_path):
        optional_file = pathlib.Path(tmp_path, "1.txt")
        optional_file.touch()
        pathlib.Path(tmp_path, "should_not_be_found.txt").touch()
        logger = mock.MagicMock()
        optional_input_files = ["1.txt", "does_not_exist.dat"]
        resources = [file_resource("provider", str(optional_file))]
        file_paths = _find_optional_input_files(resources, optional_input_files, logger)
        expected = {"1.txt": [optional_file]}
        assert len(file_paths) == len(expected)
        for label, expected_files in expected.items():
            paths = file_paths[label]
            assert len(paths) == len(expected_files)
            for file_path, expected_path in zip(paths, expected_files):
                assert expected_path.samefile(pathlib.Path(file_path))

    def test_find_optional_input_files_with_wildcards(self, tmp_path):
        optional_file1 = pathlib.Path(tmp_path, "1.txt")
        optional_file1.touch()
        optional_file2 = pathlib.Path(tmp_path, "2.txt")
        optional_file2.touch()
        pathlib.Path(tmp_path, "should_not_be_found.jpg").touch()
        logger = mock.MagicMock()
        optional_input_files = ["*.txt"]
        resources = [file_resource("provider", str(optional_file1)), file_resource("provider", str(optional_file2))]
        file_paths = _find_optional_input_files(resources, optional_input_files, logger)
        expected = {"*.txt": [optional_file1, optional_file2]}
        assert len(file_paths) == len(expected)
        for label, expected_files in expected.items():
            paths = file_paths[label]
            assert len(paths) == len(expected_files)
            for file_path, expected_path in zip(paths, expected_files):
                assert expected_path.samefile(pathlib.Path(file_path))

    def test_find_optional_input_files_in_sub_directory(self, tmp_path):
        pathlib.Path(tmp_path, "subdir").mkdir()
        optional_file1 = pathlib.Path(tmp_path, "subdir", "1.txt")
        optional_file1.touch()
        optional_file2 = pathlib.Path(tmp_path, "subdir", "data.dat")
        optional_file2.touch()
        pathlib.Path(tmp_path, "should_not_be_found.jpg").touch()
        logger = mock.MagicMock()
        optional_input_files = ["subdir/*.txt", "subdir/data.dat"]
        resources = [file_resource("provider", str(optional_file1)), file_resource("provider", str(optional_file2))]
        file_paths = _find_optional_input_files(resources, optional_input_files, logger)
        expected = {"subdir/*.txt": [optional_file1], "subdir/data.dat": [optional_file2]}
        assert len(file_paths) == len(expected)
        for label, expected_files in expected.items():
            paths = file_paths[label]
            assert len(paths) == len(expected_files)
            for file_path, expected_path in zip(paths, expected_files):
                assert expected_path.samefile(pathlib.Path(file_path))
