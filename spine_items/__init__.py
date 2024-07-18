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

""" Spine items. """
from .version import __version__


def _factories_and_executable_items():
    from . import data_connection, data_store, data_transformer, exporter, importer, merger, tool, view
    from .data_connection.data_connection_factory import DataConnectionFactory
    from .data_store.data_store_factory import DataStoreFactory
    from .data_transformer import specification_factory
    from .data_transformer.data_transformer_factory import DataTransformerFactory
    from .exporter import specification_factory
    from .exporter.exporter_factory import ExporterFactory
    from .importer import specification_factory
    from .importer.importer_factory import ImporterFactory
    from .merger.merger_factory import MergerFactory
    from .tool import specification_factory
    from .tool.tool_factory import ToolFactory
    from .view.view_factory import ViewFactory

    modules = (data_connection, data_store, data_transformer, exporter, importer, merger, tool, view)
    item_infos = tuple(module.item_info.ItemInfo for module in modules)
    factories = (
        DataConnectionFactory,
        DataStoreFactory,
        DataTransformerFactory,
        ExporterFactory,
        ImporterFactory,
        MergerFactory,
        ToolFactory,
        ViewFactory,
    )
    factories = {info.item_type(): factory for info, factory in zip(item_infos, factories)}
    executables = {module.item_info.ItemInfo.item_type(): module.executable_item.ExecutableItem for module in modules}
    specification_item_submodules = (data_transformer, exporter, importer, tool)
    specification_factories = {
        module.item_info.ItemInfo.item_type(): module.specification_factory.SpecificationFactory
        for module in specification_item_submodules
    }
    return (
        factories.copy,
        executables.copy,
        specification_factories.copy,
    )


item_factories, executable_items, item_specification_factories = _factories_and_executable_items()
del _factories_and_executable_items
