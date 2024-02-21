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

"""Contains :class:`OutputChannel` class."""
from contextlib import suppress
from dataclasses import dataclass, InitVar
from spine_engine.utils.serialization import deserialize_path, serialize_path


@dataclass
class OutputChannel:
    """Input resource specific export settings."""

    in_label: str
    """Label of input resource."""
    item_name: InitVar[str]
    """Exporter's name."""
    out_label: str = None
    """Label of output resource. Output file name in case of single file export."""
    out_url: dict = None
    """Optional URL for fixed output database."""

    def __post_init__(self, item_name):
        if self.out_label is None:
            label, separator, in_name = self.in_label.partition("@")
            if separator:
                self.out_label = f"{in_name}_exported@{item_name}"
            else:
                self.out_label = f"{self.in_label}_exported@{item_name}"

    def to_dict(self, project_dir):
        """
        Serializes :class:`OutputChannel` into a dictionary.

        Args:
            project_dir (str): project directory

        Returns:
            dict: serialized :class:`OutputChannel`
        """
        channel_dict = {"in_label": self.in_label, "out_label": self.out_label}
        if self.out_url is not None:
            url = self.out_url.copy()
            with suppress(KeyError):
                del url["username"]
            with suppress(KeyError):
                del url["password"]
            if url["dialect"] == "sqlite" and url["database"]:
                url["database"] = serialize_path(url["database"], project_dir)
            channel_dict["out_url"] = url
        return channel_dict

    @staticmethod
    def from_dict(channel_dict, item_name, project_dir):
        """
        Deserializes :class:`OutputChannel` from a dictionary.

        Args:
            channel_dict (dict): serialized :class:`OutputChannel`
            item_name (str): Exporter's name
            project_dir (str): project directory

        Returns:
            OutputChannel: deserialized instance
        """
        channel = OutputChannel(
            channel_dict["in_label"], item_name, channel_dict["out_label"], channel_dict.get("out_url")
        )
        if channel.out_url and not isinstance(channel.out_url["database"], str):
            channel.out_url["database"] = deserialize_path(channel.out_url["database"], project_dir)
        return channel
