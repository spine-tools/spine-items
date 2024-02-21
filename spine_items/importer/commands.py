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

"""Contains undo and redo commands for Import editor."""
import pickle
from enum import auto, IntEnum, unique
from PySide6.QtCore import Qt
from PySide6.QtGui import QUndoCommand
from spinedb_api import import_mapping_from_dict
from spinedb_api.import_mapping.import_mapping_compat import parse_named_mapping_spec
from spine_items.importer.mvcmodels.mappings_model_roles import Role


@unique
class _Id(IntEnum):
    SET_OPTION = auto()


class PasteMappings(QUndoCommand):
    """Command to paste copied mappings"""

    def __init__(self, table_row, list_row, model, copied_mappings):
        """
        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            model (MappingsModel): model
            copied_mappings (Iterable of dict): mappings to paste
        """
        super().__init__("paste mappings")
        self._table_row = table_row
        self._list_row = list_row
        self._model = model
        self._mapping_dicts = copied_mappings

    def redo(self):
        """Pastes the copied mappings."""
        table_index = self._model.index(self._table_row, 0)
        for i, mapping_dict in enumerate(self._mapping_dicts):
            name, root_mapping = parse_named_mapping_spec(mapping_dict)
            row = self._list_row + i
            self._model.insertRow(row, table_index)
            self._model.rename_mapping(self._table_row, row, name)
            self._model.set_root_mapping(self._table_row, row, root_mapping)

    def undo(self):
        """Removes pasted mappings."""
        table_index = self._model.index(self._table_row, 0)
        self._model.removeRows(self._list_row, len(self._mapping_dicts), table_index)


class PasteOptions(QUndoCommand):
    """Command to paste copied mapping options."""

    def __init__(self, import_sources, source_table_name, pickled_options, previous_options):
        """
        Args:
            import_sources (ImportSources): import editor
            source_table_name (str): name of the target source table
            pickled_options (bytes): pickled options
            previous_options (bytes): pickled previous options
        """
        super().__init__("paste options")
        self._import_sources = import_sources
        self._source_table_name = source_table_name
        self._pickled_options = pickled_options
        self._previous_options = previous_options

    def redo(self):
        """Pastes the options."""
        self._import_sources.paste_options(self._source_table_name, pickle.loads(self._pickled_options))

    def undo(self):
        """Restores the options to their previous values."""
        self._import_sources.paste_options(self._source_table_name, pickle.loads(self._previous_options))


class SetTableChecked(QUndoCommand):
    """Command to change a source table's checked state."""

    def __init__(self, table_name, model, checked, *rows):
        """
        Args:
            table_name (str, optional): source table name
            model (MappingsModel): model
            checked (bool): new checked state
            *rows: table row on the list
        """
        if table_name is not None:
            text = ("select" if checked else "deselect") + f" '{table_name}'"
        else:
            text = ("select" if checked else "deselect") + " all source tables'"
        super().__init__(text)
        self._model = model
        self._rows = rows
        self._checked = checked

    def redo(self):
        """Changes the checked state."""
        self._model.set_table_checked(self._checked, *self._rows)

    def undo(self):
        """Restores the previous checked state."""
        self._model.set_table_checked(not self._checked, *self._rows)


class UpdateTableItem(QUndoCommand):
    """Command to update table name and state in file-less mode."""

    def __init__(self, model, row, old_data, new_data, is_empty_row):
        """
        Args:
            model (MappingsModel): model
            row (int): table row on the list
            old_data (dict): old item data
            new_data (dict): updated item data
            is_empty_row (bool): True if the table doesn't contain any mappings
        """
        text = "rename table" if not is_empty_row else "add table"
        super().__init__(text)
        self._model = model
        self._row = row
        self._old_data = old_data
        self._new_data = new_data
        self._is_empty_row = is_empty_row

    def redo(self):
        self._model.update_table_item(self._row, self._new_data, add_empty_row=self._is_empty_row)

    def undo(self):
        self._model.update_table_item(self._row, self._old_data, remove_empty_row=self._is_empty_row)


class SetMappingPositionType(QUndoCommand):
    """Sets the type of a component mapping."""

    def __init__(self, table_row, list_row, row, model, position_type, previous_type, previous_position):
        """
        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            row (int): mapping component row index
            model (MappingsModel): model
            position_type (str): name of the new type
            previous_type (str): name of the original position type
            previous_position (str or int): original position
        """
        super().__init__("change source mapping")
        self._table_row = table_row
        self._list_row = list_row
        self._row = row
        self._model = model
        self._new_type = position_type
        self._previous_type = previous_type
        self._previous_position = previous_position

    def redo(self):
        """Changes a component mapping's type."""
        self._model.set_mapping_position_type(self._table_row, self._list_row, self._row, self._new_type)

    def undo(self):
        """Restores component mapping's original type."""
        self._model.set_mapping_position_type(self._table_row, self._list_row, self._row, self._previous_type)
        self._model.set_mapping_position(
            self._table_row, self._list_row, self._row, self._previous_type, self._previous_position
        )


class SetMappingPosition(QUndoCommand):
    """Sets the reference for a component mapping."""

    def __init__(self, table_row, list_row, row, model, new_type, new_position, previous_type, previous_position):
        """
        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            row (int): mapping component row index
            model (MappingsModel): model
            new_type (str): new position type
            new_position (str or int): new value for the position
            previous_type (str): original position type
            previous_position (str or int): position's original value
        """
        super().__init__("change source mapping reference")
        self._table_row = table_row
        self._list_row = list_row
        self._row = row
        self._model = model
        self._new_type = new_type
        self._new_position = new_position
        self._previous_type = previous_type
        self._previous_position = previous_position

    def redo(self):
        """Sets the reference's value."""
        self._model.set_mapping_position(self._table_row, self._list_row, self._row, self._new_type, self._new_position)

    def undo(self):
        """Restores the reference's value and, if necessary, mapping type to their original values."""
        if self._previous_type == "None":
            self._model.set_mapping_position_type(self._table_row, self._list_row, self._row, "None")
        else:
            self._model.set_mapping_position(
                self._table_row, self._list_row, self._row, self._previous_type, self._previous_position
            )


class SetFilterRe(QUndoCommand):
    """Sets mapping component's filter regular expression."""

    def __init__(self, table_row, list_row, row, model, new_re, previous_re):
        """
        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            row (int): mapping component row index
            model (MappingsModel): model
            new_re (str): new filter regexp
            previous_re (str): previous filter regexp
        """
        super().__init__("change source mapping reference")
        self._table_row = table_row
        self._list_row = list_row
        self._row = row
        self._model = model
        self._re = new_re
        self._previous_re = previous_re

    def redo(self):
        self._model.set_filter_re(self._table_row, self._list_row, self._row, self._re)

    def undo(self):
        self._model.set_filter_re(self._table_row, self._list_row, self._row, self._previous_re)


class SetConnectorOption(QUndoCommand):
    """Command to set a :class:`ConnectorManager` option."""

    def __init__(self, source_table, option_key, options_widget, value, previous_value):
        """
        Args:
            source_table (str): source table name
            option_key (str): option's key
            options_widget (OptionsWidget): connector options widget
            value (str or int or bool): option's new value
            previous_value (str or int or bool): option's previous value
        """
        text = f"change {option_key}"
        super().__init__(text)
        self._source_table = source_table
        self._option_key = option_key
        self._options_widget = options_widget
        self._value = value
        self._previous_value = previous_value

    def id(self):
        """
        This command's id.

        Returns:
            int: id
        """
        return _Id.SET_OPTION

    def mergeWith(self, command):
        """
        Merges command with another :class:`SetConnectorOption`.

        Args:
            command (QUndoCommand): a command to merge with

        Returns:
            bool: True if merge was successful, False otherwise
        """
        if not isinstance(command, SetConnectorOption):
            return False
        return command._option_key == self._option_key and command._value == self._value

    def redo(self):
        """Changes the connector's option."""
        self._options_widget.set_option_without_undo(self._source_table, self._option_key, self._value)

    def undo(self):
        """Restores the option back to its original value."""
        self._options_widget.set_option_without_undo(self._source_table, self._option_key, self._previous_value)


class CreateMapping(QUndoCommand):
    """Creates a new mapping."""

    def __init__(self, table_row, model, list_row):
        """
        Args:
            table_row (int): source table row index
            model (MappingsModel): model
            list_row (int): mapping list row where the new mapping should be created
        """
        super().__init__("new mapping")
        self._table_row = table_row
        self._model = model
        self._list_row = list_row

    def redo(self):
        """Creates a new mapping at the given row in mappings list."""
        table_index = self._model.index(self._table_row, 0)
        self._model.insertRow(self._list_row, table_index)

    def undo(self):
        """Deletes the created mapping."""
        table_index = self._model.index(self._table_row, 0)
        self._model.removeRow(self._list_row, table_index)


class RenameMapping(QUndoCommand):
    """Renames a mapping."""

    def __init__(self, table_row, row, model, name, previous_name):
        """
        Args:
            table_row (int): source table row
            row (int): mapping list row
            model (MappingsModel): model
            name (str): new name
            previous_name (str): previous name
        """
        super().__init__("new mapping")
        self._table_row = table_row
        self._row = row
        self._model = model
        self._name = name
        self._previous_name = previous_name

    def redo(self):
        self._model.rename_mapping(self._table_row, self._row, self._name)

    def undo(self):
        self._model.rename_mapping(self._table_row, self._row, self._previous_name)


class DuplicateMapping(QUndoCommand):
    """Duplicates an existing mapping."""

    def __init__(self, table_row, model, list_row):
        """
        Args:
            table_row (int): source table row index
            model (MappingsModel): model
            list_row (int): mapping list row where the new mapping should be created
        """
        super().__init__("duplicate mapping")
        self._table_row = table_row
        self._model = model
        self._list_row = list_row

    def redo(self):
        """Duplicates a mapping below the original one in mapping list."""
        table_index = self._model.index(self._table_row, 0)
        list_index = self._model.index(self._list_row, 0, table_index)
        root_mapping = list_index.data(Role.FLATTENED_MAPPINGS).root_mapping
        mapping_dict = [m.to_dict() for m in root_mapping.flatten()]
        self._model.insertRow(self._list_row + 1, table_index)
        self._model.set_root_mapping(self._table_row, self._list_row + 1, import_mapping_from_dict(mapping_dict))

    def undo(self):
        """Deletes the duplicated mapping."""
        table_index = self._model.index(self._table_row, 0)
        self._model.removeRow(self._list_row + 1, table_index)


class DeleteMapping(QUndoCommand):
    """Command to delete a mapping."""

    def __init__(self, table_row, model, list_row):
        """
        Args:
            table_row (int): source table row index
            model (MappingsModel): model
            list_row (int): mapping list row which should be deleted
        """
        super().__init__("delete mapping")
        self._table_row = table_row
        self._model = model
        self._list_row = list_row
        table_index = self._model.index(table_row, 0)
        list_index = self._model.index(list_row, 0, table_index)
        root_mapping = list_index.data(Role.FLATTENED_MAPPINGS).root_mapping
        self._mapping_dict = [m.to_dict() for m in root_mapping.flatten()]

    def redo(self):
        """Deletes the mapping."""
        self._model.removeRow(self._list_row, self._model.index(self._table_row, 0))

    def undo(self):
        """Restores the deleted mapping."""
        self._model.insertRow(self._list_row, self._model.index(self._table_row, 0))
        self._model.set_root_mapping(self._table_row, self._list_row, import_mapping_from_dict(self._mapping_dict))


class SetItemMappingType(QUndoCommand):
    """Command to change item mapping's type."""

    def __init__(self, table_row, list_row, model, new_type, previous_mapping):
        """
        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            model (MappingsModel): model
            new_type (str): name of the new mapping type
            previous_mapping (ImportMapping): the previous root mapping
        """
        super().__init__("mapping type change")
        self._table_row = table_row
        self._list_row = list_row
        self._model = model
        self._new_type = new_type
        self._previous_mapping_dict = [m.to_dict() for m in previous_mapping.flatten()]

    def redo(self):
        """Sets the mapping type to its new value."""
        self._model.set_mappings_type(self._table_row, self._list_row, self._new_type)

    def undo(self):
        """Resets the mapping."""
        self._model.set_root_mapping(
            self._table_row, self._list_row, import_mapping_from_dict(self._previous_mapping_dict)
        )


class SetImportEntitiesFlag(QUndoCommand):
    """Command to set item mapping's import objects flag."""

    def __init__(self, table_row, list_row, model, import_entities):
        """
        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            model (MappingsModel): model
            import_entities (bool): new flag value
        """
        super().__init__("import objects flag change")
        self._table_row = table_row
        self._list_row = list_row
        self._model = model
        self._import_entities = import_entities

    def redo(self):
        """Changes the import objects flag."""
        self._model.set_import_entities(self._table_row, self._list_row, self._import_entities)

    def undo(self):
        """Restores the import objects flag."""
        self._model.set_import_entities(self._table_row, self._list_row, not self._import_entities)


class SetParameterType(QUndoCommand):
    """Command to change the parameter type of an item mapping."""

    def __init__(self, table_row, list_row, model, new_type, previous_mapping):
        """
        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            model (MappingsModel): model
            new_type (str): name of the new parameter type
            previous_mapping (ImportMapping): previous mapping root
        """
        super().__init__("parameter type change")
        self._table_row = table_row
        self._list_row = list_row
        self._model = model
        self._new_type = new_type
        self._previous_mapping_dict = [m.to_dict() for m in previous_mapping.flatten()]

    def redo(self):
        """Changes a parameter's type."""
        self._model.set_parameter_type(self._table_row, self._list_row, self._new_type)

    def undo(self):
        """Restores a parameter to its previous type"""
        self._model.set_root_mapping(
            self._table_row, self._list_row, import_mapping_from_dict(self._previous_mapping_dict)
        )


class SetValueType(QUndoCommand):
    """Command to change the value type of an item mapping."""

    def __init__(self, table_row, list_row, model, new_type, old_type):
        """
        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            model (MappingsModel): model
            new_type (str): name of the new value type
            old_type (str): name of the old value type
        """
        super().__init__("value type change")
        self._table_row = table_row
        self._list_row = list_row
        self._model = model
        self._new_type = new_type
        self._old_type = old_type

    def redo(self):
        """Changes a parameter's value type."""
        self._model.set_value_type(self._table_row, self._list_row, self._new_type)

    def undo(self):
        """Restores a parameter to its previous value type"""
        self._model.set_value_type(self._table_row, self._list_row, self._old_type)


class SetUseBeforeAlternativeFlag(QUndoCommand):
    """Command to set item mapping's use before alternative flag."""

    def __init__(self, table_row, list_row, model, use_before_alternative, previous_mapping):
        """
        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            model (MappingsModel): model
            use_before_alternative (bool): new flag value
            previous_mapping (ImportMapping): previous mapping root
        """
        text = ("enable" if use_before_alternative else "disable") + " before alternative"
        super().__init__(text)
        self._table_row = table_row
        self._list_row = list_row
        self._model = model
        self._use_before_alternative = use_before_alternative
        self._previous_mapping_dict = [m.to_dict() for m in previous_mapping.flatten()]

    def redo(self):
        """Changes the use before alternative flag."""
        self._model.set_use_before_alternative(self._table_row, self._list_row, self._use_before_alternative)

    def undo(self):
        """Restores the use before alternative flag."""
        self._model.set_root_mapping(
            self._table_row, self._list_row, import_mapping_from_dict(self._previous_mapping_dict)
        )


class SetSkipColumns(QUndoCommand):
    """Command to change item mapping's skip columns option."""

    def __init__(self, table_row, list_row, model, skip_cols, previous_skip_cols):
        """
        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            model (MappingsModel): model
            skip_cols (list): new skip columns
            previous_skip_cols (list): previous skip columns
        """
        super().__init__("mapping ignore columns change")
        self._table_row = table_row
        self._list_row = list_row
        self._model = model
        self._skip_cols = skip_cols
        self._previous_skip_cols = previous_skip_cols

    def redo(self):
        """Changes item mapping's skip columns to a new value."""
        self._model.set_skip_columns(self._table_row, self._list_row, self._skip_cols)

    def undo(self):
        """Restores item mapping's skip columns to its previous value."""
        self._model.set_skip_columns(self._table_row, self._list_row, self._previous_skip_cols)


class SetReadStartRow(QUndoCommand):
    """Command to change item mapping's read start row option."""

    def __init__(self, table_row, list_row, model, start_row, previous_start_row):
        """
        Args:
            table_row (int): table row index
            list_row (int): list row index
            model (MappingsModel): model
            start_row (int): new read start row
            previous_start_row (int): previous read start row value
        """
        super().__init__("mapping read start row change")
        self._table_row = table_row
        self._list_row = list_row
        self._model = model
        self._start_row = start_row
        self._previous_start_row = previous_start_row

    def redo(self):
        """Changes item mapping's read start row to a new value."""
        self._model.set_read_start_row(self._table_row, self._list_row, self._start_row)

    def undo(self):
        """Restores item mapping's read start row to its previous value."""
        self._model.set_read_start_row(self._table_row, self._list_row, self._previous_start_row)


class SetItemMappingDimensionCount(QUndoCommand):
    """Command to change item mapping's dimension option."""

    def __init__(self, table_row, list_row, model, dimension_count, previous_mapping_root):
        """
        Args:
            table_row (int): table row index
            list_row (int): list row index
            model (MappingsModel): model
            dimension_count (int): new dimension count
            previous_mapping_root (ImportMapping): previous mapping root
        """
        super().__init__("mapping dimension count change")
        self._table_row = table_row
        self._list_row = list_row
        self._model = model
        self._dimension_count = dimension_count
        self._previous_mapping_dict = [m.to_dict() for m in previous_mapping_root.flatten()]

    def redo(self):
        """Changes the item mapping's dimension to the new value."""
        self._model.set_relationship_dimension_count(self._table_row, self._list_row, self._dimension_count)

    def undo(self):
        """Changes the item mapping's dimension to its previous value."""
        self._model.set_root_mapping(
            self._table_row, self._list_row, import_mapping_from_dict(self._previous_mapping_dict)
        )


class SetTimeSeriesRepeatFlag(QUndoCommand):
    """Command to change the repeat flag for time series."""

    def __init__(self, table_row, list_row, model, repeat):
        """
        Args:
            table_row (int): table row index
            list_row (int): list row index
            model (MappingsModel): model
            repeat (bool): new repeat flag value
        """
        super().__init__("change time series repeat flag")
        self._table_row = table_row
        self._list_row = list_row
        self._model = model
        self._repeat = repeat

    def redo(self):
        """Sets the repeat flag to given value."""
        self._model.set_time_series_repeat_flag(self._table_row, self._list_row, self._repeat)

    def undo(self):
        """Restores the repeat flag to its previous value."""
        self._model.set_time_series_repeat_flag(self._table_row, self._list_row, not self._repeat)


class SetMapDimensionCount(QUndoCommand):
    """Command to change the dimension_count of a Map parameter value type."""

    def __init__(self, table_row, list_row, model, dimension_count, previous_mapping_root):
        """
        Args:
            table_row (int): table row index
            list_row (int): list row index
            model (MappingsModel): model
            dimension_count (int): new dimension_count
            previous_mapping_root (ImportMapping): previous mapping root
        """
        super().__init__("map dimension count change")
        self._table_row = table_row
        self._list_row = list_row
        self._model = model
        self._dimension_count = dimension_count
        self._previous_mapping_root = [m.to_dict() for m in previous_mapping_root.flatten()]

    def redo(self):
        """Sets the Map dimension count to the new value."""
        self._model.set_map_dimension_count(self._table_row, self._list_row, self._dimension_count)

    def undo(self):
        """Restores the previous Map dimension count value."""
        self._model.set_root_mapping(
            self._table_row, self._list_row, import_mapping_from_dict(self._previous_mapping_root)
        )


class SetMapCompressFlag(QUndoCommand):
    """Command to change the Map compress flag."""

    def __init__(self, table_row, list_row, model, compress):
        """
        Args:
            table_row (int): table row index
            list_row (int): list row index
            model (MappingsModel): model
            compress (bool): compress flag value
        """
        text = ("enable" if compress else "disable") + " Map compression"
        super().__init__(text)
        self._table_row = table_row
        self._list_row = list_row
        self._model = model
        self._compress = compress

    def redo(self):
        """Sets the compress flag."""
        self._model.set_map_compress(self._table_row, self._list_row, self._compress)

    def undo(self):
        """Resets the compress flag to previous value."""
        self._model.set_map_compress(self._table_row, self._list_row, not self._compress)


class SetColumnOrRowType(QUndoCommand):
    """Command to change the type of columns or rows."""

    def __init__(self, source_table_name, header_widget, sections, new_type, previous_type):
        """
        Args:
            source_table_name (str): name of the source table
            header_widget (HeaderWithButton): widget of origin
            sections (Iterable of int): row or column indexes
            new_type (ConvertSpec): conversion specification for the rows/columns
            previous_type (ConvertSpec): previous conversion specification for the rows/columns
        """
        text = ("row" if header_widget.orientation() == Qt.Orientation.Vertical else "column") + " type change"
        super().__init__(text)
        self._source_table_name = source_table_name
        self._header_widget = header_widget
        self._sections = sections
        self._new_type = new_type
        self._previous_type = previous_type

    def redo(self):
        """Sets column/row type."""
        self._header_widget.set_data_types(self._source_table_name, self._sections, self._new_type)

    def undo(self):
        """Restores column/row type to its previous value."""
        self._header_widget.set_data_types(self._source_table_name, self._sections, self._previous_type)


class SetColumnDefaultType(QUndoCommand):
    """Command to change the default type of columns."""

    def __init__(self, import_sources, source_table_name, new_type, previous_type):
        """
        Args:
            import_sources (ImportSources): import sources manager
            source_table_name (str): name of the source table
            new_type (str): new column type
            previous_type (str): previous column type
        """
        super().__init__("surplus column type")
        self._import_sources = import_sources
        self._table_name = source_table_name
        self._new_type = new_type
        self._previous_type = previous_type

    def redo(self):
        self._import_sources.change_default_column_type(self._table_name, self._new_type)

    def undo(self):
        self._import_sources.change_default_column_type(self._table_name, self._previous_type)


class RestoreMappingsFromDict(QUndoCommand):
    """Restores mappings from a dict."""

    def __init__(self, import_sources, model, mapping_dict):
        """
        Args:
            import_sources (ImportSources): import sources manager
            model (MappingsModel): model
            mapping_dict (dict): mappings to restore
        """
        super().__init__("import mappings")
        self._import_sources = import_sources
        self._model = model
        self._mapping_dict = mapping_dict
        self._previous_mapping_dict = self._import_sources.store_connectors()
        self._previous_mapping_dict.update(self._model.store())

    def redo(self):
        """Restores the mappings."""
        self._model.restore(self._mapping_dict)
        self._import_sources.restore_connectors(self._mapping_dict)

    def undo(self):
        """Reverts back to previous mappings."""
        self._model.restore(self._previous_mapping_dict)
        self._import_sources.restore_connectors(self._mapping_dict)
