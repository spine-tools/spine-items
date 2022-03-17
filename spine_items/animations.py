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
Animation class for importers and exporters.

:authors: M. Marin (KTH)
:date:   12.11.2019
"""

import random
from PySide2.QtGui import QFont, QPainterPath
from PySide2.QtCore import Signal, Slot, QObject, QTimeLine, QPointF, Qt
from PySide2.QtWidgets import QGraphicsTextItem


class AnimationSignaller(QObject):

    animation_started = Signal()
    animation_stopped = Signal()


class ImporterExporterAnimation:
    def __init__(self, item, duration=2000, count=8, percentage_size=0.2):
        """Initializes animation stuff.

        Args:
            item (QGraphicsItem): The item on top of which the animation should play.
        """
        self._item = item
        self.cubes = [QGraphicsTextItem("\uf1b2", item) for i in range(count)]
        self.opacity_at_value_path = QPainterPath(QPointF(0.0, 0.0))
        self.opacity_at_value_path.lineTo(QPointF(0.25, 0.0))
        self.opacity_at_value_path.lineTo(QPointF(0.5, 0.0))
        self.opacity_at_value_path.lineTo(QPointF(1.0, 0.0))
        self.time_line = QTimeLine()
        self.time_line.setLoopCount(0)  # loop forever
        self.time_line.setFrameRange(0, 10)
        self.time_line.setDuration(duration)
        self.time_line.setCurveShape(QTimeLine.LinearCurve)
        self.time_line.valueChanged.connect(self._handle_time_line_value_changed)
        self.time_line.stateChanged.connect(self._handle_time_line_state_changed)
        font = QFont("Font Awesome 5 Free Solid")
        item_rect = item.rect()
        cube_size = percentage_size * item_rect.height()
        font.setPixelSize(cube_size)
        self.path = QPainterPath()
        orbit_rect = item_rect.adjusted(0, 0, -1.5 * cube_size, 0)
        orbit_rect.setHeight(cube_size)
        orbit_rect.moveTop(item_rect.center().y() - cube_size)
        self.path.addEllipse(orbit_rect)
        self.x_offsets = [i / count for i in range(count)]
        self.y_offsets = [0.5 * cube_size * i / count for i in range(-count, count)]
        for cube in self.cubes:
            cube.setFont(font)
            cube.setAcceptedMouseButtons(Qt.NoButton)
            cube.setDefaultTextColor("#003333")
            cube.setTransformOriginPoint(cube.boundingRect().center())
            cube.hide()

    @staticmethod
    def _opacity(percent):
        if percent < 0.25:
            return 0.75 + 3 * percent
        if percent < 0.5:
            return 1.5 - 3 * (percent - 0.25)
        if percent < 0.75:
            return 0.75 - 3 * (percent - 0.5)
        return 3 * (percent - 0.75)

    @Slot(float)
    def _handle_time_line_value_changed(self, value):
        for cube, x_offset, y_offset in zip(self.cubes, self.x_offsets, self.y_offsets):
            value = (x_offset + value) % 1.0
            percent = self.percent(value)
            opacity = self._opacity(percent)
            cube.setOpacity(opacity)
            point = self.path.pointAtPercent(percent)
            point += QPointF(0, y_offset)
            angle = -percent * 360.0
            cube.setPos(point)
            cube.setRotation(angle)

    @Slot(QTimeLine.State)
    def _handle_time_line_state_changed(self, new_state):
        if new_state == QTimeLine.Running:
            random.shuffle(self.y_offsets)
            for cube in self.cubes:
                cube.show()
        elif new_state == QTimeLine.NotRunning:
            for cube in self.cubes:
                cube.hide()

    @Slot()
    def start(self):
        """Starts the animation."""
        if self.time_line.state() == QTimeLine.Running:
            return
        self.time_line.start()

    @staticmethod
    def percent(value):
        raise NotImplementedError()

    @Slot()
    def stop(self):
        """Stops the animation"""
        self.time_line.stop()


class ImporterAnimation(ImporterExporterAnimation):
    @staticmethod
    def percent(value):
        return value


class ExporterAnimation(ImporterExporterAnimation):
    @staticmethod
    def percent(value):
        return 1 - value
