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
Contains utilities for all items.

:authors: A. Soininen (VTT)
:date:   1.4.2020
"""


def labelled_resource_filepaths(resources):
    """Returns a dice mapping resource labels to filepaths available in given resources.
    The label acts as an identifier for a 'transient_file'.
    """
    return {resource.label: resource.path for resource in resources if resource.hasfilepath}


def labelled_resource_args(resources):
    return {resource.label: resource.arg for resource in resources}
