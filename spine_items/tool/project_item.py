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
from dataclasses import dataclass, field
import pathlib
from typing import ClassVar
from spine_engine.project.project_item import ExecutionGroupItem
from spine_engine.project_item.project_item_resource import CmdLineArg


@dataclass
class JuliaOptions:
    sysimage_path: pathlib.Path | None


@dataclass(frozen=True)
class ToolItem(ExecutionGroupItem):
    item_type: ClassVar[str] = "tool"
    execute_in_work: bool = True
    cmd_line_args: list[CmdLineArg] = field(default_factory=list)
    kill_completed_processes: bool = False
    log_process_output: bool = False
    group_id: str | None = None
    root_dir: pathlib.Path | None = None
    output_directory: pathlib.Path | None = None
    type_options: JuliaOptions | None = None

    @classmethod
    def _constructor_kwargs(cls, item_dict: dict) -> dict:
        kwargs = ExecutionGroupItem._constructor_kwargs(item_dict)
        kwargs["cmd_line_args"] = item_dict["cmd_line_args"]
        return kwargs
