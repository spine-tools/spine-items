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
Unit tests for PythonToolSpecOptionalWidget class.

"""

import unittest
from unittest import mock
from unittest.mock import MagicMock
import logging
import sys
from PySide6.QtWidgets import QApplication, QWidget
from spine_items.tool.widgets.tool_spec_optional_widgets import PythonToolSpecOptionalWidget
from spine_items.tool.tool_specifications import PythonTool


class TestPythonToolSpecOptionalWidget(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Overridden method. Runs once before all tests in this class."""
        try:
            cls.app = QApplication().processEvents()
        except RuntimeError:
            pass
        logging.basicConfig(
            stream=sys.stderr,
            level=logging.WARNING,
            format="%(asctime)s %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def test_constructor_and_init(self):
        with mock.patch(
            "spine_items.tool.widgets.tool_spec_optional_widgets.PythonToolSpecOptionalWidget._toolbox"
        ) as mock_toolbox:
            mock_toolbox.qsettings.return_value = MockQSettings()
            mock_logger = MagicMock()
            python_tool_spec = PythonTool("a", "python", "", ["fake_main_program.py"], MockQSettings(), mock_logger)
            python_tool_spec.set_execution_settings()  # Sets defaults
            python_tool_spec.execution_settings["executable"] = "fake_python.exe"
            opt_widget = PythonToolSpecOptionalWidget(mock_toolbox)
            opt_widget.init_widget(python_tool_spec)
            self.assertEqual("fake_python.exe", opt_widget.get_executable())
        self.assertIsInstance(opt_widget, PythonToolSpecOptionalWidget)


class MockQSettings:
    def value(self, key, defaultValue=""):
        return defaultValue
