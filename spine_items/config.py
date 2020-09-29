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
Constants

:author: M. Marin (KTH)
:date:   28.9.2020
"""
import sys

REQUIRED_SPINEDB_API_VERSION = "0.8.5"

INVALID_CHARS = ["<", ">", ":", '"', "/", "\\", "|", "?", "*", "."]

# Invalid characters for file names
INVALID_FILENAME_CHARS = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]

_on_windows = sys.platform == "win32"


def _executable(name):
    """Appends a .exe extension to `name` on Windows platform."""
    if _on_windows:
        return name + ".exe"
    return name


# GAMS
GAMS_EXECUTABLE = _executable("gams")
GAMSIDE_EXECUTABLE = _executable("gamside")

# Julia
JULIA_EXECUTABLE = _executable("julia")

# Python
PYTHON_EXECUTABLE = _executable("python" if _on_windows else "python3")

STATUSBAR_SS = (
    "QStatusBar{" "background-color: #EBEBE0;" "border-width: 1px;" "border-color: gray;" "border-style: groove;}"
)

TREEVIEW_HEADER_SS = "QHeaderView::section{background-color: #ecd8c6; font-size: 12px;}"

# Tool output directory name
TOOL_OUTPUT_DIR = "output"

# Gimlet default work directory name
GIMLET_WORK_DIR_NAME = "work"
