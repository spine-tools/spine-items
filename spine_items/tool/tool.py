######################################################################################################################
# Copyright (C) 2017-2020 Spine project consortium
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
import pathlib
from collections import Counter
from PySide2.QtCore import Slot
from spinetoolbox.project_item.project_item import ProjectItem
from spinetoolbox.helpers import open_url
from spine_engine.project_item.project_item_resource import ProjectItemResource
from spine_engine.config import TOOL_OUTPUT_DIR
from spine_engine.utils.command_line_arguments import split_cmdline_args
from spine_engine.utils.serialization import serialize_url, deserialize_path
from .commands import UpdateToolExecuteInWorkCommand
from ..commands import UpdateCmdLineArgsCommand
from .item_info import ItemInfo
from .widgets.custom_menus import ToolContextMenu, ToolSpecificationMenu
from .executable_item import ExecutableItem
from .utils import flatten_file_path_duplicates, find_file, find_last_output_files, is_pattern, make_label
from ..models import ToolCommandLineArgsModel, InputFileListModel


class Tool(ProjectItem):
    def __init__(
        self,
        name,
        description,
        x,
        y,
        toolbox,
        project,
        logger,
        specification_name="",
        execute_in_work=True,
        cmd_line_args=None,
    ):
        """Tool class.

        Args:
            name (str): Object name
            description (str): Object description
            x (float): Initial X coordinate of item icon
            y (float): Initial Y coordinate of item icon
            toolbox (ToolboxUI): QMainWindow instance
            project (SpineToolboxProject): the project this item belongs to
            logger (LoggerInterface): a logger instance
            specification_name (str): Name of this Tool's Tool specification
            execute_in_work (bool): Execute associated Tool specification in work (True) or source directory (False)
            cmd_line_args (list, optional): Tool command line arguments
        """
        super().__init__(name, description, x, y, project, logger)
        self._toolbox = toolbox
        self.execute_in_work = None
        self.undo_execute_in_work = None
        self._specification = self._toolbox.specification_model.find_specification(specification_name)
        if specification_name and not self._specification:
            self._logger.msg_error.emit(
                f"Tool <b>{self.name}</b> should have a Tool specification <b>{specification_name}</b> but it was not found"
            )
        if cmd_line_args is None:
            cmd_line_args = []
        self.cmd_line_args = cmd_line_args
        self._cmdline_args_model = ToolCommandLineArgsModel(self)
        self._cmdline_args_model.args_updated.connect(self._push_update_cmd_line_args_command)
        self._populate_cmdline_args_model()
        self._input_file_model = InputFileListModel(header_label="Available resources", checkable=False)
        self.specification_options_popup_menu = None
        # Make directory for results
        self.output_dir = os.path.join(self.data_dir, TOOL_OUTPUT_DIR)
        self.do_set_specification(self._specification)
        self.do_update_execution_mode(execute_in_work)

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
        s[self._properties_ui.toolButton_tool_open_dir.clicked] = lambda checked=False: self.open_directory()
        s[self._properties_ui.pushButton_tool_results.clicked] = self.open_results
        s[self._properties_ui.comboBox_tool.textActivated] = self.update_specification
        s[self._properties_ui.radioButton_execute_in_work.toggled] = self.update_execution_mode
        s[self._properties_ui.toolButton_add_file_path_arg.clicked] = self._add_selected_file_path_args
        s[self._properties_ui.toolButton_remove_arg.clicked] = self._remove_arg
        return s

    def restore_selections(self):
        """Restore selections into shared widgets when this project item is selected."""
        self._properties_ui.label_tool_name.setText(self.name)
        self._properties_ui.treeView_input_files.setModel(self._input_file_model)
        self._properties_ui.treeView_cmdline_args.setModel(self._cmdline_args_model)
        self._properties_ui.treeView_cmdline_args.expandAll()
        self.update_execute_in_work_button()
        self._update_tool_ui()

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
        if self.execute_in_work:
            self._properties_ui.radioButton_execute_in_work.setChecked(True)
        else:
            self._properties_ui.radioButton_execute_in_source.setChecked(True)
        self._properties_ui.radioButton_execute_in_work.blockSignals(False)

    @Slot(str)
    def update_specification(self, text):
        """Update Tool specification according to selection in the specification comboBox.

        Args:
            text (str): Tool specification name in the comboBox
        """
        spec = self._toolbox.specification_model.find_specification(text)
        self.set_specification(spec)

    @Slot(bool)
    def _remove_arg(self, _=False):
        removed_rows = [index.row() for index in self._properties_ui.treeView_cmdline_args.selectedIndexes()]
        cmd_line_args = [arg for row, arg in enumerate(self.cmd_line_args) if row not in removed_rows]
        self._push_update_cmd_line_args_command(cmd_line_args)

    @Slot(bool)
    def _add_selected_file_path_args(self, _=False):
        new_args = [index.data() for index in self._properties_ui.treeView_input_files.selectedIndexes()]
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

    def _populate_cmdline_args_model(self):
        spec_args = self.specification().cmdline_args if self.specification() else []
        tool_args = self.cmd_line_args
        if self._active:
            pos = self._properties_ui.treeView_cmdline_args.verticalScrollBar().sliderPosition()
        self._cmdline_args_model.reset_model(spec_args, tool_args)
        if self._active:
            self._properties_ui.treeView_cmdline_args.expandAll()
            self._properties_ui.treeView_cmdline_args.verticalScrollBar().setSliderPosition(pos)
            # TODO: self._properties_ui.treeView_cmdline_args.setFocus()

    def do_set_specification(self, specification):
        """see base class"""
        super().do_set_specification(specification)
        self._populate_cmdline_args_model()
        self._update_tool_ui()
        if self.undo_execute_in_work is None:
            self.undo_execute_in_work = self.execute_in_work
        if specification:
            self.do_update_execution_mode(specification.execute_in_work)
        self.item_changed.emit()

    def undo_set_specification(self):
        """see base class"""
        super().undo_set_specification()
        self.do_update_execution_mode(self.undo_execute_in_work)
        self.undo_execute_in_work = None

    def _update_tool_ui(self):
        """Updates Tool UI to show Tool specification details. Used when Tool specification is changed.
        Overrides execution mode (work or source) with the specification default."""
        if not self._active:
            return
        if not self._properties_ui:
            return
        if not self.specification():
            self._properties_ui.comboBox_tool.setCurrentIndex(-1)
            self.do_update_execution_mode(True)
            spec_model_index = None
            self.do_update_execution_mode(True)
            self._properties_ui.toolButton_tool_specification.setEnabled(False)
        else:
            self._properties_ui.comboBox_tool.setCurrentText(self.specification().name)
            spec_model_index = self._toolbox.specification_model.specification_index(self.specification().name)
            self.specification_options_popup_menu = ToolSpecificationMenu(self._toolbox, spec_model_index)
            self._properties_ui.toolButton_tool_specification.setEnabled(True)
            self._properties_ui.toolButton_tool_specification.setMenu(self.specification_options_popup_menu)

    @Slot(bool)
    def open_results(self, checked=False):
        """Open output directory in file browser."""
        if not os.path.exists(self.output_dir):
            self._logger.msg_warning.emit(f"Tool <b>{self.name}</b> has no results. Click Execute to generate them.")
            return
        url = "file:///" + self.output_dir
        # noinspection PyTypeChecker, PyCallByClass, PyArgumentList
        res = open_url(url)
        if not res:
            self._logger.msg_error.emit(f"Failed to open directory: {self.output_dir}")

    @Slot()
    def edit_specification(self):
        """Open Tool specification editor for the Tool specification attached to this Tool."""
        if not self.specification():
            return
        index = self._toolbox.specification_model.specification_index(self.specification().name)
        self._toolbox.edit_specification(index)

    @Slot()
    def open_specification_file(self):
        """Open Tool specification file."""
        if not self.specification():
            return
        index = self._toolbox.specification_model.specification_index(self.specification().name)
        self._toolbox.open_specification_file(index)

    @Slot()
    def open_main_program_file(self):
        """Open Tool specification main program file in an external text edit application."""
        if not self.specification():
            return
        file_path = self.specification().get_main_program_file_path()
        if file_path is None:
            return
        main_program_url = "file:///" + file_path
        res = open_url(main_program_url)
        if not res:
            filename, file_extension = os.path.splitext(file_path)
            self._logger.msg_error.emit(
                "Unable to open Tool specification main program file {0}. "
                "Make sure that <b>{1}</b> "
                "files are associated with an editor. E.g. on Windows "
                "10, go to Control Panel -> Default Programs to do this.".format(filename, file_extension)
            )

    @Slot()
    def open_main_directory(self):
        """Open directory where the Tool specification main program is located in file explorer."""
        if not self.specification():
            return
        dir_url = "file:///" + self.specification().path
        open_url(dir_url)

    def specification(self):
        """Returns Tool specification."""
        return self._specification

    def update_name_label(self):
        """Update Tool tab name label. Used only when renaming project items."""
        self._properties_ui.label_tool_name.setText(self.name)

    def resources_for_direct_successors(self):
        """
        Returns a list of resources, i.e. the outputs defined by the tool specification.

        The output files are available only after tool has been executed,
        therefore the resource type is 'transient_file' or 'file_pattern'.
        A 'file_pattern' type resource is returned only if the pattern doesn't match any output file.
        For 'transient_file' resources, the url attribute is set to an empty string if the file doesn't exist yet,
        otherwise it points to a file from most recent execution.
        The metadata attribute's label key gives the base name or file pattern of the output file.

        Returns:
            list: a list of Tool's output resources
        """
        if self.specification() is None:
            self._logger.msg_error.emit(
                f"Fail to determine <b>{self.name}</b> resources for direct successors. Tool specification is missing."
            )
            return []
        resources = list()
        last_output_files = find_last_output_files(self.specification().outputfiles, self.output_dir)
        for out_file_label in self.specification().outputfiles:
            latest_files = last_output_files.get(out_file_label, list())
            if is_pattern(out_file_label):
                if not latest_files:
                    metadata = {"label": make_label(out_file_label)}
                    resource = ProjectItemResource(self, "file_pattern", metadata=metadata)
                    resources.append(resource)
                else:
                    for out_file in latest_files:
                        file_url = pathlib.Path(out_file.path).as_uri()
                        metadata = {"label": make_label(out_file.label)}
                        resource = ProjectItemResource(self, "transient_file", url=file_url, metadata=metadata)
                        resources.append(resource)
            else:
                if not latest_files:
                    metadata = {"label": make_label(out_file_label)}
                    resource = ProjectItemResource(self, "transient_file", metadata=metadata)
                    resources.append(resource)
                else:
                    latest_file = latest_files[0]  # Not a pattern; there should be only one element in the list.
                    file_url = pathlib.Path(latest_file.path).as_uri()
                    metadata = {"label": make_label(latest_file.label)}
                    resource = ProjectItemResource(self, "transient_file", url=file_url, metadata=metadata)
                    resources.append(resource)
        return resources

    def execution_item(self):
        """Creates project item's execution counterpart."""
        work_dir = self._toolbox.qsettings().value("appSettings/workDir") if self.execute_in_work else None
        return ExecutableItem(
            self.name, work_dir, self.output_dir, self._specification, self.cmd_line_args, self._logger
        )

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

    def _do_handle_dag_changed(self, upstream_resources, downstream_resources):
        """See base class."""
        if not self.specification():
            self.add_notification("This Tool does not have a specification. Set it in the Tool Properties Panel.")
        resources = upstream_resources + downstream_resources
        self._input_file_model.update(resources)
        if not resources:
            self.add_notification(
                "This Tool does not have any input data. Connect Items to this Tool to use their data as input."
            )
        self._notify_if_duplicate_file_paths()
        file_paths = self._find_input_files(resources)
        file_paths = flatten_file_path_duplicates(file_paths, self._logger)
        not_found = [k for k, v in file_paths.items() if v is None]
        if not_found:
            self.add_notification(
                "File(s) {0} needed to execute this Tool are not provided by any input item. "
                "Connect items that provide the required files to this Tool.".format(", ".join(not_found))
            )
        # Update cmdline args
        cmd_line_args = self.cmd_line_args.copy()
        for resource in resources:
            updated_from = resource.metadata.get("updated_from")
            try:
                i = cmd_line_args.index(updated_from)
            except ValueError:
                continue
            cmd_line_args[i] = resource.label
        self.update_cmd_line_args(cmd_line_args)

    def _notify_if_duplicate_file_paths(self):
        """Adds a notification if file_list contains duplicate entries."""
        labels = list()
        for item in self._input_file_model.files:
            labels.append(item.label)
        file_counter = Counter(labels)
        duplicates = list()
        for label, count in file_counter.items():
            if count > 1:
                duplicates.append(label)
        if duplicates:
            self.add_notification("Duplicate input files:<br>{}".format("<br>".join(duplicates)))

    def item_dict(self):
        """Returns a dictionary corresponding to this item."""
        d = super().item_dict()
        if not self.specification():
            d["specification"] = ""
        else:
            d["specification"] = self.specification().name
        d["execute_in_work"] = self.execute_in_work
        # NOTE: We enclose the arguments in quotes because that preserves the args that have spaces
        cmd_line_args = [f'"{arg}"' for arg in self.cmd_line_args]
        cmd_line_args = split_cmdline_args(" ".join(cmd_line_args))
        d["cmd_line_args"] = [serialize_url(arg, self._project.project_dir) for arg in cmd_line_args]
        return d

    @staticmethod
    def from_dict(name, item_dict, toolbox, project, logger):
        """See base class."""
        description, x, y = ProjectItem.parse_item_dict(item_dict)
        specification_name = item_dict.get("specification", "")
        execute_in_work = item_dict.get("execute_in_work", True)
        cmd_line_args = item_dict.get("cmd_line_args", [])
        cmd_line_args = [deserialize_path(arg, project.project_dir) for arg in cmd_line_args]
        return Tool(
            name, description, x, y, toolbox, project, logger, specification_name, execute_in_work, cmd_line_args
        )

    def custom_context_menu(self, parent, pos):
        """Returns the context menu for this item.

        Args:
            parent (QWidget): The widget that is controlling the menu
            pos (QPoint): Position on screen
        """
        return ToolContextMenu(parent, self, pos)

    def apply_context_menu_action(self, parent, action):
        """Applies given action from context menu. Implement in subclasses as needed.

        Args:
            parent (QWidget): The widget that is controlling the menu
            action (str): The selected action
        """
        super().apply_context_menu_action(parent, action)
        if action == "Results...":
            self.open_results()
        elif action == "Stop":
            self.stop_execution()  # Proceed with stopping
        elif action == "Edit Tool specification":
            self.edit_specification()
        elif action == "Edit main program file...":
            self.open_main_program_file()

    def rename(self, new_name):
        """Rename this item.

        Args:
            new_name (str): New name

        Returns:
            bool: Boolean value depending on success
        """
        if not super().rename(new_name):
            return False
        self.output_dir = os.path.join(self.data_dir, TOOL_OUTPUT_DIR)
        self.item_changed.emit()
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
        elif source_item.item_type() == "Exporter":
            self._logger.msg.emit(
                f"Link established. The file exported by <b>{source_item.name}</b> will "
                f"be passed to Tool <b>{self.name}</b> when executing."
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

    @staticmethod
    def default_name_prefix():
        """see base class"""
        return "Tool"

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
