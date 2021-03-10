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
Contains the GdxExporter project item.

:author: A. Soininen (VTT)
:date:   5.9.2019
"""

from copy import deepcopy
import os.path
from PySide2.QtCore import Slot
from spinedb_api import clear_filter_configs
from spinetoolbox.project_item.project_item import ProjectItem
from spine_engine.utils.serialization import deserialize_path
from spinedb_api.spine_io.exporters import gdx
from ..utils import Database
from ..item_base import ExporterBase
from .commands import UpdateSettings
from .executable_item import ExecutableItem
from .item_info import ItemInfo
from .settings_pack import SettingsPack
from .settings_state import SettingsState
from .widgets.gdx_export_settings import GdxExportSettings
from .worker import Worker


class GdxExporter(ExporterBase):
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
            settings_pack (SettingsPack, optional): export settings
            databases (list, optional): a list of :class:`Database` instances
            output_time_stamps (bool): True if time stamps should be appended to output directory names,
                False otherwise
            cancel_on_error (bool): True if execution should fail on all export errors,
                False to ignore certain error cases; optional to provide backwards compatibility
        """
        super().__init__(name, description, x, y, toolbox, project, databases, output_time_stamps, cancel_on_error)
        self._settings_pack = settings_pack if settings_pack is not None else SettingsPack()
        self._settings_window = None
        self._worker = None

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

    def make_signal_handler_dict(self):
        """Returns a dictionary of all shared signals and their handlers."""
        s = super().make_signal_handler_dict()
        s[self._properties_ui.settings_button.clicked] = self.show_settings
        return s

    def _check_missing_specification(self):
        self._notifications.missing_specification = (
            self._database_model.rowCount() != 0 and self._settings_pack.settings is None
        )

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
        self._check_missing_specification()
        self._report_notifications()

    def item_dict(self):
        """Returns a dictionary corresponding to this item's configuration."""
        d = super().item_dict()
        d["settings_pack"] = self._settings_pack.to_dict()
        return d

    @staticmethod
    def from_dict(name, item_dict, toolbox, project):
        """See base class"""
        if "settings_pack" not in item_dict:
            return _legacy_from_dict(name, item_dict, toolbox, project)
        description, x, y = ProjectItem.parse_item_dict(item_dict)
        settings_dict = item_dict.get("settings_pack")
        if settings_dict is None:
            settings_pack = SettingsPack()
        else:
            try:
                settings_pack = SettingsPack.from_dict(settings_dict, toolbox)
            except gdx.GdxExportException as error:
                toolbox.msg_error.emit(f"Failed to fully restore GdxExporter settings: {error}")
                settings_pack = SettingsPack()
        databases = list()
        for db_dict in item_dict["databases"]:
            db = Database.from_dict(db_dict)
            db.url = clear_filter_configs(deserialize_path(db_dict["database_url"], project.project_dir))
            databases.append(db)
        output_time_stamps = item_dict.get("output_time_stamps", False)
        cancel_on_error = item_dict.get("cancel_on_error", True)
        return GdxExporter(
            name, description, x, y, toolbox, project, settings_pack, databases, output_time_stamps, cancel_on_error
        )

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


def _legacy_from_dict(name, item_dict, toolbox, project):
    """
    Deserializes :class:`GdxExporter` from a legacy 0.5 item dict.

    Args:
        name (str): item's name
        item_dict (dict): serialized GdxExporter
        toolbox (ToolboxUI): Toolbox main widget
        project (SpineToolboxProject): project
    """
    description, x, y = ProjectItem.parse_item_dict(item_dict)
    settings_pack_dicts = item_dict.get("settings_packs")
    databases = list()
    if not settings_pack_dicts:
        settings_pack = SettingsPack()
    else:
        try:
            settings_pack = SettingsPack.from_dict(settings_pack_dicts[0], toolbox)
        except gdx.GdxExportException as error:
            toolbox.msg_error.emit(f"Failed to fully restore GdxExporter settings: {error}")
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
    return GdxExporter(name, description, x, y, toolbox, project, settings_pack, databases, cancel_on_error)
