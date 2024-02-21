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

"""Animation class for importers and exporters."""
from PySide6.QtGui import QPainterPath, QFont, QFontMetrics
from PySide6.QtCore import Qt, Signal, Slot, QObject, QTimeLine, QRectF, QPointF, QLineF
from PySide6.QtWidgets import QGraphicsPathItem
from spinetoolbox.helpers import color_from_index


class AnimationSignaller(QObject):
    animation_started = Signal()
    animation_stopped = Signal()


class ImporterExporterAnimation:
    def __init__(self, item, duration=1800, plane_count=4, pixel_size=12, loop_width=30, loop_aspect_ratio=3):
        """Initializes animation stuff.

        Args:
            item (QGraphicsItem): The item on top of which the animation should play.
        """
        self._item = item
        self._planes = []
        self._plane_count = plane_count
        self._loop_aspect_ratio = loop_aspect_ratio
        self._loop_width = loop_width
        self._loop_height = loop_width / loop_aspect_ratio
        self._font = QFont("Font Awesome 5 Free Solid")
        self._font.setPixelSize(pixel_size)
        self.time_line = QTimeLine()
        self.time_line.setDuration(duration)
        self.time_line.setLoopCount(0)  # loop forever
        self.time_line.valueChanged.connect(self._handle_time_line_value_changed)
        self.time_line.stateChanged.connect(self._handle_time_line_state_changed)
        self._step = self.time_line.updateInterval() / duration

    @Slot(float)
    def _handle_time_line_value_changed(self, value):
        for plane in self._planes:
            plane.advance()

    @Slot(QTimeLine.State)
    def _handle_time_line_state_changed(self, new_state):
        sources = [conn.rect().center() for conn in self._item.connectors.values() if conn.incoming_links()]
        sinks = [conn.rect().center() for conn in self._item.connectors.values() if conn.outgoing_links()]
        center = self._item.rect().center()
        if not sinks:
            sinks = [center]
        source_sink_pairs = [(source, sink) for source in sources for sink in sinks]
        for source, sink in source_sink_pairs:
            loop_rect = QRectF(
                center.x() - self._loop_width / 2,
                center.y() - self._loop_height / 2,
                self._loop_width,
                self._loop_height,
            )
            # Find sweep:
            if source == sink:
                # Same source as destination: sweep half circle
                sweep = 180
            elif source.y() == sink.y():
                # Side to side: sweep full circle
                sweep = 360
            else:
                # Side to bottom: sweep 3/4 of circle
                sweep = 270
            # Find start and sense
            invert_sense = False
            if source.y() < loop_rect.bottom():
                # From the side: start at bottom
                start = 270
                # Invert sense if from the right
                invert_sense = source.x() > center.x()
            else:
                # From the bottom
                if sink.x() < center.x():
                    # To the left: start at left and invert sense
                    start = 180
                    invert_sense = True
                else:
                    # To the right: start at right
                    start = 0
            if invert_sense:
                sweep = -sweep
            middle_point = _point_at_angle(loop_rect, start)
            path = QPainterPath()
            path.moveTo(source)
            path.quadTo(_nice_ctrl_point(path.currentPosition(), middle_point), middle_point)
            path.arcTo(loop_rect, start, sweep)
            path.quadTo(_nice_ctrl_point(path.currentPosition(), sink), sink)
            self._planes += [
                self._PaperPlane(self._item, self._font, path, -i / self._plane_count, self._step, loop_rect)
                for i in range(self._plane_count)
            ]
        for k, plane in enumerate(self._planes):
            plane.color = color_from_index(k, len(self._planes))
        if new_state == QTimeLine.State.NotRunning:
            for plane in self._planes:
                plane.wipe_out()
            self._planes.clear()

    @Slot()
    def start(self):
        """Starts the animation."""
        if self.time_line.state() == QTimeLine.State.Running:
            return
        self.time_line.start()

    @staticmethod
    def percent(value):
        raise NotImplementedError()

    @Slot()
    def stop(self):
        """Stops the animation"""
        self.time_line.stop()


class _PaperPlane(QGraphicsPathItem):
    def __init__(self, parent, font, trajectory_path, percent, step, loop_rect):
        super().__init__(parent)
        self._parent = parent
        self._trajectory_path = trajectory_path
        self._percent = percent
        self._step = step
        self._loop_rect = loop_rect
        self._icon_code = "\uf1d8"
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.setZValue(self._parent.svg_item.zValue())
        path = QPainterPath()
        path.addText(0, (1 - 0.14) * QFontMetrics(font).height(), font, self._icon_code)  # 14% baseline for FA
        self.setPath(path)
        self.setTransformOriginPoint(self.boundingRect().center())
        border_pen = self.pen()
        border_pen.setWidthF(0.5)
        self.setPen(border_pen)
        self.color = Qt.white
        self.hide()

    def advance(self):
        self._percent = self._percent + self._step
        if self._percent > 1:
            self._percent = -0.8
        if self._percent < 0:
            self.hide()
            return
        self.show()
        pos = self._trajectory_path.pointAtPercent(self._percent)  #
        self.setPos(pos - self.boundingRect().center())
        if pos.y() > self._loop_rect.center().y():
            self._parent.svg_item.stackBefore(self)
            scale = 1
        else:
            self.stackBefore(self._parent.svg_item)
            scale = 1 - 0.5 * (self._loop_rect.center().y() - pos.y()) / (self._loop_rect.height() / 2)
        self.setScale(scale)
        angle = self._trajectory_path.angleAtPercent(self._percent)
        self.resetTransform()
        if 90 < angle < 270:
            self.flip_vertical()
            self.setRotation(45 + angle)
        else:
            self.setRotation(45 - angle)
        h, s, _, _ = self.color.getHslF()
        self.color.setHslF(h, s, self._lightness())
        self.setBrush(self.color)

    def _lightness(self):
        raise NotImplementedError()

    def flip_vertical(self):
        transform = self.transform()
        m11 = transform.m11()
        m12 = transform.m12()
        m13 = transform.m13()
        m21 = transform.m21()
        m22 = transform.m22()
        m23 = transform.m23()
        m31 = transform.m31()
        m32 = super().boundingRect().height() * m22
        m33 = transform.m33()
        m22 = -m22
        transform.setMatrix(m11, m12, m13, m21, m22, m23, m31, m32, m33)
        self.setTransform(transform)

    def wipe_out(self):
        scene = self.scene()
        if scene is None:
            return
        scene.removeItem(self)


def _point_at_angle(rect, angle):
    if angle == 0:
        return QPointF(rect.right(), rect.center().y())
    if angle == 180:
        return QPointF(rect.left(), rect.center().y())
    if angle == 270:
        return QPointF(rect.center().x(), rect.bottom())


def _nice_ctrl_point(p1, p2):
    if p1.x() > p2.x():
        p1, p2 = p2, p1
    line = QLineF(p1, p2)
    p = line.center()
    normal_angle = line.normalVector().angle()
    normal_line = QLineF()
    normal_line.setP1(p)
    normal_line.setAngle(normal_angle)
    normal_line.setLength(3)
    return normal_line.p2()


class _ImporterPaperPlane(_PaperPlane):
    def _lightness(self):
        threshold = 0.66
        max_darkness = 0.5
        darkness = max(0, max_darkness * (self._percent - threshold) / (1 - threshold))
        return 1 - darkness


class _ExporterPaperPlane(_PaperPlane):
    def _lightness(self):
        threshold = 0.66
        max_darkness = 0.5
        darkness = max(0, max_darkness * (threshold - self._percent) / threshold)
        return 1 - darkness


class ImporterAnimation(ImporterExporterAnimation):
    _PaperPlane = _ImporterPaperPlane


class ExporterAnimation(ImporterExporterAnimation):
    _PaperPlane = _ExporterPaperPlane
