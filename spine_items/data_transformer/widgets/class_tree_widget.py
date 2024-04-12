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

"""Contains :class:`ClassTreeWidget`."""
import pickle
from PySide6.QtCore import QMimeData
from PySide6.QtWidgets import QTreeWidget, QMessageBox, QTreeWidgetItem
from spinedb_api import DatabaseMapping, SpineDBAPIError
from .drop_target_table import DROP_MIME_TYPE


class ClassTreeWidget(QTreeWidget):
    """A tree widget with drag capabilities to show entity classes."""

    def mimeData(self, items):
        mime_data = QMimeData()
        classes = [item.text(0) for item in items]
        mime_data.setData(DROP_MIME_TYPE, pickle.dumps(classes))
        return mime_data

    def load_data(self, url):
        """
        Loads parameter data from given URL.

        Args:
            url (str): database URL
        """
        try:
            db_map = DatabaseMapping(url)
        except SpineDBAPIError as error:
            QMessageBox.information(self, "Error while opening database", f"Could not open database {url}:\n{error}")
            return
        classes = list()
        try:
            for class_row in db_map.query(db_map.entity_class_sq):
                classes.append(class_row.name)
        except SpineDBAPIError as error:
            QMessageBox.information(
                self, "Error while reading database", f"Could not read from database {url}:\n{error}"
            )
        finally:
            db_map.close()
        self.clear()
        for class_name in classes:
            self.addTopLevelItem(QTreeWidgetItem([class_name]))
