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

"""Unit tests for ImporterIcon class."""
import unittest
from unittest import mock
from tempfile import TemporaryDirectory
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication, QGraphicsSceneMouseEvent
from tests.mock_helpers import create_toolboxui_with_project, clean_up_toolbox
from spine_items.importer.importer_factory import ImporterFactory


class TestImporterIcon(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        super().setUp()
        self._temp_dir = TemporaryDirectory()
        self._toolbox = create_toolboxui_with_project(self._temp_dir.name)
        item_dict = {"type": "Importer", "description": "", "x": 0, "y": 0, "specification": None}
        exp = ImporterFactory.make_item("I", item_dict, self._toolbox, self._toolbox.project())
        self._toolbox.project().add_item(exp)

    def tearDown(self):
        super().tearDown()
        clean_up_toolbox(self._toolbox)
        self._temp_dir.cleanup()

    def test_mouse_double_click_event(self):
        icon = self._toolbox.project()._project_items["I"].get_icon()
        with mock.patch("spine_items.importer.importer.Importer.open_import_editor") as mock_open_import_editor:
            mock_open_import_editor.return_value = True
            icon.mouseDoubleClickEvent(QGraphicsSceneMouseEvent(QEvent.Type.GraphicsSceneMouseDoubleClick))
            mock_open_import_editor.assert_called()


if __name__ == "__main__":
    unittest.main()
