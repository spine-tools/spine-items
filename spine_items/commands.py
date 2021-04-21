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
Undo/redo commands that can be used by multiple project items.

:authors: M. Marin (KTH), P. Savolainen (VTT)
:date:   5.5.2020
"""
from PySide2.QtWidgets import QUndoCommand
from spinetoolbox.project_commands import SpineToolboxCommand


class UpdateCancelOnErrorCommand(SpineToolboxCommand):
    def __init__(self, project_item, cancel_on_error):
        """Command to update Importer, GdxExporter, and Data Store cancel on error setting.

        Args:
            project_item (ProjectItem): Item
            cancel_on_error (bool): New setting
        """
        super().__init__()
        self._project_item = project_item
        self._redo_cancel_on_error = cancel_on_error
        self._undo_cancel_on_error = not cancel_on_error
        self.setText(f"change {project_item.name} cancel on error setting")

    def redo(self):
        self._project_item.set_cancel_on_error(self._redo_cancel_on_error)

    def undo(self):
        self._project_item.set_cancel_on_error(self._undo_cancel_on_error)


class ChangeItemSelectionCommand(SpineToolboxCommand):
    def __init__(self, item_name, model, index, selected):
        """Command to change file item's selection status.

        Args:
            item_name (str): project item's name
            model (FileListModel): File model
            index (QModelIndex): Index to file model
            selected (bool): True if the item is selected, False otherwise
        """
        super().__init__()
        self._model = model
        self._index = index
        self._selected = selected
        self.setText(f"change {item_name} file selection")

    def redo(self):
        self._model.set_checked(self._index, self._selected)

    def undo(self):
        self._model.set_checked(self._index, not self._selected)


class UpdateCmdLineArgsCommand(SpineToolboxCommand):
    def __init__(self, item, cmd_line_args):
        """Command to update Tool command line args.

        Args:
            item (ProjectItemBase): the item
            cmd_line_args (list): list of command line args
        """
        super().__init__()
        self.item = item
        self.redo_cmd_line_args = cmd_line_args
        self.undo_cmd_line_args = self.item.cmd_line_args
        self.setText(f"change command line arguments of {item.name}")

    def redo(self):
        self.item.update_cmd_line_args(self.redo_cmd_line_args)

    def undo(self):
        self.item.update_cmd_line_args(self.undo_cmd_line_args)


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


class UpdateOutFileName(SpineToolboxCommand):
    """Command to update exporter's output file name."""

    def __init__(self, exporter, file_name, database_path):
        """
        Args:
            exporter (ExporterBase): exporter
            file_name (str): the output filename
            database_path (str): the associated db path
        """
        super().__init__()
        self.exporter = exporter
        self.redo_file_name = file_name
        self.undo_file_name = self.exporter.database(database_path).output_file_name
        self.database_path = database_path
        self.setText(f"change output file in {exporter.name}")

    def redo(self):
        self.exporter.set_out_file_name(self.redo_file_name, self.database_path)

    def undo(self):
        self.exporter.set_out_file_name(self.undo_file_name, self.database_path)


class UpdateOutputTimeStampsFlag(SpineToolboxCommand):
    """Command to set exporter's output directory time stamps flag."""

    def __init__(self, exporter, value):
        """
        Args:
            exporter (ExporterBase): exporter item
            value (bool): flag's new value
        """
        super().__init__()
        self.setText(f"toggle output time stamps setting of {exporter.name}")
        self._exporter = exporter
        self._value = value

    def redo(self):
        self._exporter.set_output_time_stamps_flag(self._value)

    def undo(self):
        self._exporter.set_output_time_stamps_flag(not self._value)
