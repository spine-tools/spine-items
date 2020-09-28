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
Helper functions and classes.

:authors: M. Marin (KTH)
:date:   12.5.2020
"""

import os
import sys
import urllib
import logging
import datetime
import time
import re
import shutil
from collections import ChainMap
from PySide2.QtCore import Qt, QUrl
from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QCursor, QDesktopServices
from .config import PYTHON_EXECUTABLE

CMDLINE_TAG_EDGE = "@@"


class CmdlineTag:
    URL = CMDLINE_TAG_EDGE + "url:<data-store-name>" + CMDLINE_TAG_EDGE
    URL_INPUTS = CMDLINE_TAG_EDGE + "url_inputs" + CMDLINE_TAG_EDGE
    URL_OUTPUTS = CMDLINE_TAG_EDGE + "url_outputs" + CMDLINE_TAG_EDGE
    OPTIONAL_INPUTS = CMDLINE_TAG_EDGE + "optional_inputs" + CMDLINE_TAG_EDGE


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


def open_url(url):
    return QDesktopServices.openUrl(QUrl(url, QUrl.TolerantMode))


def create_log_file_timestamp():
    """Creates a new timestamp string that is used as Combiner and Importer error log file.

    Returns:
        Timestamp string or empty string if failed.
    """
    try:
        # Create timestamp
        stamp = datetime.datetime.fromtimestamp(time.time())
    except OverflowError:
        return ""
    extension = stamp.strftime("%Y%m%dT%H%M%S")
    return extension


def serialize_checked_states(files, project_path):
    """Serializes file paths and adds a boolean value
    for each, which indicates whether the path is
    selected or not. Used in saving checked file states to
    project.json.

    Args:
        files (list): List of absolute file paths
        project_path (str): Absolute project directory path

    Returns:
        list: List of serialized paths with a boolean value
    """
    return [[serialize_path(item.label, project_path), item.selected] for item in files]


def deserialize_checked_states(serialized, project_path):
    """Reverse operation for serialize_checked_states above.
    Returns absolute file paths with their check state as boolean.

    Args:
        serialized (list): List of serialized paths with a boolean value
        project_path (str): Absolute project directory path

    Returns:
        dict: Dictionary with paths as keys and boolean check states as value
    """
    if not serialized:
        return dict()
    deserialized = dict()
    for serialized_label, checked in serialized:
        label = deserialize_path(serialized_label, project_path)
        deserialized[label] = checked
    return deserialized


def split_cmdline_args(arg_string):
    """
    Splits a string of command line into a list of tokens.

    Things in single ('') and double ("") quotes are kept as single tokens
    while the quotes themselves are stripped away.
    Thus, `--file="a long quoted 'file' name.txt` becomes ["--file=a long quoted 'file' name.txt"]

    Args:
        arg_string (str): command line arguments as a string

    Returns:
        list: a list of tokens
    """
    # The expandable tags may include whitespaces, particularly in Data Store names.
    # We replace the tags temporarily by '@_@_@' to simplify splitting
    # and put them back to the args list after the string has been split.
    tag_safe = list()
    tag_fingerprint = re.compile(CMDLINE_TAG_EDGE + "url:.+?" + CMDLINE_TAG_EDGE)
    match = tag_fingerprint.search(arg_string)
    while match:
        tag_safe.append(match.group())
        arg_string = arg_string[: match.start()] + "@_@_@" + arg_string[match.end() :]
        match = tag_fingerprint.search(arg_string)
    tokens = list()
    current_word = ""
    quoted_context = False
    for character in arg_string:
        if character in ("'", '"') and not quoted_context:
            quoted_context = character
        elif character == quoted_context:
            quoted_context = False
        elif not character.isspace() or quoted_context:
            current_word = current_word + character
        else:
            tokens.append(current_word)
            current_word = ""
    if current_word:
        tokens.append(current_word)
    for index, token in enumerate(tokens):
        preface, tag_token, prologue = token.partition("@_@_@")
        if tag_token:
            tokens[index] = preface + tag_safe.pop(0) + prologue
    return tokens


def expand_tags(args, optional_input_files, input_urls, output_urls):
    """"
    Expands first @@ tags found in given list of command line arguments.

    Args:
        args (list): a list of command line arguments
        optional_input_files (list): a list of Tool's optional input file names
        input_urls (dict): a mapping from URL provider (input Data Store name) to URL string
        output_urls (dict): a mapping from URL provider (output Data Store name) to URL string

    Returns:
        tuple: a boolean flag, if True, indicates that tags were expanded and a list of
            expanded command line arguments
    """

    def expand_list(arg, tag, things, expanded_args):
        preface, tag_found, postscript = arg.partition(tag)
        if tag_found:
            if things:
                first_input_arg = preface + things[0]
                expanded_args.append(first_input_arg)
                expanded_args += things[1:]
                expanded_args[-1] = expanded_args[-1] + postscript
            else:
                expanded_args.append(preface + postscript)
            return True
        return False

    expanded_args = list()
    named_data_store_tag_fingerprint = re.compile(
        CMDLINE_TAG_EDGE + "url:.+" + CMDLINE_TAG_EDGE
    )
    all_urls = ChainMap(input_urls, output_urls)
    input_url_list = list(input_urls.values())
    output_url_list = list(output_urls.values())
    did_expand = False
    for arg in args:
        if expand_list(
            arg, CmdlineTag.OPTIONAL_INPUTS, optional_input_files, expanded_args
        ):
            did_expand = True
            continue
        if expand_list(arg, CmdlineTag.URL_INPUTS, input_url_list, expanded_args):
            did_expand = True
            continue
        if expand_list(arg, CmdlineTag.URL_OUTPUTS, output_url_list, expanded_args):
            did_expand = True
            continue
        match = named_data_store_tag_fingerprint.search(arg)
        if match:
            preface = arg[: match.start()]
            tag = match.group()
            postscript = arg[match.end() :]
            data_store_name = tag[6:-2]
            try:
                url = all_urls[data_store_name]
            except KeyError:
                raise RuntimeError(
                    f"Cannot replace tag '{tag}' since '{data_store_name}' was not found."
                )
            expanded_args.append(preface + url + postscript)
            did_expand = True
            continue
        expanded_args.append(arg)
    return did_expand, expanded_args


def shorten(name):
    """Returns the 'short name' version of given name."""
    return name.lower().replace(" ", "_")


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
