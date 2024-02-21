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

"""Module for MergerIcon class."""
import random
from PySide6.QtCore import QTimeLine, QPointF, Slot
from spinetoolbox.project_item_icon import ProjectItemIcon
from ..animations import AnimationSignaller


class MergerIcon(ProjectItemIcon):
    _SHAKE_FACTOR = 0.05

    def __init__(self, toolbox, icon, icon_color):
        """Data Store icon for the Design View.

        Args:
            toolbox (ToolBoxUI): QMainWindow instance
            icon (str): icon resource path
            icon_color (QColor): Icon's color
        """
        super().__init__(toolbox, icon, icon_color)
        self._time_line = QTimeLine()
        self._time_line.setLoopCount(0)  # loop forever
        self._time_line.setFrameRange(0, 10)
        self._time_line.setDirection(QTimeLine.Direction.Backward)
        self._time_line.valueChanged.connect(self._handle_time_line_value_changed)
        self._time_line.stateChanged.connect(self._handle_time_line_state_changed)
        self._svg_item_pos = self.svg_item.pos()
        self.animation_signaller = AnimationSignaller()
        self.animation_signaller.animation_started.connect(self.start_animation)
        self.animation_signaller.animation_stopped.connect(self.stop_animation)

    @Slot(float)
    def _handle_time_line_value_changed(self, value):
        rect = self.svg_item.sceneBoundingRect()
        width = rect.width()
        height = rect.height()
        x = random.uniform(-self._SHAKE_FACTOR, self._SHAKE_FACTOR) * width
        y = random.uniform(-self._SHAKE_FACTOR, self._SHAKE_FACTOR) * height
        self.svg_item.setPos(self._svg_item_pos + QPointF(x, y))

    @Slot(QTimeLine.State)
    def _handle_time_line_state_changed(self, new_state):
        if new_state == QTimeLine.State.NotRunning:
            self.svg_item.setPos(self._svg_item_pos)

    @Slot()
    def start_animation(self):
        """Start the animation that plays when the Merger associated to this GraphicsItem is running."""
        if self._time_line.state() == QTimeLine.State.Running:
            return
        self._time_line.start()

    @Slot()
    def stop_animation(self):
        """Stop animation"""
        if self._time_line.state() != QTimeLine.State.Running:
            return
        self._time_line.stop()
