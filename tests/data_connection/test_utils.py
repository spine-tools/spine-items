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
import pathlib
from spine_items.data_connection.utils import FilePattern
from tests.mock_helpers import ProjectForSerialization


class TestFilePattern:
    def test_serialization_outside_of_project_dir(self):
        path = pathlib.Path(__file__).parent / "data_dir"
        pattern = FilePattern(path, "*.py")
        project_dir = str(pathlib.Path(__file__).parent / "project_dir")
        serialized = pattern.to_dict(ProjectForSerialization(project_dir))
        deserialized = FilePattern.from_dict(serialized, project_dir)
        assert deserialized == pattern

    def test_serialization_inside_project_dir(self):
        project_dir = pathlib.Path(__file__).parent / "project_dir"
        path = project_dir / "data_dir"
        pattern = FilePattern(path, "*.py")
        serialized = pattern.to_dict(ProjectForSerialization(project_dir))
        deserialized = FilePattern.from_dict(serialized, str(project_dir))
        assert deserialized == pattern
