######################################################################################################################
# Copyright (C) 2017-2020 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Undo/redo commands for the GdxExporter project item.

:authors: A. Soininen (VTT)
:date:   30.4.2020
"""
from spine_items.commands import SpineToolboxCommand


class UpdateOutFileName(SpineToolboxCommand):
    def __init__(self, exporter, file_name, database_path):
        """Command to update GdxExporter output file name.

        Args:
            exporter (GdxExporter): the GdxExporter
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
        self.exporter.undo_redo_out_file_name(self.redo_file_name, self.database_path)

    def undo(self):
        self.exporter.undo_redo_out_file_name(self.undo_file_name, self.database_path)


class UpdateSettings(SpineToolboxCommand):
    def __init__(self, exporter, settings, indexing_settings, merging_settings, none_fallback, none_export):
        """Command to update GdxExporter settings.

        Args:
            exporter (GdxExporter): the GdxExporter
            settings (SetSettings): gdx settings
            indexing_settings (dict): parameter indexing settings
            merging_settings (dict): parameter merging settings
            none_fallback (NoneFallback): fallback option on None values
            none_export (NoneExport): how to handle Nones while exporting
        """
        super().__init__()
        self._exporter = exporter
        self._redo_settings_tuple = (settings, indexing_settings, merging_settings, none_fallback, none_export)
        p = exporter.settings_pack()
        self._undo_settings_tuple = (p.settings, p.indexing_settings, p.merging_settings)
        self.setText(f"change settings of {exporter.name}")

    def redo(self):
        self._exporter.undo_or_redo_settings(*self._redo_settings_tuple)

    def undo(self):
        self._exporter.undo_or_redo_settings(*self._undo_settings_tuple)
