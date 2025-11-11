######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# Copyright Spine Engine contributors
# This file is part of Spine Engine.
# Spine Engine is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################
from collections.abc import Callable
from typing import Annotated, ClassVar, Literal, Union
from pydantic import BaseModel, Field
from spine_engine.project import models
from ..utils import UrlDict


class RemoteUrl(BaseModel):
    dialect: Literal["mysql", "postgresql"]
    database: str | None
    host: str | None
    port: int | None
    schema: str | None
    username: str | None
    password: str | None

    def as_url_dict(self, deserialize_path) -> UrlDict:
        return self.model_dump()


class SQLiteUrl(BaseModel):
    dialect: Literal["sqlite"] = "sqlite"
    database: models.Path | None

    def as_url_dict(self, deserialize_path: Callable[[models.Path], str]) -> UrlDict:
        return {
            "dialect": self.dialect,
            "database": deserialize_path(self.database) if self.database is not None else "",
        }


class DataStore(models.ProjectItem):
    version: ClassVar[int] = 1
    item_type: Literal["Data Store"] = "Data Store"
    url: Annotated[Union[RemoteUrl, SQLiteUrl], Field(discriminator="dialect")]
