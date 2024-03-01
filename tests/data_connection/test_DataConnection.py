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

"""Unit tests for Data Connection project item."""
import os
from tempfile import TemporaryDirectory
from pathlib import Path
import unittest
from unittest import mock
from unittest.mock import MagicMock, NonCallableMagicMock
from PySide6.QtCore import QItemSelectionModel
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox
from PySide6.QtGui import Qt
from spinedb_api import create_new_spine_database
from spinetoolbox.helpers import signal_waiter
from spine_items.data_connection.data_connection import _Role, DataConnection
from spine_items.data_connection.data_connection_factory import DataConnectionFactory
from spine_items.data_connection.item_info import ItemInfo
from tests.mock_helpers import (
    clean_up_toolbox,
    create_toolboxui_with_project,
    mock_finish_project_item_construction,
    create_mock_project,
    create_mock_toolbox,
)


class TestDataConnection(unittest.TestCase):
    def test_item_type(self):
        self.assertEqual(DataConnection.item_type(), ItemInfo.item_type())


class TestDataConnectionWithProject(unittest.TestCase):
    def setUp(self):
        """Set up."""
        self._temp_dir = TemporaryDirectory()
        self._toolbox = create_toolboxui_with_project(self._temp_dir.name)
        factory = DataConnectionFactory()
        item_dict = {"type": "Data Connection", "description": "", "db_references": [], "x": 0, "y": 0}
        project = self._toolbox.project()
        self._data_connection = factory.make_item("DC", item_dict, self._toolbox, project)
        project.add_item(self._data_connection)
        self._ref_model = self._data_connection.reference_model

    def tearDown(self):
        clean_up_toolbox(self._toolbox)
        self._temp_dir.cleanup()

    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def test_add_file_references(self):
        temp_dir = Path(self._temp_dir.name, "references")
        temp_dir.mkdir()
        with mock.patch("spine_items.data_connection.data_connection.QFileDialog.getOpenFileNames") as mock_filenames:
            a = Path(temp_dir, "a.txt")
            a.touch()
            b = Path(temp_dir, "b.txt")
            b.touch()
            c = Path(temp_dir, "c.txt")  # Note. Does not exist
            # Add nothing
            mock_filenames.return_value = ([], "*.*")
            self._data_connection.show_add_file_references_dialog()
            self.assertEqual(1, mock_filenames.call_count)
            self.assertEqual(0, len(self._data_connection.file_references))
            self.assertEqual(0, self._ref_model.rowCount(self._ref_model.index(0, 0)))
            # Add one file
            mock_filenames.return_value = ([str(a)], "*.*")
            self._data_connection.show_add_file_references_dialog()
            self.assertEqual(2, mock_filenames.call_count)
            self.assertEqual(1, len(self._data_connection.file_references))
            self.assertEqual(1, self._ref_model.rowCount(self._ref_model.index(0, 0)))
            self.assertEqual(str(a), self._ref_model.index(0, 0, self._ref_model.index(0, 0)).data())
            # Try to add a path that has already been added
            self._data_connection.show_add_file_references_dialog()
            self.assertEqual(3, mock_filenames.call_count)
            self.assertEqual(1, len(self._data_connection.file_references))
            self.assertEqual(1, self._ref_model.rowCount(self._ref_model.index(0, 0)))
            self.assertEqual(str(a), self._ref_model.index(0, 0, self._ref_model.index(0, 0)).data())
            self._data_connection.file_references = list()
            self._data_connection.populate_reference_list([])
            # Add two references (the other one is non-existing)
            # Note: non-existing files cannot be added with the toolbox but this tests a situation when
            # project.json file has references to files that do not exist anymore and user tries to add a
            # new reference to a Data Connection that contains non-existing file references
            mock_filenames.return_value = ([str(b), str(c)], "*.*")
            self._data_connection.show_add_file_references_dialog()
            self.assertEqual(4, mock_filenames.call_count)
            self.assertEqual(1, len(self._data_connection.file_references))
            self.assertEqual(1, self._ref_model.rowCount(self._ref_model.index(0, 0)))
            self.assertEqual(str(b), self._ref_model.index(0, 0, self._ref_model.index(0, 0)).data())
            # Now add new reference
            mock_filenames.return_value = ([str(a)], "*.*")
            self._data_connection.show_add_file_references_dialog()
            self.assertEqual(5, mock_filenames.call_count)
            self.assertEqual(2, len(self._data_connection.file_references))
            self.assertEqual(2, self._ref_model.rowCount(self._ref_model.index(0, 0)))
            self.assertEqual(str(b), self._ref_model.index(0, 0, self._ref_model.index(0, 0)).data())
            self.assertEqual(str(a), self._ref_model.index(1, 0, self._ref_model.index(0, 0)).data())

    def test_add_db_references(self):
        with mock.patch(
            "spine_items.data_connection.data_connection.UrlSelectorDialog.exec"
        ) as url_selector_exec, mock.patch(
            "spine_items.data_connection.data_connection.UrlSelectorDialog.url_dict"
        ) as url_selector_url_dict:
            # Add nothing
            url_selector_exec.return_value = QDialog.DialogCode.Rejected
            self._data_connection.show_add_db_reference_dialog()
            self.assertEqual(1, url_selector_exec.call_count)
            self.assertFalse(self._data_connection.has_db_references())
            self.assertEqual(0, self._ref_model.rowCount(self._ref_model.index(1, 0)))
            # Add one url
            url_selector_exec.return_value = QDialog.DialogCode.Accepted
            url_selector_url_dict.return_value = {
                "dialect": "mysql",
                "host": "host",
                "port": 3306,
                "database": "db",
                "username": "randy",
                "password": "creamfraiche",
            }
            self._data_connection.show_add_db_reference_dialog()
            self.assertEqual(2, url_selector_exec.call_count)
            self.assertEqual(1, len(list(self._data_connection.db_reference_iter())))
            self.assertEqual(1, self._ref_model.rowCount(self._ref_model.index(1, 0)))
            # Add same url with different username and password (should not be added)
            url_selector_url_dict.return_value = {
                "dialect": "mysql",
                "host": "host",
                "port": 3306,
                "database": "db",
                "username": "scott",
                "password": "tiger",
            }
            self._data_connection.show_add_db_reference_dialog()
            self.assertEqual(3, url_selector_exec.call_count)
            self.assertEqual(1, len(list(self._data_connection.db_reference_iter())))
            self.assertEqual(1, self._ref_model.rowCount(self._ref_model.index(1, 0)))

    def test_remove_references(self):
        temp_dir = Path(self._temp_dir.name, "references")
        temp_dir.mkdir()
        with mock.patch(
            "spine_items.data_connection.data_connection.QFileDialog.getOpenFileNames"
        ) as mock_filenames, mock.patch.object(
            self._data_connection._properties_ui.treeView_dc_references, "selectedIndexes"
        ) as mock_selected_indexes, mock.patch(
            "spine_items.data_connection.data_connection.UrlSelectorDialog.exec"
        ) as url_selector_exec, mock.patch(
            "spine_items.data_connection.data_connection.UrlSelectorDialog.url_dict"
        ) as url_selector_url_dict:
            a = Path(temp_dir, "a.txt")
            a.touch()
            b = Path(temp_dir, "b.txt")
            b.touch()
            c = Path(temp_dir, "c.txt")  # Note. This file is not actually created
            d = Path(temp_dir, "d.txt")  # Note. This file is not actually created
            self.assertTrue(os.path.isfile(str(a)) and os.path.isfile(str(b)))  # existing files
            self.assertFalse(os.path.isfile(str(c)))  # non-existing file
            self.assertFalse(os.path.isfile(str(d)))  # non-existing file
            # First add a couple of files as refs
            mock_filenames.return_value = ([str(a), str(b)], "*.*")
            self._data_connection.show_add_file_references_dialog()
            self.assertEqual(1, mock_filenames.call_count)
            self.assertEqual(2, len(self._data_connection.file_references))
            self.assertEqual(2, self._ref_model.rowCount(self._ref_model.index(0, 0)))
            # Second add a couple of dbs as refs
            url_selector_exec.return_value = QDialog.DialogCode.Accepted
            url_selector_url_dict.return_value = {
                "dialect": "mysql",
                "username": "scott",
                "password": "tiger",
                "host": "host",
                "port": 3306,
                "database": "db",
            }
            self._data_connection.show_add_db_reference_dialog()
            url_selector_url_dict.return_value = {
                "dialect": "mysql",
                "username": "randy",
                "password": "creamfraiche",
                "host": "host",
                "port": 3307,
                "database": "db",
            }
            self._data_connection.show_add_db_reference_dialog()
            self.assertEqual(2, url_selector_exec.call_count)
            self.assertEqual(2, len(list(self._data_connection.db_reference_iter())))
            self.assertEqual(2, self._ref_model.rowCount(self._ref_model.index(1, 0)))
            # Test with no indexes selected
            mock_selected_indexes.return_value = []
            self._data_connection.remove_references()
            self.assertEqual(1, mock_selected_indexes.call_count)
            self.assertEqual(2, len(self._data_connection.file_references))
            self.assertEqual(2, self._ref_model.rowCount(self._ref_model.index(0, 0)))
            # Set one file selected and remove it
            a_index = self._ref_model.index(0, 0, self._ref_model.index(0, 0))
            mock_selected_indexes.return_value = [a_index]
            self._data_connection.remove_references()
            self.assertEqual(2, mock_selected_indexes.call_count)
            self.assertEqual(1, len(self._data_connection.file_references))
            self.assertEqual(1, self._ref_model.rowCount(self._ref_model.index(0, 0)))
            # Check that the remaining file is the one that's supposed to be there
            self.assertEqual([str(b)], self._data_connection.file_references)
            self.assertEqual(str(b), self._ref_model.item(0).child(0).data(Qt.ItemDataRole.DisplayRole))
            # Set one db selected and remove it
            db1_index = self._ref_model.index(0, 0, self._ref_model.index(1, 0))
            mock_selected_indexes.return_value = [db1_index]
            self._data_connection.remove_references()
            self.assertEqual(3, mock_selected_indexes.call_count)
            self.assertEqual(1, len(list(self._data_connection.db_reference_iter())))
            self.assertEqual(1, self._ref_model.rowCount(self._ref_model.index(1, 0)))
            # Check that the remaining db is the one that's supposed to be there
            self.assertEqual(
                [
                    {
                        "dialect": "mysql",
                        "host": "host",
                        "port": 3307,
                        "database": "db",
                        "username": "randy",
                        "password": "creamfraiche",
                    }
                ],
                list(self._data_connection.db_reference_iter()),
            )
            self.assertEqual(
                "mysql+pymysql://host:3307/db", self._ref_model.item(1).child(0).data(Qt.ItemDataRole.DisplayRole)
            )
            # Now remove the remaining file and db
            b_index = self._ref_model.index(0, 0, self._ref_model.index(0, 0))
            db2_index = self._ref_model.index(0, 0, self._ref_model.index(1, 0))
            mock_selected_indexes.return_value = [b_index, db2_index]
            self._data_connection.remove_references()
            self.assertEqual(4, mock_selected_indexes.call_count)
            self.assertEqual(0, len(self._data_connection.file_references))
            self.assertEqual(0, self._ref_model.rowCount(self._ref_model.index(0, 0)))
            self.assertEqual(0, len(list(self._data_connection.db_reference_iter())))
            self.assertEqual(0, self._ref_model.rowCount(self._ref_model.index(1, 0)))
            # Add a and b back and the two non-existing files as well
            # Select non-existing file c and remove it
            mock_filenames.return_value = ([str(a), str(b), str(c), str(d)], "*.*")
            self._data_connection.show_add_file_references_dialog()
            self.assertEqual(2, mock_filenames.call_count)
            self.assertEqual(2, len(self._data_connection.file_references))
            self.assertEqual(2, self._ref_model.rowCount(self._ref_model.index(0, 0)))
            # Check that the two remaining items are the ones that are supposed to be there
            self.assertEqual(str(a), self._data_connection.file_references[0])
            self.assertEqual(str(a), self._ref_model.item(0).child(0).data(Qt.ItemDataRole.DisplayRole))
            self.assertEqual(str(b), self._data_connection.file_references[1])
            self.assertEqual(str(b), self._ref_model.item(0).child(1).data(Qt.ItemDataRole.DisplayRole))
            # Now select the two remaining ones and remove them
            a_index = self._ref_model.index(0, 0, self._ref_model.index(0, 0))
            b_index = self._ref_model.index(1, 0, self._ref_model.index(0, 0))
            mock_selected_indexes.return_value = [a_index, b_index]
            self._data_connection.remove_references()
            self.assertEqual(5, mock_selected_indexes.call_count)
            self.assertEqual(0, len(self._data_connection.file_references))
            self.assertEqual(0, self._ref_model.rowCount(self._ref_model.index(0, 0)))
            # Add a, b, c, and d back Select all and remove.
            mock_filenames.return_value = ([str(a), str(b), str(c), str(d)], "*.*")
            self._data_connection.show_add_file_references_dialog()
            self.assertEqual(3, mock_filenames.call_count)
            a_index = self._ref_model.index(0, 0, self._ref_model.index(0, 0))
            b_index = self._ref_model.index(1, 0, self._ref_model.index(0, 0))
            mock_selected_indexes.return_value = [a_index, b_index]
            self._data_connection.remove_references()
            self.assertEqual(6, mock_selected_indexes.call_count)
            self.assertEqual(0, len(self._data_connection.file_references))
            self.assertEqual(0, self._ref_model.rowCount(self._ref_model.index(0, 0)))

    def test_remove_references_with_del_key(self):
        temp_dir = Path(self._temp_dir.name, "references")
        temp_dir.mkdir()
        with mock.patch(
            "spine_items.data_connection.data_connection.QFileDialog.getOpenFileNames"
        ) as mock_filenames, mock.patch(
            "spine_items.data_connection.data_connection.UrlSelectorDialog.exec"
        ) as url_selector_exec, mock.patch(
            "spine_items.data_connection.data_connection.UrlSelectorDialog.url", new_callable=mock.PropertyMock
        ) as url_selector_url:
            a = Path(temp_dir, "a.txt")
            a.touch()
            b = Path(temp_dir, "b.txt")
            b.touch()
            self.assertTrue(os.path.isfile(str(a)) and os.path.isfile(str(b)))  # existing files
            self._data_connection.restore_selections()
            self._data_connection._connect_signals()
            # First add a couple of files as refs
            mock_filenames.return_value = ([str(a), str(b)], "*.*")
            self._data_connection.show_add_file_references_dialog()
            self.assertEqual(1, mock_filenames.call_count)
            self.assertEqual(2, len(self._data_connection.file_references))
            self.assertEqual(2, self._ref_model.rowCount(self._ref_model.index(0, 0)))
            # Second add a couple of dbs as refs
            url_selector_url.return_value = "mysql://scott:tiger@host:3306/db"
            self._data_connection.show_add_db_reference_dialog()
            indexes = self._data_connection._properties_ui.treeView_dc_references.selectedIndexes()
            self.assertTrue(len(indexes) == 0)
            # Set index selected
            file_ref_root_index = self._ref_model.index(0, 0)
            ref_index = self._ref_model.index(0, 0, file_ref_root_index)
            self._data_connection._properties_ui.treeView_dc_references.selectionModel().select(
                ref_index, QItemSelectionModel.Select
            )
            indexes = self._data_connection._properties_ui.treeView_dc_references.selectedIndexes()
            self.assertTrue(len(indexes) == 1)
            self._data_connection._properties_ui.treeView_dc_references.del_key_pressed.emit()
            self.assertEqual(1, len(self._data_connection.file_references))
            # Remove remaining two simultaneously by selecting bith and removing them with delete key
            file_ref_index = self._ref_model.index(0, 0, self._ref_model.index(0, 0))
            db_ref_index = self._ref_model.index(0, 0, self._ref_model.index(1, 0))
            self._data_connection._properties_ui.treeView_dc_references.selectionModel().select(
                file_ref_index, QItemSelectionModel.Select
            )
            self._data_connection._properties_ui.treeView_dc_references.selectionModel().select(
                db_ref_index, QItemSelectionModel.Select
            )
            indexes = self._data_connection._properties_ui.treeView_dc_references.selectedIndexes()
            self._data_connection._properties_ui.treeView_dc_references.del_key_pressed.emit()
            self.assertEqual(0, len(self._data_connection.file_references))
            self.assertEqual(0, len(list(self._data_connection.db_reference_iter())))

    def test_renaming_file_marks_its_reference_as_missing(self):
        temp_dir = Path(self._temp_dir.name, "references")
        temp_dir.mkdir()
        a = Path(temp_dir, "a.txt")
        a.touch()
        with mock.patch("spine_items.data_connection.data_connection.QFileDialog.getOpenFileNames") as mock_filenames:
            mock_filenames.return_value = ([str(a)], "*.*")
            self._data_connection.show_add_file_references_dialog()
        renamed_file = a.parent / "renamed.txt"
        with signal_waiter(self._data_connection.file_system_watcher.file_renamed) as waiter:
            a.rename(renamed_file)
            waiter.wait()
        index = self._ref_model.index(0, 0, self._ref_model.index(0, 0))
        self.assertEqual(index.data(), str(a))
        self.assertTrue(index.data(Qt.ItemDataRole.UserRole + 2))
        self.assertEqual(self._data_connection.file_references, [str(a)])

    def test_deleting_file_marks_its_reference_as_missing(self):
        temp_dir = Path(self._temp_dir.name, "references")
        temp_dir.mkdir()
        a = Path(temp_dir, "a.txt")
        a.touch()
        with mock.patch("spine_items.data_connection.data_connection.QFileDialog.getOpenFileNames") as mock_filenames:
            mock_filenames.return_value = ([str(a)], "*.*")
            self._data_connection.show_add_file_references_dialog()
        with signal_waiter(self._data_connection.file_system_watcher.file_removed) as waiter:
            a.unlink()
            waiter.wait()
        index = self._ref_model.index(0, 0, self._ref_model.index(0, 0))
        self.assertEqual(index.data(), str(a))
        self.assertTrue(index.data(Qt.ItemDataRole.UserRole + 2))
        self.assertEqual(self._data_connection.file_references, [str(a)])

    def test_copy_reference_to_project(self):
        temp_dir = Path(self._temp_dir.name, "references")
        temp_dir.mkdir()
        a = Path(temp_dir, "a.txt")
        a.touch()
        with mock.patch("spine_items.data_connection.data_connection.QFileDialog.getOpenFileNames") as mock_filenames:
            mock_filenames.return_value = ([str(a)], "*.*")
            self._data_connection.show_add_file_references_dialog()
        self._data_connection.restore_selections()
        ref_root_index = self._ref_model.index(0, 0)
        ref_index = self._ref_model.index(0, 0, ref_root_index)
        properties_ui = self._toolbox.project_item_properties_ui(self._data_connection.item_type())
        properties_ui.treeView_dc_references.selectionModel().select(ref_index, QItemSelectionModel.ClearAndSelect)
        with signal_waiter(self._data_connection.file_system_watcher.file_added) as waiter:
            self._data_connection.copy_to_project()
            waiter.wait()
        self.assertEqual(self._ref_model.rowCount(ref_root_index), 0)
        self.assertTrue(Path(self._toolbox.project().items_dir, "dc", "a.txt").exists())
        self.assertEqual(self._data_connection.data_model.rowCount(), 1)
        index = self._data_connection.data_model.index(0, 0)
        self.assertEqual(index.data(), "a.txt")
        self.assertEqual(
            index.data(Qt.ItemDataRole.UserRole + 1), os.path.join(self._toolbox.project().items_dir, "dc", "a.txt")
        )

    def test_create_data_file(self):
        with mock.patch("spine_items.data_connection.data_connection.QInputDialog") as mock_input_dialog:
            mock_input_dialog.getText.return_value = ["data.csv"]
            with signal_waiter(self._data_connection.file_system_watcher.file_added) as waiter:
                self._data_connection.make_new_file()
                waiter.wait()
        model = self._data_connection.data_model
        self.assertEqual(model.rowCount(), 1)
        index = model.index(0, 0)
        self.assertEqual(index.data(), "data.csv")
        self.assertEqual(
            index.data(Qt.ItemDataRole.UserRole + 1), os.path.join(self._toolbox.project().items_dir, "dc", "data.csv")
        )

    def test_deleting_data_file_removes_it_from_dc(self):
        file_a = Path(self._data_connection.data_dir) / "data.dat"
        with signal_waiter(self._data_connection.file_system_watcher.file_added) as waiter:
            file_a.touch()
            waiter.wait()
        model = self._data_connection.data_model
        self.assertEqual(model.rowCount(), 1)
        index = model.index(0, 0)
        self.assertEqual(index.data(), "data.dat")
        self.assertEqual(index.data(Qt.ItemDataRole.UserRole + 1), str(file_a))
        with signal_waiter(self._data_connection.file_system_watcher.file_removed) as waiter:
            file_a.unlink()
            waiter.wait()
        self.assertEqual(model.rowCount(), 0)

    def test_renaming_data_file_renames_it_in_dc_as_well(self):
        file_a = Path(self._data_connection.data_dir) / "data.dat"
        with signal_waiter(self._data_connection.file_system_watcher.file_added) as waiter:
            file_a.touch()
            waiter.wait()
        model = self._data_connection.data_model
        self.assertEqual(model.rowCount(), 1)
        index = model.index(0, 0)
        self.assertEqual(index.data(), "data.dat")
        self.assertEqual(index.data(Qt.ItemDataRole.UserRole + 1), str(file_a))
        renamed = file_a.parent / "sata.txt"
        with signal_waiter(self._data_connection.file_system_watcher.file_renamed) as waiter:
            file_a.rename(renamed)
            waiter.wait()
        self.assertEqual(model.rowCount(), 1)
        index = model.index(0, 0)
        self.assertEqual(index.data(), "sata.txt")
        self.assertEqual(index.data(Qt.ItemDataRole.UserRole + 1), str(renamed))

    def test_item_dict(self):
        """Tests Item dictionary creation."""
        d = self._data_connection.item_dict()
        a = ["type", "description", "x", "y", "file_references", "db_references", "db_credentials"]
        for k in a:
            self.assertTrue(k in d, f"Key '{k}' not in dict {d}")

    def test_deserialization_with_remote_db_reference(self):
        with mock.patch(
            "spine_items.data_connection.data_connection.UrlSelectorDialog.exec"
        ) as url_selector_exec, mock.patch(
            "spine_items.data_connection.data_connection.UrlSelectorDialog.url_dict"
        ) as url_selector_url_dict:
            # Add nothing
            url_selector_exec.return_value = QDialog.DialogCode.Accepted
            url_selector_url_dict.return_value = {
                "dialect": "mysql",
                "host": "post.com",
                "port": 3306,
                "database": "db",
                "username": "randy",
                "password": "creamfraiche",
            }
            self._data_connection.show_add_db_reference_dialog()
        item_dict = self._data_connection.item_dict()
        self.assertEqual(len(item_dict["db_references"]), 1)
        self.assertNotIn("username", item_dict["db_references"][0])
        self.assertNotIn("password", item_dict["db_references"][0])
        deserialized = DataConnection.from_dict("deserialized", item_dict, self._toolbox, self._toolbox.project())
        self.assertTrue(deserialized.has_db_references())
        self.assertEqual(
            list(deserialized.db_reference_iter()),
            [
                {
                    "dialect": "mysql",
                    "host": "post.com",
                    "port": 3306,
                    "database": "db",
                    "username": "randy",
                    "password": "creamfraiche",
                }
            ],
        )

    def test_deserialization_with_sqlite_db_reference_in_project_directory(self):
        db_path = Path(self._temp_dir.name, "db.sqlite")
        create_new_spine_database("sqlite:///" + str(db_path))
        with mock.patch(
            "spine_items.data_connection.data_connection.UrlSelectorDialog.exec"
        ) as url_selector_exec, mock.patch(
            "spine_items.data_connection.data_connection.UrlSelectorDialog.url_dict"
        ) as url_selector_url_dict:
            # Add nothing
            url_selector_exec.return_value = QDialog.DialogCode.Accepted
            url_selector_url_dict.return_value = {
                "dialect": "sqlite",
                "host": None,
                "port": None,
                "database": str(db_path),
                "username": None,
                "password": None,
            }
            self._data_connection.show_add_db_reference_dialog()
        item_dict = self._data_connection.item_dict()
        self.assertEqual(len(item_dict["db_references"]), 1)
        self.assertNotIn("username", item_dict["db_references"][0])
        self.assertNotIn("password", item_dict["db_references"][0])
        deserialized = DataConnection.from_dict("deserialized", item_dict, self._toolbox, self._toolbox.project())
        self.assertTrue(deserialized.has_db_references())
        self.assertEqual(
            list(deserialized.db_reference_iter()),
            [
                {
                    "dialect": "sqlite",
                    "host": None,
                    "port": None,
                    "database": str(db_path),
                    "username": None,
                    "password": None,
                }
            ],
        )

    def test_sqlite_db_reference_is_marked_missing_when_db_file_is_renamed(self):
        db_path = Path(self._temp_dir.name, "db.sqlite")
        create_new_spine_database("sqlite:///" + str(db_path))
        with mock.patch(
            "spine_items.data_connection.data_connection.UrlSelectorDialog.exec"
        ) as url_selector_exec, mock.patch(
            "spine_items.data_connection.data_connection.UrlSelectorDialog.url_dict"
        ) as url_selector_url_dict:
            # Add nothing
            url_selector_exec.return_value = QDialog.DialogCode.Accepted
            url_selector_url_dict.return_value = {
                "dialect": "sqlite",
                "host": None,
                "port": None,
                "database": str(db_path),
                "username": None,
                "password": None,
            }
            self._data_connection.show_add_db_reference_dialog()
        while self._data_connection._database_validator.is_busy():
            QApplication.processEvents()
        self.assertEqual(
            list(self._data_connection.db_reference_iter()),
            [
                {
                    "dialect": "sqlite",
                    "host": None,
                    "port": None,
                    "database": str(db_path),
                    "username": None,
                    "password": None,
                }
            ],
        )
        with signal_waiter(self._data_connection.file_system_watcher.file_renamed) as waiter:
            db_path.rename(db_path.parent / "renamed.sqlite")
            waiter.wait()
        self.assertTrue(self._data_connection._db_ref_root.child(0, 0).data(_Role.MISSING))

    def test_refreshing_missing_sqlite_reference_resurrects_it(self):
        db_path = Path(self._temp_dir.name, "db.sqlite")
        create_new_spine_database("sqlite:///" + str(db_path))
        with mock.patch(
            "spine_items.data_connection.data_connection.UrlSelectorDialog.exec"
        ) as url_selector_exec, mock.patch(
            "spine_items.data_connection.data_connection.UrlSelectorDialog.url_dict"
        ) as url_selector_url_dict:
            # Add nothing
            url_selector_exec.return_value = QDialog.DialogCode.Accepted
            url_selector_url_dict.return_value = {
                "dialect": "sqlite",
                "host": None,
                "port": None,
                "database": str(db_path),
                "username": None,
                "password": None,
            }
            self._data_connection.show_add_db_reference_dialog()
        while self._data_connection._database_validator.is_busy():
            QApplication.processEvents()
        self.assertEqual(
            list(self._data_connection.db_reference_iter()),
            [
                {
                    "dialect": "sqlite",
                    "host": None,
                    "port": None,
                    "database": str(db_path),
                    "username": None,
                    "password": None,
                }
            ],
        )
        with signal_waiter(self._data_connection.file_system_watcher.file_renamed) as waiter:
            renamed_path = db_path.rename(db_path.parent / "renamed.sqlite")
            waiter.wait()
        self.assertTrue(self._data_connection._db_ref_root.child(0, 0).data(_Role.MISSING))
        with signal_waiter(self._data_connection.file_system_watcher.file_renamed) as waiter:
            renamed_path.rename(db_path)
            waiter.wait()
        self.assertTrue(self._data_connection._db_ref_root.child(0, 0).data(_Role.MISSING))
        self._data_connection.restore_selections()
        self._data_connection._connect_signals()
        db_ref_root_index = self._ref_model.index(1, 0)
        ref_index = self._ref_model.index(0, 0, db_ref_root_index)
        self._data_connection._properties_ui.treeView_dc_references.selectionModel().select(
            ref_index, QItemSelectionModel.Select
        )
        self._data_connection.refresh_references()
        while self._data_connection._database_validator.is_busy():
            QApplication.processEvents()
        self.assertFalse(self._data_connection._db_ref_root.child(0, 0).data(_Role.MISSING))

    def test_broken_sqlite_url_marks_the_reference_missing(self):
        db_path = Path(self._temp_dir.name, "db.sqlite")
        with mock.patch(
            "spine_items.data_connection.data_connection.UrlSelectorDialog.exec"
        ) as url_selector_exec, mock.patch(
            "spine_items.data_connection.data_connection.UrlSelectorDialog.url_dict"
        ) as url_selector_url_dict:
            # Add nothing
            url_selector_exec.return_value = QDialog.DialogCode.Accepted
            url_selector_url_dict.return_value = {
                "dialect": "sqlite",
                "host": None,
                "port": None,
                "database": str(db_path),
                "username": None,
                "password": None,
            }
            self._data_connection.show_add_db_reference_dialog()
        while self._data_connection._database_validator.is_busy():
            QApplication.processEvents()
        self.assertEqual(
            list(self._data_connection.db_reference_iter()),
            [
                {
                    "dialect": "sqlite",
                    "host": None,
                    "port": None,
                    "database": str(db_path),
                    "username": None,
                    "password": None,
                }
            ],
        )
        self.assertTrue(self._data_connection._db_ref_root.child(0, 0).data(_Role.MISSING))

    def test_notify_destination(self):
        self._data_connection.logger.msg = MagicMock()
        self._data_connection.logger.msg_warning = MagicMock()
        source_item = NonCallableMagicMock()
        source_item.name = "source name"
        source_item.item_type = MagicMock(return_value="Importer")
        self._data_connection.notify_destination(source_item)
        self._data_connection.logger.msg.emit.assert_called_with("Link established")
        source_item.item_type = MagicMock(return_value="Data Store")
        self._data_connection.notify_destination(source_item)
        self._data_connection.logger.msg.emit.assert_called_with("Link established")
        source_item.item_type = MagicMock(return_value="Tool")
        self._data_connection.notify_destination(source_item)
        self._data_connection.logger.msg.emit.assert_called_with(
            "Link established. Tool <b>source name</b> output files"
            " will be passed as references to item <b>DC</b> after execution."
        )
        source_item.item_type = MagicMock(return_value="View")
        self._data_connection.notify_destination(source_item)
        self._data_connection.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a <b>View</b> and"
            " a <b>Data Connection</b> has not been implemented yet."
        )

    def test_rename(self):
        """Tests renaming a Data Connection."""
        self._data_connection.activate()
        expected_name = "ABC"
        expected_short_name = "abc"
        expected_data_dir = os.path.join(self._toolbox.project().items_dir, expected_short_name)
        self._data_connection.rename(expected_name, "")
        # Check name
        self.assertEqual(expected_name, self._data_connection.name)  # item name
        self.assertEqual(expected_name, self._data_connection.get_icon().name())
        # Check data_dir
        self.assertEqual(expected_data_dir, self._data_connection.data_dir)  # Check data dir
        # Check that file_system_watcher has one path (new data_dir)
        watched_dirs = self._data_connection.file_system_watcher.directories()
        self.assertEqual(1, len(watched_dirs))
        self.assertEqual(self._data_connection.data_dir, watched_dirs[0])


class TestDataConnectionWithInitialDataFile(unittest.TestCase):
    def setUp(self):
        """Set up."""
        self.toolbox = create_mock_toolbox()
        factory = DataConnectionFactory()
        item_dict = {"type": "Data Connection", "description": "", "references": [], "x": 0, "y": 0}
        self._temp_dir = TemporaryDirectory()
        self.project = create_mock_project(self._temp_dir.name)
        self.toolbox.project.return_value = self.project
        self._item_dir = Path(self.project.items_dir, "dc")
        self._item_dir.mkdir(parents=True)
        self._data_file_path = self._item_dir / "data.csv"
        self._data_file_path.touch()
        self.data_connection = factory.make_item("DC", item_dict, self.toolbox, self.project)
        self._properties_tab = mock_finish_project_item_construction(factory, self.data_connection, self.toolbox)

    def tearDown(self):
        self.data_connection.tear_down()
        self._temp_dir.cleanup()

    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def test_data_file_in_list(self):
        model = self.data_connection.data_model
        self.assertEqual(model.rowCount(), 1)
        index = model.index(0, 0)
        self.assertEqual(index.data(), "data.csv")
        self.assertEqual(index.data(Qt.ItemDataRole.UserRole + 1), str(self._data_file_path))

    def test_remove_data_file(self):
        self.data_connection.restore_selections()
        index = self.data_connection.data_model.index(0, 0)
        self._properties_tab.ui.treeView_dc_data.selectionModel().select(index, QItemSelectionModel.ClearAndSelect)
        with mock.patch("spine_items.data_connection.data_connection.QMessageBox") as mock_message_box:
            mock_message_box.exec.return_value = QMessageBox.StandardButton.Ok
            with signal_waiter(self.data_connection.file_system_watcher.file_removed) as waiter:
                self.data_connection.remove_files()
                waiter.wait()
        model = self.data_connection.data_model
        self.assertEqual(model.rowCount(), 0)

    def test_rename_data_file(self):
        with signal_waiter(self.data_connection.file_system_watcher.file_renamed) as waiter:
            self._data_file_path.rename(self._item_dir / "renamed.dat")
            waiter.wait()
        model = self.data_connection.data_model
        self.assertEqual(model.rowCount(), 1)
        index = model.index(0, 0)
        self.assertEqual(index.data(), "renamed.dat")
        self.assertEqual(index.data(Qt.ItemDataRole.UserRole + 1), str(self._item_dir / "renamed.dat"))


class TestDataConnectionWithInvalidFileReference(unittest.TestCase):
    def setUp(self):
        """Set up."""
        self._temp_dir = TemporaryDirectory()
        self._non_existent_path = os.path.join(self._temp_dir.name, "file.dat")
        self.toolbox = create_mock_toolbox()
        factory = DataConnectionFactory()
        item_dict = {
            "type": "Data Connection",
            "description": "",
            "file_references": [self._non_existent_path],
            "x": 0,
            "y": 0,
        }
        self.project = create_mock_project(self._temp_dir.name)
        self.toolbox.project.return_value = self.project
        self.data_connection = factory.make_item("DC", item_dict, self.toolbox, self.project)
        self.project.get_item.return_value = self.data_connection
        self._properties_tab = mock_finish_project_item_construction(factory, self.data_connection, self.toolbox)
        self.ref_model = self.data_connection.reference_model

    def tearDown(self):
        self.data_connection.tear_down()
        self._temp_dir.cleanup()

    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def test_add_file_references(self):
        temp_dir = Path(self._temp_dir.name, "references")
        temp_dir.mkdir()
        with mock.patch("spine_items.data_connection.data_connection.QFileDialog.getOpenFileNames") as mock_filenames:
            a = Path(temp_dir, "a.txt")
            a.touch()
            mock_filenames.return_value = ([str(a)], "*.*")
            self.data_connection.show_add_file_references_dialog()
            self.assertEqual(2, len(self.data_connection.file_references))
            self.assertEqual(2, self.ref_model.rowCount(self.ref_model.index(0, 0)))
            self.assertEqual(self._non_existent_path, self.ref_model.index(0, 0, self.ref_model.index(0, 0)).data())
            self.assertEqual(str(a), self.ref_model.index(1, 0, self.ref_model.index(0, 0)).data())

    def test_refresh_file_reference(self):
        root_index = self.ref_model.index(0, 0)
        reference_index = self.ref_model.index(0, 0, root_index)
        self.assertEqual(reference_index.data(Qt.ItemDataRole.ToolTipRole), "The file is missing.")
        Path(self._non_existent_path).touch()
        self.data_connection.restore_selections()
        self._properties_tab.ui.treeView_dc_references.selectionModel().select(
            reference_index, QItemSelectionModel.ClearAndSelect
        )
        self.data_connection.refresh_references()
        self.assertIsNone(reference_index.data(Qt.ItemDataRole.ToolTipRole), "The file is missing.")
        self.project.notify_resource_changes_to_successors.assert_called_once_with(self.data_connection)


if __name__ == "__main__":
    unittest.main()
