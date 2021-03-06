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
from PySide2.QtWidgets import QUndoCommand
from .mvcmodels.mapping_list_model import MappingListModel


class NewMapping(QUndoCommand):
    def __init__(self, mapping_list_model, mapping_specification):
        """
        Args:
            mapping_list_model (MappingListModel): mapping list model
            mapping_specification (MappingSpecification): new mapping specification
        """
        super().__init__("add mapping")
        self._mapping_list_model = mapping_list_model
        self._mapping_specification = mapping_specification
        self._row = 0

    def redo(self):
        self._row = self._mapping_list_model.extend(deepcopy(self._mapping_specification))

    def undo(self):
        self._mapping_list_model.remove_mapping(self._row)


class RemoveMapping(QUndoCommand):
    def __init__(self, row, mapping_list_model):
        """
        Args:
            row (int): row index of mapping's name
            mapping_list_model (MappingListModel): mapping list model
        """
        super().__init__("remove mapping")
        self._mapping_list_model = mapping_list_model
        self._row = row
        self._name = self._mapping_list_model.index(row, 0).data()
        self._mapping_specification = self._mapping_list_model.index(row, 0).data(
            MappingListModel.MAPPING_SPECIFICATION_ROLE
        )

    def redo(self):
        self._mapping_list_model.remove_mapping(self._row)

    def undo(self):
        self._mapping_list_model.insert_mapping(self._row, self._name, self._mapping_specification)


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
        self._previous_mapping = self._index.data(MappingListModel.MAPPING_ROOT_ROLE)

    def redo(self):
        self._index.model().setData(self._index, deepcopy(self._mapping), MappingListModel.MAPPING_ROOT_ROLE)

    def undo(self):
        self._index.model().setData(self._index, deepcopy(self._previous_mapping), MappingListModel.MAPPING_ROOT_ROLE)


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
        self._previous_type = self._index.data(MappingListModel.MAPPING_TYPE_ROLE)

    def redo(self):
        self._index.model().setData(self._index, self._type, MappingListModel.MAPPING_TYPE_ROLE)

    def undo(self):
        self._index.model().setData(self._index, self._previous_type, MappingListModel.MAPPING_TYPE_ROLE)


class SetExportObjectsFlag(QUndoCommand):
    def __init__(self, index, flag):
        """
        Args:
            index (QModelIndex): mapping's row index
            flag (bool): export object flag
        """
        super().__init__(("check" if flag else "uncheck") + " export objects checkbox")
        self._index = index
        self._flag = flag

    def redo(self):
        self._index.model().setData(self._index, self._flag, MappingListModel.EXPORT_OBJECTS_FLAG_ROLE)

    def undo(self):
        self._index.model().setData(self._index, not self._flag, MappingListModel.EXPORT_OBJECTS_FLAG_ROLE)


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
        self._index.model().setData(self._index, self._flag, MappingListModel.USE_FIXED_TABLE_NAME_FLAG_ROLE)

    def undo(self):
        self._index.model().setData(self._index, not self._flag, MappingListModel.USE_FIXED_TABLE_NAME_FLAG_ROLE)


class SetFixedTitle(QUndoCommand):
    def __init__(self, model, title, previous_title):
        """
        Args:
            model (MappingTableModel): mapping model
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


class SetMappingPosition(QUndoCommand):
    def __init__(self, model, mapping_name, row, position, previous_position):
        """
        Args:
            model (MappingTableModel): mapping model
            mapping_name (str): mapping's name
            row (int): model row
            position (int, Position, optional): mapping's new position
            previous_position (int, Position, optional): previous position
        """
        super().__init__("change mapping position")
        self._mapping_table_model = model
        self._mapping_name = mapping_name
        self._row = row
        self._position = position
        self._previous_position = previous_position

    def redo(self):
        self._mapping_table_model.set_position(self._position, self._row, self._mapping_name)

    def undo(self):
        self._mapping_table_model.set_position(self._previous_position, self._row, self._mapping_name)


class SetMappingProperty(QUndoCommand):
    def __init__(self, command_name, setter, mapping_name, row, value, previous_value):
        """
        Sets either ``header`` or ``filter_re``.

        Args:
            command_name (str)
            setter (function): setter function
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
