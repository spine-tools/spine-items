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

"""Unit tests for ExporterIcon class."""
from tempfile import TemporaryDirectory
import unittest
from unittest import mock
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication, QGraphicsSceneMouseEvent
from spine_items.exporter.exporter_factory import ExporterFactory
from tests.mock_helpers import clean_up_toolbox, create_toolboxui_with_project


class TestExporterIcon(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        super().setUp()
        self._temp_dir = TemporaryDirectory()
        self._toolbox = create_toolboxui_with_project(self._temp_dir.name)
        item_dict = {"type": "Exporter", "description": "", "x": 0, "y": 0, "specification": None}
        exp = ExporterFactory.make_item("E", item_dict, self._toolbox, self._toolbox.project())
        self._toolbox.project().add_item(exp)

    def tearDown(self):
        super().tearDown()
        clean_up_toolbox(self._toolbox)
        self._temp_dir.cleanup()

    def test_mouse_double_click_event(self):
        icon = self._toolbox.project()._project_items["E"].get_icon()
        with mock.patch("spine_items.exporter.exporter.Exporter.show_specification_window") as mock_show_spec_window:
            mock_show_spec_window.return_value = True
            icon.mouseDoubleClickEvent(QGraphicsSceneMouseEvent(QEvent.Type.GraphicsSceneMouseDoubleClick))
            mock_show_spec_window.assert_called()


if __name__ == "__main__":
    unittest.main()
