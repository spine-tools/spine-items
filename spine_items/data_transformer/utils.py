######################################################################################################################
# Copyright (C) 2017-2021 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Contains utility Data Transformer functions.

:authors: M. Marin (KTH)
:date:   26.11.2020
"""


def make_label(label, name):
    return "{" + f"{label[1:-1]}@{name}" + "}"


def make_metadata(resource, name):
    metadata = resource.metadata.copy()
    label = metadata.pop("label", None)
    if label is not None:
        metadata["label"] = make_label(label, name)
    return metadata
