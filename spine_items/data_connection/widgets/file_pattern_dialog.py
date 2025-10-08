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
import pathlib
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFileDialog, QWidget
from ..utils import FilePattern


class FilePatternDialog(QDialog):
    def __init__(self, title: str, pattern: FilePattern | None, base_dir: pathlib.Path, parent: QWidget | None):
        from ..ui.file_pattern_dialog import Ui_Form

        super().__init__(parent)
        self._ui = Ui_Form()
        self._ui.setupUi(self)
        self.setWindowTitle(title)
        self._pattern = pattern
        if self._pattern is not None:
            self._ui.directory_line_edit.setText(str(self._pattern.base_path))
            self._ui.pattern_line_edit.setText(self._pattern.pattern)
        self._base_dir = base_dir
        self._ui.browse_button.clicked.connect(self._browse_directory)
        self._ui.directory_line_edit.textChanged.connect(self._check_enabled_buttons)
        self._ui.pattern_line_edit.textChanged.connect(self._check_enabled_buttons)
        self._ui.button_box.accepted.connect(self.accept)
        self._ui.button_box.rejected.connect(self.reject)
        self._check_enabled_buttons()

    @Slot(bool)
    def _browse_directory(self, _: bool) -> None:
        current_dir = self._ui.directory_line_edit.text()
        start_directory = current_dir if current_dir else str(self._base_dir)
        path = QFileDialog.getExistingDirectory(self, "Select directory", start_directory)
        if not path:
            return
        self._ui.directory_line_edit.setText(str(pathlib.Path(path)))

    @Slot(str)
    def _check_enabled_buttons(self, _="") -> None:
        enabled = bool(self._ui.directory_line_edit.text()) and bool(self._ui.pattern_line_edit.text())
        self._ui.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(enabled)

    def file_pattern(self) -> FilePattern:
        return FilePattern(pathlib.Path(self._ui.directory_line_edit.text()), self._ui.pattern_line_edit.text())
