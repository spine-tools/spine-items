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
Contains mapping filter editor delegate.

:author: A. Soininen (VTT)
:date:   13.4.2021
"""
from PySide2.QtCore import Property, Qt
from PySide2.QtWidgets import QStyledItemDelegate, QWidget
from spinedb_api.export_mapping.export_mapping import ParameterValueTypeMapping
from ..mvcmodels.mapping_editor_table_model import MappingEditorTableModel
from ..ui import default_filter_editor, value_type_filter_editor


class FilterEditDelegate(QStyledItemDelegate):
    """Edit delegate for Mapping table's filter column."""

    def createEditor(self, parent, option, index):
        mapping = index.data(MappingEditorTableModel.MAPPING_ITEM_ROLE)
        if isinstance(mapping, ParameterValueTypeMapping):
            return _FilterEdit(value_type_filter_editor.Ui_Form(), parent)
        return _FilterEdit(default_filter_editor.Ui_Form(), parent)

    def updateEditorGeometry(self, editor, option, index):
        top_left = option.rect.topLeft()
        popup_position = editor.parent().mapToGlobal(top_left)
        size_hint = editor.sizeHint()
        editor.setGeometry(
            popup_position.x(), popup_position.y(), max(option.rect.width(), size_hint.width()), size_hint.height()
        )


class _FilterEdit(QWidget):
    """Filter regular expression editor."""

    def __init__(self, ui_form, parent):
        """
        Args:
            ui_form (Any): an interface from created from a .ui file
            parent (QWidget):
        """
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup)
        self._ui = ui_form
        self._ui.setupUi(self)

    def focusInEvent(self, e):
        self._ui.regexp_line_edit.setFocus()
        super().focusInEvent(e)

    def regexp(self):
        """Returns the current regular expression.

        Returns:
            str: regular expression
        """
        return self._ui.regexp_line_edit.text()

    def set_regexp(self, regexp):
        """Sets a regular expression for editing.

        Args:
            regexp (str): new regular expression
        """
        self._ui.regexp_line_edit.setText(regexp)

    regexp = Property(str, regexp, set_regexp, user=True)
    """Property used to communicate with the editor delegate."""
