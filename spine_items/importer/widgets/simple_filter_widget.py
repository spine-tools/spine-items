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
Contains a simple filter widget for skip column filtering in mapping options.

:author: A. Soininen (VTT)
:date:   20.10.2021
"""
from spinetoolbox.mvcmodels.filter_checkbox_list_model import DataToValueFilterCheckboxListModel
from spinetoolbox.widgets.custom_qwidgets import FilterWidgetBase


class SimpleFilterWidget(FilterWidgetBase):
    def __init__(self, parent, show_empty=True):
        """
        Args:
            parent (QWidget): parent widget
        """
        super().__init__(parent)
        self._filter_model = DataToValueFilterCheckboxListModel(self, str, show_empty=show_empty)
        self._filter_model.set_list(self._filter_state)
        self._ui_list.setModel(self._filter_model)
        self.connect_signals()
