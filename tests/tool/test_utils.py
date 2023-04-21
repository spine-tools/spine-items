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

"""
Unit tests for :literal:`utils` module.

"""
from hashlib import sha1
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from spine_items.tool.utils import find_last_output_files


class TestFindLastOutputFiles(unittest.TestCase):
    def setUp(self):
        self._temp_dir = TemporaryDirectory()

    def tearDown(self):
        self._temp_dir.cleanup()

    def test_returns_empty_results_with_no_output_files_and_empty_output_dir(self):
        files = find_last_output_files([], self._temp_dir.name)
        self.assertEqual(files, {})

    def test_finds_output_file(self):
        stamped_dir = Path(self._temp_dir.name) / "2021-11-17T11.00.00"
        stamped_dir.mkdir()
        data_file = stamped_dir / "data.dat"
        data_file.touch()
        files = find_last_output_files(["data.dat"], self._temp_dir.name)
        self.assertEqual(files, {"data.dat": [str(data_file)]})

    def test_finds_output_file_in_subdirectory(self):
        stamped_dir = Path(self._temp_dir.name) / "2021-11-17T11.00.00"
        stamped_dir.mkdir()
        out_dir = stamped_dir / "out"
        out_dir.mkdir()
        data_file = out_dir / "data.dat"
        data_file.touch()
        files = find_last_output_files(["out/data.dat"], self._temp_dir.name)
        self.assertEqual(files, {"out/data.dat": [str(data_file)]})

    def test_finds_file_pattern(self):
        stamped_dir = Path(self._temp_dir.name) / "2021-11-17T11.00.00"
        stamped_dir.mkdir()
        data_file = stamped_dir / "data.dat"
        data_file.touch()
        files = find_last_output_files(["*.dat"], self._temp_dir.name)
        self.assertEqual(files, {"*.dat": [str(data_file)]})

    def test_finds_file_pattern_in_subdirectory(self):
        stamped_dir = Path(self._temp_dir.name) / "2021-11-17T11.00.00"
        stamped_dir.mkdir()
        out_dir = stamped_dir / "out"
        out_dir.mkdir()
        data_file = out_dir / "data.dat"
        data_file.touch()
        files = find_last_output_files(["out/*.dat"], self._temp_dir.name)
        self.assertEqual(files, {"out/*.dat": [str(data_file)]})

    def test_ignore_failed_directory(self):
        failed_dir = Path(self._temp_dir.name) / "failed"
        failed_dir.mkdir()
        data_file = failed_dir / "data.dat"
        data_file.touch()
        files = find_last_output_files(["data.dat"], self._temp_dir.name)
        self.assertEqual(files, {})

    def test_finds_latest_output_directory(self):
        stamped_dir_old = Path(self._temp_dir.name) / "2021-11-17T11.00.00"
        stamped_dir_old.mkdir()
        data_file_old = stamped_dir_old / "data.dat"
        data_file_old.touch()
        stamped_dir_new = Path(self._temp_dir.name) / "2021-11-17T11.30.00"
        stamped_dir_new.mkdir()
        data_file_new = stamped_dir_new / "data.dat"
        data_file_new.touch()
        files = find_last_output_files(["data.dat"], self._temp_dir.name)
        self.assertEqual(files, {"data.dat": [str(data_file_new)]})

    def test_finds_latest_output_directory_within_filter_id_directories(self):
        filter_id_dir = Path(self._temp_dir.name) / sha1(b"filter_id").hexdigest()
        filter_id_dir.mkdir()
        stamped_dir_old = filter_id_dir / "2021-11-17T11.00.00"
        stamped_dir_old.mkdir()
        data_file_old = stamped_dir_old / "data.dat"
        data_file_old.touch()
        stamped_dir_new = filter_id_dir / "2021-11-17T11.30.00"
        stamped_dir_new.mkdir()
        data_file_new = stamped_dir_new / "data.dat"
        data_file_new.touch()
        files = find_last_output_files(["data.dat"], self._temp_dir.name)
        self.assertEqual(files, {"data.dat": [str(data_file_new)]})

    def test_finds_latest_output_directory_within_filter_id_directories_with_mixed_directories(self):
        stamped_dir_old = Path(self._temp_dir.name) / "2021-11-17T11.00.00"
        stamped_dir_old.mkdir()
        data_file_old = stamped_dir_old / "data.dat"
        data_file_old.touch()
        filter_id_dir = Path(self._temp_dir.name) / sha1(b"filter_id").hexdigest()
        filter_id_dir.mkdir()
        stamped_dir_new = filter_id_dir / "2021-11-17T11.30.00"
        stamped_dir_new.mkdir()
        data_file_new = stamped_dir_new / "data.dat"
        data_file_new.touch()
        files = find_last_output_files(["data.dat"], self._temp_dir.name)
        self.assertEqual(files, {"data.dat": [str(data_file_new)]})

    def test_finds_latest_output_directory_within_non_filter_id_directories_with_mixed_directories(self):
        filter_id_dir = Path(self._temp_dir.name) / sha1(b"filter_id").hexdigest()
        filter_id_dir.mkdir()
        stamped_dir_old = filter_id_dir / "2021-11-17T11.00.00"
        stamped_dir_old.mkdir()
        data_file_old = stamped_dir_old / "data.dat"
        data_file_old.touch()
        stamped_dir_new = Path(self._temp_dir.name) / "2021-11-17T11.30.00"
        stamped_dir_new.mkdir()
        data_file_new = stamped_dir_new / "data.dat"
        data_file_new.touch()
        files = find_last_output_files(["data.dat"], self._temp_dir.name)
        self.assertEqual(files, {"data.dat": [str(data_file_new)]})


if __name__ == '__main__':
    unittest.main()
