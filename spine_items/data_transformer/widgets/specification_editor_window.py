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
Contains :class:`SettingsWindow`.

:author: A. Soininen (VTT)
:date:   2.10.2020
"""
import os.path
from PySide2.QtCore import Qt, Signal, Slot
from PySide2.QtWidgets import QFileDialog, QMessageBox, QWidget
from spinedb_api import clear_filter_configs, DatabaseMapping, SpineDBAPIError
from ..data_transformer_specification import DataTransformerSpecification
from ..mvcmodels.rename_table_model import RenameTableModel


class SpecificationEditorWindow(QWidget):
    """Data transformer's specification editor."""

    accepted = Signal(str)
    """Emitted when the specification has be accepted by the user."""

    def __init__(self, toolbox, specification, item_name=None):
        """
        Args:
            toolbox (ToolboxUI): Toolbox main window
            specification (ProjectItemSpecification, optional): transformer specification's name
            item_name (str, optional): invoking project item's name, if window was opened from its properties tab
        """
        from ..ui.specification_editor_widget import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(parent=toolbox, f=Qt.Window | Qt.WA_DeleteOnClose)
        self._toolbox = toolbox
        if specification is None:
            specification = DataTransformerSpecification(name="", renaming=dict())
        self._specification = specification
        self._class_renaming_model = RenameTableModel(self._specification.entity_class_name_map())
        self._urls = dict()
        self._ui = Ui_Form()
        self._ui.setupUi(self)
        title = "Edit Data transformer specification"
        if item_name is not None:
            title = title + f"    -- {item_name} --"
        self.setWindowTitle(title)
        if self._specification.name:
            self._ui.specification_name_edit.setText(self._specification.name)
        if self._specification.description:
            self._ui.specification_description_edit.setText(self._specification.description)
        self._ui.renaming_table.setModel(self._class_renaming_model)
        self._ui.load_url_from_fs_button.clicked.connect(self._load_url_from_filesystem)
        self._ui.load_entity_classes_button.clicked.connect(self._load_entity_classes)
        self._ui.button_box.rejected.connect(self.close)
        self._ui.button_box.accepted.connect(self._accept_settings)
        self._ui.database_url_combo_box.model().rowsInserted.connect(
            lambda *args: self._ui.load_entity_classes_button.setEnabled(True)
        )
        self._class_renaming_model.modelReset.connect(self._ui.renaming_table.resizeColumnsToContents)

    def set_available_databases(self, urls):
        """
        Sets fetchable database URLs.

        Args:
            transformation_stacks (dict): mapping from database url to list of transformation configs
        """
        self._urls = {clear_filter_configs(url): url for url in urls}
        self._ui.database_url_combo_box.clear()
        self._ui.database_url_combo_box.addItems(sorted(self._urls))

    @Slot()
    def _accept_settings(self):
        """Stores the specification to Toolbox' specification list, emits the accepted signal and closes the window."""
        specification_name = self._ui.specification_name_edit.text()
        if not specification_name:
            QMessageBox.information(self, "Specification name missing", "Please enter a name for the specification.")
            return
        existing = self._toolbox.specification_model.find_specification(specification_name)
        if existing is not None:
            # Specification names are case insensitive. Make sure we use the correct casing.
            specification_name = existing.name
            self._ui.specification_name_edit.setText(specification_name)
        description = self._ui.specification_description_edit.text()
        name_map = self._class_renaming_model.renaming_settings()
        self._specification = DataTransformerSpecification(specification_name, name_map, description)
        if not self._store_specification():
            return
        self.accepted.emit(self._specification.name)
        self.close()

    def _browse_database(self):
        """
        Queries a database file from the user.

        Returns:
            str: path to database file
        """
        initial_path = self._toolbox.project().project_dir
        return QFileDialog.getOpenFileName(self, "Select database", initial_path, "sqlite (*.sqlite)")[0]

    @Slot(bool)
    def _load_url_from_filesystem(self, _):
        path = self._browse_database()
        if not path:
            return
        url = "sqlite:///" + path
        self._ui.database_url_combo_box.addItem(url)
        self._urls[url] = url

    @Slot(bool)
    def _load_entity_classes(self, _):
        """Loads entity class names to the class renaming table."""
        url = self._ui.database_url_combo_box.currentText()
        if not url:
            return
        try:
            db_map = DatabaseMapping(self._urls[url])
        except SpineDBAPIError as error:
            QMessageBox.information(self, "Error while opening database", f"Could not open database {url}:\n{error}")
            return
        names = set()
        try:
            for entity_class_row in db_map.query(db_map.entity_class_sq).all():
                names.add(entity_class_row.name)
        except SpineDBAPIError as error:
            QMessageBox.information(
                self, "Error while reading database", f"Could not read from database {url}:\n{error}"
            )
        finally:
            db_map.connection.close()
        self._class_renaming_model.reset_originals(names)

    def _store_specification(self):
        """
        Stores the specification.

        Returns:
            bool: True if the operation was successful, False otherwise
        """
        row = self._toolbox.specification_model.specification_row(self._specification.name)
        if row >= 0:
            old_specification = self._toolbox.specification_model.specification(row)
            if old_specification.is_equivalent(self._specification):
                return True
            self._specification.definition_file_path = old_specification.definition_file_path
            self._toolbox.update_specification(row, self._specification)
            return True
        initial_path = self._specification.definition_file_path
        if not initial_path:
            initial_path = self._toolbox.project().project_dir
        path = QFileDialog.getSaveFileName(
            self, "Save Data Transformer specification file", initial_path, "JSON (*.json)"
        )[0]
        if not path:
            return False
        self._specification.definition_file_path = os.path.abspath(path)
        self._toolbox.add_specification(self._specification)
        self._specification.save()
        return True
