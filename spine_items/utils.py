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
Contains utilities for all items.

:authors: A. Soininen (VTT)
:date:   1.4.2020
"""

from contextlib import contextmanager
from spinedb_api.spine_db_server import start_spine_db_server, shutdown_spine_db_server
from spine_engine.project_item.project_item_resource import extract_packs


def labelled_resource_filepaths(resources):
    """Returns a dict mapping resource labels to file paths available in given resources.
    The label acts as an identifier for a 'transient_file'.
    """
    return {resource.label: resource.path for resource in resources if resource.hasfilepath}


class CmdLineArg:
    """Command line argument for items that execute shell commands."""

    def __init__(self, arg):
        """
        Args:
            arg (str): command line argument
        """
        self.arg = arg

    def __eq__(self, other):
        if not isinstance(other, CmdLineArg):
            return NotImplemented
        return self.arg == other.arg

    def __str__(self):
        return self.arg

    def to_dict(self):
        """Serializes argument to JSON compatible dict.

        Returns:
            dict: serialized command line argument
        """
        return {"type": "literal", "arg": self.arg}


class LabelArg(CmdLineArg):
    """Command line argument that gets replaced by a project item's resource URL/file path."""

    def to_dict(self):
        """See base class."""
        return {"type": "resource", "arg": self.arg}


def cmd_line_arg_from_dict(arg_dict):
    """Deserializes argument from dictionary.

    Args:
        arg_dict (dict): serialized command line argument

    Returns:
        CmdLineArg: deserialized command line argument
    """
    type_ = arg_dict["type"]
    construct = {"literal": CmdLineArg, "resource": LabelArg}[type_]
    return construct(arg_dict["arg"])


@contextmanager
def labelled_resource_args(resources, use_db_server=False):
    result = {}
    server_urls = []
    single_resources, pack_resources = extract_packs(resources)
    for resource in single_resources:
        if resource.type_ != "database":
            result[resource.label] = resource.path if resource.hasfilepath else ""
            continue
        if use_db_server:
            server_url = result[resource.label] = start_spine_db_server(resource.url)
            server_urls.append(server_url)
            continue
        result[resource.label] = resource.url
    for label, resources in pack_resources.items():
        result[label] = " ".join(r.path for r in resources if r.hasfilepath)
    try:
        yield result
    finally:
        for server_url in server_urls:
            shutdown_spine_db_server(server_url)


def expand_cmd_line_args(args, label_to_arg, logger):
    """Expands command line arguments by replacing resource labels by URLs/paths.

    Args:
        args (list of CmdLineArg): command line arguments
        label_to_arg (dict): a mapping from resource label to cmd line argument
        logger (LoggerInterface): a logger

    Returns:
        list of str: command line arguments as strings
    """
    expanded_args = list()
    for arg in args:
        if not isinstance(arg, LabelArg):
            expanded_args.append(str(arg))
            continue
        expanded = label_to_arg.get(str(arg))
        if expanded is None:
            logger.msg_warning.emit(f"Label '{arg}' used as command line argument not found in resources.")
            continue
        if expanded:
            expanded_args.append(expanded)
    return expanded_args


def database_label(provider_name):
    """Creates a standardized label for database resources.

    Args:
        provider_name (str): resource provider's name

    Returns:
        str: resource label
    """
    return "db_url@" + provider_name
