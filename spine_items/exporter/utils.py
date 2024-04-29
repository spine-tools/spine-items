######################################################################################################################
# Copyright (C) 2017-2023 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""Contains utilities for Exporter."""
from dataclasses import dataclass
from spine_engine.project_item.project_item_resource import url_resource
from spine_items.utils import convert_to_sqlalchemy_url

EXPORTER_EXECUTION_MANIFEST_FILE_PREFIX = ".export-manifest"
"""Prefix for the temporary files that exporter's executable uses to communicate output paths."""


@dataclass
class Database:
    """Legacy class for Database specific export settings."""

    url: str = ""
    """Database URL."""
    output_file_name: str = ""
    """Output file name; relative to item's data dir."""

    @staticmethod
    def from_dict(database_dict):
        """
        Deserializes :class:`Database` from a dictionary.

        Args:
            database_dict (dict): serialized :class:`Database`

        Returns:
            Database: deserialized instance
        """
        db = Database()
        db.output_file_name = database_dict["output_file_name"]
        return db


def output_database_resources(item_name, output_channels):
    """Gathers output database resources from output channels that have an out URL set.

    Args
        item_name (str): exporter's name
        output_channels (Iterable of OutputChannel): output channels

    Returns:
        list of ProjectItemResource: database resources
    """
    resources = []
    for channel in output_channels:
        if channel.out_url is None:
            continue
        url = str(convert_to_sqlalchemy_url(channel.out_url))
        resources.append(url_resource(item_name, url, channel.out_label))
    return resources
