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

"""Module for tool icon class."""
from PySide6.QtCore import QTimeLine, Slot, QPointF
from spinetoolbox.project_item_icon import ProjectItemIcon
from ..animations import AnimationSignaller


class ToolIcon(ProjectItemIcon):
    def __init__(self, toolbox, icon, icon_color):
        """Tool icon for the Design View.

        Args:
            toolbox (ToolBoxUI): QMainWindow instance
            icon (str): icon resource path
            icon_color (QColor): Icon's color
        """
        super().__init__(toolbox, icon, icon_color)
        self.time_line = QTimeLine()
        self.time_line.setLoopCount(0)  # loop forever
        self.time_line.setFrameRange(0, 10)
        self.time_line.setDuration(1200)
        self.time_line.setDirection(QTimeLine.Direction.Backward)
        self.time_line.valueChanged.connect(self._handle_time_line_value_changed)
        self.time_line.stateChanged.connect(self._handle_time_line_state_changed)
        self._svg_item_pos = self.svg_item.pos()
        rect = self.svg_item.sceneBoundingRect()
        self._anim_transformation_origin_point_y = -0.75 * rect.height()
        self._anim_delta_x_factor = 0.5 * rect.width()
        self.animation_signaller = AnimationSignaller()
        self.animation_signaller.animation_started.connect(self.start_animation)
        self.animation_signaller.animation_stopped.connect(self.stop_animation)

    @Slot(float)
    def _handle_time_line_value_changed(self, value):
        angle = value * 45.0
        self.svg_item.setRotation(angle)
        delta_y = 0.5 * self.svg_item.sceneBoundingRect().height()
        delta = QPointF(self._anim_delta_x_factor * value, delta_y)
        self.svg_item.setPos(self._svg_item_pos + delta)

    @Slot(int)
    def _handle_time_line_state_changed(self, new_state):
        if new_state == QTimeLine.State.Running:
            self.svg_item.setTransformOriginPoint(0, self._anim_transformation_origin_point_y)
        elif new_state == QTimeLine.State.NotRunning:
            self.svg_item.setTransformOriginPoint(0, 0)
            self.svg_item.setPos(self._svg_item_pos)
            self.svg_item.setRotation(0)

    @Slot()
    def start_animation(self):
        """Starts the item execution animation."""
        if self.time_line.state() == QTimeLine.State.Running:
            return
        self.time_line.start()

    @Slot()
    def stop_animation(self):
        """Stop animation"""
        if self.time_line.state() != QTimeLine.State.Running:
            return
        self.time_line.stop()

    def mouseDoubleClickEvent(self, e):
        """Opens Tool Specification editor when this Tool icon is double-clicked.

        Args:
            e (QGraphicsSceneMouseEvent): Event
        """
        super().mouseDoubleClickEvent(e)
        item = self._toolbox.project().get_item(self._name)
        item.show_specification_window()
