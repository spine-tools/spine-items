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
import os
from pathlib import Path
import sys
from unittest import mock
from PySide6.QtWidgets import QApplication
import pytest
from spine_engine.project_item.project_item_resource import database_resource
from spine_items.data_store.data_store import DataStore
from spine_items.data_store.data_store_factory import DataStoreFactory
from spine_items.data_store.item_info import ItemInfo
from spine_items.utils import UrlDict, convert_to_sqlalchemy_url, database_label
from spinedb_api import create_new_spine_database
from spinetoolbox.helpers import signal_waiter
from tests.mock_helpers import (
    create_mock_project,
    create_mock_toolbox,
    mock_finish_project_item_construction,
)


class TestDataStore:
    def test_item_type(self):
        """Tests that the item type is correct."""
        assert DataStore.item_type() == ItemInfo.item_type()


@pytest.fixture()
def ds_and_properties(spine_toolbox_with_project):
    factory = DataStoreFactory()
    item_dict = {"type": "Data Store", "description": "", "x": 0, "y": 0, "url": None}
    project = spine_toolbox_with_project.project()
    with mock.patch("spine_items.data_store.data_store.QMenu"):
        ds = factory.make_item("DS", item_dict, spine_toolbox_with_project, project)
    project.add_item(ds)
    properties_widget = mock_finish_project_item_construction(factory, ds, spine_toolbox_with_project)
    return ds, properties_widget


@pytest.fixture()
def project(spine_toolbox_with_project):
    return spine_toolbox_with_project.project()


@pytest.fixture()
def ds(ds_and_properties):
    return ds_and_properties[0]


@pytest.fixture()
def properties_widget(ds_and_properties):
    return ds_and_properties[1]


@pytest.fixture()
def ds_properties_ui(properties_widget):
    return properties_widget.ui


def create_temp_db(ds):
    """Let's create a real db to more easily test complicated stuff (such as opening a tree view)."""
    temp_db_path = os.path.join(ds.data_dir, "temp_db.sqlite")
    sqlite_url = "sqlite:///" + temp_db_path
    create_new_spine_database(sqlite_url)
    return temp_db_path


class TestDataStoreWithToolbox:
    @pytest.mark.skipif(
        sys.platform == "win32" and sys.version_info > (3, 12),
        reason="Deleting .sqlite files that are in use by SqlAlchemy breaks the test.",
    )
    def test_rename(self, ds, ds_properties_ui, project):
        """Tests renaming a Data Store with an existing sqlite db in its data_dir."""
        temp_path = create_temp_db(ds)
        url = {"dialect": "sqlite", "database": temp_path}
        ds._url = ds.parse_url(url)
        ds.activate()
        # Check that DS is connected to an existing DS.sqlite file that is in data_dir
        url = ds_properties_ui.url_selector_widget.url_dict()
        assert url["dialect"] == "sqlite"
        assert os.path.normcase(url["database"]), os.path.normcase(os.path.join(ds.data_dir, "temp_db.sqlite"))
        assert os.path.exists(url["database"])
        expected_name = "ABC"
        expected_short_name = "abc"
        expected_data_dir = os.path.join(project.items_dir, expected_short_name)
        assert ds.rename(expected_name, "")
        # Check name
        assert expected_name == ds.name
        assert expected_name == ds.get_icon().name()
        # Check data_dir and logs_dir
        assert expected_data_dir == ds.data_dir
        # Check that the database path in properties has been updated
        expected_db_path = os.path.normcase(os.path.join(expected_data_dir, "temp_db.sqlite"))
        url = ds_properties_ui.url_selector_widget.url_dict()
        assert os.path.normcase(url["database"]) == expected_db_path
        # Check that the db file has actually been moved
        assert os.path.exists(url["database"])

    def test_dirty_db_notification(self, ds, ds_properties_ui, spine_toolbox_with_project):
        temp_path = create_temp_db(ds)
        url = {"dialect": "sqlite", "database": temp_path}
        ds._url = ds.parse_url(url)
        ds.activate()
        # Test that there are no notifications
        ds._check_notifications()
        assert [] == ds.get_icon().exclamation_icon._notifications
        # Check that there is a warning about uncommitted changes
        db_map = ds.get_db_map()
        spine_toolbox_with_project.db_mngr.add_items("entity_class", {db_map: [{"name": "my_object_class"}]})
        assert [f"{ds.name} has uncommitted changes"] == ds.get_icon().exclamation_icon._notifications
        # Check that the warning disappears after committing the changes
        spine_toolbox_with_project.db_mngr.commit_session("Added entity classes", db_map)
        assert [] == ds.get_icon().exclamation_icon._notifications

    def test_sqlite_url_deserialization(self, ds, project, spine_toolbox_with_project):
        url: UrlDict = {
            "dialect": "sqlite",
            "database": create_temp_db(ds),
        }
        assert ds.update_url(**url)
        serialized = ds.item_dict()
        deserialized = DataStore.from_dict("deserialized DS", serialized, spine_toolbox_with_project, project)
        assert deserialized.url() == ds.url()


# noinspection PyUnusedLocal
class TestDataStoreWithMockToolbox:
    def test_item_dict(self, ds):
        """Tests Item dictionary creation."""
        d = ds.item_dict()
        a = ["type", "description", "x", "y", "url"]
        url_keys = ["dialect", "username", "password", "host", "port", "database"]
        for k in a:
            assert k in d, f"Key '{k}' not in dict {d}"
            if k == "url":
                for url_key in url_keys:
                    assert url_key in d[k], f"Key '{url_key}' not in dict {d[k]}"

    def test_create_new_empty_spine_database(self, ds, ds_properties_ui, spine_toolbox_with_project):
        """Test that an open file dialog is shown when clicking on 'New Spine db tool button'
        with an empty Data Store.
        """
        toolbox = spine_toolbox_with_project
        ds.activate()
        url = ds_properties_ui.url_selector_widget.url_dict()
        assert url["dialect"] == "sqlite"
        assert url["database"] == ""
        # Click New Spine db button
        toolbox.db_mngr = mock.MagicMock()
        with mock.patch("spine_items.data_store.data_store.QFileDialog") as file_dialog:
            file_dialog.getSaveFileName.return_value = ("", "")
            ds_properties_ui.pushButton_create_new_spine_db.click()
            file_dialog.getSaveFileName.assert_called_once()
        url = ds_properties_ui.url_selector_widget.url_dict()
        assert url["dialect"] == "sqlite"
        assert url["database"] == ""
        toolbox.db_mngr.create_new_spine_database.assert_not_called()

    def test_create_new_empty_spine_database2(self, ds, ds_properties_ui, spine_toolbox_with_project):
        """Test that a new Spine database is created when clicking on 'New Spine db' tool button
        with a Data Store that already has an .sqlite db.
        """
        temp_path = create_temp_db(ds)
        # Connect to an existing .sqlite db
        url = {"dialect": "sqlite", "database": temp_path}
        ds._url = ds.parse_url(url)
        ds.activate()  # This loads the url into properties UI widgets
        # DS should now have "sqlite" selected in the combobox
        url = ds_properties_ui.url_selector_widget.url_dict()
        assert url["dialect"] == "sqlite"
        assert url["database"] == temp_path
        assert os.path.exists(url["database"])
        # Click New Spine db button. Creates the sqlite file.
        with (
            mock.patch("spine_items.data_store.data_store.QFileDialog") as file_dialog,
            mock.patch.object(spine_toolbox_with_project.db_mngr, "create_new_spine_database") as mock_create_db,
        ):
            file_dialog.getSaveFileName.return_value = (temp_path, "*.sqlite")
            with signal_waiter(ds_properties_ui.pushButton_create_new_spine_db.clicked) as waiter:
                ds_properties_ui.pushButton_create_new_spine_db.click()
                waiter.wait()
            file_dialog.getSaveFileName.assert_called_once()
            mock_create_db.assert_called_once()
        url = ds_properties_ui.url_selector_widget.url_dict()
        assert url["database"] == temp_path
        assert url["dialect"] == "sqlite"
        assert os.path.exists(url["database"])

    def test_new_database_is_created_before_advertising_resources(
        self, ds, ds_properties_ui, project, spine_toolbox_with_project
    ):
        toolbox = spine_toolbox_with_project
        ds.activate()
        database_file_path = os.path.join(project.project_dir, "test_db.sqlite")
        ds_properties_ui.url_selector_widget.set_url({"dialect": "sqlite"})
        ds._update_url_from_properties()
        url = ds_properties_ui.url_selector_widget.url_dict()
        assert url["dialect"] == "sqlite"
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

        with (
            mock.patch("spine_items.data_store.data_store.QFileDialog") as file_dialog,
            mock.patch.object(project, "notify_resource_changes_to_successors") as mock_successor_notifier,
            mock.patch.object(project, "notify_resource_changes_to_predecessors") as mock_predecessor_notifier,
        ):
            create_new_spine_database("sqlite:///" + database_file_path)
            file_dialog.getSaveFileName.return_value = (database_file_path,)
            mock_successor_notifier.side_effect = lambda item: check_database_exists(
                item, True, calls_with_non_empty_resources
            )
            mock_predecessor_notifier.side_effect = lambda item: check_database_exists(
                item, False, calls_with_non_empty_resources
            )
            assert ds_properties_ui.pushButton_create_new_spine_db.isEnabled()
            ds_properties_ui.pushButton_create_new_spine_db.click()
            while not ds.is_url_validated():
                QApplication.processEvents()
        assert len(calls_with_non_empty_resources) > 0
        assert failure_messages == []

    def test_save_and_restore_mysql_selections(self, ds, ds_properties_ui):
        """Test that MySQL selections are saved and restored when
        deactivating a Data Store and activating it again."""
        url = {"dialect": "mysql", "database": "sqlite:///mock_db.sqlite"}
        ds._url = ds.parse_url(url)  # Set a URL for the Data Store
        ds.activate()
        ds_properties_ui.url_selector_widget.set_url(
            {
                "dialect": "mysql",
                "host": "localhost",
                "port": 8080,
                "database": "foo",
                "username": "bar",
                "password": "s3cr3t",
            }
        )
        ds._update_url_from_properties()
        ds.deactivate()
        ds.activate()
        url = ds_properties_ui.url_selector_widget.url_dict()
        assert url["dialect"] == "mysql"
        assert url["host"] == "localhost"
        assert url["port"] == 8080
        assert url["database"] == "foo"
        assert url["username"] == "bar"
        assert url["password"] == "s3cr3t"

    def test_copy_db_url_to_clipboard(self, ds, ds_properties_ui):
        """Test that the database url from current selections is copied to clipboard."""
        QApplication.clipboard().clear()
        temp_path = create_temp_db(ds)
        url = {"dialect": "sqlite", "database": temp_path}
        ds._url = ds.parse_url(url)
        ds.activate()  # This loads the url into properties UI widgets
        ds_properties_ui.toolButton_copy_url.click()
        # noinspection PyArgumentList
        clipboard_text = QApplication.clipboard().text()
        expected_url = "sqlite:///" + os.path.join(ds.data_dir, "temp_db.sqlite")
        if sys.platform == "win32":
            assert expected_url.casefold() == clipboard_text.strip().casefold()
        else:
            assert expected_url == clipboard_text.strip()

    def test_open_db_editor1(self, ds, ds_properties_ui, spine_toolbox_with_project):
        """Test that selecting the 'sqlite' dialect, browsing to an existing db file,
        and pressing open form works as expected.
        """
        toolbox = spine_toolbox_with_project
        temp_db_path = create_temp_db(ds)
        ds.activate()
        ds_properties_ui.url_selector_widget.set_url({"dialect": "sqlite", "database": temp_db_path})
        ds._update_url_from_properties()
        toolbox.db_mngr = mock.MagicMock()
        while not ds.is_url_validated():
            QApplication.processEvents()
        assert ds_properties_ui.pushButton_ds_open_editor.isEnabled()
        with mock.patch("spine_items.data_store.data_store.open_db_editor") as open_db_editor:
            ds_properties_ui.pushButton_ds_open_editor.click()
            sa_url = convert_to_sqlalchemy_url(ds.url(), "DS", logger=None)
            assert sa_url is not None
            open_db_editor.assert_called_with([sa_url], toolbox.db_mngr, True)

    def test_open_db_editor2(self, ds, ds_properties_ui, spine_toolbox_with_project):
        """Test that selecting the 'sqlite' dialect, typing the path to an existing db file,
        and pressing open form works as expected.
        """
        toolbox = spine_toolbox_with_project
        temp_db_path = create_temp_db(ds)
        ds.activate()
        ds_properties_ui.url_selector_widget.set_url({"dialect": "sqlite", "database": temp_db_path})
        ds._update_url_from_properties()
        toolbox.db_mngr = mock.MagicMock()
        while not ds.is_url_validated():
            QApplication.processEvents()
        assert ds_properties_ui.pushButton_ds_open_editor.isEnabled()
        with mock.patch("spine_items.data_store.data_store.open_db_editor") as open_db_editor:
            ds_properties_ui.pushButton_ds_open_editor.click()
            sa_url = convert_to_sqlalchemy_url(ds.url(), "DS", logger=None)
            assert sa_url is not None
            open_db_editor.assert_called_with([sa_url], toolbox.db_mngr, True)

    def test_notify_destination(self, ds):
        ds.logger.msg = mock.MagicMock()
        ds.logger.msg_warning = mock.MagicMock()
        source_item = mock.MagicMock()
        source_item.name = "source name"
        source_item.item_type = mock.MagicMock(return_value="Data Connection")
        ds.notify_destination(source_item)
        ds.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a "
            "<b>Data Connection</b> and a <b>Data Store</b> has not been implemented yet."
        )
        source_item.item_type = mock.MagicMock(return_value="Importer")
        ds.notify_destination(source_item)
        ds.logger.msg.emit.assert_called_with(
            "Link established. "
            "Mapped data generated by <b>source name</b> will be imported in <b>DS</b> when executing."
        )
        source_item.item_type = mock.MagicMock(return_value="Tool")
        ds.notify_destination(source_item)
        ds.logger.msg.emit.assert_called_with("Link established")
        source_item.item_type = mock.MagicMock(return_value="View")
        ds.notify_destination(source_item)
        ds.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a "
            "<b>View</b> and a <b>Data Store</b> has not been implemented yet."
        )

    def test_do_update_url_uses_filterable_resources_when_replacing_them(self, ds, project):
        database_1 = os.path.normcase(os.path.join(project.project_dir, "db1.sqlite"))
        create_new_spine_database("sqlite:///" + database_1)
        with (
            mock.patch.object(project, "notify_resource_changes_to_predecessors"),
            mock.patch.object(project, "notify_resource_changes_to_successors"),
            mock.patch.object(project, "notify_resource_replacement_to_predecessors"),
            mock.patch.object(project, "notify_resource_replacement_to_successors"),
        ):
            ds.do_update_url(dialect="sqlite", database=database_1)
            project.notify_resource_changes_to_predecessors.assert_called_once_with(ds)
            project.notify_resource_changes_to_successors.assert_called_once_with(ds)
            while not ds.is_url_validated():
                QApplication.processEvents()
            database_2 = os.path.normcase(os.path.join(project.project_dir, "db2.sqlite"))
            create_new_spine_database("sqlite:///" + database_2)
            ds.do_update_url(dialect="sqlite", database=database_2)
            while not ds.is_url_validated():
                QApplication.processEvents()
            expected_old_resources = [
                database_resource(ds.name, "sqlite:///" + database_1, label=database_label(ds.name), filterable=True)
            ]
            expected_new_resources = [
                database_resource(ds.name, "sqlite:///" + database_2, label=database_label(ds.name), filterable=True)
            ]
            project.notify_resource_replacement_to_predecessors.assert_called_once_with(
                ds, expected_old_resources, expected_new_resources
            )
            project.notify_resource_replacement_to_successors.assert_called_once_with(
                ds, expected_old_resources, expected_new_resources
            )
