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

"""Contains controller that manages value transformations editor."""
from PySide6.QtCore import QModelIndex, QObject, Slot
from PySide6.QtWidgets import QLineEdit, QFormLayout
from ..commands import AppendInstruction, ChangeInstructionParameter, ChangeOperation, RemoveInstruction
from ..mvcmodels.value_transformations_table_model import TransformationsTableColumn, TransformationsTableRole


_DISPLAY_TEXT_TO_OPERATION = {
    "multiply": "multiply",
    "invert": "invert,",
    "negate": "negate",
    "generate index": "generate_index",
}

_OPERATION_TO_DISPLAY_TEXT = {op: label for label, op in _DISPLAY_TEXT_TO_OPERATION.items()}


class InstructionsEditor(QObject):
    def __init__(self, ui, transformations_table_model, undo_stack, parent):
        """
        Args:
            ui (Ui_Form): ValueTransformingWidget's interface
            transformations_table_model (ValueTransformationTableModel): transforms table model
            undo_stack (QUndoStack): undo stack
            parent (QObject): parent object
        """
        super().__init__(parent)
        self._transformations_table_model = transformations_table_model
        self._transformations_table_index = QModelIndex()
        self._undo_stack = undo_stack
        self._ui = ui
        for operation_label in _DISPLAY_TEXT_TO_OPERATION:
            self._ui.operation_combo_box.addItem(operation_label)
        self._ui.add_instruction_button.clicked.connect(self._add_instruction)
        self._ui.remove_instruction_button.clicked.connect(self._ui.remove_instruction_action.trigger)
        self._ui.remove_instruction_action.triggered.connect(self._remove_instruction)
        self._ui.instructions_list_view.addAction(self._ui.remove_instruction_action)
        self._ui.instructions_list_view.currentRowChanged.connect(self._update_operation_editor)
        self._ui.operation_combo_box.currentTextChanged.connect(self._change_operation)
        self._ui.transformations_table_view.selectionModel().currentChanged.connect(self._transformation_changed)

    @Slot(bool)
    def _add_instruction(self, checked):
        """Pushes an append instruction command to undo stack.

        Args:
            checked (bool): unused
        """
        operation = _DISPLAY_TEXT_TO_OPERATION[self._ui.operation_combo_box.itemText(0)]
        instruction = {"operation": operation}
        if operation == "multiply":
            instruction["rhs"] = 1.0
        elif operation == "generate_index":
            instruction["expression"] = ""
        self._undo_stack.push(AppendInstruction(self, instruction))

    def append_instruction(self, instruction):
        """Appends an instruction to instructions list.

        Args:
            instruction (dict): instruction to append
        """
        row = self._ui.instructions_list_view.count()
        self.insert_instruction(row, instruction)

    def insert_instruction(self, i, instruction):
        """Inserts an instruction to instructions list.

        Args:
            i (int): insertion point
            instruction (dict): instruction to append
        """
        instructions = self._transformations_table_model.data(
            self._transformations_table_index, TransformationsTableRole.INSTRUCTIONS
        )
        instructions.insert(i, instruction)
        self._transformations_table_model.setData(
            self._transformations_table_index, instructions, TransformationsTableRole.INSTRUCTIONS
        )
        self._ui.instructions_list_view.insertItem(i, instruction["operation"])
        self._ui.instructions_list_view.setCurrentRow(i)
        self._ui.operation_combo_box.setEnabled(True)

    @Slot(bool)
    def _remove_instruction(self, checked):
        """Pushes a remove instruction command to undo stack.

        Args:
            checked (bool): unused
        """
        row = self._ui.instructions_list_view.currentRow()
        if row < 0:
            return
        self._undo_stack.push(RemoveInstruction(self, row))

    def pop_instruction(self, i):
        """Pops last instruction from instructions list.

        Args:
            i (int): instruction index; if negative, pop from back
        """
        row = i if i >= 0 else self._ui.instructions_list_view.count() + i
        self._ui.instructions_list_view.takeItem(row)
        if self._ui.instructions_list_view.count() == 0:
            self._ui.operation_combo_box.setEnabled(False)
            self._remove_operation_widgets()
        instructions = self._transformations_table_model.data(
            self._transformations_table_index, TransformationsTableRole.INSTRUCTIONS
        )
        instructions.pop(i)
        self._transformations_table_model.setData(
            self._transformations_table_index, instructions, TransformationsTableRole.INSTRUCTIONS
        )

    def _load_instructions(self, row):
        """Updates widgets.

        Args:
            row (int): row index to ValueTransformationsTableModel
        """
        if row == -1:
            self._transformations_table_index = QModelIndex()
            self._ui.instructions_list_view.clear()
            return
        self._transformations_table_index = self._transformations_table_model.index(
            row, TransformationsTableColumn.INSTRUCTIONS
        )
        instructions = self._transformations_table_model.data(
            self._transformations_table_index, TransformationsTableRole.INSTRUCTIONS
        )
        self._ui.instructions_list_view.clear()
        self._ui.instructions_list_view.addItems([t["operation"] for t in instructions])
        self._enable_widgets()

    @Slot(str)
    def _change_operation(self, operation_label):
        """Pushes a change operation command to undo stack.

        Args:
            operation_label (str): operation's display text
        """
        row = self._ui.instructions_list_view.currentRow()
        self._undo_stack.push(ChangeOperation(self, row, _DISPLAY_TEXT_TO_OPERATION[operation_label]))

    def set_operation(self, i, operation):
        """Sets an operation for instruction.

        Args:
            i (int), instruction index
            operation (str): operation
        """
        instructions = self._transformations_table_model.data(
            self._transformations_table_index, TransformationsTableRole.INSTRUCTIONS
        )
        instruction = {"operation": operation}
        if operation == "multiply":
            instruction["rhs"] = 1.0
        elif operation == "generate_index":
            instruction["expression"] = ""
        instructions[i] = instruction
        self._transformations_table_model.setData(
            self._transformations_table_index, instructions, TransformationsTableRole.INSTRUCTIONS
        )
        self._ui.instructions_list_view.item(i).setText(operation)
        if i == self._ui.instructions_list_view.currentRow():
            self._update_operation_editor(i)

    def instruction(self, i):
        """Returns instruction from index.

        Args:
            i (int): instruction index

        Returns:
            dict: instruction
        """
        instructions = self._transformations_table_model.data(
            self._transformations_table_index, TransformationsTableRole.INSTRUCTIONS
        )
        return instructions[i]

    def set_instruction(self, i, instruction):
        """Sets instruction.

        Args:
            i (int): instruction index
            instruction (dict): instruction
        """
        instructions = self._transformations_table_model.data(
            self._transformations_table_index, TransformationsTableRole.INSTRUCTIONS
        )
        instructions[i] = instruction
        self._transformations_table_model.setData(
            self._transformations_table_index, instructions, TransformationsTableRole.INSTRUCTIONS
        )
        self._ui.instructions_list_view.item(i).setText(instruction["operation"])
        if i == self._ui.instructions_list_view.currentRow():
            self._update_operation_editor(i)

    def _enable_widgets(self):
        """Enables or disables widgets that deal with value operations."""
        enabled = self._ui.transformations_table_view.selectionModel().currentIndex().isValid()
        self._ui.add_instruction_button.setEnabled(enabled)
        self._ui.remove_instruction_button.setEnabled(enabled)
        self._ui.instructions_list_view.setEnabled(enabled)
        enabled = enabled and self._ui.instructions_list_view.currentRow() >= 0
        self._ui.operation_combo_box.setEnabled(enabled)

    @Slot(int)
    def _update_operation_editor(self, row):
        """Updates operation editor widgets.

        Args:
            row (int): row index to operations list view
        """
        if row == -1:
            self._enable_widgets()
            return
        instructions = self._transformations_table_model.data(
            self._transformations_table_index, TransformationsTableRole.INSTRUCTIONS
        )
        instruction = instructions[row]
        operation = instruction["operation"]
        self._ui.operation_combo_box.currentTextChanged.disconnect(self._change_operation)
        self._ui.operation_combo_box.setCurrentText(_OPERATION_TO_DISPLAY_TEXT[operation])
        self._ui.operation_combo_box.currentTextChanged.connect(self._change_operation)
        self._make_operation_widgets(operation)
        self._update_operation_widgets()
        self._enable_widgets()

    def _make_operation_widgets(self, operation):
        """Creates operation-specific widgets and adds them to instruction options layout.

        Args:
            operation (str): operation
        """
        self._remove_operation_widgets()
        if operation == "multiply":
            edit = QLineEdit()
            edit.editingFinished.connect(self._change_multiply_multiplier)
            self._ui.instruction_options_layout.addRow("Multiplier:", edit)
        elif operation == "generate_index":
            edit = QLineEdit()
            edit.setPlaceholderText("Enter Python expression...")
            edit.setToolTip("A Python expression, e.g. f'T{i:03}' for T001, T002,...")
            edit.editingFinished.connect(self._change_index_generator_expression)
            self._ui.instruction_options_layout.addRow("Expression:", edit)

    def _remove_operation_widgets(self):
        """Removes operation-specific widgets from instruction option layout."""
        while self._ui.instruction_options_layout.rowCount() > 1:
            row = self._ui.instruction_options_layout.removeRow(1)

    @Slot(QModelIndex, QModelIndex)
    def _transformation_changed(self, current, previous):
        """Loads new instructions to the editor.

        Args:
            current (QModelIndex): new index in parameters table
            previous (QModelIndex): previous index in parameters table
        """
        sorted_model = self._ui.transformations_table_view.model()
        current = sorted_model.mapToSource(current)
        if current.row() == self._transformations_table_index.row():
            return
        self._remove_operation_widgets()
        self._load_instructions(current.row())

    def _update_operation_widgets(self):
        """Updates operation-specific widgets."""
        row = self._ui.instructions_list_view.currentRow()
        instructions = self._transformations_table_model.data(
            self._transformations_table_index, TransformationsTableRole.INSTRUCTIONS
        )
        instruction = instructions[row]
        operation = instruction["operation"]
        if operation == "multiply":
            edit = self._ui.instruction_options_layout.itemAt(1, QFormLayout.FieldRole).widget()
            edit.setText(str(instruction["rhs"]))
        elif operation == "generate_index":
            edit = self._ui.instruction_options_layout.itemAt(1, QFormLayout.FieldRole).widget()
            edit.setText(str(instruction["expression"]))

    @Slot()
    def _change_multiply_multiplier(self):
        """Pushes a command to change multiplier coefficient to undo stack."""
        row = self._ui.instructions_list_view.currentRow()
        edit = self._ui.instruction_options_layout.itemAt(1, QFormLayout.FieldRole).widget()
        try:
            multiplier = float(edit.text())
        except ValueError:
            return
        previous_multiplier = self.instruction(row)["rhs"]
        self._undo_stack.push(ChangeInstructionParameter(row, multiplier, previous_multiplier, self._set_multiplier))

    def _set_multiplier(self, i, multiplier):
        """Sets multiply operation's multiplier.

        Args:
            i (int): instruction index
            multiplier (float): new multiplier
        """
        instructions = self._transformations_table_model.data(
            self._transformations_table_index, TransformationsTableRole.INSTRUCTIONS
        )
        instructions[i]["rhs"] = multiplier
        self._transformations_table_model.setData(
            self._transformations_table_index, instructions, TransformationsTableRole.INSTRUCTIONS
        )
        edit = self._ui.instruction_options_layout.itemAt(1, QFormLayout.FieldRole).widget()
        if i == self._ui.instructions_list_view.currentRow() and str(multiplier) != edit.text():
            edit.setText(str(multiplier))

    @Slot()
    def _change_index_generator_expression(self):
        """Pushes a command that changes index generator expression to undo stack."""
        row = self._ui.instructions_list_view.currentRow()
        edit = self._ui.instruction_options_layout.itemAt(1, QFormLayout.FieldRole).widget()
        expression = edit.text()
        try:
            eval(expression, {}, {"i": 1})
        except (AttributeError, NameError, SyntaxError, ValueError):
            self._ui.statusbar.showMessage("Invalid expression for index generator.", timeout=5000)
            if not edit.hasFocus():
                edit.setText(self.instruction(row)["expression"])
            return
        self._ui.statusbar.clearMessage()
        previous_expression = self.instruction(row)["expression"]
        self._undo_stack.push(ChangeInstructionParameter(row, expression, previous_expression, self._set_expression))

    def _set_expression(self, i, expression):
        """Sets index generator expression.

        Args:
            i (int): instruction index
            expression (str): new expression
        """
        instructions = self._transformations_table_model.data(
            self._transformations_table_index, TransformationsTableRole.INSTRUCTIONS
        )
        instructions[i]["expression"] = expression
        self._transformations_table_model.setData(
            self._transformations_table_index, instructions, TransformationsTableRole.INSTRUCTIONS
        )
        edit = self._ui.instruction_options_layout.itemAt(1, QFormLayout.FieldRole).widget()
        if i == self._ui.instructions_list_view.currentRow() and str(expression) != edit.text():
            edit.setText(expression)
