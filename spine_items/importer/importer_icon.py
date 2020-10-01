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
Module for Importer icon class.

:authors: M. Marin (KTH), P. Savolainen (VTT)
:date:   4.4.2018
"""

from PySide2.QtGui import QColor
from spine_items.graphics_items import ProjectItemIcon
from ..animations import ImporterAnimation


class ImporterIcon(ProjectItemIcon):
    def __init__(self, toolbox, icon):
        """Importer icon for the Design View.

        Args:
            toolbox (ToolBoxUI): QMainWindow instance
            icon (str): icon resource path
        """
        super().__init__(toolbox, icon, icon_color=QColor("#990000"), background_color=QColor("#ffcccc"))
        self.animation = ImporterAnimation(self, x_shift=4)
        self.start_animation = self.animation.start
        self.stop_animation = self.animation.stop
