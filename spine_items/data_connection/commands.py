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

"""Undo/redo commands for the DataConnection project item."""
from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING
from spine_items.commands import SpineToolboxCommand
from spine_items.utils import UrlDict
from spinetoolbox.project import SpineToolboxProject

if TYPE_CHECKING:
    from spine_items.data_connection.data_connection import DataConnection


class AddDCReferencesCommand(SpineToolboxCommand):
    """Command to add DC references."""

    def __init__(
        self,
        dc_name: str,
        file_refs: list[str],
        directory_refs: list[str],
        db_refs: list[UrlDict],
        project: SpineToolboxProject,
    ):
        """
        Args:
            dc_name: DC name
            file_refs: list of file refs to add
            directory_refs: list of directory refs to add
            db_refs: list of db refs to add
            project: project
        """
        super().__init__()
        self._dc_name = dc_name
        self._file_refs = file_refs
        self._directory_refs = directory_refs
        self._db_refs = db_refs
        self._project = project
        self.setText(f"add references to {dc_name}")

    def redo(self):
        dc: DataConnection = self._project.get_item(self._dc_name)
        dc.do_add_references(self._file_refs, self._directory_refs, self._db_refs)

    def undo(self):
        dc: DataConnection = self._project.get_item(self._dc_name)
        dc.do_remove_references(self._file_refs, self._directory_refs, self._db_refs)


class UpdateFileReference(SpineToolboxCommand):
    def __init__(self, dc_name: str, old_file_ref: str, new_file_ref: str, project: SpineToolboxProject):
        super().__init__()
        self._dc_name = dc_name
        self._new_file_ref = new_file_ref
        self._old_file_ref = old_file_ref
        self._project = project
        self.setText(f"update file reference in {dc_name}")

    def redo(self):
        dc: DataConnection = self._project.get_item(self._dc_name)
        dc.do_update_file_reference(self._old_file_ref, self._new_file_ref)

    def undo(self):
        dc: DataConnection = self._project.get_item(self._dc_name)
        dc.do_update_file_reference(self._new_file_ref, self._old_file_ref)


class UpdateDirectoryReference(SpineToolboxCommand):
    def __init__(self, dc_name: str, old_ref: str, new_ref: str, project: SpineToolboxProject):
        super().__init__()
        self._dc_name = dc_name
        self._new_directory_ref = new_ref
        self._old_directory_ref = old_ref
        self._project = project
        self.setText(f"update directory reference in {dc_name}")

    def redo(self):
        dc: DataConnection = self._project.get_item(self._dc_name)
        dc.do_update_directory_reference(self._old_directory_ref, self._new_directory_ref)

    def undo(self):
        dc: DataConnection = self._project.get_item(self._dc_name)
        dc.do_update_directory_reference(self._new_directory_ref, self._old_directory_ref)


class UpdateDbUrlReference(SpineToolboxCommand):
    def __init__(self, dc_name: str, old_ref: UrlDict, new_ref: UrlDict, project: SpineToolboxProject):
        super().__init__()
        self._dc_name = dc_name
        self._new_ref = new_ref
        self._old_ref = old_ref
        self._project = project
        self.setText(f"update URL reference in {dc_name}")

    def redo(self):
        dc: DataConnection = self._project.get_item(self._dc_name)
        dc.do_update_db_url_reference(self._old_ref, self._new_ref)

    def undo(self):
        dc: DataConnection = self._project.get_item(self._dc_name)
        dc.do_update_db_url_reference(self._new_ref, self._old_ref)


class RemoveDCReferencesCommand(SpineToolboxCommand):
    """Command to remove DC references."""

    def __init__(
        self,
        dc_name: str,
        file_refs: list[str],
        directory_refs: list[str],
        db_refs: list[UrlDict],
        project: SpineToolboxProject,
    ):
        """
        Args:
            dc_name: DC name
            file_refs: list of file refs to remove
            directory_refs: list of directory refs to remove
            db_refs: list of db refs to remove
            project: project
        """
        super().__init__()
        self._dc_name = dc_name
        self._file_refs = file_refs
        self._directory_refs = directory_refs
        self._db_refs = db_refs
        self._project = project
        self.setText(f"remove references from {dc_name}")

    def redo(self):
        dc: DataConnection = self._project.get_item(self._dc_name)
        dc.do_remove_references(self._file_refs, self._directory_refs, self._db_refs)

    def undo(self):
        dc: DataConnection = self._project.get_item(self._dc_name)
        dc.do_add_references(self._file_refs, self._directory_refs, self._db_refs)


class MoveReferenceToData(SpineToolboxCommand):
    """Command to move DC references to data."""

    def __init__(self, dc_name: str, paths: list[str], project: SpineToolboxProject):
        """
        Args:
            dc_name: DC name
            paths: list of paths to move
            project: project
        """
        super().__init__()
        self._dc_name = dc_name
        self._paths = paths
        self._project = project
        self.setText(f"copy references to data in {dc_name}")

    def redo(self):
        dc: DataConnection = self._project.get_item(self._dc_name)
        dc.do_copy_to_project(self._paths)
        dc.do_remove_references(self._paths, [], [])

    def undo(self):
        dc: DataConnection = self._project.get_item(self._dc_name)
        dc.delete_files_from_project([Path(p).name for p in self._paths])
        dc.do_add_references(self._paths, [], [])
