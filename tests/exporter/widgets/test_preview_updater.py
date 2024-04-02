######################################################################################################################
# Copyright (C) 2017-2023 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""Unit tests for the ``preview_updater`` module."""
import unittest
from unittest import mock
from PySide6.QtWidgets import QApplication, QComboBox, QWidget
from spine_items.exporter.mvcmodels.full_url_list_model import FullUrlListModel
from spine_items.exporter.widgets.preview_updater import PreviewUpdater


class TestPreviewUpdater(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        self._parent_widget = QWidget()

    def tearDown(self):
        self._parent_widget.deleteLater()

    def test_deleting_url_model_does_not_break_tear_down(self):
        window = mock.MagicMock()
        ui = mock.MagicMock()
        ui.database_url_combo_box = QComboBox(self._parent_widget)
        url_model = FullUrlListModel()
        mappings_table_model = mock.MagicMock()
        mappings_proxy_model = mock.MagicMock()
        mapping_editor_table_model = mock.MagicMock()
        project_dir = ""
        preview_updater = PreviewUpdater(
            window, ui, url_model, mappings_table_model, mappings_proxy_model, mapping_editor_table_model, project_dir
        )
        # It is difficult to get the url_model deleted on C++ side.
        # We simulate it by emitting destroyed manually.
        url_model.destroyed.emit()
        self.assertIsNot(preview_updater._url_model, url_model)
        preview_updater.tear_down()


if __name__ == "__main__":
    unittest.main()
