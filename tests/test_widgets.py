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
import unittest
from unittest import mock
from PySide6.QtWidgets import QApplication
from spine_items.widgets import UrlSelectorWidget
from tests.mock_helpers import parent_widget


class TestUrlSelectorWidget(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def test_first_dialect_is_selected_in_combo_box(self):
        with parent_widget() as parent:
            widget = UrlSelectorWidget(parent)
            callback = mock.MagicMock()
            logger = mock.MagicMock()
            widget.setup(["dialect 1", "dialect 2"], callback, False, logger)
            widget.set_url({})
            self.assertEqual(widget._ui.comboBox_dialect.currentIndex(), 0)


if __name__ == "__main__":
    unittest.main()
