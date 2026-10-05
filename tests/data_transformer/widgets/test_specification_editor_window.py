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

"""Unit tests for the ``specification_editor_window`` module."""

import pytest
from unittest import mock
from PySide6.QtWidgets import QApplication
from spine_items.data_transformer.data_transformer_specification import DataTransformerSpecification
from spine_items.data_transformer.widgets.specification_editor_window import SpecificationEditorWindow
from spine_items.data_transformer.settings import EntityClassRenamingSettings
from tests.mock_helpers import create_mock_toolbox


@pytest.fixture(scope="session", autouse=True)
def qapplication():
    """Ensure a QApplication exists for all tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def mock_toolbox():
    mock_toolbox = create_mock_toolbox()
    yield mock_toolbox


class TestSpecificationEditorWindow:
    def test_make_specification_editor_window(self, mock_toolbox):
        rename_map = {"a": "b"}
        settings = EntityClassRenamingSettings(rename_map)
        dt_spec = DataTransformerSpecification("dt_spec", settings=settings)
        with mock.patch("spinetoolbox.project_item.specification_editor_window.restore_ui") as mock_restore_ui:
            editor = SpecificationEditorWindow(mock_toolbox, dt_spec)
            mock_restore_ui.assert_called_once()
        assert editor is not None
        editor.close()

    def test_make_new_specification(self, mock_toolbox):
        with mock.patch("spinetoolbox.project_item.specification_editor_window.restore_ui") as mock_restore_ui:
            editor = SpecificationEditorWindow(mock_toolbox, None)
            mock_restore_ui.assert_called_once()
        assert editor.specification is None
        spec = editor._make_new_specification("test_spec")
        editor.specification = spec
        assert editor.specification.name == "test_spec"
        editor.close()

    def test_change_filter_widget(self, mock_toolbox):
        dt_spec = DataTransformerSpecification("dt_spec")
        with mock.patch("spinetoolbox.project_item.specification_editor_window.restore_ui") as mock_restore_ui:
            editor = SpecificationEditorWindow(mock_toolbox, dt_spec)
            mock_restore_ui.assert_called_once()
        editor._change_filter_widget("Rename entity classes")
        current_filter = editor._ui.filter_combo_box.currentText()
        assert current_filter == "Rename entity classes"
        editor._change_filter_widget("Rename parameters")
        current_filter = editor._ui.filter_combo_box.currentText()
        assert current_filter == "Rename parameters"
        # Clear undo stack so tear_down does not open a confirm prompt
        editor._undo_stack.clear()
        editor.close()

    def test_load_url_from_filesystem(self, mock_toolbox):
        dt_spec = DataTransformerSpecification("dt_spec")
        with mock.patch("spinetoolbox.project_item.specification_editor_window.restore_ui") as mock_restore_ui:
            editor = SpecificationEditorWindow(mock_toolbox, dt_spec)
            mock_restore_ui.assert_called_once()
        with (
            mock.patch(
                "spine_items.data_transformer.widgets.specification_editor_window.QFileDialog.getOpenFileName"
            ) as mock_fd_gofn,
            mock.patch(
                "spine_items.data_transformer.widgets.value_transformation.ValueTransformation.load_data"
            ) as mock_load_data,
        ):
            mock_fd_gofn.return_value = ["/fake/path/db.sqlite"]
            mock_load_data.return_value = True
            editor._load_url_from_filesystem(True)
            mock_fd_gofn.assert_called_once()
            editor._change_filter_widget("Transform values")
            editor._load_data(True)
            mock_load_data.assert_called_once()
            assert editor._ui.database_url_combo_box.currentText() == "sqlite:////fake/path/db.sqlite"
        # Clear undo stack so tear_down does not open a confirm prompt
        editor._undo_stack.clear()
        editor.close()
