######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# Copyright Spine Items contributors
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""Contains a model to handle source tables and import mapping."""
from enum import Enum, unique
from spinedb_api.mapping import Position
from spinedb_api.parameter_value import split_value_and_type
from spinedb_api import from_database, ParameterValueFormatError
from spinedb_api.helpers import fix_name_ambiguity, string_to_bool
from spinedb_api.import_mapping.import_mapping import (
    EntityClassMapping,
    EntityMapping,
    DimensionMapping,
    ElementMapping,
    EntityGroupMapping,
    AlternativeMapping,
    ScenarioMapping,
    ScenarioAlternativeMapping,
    ParameterValueListMapping,
    ParameterValueMapping,
    ParameterValueTypeMapping,
    ParameterDefaultValueMapping,
    ParameterDefaultValueTypeMapping,
    check_validity,
    ParameterDefinitionMapping,
    ParameterValueIndexMapping,
    ParameterDefaultValueIndexMapping,
    DefaultValueIndexNameMapping,
    IndexNameMapping,
    ScenarioBeforeAlternativeMapping,
)
from spinetoolbox.helpers import color_from_index
from spinetoolbox.spine_db_manager import SpineDBManager


@unique
class MappingType(Enum):
    EntityClass = "Entity class"
    Entity = "Entity"
    EntityGroup = "Entity group"
    Alternative = "Alternative"
    Scenario = "Scenario"
    ScenarioAlternative = "Scenario alternative"
    ParameterValueList = "Parameter value list"


VALUE_TYPES = {
    "Single value": "single_value",
    "Array": "array",
    "Map": "map",
    "Time series": "time_series",
    "Time pattern": "time_pattern",
}
DISPLAY_VALUE_TYPES = {v: k for k, v in VALUE_TYPES.items()}

DISPLAY_MAPPING_NAMES = {
    "EntityClass": "Entity class names",
    "Entity": "Entity names",
    "EntityMetadata": "Entity metadata",
    "EntityGroup": "Member names",
    "Dimension": "Dimension names",
    "Element": "Element names",
    "Alternative": "Alternative names",
    "Scenario": "Scenario names",
    "ScenarioActiveFlag": "Scenario active flags",
    "ScenarioAlternative": "Alternative names",
    "ScenarioBeforeAlternative": "Before alternative names",
    "ParameterValueList": "Value list names",
    "ParameterValueListValue": "Parameter values",
    "ParameterDefinition": "Parameter names",
    "ParameterValue": "Parameter values",
    "ParameterValueType": None,
    "ParameterValueMetadata": "Parameter value metadata",
    "IndexName": "Parameter index names",
    "ParameterValueIndex": "Parameter indexes",
    "ExpandedValue": "Parameter values",
    "ParameterDefaultValue": "Parameter default values",
    "ParameterDefaultValueType": None,
    "DefaultValueIndexName": "Parameter index names",
    "ParameterDefaultValueIndex": "Parameter indexes",
    "ExpandedDefaultValue": "Parameter default values",
}


class FlattenedMappings:
    def __init__(self, root_mapping):
        """
        Args:
            root_mapping (ImportMapping): root mapping
        """
        self._components = None
        self._map_type = None
        self._value_type = None
        self._display_names = None
        self._display_to_logical = None
        self._display_colors = None
        self._row_issues = None
        self.mapping_list_item = None
        self.set_root_mapping(root_mapping)

    @property
    def map_type(self):
        return self._map_type

    def set_root_mapping(self, root_mapping):
        """Sets root mapping resetting data.

        Args:
            root_mapping (ImportMapping)
        """
        self._components = root_mapping.flatten()
        self._map_type = self._resolve_map_type(self._components)
        self._value_type = self._resolve_value_type()
        self._display_names, self._display_to_logical = self._displayable_component_names()
        self._display_colors = self._make_colors()
        self._row_issues = None

    @property
    def display_names(self):
        return self._display_names

    @property
    def display_colors(self):
        return self._display_colors

    @property
    def root_mapping(self):
        return self._components[0]

    @property
    def value_type(self):
        return self._value_type

    def is_time_series_value(self):
        """Checks if value is a time series.

        Returns:
            bool: True if value is a time series, False otherwise
        """
        return self._value_type == "Time series"

    def is_map_value(self):
        """Checks if value is a map.

        Returns:
            bool: True if value is a map, False otherwise
        """
        return self._value_type == "Map"

    def map_dimension_count(self):
        """Calculates dimensions count for Map type value.

        Returns:
            int: dimension count
        """
        if not self.is_map_value():
            return 1
        parameter_type = self.display_parameter_type()
        index_mapping = ParameterValueIndexMapping if parameter_type == "Value" else ParameterDefaultValueIndexMapping
        return len([m for m in self._components if isinstance(m, index_mapping)])

    def uses_before_alternative(self):
        """Checks if before alternative component is part of the mappings.

        Returns:
            bool: True if mapping uses before alternative, False otherwise
        """
        return any(isinstance(c, ScenarioBeforeAlternativeMapping) for c in reversed(self._components))

    def set_map_dimension_count(self, dimension_count):
        """Sets new dimensions for Map type value.

        Args:
            dimension_count (int): dimension count
        """
        if not self.is_map_value():
            return
        previous_dimension_count = self.map_dimension_count()
        parameter_type = self.display_parameter_type()
        name_mapping_cls = IndexNameMapping if parameter_type == "Value" else DefaultValueIndexNameMapping
        index_mapping_cls = (
            ParameterValueIndexMapping if parameter_type == "Value" else ParameterDefaultValueIndexMapping
        )
        last_index_mapping = next(m for m in reversed(self._components) if isinstance(m, index_mapping_cls))
        last_index_mapping_child = last_index_mapping.child
        if dimension_count > previous_dimension_count:
            for _ in range(previous_dimension_count, dimension_count):
                name_mapping = name_mapping_cls(Position.hidden)
                last_index_mapping.child = name_mapping
                index_mapping = index_mapping_cls(Position.hidden)
                name_mapping.child = index_mapping
                last_index_mapping = index_mapping
        else:
            for _ in range(dimension_count, previous_dimension_count):
                name_mapping = last_index_mapping.parent
                last_index_mapping = name_mapping.parent
        last_index_mapping.child = last_index_mapping_child
        self.set_root_mapping(self._components[0])

    def set_map_compress(self, compress):
        """
        Sets the compress flag for Map type parameters.

        Args:
            compress (bool): flag value
        """
        if not self.is_map_value():
            return
        self.value_mapping().compress = compress

    def set_value_components(self, component):
        """Sets value mapping components.

        Args:
            component (ImportMapping): parameter value component root
        """
        m = self.value_mapping()
        if m is None or m.parent is None:
            return
        m.parent.child = component
        self.set_root_mapping(self._components[0])

    def append_tail_component(self, component):
        """Adds a new component as the last component in mappings.

        Args:
            component (ImportMapping): component to add
        """
        self._components[-1].child = component
        self.set_root_mapping(self._components[0])

    def cut_tail_component(self):
        """Removes the tail component."""
        self._components[-2].child = None
        self.set_root_mapping(self._components[0])

    def read_start_row(self):
        """Returns read start row.

        Returns:
            int: read start row
        """
        return self._components[0].read_start_row

    def set_read_start_row(self, row):
        """Sets read start row.

        Args:
            row (int): read start row
        """
        self._components[0].read_start_row = row

    def skip_columns(self):
        """Returns skipped columns.

        Returns:
            list: list of skipped column indexes or names
        """
        return self._components[0].skip_columns

    def set_skip_columns(self, skip_columns):
        """Sets skipped columns.

        Args:
            skip_columns (list): skipped column indexes or names
        """
        self._components[0].skip_columns = skip_columns

    def component_at(self, row):
        """Returns mapping corresponding to a display row.

        Args:
            row (int): display row index

        Returns:
            ImportMapping: mapping
        """
        return self._components[self._display_to_logical[row]]

    def display_position_type(self, row):
        """Creates a 'type' for position for displaying.

        Args:
            row (int): display row

        Returns:
            str: display position
        """
        if self._components[0].is_pivoted() and row == len(self._display_names) - 1:
            return "Pivoted"
        component = self._components[self._display_to_logical[row]]
        if component.position == Position.hidden:
            if component.value is None:
                return "None"
            return "Constant"
        if component.position == Position.header:
            if component.value is None:
                return "Headers"
            return "Column Header"
        if component.position == Position.table_name:
            return "Table Name"
        if component.position >= 0:
            return "Column"
        return "Row"

    def set_display_position_type(self, row, position_type):
        """Sets component's position 'type'.

        Args:
            row (int): display row
            position_type (str or int): position type
        """
        component = self.component_at(row)
        if position_type in ("None", "", None):
            component.position = Position.hidden
            component.value = None
        elif position_type == "Constant":
            component.position = Position.hidden
            component.value = "constant"
        elif position_type == "Column":
            component.position = 0
            component.value = None
        elif position_type == "Column Header":
            component.position = Position.header
            component.value = 0
        elif position_type == "Headers":
            component.position = Position.header
            component.value = None
        elif position_type == "Row":
            component.position = -1
            component.value = None
        elif position_type == "Table Name":
            component.position = Position.table_name
        self._row_issues = None

    def display_position(self, row):
        """Converts a position to something displayable.

        Args:
            row (int): display row index

        Returns:
            str or int or bool: display position
        """
        component = self._components[self._display_to_logical[row]]
        # A) Handle two special cases for value mappings
        if self._components[0].is_pivoted() and row == len(self._display_names) - 1:
            # 1. Pivoted data
            return "Pivoted values"
        if self._display_names[row].endswith("values"):
            if component.position == Position.hidden and component.value is not None:
                # 2. Constant value: we want special database value support
                try:
                    value = from_database(*split_value_and_type(component.value))
                    return SpineDBManager.display_data_from_parsed(value)
                except ParameterValueFormatError:
                    return None
        # B) Handle all other cases cases
        if component.position == Position.hidden:
            if self._display_names[row].endswith("flags") and not isinstance(component.value, bool):
                return string_to_bool(str(component.value))
            return component.value
        if component.position == Position.header:
            if component.value is None:
                return "Headers"
            return component.value + 1
        if component.position == Position.table_name:
            return "<table name>"
        if component.position >= 0:
            return component.position + 1
        return -(component.position + 1) + 1

    def set_display_position(self, row, position_type, position):
        """Sets component's position.

        Args:
            row (int): display row
            position_type (str): display position type
            position (str or int): display position
        """
        component = self.component_at(row)
        if position_type == "Constant":
            component.value = position
        elif position_type == "Column":
            component.position = position - 1
        elif position_type == "Column Header":
            component.value = position - 1
        elif position_type == "Row":
            component.position = -position
        self._row_issues = None

    def display_row_issues(self, row):
        """Validates a display row for issues.

        Args:
            row (int): display row index

        Returns:
            list of str: issues
        """
        if self._row_issues is None:
            self._row_issues = {}
            for issue in check_validity(self._components[0]):
                self._row_issues.setdefault(issue.rank, []).append(issue.msg)
        return self._row_issues.get(self._display_to_logical[row], list())

    def _component_name_from_type(self, component_type):
        """Computes display name for a mapping component.

        Args:
            component_type (str): component's MAP_TYPE

        Returns:
            str: display name or None if component is invisible
        """
        if self._map_type == MappingType.EntityGroup and component_type == "Entity":
            return "Group names"
        if self._value_type == "Array" and component_type in ("ParameterValueIndex", "ParameterDefaultValueIndex"):
            return None
        if self._map_type == MappingType.EntityClass and component_type == "Entity" and self.has_dimensions():
            return None
        return DISPLAY_MAPPING_NAMES[component_type]

    def _displayable_component_names(self):
        """Generates a list of displayable mapping component names.

        Returns:
            list of str: displayable names
        """
        component_names = [self._component_name_from_type(m.MAP_TYPE) for m in self._components]
        display_names = []
        display_row = 0
        display_row_to_flattened_index = {}
        for logical_row, name in enumerate(component_names):
            if name is None:
                continue
            display_names.append(name)
            display_row_to_flattened_index[display_row] = logical_row
            display_row += 1
        display_names = fix_name_ambiguity(display_names, prefix=" ")
        return display_names, display_row_to_flattened_index

    @staticmethod
    def _resolve_map_type(flattened):
        """Computes general map type for given flattened mappings.

        Args:
            flattened (list of ImportMapping): flattened mappings

        Returns:
            MappingType: map type
        """
        if not flattened:
            return None
        head_mapping = flattened[0]
        if isinstance(head_mapping, EntityClassMapping):
            if any(isinstance(m, EntityGroupMapping) for m in flattened):
                return MappingType.EntityGroup
            return MappingType.EntityClass
        if isinstance(head_mapping, AlternativeMapping):
            return MappingType.Alternative
        if isinstance(head_mapping, ScenarioMapping):
            if any(isinstance(m, ScenarioAlternativeMapping) for m in flattened):
                return MappingType.ScenarioAlternative
            return MappingType.Scenario
        if isinstance(head_mapping, ParameterValueListMapping):
            return MappingType.ParameterValueList

    def _resolve_value_type(self):
        """Computes display name for value type.

        Returns:
            str: value type's display name
        """
        m = self.value_mapping()
        if m is None:
            return None
        if isinstance(m, (ParameterDefaultValueTypeMapping, ParameterValueTypeMapping)):
            return DISPLAY_VALUE_TYPES.get(m.value, "Single value")
        return "Single value"

    def can_have_dimensions(self):
        """Returns True if the mappings can have dimensions.

        Returns:
            bool: True if mappings have dimensions, False otherwise
        """
        return self._map_type == MappingType.EntityClass

    def has_dimensions(self):
        """Returns True if the mappings have dimensions.

        Returns:
            bool: True if mappings have dimensions, False otherwise
        """
        return self.dimension_count() > 0

    def dimension_count(self):
        """Counts entity dimensions.

        Returns:
            int: entity dimensions
        """
        return len([m for m in self._components if isinstance(m, DimensionMapping)])

    def set_dimension_count(self, dimension_count):
        """Sets the numbers of entity dimensions.

        Args:
            dimension_count (int): new dimension count
        """
        if not self.can_have_dimensions():
            return None, None
        current_dimension_count = self.dimension_count()
        last_dim_mapping = next(
            m for m in reversed(self._components) if isinstance(m, (DimensionMapping, EntityClassMapping))
        )
        last_el_mapping = next(m for m in reversed(self._components) if isinstance(m, (ElementMapping, EntityMapping)))
        last_dim_mapping_child = last_dim_mapping.child
        last_el_mapping_child = last_el_mapping.child
        if dimension_count > current_dimension_count:
            for _ in range(current_dimension_count, dimension_count):
                last_dim_mapping.child = DimensionMapping(Position.hidden)
                last_dim_mapping = last_dim_mapping.child
                last_el_mapping.child = ElementMapping(Position.hidden)
                last_el_mapping = last_el_mapping.child
        else:
            for _ in range(dimension_count, current_dimension_count):
                last_dim_mapping = last_dim_mapping.parent
                last_el_mapping = last_el_mapping.parent
        last_dim_mapping.child = last_dim_mapping_child
        last_el_mapping.child = last_el_mapping_child
        self.set_root_mapping(self._components[0])
        self._ensure_consistent_import_entities()

    def may_import_entities(self):
        """Checks if the mappings can optionally import entities.

        Returns:
            bool: True if mappings can import entities, False otherwise
        """
        return self._map_type in (MappingType.EntityClass, MappingType.EntityGroup)

    def _import_entities_mappings(self):
        """Collects a list of mapping components that have an import_entities attribute.

        Returns:
            list of ImportMapping: list of components with import_entities
        """
        return [m for m in self._components if hasattr(m, "import_entities")]

    def import_entities(self):
        """Returns the import entities flag.

        Returns:
            bool: True if imports entities is set, False otherwise
        """
        return all(m.import_entities for m in self._import_entities_mappings())

    def set_import_entities(self, import_entities):
        """Sets the import entities flag for components that support it.

        Args:
            import_entities (bool): flag value
        """
        for m in self._import_entities_mappings():
            m.import_entities = import_entities

    def _ensure_consistent_import_entities(self):
        """If any mapping has the import entities flag set, sets the flag also for all other mappings."""
        mappings = self._import_entities_mappings()
        if any(mapping.import_entities for mapping in mappings):
            for m in mappings:
                m.import_entities = True

    def has_parameters(self):
        """Returns True if the mappings have parameters.

        Returns:
            bool: True if mapping has parameter, False otherwise
        """
        return self._map_type == MappingType.EntityClass

    def _parameter_definition_component(self):
        """Searches for ParameterDefinitionMapping within the components.

        Returns:
            ParameterDefinitionMapping: mapping component or None if not found
        """
        return next((m for m in self._components if isinstance(m, ParameterDefinitionMapping)), None)

    def set_parameter_components(self, parameter_definition_component):
        """Changes parameter type.

        Args:
            parameter_definition_component (ImportMapping, optional): root of parameter mappings;
                None removes the mappings
        """
        m = self._parameter_definition_component()
        parent = m.parent if m is not None else self._components[-1]
        parent.child = parameter_definition_component
        self.set_root_mapping(self._components[0])

    def display_parameter_type(self):
        """Returns a string representation of mappings' parameter type.

        Returns:
            str: parameter type
        """
        if any(isinstance(m, (ParameterValueMapping, ParameterValueTypeMapping)) for m in self._components):
            return "Value"
        if any(isinstance(m, ParameterDefinitionMapping) for m in self._components):
            return "Definition"
        return "None"

    def has_value_component(self):
        """Returns True if any of the components is a value mapping.

        Returns:
            bool: True if components contain a value mapping, False otherwise
        """
        return self.value_mapping() is not None

    def value_type_label(self):
        """Returns a type label for value.

        Returns:
            str: type label
        """
        value_mapping = self.value_mapping()
        if value_mapping is None:
            return "<no label>"
        if isinstance(value_mapping, (ParameterValueTypeMapping, ParameterValueMapping)):
            return "Value:"
        return "Default value:"

    def value_mapping(self):
        """Finds first parameter value mapping component from flattened mappings.

        Returns:
            ImportMapping: value mapping or None if not found
        """
        value_mappings = (
            ParameterValueMapping,
            ParameterValueTypeMapping,
            ParameterDefaultValueMapping,
            ParameterDefaultValueTypeMapping,
        )
        return next((m for m in self._components if isinstance(m, value_mappings)), None)

    def _make_colors(self):
        """Creates display colors for mapping components.

        Returns:
            list of QColor: colors
        """
        component_count = len(self._display_names)
        return [color_from_index(i, component_count).lighter() for i in range(component_count)]
