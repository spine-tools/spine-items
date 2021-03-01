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
Unit tests for Notebook project item.

:author: A. Soininen (VTT), P. Savolainen (VTT), M. Marin (KTH)
:date:   4.10.2019
"""
from tempfile import TemporaryDirectory, TemporaryFile
import unittest
from unittest import mock
import os
from PySide2.QtGui import QStandardItem, QStandardItemModel
from PySide2.QtWidgets import QApplication, QMenu
from spine_items.notebook.item_info import ItemInfo
from spine_items.notebook.notebook_specifications import NotebookSpecification
from spine_items.notebook.notebook_instance import NotebookInstance
from spine_items.notebook.notebook import Notebook
from spine_items.notebook.notebook_factory import NotebookFactory
from spine_items.notebook.executable_item import ExecutableItem
from spine_engine.config import TOOL_OUTPUT_DIR
from tests.mock_helpers import mock_finish_project_item_construction, create_mock_project, create_mock_toolbox
from .mock_notebook_specification_model import _MockNotebookSpecModel as mock_model, SIMPLE_ITEM


class TestNotebook(unittest.TestCase):
    def setUp(self):
        """Set up."""
        self._temp_dir = TemporaryDirectory()
        self._temp_file = TemporaryFile(prefix="nb", suffix=".ipynb", dir=self._temp_dir.name)
        self.toolbox = create_mock_toolbox()
        self.project = create_mock_project(self._temp_dir.name)
        self.model = self.toolbox.specification_model = mock_model(self.toolbox, self._temp_dir.name,
                                                                   self._temp_file.name)

    def tearDown(self):
        self._temp_file.close()
        self._temp_dir.cleanup()

    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def test_item_type(self):
        self.assertEqual(Notebook.item_type(), ItemInfo.item_type())

    def test_item_category(self):
        self.assertEqual(Notebook.item_category(), ItemInfo.item_category())

    def test_item_dict(self):
        """Tests Item dictionary creation."""
        notebook = self._add_notebook()
        d = notebook.item_dict()
        a = ["type", "description", "x", "y", "specification", "execute_in_work", "cmd_line_args"]
        for k in a:
            self.assertTrue(k in d, f"Key '{k}' not in dict {d}")

    def _add_notebook(self, item_dict=None):
        if item_dict is None:
            item_dict = {"type": "Notebook", "description": "", "x": 0, "y": 0}
        factory = NotebookFactory()
        notebook = factory.make_item("NB", item_dict, self.toolbox, self.project)
        mock_finish_project_item_construction(factory, notebook, self.toolbox)
        # Set model for tool combo box
        notebook._properties_ui.comboBox_notebook.setModel(self.model)
        return notebook

    def test_notify_destination(self):
        source_item = mock.NonCallableMagicMock()
        source_item.name = "source name"
        source_item.item_type = mock.MagicMock(return_value="Data Connection")
        notebook = self._add_notebook()
        notebook.logger.msg = mock.MagicMock()
        notebook.logger.msg_warning = mock.MagicMock()
        notebook.notify_destination(source_item)
        notebook.logger.msg.emit.assert_called_with(
            "Link established. Notebook <b>NB</b> will look for input "
            "files from <b>source name</b>'s references and data directory."
        )
        source_item.item_type = mock.MagicMock(return_value="Importer")
        notebook.notify_destination(source_item)
        notebook.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a " "<b>Importer</b> and a <b>Notebook</b> has not been "
            "implemented yet."
        )
        source_item.item_type = mock.MagicMock(return_value="Data Store")
        notebook.notify_destination(source_item)
        notebook.logger.msg.emit.assert_called_with(
            "Link established. Data Store <b>source name</b> url will " "be passed to Notebook <b>NB</b> when "
            "executing."
        )
        source_item.item_type = mock.MagicMock(return_value="GdxExporter")
        notebook.notify_destination(source_item)
        notebook.logger.msg.emit.assert_called_with(
            "Link established. The file exported by <b>source name</b> will "
            "be passed to Notebook <b>NB</b> when executing."
        )
        source_item.item_type = mock.MagicMock(return_value="Tool")
        notebook.notify_destination(source_item)
        notebook.logger.msg.emit.assert_called_with("Link established")
        source_item.item_type = mock.MagicMock(return_value="Notebook")
        notebook.notify_destination(source_item)
        notebook.logger.msg.emit.assert_called_with("Link established")
        source_item.item_type = mock.MagicMock(return_value="View")
        notebook.notify_destination(source_item)
        notebook.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a " "<b>View</b> and a <b>Notebook</b> has not been implemented yet."
        )

