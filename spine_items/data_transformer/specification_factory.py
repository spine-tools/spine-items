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

"""Data transformer's specification factory."""
from spine_engine.project_item.project_item_specification_factory import ProjectItemSpecificationFactory
from .item_info import ItemInfo
from .data_transformer_specification import DataTransformerSpecification


class SpecificationFactory(ProjectItemSpecificationFactory):
    """A factory to make Data transformer specifications."""

    @staticmethod
    def item_type():
        """See base class."""
        return ItemInfo.item_type()

    @staticmethod
    def make_specification(definition, app_settings, logger):
        """Returns a Data transformer specification."""
        return DataTransformerSpecification.from_dict(definition, logger)
