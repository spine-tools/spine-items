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
"""Unit tests for the ``specification_editor_window`` module."""
from tempfile import TemporaryDirectory
import unittest

from PySide6.QtWidgets import QApplication

from spine_items.exporter.widgets.specification_editor_window import SpecificationEditorWindow
from ...mock_helpers import clean_up_toolbox, create_toolboxui_with_project


class TestSpecificationEditorWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        self._temp_dir = TemporaryDirectory()
        self._toolbox = create_toolboxui_with_project(self._temp_dir.name)

    def tearDown(self):
        clean_up_toolbox(self._toolbox)
        self._temp_dir.cleanup()

    def test_empty_editor(self):
        editor = SpecificationEditorWindow(self._toolbox)
        self.assertEqual(editor._ui.mappings_table.model().rowCount(), 1)
        self.assertEqual(editor._ui.mappings_table.model().index(0, 0).data(), "Mapping 1")

    def test_mapping_in_table_name_position_disables_fixed_table_name_widgets(self):
        editor = SpecificationEditorWindow(self._toolbox)
        self.assertTrue(editor._ui.fix_table_name_check_box.isEnabled())
        self.assertFalse(editor._ui.fix_table_name_check_box.isChecked())
        self.assertFalse(editor._ui.fix_table_name_line_edit.isEnabled())
        self.assertEqual(editor._ui.fix_table_name_line_edit.text(), "")
        editor._ui.mappings_table.setCurrentIndex(editor._ui.mappings_table.model().index(0, 0))
        model = editor._ui.mapping_table_view.model()
        model.setData(model.index(0, 1), "table name")
        self.assertFalse(editor._ui.fix_table_name_check_box.isEnabled())
        self.assertFalse(editor._ui.fix_table_name_check_box.isChecked())
        self.assertFalse(editor._ui.fix_table_name_line_edit.isEnabled())
        self.assertEqual(editor._ui.fix_table_name_line_edit.text(), "")


if __name__ == '__main__':
    unittest.main()
