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
Contains the GdxExporter project item.

:author: A. Soininen (VTT)
:date:   5.9.2019
"""

from copy import deepcopy
from itertools import zip_longest
import os.path
from PySide2.QtCore import Qt, Slot
from spinedb_api import clear_filter_configs
from spinetoolbox.project_item.project_item import ProjectItem
from spine_engine.utils.serialization import deserialize_path, serialize_url
from spine_engine.spine_io.exporters import gdx
from .commands import UpdateOutFileName, UpdateOutputTimeStampsFlag, UpdateSettings
from ..commands import UpdateCancelOnErrorCommand
from .database import Database
from .mvcmodels.database_list_model import DatabaseListModel
from .mvcmodels.full_url_list_model import FullUrlListModel
from .executable_item import ExecutableItem
from .item_info import ItemInfo
from .notifications import Notifications
from .output_resources import scan_for_resources
from .settings_pack import SettingsPack
from .settings_state import SettingsState
from .widgets.gdx_export_settings import GdxExportSettings
from .widgets.export_list_item import ExportListItem
from .worker import Worker


class GdxExporter(ProjectItem):
    """
    This project item handles all functionality regarding exporting a database to a .gdx file.
    """

    def __init__(
        self,
        name,
        description,
        x,
        y,
        toolbox,
        project,
        logger,
        settings_pack=None,
        databases=None,
        output_time_stamps=False,
        cancel_on_error=True,
    ):
        """
        Args:
            name (str): item name
            description (str): item description
            x (float): initial X coordinate of item icon
            y (float): initial Y coordinate of item icon
            toolbox (ToolboxUI): a ToolboxUI instance
            project (SpineToolboxProject): the project this item belongs to
            logger (LoggerInterface): a logger instance
            settings_pack (SettingsPack, optional): export settings
            databases (list, optional): a list of :class:`Database` instances
            output_time_stamps (bool): True if time stamps should be appended to output directory names,
                False otherwise
            cancel_on_error (bool): True if execution should fail on all export errors,
                False to ignore certain error cases; optional to provide backwards compatibility
        """
        super().__init__(name, description, x, y, project, logger)
        self._toolbox = toolbox
        self._notifications = Notifications()
        self._append_output_time_stamps = output_time_stamps
        self._cancel_on_error = cancel_on_error
        self._settings_pack = settings_pack if settings_pack is not None else SettingsPack()
        if databases is None:
            databases = list()
        self._database_model = DatabaseListModel(databases)
        self._providers = dict()
        self._output_filenames = dict()
        self._export_list_items = dict()
        self._settings_window = None
        self._worker = None
        self._full_url_model = FullUrlListModel()

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

    def settings_pack(self):
        """
        Returns export settings.

        Returns:
            SettingsPack: settings
        """
        return self._settings_pack

    def database(self, url):
        """
        Returns database information for given URL.

        Args:
            url (str): database URL

        Returns:
            Database: database information
        """
        return self._database_model.item(url)

    def make_signal_handler_dict(self):
        """Returns a dictionary of all shared signals and their handlers."""
        s = {
            self._properties_ui.settings_button.clicked: self.show_settings,
            self._properties_ui.open_directory_button.clicked: lambda _: self.open_directory(),
            self._properties_ui.output_time_stamps_check_box.stateChanged: self._change_output_time_stamps_flag,
            self._properties_ui.cancel_on_error_check_box.stateChanged: self._cancel_on_error_option_changed,
        }
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

    def _do_handle_dag_changed(self, resources, _):
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
                self._database_model.remove(url)
            for url in homeless_new_urls:
                db = Database()
                db.url = url
                self._database_model.add(db)
        self._full_url_model.set_urls(full_urls)
        if self._active:
            self._update_properties_tab()
        self._check_state()

    def _start_worker(self, database_url, update_settings=False):
        """Starts fetching settings using a worker in another thread."""
        worker = self._worker
        self._worker = None
        if worker is not None:
            worker.thread.quit()
            worker.thread.wait()
            worker.deleteLater()
        worker = Worker(database_url, self._settings_pack.none_fallback, self._logger)
        self._worker = worker
        worker.database_unavailable.connect(self._cancel_worker)
        worker.finished.connect(self._worker_finished)
        worker.errored.connect(self._worker_failed)
        if update_settings:
            worker.set_previous_settings(
                self._settings_window.set_settings,
                self._settings_window.indexing_settings,
                self._settings_window.merging_settings,
            )
        worker.thread.start()

    @Slot(object)
    def _worker_finished(self, result):
        """Gets and updates and export settings pack from a worker."""
        if self._worker is None:
            return
        self._worker.thread.quit()
        self._worker.thread.wait()
        self._worker.deleteLater()
        if self._settings_window is not None:
            self._settings_window.reset_settings(result.set_settings, result.indexing_settings, result.merging_settings)
        else:
            self._settings_pack.settings = result.set_settings
            self._settings_pack.indexing_settings = result.indexing_settings
            self._settings_pack.merging_settings = result.merging_settings
        self._worker = None
        self._toolbox.update_window_modified(False)
        self._check_state()

    @Slot(object)
    def _worker_failed(self, exception):
        """Clean up after a worker has failed fetching export settings."""
        if self._worker is None:
            return
        database_url = clear_filter_configs(self._worker.database_url)
        self._worker.thread.quit()
        self._worker.thread.wait()
        self._worker.deleteLater()
        self._worker = None
        if self._settings_window is not None:
            self._settings_window.settings_reading_cancelled()
        self._logger.msg_error.emit(
            f"<b>[{self.name}]</b> Initializing settings for database {database_url} failed: {exception}"
        )
        self._report_notifications()

    @Slot()
    def _cancel_worker(self):
        """Cleans up after worker has given up fetching export settings."""
        if self._worker is None:
            return
        self._worker.thread.quit()
        self._worker.thread.wait()
        self._worker.deleteLater()
        self._worker = None
        if self._settings_window is not None:
            self._settings_window.settings_reading_cancelled()

    def _check_state(self):
        """
        Checks the status of database export settings.

        Updates both the notification message (exclamation icon) and settings states.
        """
        self._check_missing_file_names()
        self._check_duplicate_file_names()
        self._check_missing_settings()
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

    def _check_missing_settings(self):
        """Checks the status of parameter indexing settings."""
        self._notifications.missing_settings = (
            self._database_model.rowCount() != 0 and self._settings_pack.settings is None
        )

    @Slot()
    def _report_notifications(self):
        """Updates the exclamation icon and notifications labels."""
        if self._icon is None:
            return
        self.clear_notifications()
        if self._notifications.duplicate_output_file_name:
            self.add_notification("Duplicate output file names.")
        if self._notifications.missing_output_file_name:
            self.add_notification("Output file name(s) missing.")
        if self._notifications.missing_settings:
            self.add_notification("Export settings missing.")

    @Slot(bool)
    def show_settings(self, _=True):
        """Opens the item's settings window."""
        # Give window its own settings and indexing domains so Cancel doesn't change anything here.
        if self._settings_window is None:
            settings = deepcopy(self._settings_pack.settings)
            indexing_settings = deepcopy(self._settings_pack.indexing_settings)
            merging_settings = deepcopy(self._settings_pack.merging_settings)
            self._settings_window = GdxExportSettings(
                settings,
                indexing_settings,
                merging_settings,
                self._settings_pack.none_fallback,
                self._settings_pack.none_export,
                self._full_url_model,
                self.name,
                self._toolbox,
            )
            self._settings_window.settings_accepted.connect(self._update_settings_from_settings_window)
            self._settings_window.settings_rejected.connect(self._dispose_settings_window)
            self._settings_window.update_requested.connect(self._update_settings_in_window)
        self._settings_window.show()

    @Slot(str)
    def _update_settings_in_window(self, database_url):
        """Updates settings currently in the Gdx Export Settings window."""
        self._start_worker(database_url, update_settings=True)

    @Slot()
    def _dispose_settings_window(self):
        """Deletes rejected export settings windows."""
        self._settings_window = None

    @Slot(str, str)
    def _update_out_file_name(self, file_name, url):
        """Pushes a new UpdateExporterOutFileNameCommand to the toolbox undo stack."""
        self._toolbox.undo_stack.push(UpdateOutFileName(self, file_name, url))

    @Slot()
    def _update_settings_from_settings_window(self):
        """Pushes a new UpdateExporterSettingsCommand to the toolbox undo stack."""
        settings = self._settings_window.set_settings
        indexing_settings = self._settings_window.indexing_settings
        merging_settings = self._settings_window.merging_settings
        self._toolbox.undo_stack.push(
            UpdateSettings(
                self,
                settings,
                indexing_settings,
                merging_settings,
                self._settings_window.none_fallback,
                self._settings_window.none_export,
            )
        )

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

    def undo_redo_out_file_name(self, file_name, database_path):
        """Updates the output file name for given database"""
        if self._active:
            export_list_item = self._export_list_items[database_path]
            export_list_item.out_file_name_edit.setText(file_name)
        self._database_model.item(database_path).output_file_name = file_name
        self._notifications.missing_output_file_name = not file_name
        self._check_duplicate_file_names()
        self._report_notifications()
        self.item_changed.emit()

    def undo_or_redo_settings(self, settings, indexing_settings, merging_settings, none_fallback, none_export):
        """Updates the export settings for given database."""
        self._settings_pack.settings = settings
        self._settings_pack.indexing_settings = indexing_settings
        self._settings_pack.merging_settings = merging_settings
        self._settings_pack.none_fallback = none_fallback
        self._settings_pack.none_export = none_export
        if self._settings_window is not None:
            self._settings_window.reset_settings(
                self._settings_pack.settings,
                self._settings_pack.indexing_settings,
                self._settings_pack.merging_settings,
            )
        self._check_missing_settings()
        self._report_notifications()

    def item_dict(self):
        """Returns a dictionary corresponding to this item's configuration."""
        d = super().item_dict()
        d["settings_pack"] = self._settings_pack.to_dict()
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
    def from_dict(name, item_dict, toolbox, project, logger):
        """See base class"""
        if "settings_pack" not in item_dict:
            return _legacy_from_dict(name, item_dict, toolbox, project, logger)
        description, x, y = ProjectItem.parse_item_dict(item_dict)
        settings_dict = item_dict.get("settings_pack")
        if settings_dict is None:
            settings_pack = SettingsPack()
        else:
            try:
                settings_pack = SettingsPack.from_dict(settings_dict, logger)
            except gdx.GdxExportException as error:
                logger.msg_error.emit(f"Failed to fully restore GdxExporter settings: {error}")
                settings_pack = SettingsPack()
        databases = list()
        for db_dict in item_dict["databases"]:
            db = Database.from_dict(db_dict)
            db.url = clear_filter_configs(deserialize_path(db_dict["database_url"], project.project_dir))
            databases.append(db)
        output_time_stamps = item_dict.get("output_time_stamps", False)
        cancel_on_error = item_dict.get("cancel_on_error", True)
        return GdxExporter(
            name,
            description,
            x,
            y,
            toolbox,
            project,
            logger,
            settings_pack,
            databases,
            output_time_stamps,
            cancel_on_error,
        )

    def update_name_label(self):
        """See base class."""
        self._properties_ui.item_name_label.setText(self.name)

    def notify_destination(self, source_item):
        """See base class."""
        if source_item.item_type() == "Data Store":
            self._logger.msg.emit(
                f"Link established. Data Store <b>{source_item.name}</b> will be "
                f"exported to a .gdx file by <b>{self.name}</b> when executing."
            )
        elif source_item.item_type() == "Data Transformer":
            self._logger.msg.emit(
                f"Link established. Data transformed by <b>{source_item.name}</b> will be "
                f"exported to a .gdx file by <b>{self.name}</b> when executing."
            )
        else:
            super().notify_destination(source_item)

    def resources_for_direct_successors(self):
        """See base class."""
        return scan_for_resources(self, self._database_model.items(), self.data_dir, include_missing=True)

    def tear_down(self):
        """See base class."""
        super().tear_down()
        if self._worker is not None:
            self._worker.thread.quit()
            self._worker.thread.wait()
            self._worker.deleteLater()

    @staticmethod
    def upgrade_v1_to_v2(item_name, item_dict):
        """Upgrades item's dictionary from v1 to v2.

        Changes:
        - output_file_name and database_url stay the same but state is set to Fetching.

        Args:
            item_name (str): item's name
            item_dict (dict): Version 1 item dictionary

        Returns:
            dict: Version 2 item dictionary
        """
        old_settings_packs = item_dict.pop("settings_packs", list())
        new_settings_packs = list()
        for pack in old_settings_packs:
            new_pack = dict()
            new_pack["output_file_name"] = pack["output_file_name"]
            new_pack["state"] = SettingsState.FETCHING.value
            new_pack["database_url"] = pack["database_url"]
            new_settings_packs.append(new_pack)
        item_dict["settings_packs"] = new_settings_packs
        return item_dict


def _normalize_url(url):
    """
    Normalized url's path separators to their OS specific characters.

    This function is needed during the transition period from no-version to version 1 project files.
    It should be removed once we are using version 1 files.
    """
    return "sqlite:///" + url[10:].replace("/", os.sep)


def _legacy_from_dict(name, item_dict, toolbox, project, logger):
    """
    Deserializes :class:`GdxExporter` from a legacy 0.5 item dict.

    Args:
        name (str): item's name
        item_dict (dict): serialized GdxExporter
        toolbox (ToolboxUI): Toolbox main widget
        project (SpineToolboxProject): project
        logger (LoggerInterface) a logger
    """
    description, x, y = ProjectItem.parse_item_dict(item_dict)
    settings_pack_dicts = item_dict.get("settings_packs")
    databases = list()
    if not settings_pack_dicts:
        settings_pack = SettingsPack()
    else:
        try:
            settings_pack = SettingsPack.from_dict(settings_pack_dicts[0], logger)
        except gdx.GdxExportException as error:
            logger.msg_error.emit(f"Failed to fully restore GdxExporter settings: {error}")
            settings_pack = SettingsPack()
        url_to_full_url = item_dict.get("urls")
        for pack in settings_pack_dicts:
            serialized_url = pack["database_url"]
            url = deserialize_path(serialized_url, project.project_dir)
            url = _normalize_url(url)
            db = Database()
            db.output_file_name = pack["output_file_name"]
            db.url = url if url_to_full_url is None else url_to_full_url[url]
            databases.append(db)
    cancel_on_error = item_dict.get("cancel_on_error", True)
    return GdxExporter(name, description, x, y, toolbox, project, logger, settings_pack, databases, cancel_on_error)
