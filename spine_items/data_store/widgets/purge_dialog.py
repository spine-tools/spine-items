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
"""Contains purge dialog's business code."""
from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QDialog, QDialogButtonBox

from spinetoolbox.widgets.select_database_items import SelectDatabaseItems


class PurgeDialog(QDialog):
    """Dialog for purging Data store's database."""

    def __init__(self, item_name, purge_settings, parent=None):
        """
        Args:
            item_name (str): project item's name
            purge_settings (dict, optional): purge settings
            parent (QWidget): parent widget
        """
        from ..ui.purge_dialog import Ui_Dialog

        super().__init__(parent)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)
        self.setWindowTitle(f"Purge items from {item_name}")
        self._item_check_boxes_widget = SelectDatabaseItems(purge_settings, self)
        self._ui.root_layout.insertWidget(0, self._item_check_boxes_widget)
        self._item_check_boxes_widget.checked_state_changed.connect(self._set_purge_button_enabled)
        self._purge_button = self._ui.button_box.addButton("Purge", QDialogButtonBox.AcceptRole)
        self._purge_button.setEnabled(self._item_check_boxes_widget.any_checked())

    @Slot(int)
    def _set_purge_button_enabled(self, _=None):
        """Enables or disables the purge button."""
        self._purge_button.setEnabled(self._item_check_boxes_widget.any_checked())

    def get_purge_settings(self):
        """Returns purge settings.

        Returns:
            dict: mapping from database item to purge flag
        """
        return self._item_check_boxes_widget.checked_states()
