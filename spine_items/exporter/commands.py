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

"""Contains Exporter's undo commands."""
from copy import copy, deepcopy
from enum import IntEnum, unique
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QUndoCommand

from spinetoolbox.helpers import SealCommand
from spinetoolbox.project_commands import SpineToolboxCommand
from .mvcmodels.mappings_table_model import MappingsTableModel


@unique
class CommandId(IntEnum):
    CHANGE_POSITION = 1
    CHANGE_FIXED_TABLE_NAME = 2
    CHANGE_OUT_LABEL = 3


class UpdateOutLabel(SpineToolboxCommand):
    """Command to update exporter's output label."""

    def __init__(self, exporter_name, out_label, in_label, previous_label, project):
        """
        Args:
            exporter_name (str): exporter's name
            out_label (str): new output resource label
            in_label (str): associated input resource label
            previous_label (str): previous output resource label
            project (SpineToolboxProject): project
        """
        super().__init__()
        self._exporter_name = exporter_name
        self._out_label = out_label
        self._previous_out_label = previous_label
        self._in_label = in_label
        self._project = project
        self.setText(f"change output label in {exporter_name}")
        self._sealed = False

    def id(self):
        return 1

    def redo(self):
        exporter = self._project.get_item(self._exporter_name)
        exporter.set_out_label(self._out_label, self._in_label)

    def undo(self):
        exporter = self._project.get_item(self._exporter_name)
        exporter.set_out_label(self._previous_out_label, self._in_label)

    def mergeWith(self, other):
        if not self._sealed:
            if (
                isinstance(other, UpdateOutLabel)
                and self._exporter_name == other._exporter_name
                and self._in_label == other._in_label
            ):
                if self._previous_out_label != other._out_label:
                    self._out_label = other._out_label
                else:
                    self.setObsolete(True)
                return True
            if isinstance(other, SealCommand):
                self._sealed = True
                return True
        return False


class UpdateOutUrl(SpineToolboxCommand):
    """Command to update exporter's output URL."""

    def __init__(self, exporter_name, in_label, url, previous_url, project):
        """
        Args:
            exporter_name (str): exporter's name
            in_label (str): input resource label
            url (dict, optional): new URL dict
            previous_url (dict, optional): previous URL dict
            project (SpineToolboxProject): project
        """
        super().__init__()
        self._exporter_name = exporter_name
        self._in_label = in_label
        self._url = copy(url)
        self._previous_url = copy(previous_url)
        self._project = project
        self.setText(f"change output URL in {exporter_name}")

    def redo(self):
        exporter = self._project.get_item(self._exporter_name)
        exporter.set_out_url(self._in_label, copy(self._url))

    def undo(self):
        exporter = self._project.get_item(self._exporter_name)
        exporter.set_out_url(self._in_label, copy(self._previous_url))


class NewMapping(QUndoCommand):
    def __init__(self, mappings_table_model, mapping_specification, name=""):
        """
        Args:
            mappings_table_model (MappingsTableModel): mapping table model
            mapping_specification (MappingSpecification): new mapping specification
            name (str): specification's name
        """
        super().__init__("add mapping")
        self._mappings_table_model = mappings_table_model
        self._mapping_specification = mapping_specification
        self._mapping_name = name

    def redo(self):
        row = self._mappings_table_model.extend(deepcopy(self._mapping_specification), self._mapping_name)
        self._mapping_name = self._mappings_table_model.index(row, 0).data()

    def undo(self):
        self._mappings_table_model.remove_mapping(self._mapping_name)


class RenameMapping(QUndoCommand):
    """A command to change the name of a mapping."""

    def __init__(self, row, mapping_list_model, name):
        """
        Args:
            row (int): row index
            mapping_list_model (MappingListModel): model holding the mapping names
            name (str): new name
        """
        text = "rename mapping"
        super().__init__(text)
        self._row = row
        self._model = mapping_list_model
        self._name = name
        self._previous_name = self._model.index(self._row, 0).data()

    def redo(self):
        """Renames the mapping."""
        self._model.rename_mapping(self._row, self._name)

    def undo(self):
        """Reverts renaming of the mapping."""
        self._model.rename_mapping(self._row, self._previous_name)


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
        self._previously_enabled = (
            self._mappings_table_model.index(self._row, 0).data(Qt.ItemDataRole.CheckStateRole).value
            == Qt.CheckState.Checked.value
        )
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


class SetFixedTableName(QUndoCommand):
    ID = CommandId.CHANGE_FIXED_TABLE_NAME.value

    def __init__(self, index, old_name, new_name):
        """
        Args:
            index (QModelIndex): mapping's row index
            old_name (str): old fixed table name
            new_name (str): new fixed table name
        """
        super().__init__("change fixed table name")
        self._index = index
        self._old_name = old_name
        self._new_name = new_name
        self._sealed = False

    def redo(self):
        self._index.model().setData(self._index, self._new_name, MappingsTableModel.FIXED_TABLE_NAME_ROLE)

    def undo(self):
        self._index.model().setData(self._index, self._old_name, MappingsTableModel.FIXED_TABLE_NAME_ROLE)

    def id(self):
        return self.ID

    def mergeWith(self, other):
        if not self._sealed:
            if isinstance(other, SetFixedTableName) and self.id() == other.id() and self._index == other._index:
                if self._old_name != other._new_name:
                    self._new_name = other._new_name
                else:
                    self.setObsolete(True)
                return True
            if isinstance(other, SealCommand):
                self._sealed = True
                return True
        return False


class SetGroupFunction(QUndoCommand):
    def __init__(self, index, old_function, new_function):
        """
        Args
            index (QModelIndex): mapping's row index
            old_function (str): old group function's name
            new_function (str): new group function's name
        """
        super().__init__("change group function")
        self._index = index
        self._old_function = old_function
        self._new_function = new_function

    def redo(self):
        self._index.model().setData(self._index, self._new_function, MappingsTableModel.GROUP_FN_ROLE)

    def undo(self):
        self._index.model().setData(self._index, self._old_function, MappingsTableModel.GROUP_FN_ROLE)


class SetHighlightDimension(QUndoCommand):
    def __init__(self, index, old_dimension, new_dimension):
        """
        Args
            index (QModelIndex): mapping's row index
            old_dimension (int): old highlight dimension
            new_dimension (int): new highlight dimension
        """
        super().__init__("change selected relationship dimension")
        self._index = index
        self._old_dimension = old_dimension
        self._new_dimension = new_dimension

    def redo(self):
        self._index.model().setData(self._index, self._new_dimension, MappingsTableModel.HIGHLIGHT_POSITION_ROLE)

    def undo(self):
        self._index.model().setData(self._index, self._old_dimension, MappingsTableModel.HIGHLIGHT_POSITION_ROLE)


class SetMappingPositions(QUndoCommand):
    def __init__(self, model, mapping_name, positions, previous_positions):
        """
        Args:
            model (MappingEditorTableModel): editor model
            mapping_name (str): mapping's name
            positions (list of Position): new positions
            previous_positions (list of Position): previous positions
        """
        super().__init__("change mapping item's position")
        self._mapping_editor_table_model = model
        self._mapping_name = mapping_name
        self._positions = positions
        self._previous_positions = previous_positions

    @property
    def mapping_editor_table_model(self):
        return self._mapping_editor_table_model

    @property
    def mapping_name(self):
        return self._mapping_name

    @property
    def positions(self):
        return self._positions

    @property
    def previous_positions(self):
        return self._previous_positions

    def id(self):
        return int(CommandId.CHANGE_POSITION)

    def redo(self):
        self._mapping_editor_table_model.set_positions(self._positions, self._mapping_name)

    def undo(self):
        self._mapping_editor_table_model.set_positions(self._previous_positions, self._mapping_name)


class ClearFixedTableName(QUndoCommand):
    def __init__(self, editor, is_fixed_table_checked, previous_fixed_table_name, mapping_index, mapping_root):
        """
        Args:
            editor (SpecificationEditor): specification editor window
            is_fixed_table_checked (bool): state of the fixed table name checkbox before clearing
            previous_fixed_table_name (str): fixed table name before clearing
            mapping_index (QModelIndex): mapping's row index
            mapping_root (Mapping): mapping root
        """
        super().__init__("change mapping item's position")
        self._editor = editor
        self._is_fixed_table_checked = is_fixed_table_checked
        self._previous_fixed_table_name = previous_fixed_table_name
        self._mapping_editor_table_model = None
        self._mapping_name = None
        self._positions = None
        self._previous_positions = None
        self._mapping_index = mapping_index
        self._mapping_root = mapping_root
        self._previous_mapping_root = self._mapping_index.data(MappingsTableModel.MAPPING_ROOT_ROLE)

    def id(self):
        return int(CommandId.CHANGE_POSITION)

    def mergeWith(self, other):
        if self._mapping_editor_table_model is not None:
            return False
        self._mapping_editor_table_model = other.mapping_editor_table_model
        self._mapping_name = other.mapping_name
        self._positions = other.positions
        self._previous_positions = other.previous_positions
        return True

    def redo(self):
        self._editor.clear_fixed_table_name()
        self._mapping_index.model().setData(
            self._mapping_index, deepcopy(self._mapping_root), MappingsTableModel.MAPPING_ROOT_ROLE
        )

    def undo(self):
        self._mapping_index.model().setData(
            self._mapping_index, deepcopy(self._previous_mapping_root), MappingsTableModel.MAPPING_ROOT_ROLE
        )
        self._editor.enable_fixed_table_name(self._is_fixed_table_checked, self._previous_fixed_table_name)
        if self._mapping_editor_table_model is not None:
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


class SetMappingNullable(QUndoCommand):
    def __init__(self, model, mapping_name, row, nullable):
        """
        Args:
            model (MappingEditorTableModel): editor model
            mapping_name (str): mapping's name
            row (int): row index in model
            nullable (bool): True to set, False to unset
        """
        super().__init__(("set " if nullable else "unset ") + " mapping item nullable")
        self._model = model
        self._mapping_name = mapping_name
        self._row = row
        self._nullable = nullable

    def redo(self):
        self._model.set_nullable(self._nullable, self._row, self._mapping_name)

    def undo(self):
        self._model.set_nullable(not self._nullable, self._row, self._mapping_name)


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


class UpdateOutputTimeStampsFlag(SpineToolboxCommand):
    """Command to set exporter's output directory time stamps flag."""

    def __init__(self, exporter_name, value, project):
        """
        Args:
            exporter_name (str): exporter's name
            value (bool): flag's new value
            project (SpineToolboxProject): project
        """
        super().__init__()
        self.setText(f"toggle output time stamps setting of {exporter_name}")
        self._exporter_name = exporter_name
        self._value = value
        self._project = project

    def redo(self):
        exporter = self._project.get_item(self._exporter_name)
        exporter.set_output_time_stamps_flag(self._value)

    def undo(self):
        exporter = self._project.get_item(self._exporter_name)
        exporter.set_output_time_stamps_flag(not self._value)
