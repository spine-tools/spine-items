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
Module for data store class.

:authors: P. Savolainen (VTT), M. Marin (KTH)
:date:   18.12.2017
"""

import os
from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QAction, QFileDialog, QApplication
from spinetoolbox.project_item.project_item import ProjectItem
from spinetoolbox.helpers import create_dir
from spine_engine import ExecutionDirection
from spine_engine.utils.serialization import serialize_path, deserialize_path
from .commands import UpdateDSURLCommand
from ..commands import UpdateCancelOnErrorCommand
from .executable_item import ExecutableItem
from .item_info import ItemInfo
from .utils import convert_to_sqlalchemy_url, make_label


class DataStore(ProjectItem):
    def __init__(self, name, description, x, y, toolbox, project, logger, url, cancel_on_error=False):
        """Data Store class.

        Args:
            name (str): Object name
            description (str): Object description
            x (float): Initial X coordinate of item icon
            y (float): Initial Y coordinate of item icon
            toolbox (ToolboxUI): QMainWindow instance
            project (SpineToolboxProject): the project this item belongs to
            logger (LoggerInterface): a logger instance
            url (str or dict, optional): SQLAlchemy url
            cancel_on_error (bool): if True, changes will be reverted on errors
        """
        super().__init__(name, description, x, y, project, logger)
        self._toolbox = toolbox
        self.logs_dir = os.path.join(self.data_dir, "logs")
        try:
            create_dir(self.logs_dir)
        except OSError:
            self._logger.msg_error.emit(f"[OSError] Creating directory {self.logs_dir} failed. Check permissions.")
        self.cancel_on_error = cancel_on_error
        self._actions.append(QAction("Open database editor..."))
        self._actions[-1].triggered.connect(self.open_ds_form)
        if url is None:
            url = dict()
        self._url = self.parse_url(url)
        self._additional_resource_metadata = None

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

    def parse_url(self, url):
        """Return a complete url dictionary from the given dict or string"""
        base_url = dict(dialect="", username="", password="", host="", port="", database="")
        if isinstance(url, dict):
            if "database" in url and url["database"] is not None:
                if url["database"].lower().endswith(".sqlite"):
                    # Convert relative database path back to absolute
                    abs_path = os.path.abspath(os.path.join(self._project.project_dir, url["database"]))
                    url["database"] = abs_path
            for key, value in url.items():
                if value is not None:
                    base_url[key] = value
        return base_url

    def make_signal_handler_dict(self):
        """Returns a dictionary of all shared signals and their handlers.
        This is to enable simpler connecting and disconnecting."""
        s = super().make_signal_handler_dict()
        s[self._properties_ui.toolButton_ds_open_dir.clicked] = lambda checked=False: self.open_directory()
        s[self._properties_ui.pushButton_ds_open_editor.clicked] = self.open_ds_form
        s[self._properties_ui.toolButton_open_sqlite_file.clicked] = self.open_sqlite_file
        s[self._properties_ui.pushButton_create_new_spine_db.clicked] = self.create_new_spine_database
        s[self._properties_ui.toolButton_copy_url.clicked] = self.copy_url
        s[self._properties_ui.comboBox_dialect.activated[str]] = self.refresh_dialect
        s[self._properties_ui.lineEdit_database.file_dropped] = self.set_path_to_sqlite_file
        s[self._properties_ui.lineEdit_username.editingFinished] = self.refresh_username
        s[self._properties_ui.lineEdit_password.editingFinished] = self.refresh_password
        s[self._properties_ui.lineEdit_host.editingFinished] = self.refresh_host
        s[self._properties_ui.lineEdit_port.editingFinished] = self.refresh_port
        s[self._properties_ui.lineEdit_database.editingFinished] = self.refresh_database
        s[self._properties_ui.cancel_on_error_checkBox.stateChanged] = self._handle_cancel_on_error_changed
        return s

    def restore_selections(self):
        """Load url into selections."""
        self._properties_ui.label_ds_name.setText(self.name)
        self._properties_ui.cancel_on_error_checkBox.setCheckState(Qt.Checked if self.cancel_on_error else Qt.Unchecked)
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

    @Slot(str)
    def set_path_to_sqlite_file(self, file_path):
        """Set path to SQLite file."""
        abs_path = os.path.abspath(file_path)
        self.update_url(database=abs_path)

    @Slot(bool)
    def open_sqlite_file(self, checked=False):
        """Open file browser where user can select the path to an SQLite
        file that they want to use."""
        # noinspection PyCallByClass, PyTypeChecker, PyArgumentList
        answer = QFileDialog.getOpenFileName(self._toolbox, "Select SQLite file", self.data_dir)
        file_path = answer[0]
        if not file_path:  # Cancel button clicked
            return
        # Update UI
        self.set_path_to_sqlite_file(file_path)

    def load_url_into_selections(self, url):
        """Load given url attribute into shared widget selections.
        """
        if not self._active:
            return
        if not url:
            return
        dialect = url.get("dialect")
        host = url.get("host")
        port = url.get("port")
        database = url.get("database")
        username = url.get("username")
        password = url.get("password")
        if dialect is not None:
            self.enable_dialect(dialect)
            if dialect == "":
                self._properties_ui.comboBox_dialect.setCurrentIndex(-1)
            else:
                self._properties_ui.comboBox_dialect.setCurrentText(dialect)
        if host is not None:
            self._properties_ui.lineEdit_host.setText(host)
        if port is not None:
            self._properties_ui.lineEdit_port.setText(str(port))
        if database is not None:
            if database:
                database = os.path.abspath(database)
            self._properties_ui.lineEdit_database.setText(database)
        if username is not None:
            self._properties_ui.lineEdit_username.setText(username)
        if password is not None:
            self._properties_ui.lineEdit_password.setText(password)

    def update_url(self, **kwargs):
        """Set url key to value."""
        kwargs = {k: v for k, v in kwargs.items() if v != self._url[k]}
        if not kwargs:
            return False
        self._toolbox.undo_stack.push(UpdateDSURLCommand(self, **kwargs))
        return True

    def do_update_url(self, **kwargs):
        self._url.update(kwargs)
        self.item_changed.emit()
        self.load_url_into_selections(kwargs)

    @Slot()
    def refresh_host(self):
        """Refresh host from selections."""
        host = self._properties_ui.lineEdit_host.text()
        self.update_url(host=host)

    @Slot()
    def refresh_port(self):
        """Refresh port from selections."""
        port = self._properties_ui.lineEdit_port.text()
        self.update_url(port=port)

    @Slot()
    def refresh_database(self):
        """Refresh database from selections."""
        database = self._properties_ui.lineEdit_database.text()
        self.update_url(database=database)

    @Slot()
    def refresh_username(self):
        """Refresh username from selections."""
        username = self._properties_ui.lineEdit_username.text()
        self.update_url(username=username)

    @Slot()
    def refresh_password(self):
        """Refresh password from selections."""
        password = self._properties_ui.lineEdit_password.text()
        self.update_url(password=password)

    @Slot(str)
    def refresh_dialect(self, dialect):
        self.update_url(dialect=dialect)

    @Slot(int)
    def _handle_cancel_on_error_changed(self, _state):
        cancel_on_error = self._properties_ui.cancel_on_error_checkBox.isChecked()
        if self.cancel_on_error == cancel_on_error:
            return
        self._toolbox.undo_stack.push(UpdateCancelOnErrorCommand(self, cancel_on_error))

    def set_cancel_on_error(self, cancel_on_error):
        self.cancel_on_error = cancel_on_error
        if not self._active:
            return
        check_state = Qt.Checked if self.cancel_on_error else Qt.Unchecked
        self._properties_ui.cancel_on_error_checkBox.blockSignals(True)
        self._properties_ui.cancel_on_error_checkBox.setCheckState(check_state)
        self._properties_ui.cancel_on_error_checkBox.blockSignals(False)

    def enable_dialect(self, dialect):
        """Enable the given dialect in the item controls."""
        if dialect == "":
            self.enable_no_dialect()
        elif dialect == "sqlite":
            self.enable_sqlite()
        elif dialect == "mssql":
            import pyodbc  # pylint: disable=import-outside-toplevel

            dsns = pyodbc.dataSources()
            # Collect dsns which use the msodbcsql driver
            mssql_dsns = list()
            for key, value in dsns.items():
                if "msodbcsql" in value.lower():
                    mssql_dsns.append(key)
            if mssql_dsns:
                self._properties_ui.comboBox_dsn.clear()
                self._properties_ui.comboBox_dsn.addItems(mssql_dsns)
                self._properties_ui.comboBox_dsn.setCurrentIndex(-1)
                self.enable_mssql()
            else:
                msg = "Please create a SQL Server ODBC Data Source first."
                self._logger.msg_warning.emit(msg)
        else:
            self.enable_common()

    def enable_no_dialect(self):
        """Adjust widget enabled status to default when no dialect is selected."""
        self._properties_ui.comboBox_dialect.setEnabled(True)
        self._properties_ui.comboBox_dsn.setEnabled(False)
        self._properties_ui.toolButton_open_sqlite_file.setEnabled(False)
        self._properties_ui.lineEdit_host.setEnabled(False)
        self._properties_ui.lineEdit_port.setEnabled(False)
        self._properties_ui.lineEdit_database.setEnabled(False)
        self._properties_ui.lineEdit_username.setEnabled(False)
        self._properties_ui.lineEdit_password.setEnabled(False)

    def enable_mssql(self):
        """Adjust controls to mssql connection specification."""
        self._properties_ui.comboBox_dsn.setEnabled(True)
        self._properties_ui.toolButton_open_sqlite_file.setEnabled(False)
        self._properties_ui.lineEdit_host.setEnabled(False)
        self._properties_ui.lineEdit_port.setEnabled(False)
        self._properties_ui.lineEdit_database.setEnabled(False)
        self._properties_ui.lineEdit_username.setEnabled(True)
        self._properties_ui.lineEdit_password.setEnabled(True)
        self._properties_ui.lineEdit_host.clear()
        self._properties_ui.lineEdit_port.clear()
        self._properties_ui.lineEdit_database.clear()

    def enable_sqlite(self):
        """Adjust controls to sqlite connection specification."""
        self._properties_ui.comboBox_dsn.setEnabled(False)
        self._properties_ui.comboBox_dsn.setCurrentIndex(-1)
        self._properties_ui.toolButton_open_sqlite_file.setEnabled(True)
        self._properties_ui.lineEdit_host.setEnabled(False)
        self._properties_ui.lineEdit_port.setEnabled(False)
        self._properties_ui.lineEdit_database.setEnabled(True)
        self._properties_ui.lineEdit_username.setEnabled(False)
        self._properties_ui.lineEdit_password.setEnabled(False)
        self._properties_ui.lineEdit_host.clear()
        self._properties_ui.lineEdit_port.clear()
        self._properties_ui.lineEdit_username.clear()
        self._properties_ui.lineEdit_password.clear()

    def enable_common(self):
        """Adjust controls to 'common' connection specification."""
        self._properties_ui.comboBox_dsn.setEnabled(False)
        self._properties_ui.comboBox_dsn.setCurrentIndex(-1)
        self._properties_ui.toolButton_open_sqlite_file.setEnabled(False)
        self._properties_ui.lineEdit_host.setEnabled(True)
        self._properties_ui.lineEdit_port.setEnabled(True)
        self._properties_ui.lineEdit_database.setEnabled(True)
        self._properties_ui.lineEdit_username.setEnabled(True)
        self._properties_ui.lineEdit_password.setEnabled(True)

    @Slot(bool)
    def open_ds_form(self, checked=False):
        """Opens current url in the Spine database editor."""
        if not self._url["database"]:
            self._logger.msg_error.emit(f"<b>{self.name}</b> is not connected to a database.")
            return
        sa_url = convert_to_sqlalchemy_url(self._url, self.name, self._logger)
        self._project.db_mngr.show_spine_db_editor({sa_url: self.name}, self._logger)

    def data_files(self):
        """Return a list of files that are in this items data directory."""
        if not os.path.isdir(self.data_dir):
            return None
        return os.listdir(self.data_dir)

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
    def create_new_spine_database(self, checked=False):
        """Create new (empty) Spine database."""
        # Try to make an url from the current status
        sa_url = convert_to_sqlalchemy_url(self._url, self.name, None)
        if not sa_url:
            self._logger.msg_warning.emit(
                f"Unable to generate URL from <b>{self.name}</b> selections. Defaults will be used..."
            )
            dialect = "sqlite"
            database = os.path.abspath(os.path.join(self.data_dir, self.name + ".sqlite"))
            self.update_url(dialect=dialect, database=database)
            sa_url = convert_to_sqlalchemy_url(self._url, self.name, None)
        self._project.db_mngr.create_new_spine_database(sa_url)

    def update_name_label(self):
        """Update Data Store tab name label. Used only when renaming project items."""
        self._properties_ui.label_ds_name.setText(self.name)

    @Slot(object, object)
    def handle_execution_successful(self, execution_direction, engine_state):
        """Notifies Toolbox of successful database import."""
        if execution_direction != ExecutionDirection.FORWARD:
            return
        url = self.sql_alchemy_url()
        database_map = self._project.db_mngr.get_db_map(url, self._logger)
        if database_map is not None:
            cookie = self
            self._project.db_mngr.session_committed.emit({database_map}, cookie)

    def _do_handle_dag_changed(self, resources, _):
        """See base class."""
        sa_url = convert_to_sqlalchemy_url(self._url, self.name, logger=None)
        if sa_url is None:
            self.add_notification(
                "The URL for this Data Store is not correctly set. Set it in the Data Store Properties panel."
            )

    def item_dict(self):
        """Returns a dictionary corresponding to this item."""
        d = super().item_dict()
        d["url"] = dict(self.url())
        # If database key is a file, change the path to relative
        if d["url"]["dialect"] == "sqlite" and d["url"]["database"]:
            d["url"]["database"] = serialize_path(d["url"]["database"], self._project.project_dir)
        d["cancel_on_error"] = self._properties_ui.cancel_on_error_checkBox.isChecked()
        return d

    @staticmethod
    def from_dict(name, item_dict, toolbox, project, logger):
        """See base class."""
        description, x, y = ProjectItem.parse_item_dict(item_dict)
        url = item_dict["url"]
        if url and not isinstance(url["database"], str):
            url["database"] = deserialize_path(url["database"], project.project_dir)
        cancel_on_error = item_dict.get("cancel_on_error", False)
        return DataStore(name, description, x, y, toolbox, project, logger, url, cancel_on_error)

    @staticmethod
    def upgrade_from_no_version_to_version_1(item_name, old_item_dict, old_project_dir):
        """See base class."""
        new_data_store = dict(old_item_dict)
        if "reference" in new_data_store:
            url_path = new_data_store["reference"]
            url = {"dialect": "sqlite", "username": None, "host": None, "port": None}
        else:
            url = new_data_store["url"]
            url_path = url["database"]
        if not url_path:
            url["database"] = None
        else:
            serialized_url_path = serialize_path(url_path, old_project_dir)
            if serialized_url_path["relative"]:
                serialized_url_path["path"] = os.path.join(".spinetoolbox", "items", serialized_url_path["path"])
            url["database"] = serialized_url_path
        new_data_store["url"] = url
        return new_data_store

    def rename(self, new_name):
        """Rename this item.

        Args:
            new_name (str): New name
        Returns:
            bool: True if renaming succeeded, False otherwise
        """
        old_data_dir = os.path.abspath(self.data_dir)  # Old data_dir before rename
        old_name = self.name
        if not super().rename(new_name):
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
        self._additional_resource_metadata = {"updated_from": make_label(old_name)}
        self.item_changed.emit()
        return True

    def notify_destination(self, source_item):
        """See base class."""
        if source_item.item_type() == "Importer":
            self._logger.msg.emit(
                f"Link established. Mapped data generated by <b>{source_item.name}</b> will be "
                f"imported in <b>{self.name}</b> when executing."
            )
        elif source_item.item_type() == "Data Store":
            self._logger.msg.emit(
                "Link established. "
                f"Data from <b>{source_item.name}</b> will be merged into <b>{self.name}'s upon execution</b>."
            )
        elif source_item.item_type() in ["Data Connection", "Tool", "Gimlet"]:
            # Does this type of link do anything?
            self._logger.msg.emit("Link established")
        elif source_item.item_type() == "Data Transformer":
            self._logger.msg.emit(
                "Link established. "
                f"Data transformed by <b>{source_item.name}</b> will be merged into <b>{self.name}</b> upon execution."
            )
        else:
            super().notify_destination(source_item)

    def resources_for_direct_successors(self):
        """See base class."""
        resources = self.execution_item()._output_resources_forward()
        if self._additional_resource_metadata:
            resources = [r.clone(additional_metadata=self._additional_resource_metadata) for r in resources]
        if not resources:
            self.add_notification(
                "The URL for this Data Store is not correctly set. Set it in the Data Store Properties panel."
            )
        return resources

    def resources_for_direct_predecessors(self):
        """See base class."""
        return self.resources_for_direct_successors()
