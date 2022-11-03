######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
A small widget to set up an output in Exporter properties tab.

:author: A. Soininen (VTT)
:date:   10.9.2019
"""

from PySide2.QtCore import Signal, Slot
from PySide2.QtWidgets import QWidget


class ExportListItem(QWidget):
    """A widget with few controls to select the export output label."""

    out_label_changed = Signal(str, str)
    """Emitted when the output label field is changed."""

    def __init__(self, in_label, out_label, parent=None):
        """
        Args:
            in_label (str): input resource label
            out_label (str): output resource label
            parent (QWidget): a parent widget
        """
        from ..ui.export_list_item import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(parent)
        self._ui = Ui_Form()
        self._in_label = in_label
        self._out_label = out_label
        self._ui.setupUi(self)
        self._ui.input_label_field.setText(f"<b>{in_label}</b>")
        self._ui.out_label_edit.setText(out_label)
        self._ui.out_label_edit.editingFinished.connect(self._emit_out_label_changed)

    @property
    def out_label_edit(self):
        """Output label QLineEdit"""
        return self._ui.out_label_edit

    @property
    def in_label_field(self):
        """Input label QLineEdit"""
        return self._ui.input_label_field

    @Slot()
    def _emit_out_label_changed(self):
        """Emits out_label_changed signal."""
        out_label = self._ui.out_label_edit.text()
        if self._out_label == out_label:
            return
        self._out_label = out_label
        self.out_label_changed.emit(out_label, self._in_label)
