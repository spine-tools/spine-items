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

"""Unit tests for the ``preview_updater`` module."""
from multiprocessing import Process, Queue
import pathlib
from tempfile import TemporaryDirectory
import unittest
from unittest import mock
from PySide6.QtWidgets import QApplication, QComboBox, QWidget
from spine_items.exporter.mvcmodels.full_url_list_model import FullUrlListModel
from spine_items.exporter.widgets.preview_updater import PreviewUpdater, WriteTableTask, write_task_loop
from spinedb_api import DatabaseMapping
from spinedb_api.export_mapping.export_mapping import AlternativeMapping
from spinedb_api.export_mapping.group_functions import NoGroup
from tests.mock_helpers import parent_widget


class TestPreviewUpdater(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        self._parent_widget = QWidget()

    def tearDown(self):
        self._parent_widget.deleteLater()

    def test_deleting_url_model_does_not_break_tear_down(self):
        with parent_widget() as window:
            setattr(window, "current_mapping_about_to_change", mock.MagicMock())
            setattr(window, "current_mapping_changed", mock.MagicMock())
            ui = mock.MagicMock()
            ui.database_url_combo_box = QComboBox(self._parent_widget)
            url_model = FullUrlListModel()
            mappings_table_model = mock.MagicMock()
            mappings_proxy_model = mock.MagicMock()
            mapping_editor_table_model = mock.MagicMock()
            project_dir = ""
            preview_updater = PreviewUpdater(
                window,
                ui,
                url_model,
                mappings_table_model,
                mappings_proxy_model,
                mapping_editor_table_model,
                project_dir,
            )
            # It is difficult to get the url_model deleted on C++ side.
            # We simulate it by emitting destroyed manually.
            url_model.destroyed.emit()
            self.assertIsNot(preview_updater._url_model, url_model)
            preview_updater.tear_down()


class TestWriteTaskLoop(unittest.TestCase):
    def test_quit(self):
        sender = Queue()
        receiver = Queue()
        sender.put("quit")
        write_task_loop(receiver, sender)
        self.assertTrue(receiver.get(), "finished")

    def test_quitting_takes_precedence_over_writing(self):
        with TemporaryDirectory() as temp_dir:
            url = "sqlite:///" + str(pathlib.Path(temp_dir) / "db.sqlite")
            with DatabaseMapping(url, create=True) as db_map:
                db_map.add_alternative_item(name="alt1")
                db_map.add_alternative_item(name="alt2")
                db_map.commit_session("Add test data.")
            sender = Queue()
            receiver = Queue()
            sender.put(WriteTableTask(url, "my mapping", 2.3, AlternativeMapping(0), True, 1, 3, NoGroup.NAME))
            sender.put("quit")
            write_task_loop(receiver, sender)
            self.assertTrue(receiver.get(), "finished")

    def test_writing(self):
        sender = Queue()
        receiver = Queue()
        process = Process(target=write_task_loop, args=(receiver, sender))
        process.start()
        with TemporaryDirectory() as temp_dir:
            url = "sqlite:///" + str(pathlib.Path(temp_dir) / "db.sqlite")
            with DatabaseMapping(url, create=True) as db_map:
                db_map.add_alternative_item(name="alt1")
                db_map.add_alternative_item(name="alt2")
                db_map.commit_session("Add test data.")
            sender.put(WriteTableTask(url, "my mapping", 2.3, AlternativeMapping(0), True, 1, 3, NoGroup.NAME))
            tables = receiver.get()
            self.assertEqual(tables, ((url, "my mapping"), "my mapping", {None: [["Base"], ["alt1"], ["alt2"]]}, 2.3))
        sender.put("quit")
        self.assertTrue(receiver.get(), "finished")
        process.join()

    def test_change_database_between_writes(self):
        sender = Queue()
        receiver = Queue()
        process = Process(target=write_task_loop, args=(receiver, sender))
        process.start()
        with TemporaryDirectory() as temp_dir:
            url = "sqlite:///" + str(pathlib.Path(temp_dir) / "db1.sqlite")
            with DatabaseMapping(url, create=True) as db_map:
                db_map.add_alternative_item(name="alt1")
                db_map.add_alternative_item(name="alt2")
                db_map.commit_session("Add test data.")
            sender.put(WriteTableTask(url, "my mapping", 2.3, AlternativeMapping(0), True, 1, 3, NoGroup.NAME))
            tables = receiver.get()
            self.assertEqual(tables, ((url, "my mapping"), "my mapping", {None: [["Base"], ["alt1"], ["alt2"]]}, 2.3))
            url = "sqlite:///" + str(pathlib.Path(temp_dir) / "db2.sqlite")
            with DatabaseMapping(url, create=True) as db_map:
                db_map.add_alternative_item(name="alt3")
                db_map.add_alternative_item(name="alt4")
                db_map.commit_session("Add test data.")
            sender.put(WriteTableTask(url, "my mapping", 23.0, AlternativeMapping(0), True, 1, 3, NoGroup.NAME))
            tables = receiver.get()
            self.assertEqual(tables, ((url, "my mapping"), "my mapping", {None: [["Base"], ["alt3"], ["alt4"]]}, 23.0))
        sender.put("quit")
        self.assertTrue(receiver.get(), "finished")
        process.join()


if __name__ == "__main__":
    unittest.main()
