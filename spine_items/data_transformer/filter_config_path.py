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

"""Contains utilities for filter config paths."""
from pathlib import Path


def filter_config_path(data_dir):
    """
    Constructs an absolute path to transformer's configuration file.

    Args:
        data_dir (str): absolute path to project item's data directory

    Returns:
        str: a path to the config file
    """
    file_name = ".filter_config.json"
    return str(Path(data_dir, file_name))
