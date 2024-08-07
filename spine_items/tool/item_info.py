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

"""Tool project item info."""
from spine_engine.project_item.project_item_info import ProjectItemInfo


class ItemInfo(ProjectItemInfo):
    @staticmethod
    def item_type():
        """See base class."""
        return "Tool"

    @staticmethod
    def specification_icon(specification):
        if not specification:
            return None
        if specification.tooltype == "python":
            return ":icons/item_icons/python-logo.svg"
        if specification.tooltype == "julia":
            return ":icons/item_icons/julia-logo.svg"
        if specification.tooltype == "executable":
            return ":icons/item_icons/terminal-logo.svg"
        if specification.tooltype == "gams":
            return ":icons/item_icons/gams-logo.svg"
        return None
