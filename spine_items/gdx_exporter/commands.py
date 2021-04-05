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
Undo/redo commands for the GdxExporter project item.

:authors: A. Soininen (VTT)
:date:   30.4.2020
"""
from spine_items.commands import SpineToolboxCommand


class UpdateSettings(SpineToolboxCommand):
    """Command to update GdxExporter settings."""

    def __init__(self, exporter, settings, indexing_settings, merging_settings, none_fallback, none_export):
        """
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
