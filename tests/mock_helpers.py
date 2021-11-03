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
Classes and functions that can be shared among unit test modules.

:author: M. Marin (KTH)
:date:   30.9.2020
"""
import os.path
from unittest import mock
from unittest.mock import MagicMock
from PySide2.QtGui import QStandardItemModel
from PySide2.QtWidgets import QWidget, QApplication
import spine_items.resources_icons_rc  # pylint: disable=unused-import
from spinetoolbox.ui_main import ToolboxUI


class MockQWidget(QWidget):
    """Dummy QWidget for mocking test_push_vars method in SpineConsoleWidget class."""

    # noinspection PyMethodMayBeStatic
    def test_push_vars(self):
        return True


def create_mock_toolbox():
    mock_toolbox = MagicMock()
    mock_toolbox.msg = MagicMock()
    mock_toolbox.msg.attach_mock(MagicMock(), "emit")
    mock_toolbox.msg_warning = MagicMock()
    mock_toolbox.msg_warning.attach_mock(MagicMock(), "emit")
    mock_toolbox.undo_stack.push.side_effect = lambda cmd: cmd.redo()
    mock_toolbox.filtered_spec_factory_models.__getitem__.return_value = QStandardItemModel()
    return mock_toolbox


def create_mock_project(project_dir):
    mock_project = MagicMock()
    mock_project.project_dir = project_dir
    mock_project.items_dir = os.path.join(project_dir, ".spinetoolbox", "items")
    mock_project.get_specification.side_effect = lambda x: None
    return mock_project


def mock_finish_project_item_construction(factory, project_item, mock_toolbox):
    icon = factory.make_icon(mock_toolbox)
    project_item.set_icon(icon)
    properties_widget = factory.make_properties_widget(mock_toolbox)
    project_item.set_properties_ui(properties_widget.ui)
    project_item.set_up()
    return properties_widget


def create_toolboxui_with_project(project_dir):
    """Returns ToolboxUI with a project instance where
    QSettings among others has been mocked."""
    with mock.patch("spinetoolbox.ui_main.ToolboxUI.save_project"), mock.patch(
        "spinetoolbox.ui_main.ToolboxUI.update_recent_projects"
    ), mock.patch("spinetoolbox.ui_main.QSettings.value") as mock_qsettings_value, mock.patch(
        "spinetoolbox.widgets.open_project_widget.OpenProjectDialog.update_recents"
    ), mock.patch(
        "spinetoolbox.plugin_manager.PluginManager.load_installed_plugins"
    ):
        mock_qsettings_value.side_effect = qsettings_value_side_effect
        toolbox = ToolboxUI()
        toolbox.create_project("UnitTest Project", "Project for unit tests.", project_dir)
    return toolbox


def qsettings_value_side_effect(key, defaultValue="0"):
    """Side effect for calling QSettings.value() method. Used to
    override default value for key 'appSettings/openPreviousProject'
    so that previous project is not opened in background when
    ToolboxUI is instantiated.

    Args:
        key (str): Key to read
        defaultValue (QVariant): Default value if key is missing
    """
    if key == "appSettings/openPreviousProject":
        return "0"  # Do not open previous project when instantiating ToolboxUI
    return defaultValue


def clean_up_toolbox(toolbox):
    """Cleans up toolbox and project."""
    if toolbox.project():
        toolbox.close_project(ask_confirmation=False)
        QApplication.processEvents()  # Makes sure Design view animations finish properly.
    toolbox.db_mngr.close_all_sessions()
    toolbox.db_mngr.clean_up()
    toolbox.db_mngr = None
    # Delete undo stack explicitly to prevent emitting certain signals well after ToolboxUI has been destroyed.
    toolbox.undo_stack.deleteLater()
    toolbox.deleteLater()
