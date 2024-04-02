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

"""Unit tests for ``tool_specifications`` module."""
import os
import unittest
from unittest import mock
from tempfile import TemporaryDirectory
from spine_items.tool.tool_specifications import (
    ToolSpecification,
    make_specification,
    PythonTool,
    JuliaTool,
    GAMSTool,
    ExecutableTool,
)
from spine_engine.spine_engine import SpineEngine
from spine_engine.project_item.connection import Jump
from tests.mock_helpers import MockQSettings


class TestToolSpecification(unittest.TestCase):
    def setUp(self) -> None:
        self.qsettings = MockQSettings()
        self.logger = mock.MagicMock()
        self.test_dict = {
            "name": "specification name",
            "tooltype": "Python",
            "includes": ["/included_file_1.bat", "/aa/included_file_2.std"],
            "description": "Test tool specification",
            "inputfiles": ["a_input.jpg", "b_input.png"],
            "inputfiles_opt": ["*.dat", "*.xlsx", "a.csv", "z.zip"],
            "outputfiles": ["*.atk", "*.zip"],
            "cmdline_args": ["99", "10"],
            "includes_main_path": "../tool",
        }

    def test_to_dict_sorts_input_and_output_files(self):
        specification = ToolSpecification(
            "specification name",
            "Python",
            "/path/to/tool",
            ["/included_file_1.bat", "/aa/included_file_2.std"],
            self.qsettings,
            self.logger,
            "Test tool specification",
            ["b_input.png", "a_input.jpg"],
            ["*.dat", "a.csv", "z.zip", "*.xlsx"],
            ["*.zip", "*.atk"],
            ["99", "10"],
        )
        specification.definition_file_path = "/path/to/specification/file.json"
        specification_dict = specification.to_dict()
        self.assertEqual(specification_dict, self.test_dict)

    def test_make_specification(self):
        self.test_dict["definition_file_path"] = "/path/to/specification/file.json"
        spec = make_specification(self.test_dict, self.qsettings, self.logger)  # Make PythonTool
        self.assertIsInstance(spec, PythonTool)
        spec.init_execution_settings()
        self.assertIsNotNone(spec.execution_settings)
        self.assertTrue(len(spec.execution_settings.keys()), 4)
        spec.to_dict()
        # Convert to Julia spec
        self.test_dict["tooltype"] = "Julia"
        spec = make_specification(self.test_dict, self.qsettings, self.logger)  # Make JuliaTool
        self.assertIsInstance(spec, JuliaTool)
        spec.init_execution_settings()
        self.assertIsNotNone(spec.execution_settings)
        self.assertTrue(len(spec.execution_settings.keys()), 5)
        spec.to_dict()
        # Convert to GAMS spec
        self.test_dict["tooltype"] = "GAMS"
        spec = make_specification(self.test_dict, self.qsettings, self.logger)  # Make GAMSTool
        self.assertIsInstance(spec, GAMSTool)
        spec.to_dict()
        # Convert to Executable spec
        self.test_dict["tooltype"] = "Executable"
        spec = make_specification(self.test_dict, self.qsettings, self.logger)  # Make ExecutableTool
        self.assertIsInstance(spec, ExecutableTool)
        spec.init_execution_settings()
        self.assertIsNotNone(spec.execution_settings)
        self.assertTrue(len(spec.execution_settings.keys()), 2)
        spec.to_dict()

    def test_clone(self):
        self.test_dict["definition_file_path"] = "/path/to/specification/file.json"
        spec = make_specification(self.test_dict, self.qsettings, self.logger)
        cloned_spec = spec.clone()
        self.assertFalse(spec.is_equivalent(cloned_spec))  # False because 'path' is different. Bug?

    def test_tool_specification_as_jump_condition(self):
        condition = {"type": "tool-specification", "specification": "loop_twice"}
        jump = Jump("source", "bottom", "destination", "top", condition)
        jump.make_logger(mock.Mock())
        with TemporaryDirectory() as temp_dir:
            main_file = "script.py"
            main_file_path = os.path.join(temp_dir, main_file)
            with open(main_file_path, "w+") as program_file:
                program_file.writelines(
                    ["import sys\n", "counter = int(sys.argv[1])\n", "exit(0 if counter == 23 else 1)\n"]
                )
            spec_dict = {
                "name": "loop_twice",
                "tooltype": "python",
                "includes_main_path": temp_dir,
                "includes": [main_file],
                "definition_file_path": "path/to/specification_file.json",
            }
            engine = SpineEngine(project_dir=temp_dir, specifications={"Tool": [spec_dict]}, connections=list())
            jump.set_engine(engine)
            self.assertTrue(jump.is_condition_true(23))


if __name__ == "__main__":
    unittest.main()
