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
from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtWidgets import QWidget, QStatusBar, QInputDialog, QFileDialog, QFileIconProvider, QMessageBox
from PySide2.QtCore import Slot, Qt, QFileInfo
from spinetoolbox.config import STATUSBAR_SS, TREEVIEW_HEADER_SS
from spinetoolbox.helpers import busy_effect, open_url
from spine_engine.utils.command_line_arguments import split_cmdline_args
from ..item_info import ItemInfo
from ..notebook_specifications import NOTEBOOK_TYPES, REQUIRED_KEYS
from .custom_menus import AddIncludesPopupMenu


class NotebookSpecificationWidget(QWidget):
    def __init__(self, toolbox, specification=None):
        """A widget to query user's preferences for a new tool specification.

        Args:
            toolbox (ToolboxUI): QMainWindow instance
            specification (ToolSpecification): If given, the form is pre-filled with this specification
        """
        from ..ui.notebook_specification_form import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(parent=toolbox, f=Qt.Window)  # Inherit stylesheet from ToolboxUI
        # Setup UI from Qt Designer file
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.widget_main_program.setVisible(False)
        self.ui.textEdit_jupyter_notebook.setStyleSheet(
            "QTextEdit {background-color: #19232D; border: 1px solid #32414B; color: #F0F0F0; border-radius: 2px;}"
        )
        # Class attributes
        self._toolbox = toolbox
        self._project = self._toolbox.project()
        self._original_specification = specification
        # init models
        self.input_vars_model = QStandardItemModel()
        self.input_files_model = QStandardItemModel()
        self.output_vars_model = QStandardItemModel()
        self.output_files_model = QStandardItemModel()
        # Add status bar to form
        self.statusbar = QStatusBar(self)
        self.statusbar.setFixedHeight(20)
        self.statusbar.setSizeGripEnabled(False)
        self.statusbar.setStyleSheet(STATUSBAR_SS)
        self.ui.horizontalLayout_statusbar_placeholder.addWidget(self.statusbar)
        # init ui
        self.ui.treeView_input_vars.setModel(self.input_vars_model)
        self.ui.treeView_input_files.setModel(self.input_files_model)
        self.ui.treeView_output_vars.setModel(self.output_vars_model)
        self.ui.treeView_output_files.setModel(self.output_files_model)
        self.ui.treeView_input_vars.setStyleSheet(TREEVIEW_HEADER_SS)
        self.ui.treeView_input_files.setStyleSheet(TREEVIEW_HEADER_SS)
        self.ui.treeView_output_vars.setStyleSheet(TREEVIEW_HEADER_SS)
        self.ui.treeView_output_files.setStyleSheet(TREEVIEW_HEADER_SS)
        self.ui.comboBox_notebook_type.addItem("Select type...")
        self.ui.comboBox_notebook_type.addItems(NOTEBOOK_TYPES)
        # if a specification is given, fill the form with data from it
        if specification is not None:
            self.ui.lineEdit_name.setText(specification.name)
            check_state = Qt.Checked if specification.execute_in_work else Qt.Unchecked
            self.ui.checkBox_execute_in_work.setCheckState(check_state)
            self.ui.textEdit_description.setPlainText(specification.description)
            self.ui.lineEdit_args.setText(" ".join(specification.cmdline_args))
            notebook_types = [x.lower() for x in NOTEBOOK_TYPES]
            index = notebook_types.index(specification.notebook_type) + 1
            self.ui.comboBox_notebook_type.setCurrentIndex(index)
        # Init lists
        self.source_files = list(specification.includes) if specification else list()
        # Get first item from source_files list as the main program file
        try:
            self.jupyter_notebook_file = self.source_files.pop(0)
        except IndexError:
            self.jupyter_notebook_file = ""
        self.input_vars = list(specification.input_vars) if specification else list()
        self.input_files = list(specification.input_files) if specification else list()
        self.output_vars = list(specification.output_vars) if specification else list()
        self.output_files = list(specification.output_files) if specification else list()
        self.program_path = specification.path if specification else None
        self.definition = dict(item_type=ItemInfo.item_type())
        # Populate lists (this will also create headers)
        self.populate_input_vars_list(self.input_vars)
        self.populate_input_files_list(self.input_files)
        self.populate_output_vars_list(self.output_vars)
        self.populate_output_files_list(self.output_files)
        self.ui.lineEdit_name.setFocus()
        self.connect_signals()
        if self.program_path is not None:  # It's None if the path does not exist
            self.set_jupyter_notebook_file(os.path.join(self.program_path, self.jupyter_notebook_file))

    def connect_signals(self):
        """Connect signals to slots."""
        self.ui.lineEdit_Jupyter_notebook.file_dropped.connect(self.set_jupyter_notebook_file)
        self.ui.lineEdit_Jupyter_notebook.textChanged.connect(self.validate_jupyter_notebook_file)
        self.ui.textEdit_jupyter_notebook.document().modificationChanged.connect(
            self.ui.toolButton_save_jupyter_notebook.setEnabled
        )

        self.ui.toolButton_new_jupyter_notebook.clicked.connect(self.new_jupyter_notebook)
        self.ui.toolButton_browse_jupyter_notebook.clicked.connect(self.browse_jupyter_notebook_file)
        self.ui.toolButton_save_jupyter_notebook.clicked.connect(self.save_jupyter_notebook_file)
        self.ui.toolButton_plus_input_vars.clicked.connect(self.add_input_vars)
        self.ui.toolButton_minus_input_vars.clicked.connect(self.remove_input_vars)
        self.ui.toolButton_plus_input_files.clicked.connect(self.add_input_files)
        self.ui.toolButton_minus_input_files.clicked.connect(self.remove_input_files)
        self.ui.toolButton_plus_output_vars.clicked.connect(self.add_output_vars)
        self.ui.toolButton_minus_output_vars.clicked.connect(self.remove_output_vars)
        self.ui.toolButton_plus_output_files.clicked.connect(self.add_output_files)
        self.ui.toolButton_minus_output_files.clicked.connect(self.remove_output_files)
        self.ui.pushButton_ok.clicked.connect(self.handle_ok_clicked)
        self.ui.pushButton_cancel.clicked.connect(self.close)
        # Enable removing items from QTreeViews by pressing the Delete key
        self.ui.treeView_input_vars.del_key_pressed.connect(self.remove_input_vars_with_del)
        self.ui.treeView_input_files.del_key_pressed.connect(self.remove_input_files_with_del)
        self.ui.treeView_output_vars.del_key_pressed.connect(self.remove_output_vars_with_del)
        self.ui.treeView_output_files.del_key_pressed.connect(self.remove_output_files_with_del)

    def populate_input_vars_list(self, items):
        """List source files in QTreeView.
        If items is None or empty list, model is cleared.
        """
        self.input_vars_model.clear()
        self.input_vars_model.setHorizontalHeaderItem(0, QStandardItem("Jupyter notebook input variables"))  # Add header
        if items is not None:
            for item in items:
                qitem = QStandardItem(item)
                qitem.setFlags(~Qt.ItemIsEditable)
                qitem.setData(QFileIconProvider().icon(QFileInfo(item)), Qt.DecorationRole)
                self.input_vars_model.appendRow(qitem)

    def populate_input_files_list(self, items):
        """List input files in QTreeView.
        If items is None or empty list, model is cleared.
        """
        self.input_files_model.clear()
        self.input_files_model.setHorizontalHeaderItem(0, QStandardItem("Input files"))  # Add header
        if items is not None:
            for item in items:
                qitem = QStandardItem(item)
                qitem.setData(QFileIconProvider().icon(QFileInfo(item)), Qt.DecorationRole)
                self.input_files_model.appendRow(qitem)

    def populate_output_vars_list(self, items):
        """List optional input files in QTreeView.
        If items is None or empty list, model is cleared.
        """
        self.output_vars_model.clear()
        self.output_vars_model.setHorizontalHeaderItem(0, QStandardItem("Jupyter notebook output variables"))  # Add header
        if items is not None:
            for item in items:
                qitem = QStandardItem(item)
                qitem.setData(QFileIconProvider().icon(QFileInfo(item)), Qt.DecorationRole)
                self.output_vars_model.appendRow(qitem)

    def populate_output_files_list(self, items):
        """List output files in QTreeView.
        If items is None or empty list, model is cleared.
        """
        self.output_files_model.clear()
        self.output_files_model.setHorizontalHeaderItem(0, QStandardItem("Output files"))  # Add header
        if items is not None:
            for item in items:
                qitem = QStandardItem(item)
                qitem.setData(QFileIconProvider().icon(QFileInfo(item)), Qt.DecorationRole)
                self.output_files_model.appendRow(qitem)

    @Slot(bool)
    def browse_jupyter_notebook_file(self, checked=False):
        """Open file browser where user can select the path of the main program file."""
        # noinspection PyCallByClass, PyTypeChecker, PyArgumentList
        answer = QFileDialog.getOpenFileName(
            self, "Select existing jupyter notebook file", self._project.project_dir, "*.*"
        )
        file_path = answer[0]
        if not file_path:  # Cancel button clicked
            return
        self.set_jupyter_notebook_file(file_path)

    @Slot("QString")
    def set_jupyter_notebook_file(self, file_path):
        """Set main program file and folder path."""
        self.ui.lineEdit_Jupyter_notebook.setText(file_path)

    @Slot(str)
    def validate_jupyter_notebook_file(self, file_path):
        folder_path = os.path.split(file_path)[0]
        self.program_path = os.path.abspath(folder_path)
        # Update UI
        self.ui.label_mainpath.setText(self.program_path)
        if not os.path.isfile(file_path):
            self.show_status_bar_msg("Jupyter notebook file is not valid")
            self.ui.widget_main_program.setVisible(False)
            return
        self.ui.widget_main_program.setVisible(True)
        # Load main program file into text edit
        try:
            with open(file_path, 'r') as file:
                text = file.read()
            self.ui.textEdit_jupyter_notebook.setPlainText(text)
        except IOError as e:
            self.show_status_bar_msg(e)

    @Slot(bool)
    def save_jupyter_notebook_file(self, _=False):
        """Saves main program file."""
        notebook = self.ui.lineEdit_Jupyter_notebook.text().strip()
        try:
            with open(notebook, "w") as file:
                file.write(self.ui.textEdit_jupyter_notebook.toPlainText())
            self.ui.textEdit_jupyter_notebook.document().setModified(False)
            self.show_status_bar_msg(f"Main program file '{os.path.basename(notebook)}' saved successfully")
        except IOError as e:
            self.show_status_bar_msg(e)

    @Slot(bool)
    def new_jupyter_notebook(self, _=False):
        """Creates a new blank main program file. Let's user decide the file name and path.
         Alternative version using only one getSaveFileName dialog.
         """
        # noinspection PyCallByClass
        answer = QFileDialog.getSaveFileName(self, "Create new jupyter notebook", self._project.project_dir)
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
        self.set_jupyter_notebook_file(file_path)

    @Slot(bool)
    def add_input_vars(self, checked=False):
        """Let user select output variables for this notebook specification."""
        msg = (
            "Add input variables that may be utilized by your notebook. <br/>"
            "The input variable name must be declared in the jupyter notebook.<br/>"
            "The declared input variable must be inside a \"parameters\" tagged cell.<br/>"
            "The \"parameters\" tagged cell should be placed as the first cell in the notebook.<br/>"
            "variables in the tagged cell can be declared None or given a default value<br/>"
        )
        # noinspection PyCallByClass, PyTypeChecker, PyArgumentList
        answer = QInputDialog.getText(
            self, "Add input variable", msg, flags=Qt.WindowTitleHint | Qt.WindowCloseButtonHint
        )
        file_name = answer[0]
        if not file_name:  # Cancel button clicked
            return
        qitem = QStandardItem(file_name)
        qitem.setData(QFileIconProvider().icon(QFileInfo(file_name)), Qt.DecorationRole)
        self.input_vars_model.appendRow(qitem)

    @Slot()
    def remove_input_vars_with_del(self):
        """Support for deleting items with the Delete key."""
        self.remove_input_vars()

    @Slot(bool)
    def remove_input_vars(self, checked=False):
        """Remove selected optional input files from list.
        Do not remove anything if there are no items selected.
        """
        indexes = self.ui.treeView_input_vars.selectedIndexes()
        if not indexes:  # Nothing selected
            self.show_status_bar_msg("Please select the input variables to remove")
        else:
            rows = [ind.row() for ind in indexes]
            rows.sort(reverse=True)
            for row in rows:
                self.input_vars_model.removeRow(row)
            self.show_status_bar_msg("Selected input variables removed")

    @Slot(bool)
    def add_input_files(self, checked=False):
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
        qitem = QStandardItem(file_name)
        qitem.setData(QFileIconProvider().icon(QFileInfo(file_name)), Qt.DecorationRole)
        self.input_files_model.appendRow(qitem)

    @Slot()
    def remove_input_files_with_del(self):
        """Support for deleting items with the Delete key."""
        self.remove_input_files()

    @Slot(bool)
    def remove_input_files(self, checked=False):
        """Remove selected input files from list.
        Do not remove anything if there are no items selected.
        """
        indexes = self.ui.treeView_input_files.selectedIndexes()
        if not indexes:  # Nothing selected
            self.show_status_bar_msg("Please select the input files to remove")
        else:
            rows = [ind.row() for ind in indexes]
            rows.sort(reverse=True)
            for row in rows:
                self.input_files_model.removeRow(row)
            self.show_status_bar_msg("Selected input files removed")

    @Slot(bool)
    def add_output_vars(self, checked=False):
        """Let user select output variables for this notebook specification."""
        msg = (
            "Add output variables that may be utilized by your notebook. <br/>"
            "The output variable name must be declared in the jupyter notebook.<br/>"
            "The declared output variable must be inside a \"parameters\" tagged cell.<br/>"
            "The \"parameters\" tagged cell is best to be placed as the first cell in the notebook.<br/>"
            "variables in the tagged cell can be declared None or given a default value<br/>"
        )
        # noinspection PyCallByClass, PyTypeChecker, PyArgumentList
        answer = QInputDialog.getText(
            self, "Add output variable", msg, flags=Qt.WindowTitleHint | Qt.WindowCloseButtonHint
        )
        file_name = answer[0]
        if not file_name:  # Cancel button clicked
            return
        qitem = QStandardItem(file_name)
        qitem.setData(QFileIconProvider().icon(QFileInfo(file_name)), Qt.DecorationRole)
        self.output_vars_model.appendRow(qitem)

    @Slot()
    def remove_output_vars_with_del(self):
        """Support for deleting items with the Delete key."""
        self.remove_output_vars()

    @Slot(bool)
    def remove_output_vars(self, checked=False):
        """Remove selected optional input files from list.
        Do not remove anything if there are no items selected.
        """
        indexes = self.ui.treeView_output_vars.selectedIndexes()
        if not indexes:  # Nothing selected
            self.show_status_bar_msg("Please select the output variables to remove")
        else:
            rows = [ind.row() for ind in indexes]
            rows.sort(reverse=True)
            for row in rows:
                self.output_vars_model.removeRow(row)
            self.show_status_bar_msg("Selected output variables removed")

    @Slot(bool)
    def add_output_files(self, checked=False):
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
        qitem = QStandardItem(file_name)
        qitem.setData(QFileIconProvider().icon(QFileInfo(file_name)), Qt.DecorationRole)
        self.output_files_model.appendRow(qitem)

    @Slot()
    def remove_output_files_with_del(self):
        """Support for deleting items with the Delete key."""
        self.remove_output_files()

    @Slot(bool)
    def remove_output_files(self, checked=False):
        """Remove selected output files from list.
        Do not remove anything if there are no items selected.
        """
        indexes = self.ui.treeView_output_files.selectedIndexes()
        if not indexes:  # Nothing selected
            self.show_status_bar_msg("Please select the output files to remove")
        else:
            rows = [ind.row() for ind in indexes]
            rows.sort(reverse=True)
            for row in rows:
                self.output_files_model.removeRow(row)
            self.show_status_bar_msg("Selected output files removed")

    @Slot()
    def handle_ok_clicked(self):
        """Checks that everything is valid, creates Tool spec definition dictionary and adds Tool spec to project."""
        # Check that tool type is selected
        if self.ui.comboBox_notebook_type.currentIndex() == 0:
            self.show_status_bar_msg("Notebook type not selected")
            return
        self.definition["name"] = self.ui.lineEdit_name.text()
        self.definition["description"] = self.ui.textEdit_description.toPlainText()
        self.definition["notebook_type"] = self.ui.comboBox_notebook_type.currentText().lower()
        flags = Qt.MatchContains
        # Check that path of main program file is valid before saving it
        jupyter_notebook = self.ui.lineEdit_Jupyter_notebook.text().strip()
        if not os.path.isfile(jupyter_notebook):
            self.show_status_bar_msg("Jupyter notebook is not valid")
            return
        # Fix for issue #241
        folder_path, file_path = os.path.split(jupyter_notebook)
        self.program_path = os.path.abspath(folder_path)
        self.ui.label_mainpath.setText(self.program_path)
        self.definition["execute_in_work"] = self.ui.checkBox_execute_in_work.isChecked()
        self.definition["includes"] = [file_path]
        self.definition["input_vars"] = [i.text() for i in self.input_vars_model.findItems("", flags)]
        self.definition["input_files"] = [i.text() for i in self.input_files_model.findItems("", flags)]
        self.definition["output_vars"] = [i.text() for i in self.output_vars_model.findItems("", flags)]
        self.definition["output_files"] = [i.text() for i in self.output_files_model.findItems("", flags)]
        # Strip whitespace from args before saving it to JSON
        self.definition["cmdline_args"] = split_cmdline_args(self.ui.lineEdit_args.text())
        for k in REQUIRED_KEYS:
            if not self.definition[k]:
                self.show_status_bar_msg(f"{k} missing")
                return
        # Create new Tool specification
        if self.call_add_notebook_specification():
            self.close()

    def _make_notebook_specification(self):
        """Returns a NotebookSpecification from current form settings.

        Returns:
            NotebookSpecification
        """
        self.definition["includes_main_path"] = self.program_path.replace(os.sep, "/")
        notebook = self._toolbox.load_specification(self.definition)
        if not notebook:
            self.show_status_bar_msg("Adding Notebook specification failed")
        return notebook

    def call_add_notebook_specification(self):
        """Adds or updates Tool specification according to user's selections.
        If the name is the same as an existing tool specification, it is updated and
        auto-saved to the definition file. (User is editing an existing
        tool specification.) If the name is not in the tool specification model, creates
        a new tool specification and offers to save the definition file. (User is
        creating a new tool specification from scratch or spawning from an existing one).
        """
        new_spec = self._make_notebook_specification()
        if not new_spec:
            return False
        if self._original_specification is not None and new_spec.is_equivalent(self._original_specification):
            # Nothing changed
            return True
        if self._original_specification is None or self.definition["name"] != self._original_specification.name:
            # The user is creating a new spec, either from scratch (no original spec)
            # or by changing the name of an existing one
            self._toolbox.add_specification(new_spec)
        else:
            # The user is modifying an existing spec, while conserving the name
            new_spec.definition_file_path = self._original_specification.definition_file_path
            self._toolbox.update_specification(new_spec)
        return True

    def keyPressEvent(self, e):
        """Close Setup form when escape key is pressed.

        Args:
            e (QKeyEvent): Received key press event.
        """
        if e.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event=None):
        """Handle close window.

        Args:
            event (QEvent): Closing event if 'X' is clicked.
        """
        if event:
            event.accept()

    def show_status_bar_msg(self, msg):
        word_count = len(msg.split(" "))
        mspw = 60000 / 140  # Assume people can read ~140 words per minute
        duration = mspw * word_count
        self.statusbar.showMessage(msg, duration)
