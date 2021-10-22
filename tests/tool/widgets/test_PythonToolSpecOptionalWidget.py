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
Unit tests for PythonToolSpecOptionalWidget class.

:author: P. Savolainen (VTT)
:date:   2.7.2021
"""

import unittest
from unittest import mock
import logging
import sys
from PySide2.QtWidgets import QApplication, QWidget
from spine_items.tool.widgets.tool_spec_optional_widgets import PythonToolSpecOptionalWidget


class TestPythonToolSpecOptionalWidget(unittest.TestCase):
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

    def test_constructor(self):
        with mock.patch(
            "spine_items.tool.widgets.tool_spec_optional_widgets.PythonToolSpecOptionalWidget._toolbox"
        ) as mock_toolbox:
            mock_toolbox.qsettings.return_value = MockQSettings()
            opt_widget = PythonToolSpecOptionalWidget(mock_toolbox)
        self.assertIsInstance(opt_widget, PythonToolSpecOptionalWidget)


class MockQSettings:
    def value(self, key, defaultValue=""):
        return defaultValue
