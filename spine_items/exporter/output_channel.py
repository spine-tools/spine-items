######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################
"""
Contains :class:`OutputChannel` class.

:authors: A. Soininen (VTT)
:date:    4.1.2022
"""
from dataclasses import dataclass, field


@dataclass
class OutputChannel:
    """
    Input resource specific export settings.
    """

    in_label: str
    """Label of input resource."""
    out_label: str = None
    """Label of output resource. Output file name in case of single file export."""

    def __post_init__(self):
        if self.out_label is None:
            self.out_label = "exported_" + self.in_label

    def to_dict(self):
        """
        Serializes :class:`OutputChannel` into a dictionary.

        Returns:
            dict: serialized :class:`OutputChannel`
        """
        return {"in_label": self.in_label, "out_label": self.out_label}

    @staticmethod
    def from_dict(channel_dict):
        """
        Deserializes :class:`OutputChannel` from a dictionary.

        Args:
            channel_dict (dict): serialized :class:`OutputChannel`

        Returns:
            OutputChannel: deserialized instance
        """
        channel = OutputChannel(channel_dict["in_label"], channel_dict["out_label"])
        return channel
