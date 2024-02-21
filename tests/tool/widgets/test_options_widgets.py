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

"""Unit tests for the options_widgets.py module."""
import unittest
import logging
import sys
from PySide6.QtWidgets import QApplication, QWidget
from spine_items.tool.widgets.options_widgets import JuliaOptionsWidget


class TestJuliaOptionsWidget(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Overridden method. Runs once before all tests in this class."""
        try:
            cls.app = QApplication().processEvents()
        except RuntimeError:
            pass
        logging.basicConfig(
            stream=sys.stderr,
            level=logging.WARNING,
            format="%(asctime)s %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def test_options_widget(self):
        ow = JuliaOptionsWidget()
        ow.set_tool(QWidget())  # Obviously not a real Tool
        ow._set_ui_at_work()
        ow._set_ui_at_rest()
        options = {"julia_sysimage": "/some/path"}
        ow.do_update_options(options)
        self.assertEqual("/some/path", ow.ui.lineEdit_sysimage.text())
