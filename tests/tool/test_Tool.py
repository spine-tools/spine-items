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

"""Unit tests for Tool project item."""
from tempfile import TemporaryDirectory
import unittest
from unittest import mock
import os
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QMenu
from spine_items.tool.item_info import ItemInfo
from spine_items.tool.tool_specifications import ExecutableTool
from spine_items.tool.tool import Tool
from spine_items.tool.tool_factory import ToolFactory
from spine_engine.project_item.project_item_resource import ProjectItemResource
from spine_engine.config import TOOL_OUTPUT_DIR
from tests.mock_helpers import mock_finish_project_item_construction, create_mock_project, create_mock_toolbox


class TestTool(unittest.TestCase):
    def setUp(self):
        """Set up."""
        self._temp_dir = TemporaryDirectory()
        self.toolbox = create_mock_toolbox()
        self.project = create_mock_project(self._temp_dir.name)
        specifications = [
            ExecutableTool(
                name="simple_exec",
                tooltype="executable",
                path=self._temp_dir.name,
                includes=["main.sh"],
                settings=self.toolbox.qsettings(),
                logger=self.toolbox,
                description="A simple executable tool.",
                inputfiles=["input1.csv", "input2.csv"],
                inputfiles_opt=["opt_input.csv"],
                outputfiles=["output1.csv", "output2.csv"],
                cmdline_args="<args>",
            ),
            ExecutableTool(
                name="complex_exec",
                tooltype="executable",
                path=self._temp_dir.name,
                includes=["MakeFile", "src/a.c", "src/a.h", "src/subunit/x.c", "src/subunit/x.h"],
                settings=self.toolbox.qsettings(),
                logger=self.toolbox,
                description="A more complex executable tool.",
                inputfiles=["input1.csv", "input/input2.csv"],
                inputfiles_opt=["opt/*.ini", "?abc.txt"],
                outputfiles=["output1.csv", "output/output2.csv"],
                cmdline_args="subunit",
            ),
        ]
        self.specification_dict = {x.name: x for x in specifications}
        self.project.get_specification = self.specification_dict.get
        self.toolbox.project.return_value = self.project
        self.model = _MockToolSpecModel(self.specification_dict)

    def tearDown(self):
        self._temp_dir.cleanup()

    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def test_item_type(self):
        self.assertEqual(Tool.item_type(), ItemInfo.item_type())

    def test_item_dict(self):
        """Tests Item dictionary creation."""
        tool = self._add_tool()
        d = tool.item_dict()
        a = ["type", "description", "x", "y", "specification", "execute_in_work", "cmd_line_args"]
        for k in a:
            self.assertTrue(k in d, f"Key '{k}' not in dict {d}")

    def test_notify_destination(self):
        source_item = mock.NonCallableMagicMock()
        source_item.name = "source name"
        source_item.item_type = mock.MagicMock(return_value="Data Connection")
        tool = self._add_tool()
        tool.logger.msg = mock.MagicMock()
        tool.logger.msg_warning = mock.MagicMock()
        tool.notify_destination(source_item)
        tool.logger.msg.emit.assert_called_with(
            "Link established. Tool <b>T</b> will look for input "
            "files from <b>source name</b>'s references and data directory."
        )
        source_item.item_type = mock.MagicMock(return_value="Importer")
        tool.notify_destination(source_item)
        tool.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a " "<b>Importer</b> and a <b>Tool</b> has not been implemented yet."
        )
        source_item.item_type = mock.MagicMock(return_value="Data Store")
        tool.notify_destination(source_item)
        tool.logger.msg.emit.assert_called_with(
            "Link established. Data Store <b>source name</b> url will " "be passed to Tool <b>T</b> when executing."
        )
        source_item.item_type = mock.MagicMock(return_value="Exporter")
        tool.notify_destination(source_item)
        tool.logger.msg.emit.assert_called_with(
            "Link established. The file exported by <b>source name</b> are now available in <b>T</b>."
        )
        source_item.item_type = mock.MagicMock(return_value="Tool")
        tool.notify_destination(source_item)
        tool.logger.msg.emit.assert_called_with("Link established")
        source_item.item_type = mock.MagicMock(return_value="View")
        tool.notify_destination(source_item)
        tool.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a " "<b>View</b> and a <b>Tool</b> has not been implemented yet."
        )

    def test_rename(self):
        """Tests renaming a self.tool."""
        tool = self._add_tool()
        tool.activate()
        expected_name = "ABC"
        expected_short_name = "abc"
        tool.rename(expected_name, "")
        # Check name
        self.assertEqual(expected_name, tool.name)  # item name
        self.assertEqual(expected_name, tool.get_icon().name())  # name item on Design View
        # Check data_dir
        expected_data_dir = os.path.join(self.project.items_dir, expected_short_name)
        self.assertEqual(expected_data_dir, tool.data_dir)  # Check data dir
        # Check that output_dir has been updated
        expected_output_dir = os.path.join(tool.data_dir, TOOL_OUTPUT_DIR)
        self.assertEqual(expected_output_dir, tool.output_dir)

    def test_load_tool_specification(self):
        """Test that specification is loaded into selections on Tool creation,
        and then shown in the ui when Tool is activated.
        """
        item_dict = {
            "type": "Tool",
            "description": "",
            "x": 0,
            "y": 0,
            "specification": "simple_exec",
            "execute_in_work": False,
        }
        tool = self._add_tool(item_dict)
        with mock.patch("spine_items.tool.tool.ToolSpecificationMenu") as mock_tool_spec_menu:
            mock_tool_spec_menu.side_effect = lambda *args: QMenu()
            tool.activate()
            self._assert_is_simple_exec_tool(tool)

    def test_save_and_restore_selections(self):
        """Test that selections are saved and restored when deactivating a Tool and activating it again."""
        item_dict = {"type": "Tool", "description": "", "x": 0, "y": 0, "specification": ""}
        tool = self._add_tool(item_dict)
        with mock.patch("spine_items.tool.tool.ToolSpecificationMenu") as mock_tool_spec_menu:
            mock_tool_spec_menu.side_effect = lambda *args: QMenu()
            tool.activate()
            self._assert_is_no_tool(tool)
            # Set the simple_exec tool specification manually
            tool._properties_ui.comboBox_tool.textActivated.emit("simple_exec")
            tool._properties_ui.radioButton_execute_in_source.setChecked(True)
            self._assert_is_simple_exec_tool(tool)
            tool.deactivate()
            tool.activate()
            self._assert_is_simple_exec_tool(tool)

    def test_find_input_files(self):
        """Test that input files are correctly found in resources
        when required input files and available resources are updated"""
        separator = os.sep
        item_dict = {"type": "Tool", "description": "", "x": 0, "y": 0, "specification": "simple_exec"}
        tool = self._add_tool(item_dict)
        url1 = os.path.join(self._temp_dir.name, "more_files", "input1.csv")
        url2 = os.path.join(self._temp_dir.name, "more_files", "data.csv")
        url3 = os.path.join(self._temp_dir.name, "more filess", "input1.csv")
        url4 = os.path.join(self._temp_dir.name, "other.csv")
        url5 = os.path.join(self._temp_dir.name, "other", "input2.csv")
        url6 = os.path.join(self._temp_dir.name, "input3.csv")
        expected_urls = {"url1": url1, "url2": url2, "url3": url3, "url4": url4, "url5": url5, "url6": url6}
        for key, url in expected_urls.items():
            i = url.find(separator)
            expected_urls[key] = url[:i] + separator + url[i:]
        resources = [
            ProjectItemResource("Exporter", "file", "first", url="file:///" + url1, metadata={}, filterable=False),
            ProjectItemResource("Exporter", "url", "second", url="file:///" + url2, metadata={}, filterable=False),
            ProjectItemResource("Exporter", "file", "third", url="file:///" + url3, metadata={}, filterable=False),
            ProjectItemResource("Exporter", "url", "fourth", url="file:///" + url4, metadata={}, filterable=False),
        ]
        result = tool._find_input_files(resources)
        expected = {"input1.csv": [expected_urls["url1"], expected_urls["url3"]], "input2.csv": None}
        self.assertEqual(2, len(result))
        self.assertEqual(expected["input2.csv"], result["input2.csv"])
        self.assertTrue(expected_urls["url3"] in result["input1.csv"] or expected_urls["url1"] in result["input1.csv"])
        resources.pop(0)
        resources.append(
            ProjectItemResource("Exporter", "file", "fifth", url="file:///" + url5, metadata={}, filterable=False)
        )
        result = tool._find_input_files(resources)
        expected = {"input2.csv": [expected_urls["url5"]], "input1.csv": [expected_urls["url3"]]}
        self.assertEqual(expected, result)
        resources.append(
            ProjectItemResource("Exporter", "file", "sixth", url="file:///" + url6, metadata={}, filterable=False)
        )
        tool.specification().inputfiles = set(["input2.csv", os.path.join(self._temp_dir.name, "input3.csv")])
        result = tool._find_input_files(resources)
        expected = {
            os.path.join(self._temp_dir.name, "input3.csv"): [expected_urls["url6"]],
            "input2.csv": [expected_urls["url5"]],
        }
        self.assertEqual(expected, result)

    def _add_tool(self, item_dict=None):
        if item_dict is None:
            item_dict = {"type": "Tool", "description": "", "x": 0, "y": 0}
        factory = ToolFactory()
        tool = factory.make_item("T", item_dict, self.toolbox, self.project)
        self._properties_widget = mock_finish_project_item_construction(factory, tool, self.toolbox)
        # Set model for tool combo box
        tool._properties_ui.comboBox_tool.setModel(self.model)
        self.project.get_item.return_value = tool
        return tool

    def _assert_is_simple_exec_tool(self, tool):
        """Assert that the given tool has the simple_exec specification."""
        # Check tool spec
        source_files = tool.specification().includes
        input_files = tool.specification().inputfiles
        opt_input_files = tool.specification().inputfiles_opt
        output_files = tool.specification().outputfiles
        self.assertEqual(source_files, ["main.sh"])
        self.assertIn("input1.csv", input_files)
        self.assertIn("input2.csv", input_files)
        self.assertEqual(opt_input_files, {"opt_input.csv"})
        self.assertIn("output1.csv", output_files)
        self.assertIn("output2.csv", output_files)
        # Check cmdline model
        spec_args_root = tool._cmdline_args_model.invisibleRootItem().child(0)
        self.assertEqual(spec_args_root.rowCount(), 1)
        cmdline_args = spec_args_root.child(0).text()
        self.assertEqual(cmdline_args, "<args>")
        # Check ui
        combox_text = tool._properties_ui.comboBox_tool.currentText()
        in_work = tool._properties_ui.radioButton_execute_in_work.isChecked()
        in_source = tool._properties_ui.radioButton_execute_in_source.isChecked()
        self.assertEqual(combox_text, "simple_exec")
        self.assertFalse(in_work)
        self.assertTrue(in_source)

    def _assert_is_no_tool(self, tool):
        """Assert that the given tool has no tool specification."""
        # Check cmdline model
        tool_args_root = tool._cmdline_args_model.invisibleRootItem().child(1)
        self.assertEqual(tool_args_root.rowCount(), 1)  # The "Type new arg here..." item
        # Check ui
        combox_text = tool._properties_ui.comboBox_tool.currentText()
        in_work = tool._properties_ui.radioButton_execute_in_work.isChecked()
        in_source = tool._properties_ui.radioButton_execute_in_source.isChecked()
        self.assertEqual(combox_text, "")
        self.assertTrue(in_work)
        self.assertFalse(in_source)


class _MockToolSpecModel(QStandardItemModel):
    # Create a dictionary of tool specifications to 'populate' the mock model
    def __init__(self, specifications):
        super().__init__()
        self._specifications = specifications
        self.invisibleRootItem().appendRows([QStandardItem(x) for x in self._specifications])


if __name__ == "__main__":
    unittest.main()
