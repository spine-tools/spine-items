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

"""Unit tests for ToolExecutable item."""
from multiprocessing import Lock
import sys
import pathlib
from tempfile import TemporaryDirectory
from queue import Queue
import unittest
from unittest import mock
from PySide6.QtCore import QCoreApplication
from spine_engine.project_item.project_item_resource import file_resource
from spine_engine.execution_managers.persistent_execution_manager import kill_persistent_processes
from spine_engine.project_item.project_item_resource import CmdLineArg
from spine_engine.utils.queue_logger import QueueLogger
from spine_items.tool.executable_item import ExecutableItem, _count_files_and_dirs
from spine_items.tool.tool_specifications import ToolSpecification, PythonTool


class TestToolExecutable(unittest.TestCase):
    def setUp(self):
        self._temp_dir = TemporaryDirectory()

    def tearDown(self):
        self._temp_dir.cleanup()

    def test_item_type(self):
        self.assertEqual(ExecutableItem.item_type(), "Tool")

    def test_from_dict(self):
        """Tests that from_dict creates an ExecutableItem."""
        mock_settings = _MockSettings()
        item_dict = {
            "type": "Tool",
            "description": "",
            "x": 0,
            "y": 0,
            "specification": "Python Tool",
            "execute_in_work": True,
            "cmd_line_args": [{"type": "literal", "arg": "a"}, {"type": "literal", "arg": "b"}],
            "options": {},
        }
        script_dir = pathlib.Path(self._temp_dir.name, "scripts")
        script_dir.mkdir()
        script_file_name = self._write_output_script(script_dir)
        script_files = [script_file_name]
        python_tool_spec = PythonTool(
            name="Python Tool",
            tooltype="Python",
            path=str(script_dir),
            includes=script_files,
            settings=mock_settings,
            logger=mock.MagicMock(),
        )
        specs_in_project = {"Tool": {"Python Tool": python_tool_spec}}
        temp_project_dir = str(pathlib.Path(self._temp_dir.name, "project"))
        item = ExecutableItem.from_dict(
            item_dict,
            name="T",
            project_dir=temp_project_dir,
            app_settings=mock_settings,
            specifications=specs_in_project,
            logger=mock.MagicMock(),
        )
        self.assertIsInstance(item, ExecutableItem)
        self.assertEqual("Tool", item.item_type())
        self.assertTrue(item._tool_specification.name, "Python Tool")
        self.assertEqual("some_work_dir", item._work_dir)
        self.assertEqual([CmdLineArg("a"), CmdLineArg("b")], item._cmd_line_args)
        # Test that the item is not created if "appSettings/workDir" key is missing from qsettings
        item = ExecutableItem.from_dict(
            item_dict,
            name="T",
            project_dir=temp_project_dir,
            app_settings=_EmptyMockSettings(),
            specifications=specs_in_project,
            logger=mock.MagicMock(),
        )
        self.assertIsInstance(item, ExecutableItem)
        self.assertIsNone(item._work_dir, "")
        # This time the project dict does not have any specifications
        item = ExecutableItem.from_dict(
            item_dict,
            name="T",
            project_dir=temp_project_dir,
            app_settings=mock_settings,
            specifications=dict(),
            logger=mock.MagicMock(),
        )
        self.assertIsInstance(item, ExecutableItem)
        self.assertIsNone(item._tool_specification)
        # Modify item_dict
        item_dict["execute_in_work"] = False
        item = ExecutableItem.from_dict(
            item_dict,
            name="T",
            project_dir=temp_project_dir,
            app_settings=mock_settings,
            specifications=specs_in_project,
            logger=mock.MagicMock(),
        )
        self.assertIsInstance(item, ExecutableItem)
        self.assertEqual("Tool", item.item_type())
        self.assertEqual([CmdLineArg("a"), CmdLineArg("b")], item._cmd_line_args)
        self.assertIsNone(item._work_dir)
        # Modify item_dict
        item_dict["specification"] = ""
        item = ExecutableItem.from_dict(
            item_dict,
            name="T",
            project_dir=temp_project_dir,
            app_settings=mock_settings,
            specifications=specs_in_project,
            logger=mock.MagicMock(),
        )
        self.assertIsInstance(item, ExecutableItem)

    def test_ready_to_execute(self):
        logger = mock.MagicMock()
        executable = ExecutableItem(
            "executable name",
            work_dir=str(pathlib.Path(self._temp_dir.name, "work")),
            tool_specification=None,
            cmd_line_args=[],
            options={},
            kill_completed_processes=False,
            log_process_output=False,
            group_id=None,
            project_dir=self._temp_dir.name,
            logger=logger,
        )
        self.assertFalse(executable.ready_to_execute(settings=dict()))

    def test_execute_archives_output_files(self):
        script_dir = pathlib.Path(self._temp_dir.name, "scripts")
        script_dir.mkdir()
        script_file_name = self._write_output_script(script_dir)
        script_files = [script_file_name]
        output_files = ["out.dat", "subdir/out.txt"]
        app_settings = _MockSettings()
        logger = mock.MagicMock()
        tool_specification = PythonTool(
            "Python tool", "Python", str(script_dir), script_files, app_settings, logger, outputfiles=output_files
        )
        work_dir = pathlib.Path(self._temp_dir.name, "work")
        work_dir.mkdir()
        executable = ExecutableItem(
            "Create files", str(work_dir), tool_specification, [], {}, False, False, None, self._temp_dir.name, logger
        )
        executable.execute([], [], Lock())
        while executable._tool_instance is not None:
            QCoreApplication.processEvents()
        archives = list(pathlib.Path(executable._data_dir, "output").iterdir())
        self.assertEqual(len(archives), 1)
        self.assertNotEqual(archives[0].name, "failed")
        self.assertTrue(pathlib.Path(archives[0], "out.dat").exists())
        self.assertTrue(pathlib.Path(archives[0], "subdir", "out.txt").exists())
        kill_persistent_processes()

    def test_execute_logs_messages(self):
        script_dir = pathlib.Path(self._temp_dir.name, "scripts")
        script_dir.mkdir()
        script_file_name = "script.py"
        file_path = pathlib.Path(script_dir, "script.py")
        with open(file_path, "w") as script_file:
            script_file.writelines(["print('hello')\n", "raise ValueError('foo')\n"])
        script_files = [script_file_name]
        app_settings = _MockSettings()
        item_name = "Logs stuff"
        logger = QueueLogger(Queue(), item_name, None, [])
        tool_specification = PythonTool("Python tool", "Python", str(script_dir), script_files, app_settings, logger)
        work_dir = pathlib.Path(self._temp_dir.name, "work")
        work_dir.mkdir()
        executable = ExecutableItem(
            item_name, str(work_dir), tool_specification, [], {}, False, True, None, self._temp_dir.name, logger
        )
        executable.execute([], [], Lock())
        while executable._tool_instance is not None:
            QCoreApplication.processEvents()
        logs = list(pathlib.Path(executable._logs_dir).iterdir())
        self.assertEqual(len(logs), 1)
        with open(logs[0], "r") as f:
            lines = f.readlines()
        expected_lines = [
            "### Spine execution log file\n",
            "### Item name: Logs stuff\n",
            "### Filter id: \n",
            "### Part: 1\n",
            "\n",
            "# Running python script.py\n",
            "hello\n",
            "Traceback (most recent call last):\n",
            '  File "<stdin>", line 3, in <module>\n',
            '  File "script.py", line 2, in <module>\n',
            "    raise ValueError('foo')\n",
            "ValueError: foo\n",
        ]
        self.assertCountEqual(lines, expected_lines)
        kill_persistent_processes()

    def test_find_optional_input_files_without_wildcards(self):
        optional_file = pathlib.Path(self._temp_dir.name, "1.txt")
        optional_file.touch()
        pathlib.Path(self._temp_dir.name, "should_not_be_found.txt").touch()
        logger = mock.MagicMock()
        optional_input_files = ["1.txt", "does_not_exist.dat"]
        tool_specification = ToolSpecification(
            "spec name", "Python", self._temp_dir.name, [], None, logger, inputfiles_opt=optional_input_files
        )
        executable = ExecutableItem(
            "executable name",
            work_dir=self._temp_dir.name,
            tool_specification=tool_specification,
            cmd_line_args=[],
            options={},
            kill_completed_processes=False,
            log_process_output=False,
            group_id=None,
            project_dir=self._temp_dir.name,
            logger=logger,
        )
        resources = [file_resource("provider", str(optional_file))]
        file_paths = executable._find_optional_input_files(resources)
        expected = {"1.txt": [optional_file]}
        self.assertEqual(len(file_paths), len(expected))
        for label, expected_files in expected.items():
            paths = file_paths[label]
            self.assertEqual(len(paths), len(expected_files))
            for file_path, expected_path in zip(paths, expected_files):
                self.assertTrue(expected_path.samefile(pathlib.Path(file_path)))

    def test_find_optional_input_files_with_wildcards(self):
        optional_file1 = pathlib.Path(self._temp_dir.name, "1.txt")
        optional_file1.touch()
        optional_file2 = pathlib.Path(self._temp_dir.name, "2.txt")
        optional_file2.touch()
        pathlib.Path(self._temp_dir.name, "should_not_be_found.jpg").touch()
        logger = mock.MagicMock()
        optional_input_files = ["*.txt"]
        tool_specification = ToolSpecification(
            "spec name", "Python", self._temp_dir.name, [], None, logger, inputfiles_opt=optional_input_files
        )
        executable = ExecutableItem(
            "executable name",
            work_dir=self._temp_dir.name,
            tool_specification=tool_specification,
            cmd_line_args=[],
            options={},
            kill_completed_processes=False,
            log_process_output=False,
            group_id=None,
            project_dir=self._temp_dir.name,
            logger=logger,
        )
        resources = [file_resource("provider", str(optional_file1)), file_resource("provider", str(optional_file2))]
        file_paths = executable._find_optional_input_files(resources)
        expected = {"*.txt": [optional_file1, optional_file2]}
        self.assertEqual(len(file_paths), len(expected))
        for label, expected_files in expected.items():
            paths = file_paths[label]
            self.assertEqual(len(paths), len(expected_files))
            for file_path, expected_path in zip(paths, expected_files):
                self.assertTrue(expected_path.samefile(pathlib.Path(file_path)))

    def test_find_optional_input_files_in_sub_directory(self):
        pathlib.Path(self._temp_dir.name, "subdir").mkdir()
        optional_file1 = pathlib.Path(self._temp_dir.name, "subdir", "1.txt")
        optional_file1.touch()
        optional_file2 = pathlib.Path(self._temp_dir.name, "subdir", "data.dat")
        optional_file2.touch()
        pathlib.Path(self._temp_dir.name, "should_not_be_found.jpg").touch()
        logger = mock.MagicMock()
        optional_input_files = ["subdir/*.txt", "subdir/data.dat"]
        tool_specification = ToolSpecification(
            "spec name", "Python", self._temp_dir.name, [], None, logger, inputfiles_opt=optional_input_files
        )
        executable = ExecutableItem(
            "executable name",
            work_dir=self._temp_dir.name,
            tool_specification=tool_specification,
            cmd_line_args=[],
            options={},
            kill_completed_processes=False,
            log_process_output=False,
            group_id=None,
            project_dir=self._temp_dir.name,
            logger=logger,
        )
        resources = [file_resource("provider", str(optional_file1)), file_resource("provider", str(optional_file2))]
        file_paths = executable._find_optional_input_files(resources)
        expected = {"subdir/*.txt": [optional_file1], "subdir/data.dat": [optional_file2]}
        self.assertEqual(len(file_paths), len(expected))
        for label, expected_files in expected.items():
            paths = file_paths[label]
            self.assertEqual(len(paths), len(expected_files))
            for file_path, expected_path in zip(paths, expected_files):
                self.assertTrue(expected_path.samefile(pathlib.Path(file_path)))

    def test_output_resources_forward(self):
        logger = mock.MagicMock()
        tool_specification = PythonTool(
            name="Python Tool",
            tooltype="Python",
            path=self._temp_dir.name,
            includes=["script.py"],
            settings=None,
            logger=mock.MagicMock(),
            outputfiles=["results.gdx", "report.txt"],
        )
        executable = ExecutableItem(
            "name", self._temp_dir.name, tool_specification, [], {}, False, False, None, self._temp_dir.name, logger
        )
        output_dir = pathlib.Path(executable._data_dir, "output")
        output_dir.mkdir()
        out_file_1 = output_dir / "results.gdx"
        out_file_1.touch()
        out_file_2 = output_dir / "report.txt"
        out_file_2.touch()
        with mock.patch("spine_items.tool.output_resources.find_last_output_files") as mock_find_last_output_files:
            mock_find_last_output_files.return_value = {
                "results.gdx": [str(out_file_1)],
                "report.txt": [str(out_file_2)],
            }
            resources = executable._output_resources_forward()
            mock_find_last_output_files.assert_called_once()
            self.assertIsInstance(resources, list)
            self.assertEqual(2, len(resources))
            resource_paths = [r.path for r in resources]
            self.assertTrue(any(out_file_1.samefile(p) for p in resource_paths))
            self.assertTrue(any(out_file_2.samefile(p) for p in resource_paths))

    def test_stop_execution(self):
        logger = mock.MagicMock()
        tool_specification = PythonTool(
            name="Python Tool",
            tooltype="Python",
            path=self._temp_dir.name,
            includes=["script.py"],
            settings=None,
            logger=mock.MagicMock(),
            outputfiles=["results.gdx", "report.txt"],
        )
        executable = ExecutableItem(
            "name", self._temp_dir.name, tool_specification, [], {}, False, False, None, self._temp_dir.name, logger
        )
        executable._tool_instance = executable._tool_specification.create_tool_instance(
            self._temp_dir.name, False, logger, mock.MagicMock()
        )
        executable._tool_instance.exec_mngr = mock.MagicMock()
        executable.stop_execution()
        self.assertIsNone(executable._tool_instance)

    def test_count_files_and_dirs(self):
        """Tests protected function in tool/executable_item.py."""
        paths = ["data/a.txt", "data/output", "data/input_dir/", "inc/b.txt", "directory/"]  # 3 files, 2 dirs
        n_dir, n_files = _count_files_and_dirs(paths)
        self.assertEqual(2, n_dir)
        self.assertEqual(3, n_files)

    @staticmethod
    def _write_output_script(script_dir):
        file_path = pathlib.Path(script_dir, "script.py")
        with open(file_path, "w") as script_file:
            script_file.writelines(
                [
                    "from pathlib import Path\n",
                    "Path('out.dat').touch()\n",
                    "Path('subdir').mkdir(exist_ok=True)\n",
                    "Path('subdir', 'out.txt').touch()\n",
                ]
            )
        return "script.py"


class _EmptyMockSettings:
    @staticmethod
    def value(key, defaultValue=None):
        return {None: None}.get(key, defaultValue)


class _MockSettings:
    @staticmethod
    def value(key, defaultValue=None):
        return {
            "appSettings/pythonPath": sys.executable,
            "appSettings/usePythonKernel": "0",  # Don't use Jupyter Console
            "appSettings/workDir": "some_work_dir",
        }.get(key, defaultValue)


if __name__ == "__main__":
    unittest.main()
