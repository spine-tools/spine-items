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

""" Contains unit tests for the ImportEditorWindow class. """
import csv
from unittest import mock
from frictionless import Package, Resource
from PySide6.QtCore import QAbstractItemModel, QItemSelection, QItemSelectionModel, QPoint
from PySide6.QtWidgets import QApplication, QMessageBox
from spine_items.importer.importer_specification import ImporterSpecification
from spine_items.importer.widgets.import_editor_window import ImportEditorWindow
from spinedb_api.import_mapping.import_mapping import EntityClassMapping, EntityMapping
from spinedb_api.mapping import to_dict as mapping_to_dict
from spinedb_api.spine_io.importers.csv_reader import CSVReader
from spinedb_api.spine_io.importers.datapackage_reader import DatapackageReader
from spinetoolbox.helpers import signal_waiter


class TestImportEditorWindow:
    def test_closeEvent(self, spine_toolbox_with_project):
        spec = mock.NonCallableMagicMock()
        spec.name = "spec_name"
        spec.description = "spec_desc"
        spec.mapping = {"source_type": CSVReader.__name__}
        widget = ImportEditorWindow(spine_toolbox_with_project, spec)
        QApplication.processEvents()  # Let QTimer call ImportEditorWindow.start_ui().
        widget._app_settings = mock.NonCallableMagicMock()
        widget.close()
        widget._app_settings.beginGroup.assert_called_once_with("mappingPreviewWindow")
        widget._app_settings.endGroup.assert_called_once_with()
        qsettings_save_calls = widget._app_settings.setValue.call_args_list
        assert len(qsettings_save_calls) == 8
        saved_dict = {saved[0][0]: saved[0][1] for saved in qsettings_save_calls}
        assert len(saved_dict) == 8
        for key in (
            "windowSize",
            "windowPosition",
            "windowState",
            "windowMaximized",
            "n_screens",
            "source_list_splitterState",
            "source_data_mappings_splitterState",
            "splitterState",
        ):
            assert key in saved_dict

    def test_delete_tables_not_in_source(self, spine_toolbox_with_project, tmp_path):
        csv_path = tmp_path / "table_2.csv"
        with csv_path.open("wt", newline="") as out_file:
            data_writer = csv.writer(out_file)
            data_writer.writerows(
                [
                    ["Widget", "clock"],
                    ["Widget", "calendar"],
                ]
            )
        root_mapping = EntityClassMapping(0)
        root_mapping.child = EntityMapping(1)
        mapping_dict = {
            "source_type": DatapackageReader.__name__,
            "table_mappings": {
                "table_1": [
                    {"Mapping for table 1": {"mapping": mapping_to_dict(root_mapping)}},
                ],
                "table_2": [{"Mapping for table 2": {"mapping": mapping_to_dict(root_mapping)}}],
            },
            "selected_tables": ["table_1", "table_2"],
        }
        specification = ImporterSpecification("Test specification", mapping_dict)
        datapackage_path = _build_datapackage([csv_path])
        editor = ImportEditorWindow(spine_toolbox_with_project, specification, input_source=str(datapackage_path))
        QApplication.processEvents()
        with signal_waiter(editor._connection_manager.tables_ready, timeout=5.0) as waiter:
            waiter.wait()
        source_list_model = editor._ui.source_list.model()
        expected = ["Select all", "table_1", "table_2"]
        assert_list_model(source_list_model, expected)
        assert editor._ui.remove_unavailable_sources_button.isEnabled()
        editor._ui.remove_unavailable_sources_button.click()
        expected = ["Select all", "table_2"]
        assert_list_model(source_list_model, expected)
        tear_down_editor(editor)

    def test_undo_delete_tables_not_in_source(self, spine_toolbox_with_project, tmp_path):
        csv_path = tmp_path / "table_2.csv"
        with csv_path.open("wt", newline="") as out_file:
            data_writer = csv.writer(out_file)
            data_writer.writerows(
                [
                    ["Widget", "clock"],
                    ["Widget", "calendar"],
                ]
            )
        root_mapping = EntityClassMapping(0)
        root_mapping.child = EntityMapping(1)
        mapping_dict = {
            "source_type": DatapackageReader.__name__,
            "table_mappings": {
                "table_1": [
                    {"Mapping for table 1": {"mapping": mapping_to_dict(root_mapping)}},
                ],
                "table_2": [{"Mapping for table 2": {"mapping": mapping_to_dict(root_mapping)}}],
            },
            "selected_tables": ["table_1", "table_2"],
        }
        specification = ImporterSpecification("Test specification", mapping_dict)
        datapackage_path = _build_datapackage([csv_path])
        editor = ImportEditorWindow(spine_toolbox_with_project, specification, input_source=str(datapackage_path))
        QApplication.processEvents()
        with signal_waiter(editor._connection_manager.tables_ready, timeout=5.0) as waiter:
            waiter.wait()
        editor._ui.remove_unavailable_sources_button.click()
        source_list_model = editor._ui.source_list.model()
        assert editor._undo_stack.undoText() == "remove unavailable sources"
        editor._undo_stack.undo()
        expected = ["Select all", "table_1", "table_2"]
        assert_list_model(source_list_model, expected)
        tear_down_editor(editor)

    def test_delete_selected_source_tables(self, spine_toolbox_with_project, tmp_path):
        csv_path = tmp_path / "table_2.csv"
        with csv_path.open("wt", newline="") as out_file:
            data_writer = csv.writer(out_file)
            data_writer.writerows(
                [
                    ["Widget", "clock"],
                    ["Widget", "calendar"],
                ]
            )
        root_mapping = EntityClassMapping(0)
        root_mapping.child = EntityMapping(1)
        mapping_dict = {
            "source_type": DatapackageReader.__name__,
            "table_mappings": {
                "table_1": [
                    {"Mapping for table 1": {"mapping": mapping_to_dict(root_mapping)}},
                ],
                "table_2": [{"Mapping for table 2": {"mapping": mapping_to_dict(root_mapping)}}],
            },
            "selected_tables": ["table_1", "table_2"],
        }
        specification = ImporterSpecification("Test specification", mapping_dict)
        datapackage_path = _build_datapackage([csv_path])
        editor = ImportEditorWindow(spine_toolbox_with_project, specification, input_source=str(datapackage_path))
        QApplication.processEvents()
        with signal_waiter(editor._connection_manager.tables_ready, timeout=5.0) as waiter:
            waiter.wait()
        source_list_model = editor._ui.source_list.model()
        expected = ["Select all", "table_1", "table_2"]
        assert_list_model(source_list_model, expected)
        selection = QItemSelection(source_list_model.index(1, 0), source_list_model.index(2, 0))
        editor._ui.source_list.selectionModel().select(selection, QItemSelectionModel.SelectionFlag.ClearAndSelect)
        with mock.patch("spine_items.importer.widgets.custom_menus.SourceListMenu.get_action") as get_action:
            get_action.return_value = "Delete"
            editor._import_sources.show_source_list_context_menu(QPoint())
        expected = ["Select all", "table_2"]
        assert_list_model(source_list_model, expected)
        tear_down_editor(editor)


def tear_down_editor(editor):
    with mock.patch("spinetoolbox.project_item.specification_editor_window.QMessageBox.exec") as mock_exec:
        mock_exec.return_value = QMessageBox.StandardButton.Discard
        editor.tear_down()


def assert_list_model(model: QAbstractItemModel, expected):
    assert model.rowCount() == len(expected)
    for row, value in enumerate(expected):
        assert model.index(row, 0).data() == value


def _build_datapackage(file_paths):
    base_path = file_paths[0].parent
    while any(not path.relative_to(base_path) for path in file_paths[1:]):
        base_path = base_path.parent
    package = Package(basepath=base_path)
    for path in file_paths:
        package.add_resource(Resource(path=str(path.relative_to(base_path))))
    package_path = base_path / "datapackage.json"
    package.to_json(package_path)
    return package_path
