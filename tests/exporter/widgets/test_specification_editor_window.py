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
import json
import pathlib
from tempfile import TemporaryDirectory
import unittest
from unittest import mock
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QMessageBox
from spine_items.exporter.specification import MappingSpecification, MappingType, OutputFormat, Specification
from spine_items.exporter.widgets.specification_editor_window import SpecificationEditorWindow
from spinedb_api.export_mapping.export_mapping import EntityClassMapping, FixedValueMapping
from spinedb_api.export_mapping.export_mapping import from_dict as mappings_from_dict
from spinedb_api.export_mapping.settings import entity_metadata_export, metadata_export
from spinedb_api.mapping import Position, unflatten
from spinetoolbox.helpers import color_from_index
from tests.mock_helpers import assert_table_model_data, clean_up_toolbox, create_toolboxui_with_project


class TestSpecificationEditorWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        self._temp_dir = TemporaryDirectory()
        self._toolbox = create_toolboxui_with_project(self._temp_dir.name)

    def tearDown(self):
        clean_up_toolbox(self._toolbox)
        self._temp_dir.cleanup()

    def test_empty_editor(self):
        editor = SpecificationEditorWindow(self._toolbox)
        self.assertEqual(editor._ui.mappings_table.model().rowCount(), 1)
        self.assertEqual(editor._ui.mappings_table.model().index(0, 0).data(), "Mapping (1)")
        with mock.patch("spinetoolbox.project_item.specification_editor_window.save_ui"):
            editor.tear_down()

    def test_mapping_in_table_name_position_disables_fixed_table_name_widgets(self):
        editor = SpecificationEditorWindow(self._toolbox)
        self.assertTrue(editor._ui.fix_table_name_check_box.isEnabled())
        self.assertFalse(editor._ui.fix_table_name_check_box.isChecked())
        self.assertFalse(editor._ui.fix_table_name_line_edit.isEnabled())
        self.assertEqual(editor._ui.fix_table_name_line_edit.text(), "")
        editor._ui.mappings_table.setCurrentIndex(editor._ui.mappings_table.model().index(0, 0))
        model = editor._ui.mapping_table_view.model()
        model.setData(model.index(0, 1), "table name")
        self.assertFalse(editor._ui.fix_table_name_check_box.isEnabled())
        self.assertFalse(editor._ui.fix_table_name_check_box.isChecked())
        self.assertFalse(editor._ui.fix_table_name_line_edit.isEnabled())
        self.assertEqual(editor._ui.fix_table_name_line_edit.text(), "")
        with mock.patch(
            "spinetoolbox.project_item.specification_editor_window.SpecificationEditorWindowBase.tear_down"
        ) as tear_down_window:
            tear_down_window.return_value = True
            editor.tear_down()

    def test_mapping_with_fixed_table_enables_the_check_box_and_fills_the_table_name_field(self):
        flattened_mappings = [FixedValueMapping(Position.table_name, "nice table name"), EntityClassMapping(0)]
        mapping_specification = MappingSpecification(
            MappingType.entities, True, True, "", True, unflatten(flattened_mappings)
        )
        specification = Specification("spec name", mapping_specifications={"my mappings": mapping_specification})
        editor = SpecificationEditorWindow(self._toolbox, specification)
        self.assertTrue(editor._ui.fix_table_name_check_box.isEnabled())
        self.assertTrue(editor._ui.fix_table_name_check_box.isChecked())
        self.assertTrue(editor._ui.fix_table_name_line_edit.isEnabled())
        self.assertEqual(editor._ui.fix_table_name_line_edit.text(), "nice table name")
        with mock.patch("spinetoolbox.project_item.specification_editor_window.save_ui"):
            editor.tear_down()

    def test_duplicate_specification(self):
        flattened_mappings = [FixedValueMapping(Position.table_name, "nice table name"), EntityClassMapping(0)]
        mapping_specification = MappingSpecification(
            MappingType.entities, True, True, "", True, unflatten(flattened_mappings)
        )
        specification = Specification("spec name", mapping_specifications={"my mappings": mapping_specification})
        editor = SpecificationEditorWindow(self._toolbox, specification)
        editor._spec_toolbar._line_edit_name.setText("my spec name")
        editor._spec_toolbar._line_edit_description.setText("A cool exporter.")
        editor._ui.export_format_combo_box.setCurrentText(OutputFormat.SQL.value)
        with mock.patch.object(self._toolbox, "show_specification_form") as show_duplicate:
            editor._spec_toolbar.duplicate_action.trigger()
            show_duplicate.assert_called_once()
            self.assertEqual(show_duplicate.call_args.args[0], "Exporter")
            self.assertEqual(show_duplicate.call_args.args[1].name, "")
            self.assertEqual(show_duplicate.call_args.args[1].description, "A cool exporter.")
            self.assertEqual(show_duplicate.call_args.args[1].output_format, OutputFormat.SQL)
            self.assertEqual(show_duplicate.call_args.args[1].definition_file_path, "")
            duplicate_mapping_specification_dicts = {
                key: s.to_dict() for key, s in show_duplicate.call_args.args[1].mapping_specifications().items()
            }
            self.assertEqual(duplicate_mapping_specification_dicts, {"my mappings": mapping_specification.to_dict()})
            self.assertIsNot(
                show_duplicate.call_args.args[1].mapping_specifications()["my mappings"], mapping_specification
            )
            self.assertEqual(show_duplicate.call_args.kwargs, {})
        with mock.patch(
            "spinetoolbox.project_item.specification_editor_window.SpecificationEditorWindowBase.tear_down"
        ) as tear_down_window:
            tear_down_window.return_value = True
            editor.tear_down()

    def test_forced_decrease_of_selected_dimension_by_entity_dimensions_is_stored_properly(self):
        mapping_dicts = [
            {"map_type": "EntityClass", "position": 0, "highlight_position": 1},
            {"map_type": "Dimension", "position": "hidden"},
            {"map_type": "Dimension", "position": "hidden"},
            {"map_type": "ParameterDefinition", "position": 3},
            {"map_type": "ParameterValueList", "position": "hidden", "ignorable": True},
            {"map_type": "Entity", "position": "hidden"},
            {"map_type": "Element", "position": "hidden"},
            {"map_type": "Element", "position": "hidden"},
            {"map_type": "Alternative", "position": 4},
            {"map_type": "ParameterValueType", "position": "hidden"},
            {"map_type": "ParameterValue", "position": 5},
        ]
        unflattened_mappings = mappings_from_dict(mapping_dicts)
        mapping_specification = MappingSpecification(
            MappingType.entity_dimension_parameter_values, True, True, "", True, unflattened_mappings
        )
        specification = Specification("spec name", mapping_specifications={"my mappings": mapping_specification})
        specification_path = pathlib.Path(self._temp_dir.name) / "my spec.json"
        specification.definition_file_path = str(specification_path)
        self._toolbox.project().add_specification(specification, save_to_disk=False)
        editor = SpecificationEditorWindow(self._toolbox, specification)
        self.assertEqual(editor._ui.highlight_dimension_spin_box.value(), 2)
        self.assertEqual(editor._ui.entity_dimensions_spin_box.value(), 2)
        editor._spec_toolbar._line_edit_name.setText("my spec name")
        editor._spec_toolbar._line_edit_name.editingFinished.emit()
        editor._ui.entity_dimensions_spin_box.setValue(1)
        self.assertEqual(editor._ui.entity_dimensions_spin_box.value(), 1)
        self.assertEqual(editor._ui.highlight_dimension_spin_box.value(), 1)
        editor.spec_toolbar().save_action.trigger()
        with open(specification_path) as specification_file:
            loaded_specification = Specification.from_dict(json.load(specification_file))
        self.assertEqual(loaded_specification.name, "my spec name")
        expected_dicts = [
            {"map_type": "EntityClass", "position": 0, "highlight_position": 0},
            {"map_type": "Dimension", "position": "hidden"},
            {"map_type": "ParameterDefinition", "position": 3},
            {"map_type": "ParameterValueList", "position": "hidden", "ignorable": True},
            {"map_type": "Entity", "position": "hidden"},
            {"map_type": "Element", "position": "hidden"},
            {"map_type": "Alternative", "position": 4},
            {"map_type": "ParameterValueType", "position": "hidden"},
            {"map_type": "ParameterValue", "position": 5},
        ]
        self.assertEqual(loaded_specification.mapping_specifications()["my mappings"].to_dict()["root"], expected_dicts)
        with mock.patch("spinetoolbox.project_item.specification_editor_window.save_ui"):
            editor.tear_down()

    def test_set_item_type_to_metadata(self):
        editor = SpecificationEditorWindow(self._toolbox)
        editor._ui.item_type_combo_box.setCurrentText("Metadata")
        self.assertFalse(editor._ui.entity_dimensions_spin_box.isEnabled())
        self.assertFalse(editor._ui.highlight_dimension_spin_box.isEnabled())
        self.assertFalse(editor._ui.parameter_type_combo_box.isEnabled())
        self.assertFalse(editor._ui.parameter_dimensions_spin_box.isEnabled())
        expected = [
            ["Metadata names", "1", None, None, "", ""],
            ["Metadata values", "2", None, None, "", ""],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected)
        expected = [
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected, Qt.ItemDataRole.CheckStateRole)
        expected = [
            [color_from_index(0, 2).lighter(), None, None, None, None, None],
            [color_from_index(1, 2).lighter(), None, None, None, None, None],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected, Qt.ItemDataRole.BackgroundRole)
        with (
            mock.patch(
                "spinetoolbox.project_item.specification_editor_window.QMessageBox.exec"
            ) as mock_save_dialog_exec,
            mock.patch("spinetoolbox.project_item.specification_editor_window.save_ui"),
        ):
            mock_save_dialog_exec.return_value = QMessageBox.StandardButton.No
            editor.tear_down()

    def test_set_item_type_to_entity_class_with_default_value(self):
        editor = SpecificationEditorWindow(self._toolbox)
        editor._ui.item_type_combo_box.setCurrentText("Entity class")
        self.assertTrue(editor._ui.entity_dimensions_spin_box.isEnabled())
        self.assertFalse(editor._ui.highlight_dimension_spin_box.isEnabled())
        self.assertTrue(editor._ui.parameter_type_combo_box.isEnabled())
        self.assertFalse(editor._ui.parameter_dimensions_spin_box.isEnabled())
        editor._ui.parameter_type_combo_box.setCurrentText("Default value")
        self.assertTrue(editor._ui.parameter_dimensions_spin_box.isEnabled())
        expected = [
            ["Entity classes", "1", None, None, "", ""],
            ["Parameter definitions", "2", None, None, "", ""],
            ["Parameter descriptions", "hidden", None, None, "", ""],
            ["Default value types", "hidden", None, None, "", ""],
            ["Default values", "3", None, None, "", ""],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected)
        expected = [
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Checked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected, Qt.ItemDataRole.CheckStateRole)
        expected = [
            [color_from_index(0, 2).lighter(), None, None, None, None, None],
            [color_from_index(1, 3).lighter(), None, None, None, None, None],
            [QColor(Qt.GlobalColor.gray).lighter(), None, None, None, None, None],
            [QColor(Qt.GlobalColor.gray).lighter(), None, None, None, None, None],
            [color_from_index(2, 3).lighter(), None, None, None, None, None],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected, Qt.ItemDataRole.BackgroundRole)
        with (
            mock.patch(
                "spinetoolbox.project_item.specification_editor_window.QMessageBox.exec"
            ) as mock_save_dialog_exec,
            mock.patch("spinetoolbox.project_item.specification_editor_window.save_ui"),
        ):
            mock_save_dialog_exec.return_value = QMessageBox.StandardButton.No
            editor.tear_down()

    def test_change_entity_dimensions_with_entity_class_with_default_value(self):
        editor = SpecificationEditorWindow(self._toolbox)
        editor._ui.item_type_combo_box.setCurrentText("Entity class")
        editor._ui.parameter_type_combo_box.setCurrentText("Default value")
        editor._ui.entity_dimensions_spin_box.setValue(1)
        self.assertEqual(editor._ui.entity_dimensions_spin_box.value(), 1)
        expected = [
            ["Entity classes", "1", None, None, "", ""],
            ["Dimensions", "hidden", None, None, "", ""],
            ["Parameter definitions", "2", None, None, "", ""],
            ["Parameter descriptions", "hidden", None, None, "", ""],
            ["Default value types", "hidden", None, None, "", ""],
            ["Default values", "3", None, None, "", ""],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected)
        editor._ui.entity_dimensions_spin_box.setValue(0)
        expected = [
            ["Entity classes", "1", None, None, "", ""],
            ["Parameter definitions", "2", None, None, "", ""],
            ["Parameter descriptions", "hidden", None, None, "", ""],
            ["Default value types", "hidden", None, None, "", ""],
            ["Default values", "3", None, None, "", ""],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected)
        with (
            mock.patch(
                "spinetoolbox.project_item.specification_editor_window.QMessageBox.exec"
            ) as mock_save_dialog_exec,
            mock.patch("spinetoolbox.project_item.specification_editor_window.save_ui"),
        ):
            mock_save_dialog_exec.return_value = QMessageBox.StandardButton.No
            editor.tear_down()

    def test_change_parameter_dimensions_with_entity_class_with_default_value(self):
        editor = SpecificationEditorWindow(self._toolbox)
        editor._ui.item_type_combo_box.setCurrentText("Entity class")
        editor._ui.parameter_type_combo_box.setCurrentText("Default value")
        editor._ui.parameter_dimensions_spin_box.setValue(1)
        expected = [
            ["Entity classes", "1", None, None, "", ""],
            ["Parameter definitions", "2", None, None, "", ""],
            ["Parameter descriptions", "hidden", None, None, "", ""],
            ["Default value types", "hidden", None, None, "", ""],
            ["Default value index names", "hidden", None, None, "", ""],
            ["Default value indexes", "hidden", None, None, "", ""],
            ["Default values", "3", None, None, "", ""],
        ]
        editor._ui.parameter_dimensions_spin_box.setValue(0)
        expected = [
            ["Entity classes", "1", None, None, "", ""],
            ["Parameter definitions", "2", None, None, "", ""],
            ["Parameter descriptions", "hidden", None, None, "", ""],
            ["Default value types", "hidden", None, None, "", ""],
            ["Default values", "3", None, None, "", ""],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected)

    def test_set_item_type_to_entity_metadata(self):
        editor = SpecificationEditorWindow(self._toolbox)
        editor._ui.item_type_combo_box.setCurrentText("Entity metadata")
        self.assertTrue(editor._ui.entity_dimensions_spin_box.isEnabled())
        self.assertFalse(editor._ui.highlight_dimension_spin_box.isEnabled())
        self.assertFalse(editor._ui.parameter_type_combo_box.isEnabled())
        self.assertFalse(editor._ui.parameter_dimensions_spin_box.isEnabled())
        expected = [
            ["Entity classes", "1", None, None, "", ""],
            ["Entities", "2", None, None, "", ""],
            ["Metadata names", "3", None, None, "", ""],
            ["Metadata values", "4", None, None, "", ""],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected)
        expected = [
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected, Qt.ItemDataRole.CheckStateRole)
        expected = [
            [color_from_index(0, 4).lighter(), None, None, None, None, None],
            [color_from_index(1, 4).lighter(), None, None, None, None, None],
            [color_from_index(2, 4).lighter(), None, None, None, None, None],
            [color_from_index(3, 4).lighter(), None, None, None, None, None],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected, Qt.ItemDataRole.BackgroundRole)
        with (
            mock.patch(
                "spinetoolbox.project_item.specification_editor_window.QMessageBox.exec"
            ) as mock_save_dialog_exec,
            mock.patch("spinetoolbox.project_item.specification_editor_window.save_ui"),
        ):
            mock_save_dialog_exec.return_value = QMessageBox.StandardButton.No
            editor.tear_down()

    def test_set_item_type_to_parameter_value_metadata(self):
        editor = SpecificationEditorWindow(self._toolbox)
        editor._ui.item_type_combo_box.setCurrentText("Parameter value metadata")
        self.assertTrue(editor._ui.entity_dimensions_spin_box.isEnabled())
        self.assertFalse(editor._ui.highlight_dimension_spin_box.isEnabled())
        self.assertFalse(editor._ui.parameter_type_combo_box.isEnabled())
        self.assertFalse(editor._ui.parameter_dimensions_spin_box.isEnabled())
        expected = [
            ["Entity classes", "1", None, None, "", ""],
            ["Entities", "2", None, None, "", ""],
            ["Parameter definitions", "3", None, None, "", ""],
            ["Alternatives", "4", None, None, "", ""],
            ["Metadata names", "5", None, None, "", ""],
            ["Metadata values", "6", None, None, "", ""],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected)
        expected = [
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected, Qt.ItemDataRole.CheckStateRole)
        expected = [
            [color_from_index(0, 6).lighter(), None, None, None, None, None],
            [color_from_index(1, 6).lighter(), None, None, None, None, None],
            [color_from_index(2, 6).lighter(), None, None, None, None, None],
            [color_from_index(3, 6).lighter(), None, None, None, None, None],
            [color_from_index(4, 6).lighter(), None, None, None, None, None],
            [color_from_index(5, 6).lighter(), None, None, None, None, None],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected, Qt.ItemDataRole.BackgroundRole)
        with (
            mock.patch(
                "spinetoolbox.project_item.specification_editor_window.QMessageBox.exec"
            ) as mock_save_dialog_exec,
            mock.patch("spinetoolbox.project_item.specification_editor_window.save_ui"),
        ):
            mock_save_dialog_exec.return_value = QMessageBox.StandardButton.No
            editor.tear_down()

    def test_change_item_type_from_metadata_to_entity_class_with_dimension_parameter(self):
        mapping_specification = MappingSpecification(MappingType.metadata, True, True, "", True, metadata_export(0, 1))
        specification = Specification("spec name", mapping_specifications={"my mappings": mapping_specification})
        editor = SpecificationEditorWindow(self._toolbox, specification)
        self.assertEqual(editor._ui.item_type_combo_box.currentText(), "Metadata")
        editor._ui.item_type_combo_box.setCurrentText("Entity class with dimension parameter")
        self.assertTrue(editor._ui.entity_dimensions_spin_box.isEnabled())
        self.assertEqual(editor._ui.entity_dimensions_spin_box.minimum(), 1)
        self.assertEqual(editor._ui.entity_dimensions_spin_box.value(), 1)
        self.assertTrue(editor._ui.highlight_dimension_spin_box.isEnabled())
        self.assertEqual(editor._ui.highlight_dimension_spin_box.value(), 1)
        self.assertTrue(editor._ui.parameter_type_combo_box.isEnabled())
        self.assertTrue(editor._ui.parameter_dimensions_spin_box.isEnabled())
        expected = [
            ["Entity classes", "1", None, None, "", ""],
            ["Dimensions", "2", None, None, "", ""],
            ["Parameter definitions", "4", None, None, "", ""],
            ["Value lists", "hidden", None, None, "", ""],
            ["Entities", "hidden", None, None, "", ""],
            ["Elements", "3", None, None, "", ""],
            ["Alternatives", "5", None, None, "", ""],
            ["Value types", "hidden", None, None, "", ""],
            ["Parameter values", "6", None, None, "", ""],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected)
        expected = [
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Checked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected, Qt.ItemDataRole.CheckStateRole)
        expected = [
            [color_from_index(0, 6).lighter(), None, None, None, None, None],
            [color_from_index(1, 6).lighter(), None, None, None, None, None],
            [color_from_index(2, 6).lighter(), None, None, None, None, None],
            [QColor(Qt.GlobalColor.gray).lighter(), None, None, None, None, None],
            [QColor(Qt.GlobalColor.gray).lighter(), None, None, None, None, None],
            [color_from_index(3, 6).lighter(), None, None, None, None, None],
            [color_from_index(4, 6).lighter(), None, None, None, None, None],
            [QColor(Qt.GlobalColor.gray).lighter(), None, None, None, None, None],
            [color_from_index(5, 6).lighter(), None, None, None, None, None],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected, Qt.ItemDataRole.BackgroundRole)
        with (
            mock.patch(
                "spinetoolbox.project_item.specification_editor_window.QMessageBox.exec"
            ) as mock_save_dialog_exec,
            mock.patch("spinetoolbox.project_item.specification_editor_window.save_ui"),
        ):
            mock_save_dialog_exec.return_value = QMessageBox.StandardButton.No
            editor.tear_down()

    def test_increase_dimensions_in_entity_metadata_mapping(self):
        mapping_specification = MappingSpecification(
            MappingType.entity_metadata, True, True, "", True, entity_metadata_export(0, 1, [], 2, 3)
        )
        specification = Specification("spec name", mapping_specifications={"my mappings": mapping_specification})
        editor = SpecificationEditorWindow(self._toolbox, specification)
        self.assertEqual(editor._ui.item_type_combo_box.currentText(), "Entity metadata")
        self.assertTrue(editor._ui.entity_dimensions_spin_box.isEnabled())
        self.assertEqual(editor._ui.entity_dimensions_spin_box.minimum(), 0)
        self.assertEqual(editor._ui.entity_dimensions_spin_box.value(), 0)
        editor._ui.entity_dimensions_spin_box.setValue(1)
        expected = [
            ["Entity classes", "1", None, None, "", ""],
            ["Entities", "2", None, None, "", ""],
            ["Elements", "hidden", None, None, "", ""],
            ["Metadata names", "3", None, None, "", ""],
            ["Metadata values", "4", None, None, "", ""],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected)
        expected = [
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected, Qt.ItemDataRole.CheckStateRole)
        expected = [
            [color_from_index(0, 4).lighter(), None, None, None, None, None],
            [color_from_index(1, 4).lighter(), None, None, None, None, None],
            [QColor(Qt.GlobalColor.gray).lighter(), None, None, None, None, None],
            [color_from_index(2, 4).lighter(), None, None, None, None, None],
            [color_from_index(3, 4).lighter(), None, None, None, None, None],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected, Qt.ItemDataRole.BackgroundRole)
        with (
            mock.patch(
                "spinetoolbox.project_item.specification_editor_window.QMessageBox.exec"
            ) as mock_save_dialog_exec,
            mock.patch("spinetoolbox.project_item.specification_editor_window.save_ui"),
        ):
            mock_save_dialog_exec.return_value = QMessageBox.StandardButton.No
            editor.tear_down()

    def test_decrease_dimensions_in_entity_metadata_mapping(self):
        mapping_specification = MappingSpecification(
            MappingType.entity_metadata, True, True, "", True, entity_metadata_export(0, 1, [2], 3, 4)
        )
        specification = Specification("spec name", mapping_specifications={"my mappings": mapping_specification})
        editor = SpecificationEditorWindow(self._toolbox, specification)
        self.assertEqual(editor._ui.item_type_combo_box.currentText(), "Entity metadata")
        self.assertTrue(editor._ui.entity_dimensions_spin_box.isEnabled())
        self.assertEqual(editor._ui.entity_dimensions_spin_box.minimum(), 0)
        self.assertEqual(editor._ui.entity_dimensions_spin_box.value(), 1)
        editor._ui.entity_dimensions_spin_box.setValue(0)
        expected = [
            ["Entity classes", "1", None, None, "", ""],
            ["Entities", "2", None, None, "", ""],
            ["Metadata names", "4", None, None, "", ""],
            ["Metadata values", "5", None, None, "", ""],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected)
        expected = [
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
            [None, None, Qt.CheckState.Unchecked, Qt.CheckState.Unchecked, None, None],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected, Qt.ItemDataRole.CheckStateRole)
        expected = [
            [color_from_index(0, 4).lighter(), None, None, None, None, None],
            [color_from_index(1, 4).lighter(), None, None, None, None, None],
            [color_from_index(2, 4).lighter(), None, None, None, None, None],
            [color_from_index(3, 4).lighter(), None, None, None, None, None],
        ]
        assert_table_model_data(editor._mapping_editor_model, expected, Qt.ItemDataRole.BackgroundRole)
        with (
            mock.patch(
                "spinetoolbox.project_item.specification_editor_window.QMessageBox.exec"
            ) as mock_save_dialog_exec,
            mock.patch("spinetoolbox.project_item.specification_editor_window.save_ui"),
        ):
            mock_save_dialog_exec.return_value = QMessageBox.StandardButton.No
            editor.tear_down()
