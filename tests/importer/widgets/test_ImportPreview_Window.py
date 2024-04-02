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

""" Contains unit tests for the ImportEditorWindow class. """
import unittest
from unittest import mock
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QWidget
from spine_items.importer.widgets.import_editor_window import ImportEditorWindow
from spinedb_api.spine_io.importers.csv_reader import CSVConnector


class TestImportEditorWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def test_closeEvent(self):
        spec = mock.NonCallableMagicMock()
        spec.name = "spec_name"
        spec.description = "spec_desc"
        spec.mapping = {"source_type": CSVConnector.__name__}
        toolbox = QWidget()
        toolbox.qsettings = mock.MagicMock(return_value=QSettings(toolbox))
        toolbox.restore_and_activate = mock.MagicMock()
        widget = ImportEditorWindow(toolbox, spec)
        widget._app_settings = mock.NonCallableMagicMock()
        widget.close()
        widget._app_settings.beginGroup.assert_called_once_with("mappingPreviewWindow")
        widget._app_settings.endGroup.assert_called_once_with()
        qsettings_save_calls = widget._app_settings.setValue.call_args_list
        self.assertEqual(len(qsettings_save_calls), 8)
        saved_dict = {saved[0][0]: saved[0][1] for saved in qsettings_save_calls}
        self.assertEqual(len(saved_dict), 8)
        for key in (
            "windowSize",
            "windowPosition",
            "windowState",
            "windowMaximized",
            "n_screens",
            "splitter_source_listState",
            "splitter_source_data_mappingsState",
            "splitterState",
        ):
            with self.subTest(key=key):
                self.assertIn(key, saved_dict)
        toolbox.deleteLater()


if __name__ == "__main__":
    unittest.main()
