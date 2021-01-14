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
Contains a widget to set up a renamer filter.

:author: A. Soininen (VTT)
:date:   30.10.2020
"""
from PySide2.QtWidgets import QMessageBox, QWidget
from spinedb_api import DatabaseMapping, SpineDBAPIError
from ..mvcmodels.rename_table_model import RenameTableModel
from ..settings import EntityClassRenamingSettings


class EntityClassRenamingWidget(QWidget):
    """Widget for entity class renamer settings."""

    def __init__(self, settings=None):
        """
        Args:
            settings (EntityClassRenamingSettings): filter settings
        """
        super().__init__()
        from ..ui.renamer_editor import Ui_Form  # pylint: disable=import-outside-toplevel

        self._ui = Ui_Form()
        self._ui.setupUi(self)
        name_map = settings.name_map if isinstance(settings, EntityClassRenamingSettings) else {}
        self._rename_table_model = RenameTableModel(name_map)
        self._ui.renaming_table.setModel(self._rename_table_model)

    def load_data(self, url):
        """
        Loads entity class names from given URL.

        Args:
            url (str): database URL
        """
        try:
            db_map = DatabaseMapping(url)
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
        self._rename_table_model.reset_originals(names)

    def settings(self):
        """
        Returns filter's settings.

        Returns:
            FilterSettings: settings
        """
        return EntityClassRenamingSettings(self._rename_table_model.renaming_settings())
