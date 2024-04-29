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

"""Contains the :class:`MappingsTableProxy` model."""
from itertools import takewhile
from PySide6.QtCore import QSortFilterProxyModel


class MappingsTableProxy(QSortFilterProxyModel):
    def lessThan(self, source_left, source_right):
        if source_left.column() == 0:
            left_name = source_left.data()
            left_count = "".join(takewhile(lambda c: c.isdigit(), reversed(left_name)))
            if not left_count:
                return super().lessThan(source_left, source_right)
            right_name = source_right.data()
            right_count = "".join(takewhile(lambda c: c.isdigit(), reversed(right_name)))
            if not right_count:
                return super().lessThan(source_left, source_right)
            left_base = left_name[: len(left_name) - len(left_count)]
            right_base = right_name[: len(right_name) - len(right_count)]
            if left_base != right_base:
                return super().lessThan(source_left, source_right)
            return int(left_count[::-1]) < int(right_count[::-1])
        return source_left.row() < source_right.row()
