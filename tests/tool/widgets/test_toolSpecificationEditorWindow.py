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

"""Unit tests for ToolSpecificationEditorWindow class."""

import unittest
import logging
import sys
from unittest import mock
from tempfile import NamedTemporaryFile
from pathlib import Path
from PySide6.QtWidgets import QApplication
from spine_items.tool.widgets.tool_specification_editor_window import ToolSpecificationEditorWindow
from spine_items.tool.widgets.tool_spec_optional_widgets import (
    JuliaToolSpecOptionalWidget,
    PythonToolSpecOptionalWidget,
    ExecutableToolSpecOptionalWidget,
)
from tests.mock_helpers import create_mock_toolbox_with_mock_qsettings


class TestToolSpecificationEditorWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Overridden method. Runs once before all tests in this class."""
        try:
            cls.app = QApplication().processEvents()
        except RuntimeError:
            pass
        logging.basicConfig(
            stream=sys.stderr,
            level=logging.DEBUG,
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

    def test_create_minimal_julia_tool_specification(self):
        self.tool_specification_widget._ui.comboBox_tooltype.setCurrentIndex(0)  # 0: Julia
        self.assertIsInstance(self.tool_specification_widget.optional_widget, JuliaToolSpecOptionalWidget)
        self.tool_specification_widget._spec_toolbar._line_edit_name.setText("test_julia_tool")
        with NamedTemporaryFile(mode="r") as temp_file:
            self.tool_specification_widget._set_main_program_file(str(Path(temp_file.name)))
            self._call_save()

    def test_create_minimal_python_tool_specification(self):
        self.tool_specification_widget._ui.comboBox_tooltype.setCurrentIndex(1)  # 1: Python
        self.assertIsInstance(self.tool_specification_widget.optional_widget, PythonToolSpecOptionalWidget)
        self.tool_specification_widget._spec_toolbar._line_edit_name.setText("test_python_tool")
        with NamedTemporaryFile(mode="r") as temp_file:
            self.tool_specification_widget._set_main_program_file(str(Path(temp_file.name)))
            self._call_save()

    def test_create_minimal_gams_tool_specification(self):
        self.tool_specification_widget._ui.comboBox_tooltype.setCurrentIndex(2)  # 2: gams
        self.assertIsNone(self.tool_specification_widget.optional_widget)
        self.tool_specification_widget._spec_toolbar._line_edit_name.setText("test_gams_tool")
        with NamedTemporaryFile(mode="r") as temp_file:
            self.tool_specification_widget._set_main_program_file(str(Path(temp_file.name)))
            self._call_save()

    def test_create_minimal_executable_tool_specification(self):
        self.tool_specification_widget._ui.comboBox_tooltype.setCurrentIndex(3)  # 3: executable
        self.assertIsInstance(self.tool_specification_widget.optional_widget, ExecutableToolSpecOptionalWidget)
        self.tool_specification_widget._spec_toolbar._line_edit_name.setText("test_executable_tool")
        with NamedTemporaryFile(mode="r") as temp_file:
            self.tool_specification_widget._set_main_program_file(str(Path(temp_file.name)))
            self._call_save()

    def _call_save(self):
        """Calls tool spec widgets _save() while Toolbox's tool spec widget base _save() is mocked."""
        with mock.patch(
            "spinetoolbox.project_item.specification_editor_window.SpecificationEditorWindowBase._save"
        ) as mock_save:
            mock_save.return_value = True
            self.tool_specification_widget._save()
            mock_save.assert_called()


if __name__ == "__main__":
    unittest.main()
