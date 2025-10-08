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
from __future__ import annotations
from dataclasses import dataclass
import pathlib
import sys
import urllib.parse
from spine_engine.utils.serialization import deserialize_path, serialize_path
from spine_items.utils import UrlDict, convert_url_to_safe_string


@dataclass(frozen=True)
class FilePattern:
    base_path: pathlib.Path
    pattern: str

    def __str__(self):
        return (self.base_path / self.pattern).as_posix()

    def to_dict(self, project_dir: str) -> dict:
        return {"base_path": serialize_path(str(self.base_path), project_dir), "pattern": self.pattern}

    @staticmethod
    def from_dict(serialized: dict, project_dir: str) -> FilePattern:
        return FilePattern(pathlib.Path(deserialize_path(serialized["base_path"], project_dir)), serialized["pattern"])


def restore_database_references(
    references_list: list[UrlDict | str], credentials_dict: dict[str, tuple[str, str]], project_dir: str
) -> list[UrlDict]:
    """Restores data from serialized database references.

    Args:
        references_list: serialized database references
        credentials_dict: mapping from safe URL to (username, password) tuple
        project_dir: path to project directory

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
            db_reference: UrlDict = {
                "dialect": dialect,
                "host": url.hostname if url.hostname is not None else "",
                "port": url.port,
                "database": path,
            }
        else:
            db_reference: UrlDict = dict(reference_dict)
            if "port" in db_reference and isinstance(db_reference["port"], str):
                try:
                    db_reference["port"] = int(db_reference["port"])
                except ValueError:
                    db_reference["port"] = None
        if db_reference["dialect"] == "sqlite":
            db_reference["database"] = deserialize_path(db_reference["database"], project_dir)
        db_reference["username"], db_reference["password"] = credentials_dict.get(
            convert_url_to_safe_string(db_reference), (None, None)
        )
        db_references.append(db_reference)
    return db_references


def _dialect_from_scheme(scheme: str) -> str:
    """Parses dialect from URL scheme.

    Args:
        scheme: URL scheme

    Returns:
        dialect name
    """
    return scheme.split("+")[0]
