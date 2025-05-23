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

"""Classes and functions that can be shared among unit test modules."""
from contextlib import contextmanager
import os.path
from unittest.mock import MagicMock, patch
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from spinetoolbox.ui_main import ToolboxUI


class MockQSettings:
    """Class for replacing an argument where e.g. class constructor requires an instance of QSettings.
    For example all ToolSpecification classes require a QSettings instance."""

    # noinspection PyMethodMayBeStatic, PyPep8Naming
    def value(self, key, defaultValue=""):
        """Returns the default value"""
        return defaultValue

    # noinspection PyPep8Naming
    def setValue(self, key, value):
        """Returns without modifying anything."""
        return


def create_mock_toolbox():
    mock_toolbox = MagicMock()
    mock_toolbox.msg = MagicMock()
    mock_toolbox.msg.attach_mock(MagicMock(), "emit")
    mock_toolbox.msg_warning = MagicMock()
    mock_toolbox.msg_warning.attach_mock(MagicMock(), "emit")
    mock_toolbox.undo_stack.push.side_effect = lambda cmd: cmd.redo()
    mock_toolbox.filtered_spec_factory_models.__getitem__.return_value = QStandardItemModel()
    return mock_toolbox


def create_mock_toolbox_with_mock_qsettings():
    mock_toolbox = create_mock_toolbox()
    mock_toolbox.qsettings().value.side_effect = return_default_value
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


def create_toolboxui():
    """Returns ToolboxUI for tests."""
    with (
        patch("spinetoolbox.ui_main.ToolboxUI.set_app_style") as mock_set_app_style,
        patch("spinetoolbox.plugin_manager.PluginManager.load_installed_plugins"),
    ):
        mock_set_app_style.return_value = True
        toolbox = ToolboxUI()
        toolbox._qsettings = MagicMock()
        toolbox._qsettings.value = MagicMock()
        toolbox._qsettings.value.side_effect = return_default_value
    return toolbox


def create_project(toolbox, project_dir):
    """Creates a project for the given ToolboxUI."""
    with (patch("spinetoolbox.ui_main.ToolboxUI.update_recent_projects"),):
        toolbox.create_project(project_dir)


def create_toolboxui_with_project(project_dir):
    """Returns ToolboxUI with a project instance where
    QSettings among others has been mocked."""
    with (
        patch("spinetoolbox.ui_main.ToolboxUI.set_app_style") as mock_set_app_style,
        patch("spinetoolbox.ui_main.ToolboxUI.save_project"),
        patch("spinetoolbox.plugin_manager.PluginManager.load_installed_plugins"),
    ):
        mock_set_app_style.return_value = True
        toolbox = ToolboxUI()
        toolbox._qsettings = MagicMock()
        toolbox._qsettings.value = MagicMock()
        toolbox._qsettings.value.side_effect = return_default_value
        toolbox.create_project(project_dir)
    return toolbox


def return_default_value(key, defaultValue=None):
    """Side effect function for QSettings.value() which returns defaultValue."""
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


@contextmanager
def parent_widget():
    parent = QMainWindow()
    try:
        yield parent
    finally:
        parent.deleteLater()
