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

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
import pytest
from tests.mock_helpers import clean_up_toolbox, create_toolboxui_with_project


@pytest.fixture(scope="module")
def application():
    if QApplication.instance() is None:
        QApplication()
    application_instance = QApplication.instance()
    yield application_instance
    QTimer.singleShot(0, lambda: application_instance.quit())
    application_instance.exec()


@pytest.fixture
def spine_toolbox_with_project(application, tmp_path):
    toolbox = create_toolboxui_with_project(str(tmp_path))
    yield toolbox
    clean_up_toolbox(toolbox)
