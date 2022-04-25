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

import math
from PySide2.QtGui import QPainterPath, QFont, QColor
from PySide2.QtCore import Qt, Signal, Slot, QObject, QTimeLine, QRectF
from PySide2.QtWidgets import QGraphicsTextItem


class AnimationSignaller(QObject):

    animation_started = Signal()
    animation_stopped = Signal()


class ImporterExporterAnimation:
    def __init__(self, item, duration=3000, cube_density=5, point_size=8, loop_extent=15):
        """Initializes animation stuff.

        Args:
            item (QGraphicsItem): The item on top of which the animation should play.
        """
        self._item = item
        self._cubes = []
        self._step = 100 / duration
        self._cube_density = cube_density
        self._loop_extent = loop_extent
        self._font = QFont("Font Awesome 5 Free Solid")
        self._font.setPointSize(point_size)
        self.time_line = QTimeLine()
        self.time_line.setLoopCount(0)  # loop forever
        self.time_line.valueChanged.connect(self._handle_time_line_value_changed)
        self.time_line.stateChanged.connect(self._handle_time_line_state_changed)

    @Slot(float)
    def _handle_time_line_value_changed(self, value):
        for cube in self._cubes:
            cube.advance()

    @Slot(QTimeLine.State)
    def _handle_time_line_state_changed(self, new_state):
        sources = [conn.rect().center() for conn in self._item.connectors.values() if conn.incoming_links()]
        sinks = [conn.rect().center() for conn in self._item.connectors.values() if conn.outgoing_links()]
        center = self._item.rect().center()
        if not sinks:
            sinks = [center]
        for source in sources:
            for sink in sinks:
                rect = QRectF(
                    center.x() - self._loop_extent / 2,
                    center.y() - self._loop_extent / 2,
                    self._loop_extent,
                    self._loop_extent,
                )
                if source == sink:
                    sweep = 180
                elif source.y() == sink.y():
                    sweep = 360
                else:
                    sweep = 270
                if source.x() > sink.x():
                    sweep = -sweep
                if source.y() < rect.bottom():
                    start = 270
                else:
                    if source.x() > sink.x():
                        start = 180
                    else:
                        start = 0
                path = QPainterPath()
                path.moveTo(source)
                path.arcTo(rect, start, sweep)
                path.lineTo(sink)
                cube_count = self._cube_density * path.length() // self._item.boundingRect().width()
                self._cubes += [
                    _Cube(self._item, self._font, path, -i / cube_count, self._step) for i in range(int(cube_count))
                ]
        if new_state == QTimeLine.NotRunning:
            for cube in self._cubes:
                cube.scene().removeItem(cube)
            self._cubes.clear()

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


class _Cube(QGraphicsTextItem):
    def __init__(self, parent, font, path, percent, step):
        super().__init__(parent)
        self._path = path
        self._percent = percent
        self._step = step
        self._icon_code = "\uf1b2"
        self.setHtml(self._icon_code)
        self.setFont(font)
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.setDefaultTextColor(Qt.white)
        self.setTransformOriginPoint(self.boundingRect().center())
        self._inset = QGraphicsTextItem(self)
        self._inset.setHtml(self._icon_code)
        self._inset.setFont(font)
        self._inset.setDefaultTextColor(Qt.black)
        self._inset.setTransformOriginPoint(self._inset.boundingRect().center())
        self._inset.setScale(0.9)
        self.hide()

    def advance(self):
        self._percent = self._percent + self._step
        if self._percent > 1:
            self._percent = -1
        if self._percent < 0:
            self.hide()
            return
        self.show()
        pos = self._path.pointAtPercent(self._percent)
        self.setPos(pos - self.boundingRect().center())
        opacity = math.sin(math.pi * self._percent)
        self.setOpacity(opacity)
        angle = self._percent * 360.0
        self.setRotation(angle)


class ImporterAnimation(ImporterExporterAnimation):
    @staticmethod
    def percent(value):
        return value


class ExporterAnimation(ImporterExporterAnimation):
    @staticmethod
    def percent(value):
        return 1 - value
