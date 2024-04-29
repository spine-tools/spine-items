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

""" Unit tests for the ``utils`` module. """
import sys
import unittest
from unittest import mock
from spine_items.utils import convert_to_sqlalchemy_url, convert_url_to_safe_string, database_label


class TestDatabaseLabel(unittest.TestCase):
    def test_provider_name_is_appended_to_label(self):
        self.assertEqual(database_label("Item Name"), "db_url@Item Name")


class TestConvertToSqlAlchemyUrl(unittest.TestCase):
    def test_sqlite_url_conversion_succeeds(self):
        database_path = r"h:\files\database.sqlite" if sys.platform == "win32" else "/home/data/database.sqlite"
        url = {
            "dialect": "sqlite",
            "database": database_path,
        }
        sa_url = convert_to_sqlalchemy_url(url)
        self.assertEqual(sa_url.database, database_path)
        self.assertIsNone(sa_url.username)
        self.assertIsNone(sa_url.password)
        self.assertIsNone(sa_url.port)
        self.assertIsNone(sa_url.host)
        self.assertEqual(sa_url.drivername, r"sqlite")
        self.assertEqual(str(sa_url), r"sqlite:///" + database_path)

    def test_remote_url_conversion_succeeds(self):
        url = {
            "dialect": "mysql",
            "host": "example.com",
            "port": 5432,
            "database": "trade_nuc",
            "username": "superman",
            "password": "s3cr?t",
        }
        sa_url = convert_to_sqlalchemy_url(url)
        self.assertEqual(sa_url.database, "trade_nuc")
        self.assertEqual(sa_url.password, "s3cr?t")
        self.assertEqual(sa_url.username, "superman")
        self.assertEqual(sa_url.port, 5432)
        self.assertEqual(sa_url.host, "example.com")
        self.assertEqual(sa_url.drivername, r"mysql+pymysql")

    def test_remote_url_conversion_succeeds_with_schema(self):
        url = {
            "dialect": "mysql",
            "host": "example.com",
            "port": 5432,
            "database": "trade_nuc",
            "schema": "myschema",
            "username": "superman",
            "password": "s3cr?t",
        }
        sa_url = convert_to_sqlalchemy_url(url)
        self.assertEqual(sa_url.database, "trade_nuc")
        self.assertEqual(sa_url.password, "s3cr?t")
        self.assertEqual(sa_url.username, "superman")
        self.assertEqual(sa_url.port, 5432)
        self.assertEqual(sa_url.host, "example.com")
        self.assertEqual(sa_url.drivername, r"mysql+pymysql")

    def test_item_name_and_logger(self):
        url = {}
        logger = mock.MagicMock()
        self.assertIsNone(convert_to_sqlalchemy_url(url, "Item Name", logger))
        logger.msg_error.emit.assert_called_once_with(
            "No URL specified for <b>Item Name</b> selections. Please specify one and try again."
        )

    def test_missing_dialect_is_caught(self):
        url = {
            "dialect": "",
            "database": r"h:\files\database.sqlite",
        }
        logger = mock.MagicMock()
        self.assertIsNone(convert_to_sqlalchemy_url(url, "Item Name", logger))
        logger.msg_error.emit.assert_called_once_with(
            "Unable to generate URL from <b>Item Name</b> selections: missing dialect"
        )

    def test_missing_host_is_caught(self):
        url = {
            "dialect": "mysql",
            "host": "",
            "port": 5432,
            "database": "trade_nuc",
            "username": "superman",
            "password": "s3cr?t",
        }
        logger = mock.MagicMock()
        self.assertIsNone(convert_to_sqlalchemy_url(url, "Item Name", logger))
        logger.msg_error.emit.assert_called_once_with(
            "Unable to generate URL from <b>Item Name</b> selections: missing host"
        )

    def test_missing_port_is_caught(self):
        url = {
            "dialect": "mysql",
            "host": "example.com",
            "port": None,
            "database": "trade_nuc",
            "username": "superman",
            "password": "s3cr?t",
        }
        logger = mock.MagicMock()
        self.assertIsNone(convert_to_sqlalchemy_url(url, "Item Name", logger))
        logger.msg_error.emit.assert_called_once_with(
            "Unable to generate URL from <b>Item Name</b> selections: missing port"
        )

    def test_missing_username_is_caught(self):
        url = {
            "dialect": "mysql",
            "host": "example.com",
            "port": 5432,
            "database": "trade_nuc",
            "username": None,
            "password": "s3cr?t",
        }
        logger = mock.MagicMock()
        self.assertIsNone(convert_to_sqlalchemy_url(url, "Item Name", logger))
        logger.msg_error.emit.assert_called_once_with(
            "Unable to generate URL from <b>Item Name</b> selections: missing username"
        )

    def test_missing_password_is_caught(self):
        url = {
            "dialect": "mysql",
            "host": "example.com",
            "port": 5432,
            "database": "trade_nuc",
            "username": "superman",
            "password": None,
        }
        logger = mock.MagicMock()
        self.assertIsNone(convert_to_sqlalchemy_url(url, "Item Name", logger))
        logger.msg_error.emit.assert_called_once_with(
            "Unable to generate URL from <b>Item Name</b> selections: missing password"
        )


class TestConvertUrlToSafeString(unittest.TestCase):
    def test_removes_username_and_password(self):
        url = {
            "dialect": "mysql",
            "host": "example.com",
            "port": 5432,
            "database": "trade_nuc",
            "username": "superman",
            "password": "s3cr?t",
        }
        self.assertEqual(convert_url_to_safe_string(url), "mysql+pymysql://example.com:5432/trade_nuc")

    def test_works_without_credentials_in_url(self):
        url = {
            "dialect": "mysql",
            "host": "example.com",
            "port": 5432,
            "database": "trade_nuc",
        }
        self.assertEqual(convert_url_to_safe_string(url), "mysql+pymysql://example.com:5432/trade_nuc")

    def test_works_with_sqlite_url(self):
        database_path = r"c:\files\database.sqlite" if sys.platform == "win32" else "/dir/data/database.sqlite"
        url = {
            "dialect": "sqlite",
            "database": database_path,
        }
        self.assertEqual(convert_url_to_safe_string(url), r"sqlite:///" + database_path)


if __name__ == "__main__":
    unittest.main()
