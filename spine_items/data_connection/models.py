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
from typing import ClassVar
from pydantic import BaseModel
from spine_engine.project import models
from spine_items.utils import UrlDict


class FilePattern(BaseModel):
    base_path: models.Path
    pattern: str


class DataConnection(models.ProjectItem):
    version: ClassVar[int] = 1
    file_preferences: list[models.Path]
    file_patterns: list[FilePattern]
    directory_references: list[models.Path]
    db_references: list[UrlDict]
    db_credentials: dict[str, tuple[str, str]]
