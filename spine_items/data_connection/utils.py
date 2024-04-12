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

"""This module contains utilities for Data Connection."""
import sys
import urllib.parse
from spine_engine.utils.serialization import deserialize_path
from spine_items.utils import convert_url_to_safe_string


def restore_database_references(references_list, credentials_dict, project_dir):
    """Restores data from serialized database references.

    Args:
        references_list (list of dict): serialized database references
        credentials_dict (dict): mapping from safe URL to (username, password) tuple
        project_dir (str): path to project directory

    Returns:
        list of dict: deserialized database references
    """
    db_references = []
    for reference_dict in references_list:
        if isinstance(reference_dict, str):
            # legacy db reference
            url = urllib.parse.urlparse(reference_dict)
            dialect = _dialect_from_scheme(url.scheme)
            path = url.path
            if dialect == "sqlite" and sys.platform == "win32":
                # Remove extra '/' from file path on Windows.
                path = path[1:]
            db_reference = {
                "dialect": dialect,
                "host": url.hostname,
                "port": url.port,
                "database": path,
            }
        else:
            db_reference = dict(reference_dict)
        if db_reference["dialect"] == "sqlite":
            db_reference["database"] = deserialize_path(db_reference["database"], project_dir)
        db_reference["username"], db_reference["password"] = credentials_dict.get(
            convert_url_to_safe_string(db_reference), (None, None)
        )
        db_references.append(db_reference)
    return db_references


def _dialect_from_scheme(scheme):
    """Parses dialect from URL scheme.

    Args:
        scheme (str): URL scheme

    Returns:
        str: dialect name
    """
    return scheme.split("+")[0]
