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
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock, NonCallableMagicMock
from PySide6.QtCore import QItemSelectionModel
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox
import pytest
from spine_engine.project_item.project_item_resource import file_resource_in_pack
from spine_engine.utils.serialization import serialize_path
from spine_items.data_connection.data_connection import DataConnection, _Role
from spine_items.data_connection.data_connection_factory import DataConnectionFactory
from spine_items.data_connection.item_info import ItemInfo
from spine_items.data_connection.utils import FilePattern
from spine_items.utils import UrlDict, convert_url_to_safe_string
from spine_items.widgets import UrlSelectorDialog
from spinedb_api import create_new_spine_database
from spinetoolbox.helpers import signal_waiter

FILE_REF_ROOT_ROW = 0
FILE_PATTERN_ROOT_ROW = 1
DIRECTORY_ROOT_ROW = 2
URL_ROOT_ROW = 3


@pytest.fixture
def dc_factory(spine_toolbox_with_project):
    class Factory:
        def __call__(self, item_dict_extras):
            factory = DataConnectionFactory()
            item_dict = {"type": "Data Connection", "description": "", "x": 0, "y": 0, **item_dict_extras}
            project = spine_toolbox_with_project.project()
            data_connection: DataConnection = factory.make_item("DC", item_dict, spine_toolbox_with_project, project)
            project.add_item(data_connection)
            return data_connection

    return Factory()


@pytest.fixture
def data_connection(dc_factory):
    return dc_factory({})


@pytest.fixture
def non_existent_path(spine_toolbox_with_project):
    return Path(spine_toolbox_with_project.project().project_dir, "file.dat")


@pytest.fixture
def data_file(spine_toolbox_with_project):
    project = spine_toolbox_with_project.project()
    item_dir = Path(project.items_dir, "dc")
    item_dir.mkdir(parents=True)
    data_file_path = item_dir / "data.csv"
    data_file_path.touch()
    return data_file_path


class TestDataConnection:
    def test_item_type(self):
        assert DataConnection.item_type() == ItemInfo.item_type()

    def test_add_file_references(self, data_connection, tmp_path):
        temp_dir = tmp_path / "references"
        temp_dir.mkdir()
        ref_model = data_connection.reference_model
        with mock.patch("spine_items.data_connection.data_connection.QFileDialog.getOpenFileNames") as mock_filenames:
            a = Path(temp_dir, "a.txt")
            a.touch()
            b = Path(temp_dir, "b.txt")
            b.touch()
            c = Path(temp_dir, "c.txt")  # Note. Does not exist
            file_ref_root_index = ref_model.index(FILE_REF_ROOT_ROW, 0)
            # Add nothing
            mock_filenames.return_value = ([], "*.*")
            data_connection.show_add_file_references_dialog()
            assert 1 == mock_filenames.call_count
            assert 0 == len(data_connection.file_references)
            assert 0 == ref_model.rowCount(file_ref_root_index)
            # Add one file
            mock_filenames.return_value = ([str(a)], "*.*")
            data_connection.show_add_file_references_dialog()
            assert 2 == mock_filenames.call_count
            assert 1 == len(data_connection.file_references)
            file_ref_root_index = ref_model.index(FILE_REF_ROOT_ROW, 0)
            assert 1 == ref_model.rowCount(file_ref_root_index)
            assert str(a) == ref_model.index(0, 0, file_ref_root_index).data()
            # Try to add a path that has already been added
            data_connection.show_add_file_references_dialog()
            assert 3 == mock_filenames.call_count
            assert 1 == len(data_connection.file_references)
            file_ref_root_index = ref_model.index(FILE_REF_ROOT_ROW, 0)
            assert 1 == ref_model.rowCount(file_ref_root_index)
            assert str(a) == ref_model.index(0, 0, file_ref_root_index).data()
            data_connection.file_references = []
            data_connection.populate_reference_list([], [], [])
            # Add two references (the other one is non-existing)
            # Note: non-existing files cannot be added with the toolbox but this tests a situation when
            # project.json file has references to files that do not exist anymore and user tries to add a
            # new reference to a Data Connection that contains non-existing file references
            mock_filenames.return_value = ([str(b), str(c)], "*.*")
            data_connection.show_add_file_references_dialog()
            assert 4 == mock_filenames.call_count
            assert 1 == len(data_connection.file_references)
            file_ref_root_index = ref_model.index(FILE_REF_ROOT_ROW, 0)
            assert 1 == ref_model.rowCount(file_ref_root_index)
            assert str(b) == ref_model.index(0, 0, file_ref_root_index).data()
            # Now add new reference
            mock_filenames.return_value = ([str(a)], "*.*")
            data_connection.show_add_file_references_dialog()
            assert 5 == mock_filenames.call_count
            assert 2 == len(data_connection.file_references)
            assert 2 == ref_model.rowCount(file_ref_root_index)
            file_ref_root_index = ref_model.index(FILE_REF_ROOT_ROW, 0)
            assert str(b) == ref_model.index(0, 0, file_ref_root_index).data()
            assert str(a) == ref_model.index(1, 0, file_ref_root_index).data()

    def test_cancel_add_file_pattern_dialog(self, data_connection):
        with mock.patch("spine_items.data_connection.data_connection.FilePatternDialog") as mock_dialog_init:
            mock_dialog = mock.MagicMock()
            mock_dialog_init.return_value = mock_dialog
            mock_dialog.exec_.return_value = QDialog.DialogCode.Rejected
            data_connection.show_add_file_pattern_dialog()
            mock_dialog.exec_.assert_called_once()
        assert list(data_connection.file_pattern_iter()) == []

    def test_add_file_pattern_via_dialog(self, data_connection, tmp_path):
        with mock.patch("spine_items.data_connection.data_connection.FilePatternDialog") as mock_dialog_init:
            mock_dialog = mock.MagicMock()
            mock_dialog_init.return_value = mock_dialog
            mock_dialog.exec_.return_value = QDialog.DialogCode.Accepted
            mock_dialog.file_pattern.return_value = FilePattern(tmp_path / "pattern_dir", "*.txt")
            data_connection.show_add_file_pattern_dialog()
            mock_dialog.exec_.assert_called_once()
        assert list(data_connection.file_pattern_iter()) == [FilePattern(tmp_path / "pattern_dir", "*.txt")]

    def test_undo_adding_file_pattern(self, data_connection, spine_toolbox_with_project, tmp_path):
        with mock.patch("spine_items.data_connection.data_connection.FilePatternDialog") as mock_dialog_init:
            mock_dialog = mock.MagicMock()
            mock_dialog_init.return_value = mock_dialog
            mock_dialog.exec_.return_value = QDialog.DialogCode.Accepted
            mock_dialog.file_pattern.return_value = FilePattern(tmp_path / "pattern_dir", "*.txt")
            data_connection.show_add_file_pattern_dialog()
        assert list(data_connection.file_pattern_iter()) == [FilePattern(tmp_path / "pattern_dir", "*.txt")]
        spine_toolbox_with_project.undo_stack.undo()
        assert list(data_connection.file_pattern_iter()) == []

    def test_cancel_add_directory_reference_dialog(self, data_connection):
        with mock.patch(
            "spine_items.data_connection.data_connection.QFileDialog.getExistingDirectory"
        ) as mock_directory_dialog:
            mock_directory_dialog.return_value = ""
            data_connection.show_add_directory_reference_dialog()
            mock_directory_dialog.assert_called_once()
            assert list(data_connection.directory_iter()) == []

    def test_add_directory_reference_via_dialog(self, data_connection, tmp_path):
        temp_dir = tmp_path / "target_dir"
        temp_dir.mkdir()
        with mock.patch(
            "spine_items.data_connection.data_connection.QFileDialog.getExistingDirectory"
        ) as mock_directory_dialog:
            mock_directory_dialog.return_value = str(temp_dir)
            data_connection.show_add_directory_reference_dialog()
            mock_directory_dialog.assert_called_once()
        directory_references = list(data_connection.directory_iter())
        assert directory_references == [str(temp_dir)]

    def test_undo_add_directory_reference(self, data_connection, spine_toolbox_with_project, tmp_path):
        toolbox = spine_toolbox_with_project
        temp_dir = tmp_path / "target_dir"
        temp_dir.mkdir()
        with mock.patch(
            "spine_items.data_connection.data_connection.QFileDialog.getExistingDirectory"
        ) as mock_directory_dialog:
            mock_directory_dialog.return_value = str(temp_dir)
            data_connection.show_add_directory_reference_dialog()
            mock_directory_dialog.assert_called_once()
        assert list(data_connection.directory_iter()) == [str(temp_dir)]
        assert toolbox.undo_stack.count() == 1
        assert toolbox.undo_stack.index() == 1
        assert toolbox.undo_stack.text(0) == f"add references to {data_connection.name}"
        toolbox.undo_stack.undo()
        assert toolbox.undo_stack.index() == 0
        assert list(data_connection.directory_iter()) == []

    def test_add_db_references(self, data_connection):
        with (
            mock.patch("spine_items.data_connection.data_connection.UrlSelectorDialog.exec") as url_selector_exec,
            mock.patch(
                "spine_items.data_connection.data_connection.UrlSelectorDialog.url_dict"
            ) as url_selector_url_dict,
        ):
            # Add nothing
            url_selector_exec.return_value = QDialog.DialogCode.Rejected
            data_connection.show_add_db_reference_dialog()
            ref_model = data_connection.reference_model
            assert 1 == url_selector_exec.call_count
            assert not data_connection.has_db_references()
            assert 0 == ref_model.rowCount(ref_model.index(URL_ROOT_ROW, 0))
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
            data_connection.show_add_db_reference_dialog()
            assert 2 == url_selector_exec.call_count
            assert 1 == len(list(data_connection.db_reference_iter()))
            assert 1 == ref_model.rowCount(ref_model.index(URL_ROOT_ROW, 0))
            # Add same url with different username and password (should not be added)
            url_selector_url_dict.return_value = {
                "dialect": "mysql",
                "host": "host",
                "port": 3306,
                "database": "db",
                "username": "scott",
                "password": "tiger",
            }
            data_connection.show_add_db_reference_dialog()
            assert 3 == url_selector_exec.call_count
            assert 1 == len(list(data_connection.db_reference_iter()))
            assert 1 == ref_model.rowCount(ref_model.index(URL_ROOT_ROW, 0))

    def test_replace_file_reference_via_dialog(self, data_connection, tmp_path):
        temp_dir = Path(tmp_path, "data")
        temp_dir.mkdir()
        old_ref = temp_dir / "old.csv"
        old_ref.touch()
        new_ref = temp_dir / "new.csv"
        new_ref.touch()
        data_connection.do_add_references([str(old_ref)], [], [], [])
        old_resources = data_connection.resources_for_direct_successors()
        ref_model = data_connection.reference_model
        with (
            mock.patch("spine_items.data_connection.data_connection.QFileDialog.getOpenFileName") as mock_file_dialog,
            mock.patch.object(data_connection, "_resources_to_successors_replaced") as mock_replace_resources,
        ):
            mock_file_dialog.return_value = [new_ref.as_posix(), "*.*"]
            index = ref_model.index(0, 0, ref_model.index(FILE_REF_ROOT_ROW, 0))
            data_connection.select_another_target_for_reference(index)
            mock_file_dialog.assert_called_once()
            new_resources = data_connection.resources_for_direct_successors()
            mock_replace_resources.assert_called_once_with(old_resources, new_resources)
        assert data_connection.file_references, [str(new_ref)]

    def test_cancel_replace_file_reference_dialog(self, data_connection, tmp_path):
        temp_dir = Path(tmp_path, "data")
        temp_dir.mkdir()
        old_ref = temp_dir / "old.csv"
        old_ref.touch()
        data_connection.do_add_references([str(old_ref)], [], [], [])
        ref_model = data_connection.reference_model
        with (
            mock.patch("spine_items.data_connection.data_connection.QFileDialog.getOpenFileName") as mock_file_dialog,
            mock.patch.object(data_connection, "_resources_to_successors_replaced") as mock_replace_resources,
        ):
            mock_file_dialog.return_value = ["", "*.*"]
            index = ref_model.index(0, 0, ref_model.index(0, 0))
            data_connection.select_another_target_for_reference(index)
            mock_file_dialog.assert_called_once()
            mock_replace_resources.assert_not_called()
        assert data_connection.file_references, [str(old_ref)]

    def test_replacing_file_reference_with_same_reference_gives_warning(
        self, data_connection, spine_toolbox_with_project, tmp_path
    ):
        temp_dir = Path(tmp_path, "data")
        temp_dir.mkdir()
        old_ref = temp_dir / "old.csv"
        old_ref.touch()
        data_connection.do_add_references([str(old_ref)], [], [], [])
        ref_model = data_connection.reference_model
        with (
            mock.patch("spine_items.data_connection.data_connection.QFileDialog.getOpenFileName") as mock_file_dialog,
            mock.patch.object(data_connection, "_resources_to_successors_replaced") as mock_replace_resources,
            mock.patch.object(spine_toolbox_with_project, "msg_warning") as mock_warning,
        ):
            mock_file_dialog.return_value = [old_ref.as_posix(), "*.*"]
            mock_warning.emit = MagicMock()
            index = ref_model.index(0, 0, ref_model.index(FILE_REF_ROOT_ROW, 0))
            data_connection.select_another_target_for_reference(index)
            mock_file_dialog.assert_called_once()
            mock_replace_resources.assert_not_called()
            mock_warning.emit.assert_called_once_with(f"Reference to <b>{old_ref}</b> already exists.")
        assert data_connection.file_references, [str(old_ref)]

    def test_undo_replace_file_reference(self, data_connection, spine_toolbox_with_project, tmp_path):
        temp_dir = Path(tmp_path, "data")
        temp_dir.mkdir()
        old_ref = temp_dir / "old.csv"
        old_ref.touch()
        new_ref = temp_dir / "new.csv"
        new_ref.touch()
        data_connection.do_add_references([str(old_ref)], [], [], [])
        old_resources = data_connection.resources_for_direct_successors()
        ref_model = data_connection.reference_model
        with (
            mock.patch("spine_items.data_connection.data_connection.QFileDialog.getOpenFileName") as mock_file_dialog,
            mock.patch.object(data_connection, "_resources_to_successors_replaced") as mock_replace_resources,
        ):
            mock_file_dialog.return_value = [new_ref.as_posix(), "*.*"]
            index = ref_model.index(0, 0, ref_model.index(FILE_REF_ROOT_ROW, 0))
            data_connection.select_another_target_for_reference(index)
            new_resources = data_connection.resources_for_direct_successors()
            mock_replace_resources.assert_called_once_with(old_resources, new_resources)
        assert data_connection.file_references == [str(new_ref)]
        with mock.patch.object(data_connection, "_resources_to_successors_replaced") as mock_replace_resources:
            spine_toolbox_with_project.undo_stack.undo()
            mock_replace_resources.assert_called_once_with(new_resources, old_resources)
        assert data_connection.file_references == [str(old_ref)]

    def test_replace_file_pattern_via_dialog(self, data_connection, tmp_path):
        temp_dir = Path(tmp_path, "data")
        temp_dir.mkdir()
        data_connection.do_add_references([], [FilePattern(temp_dir, "*.json")], [], [])
        ref_model = data_connection.reference_model
        with (
            mock.patch("spine_items.data_connection.data_connection.FilePatternDialog") as mock_dialog_constructor,
            mock.patch.object(data_connection, "_resources_to_successors_changed") as mock_replace_resources,
        ):
            mock_dialog = mock.MagicMock()
            mock_dialog_constructor.return_value = mock_dialog
            mock_dialog.exec_.return_value = QDialog.DialogCode.Accepted
            mock_dialog.file_pattern.return_value = FilePattern(temp_dir, "*.txt")
            index = ref_model.index(0, 0, ref_model.index(FILE_PATTERN_ROOT_ROW, 0))
            data_connection.select_another_target_for_reference(index)
            mock_dialog.exec_.assert_called_once()
            mock_replace_resources.assert_called_once()
        assert data_connection.resources_for_direct_successors() == [
            file_resource_in_pack("DC", str(FilePattern(temp_dir, "*.txt")))
        ]

    def test_cancel_replace_file_pattern_dialog(self, data_connection, tmp_path):
        temp_dir = Path(tmp_path, "data")
        temp_dir.mkdir()
        data_connection.do_add_references([], [FilePattern(temp_dir, "*.json")], [], [])
        ref_model = data_connection.reference_model
        with (
            mock.patch("spine_items.data_connection.data_connection.FilePatternDialog") as mock_dialog_constructor,
            mock.patch.object(data_connection, "_resources_to_successors_changed") as mock_replace_resources,
        ):
            mock_dialog = mock.MagicMock()
            mock_dialog_constructor.return_value = mock_dialog
            mock_dialog.exec_.return_value = QDialog.DialogCode.Rejected
            mock_dialog.file_pattern.return_value = FilePattern(temp_dir, "*.txt")
            index = ref_model.index(0, 0, ref_model.index(FILE_PATTERN_ROOT_ROW, 0))
            data_connection.select_another_target_for_reference(index)
            mock_dialog.exec_.assert_called_once()
            mock_replace_resources.assert_not_called()
        assert data_connection.resources_for_direct_successors() == [
            file_resource_in_pack("DC", str(FilePattern(temp_dir, "*.json")))
        ]

    def test_replace_file_pattern_with_same_pattern_gives_warning(
        self, data_connection, spine_toolbox_with_project, tmp_path
    ):
        temp_dir = Path(tmp_path, "data")
        temp_dir.mkdir()
        data_connection.do_add_references([], [FilePattern(temp_dir, "*.json")], [], [])
        ref_model = data_connection.reference_model
        with (
            mock.patch("spine_items.data_connection.data_connection.FilePatternDialog") as mock_dialog_constructor,
            mock.patch.object(data_connection, "_resources_to_successors_changed") as mock_replace_resources,
            mock.patch.object(spine_toolbox_with_project, "msg_warning") as mock_warning,
        ):
            mock_dialog = mock.MagicMock()
            mock_dialog_constructor.return_value = mock_dialog
            mock_dialog.exec_.return_value = QDialog.DialogCode.Accepted
            mock_dialog.file_pattern.return_value = FilePattern(temp_dir, "*.json")
            index = ref_model.index(0, 0, ref_model.index(FILE_PATTERN_ROOT_ROW, 0))
            data_connection.select_another_target_for_reference(index)
            mock_dialog.exec_.assert_called_once()
            mock_warning.emit.assert_called_once_with(
                f"File pattern <b>{FilePattern(temp_dir, '*.json')}</b> already exists"
            )
            mock_replace_resources.assert_not_called()
        assert data_connection.resources_for_direct_successors() == [
            file_resource_in_pack("DC", str(FilePattern(temp_dir, "*.json")))
        ]

    def test_undo_replace_file_pattern(self, data_connection, spine_toolbox_with_project, tmp_path):
        toolbox = spine_toolbox_with_project
        temp_dir = Path(tmp_path, "data")
        temp_dir.mkdir()
        data_connection.do_add_references([], [FilePattern(temp_dir, "*.json")], [], [])
        ref_model = data_connection.reference_model
        with (mock.patch("spine_items.data_connection.data_connection.FilePatternDialog") as mock_dialog_constructor,):
            mock_dialog = mock.MagicMock()
            mock_dialog_constructor.return_value = mock_dialog
            mock_dialog.exec_.return_value = QDialog.DialogCode.Accepted
            mock_dialog.file_pattern.return_value = FilePattern(temp_dir, "*.txt")
            index = ref_model.index(0, 0, ref_model.index(FILE_PATTERN_ROOT_ROW, 0))
            data_connection.select_another_target_for_reference(index)
            mock_dialog.exec_.assert_called_once()
        with mock.patch.object(data_connection, "_resources_to_successors_changed") as mock_replace_resources:
            assert toolbox.undo_stack.text(toolbox.undo_stack.count() - 1) == "update file pattern in DC"
            toolbox.undo_stack.undo()
            mock_replace_resources.assert_called_once()
        assert data_connection.resources_for_direct_successors() == [
            file_resource_in_pack("DC", str(FilePattern(temp_dir, "*.json")))
        ]

    def test_replace_directory_reference_via_dialog(self, data_connection, tmp_path):
        old_dir = Path(tmp_path, "old_target_dir")
        old_dir.mkdir()
        new_dir = Path(tmp_path, "new_target_dir")
        new_dir.mkdir()
        data_connection.do_add_references([], [], [str(old_dir)], [])
        old_resources = data_connection.resources_for_direct_successors()
        ref_model = data_connection.reference_model
        with (
            mock.patch(
                "spine_items.data_connection.data_connection.QFileDialog.getExistingDirectory"
            ) as mock_directory_dialog,
            mock.patch.object(data_connection, "_resources_to_successors_replaced") as mock_replace_resources,
        ):
            mock_directory_dialog.return_value = new_dir.as_posix()
            index = ref_model.index(0, 0, ref_model.index(DIRECTORY_ROOT_ROW, 0))
            data_connection.select_another_target_for_reference(index)
            mock_directory_dialog.assert_called_once()
            new_resources = data_connection.resources_for_direct_successors()
            mock_replace_resources.assert_called_once_with(old_resources, new_resources)
        directory_references = list(data_connection.directory_iter())
        assert directory_references == [str(new_dir)]

    def test_cancel_replace_directory_reference_dialog(self, data_connection, tmp_path):
        old_dir = Path(tmp_path, "old_target_dir")
        old_dir.mkdir()
        data_connection.do_add_references([], [], [str(old_dir)], [])
        ref_model = data_connection.reference_model
        with (
            mock.patch(
                "spine_items.data_connection.data_connection.QFileDialog.getExistingDirectory"
            ) as mock_directory_dialog,
            mock.patch.object(data_connection, "_resources_to_successors_replaced") as mock_replace_resources,
        ):
            mock_directory_dialog.return_value = ""
            index = ref_model.index(0, 0, ref_model.index(DIRECTORY_ROOT_ROW, 0))
            data_connection.select_another_target_for_reference(index)
            mock_directory_dialog.assert_called_once()
            mock_replace_resources.assert_not_called()
        directory_references = list(data_connection.directory_iter())
        assert directory_references == [str(old_dir)]

    def test_replace_directory_reference_with_same_directory_gives_warning(
        self, data_connection, spine_toolbox_with_project, tmp_path
    ):
        old_dir = Path(tmp_path, "old_target_dir")
        old_dir.mkdir()
        data_connection.do_add_references([], [], [str(old_dir)], [])
        ref_model = data_connection.reference_model
        with (
            mock.patch(
                "spine_items.data_connection.data_connection.QFileDialog.getExistingDirectory"
            ) as mock_directory_dialog,
            mock.patch.object(data_connection, "_resources_to_successors_replaced") as mock_replace_resources,
            mock.patch.object(spine_toolbox_with_project, "msg_warning") as mock_warning,
        ):
            mock_directory_dialog.return_value = old_dir.as_posix()
            mock_warning.emit = mock.MagicMock()
            index = ref_model.index(0, 0, ref_model.index(DIRECTORY_ROOT_ROW, 0))
            data_connection.select_another_target_for_reference(index)
            mock_directory_dialog.assert_called_once()
            mock_replace_resources.assert_not_called()
            mock_warning.emit.assert_called_once_with(f"Reference to <b>{str(old_dir)}</b> already exists.")
        directory_references = list(data_connection.directory_iter())
        assert directory_references == [str(old_dir)]

    def test_undo_replace_directory_reference(self, data_connection, spine_toolbox_with_project, tmp_path):
        old_dir = Path(tmp_path, "old_target_dir")
        old_dir.mkdir()
        new_dir = Path(tmp_path, "new_target_dir")
        new_dir.mkdir()
        data_connection.do_add_references([], [], [str(old_dir)], [])
        old_resources = data_connection.resources_for_direct_successors()
        ref_model = data_connection.reference_model
        with (
            mock.patch(
                "spine_items.data_connection.data_connection.QFileDialog.getExistingDirectory"
            ) as mock_directory_dialog,
            mock.patch.object(data_connection, "_resources_to_successors_replaced") as mock_replace_resources,
        ):
            mock_directory_dialog.return_value = new_dir.as_posix()
            index = ref_model.index(0, 0, ref_model.index(DIRECTORY_ROOT_ROW, 0))
            data_connection.select_another_target_for_reference(index)
            new_resources = data_connection.resources_for_direct_successors()
            mock_replace_resources.assert_called_once_with(old_resources, new_resources)
        directory_references = list(data_connection.directory_iter())
        assert directory_references == [str(new_dir)]
        with mock.patch.object(data_connection, "_resources_to_successors_replaced") as mock_replace_resources:
            spine_toolbox_with_project.undo_stack.undo()
            mock_replace_resources.assert_called_once_with(new_resources, old_resources)
        directory_references = list(data_connection.directory_iter())
        assert directory_references == [str(old_dir)]

    def test_replace_url_reference_via_dialog(self, data_connection):
        old_url: UrlDict = {
            "dialect": "mysql",
            "host": "example.com",
            "port": 2323,
            "database": "my_database",
            "schema": "private",
            "username": "julius",
            "password": "caesar",
        }
        new_url = dict(old_url, username="gaius", password="octavius")
        data_connection.do_add_references([], [], [], [old_url])
        old_resources = data_connection.resources_for_direct_successors()
        ref_model = data_connection.reference_model
        with (
            mock.patch("spine_items.data_connection.data_connection.UrlSelectorDialog.exec") as mock_dialog_exec,
            mock.patch("spine_items.data_connection.data_connection.UrlSelectorDialog.url_dict") as mock_url_getter,
            mock.patch.object(data_connection, "_resources_to_successors_replaced") as mock_replace_resources,
        ):
            mock_dialog_exec.return_value = UrlSelectorDialog.DialogCode.Accepted
            mock_url_getter.return_value = new_url
            index = ref_model.index(0, 0, ref_model.index(URL_ROOT_ROW, 0))
            data_connection.select_another_target_for_reference(index)
            mock_dialog_exec.assert_called_once()
            mock_url_getter.assert_called_once()
            new_resources = data_connection.resources_for_direct_successors()
            mock_replace_resources.assert_called_once_with(old_resources, new_resources)
        assert list(data_connection.db_reference_iter()) == [new_url]

    def test_cancel_replace_url_dialog(self, data_connection):
        old_url: UrlDict = {
            "dialect": "mysql",
            "host": "example.com",
            "port": 2323,
            "database": "my_database",
            "schema": "private",
            "username": "julius",
            "password": "caesar",
        }
        data_connection.do_add_references([], [], [], [old_url])
        ref_model = data_connection.reference_model
        with (
            mock.patch("spine_items.data_connection.data_connection.UrlSelectorDialog.exec") as mock_dialog_exec,
            mock.patch.object(data_connection, "_resources_to_successors_replaced") as mock_replace_resources,
        ):
            mock_dialog_exec.return_value = UrlSelectorDialog.DialogCode.Rejected
            index = ref_model.index(0, 0, ref_model.index(URL_ROOT_ROW, 0))
            data_connection.select_another_target_for_reference(index)
            mock_dialog_exec.assert_called_once()
            mock_replace_resources.assert_not_called()
        assert list(data_connection.db_reference_iter()) == [old_url]

    def test_replace_url_reference_with_same_reference_gives_warning(self, data_connection, spine_toolbox_with_project):
        old_url: UrlDict = {
            "dialect": "mysql",
            "host": "example.com",
            "port": 2323,
            "database": "my_database",
            "schema": "private",
            "username": "julius",
            "password": "caesar",
        }
        data_connection.do_add_references([], [], [], [old_url])
        ref_model = data_connection.reference_model
        with (
            mock.patch("spine_items.data_connection.data_connection.UrlSelectorDialog.exec") as mock_dialog_exec,
            mock.patch("spine_items.data_connection.data_connection.UrlSelectorDialog.url_dict") as mock_url_getter,
            mock.patch.object(data_connection, "_resources_to_successors_replaced") as mock_replace_resources,
            mock.patch.object(spine_toolbox_with_project, "msg_warning") as mock_warning,
        ):
            mock_dialog_exec.return_value = UrlSelectorDialog.DialogCode.Accepted
            mock_url_getter.return_value = old_url
            mock_warning.emit = mock.MagicMock()
            index = ref_model.index(0, 0, ref_model.index(URL_ROOT_ROW, 0))
            data_connection.select_another_target_for_reference(index)
            mock_dialog_exec.assert_called_once()
            mock_url_getter.assert_called_once()
            mock_replace_resources.assert_not_called()
            mock_warning.emit.assert_called_once_with(
                f"Reference to <b>{convert_url_to_safe_string(old_url)}</b> already exists."
            )
        assert list(data_connection.db_reference_iter()) == [old_url]

    def test_undo_replace_url_reference(self, data_connection, spine_toolbox_with_project):
        old_url: UrlDict = {
            "dialect": "mysql",
            "host": "example.com",
            "port": 2323,
            "database": "my_database",
            "schema": "private",
            "username": "julius",
            "password": "caesar",
        }
        new_url = dict(old_url, username="gaius", password="octavius")
        data_connection.do_add_references([], [], [], [old_url])
        old_resources = data_connection.resources_for_direct_successors()
        ref_model = data_connection.reference_model
        with (
            mock.patch("spine_items.data_connection.data_connection.UrlSelectorDialog.exec") as mock_dialog_exec,
            mock.patch("spine_items.data_connection.data_connection.UrlSelectorDialog.url_dict") as mock_url_getter,
            mock.patch.object(data_connection, "_resources_to_successors_replaced") as mock_replace_resources,
        ):
            mock_dialog_exec.return_value = UrlSelectorDialog.DialogCode.Accepted
            mock_url_getter.return_value = new_url
            index = ref_model.index(0, 0, ref_model.index(URL_ROOT_ROW, 0))
            data_connection.select_another_target_for_reference(index)
            new_resources = data_connection.resources_for_direct_successors()
            mock_replace_resources.assert_called_once_with(old_resources, new_resources)
        assert list(data_connection.db_reference_iter()) == [new_url]
        with mock.patch.object(data_connection, "_resources_to_successors_replaced") as mock_replace_resources:
            spine_toolbox_with_project.undo_stack.undo()
            mock_replace_resources.assert_called_once_with(new_resources, old_resources)
        assert list(data_connection.db_reference_iter()) == [old_url]

    def test_remove_references(self, data_connection, tmp_path):
        temp_dir = Path(tmp_path, "references")
        temp_dir.mkdir()
        ref_model = data_connection.reference_model
        with (
            mock.patch("spine_items.data_connection.data_connection.QFileDialog.getOpenFileNames") as mock_filenames,
            mock.patch.object(
                data_connection._properties_ui.treeView_dc_references, "selectedIndexes"
            ) as mock_selected_indexes,
            mock.patch("spine_items.data_connection.data_connection.UrlSelectorDialog.exec") as url_selector_exec,
            mock.patch(
                "spine_items.data_connection.data_connection.UrlSelectorDialog.url_dict"
            ) as url_selector_url_dict,
        ):
            a = Path(temp_dir, "a.txt")
            a.touch()
            b = Path(temp_dir, "b.txt")
            b.touch()
            c = Path(temp_dir, "c.txt")  # Note. This file is not actually created
            d = Path(temp_dir, "d.txt")  # Note. This file is not actually created
            assert os.path.isfile(str(a)) and os.path.isfile(str(b))  # existing files
            assert not os.path.isfile(str(c))  # non-existing file
            assert not os.path.isfile(str(d))  # non-existing file
            # First add a couple of files as refs
            mock_filenames.return_value = ([str(a), str(b)], "*.*")
            data_connection.show_add_file_references_dialog()
            assert 1 == mock_filenames.call_count
            assert 2 == len(data_connection.file_references)
            assert 2 == ref_model.rowCount(ref_model.index(FILE_REF_ROOT_ROW, 0))
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
            data_connection.show_add_db_reference_dialog()
            url_selector_url_dict.return_value = {
                "dialect": "mysql",
                "username": "randy",
                "password": "creamfraiche",
                "host": "host",
                "port": 3307,
                "database": "db",
            }
            data_connection.show_add_db_reference_dialog()
            assert 2 == url_selector_exec.call_count
            assert 2 == len(list(data_connection.db_reference_iter()))
            assert 2 == ref_model.rowCount(ref_model.index(URL_ROOT_ROW, 0))
            # Test with no indexes selected
            mock_selected_indexes.return_value = []
            data_connection.remove_references()
            assert 1 == mock_selected_indexes.call_count
            assert 2 == len(data_connection.file_references)
            assert 2 == ref_model.rowCount(ref_model.index(FILE_REF_ROOT_ROW, 0))
            # Set one file selected and remove it
            a_index = ref_model.index(0, 0, ref_model.index(FILE_REF_ROOT_ROW, 0))
            mock_selected_indexes.return_value = [a_index]
            data_connection.remove_references()
            assert 2 == mock_selected_indexes.call_count
            assert 1 == len(data_connection.file_references)
            assert 1 == ref_model.rowCount(ref_model.index(FILE_REF_ROOT_ROW, 0))
            # Check that the remaining file is the one that's supposed to be there
            assert [str(b)] == data_connection.file_references
            assert str(b) == ref_model.item(FILE_REF_ROOT_ROW).child(0).data(Qt.ItemDataRole.DisplayRole)
            # Set one db selected and remove it
            db1_index = ref_model.index(0, 0, ref_model.index(URL_ROOT_ROW, 0))
            mock_selected_indexes.return_value = [db1_index]
            data_connection.remove_references()
            assert 3 == mock_selected_indexes.call_count
            assert 1 == len(list(data_connection.db_reference_iter()))
            assert 1 == ref_model.rowCount(ref_model.index(URL_ROOT_ROW, 0))

    def test_remove_file_pattern(self, data_connection, tmp_path):
        file_dir = Path(tmp_path, "files")
        file_dir.mkdir()
        data_connection.activate()
        data_connection.do_add_references([], [FilePattern(file_dir, "*.dat")], [], [])
        assert list(data_connection.file_pattern_iter()) == [FilePattern(file_dir, "*.dat")]
        ref_model = data_connection.reference_model
        root_index = ref_model.index(FILE_PATTERN_ROOT_ROW, 0)
        assert ref_model.rowCount(root_index) == 1
        pattern_index = ref_model.index(0, 0, root_index)
        data_connection._properties_ui.treeView_dc_references.selectionModel().select(
            pattern_index, QItemSelectionModel.SelectionFlag.ClearAndSelect
        )
        data_connection.remove_references()
        assert list(data_connection.file_pattern_iter()) == []

    def test_undo_removing_file_pattern(self, data_connection, spine_toolbox_with_project, tmp_path):
        toolbox = spine_toolbox_with_project
        file_dir = Path(tmp_path, "files")
        file_dir.mkdir()
        data_connection.activate()
        data_connection.do_add_references([], [FilePattern(file_dir, "*.dat")], [], [])
        ref_model = data_connection.reference_model
        root_index = ref_model.index(FILE_PATTERN_ROOT_ROW, 0)
        assert ref_model.rowCount(root_index) == 1
        pattern_index = ref_model.index(0, 0, root_index)
        data_connection._properties_ui.treeView_dc_references.selectionModel().select(
            pattern_index, QItemSelectionModel.SelectionFlag.ClearAndSelect
        )
        data_connection.remove_references()
        assert list(data_connection.file_pattern_iter()) == []
        assert toolbox.undo_stack.text(toolbox.undo_stack.count() - 1) == "remove references from DC"
        toolbox.undo_stack.undo()
        assert list(data_connection.file_pattern_iter()), [FilePattern(file_dir, "*.dat")]

    def test_remove_directory_reference(self, data_connection, tmp_path):
        temp_dir = Path(tmp_path, "references")
        temp_dir.mkdir()
        data_connection.activate()
        data_connection.do_add_references([], [], [str(temp_dir)], [])
        assert list(data_connection.directory_iter()) == [str(temp_dir)]
        ref_model = data_connection.reference_model
        directory_root_index = ref_model.index(DIRECTORY_ROOT_ROW, 0)
        assert ref_model.rowCount(directory_root_index) == 1
        directory_ref_index = ref_model.index(0, 0, directory_root_index)
        data_connection._properties_ui.treeView_dc_references.selectionModel().select(
            directory_ref_index, QItemSelectionModel.SelectionFlag.ClearAndSelect
        )
        data_connection.remove_references()
        assert list(data_connection.directory_iter()) == []

    def test_undo_removing_directory_reference(self, data_connection, spine_toolbox_with_project, tmp_path):
        toolbox = spine_toolbox_with_project
        temp_dir = Path(tmp_path, "references")
        temp_dir.mkdir()
        data_connection.activate()
        data_connection.do_add_references([], [], [str(temp_dir)], [])
        ref_model = data_connection.reference_model
        directory_root_index = ref_model.index(DIRECTORY_ROOT_ROW, 0)
        assert ref_model.rowCount(directory_root_index) == 1
        directory_ref_index = ref_model.index(0, 0, directory_root_index)
        data_connection._properties_ui.treeView_dc_references.selectionModel().select(
            directory_ref_index, QItemSelectionModel.SelectionFlag.ClearAndSelect
        )
        data_connection.remove_references()
        assert list(data_connection.directory_iter()) == []
        assert toolbox.undo_stack.count() == 1
        assert toolbox.undo_stack.index() == 1
        assert toolbox.undo_stack.text(0) == f"remove references from {data_connection.name}"
        toolbox.undo_stack.undo()
        assert list(data_connection.directory_iter()) == [str(temp_dir)]

    def test_remove_references_with_del_key(self, data_connection, tmp_path):
        temp_dir = Path(tmp_path, "references")
        temp_dir.mkdir()
        with (
            mock.patch("spine_items.data_connection.data_connection.QFileDialog.getOpenFileNames") as mock_filenames,
            mock.patch("spine_items.data_connection.data_connection.UrlSelectorDialog.exec"),
            mock.patch(
                "spine_items.data_connection.data_connection.UrlSelectorDialog.url", new_callable=mock.PropertyMock
            ) as url_selector_url,
        ):
            a = Path(temp_dir, "a.txt")
            a.touch()
            b = Path(temp_dir, "b.txt")
            b.touch()
            assert os.path.isfile(str(a)) and os.path.isfile(str(b))  # existing files
            data_connection.restore_selections()
            data_connection._connect_signals()
            # First add a couple of files as refs
            mock_filenames.return_value = ([str(a), str(b)], "*.*")
            data_connection.show_add_file_references_dialog()
            ref_model = data_connection.reference_model
            assert 1 == mock_filenames.call_count
            assert 2 == len(data_connection.file_references)
            assert 2 == ref_model.rowCount(ref_model.index(FILE_REF_ROOT_ROW, 0))
            # Second add a couple of dbs as refs
            url_selector_url.return_value = "mysql://scott:tiger@host:3306/db"
            data_connection.show_add_db_reference_dialog()
            indexes = data_connection._properties_ui.treeView_dc_references.selectedIndexes()
            assert len(indexes) == 0
            # Set index selected
            file_ref_root_index = ref_model.index(FILE_REF_ROOT_ROW, 0)
            ref_index = ref_model.index(0, 0, file_ref_root_index)
            data_connection._properties_ui.treeView_dc_references.selectionModel().select(
                ref_index, QItemSelectionModel.SelectionFlag.Select
            )
            indexes = data_connection._properties_ui.treeView_dc_references.selectedIndexes()
            assert len(indexes) == 1
            data_connection._properties_ui.treeView_dc_references.del_key_pressed.emit()
            assert 1 == len(data_connection.file_references)
            # Remove remaining two simultaneously by selecting bith and removing them with delete key
            file_ref_index = ref_model.index(0, 0, ref_model.index(FILE_REF_ROOT_ROW, 0))
            db_ref_index = ref_model.index(0, 0, ref_model.index(URL_ROOT_ROW, 0))
            data_connection._properties_ui.treeView_dc_references.selectionModel().select(
                file_ref_index, QItemSelectionModel.SelectionFlag.Select
            )
            data_connection._properties_ui.treeView_dc_references.selectionModel().select(
                db_ref_index, QItemSelectionModel.SelectionFlag.Select
            )
            data_connection._properties_ui.treeView_dc_references.del_key_pressed.emit()
            assert 0 == len(data_connection.file_references)
            assert 0 == len(list(data_connection.db_reference_iter()))

    def test_renaming_file_marks_its_reference_as_missing(self, data_connection, tmp_path):
        temp_dir = Path(tmp_path, "references")
        temp_dir.mkdir()
        a = Path(temp_dir, "a.txt")
        a.touch()
        with mock.patch("spine_items.data_connection.data_connection.QFileDialog.getOpenFileNames") as mock_filenames:
            mock_filenames.return_value = ([str(a)], "*.*")
            data_connection.show_add_file_references_dialog()
        renamed_file = a.parent / "renamed.txt"
        with signal_waiter(data_connection.file_system_watcher.file_renamed) as waiter:
            a.rename(renamed_file)
            waiter.wait()
        ref_model = data_connection.reference_model
        index = ref_model.index(0, 0, ref_model.index(FILE_REF_ROOT_ROW, 0))
        assert index.data() == str(a)
        assert index.data(Qt.ItemDataRole.UserRole + 2)
        assert data_connection.file_references == [str(a)]

    def test_deleting_file_marks_its_reference_as_missing(self, data_connection, tmp_path):
        temp_dir = Path(tmp_path, "references")
        temp_dir.mkdir()
        a = Path(temp_dir, "a.txt")
        a.touch()
        with mock.patch("spine_items.data_connection.data_connection.QFileDialog.getOpenFileNames") as mock_filenames:
            mock_filenames.return_value = ([str(a)], "*.*")
            data_connection.show_add_file_references_dialog()
        with signal_waiter(data_connection.file_system_watcher.file_removed) as waiter:
            a.unlink()
            waiter.wait()
        ref_model = data_connection.reference_model
        index = ref_model.index(0, 0, ref_model.index(FILE_REF_ROOT_ROW, 0))
        assert index.data() == str(a)
        assert index.data(Qt.ItemDataRole.UserRole + 2)
        assert data_connection.file_references == [str(a)]

    def test_copy_reference_to_project(self, data_connection, spine_toolbox_with_project, tmp_path):
        toolbox = spine_toolbox_with_project
        temp_dir = Path(tmp_path, "references")
        temp_dir.mkdir()
        a = Path(temp_dir, "a.txt")
        a.touch()
        with mock.patch("spine_items.data_connection.data_connection.QFileDialog.getOpenFileNames") as mock_filenames:
            mock_filenames.return_value = ([str(a)], "*.*")
            data_connection.show_add_file_references_dialog()
        data_connection.restore_selections()
        ref_model = data_connection.reference_model
        ref_index = ref_model.index(0, 0, ref_model.index(FILE_REF_ROOT_ROW, 0))
        properties_ui = toolbox.project_item_properties_ui(data_connection.item_type())
        properties_ui.treeView_dc_references.selectionModel().select(
            ref_index, QItemSelectionModel.SelectionFlag.ClearAndSelect
        )
        with signal_waiter(data_connection.file_system_watcher.file_added) as waiter:
            data_connection.copy_to_project()
            waiter.wait()
        assert ref_model.rowCount(ref_model.index(FILE_REF_ROOT_ROW, 0)) == 0
        assert Path(toolbox.project().items_dir, "dc", "a.txt").exists()
        assert data_connection.data_model.rowCount() == 1
        index = data_connection.data_model.index(0, 0)
        assert index.data() == "a.txt"
        assert index.data(Qt.ItemDataRole.UserRole + 1) == os.path.join(toolbox.project().items_dir, "dc", "a.txt")

    def test_create_data_file(self, data_connection, spine_toolbox_with_project):
        with mock.patch("spine_items.data_connection.data_connection.QInputDialog") as mock_input_dialog:
            mock_input_dialog.getText.return_value = ["data.csv"]
            with signal_waiter(data_connection.file_system_watcher.file_added) as waiter:
                data_connection.make_new_file()
                waiter.wait()
        model = data_connection.data_model
        assert model.rowCount() == 1
        index = model.index(0, 0)
        assert index.data() == "data.csv"
        assert index.data(Qt.ItemDataRole.UserRole + 1) == os.path.join(
            spine_toolbox_with_project.project().items_dir, "dc", "data.csv"
        )

    def test_deleting_data_file_removes_it_from_dc(self, data_connection):
        file_a = Path(data_connection.data_dir) / "data.dat"
        with signal_waiter(data_connection.file_system_watcher.file_added) as waiter:
            file_a.touch()
            waiter.wait()
        model = data_connection.data_model
        assert model.rowCount() == 1
        index = model.index(0, 0)
        assert index.data() == "data.dat"
        assert index.data(Qt.ItemDataRole.UserRole + 1) == str(file_a)
        with signal_waiter(data_connection.file_system_watcher.file_removed) as waiter:
            file_a.unlink()
            waiter.wait()
        assert model.rowCount() == 0

    def test_renaming_data_file_renames_it_in_dc_as_well(self, data_connection):
        file_a = Path(data_connection.data_dir) / "data.dat"
        with signal_waiter(data_connection.file_system_watcher.file_added) as waiter:
            file_a.touch()
            waiter.wait()
        model = data_connection.data_model
        assert model.rowCount() == 1
        index = model.index(0, 0)
        assert index.data() == "data.dat"
        assert index.data(Qt.ItemDataRole.UserRole + 1) == str(file_a)
        renamed = file_a.parent / "sata.txt"
        with signal_waiter(data_connection.file_system_watcher.file_renamed) as waiter:
            file_a.rename(renamed)
            waiter.wait()
        assert model.rowCount() == 1
        index = model.index(0, 0)
        assert index.data() == "sata.txt"
        assert index.data(Qt.ItemDataRole.UserRole + 1) == str(renamed)

    def test_item_dict(self, data_connection):
        """Tests Item dictionary creation."""
        d = data_connection.item_dict()
        a = [
            "type",
            "description",
            "x",
            "y",
            "file_references",
            "file_patterns",
            "directory_references",
            "db_references",
            "db_credentials",
        ]
        for k in a:
            assert k in d, f"Key '{k}' not in dict {d}"

    def test_deserialization_with_remote_db_reference(self, data_connection, spine_toolbox_with_project):
        toolbox = spine_toolbox_with_project
        with (
            mock.patch("spine_items.data_connection.data_connection.UrlSelectorDialog.exec") as url_selector_exec,
            mock.patch(
                "spine_items.data_connection.data_connection.UrlSelectorDialog.url_dict"
            ) as url_selector_url_dict,
        ):
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
            data_connection.show_add_db_reference_dialog()
        item_dict = data_connection.item_dict()
        assert len(item_dict["db_references"]) == 1
        assert "username" not in item_dict["db_references"][0]
        assert "password" not in item_dict["db_references"][0]
        deserialized = DataConnection.from_dict("deserialized", item_dict, toolbox, toolbox.project())
        assert deserialized.has_db_references()
        assert list(deserialized.db_reference_iter()) == [
            {
                "dialect": "mysql",
                "host": "post.com",
                "port": 3306,
                "database": "db",
                "username": "randy",
                "password": "creamfraiche",
            }
        ]

    def test_deserialization_with_sqlite_db_reference_in_project_directory(
        self, data_connection, spine_toolbox_with_project, tmp_path
    ):
        toolbox = spine_toolbox_with_project
        db_path = Path(tmp_path, "db.sqlite")
        create_new_spine_database("sqlite:///" + str(db_path))
        with (
            mock.patch("spine_items.data_connection.data_connection.UrlSelectorDialog.exec") as url_selector_exec,
            mock.patch(
                "spine_items.data_connection.data_connection.UrlSelectorDialog.url_dict"
            ) as url_selector_url_dict,
        ):
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
            data_connection.show_add_db_reference_dialog()
        item_dict = data_connection.item_dict()
        assert len(item_dict["db_references"]) == 1
        assert "username" not in item_dict["db_references"][0]
        assert "password" not in item_dict["db_references"][0]
        deserialized = DataConnection.from_dict("deserialized", item_dict, toolbox, toolbox.project())
        assert deserialized.has_db_references()
        assert list(deserialized.db_reference_iter()) == [
            {
                "dialect": "sqlite",
                "host": None,
                "port": None,
                "database": str(db_path),
                "username": None,
                "password": None,
            }
        ]

    def test_sqlite_db_reference_is_marked_missing_when_db_file_is_renamed(self, data_connection, tmp_path):
        db_path = Path(tmp_path, "db.sqlite")
        engine = create_new_spine_database("sqlite:///" + str(db_path))
        engine.dispose()
        with (
            mock.patch("spine_items.data_connection.data_connection.UrlSelectorDialog.exec") as url_selector_exec,
            mock.patch(
                "spine_items.data_connection.data_connection.UrlSelectorDialog.url_dict"
            ) as url_selector_url_dict,
        ):
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
            data_connection.show_add_db_reference_dialog()
        while data_connection._database_validator.is_busy():
            QApplication.processEvents()
        assert list(data_connection.db_reference_iter()) == [
            {
                "dialect": "sqlite",
                "host": None,
                "port": None,
                "database": str(db_path),
                "username": None,
                "password": None,
            }
        ]
        with signal_waiter(data_connection.file_system_watcher.file_renamed) as waiter:
            db_path.rename(db_path.parent / "renamed.sqlite")
            waiter.wait()
        assert data_connection._db_ref_root.child(0, 0).data(_Role.MISSING)

    def test_refreshing_missing_sqlite_reference_resurrects_it(self, data_connection, tmp_path):
        db_path = Path(tmp_path, "db.sqlite")
        engine = create_new_spine_database("sqlite:///" + str(db_path))
        engine.dispose()
        with (
            mock.patch("spine_items.data_connection.data_connection.UrlSelectorDialog.exec") as url_selector_exec,
            mock.patch(
                "spine_items.data_connection.data_connection.UrlSelectorDialog.url_dict"
            ) as url_selector_url_dict,
        ):
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
            data_connection.show_add_db_reference_dialog()
        while data_connection._database_validator.is_busy():
            QApplication.processEvents()
        assert list(data_connection.db_reference_iter()) == [
            {
                "dialect": "sqlite",
                "host": None,
                "port": None,
                "database": str(db_path),
                "username": None,
                "password": None,
            }
        ]
        with signal_waiter(data_connection.file_system_watcher.file_renamed) as waiter:
            renamed_path = db_path.rename(db_path.parent / "renamed.sqlite")
            waiter.wait()
        assert data_connection._db_ref_root.child(0, 0).data(_Role.MISSING)
        with signal_waiter(data_connection.file_system_watcher.file_renamed) as waiter:
            renamed_path.rename(db_path)
            waiter.wait()
        assert data_connection._db_ref_root.child(0, 0).data(_Role.MISSING)
        data_connection.restore_selections()
        data_connection._connect_signals()
        ref_model = data_connection.reference_model
        db_ref_root_index = ref_model.index(URL_ROOT_ROW, 0)
        ref_index = ref_model.index(FILE_REF_ROOT_ROW, 0, db_ref_root_index)
        data_connection._properties_ui.treeView_dc_references.selectionModel().select(
            ref_index, QItemSelectionModel.SelectionFlag.Select
        )
        data_connection.refresh_references()
        while data_connection._database_validator.is_busy():
            QApplication.processEvents()
        assert not data_connection._db_ref_root.child(FILE_REF_ROOT_ROW, 0).data(_Role.MISSING)

    def test_broken_sqlite_url_marks_the_reference_missing(self, data_connection, tmp_path):
        db_path = Path(tmp_path, "db.sqlite")
        with (
            mock.patch("spine_items.data_connection.data_connection.UrlSelectorDialog.exec") as url_selector_exec,
            mock.patch(
                "spine_items.data_connection.data_connection.UrlSelectorDialog.url_dict"
            ) as url_selector_url_dict,
        ):
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
            data_connection.show_add_db_reference_dialog()
        while data_connection._database_validator.is_busy():
            QApplication.processEvents()
        assert list(data_connection.db_reference_iter()) == [
            {
                "dialect": "sqlite",
                "host": None,
                "port": None,
                "database": str(db_path),
                "username": None,
                "password": None,
            }
        ]
        assert data_connection._db_ref_root.child(0, 0).data(_Role.MISSING)

    def test_notify_destination(self, data_connection):
        data_connection.logger.msg = MagicMock()
        data_connection.logger.msg_warning = MagicMock()
        source_item = NonCallableMagicMock()
        source_item.name = "source name"
        source_item.item_type = MagicMock(return_value="Importer")
        data_connection.notify_destination(source_item)
        data_connection.logger.msg.emit.assert_called_with("Link established")
        source_item.item_type = MagicMock(return_value="Data Store")
        data_connection.notify_destination(source_item)
        data_connection.logger.msg.emit.assert_called_with("Link established")
        source_item.item_type = MagicMock(return_value="Tool")
        data_connection.notify_destination(source_item)
        data_connection.logger.msg.emit.assert_called_with(
            "Link established. Tool <b>source name</b> output files"
            " will be passed as references to item <b>DC</b> after execution."
        )
        source_item.item_type = MagicMock(return_value="View")
        data_connection.notify_destination(source_item)
        data_connection.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a <b>View</b> and"
            " a <b>Data Connection</b> has not been implemented yet."
        )

    def test_rename(self, data_connection, spine_toolbox_with_project):
        """Tests renaming a Data Connection."""
        data_connection.activate()
        expected_name = "ABC"
        expected_short_name = "abc"
        expected_data_dir = os.path.join(spine_toolbox_with_project.project().items_dir, expected_short_name)
        data_connection.rename(expected_name, "")
        # Check name
        assert expected_name == data_connection.name
        assert expected_name == data_connection.get_icon().name()
        # Check data_dir
        assert expected_data_dir == data_connection.data_dir
        # Check that file_system_watcher has one path (new data_dir)
        watched_dirs = data_connection.file_system_watcher.directories()
        assert 1 == len(watched_dirs)
        assert data_connection.data_dir == watched_dirs[0]

    def test_selection_states(self, data_connection, tmp_path):
        data_dir = Path(tmp_path, "data_dir")
        data_dir.mkdir()
        (data_dir / "data.dat").touch()
        pattern_dir = Path(tmp_path, "pattern_dir")
        pattern_dir.mkdir()
        dir_dir = Path(tmp_path, "dir_dir")
        dir_dir.mkdir()
        url: UrlDict = {
            "dialect": "mysql",
            "host": "tools-for-energy-system-modelling.com",
            "port": 555,
            "database": "input",
            "username": "albert",
            "password": "zweistein",
        }
        data_connection.do_add_references([str(data_dir)], [FilePattern(pattern_dir, "*.gdx")], [str(dir_dir)], [url])
        data_connection.activate()
        assert not data_connection.any_refs_selected
        assert not data_connection.file_refs_selected
        assert not data_connection.current_is_file_ref
        assert not data_connection.current_is_file_pattern
        assert not data_connection.current_is_directory_ref
        properties_ui = data_connection._properties_ui
        selection_model = properties_ui.treeView_dc_references.selectionModel()
        ref_model = data_connection.reference_model
        root_index = ref_model.index(FILE_REF_ROOT_ROW, 0)
        selection_model.setCurrentIndex(
            ref_model.index(0, 0, root_index), QItemSelectionModel.SelectionFlag.ClearAndSelect
        )
        assert data_connection.any_refs_selected
        assert data_connection.file_refs_selected
        assert data_connection.current_is_file_ref
        assert not data_connection.current_is_file_pattern
        assert not data_connection.current_is_directory_ref
        root_index = ref_model.index(FILE_PATTERN_ROOT_ROW, 0)
        selection_model.setCurrentIndex(
            ref_model.index(0, 0, root_index), QItemSelectionModel.SelectionFlag.ClearAndSelect
        )
        assert data_connection.any_refs_selected
        assert not data_connection.file_refs_selected
        assert not data_connection.current_is_file_ref
        assert data_connection.current_is_file_pattern
        assert not data_connection.current_is_directory_ref
        root_index = ref_model.index(DIRECTORY_ROOT_ROW, 0)
        selection_model.setCurrentIndex(
            ref_model.index(0, 0, root_index), QItemSelectionModel.SelectionFlag.ClearAndSelect
        )
        assert data_connection.any_refs_selected
        assert not data_connection.file_refs_selected
        assert not data_connection.current_is_file_ref
        assert not data_connection.current_is_file_pattern
        assert data_connection.current_is_directory_ref
        root_index = ref_model.index(URL_ROOT_ROW, 0)
        selection_model.setCurrentIndex(
            ref_model.index(0, 0, root_index), QItemSelectionModel.SelectionFlag.ClearAndSelect
        )
        assert data_connection.any_refs_selected
        assert not data_connection.file_refs_selected
        assert not data_connection.current_is_file_ref
        assert not data_connection.current_is_file_pattern
        assert not data_connection.current_is_directory_ref

    def test_data_file_in_list(self, data_file, data_connection):
        model = data_connection.data_model
        assert model.rowCount() == 1
        index = model.index(0, 0)
        assert index.data() == "data.csv"
        assert index.data(Qt.ItemDataRole.UserRole + 1) == str(data_file)

    def test_remove_data_file(self, data_file, data_connection):
        data_connection.restore_selections()
        index = data_connection.data_model.index(0, 0)
        data_connection._properties_ui.treeView_dc_data.selectionModel().select(
            index, QItemSelectionModel.SelectionFlag.ClearAndSelect
        )
        with mock.patch("spine_items.data_connection.data_connection.QMessageBox") as mock_message_box:
            mock_message_box.exec.return_value = QMessageBox.StandardButton.Ok
            with signal_waiter(data_connection.file_system_watcher.file_removed) as waiter:
                data_connection.remove_files()
                waiter.wait()
        model = data_connection.data_model
        assert model.rowCount() == 0

    def test_rename_data_file(self, data_file, data_connection):
        with signal_waiter(data_connection.file_system_watcher.file_renamed) as waiter:
            data_file.rename(data_file.parent / "renamed.dat")
            waiter.wait()
        model = data_connection.data_model
        assert model.rowCount() == 1
        index = model.index(0, 0)
        assert index.data() == "renamed.dat"
        assert index.data(Qt.ItemDataRole.UserRole + 1) == str(data_file.parent / "renamed.dat")

    def test_add_file_references_when_invalid_file_reference_is_present(self, non_existent_path, dc_factory, tmp_path):
        data_connection = dc_factory({"file_references": [str(non_existent_path)]})
        temp_dir = Path(tmp_path, "references")
        temp_dir.mkdir()
        with mock.patch("spine_items.data_connection.data_connection.QFileDialog.getOpenFileNames") as mock_filenames:
            a = Path(temp_dir, "a.txt")
            a.touch()
            mock_filenames.return_value = ([str(a)], "*.*")
            data_connection.show_add_file_references_dialog()
            ref_model = data_connection.reference_model
            assert 2 == len(data_connection.file_references)
            assert 2 == ref_model.rowCount(ref_model.index(FILE_REF_ROOT_ROW, 0))
            assert str(non_existent_path) == ref_model.index(0, 0, ref_model.index(FILE_REF_ROOT_ROW, 0)).data()
            assert str(a) == ref_model.index(1, 0, ref_model.index(FILE_REF_ROOT_ROW, 0)).data()

    def test_refresh_file_reference_when_invalid_file_reference_is_present(
        self, non_existent_path, dc_factory, spine_toolbox_with_project
    ):
        toolbox = spine_toolbox_with_project
        data_connection = dc_factory({"file_references": [str(non_existent_path)]})
        ref_model = data_connection.reference_model
        root_index = ref_model.index(FILE_REF_ROOT_ROW, 0)
        reference_index = ref_model.index(0, 0, root_index)
        assert reference_index.data(Qt.ItemDataRole.ToolTipRole) == "The file is missing."
        non_existent_path.touch()
        data_connection.restore_selections()
        data_connection._properties_ui.treeView_dc_references.selectionModel().select(
            reference_index, QItemSelectionModel.SelectionFlag.ClearAndSelect
        )
        with mock.patch.object(toolbox.project(), "notify_resource_changes_to_successors") as resource_notifier:
            data_connection.refresh_references()
            assert reference_index.data(Qt.ItemDataRole.ToolTipRole) is None, "The file is missing."
            resource_notifier.assert_called_once_with(data_connection)

    def test_invalid_file_pattern_reference_is_marked_in_model(self, dc_factory, spine_toolbox_with_project):
        toolbox = spine_toolbox_with_project
        project = toolbox.project()
        non_existent_directory = Path(project.project_dir, "non_existent")
        file_pattern = FilePattern(non_existent_directory, "data?.csv")
        data_connection = dc_factory({"file_patterns": [file_pattern.to_dict(project)]})
        ref_model = data_connection.reference_model
        assert ref_model.rowCount() == 4
        root_index = ref_model.index(FILE_PATTERN_ROOT_ROW, 0)
        assert ref_model.rowCount(root_index) == 1
        missing_pattern_index = ref_model.index(0, 0, root_index)
        assert missing_pattern_index.data() == str(file_pattern)
        assert missing_pattern_index.data(Qt.ItemDataRole.ForegroundRole) == Qt.GlobalColor.red
        assert missing_pattern_index.data(Qt.ItemDataRole.ToolTipRole) == "The directory is missing."

    def test_invalid_directory_reference_is_marked_in_model(self, dc_factory, spine_toolbox_with_project):
        toolbox = spine_toolbox_with_project
        project = toolbox.project()
        non_existent_directory = Path(project.project_dir, "non_existent")
        data_connection = dc_factory(
            {"directory_references": [serialize_path(str(non_existent_directory), project.project_dir)]}
        )
        ref_model = data_connection.reference_model
        assert ref_model.rowCount() == 4
        directory_root_index = ref_model.index(DIRECTORY_ROOT_ROW, 0)
        assert ref_model.rowCount(directory_root_index) == 1
        missing_directory_index = ref_model.index(0, 0, directory_root_index)
        assert missing_directory_index.data() == str(non_existent_directory)
        assert missing_directory_index.data(Qt.ItemDataRole.ForegroundRole) == Qt.GlobalColor.red
        assert missing_directory_index.data(Qt.ItemDataRole.ToolTipRole) == "The directory is missing."
