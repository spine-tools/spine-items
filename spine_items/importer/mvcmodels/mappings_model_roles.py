######################################################################################################################
# Copyright (C) 2017-2021 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################
"""
Contains user data roles for :class:`MappingsModel`.

:author: A. Soininen (VTT)
:date:   15.10.2021
"""
from PySide2.QtCore import Qt
from enum import IntEnum, unique


@unique
class Role(IntEnum):
    ITEM = Qt.UserRole + 1
    FLATTENED_MAPPINGS = Qt.UserRole + 2
