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

"""Unit tests for the ``database_validation`` module."""

from pathlib import Path
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QApplication
from sqlalchemy.engine.url import make_url
from spine_items.database_validation import DatabaseConnectionValidator
from spinedb_api import create_new_spine_database


class TestDatabaseConnectionValidator:
    def test_successful_validation_of_sqlite_database(self, application, tmp_path):
        url = "sqlite:///" + str(Path(tmp_path, "db.sqlite"))
        create_new_spine_database(url)
        listener = _Listener()
        validator = DatabaseConnectionValidator()
        try:
            sa_url = make_url(url)
            validator.validate_url("sqlite", sa_url, listener.failure, listener.success)
            while not listener.is_done:
                QApplication.processEvents()
        finally:
            validator.wait_for_finish()
            validator.deleteLater()
        assert listener.is_success

    def test_successful_validation_of_sqlite_database_with_str_url(self, application, tmp_path):
        url = "sqlite:///" + str(Path(tmp_path, "db.sqlite"))
        create_new_spine_database(url)
        listener = _Listener()
        validator = DatabaseConnectionValidator()
        try:
            sa_url = make_url(url)
            validator.validate_url("sqlite", sa_url, listener.failure, listener.success)
            while not listener.is_done:
                QApplication.processEvents()
        finally:
            validator.wait_for_finish()
            validator.deleteLater()
        assert listener.is_success

    def test_validation_failure_due_to_missing_sqlite_file(self, application, tmp_path):
        url = "sqlite:///" + str(Path(tmp_path, "db.sqlite"))
        listener = _Listener()
        validator = DatabaseConnectionValidator()
        try:
            sa_url = make_url(url)
            validator.validate_url("sqlite", sa_url, listener.failure, listener.success)
            while not listener.is_done:
                QApplication.processEvents()
        finally:
            validator.wait_for_finish()
            validator.deleteLater()
        assert not listener.is_success
        assert listener.fail_message, "File does not exist. Check the Database field in the URL."


class _Listener:
    def __init__(self):
        self.fail_message = None
        self._is_done = False

    @property
    def is_done(self):
        return self._is_done

    @property
    def is_success(self):
        if not self._is_done:
            raise RuntimeError("No success status available!")
        return self.fail_message is None

    @Slot(str)
    def failure(self, message):
        self.fail_message = message
        self._is_done = True

    @Slot()
    def success(self):
        self._is_done = True
