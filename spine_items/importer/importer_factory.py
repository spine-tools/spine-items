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
The ImporterFactory class.

:author: M. Marin (KTH)
:date:   15.4.2020
"""

from PySide2.QtCore import Qt
from spinetoolbox.project_item.project_item_factory import ProjectItemFactory
from spinetoolbox.import_editor.widgets.import_editor_window import ImportEditorWindow
from .importer import Importer
from .importer_icon import ImporterIcon
from .importer_specification import ImporterSpecification
from .widgets.importer_properties_widget import ImporterPropertiesWidget
from .widgets.add_importer_widget import AddImporterWidget
from .widgets.custom_menus import SpecificationMenu


_import_editors = {}  # Key is (spec_name, filepath), value is the ImportEditorWindow instance


class ImporterFactory(ProjectItemFactory):
    @staticmethod
    def item_class():
        return Importer

    @staticmethod
    def icon():
        return ":/icons/item_icons/database-import.svg"

    @staticmethod
    def supports_specifications():
        return True

    @staticmethod
    def make_add_item_widget(toolbox, x, y, specification):
        return AddImporterWidget(toolbox, x, y, specification)

    @staticmethod
    def make_icon(toolbox):
        return ImporterIcon(toolbox, ImporterFactory.icon())

    @staticmethod
    def make_item(name, item_dict, toolbox, project, logger):
        return Importer.from_dict(name, item_dict, toolbox, project, logger)

    @staticmethod
    def make_properties_widget(toolbox):
        return ImporterPropertiesWidget(toolbox)

    @staticmethod
    def make_specification_menu(parent, index):
        return SpecificationMenu(parent, index)

    @staticmethod
    def show_specification_widget(toolbox, specification=None, filepath=None):
        """See base class."""
        key = specification.name if specification else None
        import_editor = _import_editors.get(key, None)
        if import_editor:
            if import_editor.windowState() & Qt.WindowMinimized:
                # Remove minimized status and restore window with the previous state (maximized/normal state)
                import_editor.setWindowState(import_editor.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
                import_editor.activateWindow()
            else:
                import_editor.raise_()
            return
        msg = "Opening Import editor"
        if specification:
            msg += f" for specification {specification.name}"
            if filepath:
                msg += f" with working file {filepath}"
        toolbox.msg.emit(msg)
        import_editor = _import_editors[key] = ImportEditorWindow(toolbox, specification, filepath)
        import_editor.destroyed.connect(lambda o=None, key=key: _import_editors.pop(key, None))
        import_editor.show()

    @staticmethod
    def tear_down():
        """Closes all preview widgets."""
        for widget in _import_editors.values():
            widget.close()
