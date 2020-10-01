######################################################################################################################
# Copyright (C) 2017-2020 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Classes and functions that can be shared among unit test modules.

:author: M. Marin (KTH)
:date:   30.9.2020
"""

from tempfile import TemporaryDirectory
from unittest.mock import MagicMock
from PySide2.QtWidgets import QWidget
import spine_items.resources_icons_rc  # pylint: disable=unused-import


class MockQWidget(QWidget):
    """Dummy QWidget for mocking test_push_vars method in PythonReplWidget class."""

    # noinspection PyMethodMayBeStatic
    def test_push_vars(self):
        return True


def create_mock_project():
    mock_project = MagicMock()
    with TemporaryDirectory() as items_dir:
        mock_project.items_dir = items_dir
    with TemporaryDirectory() as project_dir:
        mock_project.project_dir = project_dir
    return mock_project


def finish_mock_project_item_construction(factory, project_item, mock_toolbox):
    icon = factory.make_icon(mock_toolbox, 0, 0)
    project_item.set_icon(icon)
    properties_widget = factory.make_properties_widget(mock_toolbox)
    project_item.set_properties_ui(properties_widget.ui)
    project_item.create_data_dir()
    project_item.set_up()
    mock_toolbox.msg = MagicMock()
    mock_toolbox.msg.attach_mock(MagicMock(), "emit")
    mock_toolbox.msg_warning = MagicMock()
    mock_toolbox.msg_warning.attach_mock(MagicMock(), "emit")
    mock_toolbox.undo_stack.push.side_effect = lambda cmd: cmd.redo()
