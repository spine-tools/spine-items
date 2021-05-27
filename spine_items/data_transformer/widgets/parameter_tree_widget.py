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
Contains :class:`ParameterTreeWidget`.

:author: A. Soininen (VTT)
:date:   25.5.2021
"""
import pickle
from PySide2.QtCore import QMimeData
from PySide2.QtWidgets import QTreeWidget


class ParameterTreeWidget(QTreeWidget):
    """A tree widget with drag capabilities to show entity classes and parameters."""

    MIME_TYPE = "application/spine-parameters"
    """Mime type for drag and drop actions."""

    def mimeData(self, items):
        mime_data = QMimeData()
        parameters = dict()
        for item in items:
            if item.parent() is None:
                for i in range(item.childCount()):
                    parameters.setdefault(item.text(0), []).append(item.child(i).text(0))
            else:
                parameters.setdefault(item.parent().text(0), []).append(item.text(0))
        mime_data.setData("application/spine-parameters", pickle.dumps(parameters))
        return mime_data
