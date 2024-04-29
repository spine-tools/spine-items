######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# Copyright Spine Items contributors
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""Contains unit tests for the ``import_mapping_options`` module."""
import unittest
from contextlib import contextmanager
from PySide6.QtCore import Qt, QItemSelectionModel
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QUndoStack
from spine_items.importer.mvcmodels.mappings_model import MappingsModel
from spine_items.importer.mvcmodels.mappings_model_roles import Role
from spine_items.importer.ui.import_editor_window import Ui_MainWindow
from spine_items.importer.widgets.import_mapping_options import ImportMappingOptions
from spinetoolbox.helpers import signal_waiter


class TestImportMappingOptions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def test_time_series_repeat_flag_check_box(self):
        with parent_widget() as parent:
            undo_stack = QUndoStack()
            mappings_model = MappingsModel(undo_stack, parent)
            mappings_dict = self._template_mapping()
            mappings_model.restore(mappings_dict)
            ui = Ui_MainWindow()
            ui.setupUi(parent)
            ui.source_list.setModel(mappings_model)
            ui.mapping_list.setModel(mappings_model)
            ui.mapping_list.setRootIndex(mappings_model.dummy_parent())
            import_mapping_options = ImportMappingOptions(mappings_model, ui, undo_stack)
            table_index = mappings_model.index(1, 0)
            ui.source_list.selectionModel().setCurrentIndex(table_index, QItemSelectionModel.ClearAndSelect)
            mapping_list_index = mappings_model.index(0, 0, table_index)
            ui.mapping_list.selectionModel().setCurrentIndex(mapping_list_index, QItemSelectionModel.ClearAndSelect)
            self.assertEqual(ui.time_series_repeat_check_box.checkState(), Qt.CheckState.Unchecked)
            table_index = mappings_model.index(1, 0)
            flattened_mappings = mappings_model.index(0, 0, table_index).data(Role.FLATTENED_MAPPINGS)
            self.assertEqual(flattened_mappings.value_mapping().options.get("repeat", False), False)
            with signal_waiter(ui.time_series_repeat_check_box.stateChanged) as waiter:
                ui.time_series_repeat_check_box.setChecked(True)
                waiter.wait()
            self.assertEqual(ui.time_series_repeat_check_box.checkState(), Qt.CheckState.Checked)
            table_index = mappings_model.index(1, 0)
            flattened_mappings = mappings_model.index(0, 0, table_index).data(Role.FLATTENED_MAPPINGS)
            self.assertEqual(flattened_mappings.value_mapping().options["repeat"], True)

    @staticmethod
    def _template_mapping():
        return {
            "table_mappings": {
                "Sheet1": [
                    {
                        "Mapping 1": {
                            "mapping": [
                                {"map_type": "ObjectClass", "position": "hidden", "value": "Item"},
                                {"map_type": "Object", "position": "hidden", "value": "spoon"},
                                {"map_type": "ObjectMetadata", "position": "hidden"},
                                {"map_type": "ParameterDefinition", "position": "hidden", "value": "temperature"},
                                {"map_type": "Alternative", "position": "hidden", "value": "Base"},
                                {"map_type": "ParameterValueMetadata", "position": "hidden"},
                                {"map_type": "ParameterValueType", "position": "hidden", "value": "time_series"},
                                {"map_type": "IndexName", "position": "hidden"},
                                {"map_type": "ParameterValueIndex", "position": 0},
                                {"map_type": "ExpandedValue", "position": 1},
                            ]
                        }
                    }
                ]
            },
            "selected_tables": ["Sheet1"],
            "table_options": {"Sheet1": {}},
            "table_types": {"Sheet1": {"0": "datetime", "1": "float"}},
            "table_default_column_type": {},
            "table_row_types": {},
            "source_type": "ExcelConnector",
        }


@contextmanager
def parent_widget():
    parent = QMainWindow()
    try:
        yield parent
    finally:
        parent.deleteLater()


if __name__ == "__main__":
    unittest.main()
