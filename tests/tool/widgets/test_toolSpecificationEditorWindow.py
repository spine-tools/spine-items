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
Unit tests for ToolSpecificationEditorWindow class.

"""

import unittest
import logging
import sys
from unittest import mock
from tempfile import NamedTemporaryFile
from pathlib import Path
from PySide6.QtWidgets import QApplication
from spine_items.tool.widgets.tool_specification_editor_window import ToolSpecificationEditorWindow
from tests.mock_helpers import create_mock_toolbox


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
        self.toolbox = create_mock_toolbox()
        with mock.patch("spinetoolbox.project_item.specification_editor_window.restore_ui"):
            self.tool_specification_widget = ToolSpecificationEditorWindow(self.toolbox)

    def tearDown(self):
        """Overridden method. Runs after each test.
        Use this to free resources after a test if needed.
        """
        self.tool_specification_widget.deleteLater()
        self.tool_specification_widget = None

    def test_create_minimal_julia_tool_specification(self):
        self.tool_specification_widget._ui.comboBox_tooltype.setCurrentIndex(0)  # 0: Julia
        self.tool_specification_widget._spec_toolbar._line_edit_name.setText("test_tool")
        with NamedTemporaryFile(mode="r") as temp_file:
            self.tool_specification_widget._set_main_program_file(str(Path(temp_file.name)))
            self.tool_specification_widget._save()

    def test_create_minimal_gams_tool_specification(self):
        self.tool_specification_widget._ui.comboBox_tooltype.setCurrentIndex(2)  # 2: gams
        self.tool_specification_widget._spec_toolbar._line_edit_name.setText("test_tool")
        with NamedTemporaryFile(mode="r") as temp_file:
            self.tool_specification_widget._set_main_program_file(str(Path(temp_file.name)))
            self.tool_specification_widget._save()

    def test_create_minimal_executable_tool_specification(self):
        self.tool_specification_widget._ui.comboBox_tooltype.setCurrentIndex(3)  # 3: executable
        self.tool_specification_widget._spec_toolbar._line_edit_name.setText("test_tool")
        with NamedTemporaryFile(mode="r") as temp_file:
            self.tool_specification_widget._set_main_program_file(str(Path(temp_file.name)))
            self.tool_specification_widget._save()

    # @unittest.skip("Obsolete")
    # def test_add_cmdline_tag_url_inputs(self):
    #     self._test_add_cmdline_tag_on_empty_args_field("@@url_inputs@@")
    #
    # @unittest.skip("Obsolete")
    # def test_add_cmdline_tag_url_inputs_middle_of_other_tags(self):
    #     self._test_add_cmdline_tag_middle_of_other_tags("@@url_inputs@@")
    #
    # @unittest.skip("Obsolete")
    # def test_add_cmdline_tag_url_inputs_no_space_before_regular_arg(self):
    #     self._test_add_cmdline_tag_adds_no_space_before_regular_arg("@@url_inputs@@")
    #
    # @unittest.skip("Obsolete")
    # def test_add_cmdline_tag_url_outputs(self):
    #     self._test_add_cmdline_tag_on_empty_args_field("@@url_outputs@@")
    #
    # @unittest.skip("Obsolete")
    # def test_add_cmdline_tag_url_outputs_middle_of_other_tags(self):
    #     self._test_add_cmdline_tag_middle_of_other_tags("@@url_outputs@@")
    #
    # @unittest.skip("Obsolete")
    # def test_add_cmdline_tag_url_outputs_no_space_before_regular_arg(self):
    #     self._test_add_cmdline_tag_adds_no_space_before_regular_arg("@@url_outputs@@")
    #
    # @unittest.skip("Obsolete")
    # def test_add_cmdline_tag_data_store_url(self):
    #     self._test_add_cmdline_tag_on_empty_args_field("@@url:<data-store-name>@@")
    #     selection = self.tool_specification_widget.ui.lineEdit_args.selectedText()
    #     self.assertEqual(selection, "<data-store-name>")
    #
    # @unittest.skip("Obsolete")
    # def test_add_cmdline_tag_data_store_url_middle_of_other_tags(self):
    #     self._test_add_cmdline_tag_middle_of_other_tags("@@url:<data-store-name>@@")
    #     selection = self.tool_specification_widget.ui.lineEdit_args.selectedText()
    #     self.assertEqual(selection, "<data-store-name>")
    #
    # @unittest.skip("Obsolete")
    # def test_add_cmdline_tag_data_store_url_no_space_before_regular_arg(self):
    #     self._test_add_cmdline_tag_adds_no_space_before_regular_arg("@@url:<data-store-name>@@")
    #     selection = self.tool_specification_widget.ui.lineEdit_args.selectedText()
    #     self.assertEqual(selection, "<data-store-name>")
    #
    # @unittest.skip("Obsolete")
    # def test_add_cmdline_tag_optional_inputs(self):
    #     self._test_add_cmdline_tag_on_empty_args_field("@@optional_inputs@@")
    #
    # @unittest.skip("Obsolete")
    # def test_add_cmdline_tag_optional_inputs_middle_of_other_tags(self):
    #     self._test_add_cmdline_tag_middle_of_other_tags("@@optional_inputs@@")
    #
    # @unittest.skip("Obsolete")
    # def test_add_cmdline_tag_optional_inputs_no_space_before_regular_arg(self):
    #     self._test_add_cmdline_tag_adds_no_space_before_regular_arg("@@optional_inputs@@")
    #
    # def _find_action(self, action_text, actions):
    #     found_action = None
    #     for action in actions:
    #         if action.text() == action_text:
    #             found_action = action
    #             break
    #     self.assertIsNotNone(found_action)
    #     return found_action
    #
    # def _test_add_cmdline_tag_on_empty_args_field(self, tag):
    #     menu = self.tool_specification_widget.ui.toolButton_add_cmdline_tag.menu()
    #     url_inputs_action = self._find_action(tag, menu.actions())
    #     url_inputs_action.trigger()
    #     args = self.tool_specification_widget.ui.lineEdit_args.text()
    #     expected = tag + " "
    #     self.assertEqual(args, expected)
    #     if not self.tool_specification_widget.ui.lineEdit_args.hasSelectedText():
    #         cursor_position = self.tool_specification_widget.ui.lineEdit_args.cursorPosition()
    #         self.assertEqual(cursor_position, len(expected))
    #
    # def _test_add_cmdline_tag_middle_of_other_tags(self, tag):
    #     self.tool_specification_widget.ui.lineEdit_args.setText("@@optional_inputs@@@@url_outputs@@")
    #     self.tool_specification_widget.ui.lineEdit_args.setCursorPosition(len("@@optional_inputs@@"))
    #     menu = self.tool_specification_widget.ui.toolButton_add_cmdline_tag.menu()
    #     url_inputs_action = self._find_action(tag, menu.actions())
    #     url_inputs_action.trigger()
    #     args = self.tool_specification_widget.ui.lineEdit_args.text()
    #     self.assertEqual(args, f"@@optional_inputs@@ {tag} @@url_outputs@@")
    #     if not self.tool_specification_widget.ui.lineEdit_args.hasSelectedText():
    #         cursor_position = self.tool_specification_widget.ui.lineEdit_args.cursorPosition()
    #         self.assertEqual(cursor_position, len(f"@@optional_inputs@@ {tag} "))
    #
    # def _test_add_cmdline_tag_adds_no_space_before_regular_arg(self, tag):
    #     self.tool_specification_widget.ui.lineEdit_args.setText("--tag=")
    #     self.tool_specification_widget.ui.lineEdit_args.setCursorPosition(len("--tag="))
    #     menu = self.tool_specification_widget.ui.toolButton_add_cmdline_tag.menu()
    #     url_inputs_action = self._find_action(tag, menu.actions())
    #     url_inputs_action.trigger()
    #     args = self.tool_specification_widget.ui.lineEdit_args.text()
    #     self.assertEqual(args, f"--tag={tag} ")
    #     if not self.tool_specification_widget.ui.lineEdit_args.hasSelectedText():
    #         cursor_position = self.tool_specification_widget.ui.lineEdit_args.cursorPosition()
    #         self.assertEqual(cursor_position, len(f"--tag={tag} "))


if __name__ == "__main__":
    unittest.main()
