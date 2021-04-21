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
Contains Exporter's undo commands.

:authors: A. Soininen (VTT)
:date:    11.12.2020
"""
from copy import deepcopy
from PySide2.QtCore import QModelIndex, Qt
from PySide2.QtWidgets import QUndoCommand
from .mvcmodels.mappings_table_model import MappingsTableModel


class NewMapping(QUndoCommand):
    def __init__(self, mappings_table_model, mapping_specification):
        """
        Args:
            mappings_table_model (MappingsTableModel): mapping table model
            mapping_specification (MappingSpecification): new mapping specification
        """
        super().__init__("add mapping")
        self._mappings_table_model = mappings_table_model
        self._mapping_specification = mapping_specification
        self._mapping_name = None

    def redo(self):
        self._mappings_table_model.extend(deepcopy(self._mapping_specification))
        self._mapping_name = self._mappings_table_model.index(self._mappings_table_model.rowCount() - 1, 0).data()

    def undo(self):
        self._mappings_table_model.remove_mapping(self._mapping_name)


class RemoveMapping(QUndoCommand):
    def __init__(self, row, mappings_table_model):
        """
        Args:
            row (int): row index of mapping's name
            mappings_table_model (MappingsTableModel): mapping list model
        """
        super().__init__("remove mapping")
        self._mappings_table_model = mappings_table_model
        self._row = row
        index = self._mappings_table_model.index(row, 0)
        self._name = index.data()
        self._mapping_specification = index.data(MappingsTableModel.MAPPING_SPECIFICATION_ROLE)

    def redo(self):
        self._mappings_table_model.remove_mapping(self._name)

    def undo(self):
        self._mappings_table_model.insert_mapping(self._row, self._name, self._mapping_specification)


class SetMappingEnabled(QUndoCommand):
    def __init__(self, row, mappings_table_model):
        """
        Args:
            row (int): row index of mapping's name
            mappings_table_model (MappingsTableModel): mapping list model
        """
        self._mappings_table_model = mappings_table_model
        name = self._mappings_table_model.index(row, 0).data()
        self._row = row
        self._previously_enabled = self._mappings_table_model.index(self._row, 0).data(Qt.CheckStateRole) == Qt.Checked
        super().__init__(("disable" if self._previously_enabled else "enable") + f" '{name}'")

    def redo(self):
        self._mappings_table_model.set_mapping_enabled(self._row, not self._previously_enabled)

    def undo(self):
        self._mappings_table_model.set_mapping_enabled(self._row, self._previously_enabled)


class EnableAllMappings(QUndoCommand):
    def __init__(self, mappings_table_model):
        """
        Args:
            mappings_table_model (MappingsTableModel): mapping list model
        """
        super().__init__("enable all mappings")
        self._mappings_table_model = mappings_table_model
        self._previously_enabled = self._mappings_table_model.enabled_mapping_rows()

    def redo(self):
        self._mappings_table_model.set_all_enabled(True)

    def undo(self):
        self._mappings_table_model.enable_mapping_rows(self._previously_enabled)


class DisableAllMappings(QUndoCommand):
    def __init__(self, mappings_table_model):
        """
        Args:
            mappings_table_model (MappingsTableModel): mapping list model
        """
        super().__init__("disable all mappings")
        self._mappings_table_model = mappings_table_model

    def redo(self):
        self._mappings_table_model.set_all_enabled(False)

    def undo(self):
        self._mappings_table_model.set_all_enabled(True)


class ChangeWriteOrder(QUndoCommand):
    def __init__(self, row, earlier, mappings_table_model):
        """
        Args:
            row (int): row index of mapping's name
            earlier (bool): True to write mapping earlier, False to write later
            mappings_table_model (MappingsTableModel): mappings table model
        """
        super().__init__("change writing order")
        self._row = row
        self._earlier = earlier
        self._mappings_table_model = mappings_table_model

    def redo(self):
        self._mappings_table_model.reorder_writing(self._row, self._earlier)

    def undo(self):
        self._mappings_table_model.reorder_writing(self._row - 1 if self._earlier else self._row + 1, not self._earlier)


class SetMapping(QUndoCommand):
    def __init__(self, index, mapping):
        """
        Args:
            index (QModelIndex): mapping's row index
            mapping (Mapping): mapping root
        """
        super().__init__("mapping change")
        self._index = index
        self._mapping = mapping
        self._previous_mapping = self._index.data(MappingsTableModel.MAPPING_ROOT_ROLE)

    def redo(self):
        self._index.model().setData(self._index, deepcopy(self._mapping), MappingsTableModel.MAPPING_ROOT_ROLE)

    def undo(self):
        self._index.model().setData(self._index, deepcopy(self._previous_mapping), MappingsTableModel.MAPPING_ROOT_ROLE)


class SetMappingType(QUndoCommand):
    def __init__(self, index, type_):
        """
        Args:
            index (QModelIndex): mapping's row index
            type_ (MappingType): mapping type
        """
        super().__init__("mapping type change")
        self._index = index
        self._type = type_
        self._previous_type = self._index.data(MappingsTableModel.MAPPING_TYPE_ROLE)

    def redo(self):
        self._index.model().setData(self._index, self._type, MappingsTableModel.MAPPING_TYPE_ROLE)

    def undo(self):
        self._index.model().setData(self._index, self._previous_type, MappingsTableModel.MAPPING_TYPE_ROLE)


class SetAlwaysExportHeader(QUndoCommand):
    def __init__(self, index, always_export_header):
        """
        Args:
            index (QModelIndex): mapping's row index
            always_export_header (bool): always export header flag
        """
        super().__init__(("check" if always_export_header else "uncheck") + " always export header checkbox")
        self._index = index
        self._flag = always_export_header

    def redo(self):
        self._index.model().setData(self._index, self._flag, MappingsTableModel.ALWAYS_EXPORT_HEADER_ROLE)

    def undo(self):
        self._index.model().setData(self._index, not self._flag, MappingsTableModel.ALWAYS_EXPORT_HEADER_ROLE)


class SetUseFixedTableNameFlag(QUndoCommand):
    def __init__(self, index, flag):
        """
        Args:
            index (QModelIndex): mapping's row index
            flag (bool): use fixed table name flag
        """
        super().__init__(("check" if flag else "uncheck") + " fixed table name checkbox")
        self._index = index
        self._flag = flag

    def redo(self):
        self._index.model().setData(self._index, self._flag, MappingsTableModel.USE_FIXED_TABLE_NAME_FLAG_ROLE)

    def undo(self):
        self._index.model().setData(self._index, not self._flag, MappingsTableModel.USE_FIXED_TABLE_NAME_FLAG_ROLE)


class SetFixedTitle(QUndoCommand):
    def __init__(self, model, title, previous_title):
        """
        Args:
            model (MappingEditorTableModel): editor model
            title (str): table name
            previous_title (str): previous table name
        """
        super().__init__("change table name")
        self._model = model
        self._title = title
        self._previous_title = previous_title

    def redo(self):
        self._model.set_fixed_title(self._title)

    def undo(self):
        self._model.set_fixed_title(self._previous_title)


class SetMappingPositions(QUndoCommand):
    def __init__(self, model, mapping_name, positions, previous_positions):
        """
        Args:
            model (MappingEditorTableModel): editor model
            mapping_name (str): mapping's name
            positions (list of Position): new positions
            previous_positions (list of Position): previous positions
        """
        super().__init__("change mapping position")
        self._mapping_editor_table_model = model
        self._mapping_name = mapping_name
        self._positions = positions
        self._previous_positions = previous_positions

    def redo(self):
        self._mapping_editor_table_model.set_positions(self._positions, self._mapping_name)

    def undo(self):
        self._mapping_editor_table_model.set_positions(self._previous_positions, self._mapping_name)


class SetMappingProperty(QUndoCommand):
    def __init__(self, command_name, setter, mapping_name, row, value, previous_value):
        """
        Sets either ``header`` or ``filter_re``.

        Args:
            command_name (str)
            setter (Callable): setter function
            mapping_name (str): mapping's name
            row (int): model row
            value (str): mapping's new value for the property
            previous_value (str): previous value
        """
        super().__init__(command_name)
        self._setter = setter
        self._mapping_name = mapping_name
        self._row = row
        self._value = value
        self._previous_value = previous_value

    def redo(self):
        self._setter(self._value, self._row, self._mapping_name)

    def undo(self):
        self._setter(self._previous_value, self._row, self._mapping_name)


class CompactMapping(QUndoCommand):
    def __init__(self, model, mapping_name):
        """
        Args:
            model (MappingEditorTableModel): editor model
            mapping_name (str): mapping's name
        """
        super().__init__("compact mapping")
        self._model = model
        self._mapping_name = mapping_name
        self._previous_positions = self._model.positions()

    def redo(self):
        self._model.compact()

    def undo(self):
        self._model.set_positions(self._previous_positions, self._mapping_name)


class SetExportFormat(QUndoCommand):
    def __init__(self, editor, export_format, previous_format):
        """
        Args:
            editor (SpecificationEditor): specification editor window
            export_format (OutputFormat): new format
            previous_format (OutputFormat): previous format
        """
        super().__init__("change export format")
        self._specification_editor = editor
        self._format = export_format
        self._previous_format = previous_format

    def redo(self):
        self._specification_editor.set_export_format_silently(self._format)

    def undo(self):
        self._specification_editor.set_export_format_silently(self._previous_format)
