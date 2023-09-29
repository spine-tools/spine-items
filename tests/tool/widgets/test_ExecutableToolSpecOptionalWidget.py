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

"""Unit tests for ExecutableToolSpecOptionalWidget class."""

import unittest
from unittest import mock
import logging
import sys
from PySide6.QtWidgets import QApplication
from spine_items.tool.widgets.tool_specification_editor_window import ToolSpecificationEditorWindow
from spine_items.tool.widgets.tool_spec_optional_widgets import ExecutableToolSpecOptionalWidget
from spine_items.tool.tool_specifications import ExecutableTool
from tests.mock_helpers import create_mock_toolbox_with_mock_qsettings, MockQSettings


class TestExecutableToolSpecOptionalWidget(unittest.TestCase):
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

    def tearDown(self):
        """Overridden method. Runs after each test.
        Use this to free resources after a test if needed.
        """
        self.tool_specification_widget.deleteLater()
        self.tool_specification_widget = None

    def test_open_specification_editor_with_spec(self):
        mock_logger = mock.MagicMock()
        exec_tool_spec = ExecutableTool("a", "executable", "", ["fake_main_program.bat"], MockQSettings(), mock_logger)
        exec_tool_spec.set_execution_settings()  # Sets defaults
        exec_tool_spec.execution_settings["executable"] = "fake_main_program.bat"
        with mock.patch("spinetoolbox.project_item.specification_editor_window.restore_ui") as mock_restore_ui:
            self.tool_specification_widget = ToolSpecificationEditorWindow(self.toolbox, exec_tool_spec)
        opt_widget = ExecutableToolSpecOptionalWidget(self.tool_specification_widget)
        opt_widget.init_widget(exec_tool_spec)
        self.assertIsInstance(opt_widget, ExecutableToolSpecOptionalWidget)
        exec_settings = opt_widget.add_execution_settings("executable")
        self.assertEqual(2, len(exec_settings))
        self.assertEqual("", opt_widget.get_current_shell())
