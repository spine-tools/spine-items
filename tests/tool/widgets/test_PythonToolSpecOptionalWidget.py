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

"""Unit tests for PythonToolSpecOptionalWidget class."""

import unittest
from unittest import mock
import logging
import sys
from PySide6.QtWidgets import QApplication
from spine_items.tool.widgets.tool_specification_editor_window import ToolSpecificationEditorWindow
from spine_items.tool.widgets.tool_spec_optional_widgets import PythonToolSpecOptionalWidget
from spine_items.tool.tool_specifications import PythonTool
from tests.mock_helpers import create_mock_toolbox_with_mock_qsettings, MockQSettings


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

    def setUp(self):
        """Overridden method. Runs before each test."""
        self.toolbox = create_mock_toolbox_with_mock_qsettings()
        with mock.patch("spinetoolbox.project_item.specification_editor_window.restore_ui") as mock_restore_ui:
            self.tool_specification_widget = ToolSpecificationEditorWindow(self.toolbox)

    def tearDown(self):
        """Overridden method. Runs after each test.
        Use this to free resources after a test if needed.
        """
        self.tool_specification_widget.deleteLater()
        self.tool_specification_widget = None

    def test_constructor_and_init(self):
        mock_logger = mock.MagicMock()
        python_tool_spec = PythonTool("a", "python", "", ["fake_main_program.py"], MockQSettings(), mock_logger)
        python_tool_spec.set_execution_settings()  # Sets defaults
        python_tool_spec.execution_settings["executable"] = "fake_python.exe"
        opt_widget = PythonToolSpecOptionalWidget(self.tool_specification_widget)
        opt_widget.init_widget(python_tool_spec)
        self.assertEqual("fake_python.exe", opt_widget.get_executable())
        self.assertIsInstance(opt_widget, PythonToolSpecOptionalWidget)
