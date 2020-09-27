######################################################################################################################
# Copyright (C) 2017-2020 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
General helper functions and classes.

:authors: P. Savolainen (VTT)
:date:   10.1.2018
"""
import os
import logging
import shutil
import sys
from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QCursor, QDesktopServices
from PySide2.QtCore import Qt, QUrl


def shorten(name):
    """Returns the 'short name' version of given name."""
    return name.lower().replace(" ", "_")


def open_url(url):
    return QDesktopServices.openUrl(QUrl(url, QUrl.TolerantMode))


def create_dir(base_path, folder="", verbosity=False):
    """Create (input/output) directories recursively.

    Args:
        base_path (str): Absolute path to wanted dir
        folder (str): (Optional) Folder name. Usually short name of item.
        verbosity (bool): True prints a message that tells if the directory already existed or if it was created.

    Returns:
        True if directory already exists or if it was created successfully.

    Raises:
        OSError if operation failed.
    """
    directory = os.path.join(base_path, folder)
    if os.path.exists(directory) and verbosity:
        logging.debug("Directory found: %s", directory)
    else:
        os.makedirs(directory, exist_ok=True)
        if verbosity:
            logging.debug("Directory created: %s", directory)
    return True


def rename_dir(old_dir, new_dir, logger):
    """Rename directory. Note: This is not used in renaming projects due to unreliability.
    Looks like it works fine in renaming project items though.

    Args:
        old_dir (str): Absolute path to directory that will be renamed
        new_dir (str): Absolute path to new directory
        logger (LoggerInterface): A logger instance
    """
    if os.path.exists(new_dir):
        # If the target is a directory, then there will not be a name clash in shutil.move()
        # as the old_dir will be moved inside new_dir which is not a rename operation.
        # We guard against that here.
        msg = "Directory<br/><b>{0}</b><br/>already exists".format(new_dir)
        logger.information_box.emit("Renaming directory failed", msg)
        return False
    try:
        shutil.move(old_dir, new_dir)
    except FileExistsError:
        msg = "Directory<br/><b>{0}</b><br/>already exists".format(new_dir)
        logger.information_box.emit("Renaming directory failed", msg)
        return False
    except PermissionError as pe_e:
        logging.error(pe_e)
        msg = (
            "Access to directory <br/><b>{0}</b><br/>denied."
            "<br/><br/>Possible reasons:"
            "<br/>1. You don't have a permission to edit the directory"
            "<br/>2. Windows Explorer is open in the directory"
            "<br/><br/>Check these and try again.".format(old_dir)
        )
        logger.information_box.emit("Renaming directory failed (Permission Error)", msg)
        return False
    except OSError as os_e:
        logging.error(os_e)
        msg = (
            "Renaming directory "
            "<br/><b>{0}</b> "
            "<br/>to "
            "<br/><b>{1}</b> "
            "<br/>failed."
            "<br/><br/>Possibly reasons:"
            "<br/>1. Windows Explorer is open in the directory."
            "<br/>2. A file in the directory is open in another program. "
            "<br/><br/>Check these and try again.".format(old_dir, new_dir)
        )
        logger.information_box.emit("Renaming directory failed (OS Error)", msg)
        return False
    return True


def busy_effect(func):
    """ Decorator to change the mouse cursor to 'busy' while a function is processed.

    Args:
        func: Decorated function.
    """

    def new_function(*args, **kwargs):
        # noinspection PyTypeChecker, PyArgumentList, PyCallByClass
        QApplication.setOverrideCursor(QCursor(Qt.BusyCursor))
        try:
            return func(*args, **kwargs)
        finally:
            # noinspection PyArgumentList
            QApplication.restoreOverrideCursor()

    return new_function


def deserialize_path(serialized, project_dir):
    """
    Returns a deserialized path or URL.

    Args:
        serialized (dict): a serialized path or URL
        project_dir (str): path to the project directory

    Returns:
        str: Path or URL as string
    """
    if not isinstance(serialized, dict):
        return serialized
    try:
        path_type = serialized["type"]
        if path_type == "path":
            path = serialized["path"]
            return os.path.normpath(
                os.path.join(project_dir, path) if serialized["relative"] else path
            )
        if path_type == "file_url":
            path = serialized["path"]
            if serialized["relative"]:
                path = os.path.join(project_dir, path)
            path = os.path.normpath(path)
            return serialized["scheme"] + ":///" + path
        if path_type == "url":
            return serialized["path"]
    except KeyError as error:
        raise RuntimeError("Key missing from serialized path: {}".format(error))
    raise RuntimeError("Cannot deserialize: unknown path type '{}'.".format(path_type))


def path_in_dir(path, directory):
    """Returns True if the given path is in the given directory."""
    try:
        retval = os.path.samefile(os.path.commonpath((path, directory)), directory)
    except ValueError:
        return False
    return retval


def serialize_path(path, project_dir):
    """
    Returns a dict representation of the given path.

    If path is in project_dir, converts the path to relative.

    Args:
        path (str): path to serialize
        project_dir (str): path to the project directory

    Returns:
        dict: Dictionary representing the given path
    """
    is_relative = path_in_dir(path, project_dir)
    serialized = {
        "type": "path",
        "relative": is_relative,
        "path": os.path.relpath(path, project_dir).replace(os.sep, "/")
        if is_relative
        else path.replace(os.sep, "/"),
    }
    return serialized


def serialize_url(url, project_dir):
    """
    Return a dict representation of the given URL.

    If the URL is a file that is in project dir, the URL is converted to a relative path.

    Args:
        url (str): a URL to serialize
        project_dir (str): path to the project directory

    Returns:
        dict: Dictionary representing the URL
    """
    parsed = urllib.parse.urlparse(url)
    path = urllib.parse.unquote(parsed.path)
    if sys.platform == "win32":
        path = path[1:]  # Remove extra '/' from the beginning
    if os.path.isfile(path):
        is_relative = path_in_dir(path, project_dir)
        serialized = {
            "type": "file_url",
            "relative": is_relative,
            "path": os.path.relpath(path, project_dir).replace(os.sep, "/")
            if is_relative
            else path.replace(os.sep, "/"),
            "scheme": parsed.scheme,
        }
    else:
        serialized = {"type": "url", "relative": False, "path": url}
    return serialized


def python_interpreter(app_settings):
    """Returns the full path to Python interpreter depending on
    user's settings and whether the app is frozen or not.

    Args:
        app_settings (QSettings): Application preferences

    Returns:
        str: Path to python executable
    """
    python_path = app_settings.value("appSettings/pythonPath", defaultValue="")
    if python_path != "":
        path = python_path
    else:
        if not getattr(sys, "frozen", False):
            path = (
                sys.executable
            )  # If not frozen, return the one that is currently used.
        else:
            path = PYTHON_EXECUTABLE  # If frozen, return the one in path
    return path
