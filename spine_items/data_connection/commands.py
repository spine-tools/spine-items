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
Undo/redo commands for the DataConnection project item.

"""
from pathlib import Path
from spine_items.commands import SpineToolboxCommand


class AddDCReferencesCommand(SpineToolboxCommand):
    """Command to add DC references."""

    def __init__(self, dc, file_refs, db_refs):
        """
        Args:
            dc (DataConnection): the DC
            file_refs (list of str): list of file refs to add
            db_refs (list of str): list of db refs to add
        """
        super().__init__()
        self.dc = dc
        self.file_refs = file_refs
        self.db_refs = db_refs
        self.setText(f"add references to {dc.name}")

    def redo(self):
        self.dc.do_add_references(self.file_refs, self.db_refs)

    def undo(self):
        self.dc.do_remove_references(self.file_refs, self.db_refs)


class RemoveDCReferencesCommand(SpineToolboxCommand):
    """Command to remove DC references."""

    def __init__(self, dc, file_refs, db_refs):
        """
        Args:
            dc (DataConnection): the DC
            file_refs (list of str): list of file refs to remove
            db_refs (list of str): list of db refs to remove
        """
        super().__init__()
        self.dc = dc
        self.file_refs = file_refs
        self.db_refs = db_refs
        self.setText(f"remove references from {dc.name}")

    def redo(self):
        self.dc.do_remove_references(self.file_refs, self.db_refs)

    def undo(self):
        self.dc.do_add_references(self.file_refs, self.db_refs)


class MoveReferenceToData(SpineToolboxCommand):
    """Command to move DC references to data."""

    def __init__(self, dc, paths):
        """
        Args:
            dc (DataConnection): the DC
            paths (list of str): list of paths to move
        """
        super().__init__()
        self._dc = dc
        self._paths = paths
        self.setText("copy references to data")

    def redo(self):
        self._dc.do_copy_to_project(self._paths)
        self._dc.do_remove_references(self._paths, [])

    def undo(self):
        self._dc.delete_files_from_project([Path(p).name for p in self._paths])
        self._dc.do_add_references(self._paths, [])
