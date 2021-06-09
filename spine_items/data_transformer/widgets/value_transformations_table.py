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
Contains value transforms table widget.

:author: A. Soininen (VTT)
:date:   25.5.2021
"""
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QTableView
from ..widgets.parameter_tree_widget import ParameterTreeWidget


class ValueTransformationsTable(QTableView):
    def dragEnterEvent(self, event):
        super().dragEnterEvent(event)
        if event.mimeData().hasFormat(ParameterTreeWidget.MIME_TYPE):
            event.setDropAction(Qt.CopyAction)
            event.acceptProposedAction()