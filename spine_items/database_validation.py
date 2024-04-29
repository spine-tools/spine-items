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

"""Utilities to validate that a database exists."""
from pathlib import Path
from PySide6.QtCore import QObject, QRunnable, QThread, QThreadPool, QTimer, Signal, Slot
from PySide6.QtWidgets import QApplication
from spine_items.utils import check_database_url


class _ValidationTask(QRunnable):
    """Runnable that performs the actual validation in a worker thread."""

    def __init__(self, dialect, sa_url, finish_slot, fail_slot, success_slot):
        """
        Args:
            dialect (str): database dialect
            sa_url (URL): SQLAlchemy URL
            finish_slot (Callable): a Qt slot to connect to the finished signal
            fail_slot (Callable): a Qt slot to connect to the fail signal
            success_slot (Callable, optional): a Qt slot to connect to the success signal
        """
        super().__init__()
        self._dialect = dialect
        self._sa_url = sa_url
        self._signals = _TaskSignals()
        self._signals.moveToThread(None)
        self._signals.validation_failed.connect(fail_slot)
        if success_slot is not None:
            self._signals.validation_succeeded.connect(success_slot)
        self._signals.finished.connect(finish_slot)

    def run(self):
        """Checks if it is possible to establish an SQLAlchemy connection to the given URL."""
        try:
            self._signals.moveToThread(QThread.currentThread())
            if self._dialect == "sqlite":
                database_path = Path(self._sa_url.database)
                if not database_path.exists():
                    self._signals.validation_failed.emit(
                        "File does not exist. Check the Database field in the URL.", self._sa_url
                    )
                    return
                elif database_path.is_dir():
                    self._signals.validation_failed.emit(
                        "Database points to a directory, not a file. Check the Database field in the URL.",
                        self._sa_url,
                    )
                    return
            error = check_database_url(self._sa_url)
            if error is not None:
                self._signals.validation_failed.emit(error, self._sa_url)
                return
            self._signals.validation_succeeded.emit(self._sa_url)
        finally:
            self._signals.finished.emit()
            application = QApplication.instance()
            self._signals.moveToThread(application.thread())
            self._signals.deleteLater()


class _TaskSignals(QObject):
    """Signals for validation task."""

    validation_failed = Signal(str, object)
    validation_succeeded = Signal(object)
    finished = Signal()


class DatabaseConnectionValidator(QObject):
    """Database connection validator.

    Executes a single validation task at a time in a separate thread.
    While the thread is busy, queues the latest validation request.
    """

    def __init__(self, parent=None):
        """
        Args:
            parent (QObject): parent object
        """
        super().__init__(parent)
        self._threadpool = QThreadPool.globalInstance()
        self._busy = False
        self._deferred_task = None
        self._closed = False

    def is_busy(self):
        """Tests if there is a validator task running."""
        return self._busy

    def validate_url(self, dialect, sa_url, fail_slot, success_slot):
        """Connects signals and starts a task to validate the given URL.

        If validation task is running, puts a new task to a queue.
        If there is a task in the queue, it is replaced by a new one.

        If validation succeeds, success_slot will be called with no arguments.
        If validation fails, fail_slot will be called with an error string parameter.

        Args:
            dialect (str): database dialect
            sa_url (URL): SQLAlchemy URL
            fail_slot (Callable): a Qt slot that is invoked if validation fails
            success_slot (Callable, optional): a Qt Slot that is invoked if validation succeeds
        """
        if self._closed:
            return
        if not self._busy:
            self._busy = True
            self._threadpool.start(_ValidationTask(dialect, sa_url, self._set_non_busy, fail_slot, success_slot))
        else:
            queued = self._deferred_task is not None
            self._deferred_task = _ValidationTask(dialect, sa_url, self._set_non_busy, fail_slot, success_slot)
            if not queued:
                QTimer.singleShot(500, self._start_from_queue)

    def _start_from_queue(self):
        """Tries to start a deferred task from the queue."""
        if self._closed:
            return
        if self._busy:
            QTimer.singleShot(500, self._start_from_queue)
            return
        self._busy = True
        self._threadpool.start(self._deferred_task)
        self._deferred_task = None

    @Slot()
    def _set_non_busy(self):
        """Sets the machine not busy."""
        self._busy = False

    def wait_for_finish(self):
        """Waits for the thread to finish."""
        self._closed = True
        while self._busy:
            QApplication.processEvents()
