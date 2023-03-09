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
"""Unit tests for ``tool_specifications`` module."""
import unittest
from unittest.mock import MagicMock
from spine_items.tool.tool_specifications import ToolSpecification


class TestToolSpecification(unittest.TestCase):
    def test_to_dict_sorts_input_and_output_files(self):
        app_settings = MagicMock()
        logger = MagicMock()
        specification = ToolSpecification(
            "specification name",
            "Python",
            "/path/to/tool",
            ["/included_file_1.bat", "/aa/included_file_2.std"],
            app_settings,
            logger,
            "Test tool specification",
            ["b_input.png", "a_input.jpg"],
            ["*.dat", "a.csv", "z.zip", "*.xlsx"],
            ["*.zip", "*.atk"],
            ["99", "10"],
        )
        specification.definition_file_path = "/path/to/specification/file.json"
        specification_dict = specification.to_dict()
        self.assertEqual(
            specification_dict,
            {
                "name": "specification name",
                "tooltype": "Python",
                "includes": ["/included_file_1.bat", "/aa/included_file_2.std"],
                "description": "Test tool specification",
                "inputfiles": ["a_input.jpg", "b_input.png"],
                "inputfiles_opt": ["*.dat", "*.xlsx", "a.csv", "z.zip"],
                "outputfiles": ["*.atk", "*.zip"],
                "cmdline_args": ["99", "10"],
                "includes_main_path": "../tool",
            },
        )


if __name__ == '__main__':
    unittest.main()
