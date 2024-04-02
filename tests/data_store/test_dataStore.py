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

"""Unit tests for DataStore class."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest import mock
import os
import logging
import sys
from spinedb_api import create_new_spine_database
from spine_engine.project_item.project_item_resource import database_resource
from PySide6.QtWidgets import QApplication
import spine_items.resources_icons_rc  # pylint: disable=unused-import
from spine_items.data_store.data_store import DataStore
from spine_items.data_store.data_store_factory import DataStoreFactory
from spine_items.data_store.item_info import ItemInfo
from spine_items.utils import convert_to_sqlalchemy_url, database_label
from spinetoolbox.helpers import signal_waiter
from ..mock_helpers import mock_finish_project_item_construction, create_mock_project, create_mock_toolbox


class TestDataStore(unittest.TestCase):
    def test_item_type(self):
        """Tests that the item type is correct."""
        self.assertEqual(DataStore.item_type(), ItemInfo.item_type())


# noinspection PyUnusedLocal
class TestDataStoreWithMockToolbox(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Overridden method. Runs once before all tests in this class."""
        try:
            cls.app = QApplication().processEvents()
        except RuntimeError:
            pass
        logging.basicConfig(
            stream=sys.stderr,
            level=logging.DEBUG,
            format="%(asctime)s %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def setUp(self):
        """Set up."""
        self.toolbox = create_mock_toolbox()
        factory = DataStoreFactory()
        item_dict = {"type": "Data Store", "description": "", "x": 0, "y": 0, "url": None}
        self._temp_dir = TemporaryDirectory()
        self.project = create_mock_project(self._temp_dir.name)
        self.toolbox.project.return_value = self.project
        with mock.patch("spine_items.data_store.data_store.QMenu"):
            self.ds = factory.make_item("DS", item_dict, self.toolbox, self.project)
        self.project.get_item.return_value = self.ds
        self._properties_widget = mock_finish_project_item_construction(factory, self.ds, self.toolbox)
        self.ds_properties_ui = self.ds._properties_ui

    def tearDown(self):
        """Overridden method. Runs after each test.
        Use this to free resources after a test if needed.
        """
        ds_db_path = os.path.join(self.ds.data_dir, "DS.sqlite")
        temp_db_path = os.path.join(self.ds.data_dir, "temp_db.sqlite")
        self.ds.tear_down()
        if os.path.exists(ds_db_path):
            try:
                os.remove(ds_db_path)
            except OSError as os_e:
                logging.error("Failed to remove %s. Error: %s", ds_db_path, os_e)
        if os.path.exists(temp_db_path):
            try:
                os.remove(temp_db_path)
            except OSError as os_e:
                logging.error("Failed to remove %s. Error: %s", temp_db_path, os_e)
        self._temp_dir.cleanup()

    def create_temp_db(self):
        """Let's create a real db to more easily test complicated stuff (such as opening a tree view)."""
        temp_db_path = os.path.join(self.ds.data_dir, "temp_db.sqlite")
        sqlite_url = "sqlite:///" + temp_db_path
        create_new_spine_database(sqlite_url)
        return temp_db_path

    def test_item_dict(self):
        """Tests Item dictionary creation."""
        d = self.ds.item_dict()
        a = ["type", "description", "x", "y", "url"]
        url_keys = ["dialect", "username", "password", "host", "port", "database"]
        for k in a:
            self.assertTrue(k in d, f"Key '{k}' not in dict {d}")
            if k == "url":
                for url_key in url_keys:
                    self.assertTrue(url_key in d[k], f"Key '{url_key}' not in dict {d[k]}")

    def test_create_new_empty_spine_database(self):
        """Test that a new Spine database is not created when clicking on 'New Spine db tool button'
        with an empty Data Store.
        """
        self.ds.activate()
        url = self.ds_properties_ui.url_selector_widget.url_dict()
        self.assertEqual(url["dialect"], "")
        self.assertEqual(url["database"], "")
        # Click New Spine db button
        self.toolbox.db_mngr = mock.MagicMock()
        self.ds_properties_ui.pushButton_create_new_spine_db.click()
        url = self.ds_properties_ui.url_selector_widget.url_dict()
        self.assertEqual(url["dialect"], "")
        self.assertEqual(url["database"], "")
        self.toolbox.db_mngr.create_new_spine_database.assert_not_called()

    def test_create_new_empty_spine_database2(self):
        """Test that a new Spine database is created when clicking on 'New Spine db' tool button
        with a Data Store that already has an .sqlite db.
        """
        temp_path = self.create_temp_db()
        # Connect to an existing .sqlite db
        url = dict(dialect="sqlite", database=temp_path)
        self.ds._url = self.ds.parse_url(url)
        self.ds.activate()  # This loads the url into properties UI widgets
        # DS should now have "sqlite" selected in the combobox
        url = self.ds_properties_ui.url_selector_widget.url_dict()
        self.assertEqual(url["dialect"], "sqlite")
        self.assertEqual(url["database"], temp_path)
        self.assertTrue(os.path.exists(url["database"]))
        # Click New Spine db button. Creates the sqlite file.
        with mock.patch("spine_items.data_store.data_store.QFileDialog") as file_dialog:
            file_dialog.getSaveFileName.return_value = (temp_path, "*.sqlite")
            with signal_waiter(self.ds_properties_ui.pushButton_create_new_spine_db.clicked) as waiter:
                self.ds_properties_ui.pushButton_create_new_spine_db.click()
                waiter.wait()
            file_dialog.getSaveFileName.assert_called_once()
        url = self.ds_properties_ui.url_selector_widget.url_dict()
        self.assertEqual(url["database"], temp_path)
        self.assertEqual(url["dialect"], "sqlite")
        self.assertTrue(os.path.exists(url["database"]))
        self.toolbox.db_mngr.create_new_spine_database.assert_called_once()

    def test_new_database_is_created_before_advertising_resources(self):
        self.ds.activate()
        database_file_path = os.path.join(self._temp_dir.name, "test_db.sqlite")
        self.ds_properties_ui.url_selector_widget.set_url({"dialect": "sqlite"})
        self.ds._update_url_from_properties()
        url = self.ds_properties_ui.url_selector_widget.url_dict()
        self.assertEqual(url["dialect"], "sqlite")
        calls_with_non_empty_resources = []
        failure_messages = []

        def check_database_exists(data_store, for_successors, non_empty_calls):
            if for_successors:
                resources = data_store.resources_for_direct_successors()
            else:
                resources = data_store.resources_for_direct_predecessors()
            if len(resources) == 0:
                return
            non_empty_calls.append(1)
            if len(resources) > 1:
                failure_messages.append("resources length is not equal to 1")
                return
            call_args = self.toolbox.db_mngr.create_new_spine_database.call_args
            if len(call_args[0]) != 2:
                failure_messages.append("call_args *args length is not equal to 2")
                return
            if str(call_args[0][0]) != resources[0].url:
                failure_messages.append("create_new_spine_database() called with wrong URL")

        with mock.patch("spine_items.data_store.data_store.QFileDialog") as file_dialog:
            Path(database_file_path).touch()
            file_dialog.getSaveFileName.return_value = (database_file_path,)
            self.project.notify_resource_changes_to_successors.side_effect = lambda item: check_database_exists(
                item, True, calls_with_non_empty_resources
            )
            self.project.notify_resource_changes_to_predecessors.side_effect = lambda item: check_database_exists(
                item, False, calls_with_non_empty_resources
            )
            self.assertTrue(self.ds_properties_ui.pushButton_create_new_spine_db.isEnabled())
            self.ds_properties_ui.pushButton_create_new_spine_db.click()
        while not self.ds.is_url_validated():
            QApplication.processEvents()
        self.assertGreater(len(calls_with_non_empty_resources), 0)
        if failure_messages:
            self.fail(failure_messages[0])

    def test_save_and_restore_mysql_selections(self):
        """Test that MySQL selections are saved and restored when
        deactivating a Data Store and activating it again."""
        url = dict(dialect="mysql", database="sqlite:///mock_db.sqlite")
        self.ds._url = self.ds.parse_url(url)  # Set a URL for the Data Store
        self.ds.activate()
        self.ds_properties_ui.url_selector_widget.set_url(
            {
                "dialect": "mysql",
                "host": "localhost",
                "port": "8080",
                "database": "foo",
                "username": "bar",
                "password": "s3cr3t",
            }
        )
        self.ds._update_url_from_properties()
        self.ds.deactivate()
        self.ds.activate()
        url = self.ds_properties_ui.url_selector_widget.url_dict()
        self.assertEqual(url["dialect"], "mysql")
        self.assertEqual(url["host"], "localhost")
        self.assertEqual(url["port"], "8080")
        self.assertEqual(url["database"], "foo")
        self.assertEqual(url["username"], "bar")
        self.assertEqual(url["password"], "s3cr3t")

    def test_copy_db_url_to_clipboard(self):
        """Test that the database url from current selections is copied to clipboard."""
        QApplication.clipboard().clear()
        temp_path = self.create_temp_db()
        url = dict(dialect="sqlite", database=temp_path)
        self.ds._url = self.ds.parse_url(url)
        self.ds.activate()  # This loads the url into properties UI widgets
        self.ds_properties_ui.toolButton_copy_url.click()
        # noinspection PyArgumentList
        clipboard_text = QApplication.clipboard().text()
        expected_url = "sqlite:///" + os.path.join(self.ds.data_dir, "temp_db.sqlite")
        self.assertEqual(expected_url, clipboard_text.strip())

    def test_open_db_editor1(self):
        """Test that selecting the 'sqlite' dialect, browsing to an existing db file,
        and pressing open form works as expected.
        """
        temp_db_path = self.create_temp_db()
        self.ds.activate()
        self.ds_properties_ui.url_selector_widget.set_url({"dialect": "sqlite", "database": temp_db_path})
        self.ds._update_url_from_properties()
        self.toolbox.db_mngr = mock.MagicMock()
        self.toolbox.db_mngr.get_all_multi_spine_db_editors = lambda: iter([])
        while not self.ds.is_url_validated():
            QApplication.processEvents()
        self.assertTrue(self.ds_properties_ui.pushButton_ds_open_editor.isEnabled())
        self.ds_properties_ui.pushButton_ds_open_editor.click()
        sa_url = convert_to_sqlalchemy_url(self.ds.url(), "DS", logger=None)
        self.assertIsNotNone(sa_url)
        self.toolbox.db_mngr.open_db_editor.assert_called_with({sa_url: "DS"}, True)

    def test_open_db_editor2(self):
        """Test that selecting the 'sqlite' dialect, typing the path to an existing db file,
        and pressing open form works as expected.
        """
        temp_db_path = self.create_temp_db()
        self.ds.activate()
        self.ds_properties_ui.url_selector_widget.set_url({"dialect": "sqlite", "database": temp_db_path})
        self.ds._update_url_from_properties()
        self.toolbox.db_mngr = mock.MagicMock()
        self.toolbox.db_mngr.get_all_multi_spine_db_editors = lambda: iter([])
        while not self.ds.is_url_validated():
            QApplication.processEvents()
        self.assertTrue(self.ds_properties_ui.pushButton_ds_open_editor.isEnabled())
        self.ds_properties_ui.pushButton_ds_open_editor.click()
        sa_url = convert_to_sqlalchemy_url(self.ds.url(), "DS", logger=None)
        self.assertIsNotNone(sa_url)
        self.toolbox.db_mngr.open_db_editor.assert_called_with({sa_url: "DS"}, True)

    def test_notify_destination(self):
        self.ds.logger.msg = mock.MagicMock()
        self.ds.logger.msg_warning = mock.MagicMock()
        source_item = mock.MagicMock()
        source_item.name = "source name"
        source_item.item_type = mock.MagicMock(return_value="Data Connection")
        self.ds.notify_destination(source_item)
        self.ds.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a "
            "<b>Data Connection</b> and a <b>Data Store</b> has not been implemented yet."
        )
        source_item.item_type = mock.MagicMock(return_value="Importer")
        self.ds.notify_destination(source_item)
        self.ds.logger.msg.emit.assert_called_with(
            "Link established. "
            "Mapped data generated by <b>source name</b> will be imported in <b>DS</b> when executing."
        )
        source_item.item_type = mock.MagicMock(return_value="Tool")
        self.ds.notify_destination(source_item)
        self.ds.logger.msg.emit.assert_called_with("Link established")
        source_item.item_type = mock.MagicMock(return_value="View")
        self.ds.notify_destination(source_item)
        self.ds.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a "
            "<b>View</b> and a <b>Data Store</b> has not been implemented yet."
        )

    def test_rename(self):
        """Tests renaming a Data Store with an existing sqlite db in it's data_dir."""
        temp_path = self.create_temp_db()
        url = dict(dialect="sqlite", database=temp_path)
        self.ds._url = self.ds.parse_url(url)
        self.ds.activate()
        # Check that DS is connected to an existing DS.sqlite file that is in data_dir
        url = self.ds_properties_ui.url_selector_widget.url_dict()
        self.assertEqual(url["dialect"], "sqlite")
        self.assertEqual(url["database"], os.path.join(self.ds.data_dir, "temp_db.sqlite"))  # data_dir before rename
        self.assertTrue(os.path.exists(url["database"]))
        expected_name = "ABC"
        expected_short_name = "abc"
        expected_data_dir = os.path.join(self.project.items_dir, expected_short_name)
        self.ds.rename(expected_name, "")  # Do rename
        # Check name
        self.assertEqual(expected_name, self.ds.name)  # item name
        self.assertEqual(expected_name, self.ds.get_icon().name())  # name item on Design View
        # Check data_dir and logs_dir
        self.assertEqual(expected_data_dir, self.ds.data_dir)  # Check data dir
        # Check that the database path in properties has been updated
        expected_db_path = os.path.join(expected_data_dir, "temp_db.sqlite")
        url = self.ds_properties_ui.url_selector_widget.url_dict()
        self.assertEqual(url["database"], expected_db_path)
        # Check that the db file has actually been moved
        self.assertTrue(os.path.exists(url["database"]))

    def test_do_update_url_uses_filterable_resources_when_replacing_them(self):
        database_1 = os.path.join(self._temp_dir.name, "db1.sqlite")
        Path(database_1).touch()
        self.ds.do_update_url(dialect="sqlite", database=database_1)
        self.project.notify_resource_changes_to_predecessors.assert_called_once_with(self.ds)
        self.project.notify_resource_changes_to_successors.assert_called_once_with(self.ds)
        while not self.ds.is_url_validated():
            QApplication.processEvents()
        database_2 = os.path.join(self._temp_dir.name, "db2.sqlite")
        Path(database_2).touch()
        self.ds.do_update_url(dialect="sqlite", database=database_2)
        while not self.ds.is_url_validated():
            QApplication.processEvents()
        expected_old_resources = [
            database_resource(
                self.ds.name, "sqlite:///" + database_1, label=database_label(self.ds.name), filterable=True
            )
        ]
        expected_new_resources = [
            database_resource(
                self.ds.name, "sqlite:///" + database_2, label=database_label(self.ds.name), filterable=True
            )
        ]
        self.project.notify_resource_replacement_to_predecessors.assert_called_once_with(
            self.ds, expected_old_resources, expected_new_resources
        )
        self.project.notify_resource_replacement_to_successors.assert_called_once_with(
            self.ds, expected_old_resources, expected_new_resources
        )


if __name__ == "__main__":
    unittest.main()
