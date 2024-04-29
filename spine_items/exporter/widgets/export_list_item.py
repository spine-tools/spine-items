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

"""A small widget to set up an output in Exporter properties tab."""
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QWidget
from spine_items.utils import convert_to_sqlalchemy_url
from spine_items.widgets import UrlSelectorDialog


class ExportListItem(QWidget):
    """A widget with few controls to select the export output label."""

    _URL_SET_TEXT = "Output database URL set."
    _URL_UNSET_TEXT = "No output database URL set."
    _URL_IGNORED_TEXT = "Ignoring output database URL."

    out_label_changed = Signal(str, str)
    """Emitted when the output label field changes."""
    out_label_editing_finished = Signal(str)
    """Emitted when output label editing is finished."""
    out_url_changed = Signal(str, dict)
    """Emitted when the output URL changes."""

    def __init__(self, in_label, out_label, out_url, app_settings, logger, parent=None):
        """
        Args:
            in_label (str): input resource label
            out_label (str): output resource label
            out_url (dict): output ULR
            app_settings (QSettings): Toolbox settings
            logger (LoggerInterface): logger
            parent (QWidget): a parent widget
        """
        from ..ui.export_list_item import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(parent)
        self._ui = Ui_Form()
        self._in_label = in_label
        self._out_label = out_label
        self._out_url = out_url
        self._app_settings = app_settings
        self._logger = logger
        self._ui.setupUi(self)
        self.set_in_label(in_label)
        self._ui.out_url_status_label.setText(self._URL_UNSET_TEXT)
        self._ui.out_label_edit.setText(out_label)
        self._ui.out_label_edit.textEdited.connect(self._emit_out_label_changed)
        self._ui.out_label_edit.editingFinished.connect(self._emit_out_label_editing_finished)
        self._ui.out_url_setup_button.clicked.connect(self._show_url_dialog)
        self._ui.out_url_clear_button.clicked.connect(self._clear_out_url)

    @property
    def out_label_edit(self):
        """Output label QLineEdit"""
        return self._ui.out_label_edit

    @property
    def in_label_field(self):
        """Input label QLineEdit"""
        return self._ui.input_label_field

    def set_in_label(self, in_label):
        """Sets new input label.

        Args:
            in_label (str): input label
        """
        self._ui.input_label_field.setText(f"<b>{in_label}</b>")

    def set_out_url_enabled(self, enabled):
        """Enables or disables the output URL widgets.

        Args:
            enabled (bool): True to enable, False to disable
        """
        if not enabled:
            self._ui.out_url_status_label.setText(self._URL_IGNORED_TEXT)
        else:
            self._update_url_dependent_widgets()
        self._ui.out_url_widget.setEnabled(enabled)

    def set_out_url(self, url_dict):
        """Sets new output URL.

        Args:
            url_dict (dict, optional): URL dict
        """
        self._out_url = url_dict
        self._update_url_dependent_widgets()

    def _update_url_dependent_widgets(self):
        """Sets suitable text for the status label and enables the clear button as needed."""
        sa_url = convert_to_sqlalchemy_url(self._out_url)
        if sa_url is not None:
            self._ui.out_url_clear_button.setEnabled(True)
            self._ui.out_url_status_label.setText(self._URL_SET_TEXT)
        else:
            self._ui.out_url_clear_button.setEnabled(False)
            self._ui.out_url_status_label.setText(self._URL_UNSET_TEXT)

    @Slot(str)
    def _emit_out_label_changed(self, out_label):
        """Emits out_label_changed signal.

        Args:
            out_label (str): new out label
        """
        if self._out_label == out_label:
            return
        self._out_label = out_label
        self.out_label_changed.emit(out_label, self._in_label)

    @Slot()
    def _emit_out_label_editing_finished(self):
        self.out_label_editing_finished.emit(self._in_label)

    @Slot(bool)
    def _show_url_dialog(self, _=False):
        """Opens the URL selector dialog."""
        dialog = UrlSelectorDialog(self._app_settings, True, self._logger, self)
        if self._out_url is not None:
            dialog.set_url_dict(self._out_url)
        dialog.exec_()
        url = dialog.url_dict()
        if not url:
            return
        self.set_out_url(url)
        self.out_url_changed.emit(self._in_label, self._out_url)

    @Slot(bool)
    def _clear_out_url(self, _=False):
        """Clears the output URL."""
        self.set_out_url(None)
        self.out_url_changed.emit(self._in_label, self._out_url)
