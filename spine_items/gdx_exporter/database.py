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
Contains :class:`Database`.

:authors: A. Soininen (VTT)
:date:    14.10.2020
"""


class Database:
    """
    Database specific export settings.

    Attributes:
        url (str): database URL
        output_file_name (str): output file name (relative to item's data dir)
    """

    def __init__(self):
        self.url = ""
        self.output_file_name = ""

    def to_dict(self):
        """
        Serializes :class:`Database` into a dictionary.

        Returns:
            dict: serialized :class:`Database`
        """
        return {"output_file_name": self.output_file_name}

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
