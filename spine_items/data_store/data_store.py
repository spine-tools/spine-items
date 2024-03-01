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

""" Module for data store class. """
import os
from dataclasses import dataclass
from shutil import copyfile
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QFileDialog, QApplication, QMenu
from PySide6.QtGui import QAction
from spinedb_api.helpers import remove_credentials_from_url, vacuum
from spine_engine.project_item.project_item_resource import database_resource, ProjectItemResource
from spinetoolbox.project_item.project_item import ProjectItem
from spinetoolbox.helpers import create_dir
from spine_engine.utils.serialization import serialize_path, deserialize_path
from spinetoolbox.widgets.custom_qwidgets import SelectDatabaseItemsDialog
from .commands import UpdateDSURLCommand
from .executable_item import ExecutableItem
from .item_info import ItemInfo
from .output_resources import scan_for_resources
from ..database_validation import DatabaseConnectionValidator
from ..utils import database_label, convert_to_sqlalchemy_url


@dataclass(frozen=True)
class ReplaceableResource:
    resource: ProjectItemResource
    is_valid: bool


class DataStore(ProjectItem):
    def __init__(self, name, description, x, y, toolbox, project, url):
        """Data Store class.

        Args:
            name (str): Object name
            description (str): Object description
            x (float): Initial X coordinate of item icon
            y (float): Initial Y coordinate of item icon
            toolbox (ToolboxUI): QMainWindow instance
            project (SpineToolboxProject): the project this item belongs to
            url (dict, optional): SQLAlchemy url
        """
        super().__init__(name, description, x, y, project)
        self._toolbox = toolbox
        self.logs_dir = os.path.join(self.data_dir, "logs")
        try:
            create_dir(self.logs_dir)
        except OSError:
            self._logger.msg_error.emit(f"[OSError] Creating directory {self.logs_dir} failed. Check permissions.")
        if url is None:
            url = dict()
        self._url = self.parse_url(url)
        self._url_validated = False
        self._resource_to_replace = None
        self._multi_db_editors_open = {}
        self._open_url_menu = QMenu("Open URL in Spine DB editor", self._toolbox)
        self._open_url_action = QAction("Open URL in Spine DB editor")
        self._open_url_menu.triggered.connect(self._handle_open_url_menu_triggered)
        self._open_url_action.triggered.connect(self.open_url_in_spine_db_editor)
        self._purge_settings = None
        self._purge_dialog = None
        self._database_validator = DatabaseConnectionValidator(self)

    @staticmethod
    def item_type():
        """See base class."""
        return ItemInfo.item_type()

    @property
    def executable_class(self):
        return ExecutableItem

    def set_up(self):
        """See base class."""
        super().set_up()
        self._actions.clear()
        self._actions.append(self._open_url_action)

    def parse_url(self, url):
        """Return a complete url dictionary from the given dict or string"""
        base_url = dict(dialect="", username="", password="", host="", port="", database="", schema="")
        if isinstance(url, dict):
            if url.get("dialect") == "sqlite" and "database" in url and url["database"] is not None:
                # Convert relative database path back to absolute
                url["database"] = os.path.abspath(os.path.join(self._project.project_dir, url["database"]))
            for key, value in url.items():
                if value is not None:
                    base_url[key] = value
        return base_url

    def make_signal_handler_dict(self):
        """Returns a dictionary of all shared signals and their handlers.
        This is to enable simpler connecting and disconnecting."""
        s = super().make_signal_handler_dict()
        s[self._properties_ui.url_selector_widget.url_changed] = self._update_url_from_properties
        s[self._properties_ui.pushButton_ds_open_editor.clicked] = self.open_url_in_spine_db_editor
        s[self._properties_ui.pushButton_create_new_spine_db.clicked] = self.create_new_spine_database
        s[self._properties_ui.toolButton_copy_url.clicked] = self.copy_url
        s[self._properties_ui.toolButton_vacuum.clicked] = self.vacuum
        s[self._properties_ui.purge_button.clicked] = self._show_purge_dialog
        return s

    def restore_selections(self):
        """Load url into selections."""
        self.load_url_into_selections(self._url)

    def url(self):
        """Returns the url attribute."""
        return self._url

    def sql_alchemy_url(self):
        """Returns the URL as an SQLAlchemy URL object or None if no URL is set."""
        return convert_to_sqlalchemy_url(self._url, self.name, self._logger)

    def project(self):
        """Returns current project or None if no project open."""
        return self._project

    def select_sqlite_file(self):
        """Open file browser where user can select the path to an SQLite file that they want to use."""
        candidate_path = os.path.abspath(self._url["database"]) if self._url["database"] else self.data_dir
        answer = QFileDialog.getOpenFileName(self._toolbox, "Select SQLite file", candidate_path)
        file_path = answer[0]
        return file_path if file_path else None

    def _new_sqlite_file(self):
        """Shows a file dialog and creates a new sqlite file at the chosen path.

        Returns:
            bool: True if the file was created successfully, False otherwise
        """
        candidate_path = os.path.abspath(os.path.join(self.data_dir, self.name + ".sqlite"))
        answer = QFileDialog.getSaveFileName(self._toolbox, "Create SQLite file", candidate_path)
        file_path = answer[0]
        if not file_path:  # Cancel button clicked
            return False
        abs_path = os.path.abspath(file_path)
        url = dict(self._url)
        url["database"] = abs_path
        sa_url = convert_to_sqlalchemy_url(url, self.name)
        self._toolbox.db_mngr.create_new_spine_database(sa_url, self._logger, overwrite=True)
        self.update_url(dialect="sqlite", database=abs_path)
        return True

    def load_url_into_selections(self, url):
        """Load given url attribute into shared widget selections.

        Args:
            url (dict): URL dict
        """
        if not self._active or not url:
            return
        self._properties_ui.url_selector_widget.set_url(url)
        self._update_actions_enabled()

    @Slot()
    def _update_url_from_properties(self):
        """Gets new URL from Properties tab."""
        url = self._properties_ui.url_selector_widget.url_dict()
        self.update_url(**url)

    def update_url(self, **kwargs):
        """Pushes a command to update the URL to the undo stack.

        Args:
            **kwargs: URL keys and values
        """
        invalidating_url = self._url_validated
        kwargs = {k: v for k, v in kwargs.items() if v != self._url[k]}
        if not kwargs:
            return False
        self._toolbox.undo_stack.push(UpdateDSURLCommand(self.name, invalidating_url, self._project, **kwargs))
        return True

    def do_update_url(self, **kwargs):
        """Updates URL.

        Args:
            **kwargs: URL keys and values
        """
        was_valid = self._url_validated
        self._url_validated = False
        old_url = convert_to_sqlalchemy_url(self._url, self.name)
        new_dialect = kwargs.get("dialect")
        if new_dialect == "sqlite":
            kwargs.update({"username": "", "password": "", "host": "", "port": "", "schema": ""})
        self._url.update(kwargs)
        new_url = convert_to_sqlalchemy_url(self._url, self.name)
        self.load_url_into_selections(self._url)
        if old_url and new_url:
            old_resource = database_resource(self.name, str(old_url), label=database_label(self.name), filterable=True)
            self._resource_to_replace = ReplaceableResource(old_resource, was_valid)
        else:
            self._resources_to_predecessors_changed()
            self._resources_to_successors_changed()
        self._check_notifications()

    def has_listeners(self):
        """Checks whether the Data Store has listeners or not

        Returns:
             (bool): True if there are listeners for the Data Store, False otherwise
        """
        if self._multi_db_editors_open:
            return bool(
                self._toolbox.db_mngr.db_map_listeners(
                    self._toolbox.db_mngr.get_db_map(self.sql_alchemy_url(), self._logger, codename=self.name)
                )
            )
        return False

    def _update_actions_enabled(self):
        url_exists = convert_to_sqlalchemy_url(self._url, self.name) is not None
        url_valid = url_exists and self._url_validated
        self._open_url_action.setEnabled(url_valid)
        self._open_url_menu.setEnabled(url_valid)
        if not self._active:
            return
        is_sqlite = self._url["dialect"].lower() == "sqlite"
        self._properties_ui.pushButton_ds_open_editor.setEnabled(url_valid)
        self._properties_ui.pushButton_create_new_spine_db.setEnabled(is_sqlite or url_valid)
        self._properties_ui.purge_button.setEnabled(url_valid)
        self._properties_ui.toolButton_copy_url.setEnabled(url_exists)
        self._properties_ui.toolButton_vacuum.setEnabled(is_sqlite and url_valid)

    @Slot(bool)
    def _show_purge_dialog(self, _=False):
        """Shows the Purge dialog."""
        if self._purge_dialog is not None:
            self._purge_dialog.raise_()
            return
        self._purge_dialog = SelectDatabaseItemsDialog(self._purge_settings, "Purge", self._toolbox)
        self._purge_dialog.setWindowTitle(f"Purge items from {self.name}")
        self._purge_dialog.accepted.connect(self._purge)
        self._purge_dialog.destroyed.connect(self._clean_up_purge_dialog)
        self._purge_dialog.show()

    @Slot()
    def _purge(self):
        """Purges the database."""
        self._purge_settings = self._purge_dialog.get_checked_states()
        db_map = self._toolbox.db_mngr.get_db_map(self.sql_alchemy_url(), self._logger, codename=self.name)
        if db_map is None:
            return
        db_map_purge_data = {db_map: {item_type for item_type, checked in self._purge_settings.items() if checked}}
        self._toolbox.db_mngr.purge_items(db_map_purge_data)
        self._toolbox.db_mngr.commit_session("Purge the database.", db_map)
        self._logger.msg_success.emit(f"<b>{self.name}</b>: Database purged.")

    @Slot()
    def _clean_up_purge_dialog(self):
        """Cleans up stuff after Purge dialog has been closed."""
        self._purge_dialog = None

    def actions(self):
        self._multi_db_editors_open = {x.name(): x for x in self._toolbox.db_mngr.get_all_multi_spine_db_editors()}
        if not self._multi_db_editors_open:
            return super().actions()
        self._open_url_menu.clear()
        self._open_url_menu.addAction("New window")
        self._open_url_menu.addSeparator()
        for name in self._multi_db_editors_open:
            self._open_url_menu.addAction(name)
        return [self._open_url_menu.menuAction()]

    @Slot(QAction)
    def _handle_open_url_menu_triggered(self, action):
        """Opens current url."""
        if action.text() == "New window":
            self._open_url_in_new_db_editor()
            return
        db_editor = self._multi_db_editors_open[action.text()]
        self._open_url_in_existing_db_editor(db_editor)

    @Slot(bool)
    def open_url_in_spine_db_editor(self, checked=False):
        """Opens current url in the Spine database editor."""
        self._open_spine_db_editor(reuse_existing=True)

    def _open_url_in_new_db_editor(self, checked=False):
        self._open_spine_db_editor(reuse_existing=False)

    def _open_spine_db_editor(self, reuse_existing):
        """Opens Data Store's URL in Spine Database editor.

        Args:
            reuse_existing (bool): if True and the URL is already open, just raise the window
        """
        if not self._url_validated:
            self._logger.msg_error.emit(
                f"<b>{self.name}</b> is still validating the database URL or the URL is invalid."
            )
            return
        sa_url = self.sql_alchemy_url()
        if sa_url is not None:
            db_url_codenames = {sa_url: self.name}
            self._toolbox.db_mngr.open_db_editor(db_url_codenames, reuse_existing)
        self._check_notifications()

    def _open_url_in_existing_db_editor(self, db_editor):
        if not self._url_validated:
            db_editor.add_message(f"<b>{self.name}</b> is still validating the database URL or the URL is invalid.")
            return
        sa_url = self.sql_alchemy_url()
        if sa_url is not None:
            db_editor.add_new_tab({sa_url: self.name})
            db_editor.raise_()
            db_editor.activateWindow()

    @Slot(bool)
    def copy_url(self, checked=False):
        """Copy db url to clipboard."""
        sa_url = convert_to_sqlalchemy_url(self._url, self.name, self._logger)
        if sa_url is None:
            return
        sa_url.password = None
        QApplication.clipboard().setText(str(sa_url))
        self._logger.msg.emit(f"Database url <b>{sa_url}</b> copied to clipboard")

    @Slot(bool)
    def vacuum(self, checked=False):
        sa_url = convert_to_sqlalchemy_url(self._url, self.name, self._logger)
        freed, unit = vacuum(sa_url)
        self._logger.msg.emit(f"Vacuum finished, {freed} {unit} freed from {sa_url.database}")

    @Slot(bool)
    def create_new_spine_database(self, checked=False):
        """Create new (empty) Spine database."""
        if self._url["dialect"] == "sqlite":
            sqlite_file_creation_successful = self._new_sqlite_file()
            if not sqlite_file_creation_successful:  # User cancelled
                return
        elif self._url["dialect"] == "mysql":
            sa_url = convert_to_sqlalchemy_url(self._url, self.name, self._logger)
            if sa_url:
                self._toolbox.db_mngr.create_new_spine_database(sa_url, self._logger)
        else:
            self._logger.msg_error.emit(f"Unknown data store dialect: {self._url['dialect']}.")
        self._check_notifications()

    def _check_notifications(self):
        """Updates the SqlAlchemy format URL and checks for notifications"""
        self._update_actions_enabled()
        sa_url = convert_to_sqlalchemy_url(self._url, self.name)
        if sa_url is None:
            self.clear_notifications()
            self.add_notification(
                "The URL for this Data Store is not correctly set. Set it in the Data Store Properties panel."
            )
            return
        self._database_validator.validate_url(
            self._url["dialect"], sa_url, self._set_invalid_url_notification, self._accept_url
        )

    @Slot(str, object)
    def _set_invalid_url_notification(self, error_message, url):
        """Sets a single notification that warns about broken URL.

        Args:
            error_message (str): URL failure message
            url (URL): SqlAlchemy URL
        """
        self.clear_notifications()
        self.add_notification(
            f"Couldn't connect to the database <b>{remove_credentials_from_url(str(url))}</b>: {error_message}"
        )
        if self._resource_to_replace is None:
            self._resources_to_predecessors_changed()
            self._resources_to_successors_changed()

    @Slot(object)
    def _accept_url(self, url):
        """Sets URL as validated and updates advertised resources."""
        self._url_validated = True
        self.clear_notifications()
        if self._resource_to_replace is not None and self._resource_to_replace.is_valid:
            old = self._resource_to_replace.resource
            sa_url = convert_to_sqlalchemy_url(self._url, self.name)
            new = database_resource(self.name, str(sa_url), label=database_label(self.name), filterable=True)
            self._resources_to_predecessors_replaced([old], [new])
            self._resources_to_successors_replaced([old], [new])
            self._resource_to_replace = None
        else:
            self._resources_to_predecessors_changed()
            self._resources_to_successors_changed()
        self._update_actions_enabled()

    def is_url_validated(self):
        """Tests whether the URL has been validated.

        Returns:
            bool: True if URL has been validated, False otherwise
        """
        return self._url_validated

    def item_dict(self):
        """Returns a dictionary corresponding to this item."""
        d = super().item_dict()
        d["url"] = dict(self.url())
        # If database key is a file, change the path to relative
        if d["url"]["dialect"] == "sqlite" and d["url"]["database"]:
            d["url"]["database"] = serialize_path(d["url"]["database"], self._project.project_dir)
        return d

    @staticmethod
    def item_dict_local_entries():
        """See base class."""
        return [("url", "username"), ("url", "password")]

    def copy_local_data(self, item_dict):
        """See base class."""
        original_data_dir = item_dict.get("original_data_dir")  # (str) original dir of duplicated ProjectItem
        original_db_url = item_dict.get("original_db_url")  # (dict) original url of the duplicated ProjectItem
        duplicate_files = item_dict.get("duplicate_files")  # (bool) Flag indicating if linked files should be copied
        if original_data_dir is None and original_db_url is None and duplicate_files is None:
            return
        original_project_dir = original_data_dir.split(".spinetoolbox")[0]
        linked_db_dialect = original_db_url.get("dialect")
        if linked_db_dialect != "sqlite":
            return
        original_db = original_db_url.get("database")
        if isinstance(original_db, dict):
            if original_db["relative"]:
                linked_db_path = os.path.join(original_project_dir, original_db["path"])
            else:
                linked_db_path = original_db["path"]
        else:
            linked_db_path = original_db
        if duplicate_files:
            db_copy_destination = os.path.join(self.data_dir, os.path.basename(linked_db_path))
            copyfile(linked_db_path, db_copy_destination)
            self._url["database"] = db_copy_destination
        else:
            self._url["database"] = linked_db_path

    @staticmethod
    def from_dict(name, item_dict, toolbox, project):
        """See base class."""
        description, x, y = ProjectItem.parse_item_dict(item_dict)
        url = item_dict["url"]
        if url and not isinstance(url["database"], str):
            url["database"] = deserialize_path(url["database"], project.project_dir)
        return DataStore(name, description, x, y, toolbox, project, url)

    def rename(self, new_name, rename_data_dir_message):
        """See base class."""
        old_data_dir = os.path.abspath(self.data_dir)  # Old data_dir before rename
        if not super().rename(new_name, rename_data_dir_message):
            return False
        # If dialect is sqlite and db line edit refers to a file in the old data_dir, db line edit needs updating
        if self._url["dialect"] == "sqlite":
            db_dir, db_filename = os.path.split(os.path.abspath(self._url["database"].strip()))
            if db_dir == old_data_dir:
                database = os.path.join(self.data_dir, db_filename)  # NOTE: data_dir has been updated at this point
                # Check that the db was moved successfully to the new data_dir
                if os.path.exists(database):
                    self._url.update(database=database)
                    self.load_url_into_selections(self._url)
        return True

    def notify_destination(self, source_item):
        """See base class."""
        if source_item.item_type() == "Importer":
            self._logger.msg.emit(
                f"Link established. Mapped data generated by <b>{source_item.name}</b> will be "
                f"imported in <b>{self.name}</b> when executing."
            )
        elif source_item.item_type() == "Tool":
            self._logger.msg.emit("Link established")
        elif source_item.item_type() == "Data Transformer":
            self._logger.msg.emit(
                "Link established. "
                f"Data transformed by <b>{source_item.name}</b> will be merged into <b>{self.name}</b> upon execution."
            )
        elif source_item.item_type() == "Merger":
            src_ds_names = ", ".join(x.name for x in source_item.predecessor_data_stores())
            self._logger.msg.emit(
                "Link established. "
                f"Data from <b>{src_ds_names}</b> will be merged into <b>{self.name}</b> upon execution."
            )
        else:
            super().notify_destination(source_item)

    def resources_for_direct_successors(self):
        """See base class."""
        if not self._url_validated:
            return []
        sa_url = convert_to_sqlalchemy_url(self._url, self.name)
        resources = scan_for_resources(self, sa_url)
        return resources

    def resources_for_direct_predecessors(self):
        """See base class."""
        return self.resources_for_direct_successors()

    def tear_down(self):
        """See base class"""
        self._database_validator.wait_for_finish()
        super().tear_down()
