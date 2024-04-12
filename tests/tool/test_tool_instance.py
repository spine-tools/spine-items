######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# Copyright Spine Items contributors
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""Contains unit tests for the tool_instance module."""
import sys
import unittest
from unittest import mock
from tempfile import TemporaryDirectory
from pathlib import Path
from spine_items.tool.tool_specifications import PythonTool, JuliaTool, GAMSTool, ExecutableTool
from tests.mock_helpers import MockQSettings


class TestToolInstance(unittest.TestCase):
    def test_python_prepare_with_jupyter_console(self):
        # No cmd line args
        instance = self._make_python_tool_instance(True)
        with mock.patch("spine_items.tool.tool_instance.KernelExecutionManager") as mock_manager:
            instance.prepare([])
            mock_manager.assert_called_once()
            self.assertEqual(mock_manager.call_args[0][1], "some_kernel")  # kernel_name
            self.assertEqual(mock_manager.call_args[0][2], ["%cd -q path/", '%run "main.py"'])  # commands
        # With tool cmd line args
        instance = self._make_python_tool_instance(True)
        with mock.patch("spine_items.tool.tool_instance.KernelExecutionManager") as mock_manager:
            instance.prepare(["arg1", "arg2"])
            mock_manager.assert_called_once()
            self.assertEqual(mock_manager.call_args[0][1], "some_kernel")
            self.assertEqual(mock_manager.call_args[0][2], ["%cd -q path/", '%run "main.py" "arg1" "arg2"'])
        # With tool and tool spec cmd line args
        instance = self._make_python_tool_instance(True, ["arg3"])
        with mock.patch("spine_items.tool.tool_instance.KernelExecutionManager") as mock_manager:
            instance.prepare(["arg1", "arg2"])
            mock_manager.assert_called_once()
            self.assertEqual(mock_manager.call_args[0][1], "some_kernel")
            self.assertEqual(mock_manager.call_args[0][2], ["%cd -q path/", '%run "main.py" "arg3" "arg1" "arg2"'])

    def test_python_prepare_with_basic_console(self):
        # No cmd line args
        instance = self._make_python_tool_instance(False)
        with mock.patch("spine_items.tool.tool_instance.PythonPersistentExecutionManager") as mock_manager:
            mock_manager.return_value = True
            instance.prepare([])
            mock_manager.assert_called_once()
            self.assertEqual([sys.executable], mock_manager.call_args[0][1])  # args
            self.assertEqual(5, len(mock_manager.call_args[0][2]))  # commands
            self.assertEqual("python main.py", mock_manager.call_args[0][3])  # alias
        # With tool cmd line args
        instance = self._make_python_tool_instance(False)
        with mock.patch("spine_items.tool.tool_instance.PythonPersistentExecutionManager") as mock_manager:
            mock_manager.return_value = True
            instance.prepare(["arg1", "arg2"])
            mock_manager.assert_called_once()
            self.assertEqual([sys.executable], mock_manager.call_args[0][1])  # args
            self.assertEqual(5, len(mock_manager.call_args[0][2]))  # commands
            self.assertEqual("python main.py arg1 arg2", mock_manager.call_args[0][3])  # alias
        # With tool and tool spec cmd line args
        instance = self._make_python_tool_instance(False, ["arg3"])
        with mock.patch("spine_items.tool.tool_instance.PythonPersistentExecutionManager") as mock_manager:
            mock_manager.return_value = True
            instance.prepare(["arg1", "arg2"])
            mock_manager.assert_called_once()
            self.assertEqual([sys.executable], mock_manager.call_args[0][1])  # args
            self.assertEqual(5, len(mock_manager.call_args[0][2]))  # commands
            self.assertEqual("python main.py arg3 arg1 arg2", mock_manager.call_args[0][3])  # alias

    def test_julia_prepare_with_jupyter_console(self):
        # No cmd line args
        instance = self._make_julia_tool_instance(True)
        with mock.patch("spine_items.tool.tool_instance.KernelExecutionManager") as mock_kem, mock.patch(
            "os.path.isfile"
        ) as mock_isfile, mock.patch("spine_items.tool.utils.find_kernel_specs") as mock_find_kernel_specs:
            mock_find_kernel_specs.return_value = {"some_julia_kernel": Path(__file__).parent / "dummy_julia_kernel"}
            mock_isfile.return_value = False
            instance.prepare([])
            mock_isfile.assert_called()
            mock_kem.assert_called_once()
            mock_find_kernel_specs.assert_called_once()
            self.assertEqual(mock_kem.call_args[0][1], "some_julia_kernel")  # kernel_name
            self.assertEqual(mock_kem.call_args[0][2], ['cd("path/");', 'include("hello.jl")'])  # commands
        # With tool cmd line args
        instance = self._make_julia_tool_instance(True)
        with mock.patch("spine_items.tool.tool_instance.KernelExecutionManager") as mock_kem, mock.patch(
            "os.path.isfile"
        ) as mock_isfile, mock.patch("spine_items.tool.utils.find_kernel_specs") as mock_find_kernel_specs:
            mock_find_kernel_specs.return_value = {"some_julia_kernel": Path(__file__).parent / "dummy_julia_kernel"}
            mock_isfile.return_value = False
            instance.prepare(["arg1", "arg2"])
            mock_isfile.assert_called()
            mock_kem.assert_called_once()
            mock_find_kernel_specs.assert_called_once()
            self.assertEqual(mock_kem.call_args[0][1], "some_julia_kernel")
            self.assertEqual(
                mock_kem.call_args[0][2],
                ['cd("path/");', 'empty!(ARGS); append!(ARGS, ["arg1", "arg2"]);', 'include("hello.jl")'],
            )
        # With tool and tool spec cmd line args
        instance = self._make_julia_tool_instance(True, ["arg3"])
        with mock.patch("spine_items.tool.tool_instance.KernelExecutionManager") as mock_kem, mock.patch(
            "os.path.isfile"
        ) as mock_isfile, mock.patch("spine_items.tool.utils.find_kernel_specs") as mock_find_kernel_specs:
            mock_find_kernel_specs.return_value = {"some_julia_kernel": Path(__file__).parent / "dummy_julia_kernel"}
            mock_isfile.return_value = False
            instance.prepare(["arg1", "arg2"])
            mock_isfile.assert_called()
            mock_kem.assert_called_once()
            mock_find_kernel_specs.assert_called_once()
            self.assertEqual(mock_kem.call_args[0][1], "some_julia_kernel")
            self.assertEqual(
                mock_kem.call_args[0][2],
                ['cd("path/");', 'empty!(ARGS); append!(ARGS, ["arg3", "arg1", "arg2"]);', 'include("hello.jl")'],
            )

    def test_julia_prepare_with_basic_console(self):
        # No cmd line args
        instance = self._make_julia_tool_instance(False)
        instance._owner.options = {"julia_sysimage": "path/to/sysimage.so"}
        with mock.patch("spine_items.tool.tool_instance.JuliaPersistentExecutionManager") as mock_manager, mock.patch(
            "os.path.isfile"
        ) as mock_isfile, mock.patch("spine_items.tool.utils.resolve_julia_executable") as mock_resolve_julia:
            mock_isfile.return_value = True  # Make isfile() accept fake julia_sysimage path
            mock_manager.return_value = True
            mock_resolve_julia.return_value = "path/to/julia"
            instance.prepare([])
            mock_isfile.assert_called()
            mock_manager.assert_called_once()
            mock_resolve_julia.assert_called()
            self.assertEqual(
                ["path/to/julia", "--sysimage=path/to/sysimage.so"], mock_manager.call_args[0][1]
            )  # args attribute for JuliaPersistentExecutionManger
            self.assertEqual(['cd("path/");', 'include("hello.jl")'], mock_manager.call_args[0][2])  # commands
            self.assertEqual("julia hello.jl", mock_manager.call_args[0][3])  # alias
        # With tool cmd line args
        instance = self._make_julia_tool_instance(False)
        with mock.patch("spine_items.tool.tool_instance.JuliaPersistentExecutionManager") as mock_manager, mock.patch(
            "os.path.isfile"
        ) as mock_isfile, mock.patch("spine_items.tool.utils.resolve_julia_executable") as mock_resolve_julia:
            mock_isfile.return_value = False
            mock_manager.return_value = True
            mock_resolve_julia.return_value = "path/to/julia"
            instance.prepare(["arg1", "arg2"])
            mock_isfile.assert_called()
            mock_manager.assert_called_once()
            mock_resolve_julia.assert_called()
            self.assertEqual(["path/to/julia"], mock_manager.call_args[0][1])
            self.assertEqual(
                ['cd("path/");', 'empty!(ARGS); append!(ARGS, ["arg1", "arg2"]);', 'include("hello.jl")'],
                mock_manager.call_args[0][2],
            )
            self.assertEqual("julia hello.jl arg1 arg2", mock_manager.call_args[0][3])  # alias
        # With tool and tool spec cmd line args
        instance = self._make_julia_tool_instance(False, ["arg3"])
        with mock.patch("spine_items.tool.tool_instance.JuliaPersistentExecutionManager") as mock_manager, mock.patch(
            "os.path.isfile"
        ) as mock_isfile, mock.patch("spine_items.tool.utils.resolve_julia_executable") as mock_resolve_julia:
            mock_isfile.return_value = False
            mock_manager.return_value = True
            mock_resolve_julia.return_value = "path/to/julia"
            instance.prepare(["arg1", "arg2"])
            mock_isfile.assert_called()
            mock_manager.assert_called_once()
            mock_resolve_julia.assert_called()
            self.assertEqual(["path/to/julia"], mock_manager.call_args[0][1])
            self.assertEqual(
                ['cd("path/");', 'empty!(ARGS); append!(ARGS, ["arg3", "arg1", "arg2"]);', 'include("hello.jl")'],
                mock_manager.call_args[0][2],
            )
            self.assertEqual("julia hello.jl arg3 arg1 arg2", mock_manager.call_args[0][3])  # alias

    def test_prepare_sysimg_maker(self):
        instance = self._make_julia_tool_instance(False)
        instance._settings = FakeQSettings()
        with mock.patch("spine_items.tool.tool_instance.ProcessExecutionManager") as mock_pem, mock.patch(
            "spine_items.tool.utils.resolve_julia_executable"
        ) as mock_resolve_julia:
            mock_resolve_julia.return_value = "path/to/julia"
            instance.prepare([])
            mock_pem.assert_called_once()
            mock_resolve_julia.assert_called()
            self.assertEqual("path/to/julia", mock_pem.call_args[0][1])  # Julia exe
            self.assertEqual(["hello.jl"], mock_pem.call_args[0][2])  # script
            self.assertEqual("path/", mock_pem.call_args[1]["workdir"])  # workdir
        instance.terminate_instance()  # Increase coverage

    def test_julia_prepare_with_invalid_kernel(self):
        instance = self._make_julia_tool_instance(True)
        instance.prepare([])
        self.assertEqual(None, instance.exec_mngr)
        self.assertEqual(False, instance.is_running())
        instance.terminate_instance()  # Cover terminate_instance()

    def test_gams_prepare_with_cmd_line_arguments(self):
        # No cmd line args
        instance = self._make_gams_tool_instance()
        path_to_gams = "path/to/gams"
        with mock.patch("spine_items.tool.tool_instance.ProcessExecutionManager") as mock_manager, mock.patch(
            "spine_items.tool.tool_instance.resolve_gams_executable"
        ) as mock_gams_exe:
            mock_manager.return_value = True
            mock_gams_exe.return_value = path_to_gams
            instance.prepare([])
            mock_manager.assert_called()
            mock_gams_exe.assert_called()
            self.assertEqual(path_to_gams, instance.program)
            self.assertEqual(3, len(instance.args))
            self.assertEqual("model.gms", instance.args[0])
            self.assertEqual("curDir=path/", instance.args[1])
            self.assertEqual("logoption=3", instance.args[2])
        # With tool cmd line args
        instance = self._make_gams_tool_instance()
        path_to_gams = "path/to/gams"
        with mock.patch("spine_items.tool.tool_instance.ProcessExecutionManager") as mock_manager, mock.patch(
            "spine_items.tool.tool_instance.resolve_gams_executable"
        ) as mock_gams_exe:
            mock_manager.return_value = True
            mock_gams_exe.return_value = path_to_gams
            instance.prepare(["arg1", "arg2"])
            mock_manager.assert_called()
            mock_gams_exe.assert_called()
            self.assertEqual(path_to_gams, instance.program)
            self.assertEqual(5, len(instance.args))
            self.assertEqual("model.gms", instance.args[0])
            self.assertEqual("curDir=path/", instance.args[1])
            self.assertEqual("logoption=3", instance.args[2])
            self.assertEqual("arg1", instance.args[3])
            self.assertEqual("arg2", instance.args[4])
        # With tool and tool spec cmd line args
        instance = self._make_gams_tool_instance(tool_spec_args=["arg3"])
        path_to_gams = "path/to/gams"
        with mock.patch("spine_items.tool.tool_instance.ProcessExecutionManager") as mock_manager, mock.patch(
            "spine_items.tool.tool_instance.resolve_gams_executable"
        ) as mock_gams_exe:
            mock_manager.return_value = True
            mock_gams_exe.return_value = path_to_gams
            instance.prepare(["arg1", "arg2"])
            mock_manager.assert_called()
            mock_gams_exe.assert_called()
            self.assertEqual(path_to_gams, instance.program)
            self.assertEqual(6, len(instance.args))
            self.assertEqual("model.gms", instance.args[0])
            self.assertEqual("curDir=path/", instance.args[1])
            self.assertEqual("logoption=3", instance.args[2])
            self.assertEqual("arg3", instance.args[3])
            self.assertEqual("arg1", instance.args[4])
            self.assertEqual("arg2", instance.args[5])

    def test_executable_prepare_with_main_program(self):
        instance = self._make_executable_tool_instance(tool_spec_args=["arg3"])
        # when os.path.isfile fails, we throw a RuntimeError
        self.assertRaises(RuntimeError, instance.prepare, ["arg1", "arg2"])
        # Test when sys.platform is win32
        with mock.patch("spine_items.tool.tool_instance.ProcessExecutionManager") as mock_manager, mock.patch(
            "os.path.isfile"
        ) as mock_isfile, mock.patch("sys.platform", "win32"):
            mock_isfile.return_value = True
            mock_manager.return_value = True
            instance.prepare(["arg1", "arg2"])  # With tool cmd line args
            self.assertEqual(1, mock_manager.call_count)
            self.assertEqual(1, mock_isfile.call_count)
            self.assertEqual("path/program.exe", instance.program)
            self.assertEqual(3, len(instance.args))
            self.assertEqual(["arg3", "arg1", "arg2"], instance.args)
            instance = self._make_executable_tool_instance()
            instance.prepare([])  # Without cmd line args
            self.assertEqual(2, mock_manager.call_count)
            self.assertEqual(2, mock_isfile.call_count)
            self.assertEqual("path/program.exe", instance.program)
            self.assertEqual(0, len(instance.args))
        # Test when sys.platform is linux
        with mock.patch("spine_items.tool.tool_instance.ProcessExecutionManager") as mock_manager, mock.patch(
            "os.path.isfile"
        ) as mock_isfile, mock.patch("sys.platform", "linux"):
            instance = self._make_executable_tool_instance(tool_spec_args=["arg3"])
            mock_isfile.return_value = True
            mock_manager.return_value = True
            instance.prepare(["arg1", "arg2"])  # With cmd line args
            self.assertEqual(1, mock_manager.call_count)
            self.assertEqual(1, mock_isfile.call_count)
            self.assertEqual("sh", instance.program)
            self.assertEqual(4, len(instance.args))
            self.assertEqual(["path/program.exe", "arg3", "arg1", "arg2"], instance.args)

    def test_executable_prepare_with_cmd(self):
        instance = self._make_executable_tool_instance(shell="cmd.exe", cmd="dir", tool_spec_args=["arg3"])
        with mock.patch("spine_items.tool.tool_instance.ProcessExecutionManager") as mock_manager:
            # Run command with cmd.exe
            mock_manager.return_value = True
            instance.prepare(["arg1", "arg2"])
            self.assertEqual(1, mock_manager.call_count)
            self.assertEqual("cmd.exe", instance.program)
            self.assertEqual(5, len(instance.args))
            self.assertEqual(["/C", "dir", "arg3", "arg1", "arg2"], instance.args)
            # Run command with bash shell
            instance = self._make_executable_tool_instance(shell="bash", cmd="ls")
            instance.prepare(["-a"])
            self.assertEqual(2, mock_manager.call_count)
            self.assertEqual("sh", instance.program)
            self.assertEqual(2, len(instance.args))
            self.assertEqual(["ls", "-a"], instance.args)
            # Run command without shell
            instance = self._make_executable_tool_instance(cmd="cat")
            instance.prepare(["file.txt"])
            self.assertEqual(3, mock_manager.call_count)
            self.assertEqual("cat", instance.program)
            self.assertEqual(1, len(instance.args))
            self.assertEqual(["file.txt"], instance.args)

    def test_execute_julia_tool_instance(self):
        instance = self._make_julia_tool_instance(False)
        self.execute_fake_python_julia_and_executable_tool_instances(instance)

    def test_execute_python_tool_instance(self):
        instance = self._make_python_tool_instance(False)
        self.execute_fake_python_julia_and_executable_tool_instances(instance)

    def test_execute_executable_tool_instance(self):
        instance = self._make_executable_tool_instance("cmd.exe", cmd="dir")
        self.execute_fake_python_julia_and_executable_tool_instances(instance)

    def execute_fake_python_julia_and_executable_tool_instances(self, instance):
        """Python and Julia Tool Specification return codes are the same."""
        instance.exec_mngr = FakeExecutionManager(0)  # Valid return code
        self.assertEqual(0, instance.execute())
        instance.exec_mngr = FakeExecutionManager(-1)  # Valid return code
        self.assertEqual(-1, instance.execute())
        instance.exec_mngr = FakeExecutionManager(1)  # Invalid return code
        self.assertEqual(1, instance.execute())

    def test_execute_gams_tool_instance(self):
        temp_dir = TemporaryDirectory()
        instance = self._make_gams_tool_instance(temp_dir.name)
        instance.exec_mngr = FakeExecutionManager(0)  # Valid return code
        self.assertEqual(0, instance.execute())
        instance.exec_mngr = FakeExecutionManager(1)  # Valid return code
        self.assertEqual(1, instance.execute())  # This creates a GAMS project file for debugging
        debug_gpr_path = Path(temp_dir.name) / "specification_name_autocreated.gpr"
        self.assertTrue(debug_gpr_path.is_file())
        debug_gpr_path.unlink()  # Remove file (Path.unlink is equivalent to os.remove)
        self.assertFalse(debug_gpr_path.is_file())
        instance.exec_mngr = FakeExecutionManager(-1)  # Invalid return code
        self.assertEqual(-1, instance.execute())  # This creates a GAMS project file for debugging
        self.assertTrue(debug_gpr_path.is_file())
        temp_dir.cleanup()

    @staticmethod
    def _make_python_tool_instance(use_jupyter_console, tool_spec_args=None):
        specification = PythonTool(
            "specification name",
            "python",
            "",
            ["main.py"],
            MockQSettings(),
            mock.MagicMock(),
            cmdline_args=tool_spec_args,
        )
        specification.init_execution_settings()
        if use_jupyter_console:
            specification.execution_settings["use_jupyter_console"] = True
            specification.execution_settings["kernel_spec_name"] = "some_kernel"
        return specification.create_tool_instance("path/", False, logger=mock.MagicMock(), owner=mock.MagicMock())

    @staticmethod
    def _make_julia_tool_instance(use_jupyter_console, tool_spec_args=None):
        specification = JuliaTool(
            "specification name",
            "julia",
            "",
            ["hello.jl"],
            MockQSettings(),
            mock.MagicMock(),
            cmdline_args=tool_spec_args,
        )
        specification.init_execution_settings()
        if use_jupyter_console:
            specification.execution_settings["use_jupyter_console"] = True
            specification.execution_settings["kernel_spec_name"] = "some_julia_kernel"
        return specification.create_tool_instance("path/", False, logger=mock.MagicMock(), owner=mock.MagicMock())

    @staticmethod
    def _make_gams_tool_instance(temp_dir=None, tool_spec_args=None):
        path = temp_dir if temp_dir else ""
        specification = GAMSTool(
            "specification name",
            "gams",
            path,
            ["model.gms"],
            MockQSettings(),
            mock.MagicMock(),
            cmdline_args=tool_spec_args,
        )
        return specification.create_tool_instance("path/", False, logger=mock.MagicMock(), owner=mock.MagicMock())

    @staticmethod
    def _make_executable_tool_instance(shell=None, cmd=None, tool_spec_args=None):
        if cmd:
            specification = ExecutableTool(
                "name", "executable", "", [], MockQSettings(), mock.MagicMock(), cmdline_args=tool_spec_args
            )
        else:
            specification = ExecutableTool(
                "name",
                "executable",
                "",
                ["program.exe"],
                MockQSettings(),
                mock.MagicMock(),
                cmdline_args=tool_spec_args,
            )
        specification.init_execution_settings()
        if shell == "cmd.exe":
            specification.execution_settings["shell"] = "cmd.exe"
        elif shell == "bash":
            specification.execution_settings["shell"] = "bash"
        if cmd:
            specification.execution_settings["cmd"] = cmd
        return specification.create_tool_instance("path/", False, logger=mock.MagicMock(), owner=mock.MagicMock())


class FakeExecutionManager:
    def __init__(self, retval):
        self.retval = retval

    def run_until_complete(self):
        return self.retval


class FakeQSettings:
    def value(self, key, defaultValue=""):
        if key == "appSettings/makeSysImage":
            return "true"


if __name__ == "__main__":
    unittest.main()
