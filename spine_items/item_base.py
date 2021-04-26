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
Contains base class for project items.

:author: A. Soininen (VTT)
:date:   15.12.2020
"""

from itertools import zip_longest
from PySide2.QtCore import Qt, Slot
from spinedb_api import clear_filter_configs
from spinetoolbox.project_item.project_item import ProjectItem
from spine_engine.utils.serialization import serialize_url
from spine_items.models import DatabaseListModel
from spine_items.utils import Database
from spine_items.exporter.widgets.export_list_item import ExportListItem
from .commands import UpdateCancelOnErrorCommand, UpdateOutFileName, UpdateOutputTimeStampsFlag
from .models import FullUrlListModel
from .utils import ExporterNotifications, exported_files_as_resources


class ExporterBase(ProjectItem):
    """A base class for exporter project items."""

    def __init__(
        self, name, description, x, y, toolbox, project, databases=None, output_time_stamps=False, cancel_on_error=True
    ):
        """
        Args:
            name (str): item name
            description (str): item description
            x (float): initial X coordinate of item icon
            y (float): initial Y coordinate of item icon
            toolbox (ToolboxUI): a ToolboxUI instance
            project (SpineToolboxProject): the project this item belongs to
            databases (list, optional): a list of :class:`Database` instances
            output_time_stamps (bool): True if time stamps should be appended to output directory names,
                False otherwise
            cancel_on_error (bool): True if execution should fail on all export errors,
                False to ignore certain error cases; optional to provide backwards compatibility
        """
        super().__init__(name, description, x, y, project)
        self._toolbox = toolbox
        self._notifications = ExporterNotifications()
        self._append_output_time_stamps = output_time_stamps
        self._cancel_on_error = cancel_on_error
        if databases is None:
            databases = list()
        self._database_model = DatabaseListModel(databases)
        self._inactive_databases = dict()
        self._output_filenames = dict()
        self._export_list_items = dict()
        self._full_url_model = FullUrlListModel()
        self._exported_files = None

    @staticmethod
    def item_type():
        """See base class."""
        raise NotImplementedError()

    @staticmethod
    def item_category():
        """See base class."""
        raise NotImplementedError()

    @property
    def executable_class(self):
        raise NotImplementedError()

    def handle_execution_successful(self, execution_direction, engine_state):
        """See base class."""
        if execution_direction != "FORWARD":
            return
        self._resources_to_successors_changed()

    def database(self, url):
        """
        Returns database information for given URL.

        Args:
            url (str): database URL

        Returns:
            Database: database information
        """
        return self._database_model.item(url)

    def full_url_model(self):
        """
        Returns the full URL model held by the exporter.

        Returns:
            FullUrlListModel: full URL model
        """
        return self._full_url_model

    def make_signal_handler_dict(self):
        """Returns a dictionary of all shared signals and their handlers."""
        s = super().make_signal_handler_dict()
        s[self._properties_ui.open_directory_button.clicked] = lambda _: self.open_directory()
        s[self._properties_ui.output_time_stamps_check_box.stateChanged] = self._change_output_time_stamps_flag
        s[self._properties_ui.cancel_on_error_check_box.stateChanged] = self._cancel_on_error_option_changed
        return s

    def restore_selections(self):
        """Restores selections and connects signals."""
        self._properties_ui.item_name_label.setText(self.name)
        self._update_properties_tab()

    def _update_properties_tab(self):
        """Updates the database list in the properties tab."""
        database_list_storage = self._properties_ui.databases_list_layout
        while not database_list_storage.isEmpty():
            widget_to_remove = database_list_storage.takeAt(0)
            widget_to_remove.widget().deleteLater()
        self._export_list_items.clear()
        for db in self._database_model.items():
            item = self._export_list_items[db.url] = ExportListItem(db.url, db.output_file_name)
            database_list_storage.addWidget(item)
            item.file_name_changed.connect(self._update_out_file_name)
        self._properties_ui.output_time_stamps_check_box.setCheckState(
            Qt.Checked if self._append_output_time_stamps else Qt.Unchecked
        )
        self._properties_ui.cancel_on_error_check_box.setCheckState(
            Qt.Checked if self._cancel_on_error else Qt.Unchecked
        )

    def upstream_resources_updated(self, resources):
        """See base class."""
        full_urls = set(r.url for r in resources if r.type_ == "database")
        database_urls = set(clear_filter_configs(url) for url in full_urls)
        old_urls = self._database_model.urls()
        if database_urls != old_urls:
            common = old_urls & database_urls
            old_urls_by_base = dict()
            for url in old_urls:
                if url not in common:
                    old_urls_by_base.setdefault(clear_filter_configs(url), list()).append(url)
            old_urls_by_base = {base: sorted(url_list) for base, url_list in old_urls_by_base.items()}
            new_urls_by_base = dict()
            for url in database_urls:
                if url not in common:
                    new_urls_by_base.setdefault(clear_filter_configs(url), list()).append(url)
            new_urls_by_base = {base: sorted(url_list) for base, url_list in new_urls_by_base.items()}
            useless_oldies = set()
            homeless_new_urls = set()
            for new_base, newbies in new_urls_by_base.items():
                oldies = old_urls_by_base.get(new_base)
                if oldies is None:
                    homeless_new_urls |= set(newbies)
                    continue
                for oldie, newbie in zip_longest(oldies, newbies):
                    if oldie is None:
                        homeless_new_urls.add(newbie)
                        continue
                    if newbie is None:
                        useless_oldies.add(oldie)
                        continue
                    self._database_model.update_url(oldie, newbie)
            useless_oldies |= old_urls - database_urls
            for url in useless_oldies:
                self._inactive_databases[url] = self._database_model.remove(url)
            for url in homeless_new_urls:
                db = self._inactive_databases.pop(url, None)
                if db is None:
                    db = Database()
                    db.url = url
                self._database_model.add(db)
        self._full_url_model.set_urls(full_urls)
        if self._active:
            self._update_properties_tab()
        self._check_notifications()

    def replace_resource_from_upstream(self, old, new):
        """See base class."""
        if not old.type_ == "database":
            return
        self._database_model.update_url(clear_filter_configs(old.url), clear_filter_configs(new.url))
        self._full_url_model.update_url(old.url, new.url)

    def _check_notifications(self):
        """
        Checks the status of database export settings.

        Updates both the notification message (exclamation icon) and settings states.
        """
        self._check_missing_file_names()
        self._check_duplicate_file_names()
        self._check_missing_specification()
        self._report_notifications()

    def _check_missing_file_names(self):
        """Checks the status of output file names."""
        self._notifications.missing_output_file_name = not all(
            bool(db.output_file_name) for db in self._database_model.items()
        )

    def _check_duplicate_file_names(self):
        """Checks for duplicate output file names."""
        self._notifications.duplicate_output_file_name = False
        names = set()
        for db in self._database_model.items():
            if db.output_file_name in names:
                self._notifications.duplicate_output_file_name = True
                break
            names.add(db.output_file_name)

    def _check_missing_specification(self):
        """Checks specification's status."""
        raise NotImplementedError()

    def _report_notifications(self):
        """Updates the exclamation icon and notifications labels."""
        if self._icon is None:
            return
        self.clear_notifications()
        if self._notifications.duplicate_output_file_name:
            self.add_notification("Duplicate output file names.")
        if self._notifications.missing_output_file_name:
            self.add_notification("Output file name(s) missing.")
        if self._notifications.missing_specification:
            self.add_notification("Export specification missing.")

    @Slot(str, str)
    def _update_out_file_name(self, file_name, url):
        """Pushes a new UpdateExporterOutFileNameCommand to the toolbox undo stack."""
        self._toolbox.undo_stack.push(UpdateOutFileName(self, file_name, url))

    @Slot(int)
    def _change_output_time_stamps_flag(self, checkbox_state):
        """
        Pushes a command that changes the output time stamps flag value.

        Args:
            checkbox_state (int): setting's checkbox state on properties tab
        """
        flag = checkbox_state == Qt.Checked
        if flag == self._append_output_time_stamps:
            return
        self._toolbox.undo_stack.push(UpdateOutputTimeStampsFlag(self, flag))

    def set_output_time_stamps_flag(self, flag):
        """
        Sets the output time stamps flag.

        Args:
            flag (bool): flag value
        """
        self._append_output_time_stamps = flag

    @Slot(int)
    def _cancel_on_error_option_changed(self, checkbox_state):
        """Handles changes to the Cancel export on error option."""
        cancel = checkbox_state == Qt.Checked
        if self._cancel_on_error == cancel:
            return
        self._toolbox.undo_stack.push(UpdateCancelOnErrorCommand(self, cancel))

    def set_cancel_on_error(self, cancel):
        """Sets the Cancel export on error option."""
        self._cancel_on_error = cancel
        if not self._active:
            return
        # This does not trigger the stateChanged signal.
        self._properties_ui.cancel_on_error_check_box.setCheckState(Qt.Checked if cancel else Qt.Unchecked)

    def set_out_file_name(self, file_name, database_path):
        """Updates the output file name for given database"""
        if self._active:
            export_list_item = self._export_list_items[database_path]
            export_list_item.out_file_name_edit.setText(file_name)
        database = self._database_model.item(database_path)
        old_file_name = database.output_file_name
        old_resources = self.resources_for_direct_successors() if old_file_name else []
        database.output_file_name = file_name
        self._notifications.missing_output_file_name = not file_name
        self._check_duplicate_file_names()
        self._report_notifications()
        if self._exported_files is not None:
            exported_files = self._exported_files.pop(old_file_name, None)
            if exported_files is not None and file_name:
                self._exported_files[file_name] = exported_files
        if not old_file_name or not file_name:
            self._resources_to_successors_changed()
        else:
            new_resources = self.resources_for_direct_successors()
            olds = (resource for resource in old_resources if resource.label == old_file_name)
            news = (resource for resource in new_resources if resource.label == file_name)
            for old, new in zip(olds, news):
                self._resource_to_successors_replaced(old, new)

    def item_dict(self):
        """Returns a dictionary corresponding to this item's configuration."""
        d = super().item_dict()
        databases = list()
        for db in self._database_model.items():
            db_dict = db.to_dict()
            serialized_url = serialize_url(db.url, self._project.project_dir)
            db_dict["database_url"] = serialized_url
            databases.append(db_dict)
        d["databases"] = databases
        d["output_time_stamps"] = self._append_output_time_stamps
        d["cancel_on_error"] = self._cancel_on_error
        return d

    @staticmethod
    def from_dict(name, item_dict, toolbox, project):
        """See base class"""
        raise NotImplementedError()

    def update_name_label(self):
        """See base class."""
        self._properties_ui.item_name_label.setText(self.name)

    def resources_for_direct_successors(self):
        """See base class."""
        resources, self._exported_files = exported_files_as_resources(
            self.name, self._exported_files, self.data_dir, self._database_model.items()
        )
        return resources

    def tear_down(self):
        super().tear_down()
        self._database_model.deleteLater()
        self._full_url_model.deleteLater()
