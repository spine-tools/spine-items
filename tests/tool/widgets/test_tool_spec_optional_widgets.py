######################################################################################################################
# Copyright (C) 2017-2021 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Unit tests for tool_spec_optional_widgets module.

:author: A. Soininen (VTT)
:date:   4.8.2022
"""
import unittest
from PySide2.QtWidgets import QApplication, QUndoStack
from spine_items.tool.widgets.tool_spec_optional_widgets import ExecutableToolSpecOptionalWidget


class TestExecutableToolSpecOptionalWidget(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        self._undo_stack = QUndoStack()

    def tearDown(self):
        self._undo_stack.deleteLater()

    def test_command_line_edit_initially_empty(self):
        opt_widget = ExecutableToolSpecOptionalWidget(self._undo_stack)
        self.assertEqual(opt_widget._ui.lineEdit_command.text(), "")

    def test_specification_dict_data(self):
        opt_widget = ExecutableToolSpecOptionalWidget(self._undo_stack)
        opt_widget._ui.lineEdit_command.setText("my command")
        opt_widget._ui.lineEdit_command.editingFinished.emit()
        QApplication.processEvents()
        self.assertEqual(opt_widget._ui.lineEdit_command.text(), "my command")
        self.assertEqual(opt_widget.specification_dict_data(), {"command": "my command"})


if __name__ == '__main__':
    unittest.main()
