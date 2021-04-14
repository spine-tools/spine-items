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
QWidget that is used to create or edit Tool specifications.
In the former case it is presented empty, but in the latter it
is filled with all the information from the specification being edited.

:author: M. Marin (KTH), P. Savolainen (VTT)
:date:   12.4.2018
"""

import os
from copy import deepcopy
from PySide2.QtGui import QStandardItemModel, QStandardItem, QKeySequence, QTextDocument
from PySide2.QtWidgets import QMainWindow, QInputDialog, QFileDialog, QFileIconProvider, QMessageBox, QUndoStack
from PySide2.QtCore import Slot, Qt, QFileInfo, QTimer
from spinetoolbox.config import STATUSBAR_SS
from spinetoolbox.helpers import busy_effect, open_url
from spinetoolbox.widgets.notification import ChangeNotifier
from spinetoolbox.widgets.custom_qwidgets import ToolBarWidget
from spine_engine.utils.command_line_arguments import split_cmdline_args
from ...widgets import SpecNameDescriptionToolbar, prompt_to_save_changes, save_ui, restore_ui
from ...commands import ChangeSpecPropertyCommand
from ..item_info import ItemInfo
from ..tool_specifications import TOOL_TYPES, REQUIRED_KEYS


class ToolSpecificationEditorWindow(QMainWindow):
    def __init__(self, toolbox, specification=None, item=None):
        """A widget to query user's preferences for a new tool specification.

        Args:
            toolbox (ToolboxUI): QMainWindow instance
            specification (ToolSpecification, optional): If given, the form is pre-filled with this specification
            item (ProjectItem, optional): Sets the spec for this item if accepted
        """
        from ..ui.tool_specification_form import Ui_MainWindow  # pylint: disable=import-outside-toplevel

        super().__init__(parent=toolbox)  # Inherit stylesheet from ToolboxUI
        self._item = item
        self._new_spec = None
        self._app_settings = toolbox.qsettings()
        self.settings_group = "toolSpecificationEditorWindow"
        # Setup UI from Qt Designer file
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Tool Specification Editor[*]")
        self._restore_dock_widgets()
        restore_ui(self, self._app_settings, self.settings_group)
        self._undo_stack = QUndoStack(self)
        self._change_notifier = ChangeNotifier(self._undo_stack, self)
        self._spec_toolbar = SpecNameDescriptionToolbar(self, specification, self._undo_stack)
        self.addToolBar(Qt.TopToolBarArea, self._spec_toolbar)
        self._populate_main_menu()
        # Customize text edit main program
        self.ui.textEdit_program.setEnabled(False)
        self._curren_programfile_path = None
        self._programfile_documents = {}
        # Class attributes
        self._toolbox = toolbox
        self._project = self._toolbox.project()
        self._original_spec_name = None if specification is None else specification.name
        # init models
        self.programfiles_model = QStandardItemModel()
        self.io_files_model = QStandardItemModel()
        # init ui
        self.ui.treeView_programfiles.setModel(self.programfiles_model)
        self.ui.treeView_io_files.setModel(self.io_files_model)
        self.ui.comboBox_tooltype.addItems(TOOL_TYPES)
        self.ui.comboBox_tooltype.setCurrentIndex(-1)
        # if a specification is given, fill the form with data from it
        if specification is not None:
            self.ui.checkBox_execute_in_work.setChecked(specification.execute_in_work)
            self.ui.lineEdit_args.setText(" ".join(specification.cmdline_args))
            tooltype = specification.tooltype.lower()
            index = next(iter(k for k, t in enumerate(TOOL_TYPES) if t.lower() == tooltype), -1)
            self.ui.comboBox_tooltype.setCurrentIndex(index)
            self.ui.textEdit_program.set_lexer_name(tooltype.lower())
        # Init lists
        programfiles = list(specification.includes) if specification else list()
        # Get first item from programfiles list as the main program file
        try:
            main_program_file = programfiles.pop(0)
        except IndexError:
            main_program_file = ""
        inputfiles = list(specification.inputfiles) if specification else list()
        inputfiles_opt = list(specification.inputfiles_opt) if specification else list()
        outputfiles = list(specification.outputfiles) if specification else list()
        self.includes_main_path = specification.path if specification else None
        self.spec_dict = deepcopy(specification.to_dict()) if specification else dict(item_type=ItemInfo.item_type())
        # Populate lists (this will also create headers)
        self.init_programfile_list()
        self.init_io_file_list()
        self.populate_programfile_list(programfiles)
        self.populate_inputfiles_list(inputfiles)
        self.populate_inputfiles_opt_list(inputfiles_opt)
        self.populate_outputfiles_list(outputfiles)
        if self.includes_main_path is not None:
            self._set_main_program_file(os.path.join(self.includes_main_path, main_program_file))
        self.ui.statusbar.setStyleSheet(STATUSBAR_SS)
        self.connect_signals()

    def _restore_dock_widgets(self):
        docks = (self.ui.dockWidget_program_files, self.ui.dockWidget_program)
        self.splitDockWidget(*docks, Qt.Horizontal)
        width = sum(d.width() for d in docks)
        self.resizeDocks(docks, [width * x for x in (0.3, 0.7)], Qt.Horizontal)
        docks = (self.ui.dockWidget_program_files, self.ui.dockWidget_io_files)
        self.splitDockWidget(*docks, Qt.Vertical)
        height = sum(d.height() for d in docks)
        self.resizeDocks(docks, [height * x for x in (0.6, 0.4)], Qt.Vertical)

    def _populate_main_menu(self):
        undo_action = self._undo_stack.createUndoAction(self)
        redo_action = self._undo_stack.createRedoAction(self)
        undo_action.setShortcuts(QKeySequence.Undo)
        redo_action.setShortcuts(QKeySequence.Redo)
        self._spec_toolbar.menu.insertActions(self._spec_toolbar.save_action, [redo_action, undo_action])
        self._spec_toolbar.menu.insertSeparator(self._spec_toolbar.save_action)
        self.ui.menubar.hide()

    def init_programfile_list(self):
        """List program files in QTreeView."""
        for name in ("Main program file", "Additional program files"):
            item = QStandardItem(name)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable)
            self.programfiles_model.appendRow(item)
        # Setup 'Main' item
        index = self.programfiles_model.index(0, 0)
        widget = ToolBarWidget("Main program file", self)
        widget.tool_bar.addActions([self.ui.actionNew_main_program_file, self.ui.actionSelect_main_program_file])
        widget.tool_bar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.ui.treeView_programfiles.setIndexWidget(index, widget)
        # Setup 'Additional...' item
        index = self.programfiles_model.index(1, 0)
        widget = ToolBarWidget("Additional program files", self)
        widget.tool_bar.addActions(
            [
                self.ui.actionNew_program_file,
                self.ui.actionAdd_program_file,
                self.ui.actionAdd_program_directory,
                self.ui.actionRemove_selected_program_files,
            ]
        )
        widget.tool_bar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.ui.treeView_programfiles.setIndexWidget(index, widget)
        self.ui.treeView_programfiles.expandAll()
        tool_tip = (
            '<p>Other program files and/or directories (in addition to the main program file) required by the tool.</p>'
            '<p><span style=" font-weight:600;">Tip</span>: '
            'You can Drag &amp; Drop files and/or directories here from your computer.</p>'
        )
        self.programfiles_model.setData(index, tool_tip, role=Qt.ToolTipRole)

    def _current_main_program_file(self):
        index = self.programfiles_model.index(0, 0)
        root_item = self.programfiles_model.itemFromIndex(index)
        if not root_item.hasChildren():
            return None
        return root_item.child(0).data(Qt.UserRole)

    def _additional_program_file_list(self):
        return self.spec_dict.get("includes", [])[1:]

    def populate_main_programfile(self, name):
        """List program files in QTreeView.
        Args:
            name (str): *absolute* path
        """
        index = self.programfiles_model.index(0, 0)
        root_item = self.programfiles_model.itemFromIndex(index)
        root_item.removeRows(0, root_item.rowCount())
        if not name:
            return
        item = QStandardItem(os.path.basename(name))
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        item.setData(QFileIconProvider().icon(QFileInfo(name)), Qt.DecorationRole)
        item.setData(name, Qt.UserRole)
        root_item.appendRow(item)
        QTimer.singleShot(0, self._push_change_main_program_file_command)

    def populate_programfile_list(self, names):
        """List program files in QTreeView.
        """
        # Find visible indexes
        visible = set()
        for item in self.programfiles_model.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            if not item.rowCount():
                index = self.programfiles_model.indexFromItem(item)
                if self.ui.treeView_programfiles.isExpanded(index.parent()):
                    visible.add(self._programfile_path_from_index(index))
        # Repopulate
        index = self.programfiles_model.index(1, 0)
        root_item = self.programfiles_model.itemFromIndex(index)
        root_item.removeRows(0, root_item.rowCount())
        components = _collect_components(names)
        _build_tree(root_item, components)
        # Reexpand visible
        for item in self.programfiles_model.findItems("", Qt.MatchContains | Qt.MatchRecursive):
            if not item.rowCount():
                index = self.programfiles_model.indexFromItem(item)
                if self._programfile_path_from_index(index) in visible:
                    self.ui.treeView_programfiles.expand(index.parent())

    def init_io_file_list(self):
        for name in ("Input files", "Optional input files", "Output files"):
            item = QStandardItem(name)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable)
            self.io_files_model.appendRow(item)
        # Setup 'Input' item
        index = self.io_files_model.index(0, 0)
        widget = ToolBarWidget("Input files", self)
        widget.tool_bar.addActions([self.ui.actionAdd_input_files, self.ui.actionRemove_selected_input_files])
        widget.tool_bar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.ui.treeView_io_files.setIndexWidget(index, widget)
        # Setup 'Optional' item
        index = self.io_files_model.index(1, 0)
        widget = ToolBarWidget("Optional input files", self)
        widget.tool_bar.addActions([self.ui.actionAdd_opt_input_files, self.ui.actionRemove_selected_opt_input_files])
        widget.tool_bar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.ui.treeView_io_files.setIndexWidget(index, widget)
        # Setup 'Output' item
        index = self.io_files_model.index(2, 0)
        widget = ToolBarWidget("Output files", self)
        widget.tool_bar.addActions([self.ui.actionAdd_output_files, self.ui.actionRemove_selected_output_files])
        widget.tool_bar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.ui.treeView_io_files.setIndexWidget(index, widget)

    def _input_file_list(self):
        return self.spec_dict.get("inputfiles", [])

    def _opt_input_file_list(self):
        return self.spec_dict.get("inputfiles_opt", [])

    def _output_file_list(self):
        return self.spec_dict.get("outputfiles", [])

    def _populate_io_files_list(self, index, names):
        root_item = self.io_files_model.itemFromIndex(index)
        root_item.removeRows(0, root_item.rowCount())
        for name in names:
            item = QStandardItem(name)
            item.setData(QFileIconProvider().icon(QFileInfo(name)), Qt.DecorationRole)
            root_item.appendRow(item)
        self.ui.treeView_io_files.expand(index)

    def populate_inputfiles_list(self, names):
        """List input files in QTreeView.
        """
        self.spec_dict["inputfiles"] = names
        index = self.io_files_model.index(0, 0)
        self._populate_io_files_list(index, names)

    def populate_inputfiles_opt_list(self, names):
        """List optional input files in QTreeView.
        """
        self.spec_dict["inputfiles_opt"] = names
        index = self.io_files_model.index(1, 0)
        self._populate_io_files_list(index, names)

    def populate_outputfiles_list(self, names):
        """List output files in QTreeView.
        """
        self.spec_dict["outputfiles"] = names
        index = self.io_files_model.index(2, 0)
        self._populate_io_files_list(index, names)

    def connect_signals(self):
        """Connect signals to slots."""
        self.ui.actionNew_main_program_file.triggered.connect(self.new_main_program_file)
        self.ui.actionSelect_main_program_file.triggered.connect(self.browse_main_program_file)
        self.ui.actionNew_program_file.triggered.connect(self.new_program_file)
        self.ui.actionAdd_program_file.triggered.connect(self.show_add_program_files_dialog)
        self.ui.actionAdd_program_directory.triggered.connect(self.show_add_program_dirs_dialog)
        self.ui.actionRemove_selected_program_files.triggered.connect(self.remove_program_files)
        self.ui.treeView_programfiles.files_dropped.connect(self.add_dropped_program_files)
        self.ui.treeView_programfiles.doubleClicked.connect(self.open_program_file)
        self.ui.toolButton_save_program.clicked.connect(self.save_program_file)
        self.ui.textEdit_program.save_action.triggered.connect(self.save_program_file)
        self.ui.actionAdd_input_files.triggered.connect(self.add_inputfiles)
        self.ui.actionRemove_selected_input_files.triggered.connect(self.remove_inputfiles)
        self.ui.actionAdd_opt_input_files.triggered.connect(self.add_inputfiles_opt)
        self.ui.actionRemove_selected_opt_input_files.triggered.connect(self.remove_inputfiles_opt)
        self.ui.actionAdd_output_files.triggered.connect(self.add_outputfiles)
        self.ui.actionRemove_selected_output_files.triggered.connect(self.remove_outputfiles)
        # Enable removing items from QTreeViews by pressing the Delete key
        self.ui.treeView_programfiles.del_key_pressed.connect(self.remove_program_files_with_del)
        self.ui.treeView_io_files.del_key_pressed.connect(self.remove_io_files_with_del)
        # Push undo commands
        self.ui.comboBox_tooltype.activated.connect(self._push_change_tooltype_command)
        self.ui.checkBox_execute_in_work.toggled.connect(self._push_change_execute_in_work_command)
        self.ui.lineEdit_args.editingFinished.connect(self._push_change_args_command)
        self._undo_stack.cleanChanged.connect(self._update_window_modified)
        # Selection changed
        self.ui.treeView_programfiles.selectionModel().selectionChanged.connect(
            self._handle_programfile_selection_changed
        )
        self.ui.treeView_io_files.selectionModel().selectionChanged.connect(self._handle_io_file_selection_changed)
        self._spec_toolbar.save_action.triggered.connect(self._save)
        self._spec_toolbar.close_action.triggered.connect(self.close)

    @Slot(bool)
    def _update_window_modified(self, clean):
        self.setWindowModified(not clean)
        self._spec_toolbar.save_action.setEnabled(not clean)

    @Slot(int)
    def _push_change_tooltype_command(self, index):
        new_type = TOOL_TYPES[index]
        old_type = self.spec_dict.get("tooltype", "")
        if new_type == old_type:
            return
        self._undo_stack.push(ChangeSpecPropertyCommand(self._set_tooltype, new_type, old_type, "change tooltype"))

    def _set_tooltype(self, value):
        value = value.lower()
        self.spec_dict["tooltype"] = value
        self.ui.textEdit_program.set_lexer_name(value)
        index = next(iter(k for k, t in enumerate(TOOL_TYPES) if t.lower() == value), -1)
        self.ui.comboBox_tooltype.setCurrentIndex(index)

    @Slot(bool)
    def _push_change_execute_in_work_command(self, new_value):
        old_value = self.spec_dict.get("execute_in_work", True)
        if new_value == old_value:
            return
        self._undo_stack.push(
            ChangeSpecPropertyCommand(self._set_execute_in_work, new_value, old_value, "change execute in work")
        )

    def _set_execute_in_work(self, value):
        self.spec_dict["execute_in_work"] = value
        self.ui.checkBox_execute_in_work.setChecked(value)

    @Slot()
    def _push_change_args_command(self):
        old_value = self.spec_dict.get("cmdline_args", [])
        new_value = split_cmdline_args(self.ui.lineEdit_args.text())
        if new_value == old_value:
            return
        self._undo_stack.push(
            ChangeSpecPropertyCommand(self._set_cmdline_args, new_value, old_value, "change command line args")
        )

    def _set_cmdline_args(self, value):
        self.spec_dict["cmdline_args"] = value
        self.ui.lineEdit_args.setText(" ".join(value))

    @Slot()
    def _push_change_main_program_file_command(self):
        new_value = self._current_main_program_file()
        old_program_files = self.spec_dict.get("includes", [])
        if self.includes_main_path is not None:
            old_program_files = [os.path.join(self.includes_main_path, f) for f in old_program_files]
        old_value = old_program_files[0] if old_program_files else ""
        if os.path.normcase(old_value) == os.path.normcase(new_value):
            return
        new_program_files = old_program_files.copy()
        if new_program_files:
            new_program_files[0] = new_value
        elif new_value:
            new_program_files.append(new_value)
        self._undo_stack.push(
            ChangeSpecPropertyCommand(
                self._set_program_files, new_program_files, old_program_files, "change main program file"
            )
        )

    def _set_program_files(self, program_files):
        """Sets program files.

        Args:
            program_files (list(str)): List of *absolute* paths
        """
        main_program_file = program_files[0] if program_files else ""
        self.includes_main_path = os.path.dirname(next(iter(f for f in program_files if f), ""))
        additional_program_files = [os.path.relpath(file, self.includes_main_path) for file in program_files[1:]]
        self._set_main_program_file(main_program_file)
        self.populate_programfile_list(additional_program_files)
        self.spec_dict["includes"] = [os.path.basename(main_program_file), *additional_program_files]

    def _set_main_program_file(self, file_path):
        """Sets main program file and dumps its contents into the text edit.

        Args:
            file_path (str): absolute path
        """
        self.populate_main_programfile(file_path)
        self.ui.label_mainpath.setText(self.includes_main_path)

    @Slot("QItemSelection", "QItemSelection")
    def _handle_programfile_selection_changed(self, _selected, _deselected):
        # Set remove action enabled
        indexes = self._selected_program_file_indexes()
        self.ui.actionRemove_selected_program_files.setEnabled(bool(indexes))
        # Load selected file code on text edit
        current = self.ui.treeView_programfiles.selectionModel().currentIndex()
        if self.programfiles_model.rowCount(current):
            # Not a leaf
            self._clear_program_text_edit()
            return
        file_path = self._programfile_path_from_index(current)
        self._load_programfile_in_editor(file_path)

    def _programfile_path_from_index(self, index):
        """Return absolute path to a file pointed by index.

        Args:
            index (QModelIndex): index

        Returns:
            str: file path
        """
        components = _path_components_from_index(index)
        if not components:
            return ""
        return os.path.join(self.includes_main_path, *components)

    def _clear_program_text_edit(self):
        self.ui.textEdit_program.setDocument(QTextDocument())
        self.ui.textEdit_program.setEnabled(False)
        self.ui.toolButton_save_program.setEnabled(False)
        self.ui.dockWidget_program.setWindowTitle("")

    def _load_programfile_in_editor(self, file_path):
        self._curren_programfile_path = file_path
        if not os.path.isfile(file_path):
            self.show_status_bar_msg(f"Program file {file_path} is not valid")
            self._clear_program_text_edit()
            return
        if file_path not in self._programfile_documents:
            try:
                with open(file_path, 'r') as file:
                    text = file.read()
            except (IOError, UnicodeDecodeError) as e:
                self.show_status_bar_msg(str(e))
                return
            document = self._programfile_documents[file_path] = QTextDocument(self.ui.textEdit_program)
            document.setPlainText(text)
            document.setModified(False)
            document.modificationChanged.connect(self.ui.toolButton_save_program.setEnabled)
            document.modificationChanged.connect(self.ui.dockWidget_program.setWindowModified)
        else:
            document = self._programfile_documents[file_path]
        self.ui.toolButton_save_program.setEnabled(document.isModified())
        self.ui.dockWidget_program.setWindowModified(document.isModified())
        self.ui.textEdit_program.setDocument(document)
        self.ui.textEdit_program.setEnabled(True)
        self.ui.dockWidget_program.setWindowTitle(os.path.basename(file_path) + "[*]")

    @Slot(bool)
    def browse_main_program_file(self, checked=False):
        """Open file browser where user can select the path of the main program file."""
        # noinspection PyCallByClass, PyTypeChecker, PyArgumentList
        answer = QFileDialog.getOpenFileName(
            self, "Select existing main program file", self._project.project_dir, "*.*"
        )
        file_path = answer[0]
        if not file_path:  # Cancel button clicked
            return
        self.populate_main_programfile(file_path)

    @Slot(bool)
    def save_program_file(self, _=False):
        """Saves program file."""
        try:
            with open(self._curren_programfile_path, "w") as file:
                file.write(self.ui.textEdit_program.toPlainText())
            self.ui.textEdit_program.document().setModified(False)
            basename = os.path.basename(self._curren_programfile_path)
            self.show_status_bar_msg(f"Program file '{basename}' saved successfully")
        except IOError as e:
            self.show_status_bar_msg(e)

    @Slot(bool)
    def new_main_program_file(self, _=False):
        """Creates a new blank main program file."""
        # noinspection PyCallByClass
        answer = QFileDialog.getSaveFileName(self, "Create new main program file", self._project.project_dir)
        file_path = answer[0]
        if not file_path:  # Cancel button clicked
            return
        # Remove file if it exists. getSaveFileName has asked confirmation for us.
        try:
            os.remove(file_path)
        except OSError:
            pass
        try:
            with open(file_path, "w"):
                pass
        except OSError:
            msg = "Please check directory permissions."
            # noinspection PyTypeChecker, PyArgumentList, PyCallByClass
            QMessageBox.information(self, "Creating file failed", msg)
            return
        self.populate_main_programfile(file_path)

    @Slot()
    def new_program_file(self):
        """Let user create a new program file for this tool specification."""
        path = self.includes_main_path if self.includes_main_path else self._project.project_dir
        # noinspection PyCallByClass, PyTypeChecker, PyArgumentList
        dir_path = QFileDialog.getSaveFileName(self, "Create program file", path, "*.*")
        file_path = dir_path[0]
        if file_path == "":  # Cancel button clicked
            return
        # create file. NOTE: getSaveFileName does the 'check for existence' for us
        open(file_path, "w").close()
        self.add_program_files(file_path)

    @Slot(bool)
    def show_add_program_files_dialog(self, checked=False):
        """Let user select program files for this tool specification."""
        path = self.includes_main_path if self.includes_main_path else self._project.project_dir
        # noinspection PyCallByClass, PyTypeChecker, PyArgumentList
        answer = QFileDialog.getOpenFileNames(self, "Add program file", path, "*.*")
        file_paths = answer[0]
        if not file_paths:  # Cancel button clicked
            return
        self.add_program_files(*file_paths)

    @Slot(bool)
    def show_add_program_dirs_dialog(self, checked=False):
        """Let user select a program directory for this tool specification.
        All files and sub-directories will be added to the program files.
        """
        path = self.includes_main_path if self.includes_main_path else self._project.project_dir
        # noinspection PyCallByClass, PyTypeChecker, PyArgumentList
        answer = QFileDialog.getExistingDirectory(self, "Select a directory to add to program files", path)
        file_paths = list()
        for root, _, files in os.walk(answer):
            for file in files:
                file_paths.append(os.path.abspath(os.path.join(root, file)))
        self.add_program_files(*file_paths)

    @Slot("QVariant")
    def add_dropped_program_files(self, file_paths):
        """Adds dropped file paths to Source files list."""
        self.add_program_files(*file_paths)

    def _validate_additional_program_files(self, new_files, old_program_files):
        valid_files = []
        dupes = []
        invalid = []
        for file in new_files:
            if file in old_program_files:
                dupes.append(os.path.basename(file))
                continue
            if self.includes_main_path is not None:
                common_prefix = os.path.commonprefix([os.path.abspath(self.includes_main_path), os.path.abspath(file)])
                if os.path.normcase(common_prefix) != os.path.normcase(self.includes_main_path):
                    invalid.append(os.path.basename(file))
                    continue
            valid_files.append(file)
        if dupes:
            dupes = ", ".join(dupes)
            self.show_status_bar_msg(f"Program file(s) '{dupes}' already added")
        if invalid:
            invalid = ", ".join(invalid)
            self.show_status_bar_msg(f"Program file(s) '{invalid}' not in main directory")
        return valid_files

    def add_program_files(self, *new_files):
        """Appends program files.

        Args:
            *new_files (str): Absolute paths to append.
        """
        old_program_files = self.spec_dict.get("includes", [""])
        if self.includes_main_path is not None:
            old_program_files = [os.path.join(self.includes_main_path, f) for f in old_program_files]
        new_files = self._validate_additional_program_files(list(new_files), old_program_files)
        if not new_files:
            return
        new_program_files = old_program_files.copy() + new_files
        self._undo_stack.push(
            ChangeSpecPropertyCommand(
                self._set_program_files, new_program_files, old_program_files, "add program files"
            )
        )

    @Slot()
    def remove_program_files_with_del(self):
        """Support for deleting items with the Delete key."""
        self.remove_program_files()

    def _selected_program_file_indexes(self):
        indexes = set(self.ui.treeView_programfiles.selectedIndexes())
        # discard main program file
        parent = self.programfiles_model.index(0, 0)
        indexes.discard(self.programfiles_model.index(0, 0, parent))
        # keep only leaves
        return {ind for ind in indexes if not self.programfiles_model.rowCount(ind)}

    @Slot(bool)
    def remove_program_files(self, checked=False):
        """Removes selected program files from program_file list."""
        indexes = self._selected_program_file_indexes()
        if not indexes:  # Nothing removable selected
            self.show_status_bar_msg("Please select program files to remove")
            return
        removed_files = {os.path.join(*_path_components_from_index(ind)) for ind in indexes}
        old_program_files = self.spec_dict.get("includes", [""])
        new_program_files = [f for f in old_program_files if f not in removed_files]
        if self.includes_main_path is not None:
            old_program_files = [os.path.join(self.includes_main_path, f) for f in old_program_files]
            new_program_files = [os.path.join(self.includes_main_path, f) for f in new_program_files]
        self._undo_stack.push(
            ChangeSpecPropertyCommand(
                self._set_program_files, new_program_files, old_program_files, "remove program files"
            )
        )

    @busy_effect
    @Slot("QModelIndex")
    def open_program_file(self, index):
        """Open program file in default program."""
        if not index.isValid() or self.programfiles_model.rowCount(index):
            return
        program_file = self._programfile_path_from_index(index)
        _, ext = os.path.splitext(program_file)
        if ext in [".bat", ".exe"]:
            self._toolbox.msg_warning.emit(
                "Sorry, opening files with extension <b>{0}</b> not implemented. "
                "Please open the file manually.".format(ext)
            )
            return
        url = "file:///" + os.path.join(self.includes_main_path, program_file)
        # noinspection PyCallByClass, PyTypeChecker, PyArgumentList
        res = open_url(url)
        if not res:
            self._toolbox.msg_error.emit("Failed to open file: <b>{0}</b>".format(program_file))

    @Slot(bool)
    def add_inputfiles(self, checked=False):
        """Let user select input files for this tool specification."""
        msg = (
            "Add an input file or a directory required by your program. Wildcards "
            "<b>are not</b> supported.<br/><br/>"
            "Examples:<br/>"
            "<b>data.csv</b> -> File is copied to the same work directory as the main program.<br/>"
            "<b>input/data.csv</b> -> Creates subdirectory /input to work directory and "
            "copies file data.csv there.<br/>"
            "<b>output/</b> -> Creates an empty directory into the work directory.<br/><br/>"
        )
        # noinspection PyCallByClass, PyTypeChecker, PyArgumentList
        answer = QInputDialog.getText(self, "Add input item", msg, flags=Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        file_name = answer[0]
        if not file_name:  # Cancel button clicked
            return
        old_files = self.spec_dict.get("inputfiles", [])
        new_files = old_files + [file_name]
        self._undo_stack.push(
            ChangeSpecPropertyCommand(self.populate_inputfiles_list, new_files, old_files, "add input file")
        )

    @Slot(bool)
    def add_inputfiles_opt(self, checked=False):
        """Let user select optional input files for this tool specification."""
        msg = (
            "Add optional input files that may be utilized by your program. <br/>"
            "Wildcards are supported.<br/><br/>"
            "Examples:<br/>"
            "<b>data.csv</b> -> If found, file is copied to the same work directory as the main program.<br/>"
            "<b>*.csv</b> -> All found CSV files are copied to the same work directory as the main program.<br/>"
            "<b>input/data_?.dat</b> -> All found files matching the pattern 'data_?.dat' will be copied to <br/>"
            "input/ subdirectory under the same work directory as the main program.<br/><br/>"
        )
        # noinspection PyCallByClass, PyTypeChecker, PyArgumentList
        answer = QInputDialog.getText(
            self, "Add optional input item", msg, flags=Qt.WindowTitleHint | Qt.WindowCloseButtonHint
        )
        file_name = answer[0]
        if not file_name:  # Cancel button clicked
            return
        old_files = self.spec_dict.get("inputfiles_opt", [])
        new_files = old_files + [file_name]
        self._undo_stack.push(
            ChangeSpecPropertyCommand(
                self.populate_inputfiles_opt_list, new_files, old_files, "add optional input file"
            )
        )

    @Slot(bool)
    def add_outputfiles(self, checked=False):
        """Let user select output files for this tool specification."""
        msg = (
            "Add output files that will be archived into the Tool results directory after the <br/>"
            "Tool specification has finished execution. Wildcards are supported.<br/><br/>"
            "Examples:<br/>"
            "<b>results.csv</b> -> File is copied from work directory into results.<br/> "
            "<b>*.csv</b> -> All CSV files will copied into results.<br/> "
            "<b>output/*.gdx</b> -> All GDX files from the work subdirectory /output will be copied into <br/>"
            "results /output subdirectory.<br/><br/>"
        )
        # noinspection PyCallByClass, PyTypeChecker, PyArgumentList
        answer = QInputDialog.getText(self, "Add output item", msg, flags=Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        file_name = answer[0]
        if not file_name:  # Cancel button clicked
            return
        old_files = self.spec_dict.get("outputfiles", [])
        new_files = old_files + [file_name]
        self._undo_stack.push(
            ChangeSpecPropertyCommand(self.populate_outputfiles_list, new_files, old_files, "add output file")
        )

    def _selected_io_file_indexes(self, parent):
        indexes = self.ui.treeView_io_files.selectedIndexes()
        return [ind for ind in indexes if ind.parent() == parent]

    @Slot("QItemSelection", "QItemSelection")
    def _handle_io_file_selection_changed(self, _deselected, _selected):
        parent = self.io_files_model.index(0, 0)
        indexes = self._selected_io_file_indexes(parent)
        self.ui.actionRemove_selected_input_files.setEnabled(bool(indexes))
        parent = self.io_files_model.index(1, 0)
        indexes = self._selected_io_file_indexes(parent)
        self.ui.actionRemove_selected_opt_input_files.setEnabled(bool(indexes))
        parent = self.io_files_model.index(2, 0)
        indexes = self._selected_io_file_indexes(parent)
        self.ui.actionRemove_selected_output_files.setEnabled(bool(indexes))

    @Slot(bool)
    def remove_inputfiles(self, checked=False):
        """Remove selected input files from list.
        Do not remove anything if there are no items selected.
        """
        parent = self.io_files_model.index(0, 0)
        indexes = self._selected_io_file_indexes(parent)
        if not indexes:  # Nothing selected
            self.show_status_bar_msg("Please select the input files to remove")
            return
        removed_files = {ind.data(Qt.DisplayRole) for ind in indexes}
        old_files = self.spec_dict.get("inputfiles", [])
        new_files = [f for f in old_files if f not in removed_files]
        self._undo_stack.push(
            ChangeSpecPropertyCommand(self.populate_inputfiles_list, new_files, old_files, "remove input files")
        )

    @Slot(bool)
    def remove_inputfiles_opt(self, checked=False):
        """Remove selected optional input files from list.
        Do not remove anything if there are no items selected.
        """
        parent = self.io_files_model.index(1, 0)
        indexes = self._selected_io_file_indexes(parent)
        if not indexes:  # Nothing selected
            self.show_status_bar_msg("Please select the optional input files to remove")
            return
        removed_files = {ind.data(Qt.DisplayRole) for ind in indexes}
        old_files = self.spec_dict.get("inputfiles_opt", [])
        new_files = [f for f in old_files if f not in removed_files]
        self._undo_stack.push(
            ChangeSpecPropertyCommand(
                self.populate_inputfiles_opt_list, new_files, old_files, "remove optional input files"
            )
        )

    @Slot(bool)
    def remove_outputfiles(self, checked=False):
        """Remove selected output files from list.
        Do not remove anything if there are no items selected.
        """
        parent = self.io_files_model.index(2, 0)
        indexes = self._selected_io_file_indexes(parent)
        if not indexes:  # Nothing selected
            self.show_status_bar_msg("Please select the output files to remove")
            return
        removed_files = {ind.data(Qt.DisplayRole) for ind in indexes}
        old_files = self.spec_dict.get("outputfiles", [])
        new_files = [f for f in old_files if f not in removed_files]
        self._undo_stack.push(
            ChangeSpecPropertyCommand(self.populate_outputfiles_list, new_files, old_files, "remove output files")
        )

    @Slot()
    def remove_io_files_with_del(self):
        """Support for deleting items with the Delete key."""
        self.remove_inputfiles()
        self.remove_inputfiles_opt()
        self.remove_outputfiles()

    def _save(self):
        """Checks that everything is valid, creates Tool spec dictionary and adds Tool spec to project."""
        # Check that tool type is selected
        if self.ui.comboBox_tooltype.currentIndex() == -1:
            self.show_status_bar_msg("Tool type not selected")
            return False
        # Check that path of main program file is valid before saving it
        main_program = self._current_main_program_file().strip()
        if not os.path.isfile(main_program):
            self.show_status_bar_msg("Main program file is not valid")
            return False
        new_spec_dict = {}
        new_spec_dict["name"] = self._spec_toolbar.name()
        new_spec_dict["description"] = self._spec_toolbar.description()
        new_spec_dict["tooltype"] = self.ui.comboBox_tooltype.currentText().lower()
        # Fix for issue #241
        folder_path, file_path = os.path.split(main_program)
        self.includes_main_path = os.path.abspath(folder_path)
        self.ui.label_mainpath.setText(self.includes_main_path)
        new_spec_dict["execute_in_work"] = self.ui.checkBox_execute_in_work.isChecked()
        new_spec_dict["includes"] = [file_path]
        new_spec_dict["includes"] += self._additional_program_file_list()
        new_spec_dict["inputfiles"] = self._input_file_list()
        new_spec_dict["inputfiles_opt"] = self._opt_input_file_list()
        new_spec_dict["outputfiles"] = self._output_file_list()
        # Strip whitespace from args before saving it to JSON
        new_spec_dict["cmdline_args"] = split_cmdline_args(self.ui.lineEdit_args.text())
        for k in REQUIRED_KEYS:
            if not new_spec_dict[k]:
                self.show_status_bar_msg(f"Missing mandatory field '{k}'")
                return False
        # Create new Tool specification
        new_spec_dict["includes_main_path"] = self.includes_main_path.replace(os.sep, "/")
        self._new_spec = self._make_tool_specification(new_spec_dict)
        if not self.call_add_tool_specification():
            return False
        self._undo_stack.setClean()
        if self._item:
            self._item.set_specification(self._new_spec)
        return True

    def _make_tool_specification(self, new_spec_dict):
        """Returns a ToolSpecification from current form settings.

        Args:
            new_spec_dict (dcit)

        Returns:
            ToolSpecification
        """
        tool_spec = self._toolbox.load_specification(new_spec_dict)
        if not tool_spec:
            self.show_status_bar_msg("Creating Tool specification failed")
        return tool_spec

    def call_add_tool_specification(self):
        """Adds new Tool specification to project.

        Returns:
            bool
        """
        if self._new_spec is None:
            return False
        update_existing = self._new_spec.name == self._original_spec_name
        return self._toolbox.add_specification(self._new_spec, update_existing, self)

    def showEvent(self, event):
        super().showEvent(event)
        self._undo_stack.cleanChanged.connect(self._update_window_modified)

    def closeEvent(self, event=None):
        """Handle close window.

        Args:
            event (QEvent): Closing event if 'X' is clicked.
        """
        self.focusWidget().clearFocus()
        if not self._undo_stack.isClean() and not prompt_to_save_changes(self, self._toolbox.qsettings(), self._save):
            event.ignore()
            return
        self._undo_stack.cleanChanged.disconnect(self._update_window_modified)
        save_ui(self, self._app_settings, self.settings_group)
        if event:
            event.accept()

    def show_status_bar_msg(self, msg):
        word_count = len(msg.split(" "))
        mspw = 60000 / 140  # Assume people can read ~140 words per minute
        duration = mspw * word_count
        self.ui.statusbar.showMessage(msg, duration)


def _path_components(path):
    """
    Args:
        path(str): a filesytem path, e.g. (/home/user/spine/toolbox/file.py)

    Yields:
        str: path components in 'reverse' order, e.g., file.py, toolbox, spine, user, home
    """
    while path:
        path, component = os.path.split(path)
        yield component


def _collect_components(names):
    """
    Args:
        names (list(str)): list of filepaths

    Returns:
        dict: mapping folders to contents recursively
    """
    components = {}
    for name in names:
        d = components
        for component in reversed(list(_path_components(name))):
            d = d.setdefault(component, {})
    return components


def _build_tree(root, components):
    """
    Appends rows from given components to given root item.

    Args:
        root (QStandardItem): root item
        components (dict): mapping folders to contents recursively
    """
    nodes = []
    leafs = []
    for parent, children in components.items():
        item = QStandardItem(parent)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        _build_tree(item, children)
        if item.hasChildren():
            nodes.append(item)
            item.setData(QFileIconProvider().icon(QFileIconProvider.Folder), Qt.DecorationRole)
        else:
            item.setData(QFileIconProvider().icon(QFileInfo(parent)), Qt.DecorationRole)
            leafs.append(item)
    for item in sorted(nodes, key=lambda x: x.text()):
        root.appendRow(item)
    for item in sorted(leafs, key=lambda x: x.text()):
        root.appendRow(item)


def _path_components_from_index(index):
    components = []
    while index.parent().isValid():
        components.insert(0, index.data())
        index = index.parent()
    return components
