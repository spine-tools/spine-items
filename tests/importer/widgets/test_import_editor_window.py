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

"""Unit tests for the ``import_editor_window`` module."""
from tempfile import TemporaryDirectory
import unittest
from unittest import mock
from PySide6.QtWidgets import QApplication, QDialog
from spine_items.importer.widgets.import_editor_window import ImportEditorWindow
from spinedb_api.spine_io.importers.sqlalchemy_connector import SqlAlchemyConnector
from tests.mock_helpers import clean_up_toolbox, create_toolboxui_with_project


class TestIsUrl(unittest.TestCase):
    def test_url_is_url(self):
        self.assertTrue(ImportEditorWindow._is_url("sqlite:///C:\\data\\db.sqlite"))
        self.assertTrue(ImportEditorWindow._is_url("postgresql+psycopg://spuser:s3cr3t@server.com/db"))

    def test_non_url_is_not_url(self):
        self.assertFalse(ImportEditorWindow._is_url("C:\\path\\to\\file"))
        self.assertFalse(ImportEditorWindow._is_url("/unix/style/path"))


class TestImportEditorWindow(unittest.TestCase):
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

    def test_get_connector_selects_sql_alchemy_connector_when_source_is_url(self):
        with mock.patch("spine_items.importer.widgets.import_editor_window.QDialog.exec") as exec_dialog:
            exec_dialog.return_value = QDialog.DialogCode.Accepted
            editor = ImportEditorWindow(self._toolbox, None)
            exec_dialog.assert_called_once()
            exec_dialog.reset_mock()
            connector = editor._get_connector("mysql://server.com/db")
            exec_dialog.assert_called_once()
            editor.close()
        self.assertIs(connector, SqlAlchemyConnector)


if __name__ == "__main__":
    unittest.main()
