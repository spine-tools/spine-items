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

"""Unit tests for export mapping setup table."""
from unittest import mock
from PySide6.QtCore import Qt
from PySide6.QtGui import QUndoStack
import pytest
from spine_items.exporter.mvcmodels.mapping_editor_table_model import MappingEditorTableModel
from spinedb_api.export_mapping import entity_export
from spinedb_api.mapping import Position
from spinetoolbox.helpers import signal_waiter
from tests.mock_helpers import assert_table_model_data


@pytest.fixture
def undo_stack(parent_object):
    undo_stack = QUndoStack(parent_object)
    yield undo_stack


class TestMappingEditorTableModel:
    def test_column_count(self, undo_stack, parent_object):
        model = MappingEditorTableModel("mapping", entity_export(), undo_stack, mock.MagicMock(), parent_object)
        assert model.rowCount() == 4

    def test_row_count(self, undo_stack, parent_object):
        mapping_root = entity_export()
        model = MappingEditorTableModel("mapping", mapping_root, undo_stack, mock.MagicMock(), parent_object)
        assert model.rowCount() == mapping_root.count_mappings()

    def test_data(self, undo_stack, parent_object):
        model = MappingEditorTableModel(
            "mapping", entity_export(1, Position.hidden, 2), undo_stack, mock.MagicMock(), parent_object
        )
        expected = [
            ["Entity classes", "2", None, None, "", ""],
            ["Class descriptions", "hidden", None, None, "", ""],
            ["Entities", "3", None, None, "", ""],
            ["Entity descriptions", "hidden", None, None, "", ""],
        ]
        assert_table_model_data(model, expected)
        expected = [
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Checked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Checked, None, None],
        ]
        assert_table_model_data(model, expected, Qt.ItemDataRole.CheckStateRole)

    def test_set_data_column_number(self, undo_stack, parent_object):
        model = MappingEditorTableModel("mapping", entity_export(), undo_stack, mock.MagicMock(), parent_object)
        assert model.setData(model.index(0, 1), "23")
        assert model.index(0, 1).data() == "23"

    def test_set_data_prevents_duplicate_table_name_positions(self, undo_stack, parent_object):
        model = MappingEditorTableModel(
            "mapping",
            entity_export(Position.table_name, Position.hidden, 0),
            undo_stack,
            mock.MagicMock(),
            parent_object,
        )
        expected = [
            ["Entity classes", "table name", None, None, "", ""],
            ["Class descriptions", "hidden", None, None, "", ""],
            ["Entities", "1", None, None, "", ""],
            ["Entity descriptions", "hidden", None, None, "", ""],
        ]
        assert_table_model_data(model, expected)
        with signal_waiter(model.dataChanged) as waiter:
            model.setData(model.index(2, 1), "table name")
            waiter.wait()
            assert waiter.args == (model.index(0, 1), model.index(2, 1), [Qt.ItemDataRole.DisplayRole])
        expected = [
            ["Entity classes", "1", None, None, "", ""],
            ["Class descriptions", "hidden", None, None, "", ""],
            ["Entities", "table name", None, None, "", ""],
            ["Entity descriptions", "hidden", None, None, "", ""],
        ]
        assert_table_model_data(model, expected)

    def test_set_data_emits_data_changed_correctly_in_pivoted_mode(self, undo_stack, parent_object):
        model = MappingEditorTableModel("mapping", entity_export(-1), undo_stack, mock.MagicMock(), parent_object)
        expected = [
            ["Entity classes", "1", None, None, "", ""],
            ["Class descriptions", "hidden", None, None, "", ""],
            ["Entities", "hidden", None, None, "", ""],
            ["Entity descriptions", "hidden", None, None, "", ""],
        ]
        assert_table_model_data(model, expected)
        expected = [
            [None, None, Qt.CheckState.Checked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Checked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Checked, None, None],
        ]
        assert_table_model_data(model, expected, Qt.ItemDataRole.CheckStateRole)
        data_changed_listener = mock.MagicMock()
        model.dataChanged.connect(data_changed_listener)
        with signal_waiter(model.dataChanged) as waiter:
            model.setData(model.index(0, 1), "2")
            waiter.wait()
        data_changed_listener.assert_has_calls(
            [
                mock.call(model.index(0, 1), model.index(0, 1), [Qt.ItemDataRole.DisplayRole]),
                mock.call(model.index(0, 2), model.index(0, 2), [Qt.ItemDataRole.CheckStateRole]),
                mock.call(model.index(0, 0), model.index(3, 0), [Qt.ItemDataRole.BackgroundRole]),
            ]
        )
        expected = [
            ["Entity classes", "2", None, None, "", ""],
            ["Class descriptions", "hidden", None, None, "", ""],
            ["Entities", "hidden", None, None, "", ""],
            ["Entity descriptions", "hidden", None, None, "", ""],
        ]
        assert_table_model_data(model, expected)
        expected = [
            [None, None, Qt.CheckState.Checked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Checked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Checked, None, None],
        ]
        assert_table_model_data(model, expected, Qt.ItemDataRole.CheckStateRole)
