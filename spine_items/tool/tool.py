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
Tool class.

:author: P. Savolainen (VTT)
:date:   19.12.2017
"""
import os
from PySide2.QtCore import Slot, QItemSelection
from PySide2.QtWidgets import QAction

from spinetoolbox.project_commands import SetItemSpecificationCommand
from spinetoolbox.project_item.project_item import ProjectItem
from spinetoolbox.helpers import open_url
from spinetoolbox.mvcmodels.file_list_models import FileListModel
from spine_engine.config import TOOL_OUTPUT_DIR
from spine_engine.project_item.project_item_resource import CmdLineArg, cmd_line_arg_from_dict, LabelArg
from .commands import UpdateToolExecuteInWorkCommand, UpdateToolOptionsCommand, StoreExecutionSettings
from .widgets.execution_settings_widgets import ExecutableExecutionSettingsWidget, PythonExecutionSettingsWidget
from ..commands import UpdateCmdLineArgsCommand, UpdateGroupIdCommand
from .item_info import ItemInfo
from .widgets.custom_menus import ToolSpecificationMenu
from .widgets.options_widgets import JuliaOptionsWidget
from .executable_item import ExecutableItem
from .utils import (
    flatten_file_path_duplicates,
    find_file,
    legacy_execution_settings_in_specification,
    default_execution_settings,
)
from ..models import ToolCommandLineArgsModel
from .output_resources import scan_for_resources


class Tool(ProjectItem):
    """The Tool project item."""

    def __init__(
        self,
        name,
        description,
        x,
        y,
        toolbox,
        project,
        specification_name="",
        execute_in_work=True,
        cmd_line_args=None,
        options=None,
        group_id=None,
        execution_settings=None,
    ):
        """
        Args:
            name (str): Project item name
            description (str): Project item description
            x (float): Initial X coordinate of item icon
            y (float): Initial Y coordinate of item icon
            toolbox (ToolboxUI): QMainWindow instance
            project (SpineToolboxProject): the project this item belongs to
            specification_name (str): Name of this Tool's Tool specification
            execute_in_work (bool): Execute associated Tool specification in work (True) or source directory (False)
            cmd_line_args (list, optional): Tool command line arguments
            options (dict, optional): misc tool options. At the moment it just holds the location of the julia sysimage
            execution_settings (dict, optional): execution settings
        """
        super().__init__(name, description, x, y, project)
        self._toolbox = toolbox
        self.execute_in_work = execute_in_work
        if cmd_line_args is None:
            cmd_line_args = []
        self.cmd_line_args = cmd_line_args
        self._cmdline_args_model = ToolCommandLineArgsModel(self)
        self._specification = self._project.get_specification(specification_name)
        if specification_name and self._specification is None:
            self._logger.msg_error.emit(
                f"Tool <b>{self.name}</b> should have a Tool specification "
                f"<b>{specification_name}</b> but it was not found"
            )
        self._group_id = group_id
        self._cmdline_args_model.args_updated.connect(self._push_update_cmd_line_args_command)
        self._populate_cmdline_args_model()
        self._input_file_model = FileListModel(header_label="Available resources", draggable=True)
        self.output_dir = os.path.join(self.data_dir, TOOL_OUTPUT_DIR)
        self._specification_menu = None
        self._options = options if options is not None else {}
        self._execution_settings = execution_settings
        if execution_settings is None and self._specification is not None:
            if legacy_execution_settings_in_specification(self._specification):
                self._execution_settings = self._specification.execution_settings
            else:
                self._execution_settings = default_execution_settings(self._specification.tooltype, toolbox.qsettings())
        self._resources_from_upstream = list()
        self._resources_from_downstream = list()

    def set_up(self):
        execute_in_work = self.execute_in_work
        super().set_up()
        self.do_update_execution_mode(execute_in_work)

    @property
    def group_id(self):
        return self._group_id

    def _get_options_widget(self):
        """Returns a widget to specify the options for this tool.
        It is embedded in the ui in ``self._update_tool_ui()``.

        Returns:
            OptionsWidget
        """
        tool_type = self._specification.tooltype
        options_widget = self._properties_ui.options_widgets.get(tool_type)
        if options_widget is None:
            constructors = {"julia": JuliaOptionsWidget}  # Add others as needed
            constructor = constructors.get(tool_type)
            if constructor is None:
                return None
            options_widget = constructor()
            self._properties_ui.options_widgets[tool_type] = options_widget
        options_widget.set_tool(self)
        options_widget.do_update_options(self._options)
        return options_widget

    def _get_execution_settings_widget(self):
        """Returns execution settings widget for the properties tab.

        Returns:
            ExecutionSettingsWidget: execution settings widget for current tool type
        """
        tool_type = self._specification.tooltype
        execution_settings_widget = self._properties_ui.execution_settings_widgets.get(tool_type)
        if execution_settings_widget is None:
            constructors = {"executable": ExecutableExecutionSettingsWidget, "python": PythonExecutionSettingsWidget}
            constructor = constructors.get(tool_type)
            if constructor is None:
                return None
            execution_settings_widget = constructor(self._toolbox.qsettings(), self._toolbox.undo_stack, self._logger)
            self._properties_ui.execution_settings_widgets[tool_type] = execution_settings_widget
        return execution_settings_widget

    @staticmethod
    def item_type():
        """See base class."""
        return ItemInfo.item_type()

    @staticmethod
    def item_category():
        """See base class."""
        return ItemInfo.item_category()

    def make_signal_handler_dict(self):
        """Returns a dictionary of all shared signals and their handlers.
        This is to enable simpler connecting and disconnecting."""
        s = super().make_signal_handler_dict()
        s[self._properties_ui.toolButton_tool_specification.clicked] = self.show_specification_window
        s[self._properties_ui.pushButton_tool_results.clicked] = self._open_results_directory
        s[self._properties_ui.comboBox_tool.textActivated] = self.update_specification
        s[self._properties_ui.radioButton_execute_in_work.toggled] = self.update_execution_mode
        s[self._properties_ui.toolButton_add_file_path_arg.clicked] = self._add_selected_file_path_args
        s[self._properties_ui.toolButton_remove_arg.clicked] = self._remove_arg
        s[
            self._properties_ui.treeView_input_files.selectionModel().selectionChanged
        ] = self._update_add_args_button_enabled
        s[
            self._properties_ui.treeView_cmdline_args.selectionModel().selectionChanged
        ] = self._update_remove_args_button_enabled
        s[self._properties_ui.lineEdit_group_id.editingFinished] = self._set_group_id
        return s

    @Slot()
    def _set_group_id(self):
        """Pushes a command to update group id whenever the user edits the line edit."""
        group_id = self._properties_ui.lineEdit_group_id.text()
        if not group_id:
            group_id = None
        if self._group_id == group_id:
            return
        self._toolbox.undo_stack.push(UpdateGroupIdCommand(self, group_id))

    def do_set_group_id(self, group_id):
        """Sets group id."""
        self._group_id = group_id
        if self._active:
            self._properties_ui.lineEdit_group_id.setText(group_id)

    @Slot(QItemSelection, QItemSelection)
    def _update_add_args_button_enabled(self, _selected, _deselected):
        self._do_update_add_args_button_enabled()

    def _do_update_add_args_button_enabled(self):
        enabled = self._properties_ui.treeView_input_files.selectionModel().hasSelection()
        self._properties_ui.toolButton_add_file_path_arg.setEnabled(enabled)

    @Slot(QItemSelection, QItemSelection)
    def _update_remove_args_button_enabled(self, _selected, _deselected):
        self._do_update_remove_args_button_enabled()

    def _do_update_remove_args_button_enabled(self):
        enabled = self._properties_ui.treeView_cmdline_args.selectionModel().hasSelection()
        self._properties_ui.toolButton_remove_arg.setEnabled(enabled)

    def restore_selections(self):
        """Restore selections into shared widgets when this project item is selected."""
        self._properties_ui.treeView_input_files.setModel(self._input_file_model)
        self._properties_ui.treeView_cmdline_args.setModel(self._cmdline_args_model)
        self._properties_ui.treeView_cmdline_args.expandAll()
        self.update_execute_in_work_button()
        self._update_tool_ui()
        self._do_update_add_args_button_enabled()
        self._do_update_remove_args_button_enabled()
        self._properties_ui.lineEdit_group_id.setText(self._group_id)

    @Slot(bool)
    def show_specification_window(self, _=True):
        """Opens the settings window."""
        self._toolbox.show_specification_form(self.item_type(), self.specification(), self)

    @Slot(bool)
    def update_execution_mode(self, checked):
        """Pushes a new UpdateToolExecuteInWorkCommand to the toolbox stack."""
        self._toolbox.undo_stack.push(UpdateToolExecuteInWorkCommand(self, checked))

    def do_update_execution_mode(self, execute_in_work):
        """Updates execute_in_work setting."""
        if self.execute_in_work == execute_in_work:
            return
        self.execute_in_work = execute_in_work
        self.update_execute_in_work_button()

    def update_execute_in_work_button(self):
        """Sets the execute in work radio button check state according to
        execute_in_work instance variable."""
        if not self._active:
            return
        self._properties_ui.radioButton_execute_in_work.blockSignals(True)
        self._properties_ui.radioButton_execute_in_source.blockSignals(True)
        if self.execute_in_work:
            self._properties_ui.radioButton_execute_in_work.setChecked(True)
        else:
            self._properties_ui.radioButton_execute_in_source.setChecked(True)
        self._properties_ui.radioButton_execute_in_work.blockSignals(False)
        self._properties_ui.radioButton_execute_in_source.blockSignals(False)

    @Slot(str)
    def update_specification(self, text):
        """Update Tool specification according to selection in the specification comboBox.

        Args:
            text (str): Tool specification name in the comboBox
        """
        spec = self._project.get_specification(text)
        self.set_specification(spec)

    @Slot(bool)
    def _remove_arg(self, _=False):
        removed_rows = [index.row() for index in self._properties_ui.treeView_cmdline_args.selectedIndexes()]
        cmd_line_args = [arg for row, arg in enumerate(self.cmd_line_args) if row not in removed_rows]
        self._push_update_cmd_line_args_command(cmd_line_args)

    @Slot(bool)
    def _add_selected_file_path_args(self, _=False):
        new_args = [LabelArg(index.data()) for index in self._properties_ui.treeView_input_files.selectedIndexes()]
        self._push_update_cmd_line_args_command(self.cmd_line_args + new_args)

    @Slot(list)
    def _push_update_cmd_line_args_command(self, cmd_line_args):
        if self.cmd_line_args == cmd_line_args:
            return
        self._toolbox.undo_stack.push(UpdateCmdLineArgsCommand(self, cmd_line_args))

    def update_cmd_line_args(self, cmd_line_args):
        """Updates instance cmd line args list and sets the list as text to the line edit widget.

        Args:
            cmd_line_args (list): Tool cmd line args
        """
        self.cmd_line_args = cmd_line_args
        self._populate_cmdline_args_model()
        self._check_notifications()

    def _populate_cmdline_args_model(self):
        spec_args = [CmdLineArg(arg) for arg in self._specification.cmdline_args] if self._specification else []
        tool_args = self.cmd_line_args
        self._cmdline_args_model.reset_model(spec_args, tool_args)
        if self._active:
            self._properties_ui.treeView_cmdline_args.setFocus()

    def undo_specification(self):
        if self._specification is None:
            return None
        undo_spec = self._specification.clone()
        undo_spec.execute_in_work = self.execute_in_work
        return undo_spec

    def set_specification(self, specification):
        """See base class."""
        if self._execution_settings is None:
            super().set_specification(specification)
            return
        self._toolbox.undo_stack.beginMacro(SetItemSpecificationCommand.make_text(self.name))
        self._toolbox.undo_stack.push(StoreExecutionSettings(self, self._execution_settings))
        super().set_specification(specification)
        self._toolbox.undo_stack.endMacro()

    def do_set_specification(self, specification):
        """see base class"""
        same_tool_type = (
            hasattr(specification, "tooltype")
            and self._specification is not None
            and self._specification.tooltype == specification.tooltype
        )
        if not super().do_set_specification(specification):
            return False
        self._populate_cmdline_args_model()
        self._update_execution_settings(same_tool_type)
        if self._active:
            self._update_tool_ui()
        if specification:
            self.do_update_execution_mode(specification.execute_in_work)
        self._resources_to_successors_changed()
        self._check_notifications()
        return True

    def update_options(self, options):
        """Pushes a new UpdateToolOptionsCommand to the toolbox stack."""
        self._toolbox.undo_stack.push(UpdateToolOptionsCommand(self, options))

    def do_set_options(self, options):
        """Sets options for this tool.

        Args:
            options (dict): The new options dictionary, must include *ALL* the options, not only changed ones.
        """
        self._options = options
        if self._active:
            _ = self._get_options_widget()

    def set_execution_settings(self, execution_settings):
        """Sets new execution settings.

        Args:
            execution_settings (dict): execution settings
        """
        self._execution_settings = execution_settings
        execution_settings_widget = self._get_execution_settings_widget()
        execution_settings_widget.set_settings(execution_settings)

    def _update_execution_settings(self, same_tool_type):
        """Updates execution settings after new specification has been set.

        Args:
            same_tool_type (bool): If True, assume that the tool type remains unchanged
        """
        if self._specification is None:
            self._execution_settings = None
            return
        elif same_tool_type:
            return
        if legacy_execution_settings_in_specification(self._specification):
            self._execution_settings = self._specification.execution_settings
        else:
            self._execution_settings = default_execution_settings(
                self._specification.tooltype, self._toolbox.qsettings()
            )

    def _update_tool_ui(self):
        """Updates Tool properties UI. Used when Tool specification is changed.."""
        options_layout_item = self._properties_ui.horizontalLayout_options.takeAt(0)
        if options_layout_item is not None:
            options_layout_item.widget().hide()
        execution_settings_layout_item = self._properties_ui.execution_settings_placeholder_layout.takeAt(0)
        if execution_settings_layout_item is not None:
            execution_settings_layout_item.widget().hide()
        if not self.specification():
            self._properties_ui.comboBox_tool.setCurrentIndex(-1)
            self.do_update_execution_mode(True)
            self._properties_ui.toolButton_tool_specification.setMenu(None)
            return
        self._properties_ui.comboBox_tool.setCurrentText(self.specification().name)
        self._update_specification_menu()
        self._properties_ui.toolButton_tool_specification.setMenu(self._specification_menu)
        options_widget = self._get_options_widget()
        if options_widget is not None:
            self._properties_ui.horizontalLayout_options.addWidget(options_widget)
            options_widget.show()
        execution_settings_widget = self._get_execution_settings_widget()
        if execution_settings_widget is not None:
            execution_settings_widget.set_settings(self._execution_settings)
            self._properties_ui.execution_settings_placeholder_layout.addWidget(execution_settings_widget)
            execution_settings_widget.show()

    def _update_specification_menu(self):
        spec_model_index = self._toolbox.specification_model.specification_index(self.specification().name)
        self._specification_menu = ToolSpecificationMenu(self._toolbox, spec_model_index, self)
        self._specification_menu.setTitle("Specification...")

    @Slot(bool)
    def _open_results_directory(self, _):
        """Open output directory in file browser."""
        if not os.path.exists(self.output_dir):
            self._logger.msg_warning.emit(f"Tool <b>{self.name}</b> has no results. Click Execute to generate them.")
            return
        url = "file:///" + self.output_dir
        # noinspection PyTypeChecker, PyCallByClass, PyArgumentList
        res = open_url(url)
        if not res:
            self._logger.msg_error.emit(f"Failed to open directory: {self.output_dir}")

    def specification(self):
        """Returns Tool specification."""
        return self._specification

    def resources_for_direct_successors(self):
        """See base class"""
        return scan_for_resources(self, self.specification(), self.output_dir)

    @property
    def executable_class(self):
        return ExecutableItem

    def _find_input_files(self, resources):
        """Iterates files in required input files model and looks for them in the given resources.

        Args:
            resources (list): resources available

        Returns:
            Dictionary mapping required files to path where they are found, or to None if not found
        """
        if not self.specification():
            return {}
        file_paths = dict()
        for req_file_path in self.specification().inputfiles:
            # Just get the filename if there is a path attached to the file
            _, filename = os.path.split(req_file_path)
            if not filename:
                # It's a directory
                continue
            file_paths[req_file_path] = find_file(filename, resources)
        return file_paths

    def _check_notifications(self):
        """See base class."""
        self.clear_notifications()
        if not self.specification():
            self.add_notification("This Tool does not have a specification. Set it in the Tool Properties Panel.")
        elif self.specification().includes and not self.specification().path:
            n = self.specification().name
            self.add_notification(
                f"Tool specification <b>{n}</b> path does not exist. Fix this in Tool specification editor."
            )
        duplicates = self._input_file_model.duplicate_paths()
        if duplicates:
            self.add_notification("Duplicate input files:<br>{}".format("<br>".join(duplicates)))
        file_paths = self._find_input_files(self._resources_from_upstream + self._resources_from_downstream)
        file_paths = flatten_file_path_duplicates(file_paths, self._logger)
        not_found = [k for k, v in file_paths.items() if v is None]
        if not_found:
            self.add_notification(
                "File(s) {0} needed to execute this Tool are not provided by any input item. "
                "Connect items that provide the required files to this Tool.".format(", ".join(not_found))
            )
        missing_args = ", ".join(arg.arg for arg in self.cmd_line_args if isinstance(arg, LabelArg) and arg.missing)
        if missing_args:
            self.add_notification(
                f"The following command line argument(s) don't match any available resources: {missing_args}"
            )

    def handle_execution_successful(self, execution_direction, engine_state):
        """See base class."""
        if execution_direction != "FORWARD":
            return
        self._resources_to_successors_changed()

    def upstream_resources_updated(self, resources):
        """See base class."""
        self._resources_from_upstream = resources
        self._update_files_and_cmd_line_args()

    def replace_resources_from_upstream(self, old, new):
        """See base class."""
        self._replace_resources(old, new, self._resources_from_upstream)

    def downstream_resources_updated(self, resources):
        """See base class."""
        self._resources_from_downstream = resources
        self._update_files_and_cmd_line_args()

    def replace_resources_from_downstream(self, old, new):
        """See base class."""
        self._replace_resources(old, new, self._resources_from_downstream)

    def _replace_resources(self, old_resources, new_resources, resource_list):
        """Replaces resources.

        Modifies ``resource_list`` in-place!

        Args:
            old_resources (list of ProjectItemResource): old resources
            new_resources (list of ProjectItemResource): new resources
            resource_list (list of ProjectItemResource): current downstream or upstream resources
        """
        for old, new in zip(old_resources, new_resources):
            for i, resource in enumerate(resource_list):
                if resource == old:
                    resource_list[i] = new
                    break
            for i, arg in enumerate(self.cmd_line_args):
                if arg.arg == old.label:
                    self.cmd_line_args[i] = LabelArg(new.label)
        self._input_file_model.update(self._resources_from_upstream + self._resources_from_downstream)
        self.update_cmd_line_args(self.cmd_line_args)

    def _update_files_and_cmd_line_args(self):
        """Updates the file model and command line arguments."""
        resources = self._resources_from_upstream + self._resources_from_downstream
        self._input_file_model.update(resources)
        update_args = list()
        resource_labels = {resource.label for resource in resources}
        for arg in self.cmd_line_args:
            if arg.arg in resource_labels:
                arg.missing = False
            elif isinstance(arg, LabelArg):
                # Arg may refer to legacy Data connection resource labels that weren't prefixed by <project> or <data>
                legacy_arg_converted = False
                for label in resource_labels:
                    if label.startswith("<") and label.endswith(arg.arg):
                        legacy_arg_converted = True
                        arg.arg = label
                        break
                if not legacy_arg_converted:
                    arg.missing = True
            update_args.append(arg)
        self.update_cmd_line_args(update_args)

    def item_dict(self):
        """Returns a dictionary corresponding to this item."""
        d = super().item_dict()
        if not self.specification():
            d["specification"] = ""
        else:
            d["specification"] = self.specification().name
        d["execute_in_work"] = self.execute_in_work
        d["cmd_line_args"] = [arg.to_dict() for arg in self.cmd_line_args]
        if self._execution_settings is not None:
            d["execution_settings"] = self._execution_settings
        if self._options:
            d["options"] = self._options
        if self._group_id:
            d["group_id"] = self._group_id
        return d

    @staticmethod
    def item_dict_local_entries():
        """See base class."""
        return [("execution_settings",)]

    @staticmethod
    def from_dict(name, item_dict, toolbox, project):
        """See base class."""
        description, x, y = ProjectItem.parse_item_dict(item_dict)
        specification_name = item_dict.get("specification", "")
        execute_in_work = item_dict.get("execute_in_work", True)
        cmd_line_args = item_dict.get("cmd_line_args", [])
        cmd_line_args = [cmd_line_arg_from_dict(arg) for arg in cmd_line_args]
        options = item_dict.get("options", {})
        execution_settings = item_dict.get("execution_settings")
        group_id = item_dict.get("group_id")
        return Tool(
            name,
            description,
            x,
            y,
            toolbox,
            project,
            specification_name,
            execute_in_work,
            cmd_line_args,
            options,
            group_id,
            execution_settings,
        )

    def rename(self, new_name, rename_data_dir_message):
        """See base class."""
        if not super().rename(new_name, rename_data_dir_message):
            return False
        self.output_dir = os.path.join(self.data_dir, TOOL_OUTPUT_DIR)
        return True

    def notify_destination(self, source_item):
        """See base class."""
        if source_item.item_type() == "Data Store":
            self._logger.msg.emit(
                f"Link established. Data Store <b>{source_item.name}</b> url will "
                f"be passed to Tool <b>{self.name}</b> when executing."
            )
        elif source_item.item_type() == "Data Connection":
            self._logger.msg.emit(
                f"Link established. Tool <b>{self.name}</b> will look for input "
                f"files from <b>{source_item.name}</b>'s references and data directory."
            )
        elif source_item.item_type() in ("GdxExporter", "Exporter"):
            self._logger.msg.emit(
                f"Link established. The file exported by <b>{source_item.name}</b> are now "
                f"available in <b>{self.name}</b>."
            )
        elif source_item.item_type() in ["Data Transformer", "Tool"]:
            self._logger.msg.emit("Link established")
        elif source_item.item_type() == "Gimlet":
            self._logger.msg.emit(
                f"Link established. Tool <b>{self.name}</b> will look for input "
                f"files from <b>{source_item.name}</b>."
            )
        else:
            super().notify_destination(source_item)

    def actions(self):
        # pylint: disable=attribute-defined-outside-init
        if self.specification() is not None:
            if self._specification_menu is None:
                self._update_specification_menu()
            self._actions = [self._specification_menu.menuAction()]
        else:
            action = QAction("New specification")
            action.triggered.connect(self.show_specification_window)
            self._actions = [action]
        self._actions.append(QAction("Open results directory"))
        self._actions[-1].triggered.connect(self._open_results_directory)
        return self._actions

    @staticmethod
    def upgrade_v1_to_v2(item_name, item_dict):
        """Upgrades item's dictionary from v1 to v2.

        Changes:
        - 'tool' key is renamed to 'specification'

        Args:
            item_name (str): item's name
            item_dict (dict): Version 1 item dictionary

        Returns:
            dict: Version 2 Tool dictionary
        """
        item_dict["specification"] = item_dict.pop("tool", "")
        return item_dict
