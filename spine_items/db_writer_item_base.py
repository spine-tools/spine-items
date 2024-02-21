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

"""Contains base classes for items that write to db."""
from PySide6.QtCore import Slot
from spinetoolbox.project_item.project_item import ProjectItem


class DBWriterItemBase(ProjectItem):
    """Base class for items that might write to a Spine DB."""

    def successor_data_stores(self):
        for name in self._project.successor_names(self.name):
            item = self._project.get_item(name)
            if item.item_type() == "Data Store":
                yield item

    @Slot(object, object)
    def handle_execution_successful(self, execution_direction, engine_state):
        """Notifies Toolbox of successful database import."""
        if execution_direction != "FORWARD":
            return
        committed_db_maps = set()
        for successor in self.successor_data_stores():
            url = successor.sql_alchemy_url()
            db_map = self._toolbox.db_mngr.db_map(url)
            if db_map:
                committed_db_maps.add(db_map)
        if committed_db_maps:
            self._toolbox.db_mngr.notify_session_committed(self, *committed_db_maps)

    def _check_write_index(self):
        """Checks if write index is valid."""
        conflicting = {}
        descendants = set(self._project.descendant_names(self.name))
        for connection in self._project.outgoing_connections(self.name):
            sibling_connections = set(self._project.incoming_connections(connection.destination)) - {connection}
            conflicting.update(
                {
                    c.source: c.destination
                    for c in sibling_connections
                    if c.write_index < connection.write_index and c.source in descendants
                }
            )
        for name, dest in conflicting.items():
            self.add_notification(
                f"This item can't be a dependency to {name}, because {name} is set to write earlier to {dest}.\n"
                f"Possible fix: increase the write_index in the arrow from {name} to {dest}"
            )
