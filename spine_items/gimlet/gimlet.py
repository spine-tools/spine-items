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
Gimlet class module.

:author: P. Savolainen (VTT)
:date:   15.4.2020
"""
import os
from PySide2.QtCore import QModelIndex, Slot, Qt
from spinetoolbox.project_item.project_item import ProjectItem
from spine_engine.config import GIMLET_WORK_DIR_NAME
from .item_info import ItemInfo
from .executable_item import ExecutableItem
from .commands import UpdateShellCheckBoxCommand, UpdateShellComboboxCommand, UpdatecmdCommand, UpdateWorkDirModeCommand
from ..commands import ChangeItemSelectionCommand, UpdateCmdLineArgsCommand
from ..models import GimletCommandLineArgsModel, CheckableFileListModel
from ..utils import cmd_line_arg_from_dict, LabelArg


class Gimlet(ProjectItem):
    """Gimlet class."""

    def __init__(
        self,
        name,
        description,
        x,
        y,
        toolbox,
        project,
        use_shell=True,
        shell_index=0,
        cmd="",
        cmd_line_args=None,
        selections=None,
        work_dir_mode=True,
    ):
        """
        Args:
            name (str): Project item name
            description (str): Description
            x (float): Initial X coordinate of item icon
            y (float): Initial Y coordinate of item icon
            toolbox (ToolboxUI): QMainWindow instance
            project (SpineToolboxProject): Project this item belongs to
            use_shell (bool): Use shell flag
            shell_index (int): Selected shell as index
            cmd (str): Command that this Gimlet executes at run time
            cmd_line_args (list, optional): Gimlet command line arguments
            selections (dict, optional): A mapping from file label to boolean 'checked' flag
            work_dir_mode (bool): True uses Gimlet's default work dir, False uses a unique work dir on every execution
        """
        super().__init__(name, description, x, y, project)
        self._toolbox = toolbox
        self._file_model = CheckableFileListModel(header_label="Available resources", draggable=True)
        self._resources_from_downstream = list()
        self._resources_from_upstream = list()
        self.use_shell = use_shell
        self.shell_index = shell_index
        self.cmd = cmd
        if cmd_line_args is None:
            cmd_line_args = []
        self.cmd_line_args = cmd_line_args
        self._cmdline_args_model = GimletCommandLineArgsModel(self)
        self._cmdline_args_model.args_updated.connect(self._push_update_cmd_line_args_command)
        self._populate_cmdline_args_model()
        self._file_model.set_initial_state(selections if selections is not None else dict())
        self._file_model.checked_state_changed.connect(self._push_file_selection_change_to_undo_stack)
        self._work_dir_mode = None
        self.update_work_dir_mode(work_dir_mode)
        self.default_gimlet_work_dir = os.path.join(self.data_dir, GIMLET_WORK_DIR_NAME)

    @staticmethod
    def item_type():
        """See base class."""
        return ItemInfo.item_type()

    @staticmethod
    def item_category():
        """See base class."""
        return ItemInfo.item_category()

    @property
    def executable_class(self):
        return ExecutableItem

    def make_signal_handler_dict(self):
        """Returns a dictionary of all shared signals and their handlers.
        This is to enable simpler connecting and disconnecting."""
        s = super().make_signal_handler_dict()
        s[self._properties_ui.toolButton_gimlet_open_dir.clicked] = lambda checked=False: self.open_directory()
        s[self._properties_ui.checkBox_shell.stateChanged] = self.shell_checkbox_clicked
        s[self._properties_ui.comboBox_shell.activated] = self.shell_combobox_index_changed
        s[self._properties_ui.lineEdit_cmd.editingFinished] = self.cmd_edited
        s[self._properties_ui.radioButton_default.toggled] = self.push_work_dir_mode_cmd
        s[self._properties_ui.toolButton_add_file_path_arg.clicked] = self._add_selected_file_path_args
        s[self._properties_ui.toolButton_remove_arg.clicked] = self._remove_arg
        return s

    def restore_selections(self):
        """Restores selections into shared widgets when this project item is selected."""
        self._properties_ui.label_gimlet_name.setText(self.name)
        if not self._active:
            return
        self._properties_ui.treeView_cmdline_args.setModel(self._cmdline_args_model)
        self._properties_ui.treeView_files.setModel(self._file_model)
        self._properties_ui.checkBox_shell.setChecked(self.use_shell)
        if self.use_shell:
            self._properties_ui.comboBox_shell.setEnabled(True)
        else:
            self._properties_ui.comboBox_shell.setEnabled(False)
        self._properties_ui.comboBox_shell.setCurrentIndex(self.shell_index)
        self._properties_ui.lineEdit_cmd.setText(self.cmd)
        self.update_work_dir_button_state()

    def save_selections(self):
        """Saves selections in shared widgets for this project item into instance variables."""
        self._properties_ui.treeView_files.setModel(None)

    @Slot(int)
    def shell_checkbox_clicked(self, state):
        """Pushes a new shell check box command to undo stack.
        Pushing the command calls the commands redo method.

        Args:
            state (int): New check box state (Qt.CheckState enum)
        """
        use_shell = state == Qt.Checked
        if self.use_shell == use_shell:
            return
        self._toolbox.undo_stack.push(UpdateShellCheckBoxCommand(self, use_shell))

    def toggle_shell_state(self, use_shell):
        """Sets the use shell check box state. Disables shell
        combobox when shell check box is unchecked.

        Args:
            use_shell (bool): New check box state
        """
        self.use_shell = use_shell
        if not self._active:
            return
        # This does not trigger the stateChanged signal.
        self._properties_ui.checkBox_shell.setCheckState(Qt.Checked if use_shell else Qt.Unchecked)
        self._properties_ui.comboBox_shell.setEnabled(bool(use_shell))

    @Slot(int)
    def shell_combobox_index_changed(self, ind):
        """Pushes a shell combobox selection changed command to
        undo stack, which in turn calls set_shell_combobox_index() below.

        Args:
            ind (int): New index in combo box
        """
        if self.shell_index == ind:
            return
        self._toolbox.undo_stack.push(UpdateShellComboboxCommand(self, ind))

    def set_shell_combobox_index(self, ind):
        """Sets new index to shell combobox.

        Args:
            ind (int): New index in shell combo box
        """
        self.shell_index = ind
        if not self._active:
            return
        self._properties_ui.comboBox_shell.setCurrentIndex(ind)

    @Slot()
    def cmd_edited(self):
        """Updates the command instance variable when user has
        finished editing text in the line edit."""
        cmd = self._properties_ui.lineEdit_cmd.text().strip()
        if self.cmd == cmd:
            return
        self._toolbox.undo_stack.push(UpdatecmdCommand(self, cmd))

    def set_command(self, txt):
        self.cmd = txt
        if not self._active:
            return
        self._properties_ui.lineEdit_cmd.setText(txt)

    @Slot(bool)
    def _remove_arg(self, _=False):
        removed_rows = [index.row() for index in self._properties_ui.treeView_cmdline_args.selectedIndexes()]
        cmd_line_args = [arg for row, arg in enumerate(self.cmd_line_args) if row not in removed_rows]
        self._push_update_cmd_line_args_command(cmd_line_args)

    @Slot(bool)
    def _add_selected_file_path_args(self, _=False):
        new_args = [LabelArg(index.data()) for index in self._properties_ui.treeView_files.selectedIndexes()]
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
        self._cmdline_args_model.reset_model(self.cmd_line_args)
        if self._active:
            self._properties_ui.treeView_cmdline_args.setFocus()

    @Slot(QModelIndex, bool)
    def _push_file_selection_change_to_undo_stack(self, index, checked):
        """Makes changes to file selection undoable."""
        self._toolbox.undo_stack.push(ChangeItemSelectionCommand(self.name, self._file_model, index, checked))

    @Slot(bool)
    def push_work_dir_mode_cmd(self, checked):
        """Pushes a new UpdateWorkDirModeCommand to the undo stack."""
        self._toolbox.undo_stack.push(UpdateWorkDirModeCommand(self, checked))

    def update_work_dir_mode(self, work_dir_mode):
        """Updates work_dir_mode setting.

        Args:
            work_dir_mode (bool): If True, work dir is set to this Gimlet's data dir,
            IF False, a unique work dir is created for every execution.
        """
        if self._work_dir_mode == work_dir_mode:
            return
        self._work_dir_mode = work_dir_mode
        self.update_work_dir_button_state()

    def update_work_dir_button_state(self):
        """Sets the work dir radio button check state according to
        work_dir_mode instance variable."""
        if not self._active:
            return
        self._properties_ui.radioButton_default.blockSignals(True)
        if self._work_dir_mode:
            self._properties_ui.radioButton_default.setChecked(True)
        else:
            self._properties_ui.radioButton_unique.setChecked(True)
        self._properties_ui.radioButton_default.blockSignals(False)

    def upstream_resources_updated(self, resources):
        self._resources_from_upstream = list(resources)
        self._update_files_and_cmd_line_args()

    def replace_resource_from_upstream(self, old, new):
        """See base class."""
        self._replace_resources(old, new, self._resources_from_upstream)

    def downstream_resources_updated(self, resources):
        self._resources_from_downstream = list(resources)
        self._update_files_and_cmd_line_args()

    def replace_resource_from_downstream(self, old, new):
        """See base class."""
        self._replace_resources(old, new, self._resources_from_downstream)

    def _replace_resources(self, old, new, resource_list):
        """Replaces resources.

        Modifies ``resource_list`` in-place!

        Args:
            old (ProjectItemResource): old resource
            new (ProjectItemResource): new resource
            resource_list (list of ProjectItemResource): current downstream or upstream resources
        """
        updated_resources = list()
        for resource in resource_list:
            if resource == old:
                updated_resources.append(new)
            else:
                updated_resources.append(resource)
        resource_list.clear()
        resource_list += updated_resources
        self._file_model.update(self._resources_from_upstream + self._resources_from_downstream)
        self._check_notifications()
        cmd_line_args = list()
        for arg in self.cmd_line_args:
            if arg.arg == old.label:
                cmd_line_args.append(LabelArg(new.label))
            else:
                cmd_line_args.append(arg)
        self.update_cmd_line_args(cmd_line_args)

    def _update_files_and_cmd_line_args(self):
        """Updates the file model and command line arguments with regards to available resources."""
        all_resources = self._resources_from_upstream + self._resources_from_downstream
        self._file_model.update(all_resources)
        self._check_notifications()
        update_args = list()
        resource_labels = {resource.label for resource in all_resources}
        for arg in self.cmd_line_args:
            if isinstance(arg, LabelArg):
                if arg.arg in resource_labels:
                    update_args.append(arg)
                else:
                    # The corresponding resource does not exist anymore so we drop the argument.
                    continue
            else:
                update_args.append(arg)
        self.update_cmd_line_args(update_args)

    def item_dict(self):
        """Returns a dictionary corresponding to this item."""
        d = super().item_dict()
        d["use_shell"] = self.use_shell
        d["shell_index"] = self.shell_index
        d["cmd"] = self.cmd
        selections = list()
        for row in range(self._file_model.rowCount()):
            label, selected = self._file_model.checked_data(self._file_model.index(row, 0))
            selections.append([label, selected])
        d["file_selection"] = selections
        d["work_dir_mode"] = self._work_dir_mode
        d["cmd_line_args"] = [arg.to_dict() for arg in self.cmd_line_args]
        return d

    @staticmethod
    def from_dict(name, item_dict, toolbox, project):
        """See base class."""
        description, x, y = ProjectItem.parse_item_dict(item_dict)
        use_shell = item_dict.get("use_shell", True)
        shel_index = item_dict.get("shell_index", 0)
        cmd = item_dict.get("cmd", "")
        selections = {label: selected for label, selected in item_dict.get("file_selection", list())}
        work_dir_mode = item_dict.get("work_dir_mode", True)
        cmd_line_args = item_dict.get("cmd_line_args", [])
        cmd_line_args = [cmd_line_arg_from_dict(arg) for arg in cmd_line_args]
        return Gimlet(
            name,
            description,
            x,
            y,
            toolbox,
            project,
            use_shell,
            shel_index,
            cmd,
            cmd_line_args,
            selections,
            work_dir_mode,
        )

    def notify_destination(self, source_item):
        """See base class."""
        if source_item.item_type() == "Data Connection":
            self._logger.msg.emit(
                f"Link established. Files from <b>{source_item.name}</b> are now available in <b>{self.name}</b>."
            )
            return
        if source_item.item_type() in ["Data Store", "Data Transformer", "Data Connection", "Tool", "Gimlet"]:
            self._logger.msg.emit("Link established")
            return
        if source_item.item_type() in ("GdxExporter", "Exporter"):
            self._logger.msg.emit(
                f"Link established. Files exported by <b>{source_item.name}</b> are "
                f"now available in <b>{self.name}</b>."
            )
            return
        super().notify_destination(source_item)

    def _check_notifications(self):
        """See base class."""
        self.clear_notifications()
        duplicates = self._file_model.duplicate_paths()
        if duplicates:
            self.add_notification("Duplicate input files from predecessor items:<br>{}".format("<br>".join(duplicates)))

    def update_name_label(self):
        """Updates the name label in Gimlet properties tab.
        Used only when a project item is renamed."""
        self._properties_ui.label_gimlet_name.setText(self.name)

    def resources_for_direct_successors(self):
        """Returns resources for direct successors.

        This enables communication of resources between
        project items in the app.

        Returns:
            list: List of ProjectItemResources
        """
        return self._resources_from_upstream + self._resources_from_downstream
