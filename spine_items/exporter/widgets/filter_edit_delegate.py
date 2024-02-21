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

"""Contains mapping filter editor delegate."""
from spinedb_api.export_mapping.export_mapping import ParameterValueTypeMapping
from spine_items.ui import default_filter_editor
from spine_items.widgets import FilterEdit, FilterEditDelegateBase
from ..mvcmodels.mapping_editor_table_model import MappingEditorTableModel
from ..ui import value_type_filter_editor


class FilterEditDelegate(FilterEditDelegateBase):
    """Edit delegate for Mapping table's filter column."""

    def createEditor(self, parent, option, index):
        mapping = index.data(MappingEditorTableModel.MAPPING_ITEM_ROLE)
        if isinstance(mapping, ParameterValueTypeMapping):
            return FilterEdit(value_type_filter_editor.Ui_Form(), parent)
        return FilterEdit(default_filter_editor.Ui_Form(), parent)
