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

""" Unit tests for :literal:`utils` module. """
from hashlib import sha1
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest import mock
from spine_items.tool.utils import find_last_output_files, get_julia_path_and_project
from spine_engine.utils.helpers import AppSettings


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


class TestGetJuliaPathAndProject(unittest.TestCase):
    def test_get_julia_path_and_project(self):
        # Use Jupyter Console: False
        exec_settings = {
            "use_jupyter_console": False,
            "executable": "",
            "env": "",
            "kernel_spec_name": "",
            "project": "",
        }
        app_settings = AppSettings({"appSettings/juliaPath": "path/to/julia"})
        julia_args = get_julia_path_and_project(exec_settings, app_settings)
        self.assertTrue(len(julia_args) == 1)
        self.assertTrue(julia_args[0] == "path/to/julia")
        # Use Jupyter Console: False
        exec_settings = {
            "use_jupyter_console": False,
            "executable": "/path/to/julia",
            "env": "",
            "kernel_spec_name": "",
            "project": "/path/to/myjuliaproject",
        }
        julia_args = get_julia_path_and_project(exec_settings, app_settings)
        self.assertTrue(julia_args[0] == "/path/to/julia")
        self.assertTrue(julia_args[1] == "--project=/path/to/myjuliaproject")
        # Use Jupyter Console: True
        exec_settings = {
            "use_jupyter_console": True,
            "executable": "",
            "env": "",
            "kernel_spec_name": "unknown_kernel",
            "project": "",
        }
        julia_args = get_julia_path_and_project(exec_settings, app_settings)
        self.assertIsNone(julia_args)
        # Use Jupyter Console: True
        exec_settings = {
            "use_jupyter_console": True,
            "executable": "/path/to/nowhere",
            "env": "conda",
            "kernel_spec_name": "test_kernel",
            "project": "/path/to/nonexistingprojectthatshouldnotbereturnedherebecausetheprojectisdefinedinkerneljson",
        }
        with mock.patch("spine_items.tool.utils.find_kernel_specs") as mock_find_kernel_specs:
            # Return a dict containing a path to a dummy kernel resource dir when find_kernel_specs is called
            mock_find_kernel_specs.return_value = {"test_kernel": Path(__file__).parent / "dummy_julia_kernel"}
            julia_args = get_julia_path_and_project(exec_settings, app_settings)
            self.assertEqual(2, len(julia_args))
            self.assertTrue(julia_args[0] == "/path/to/somejulia")
            self.assertTrue(julia_args[1] == "--project=/path/to/someotherjuliaproject")


if __name__ == "__main__":
    unittest.main()
