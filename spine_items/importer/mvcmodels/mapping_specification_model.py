######################################################################################################################
# Copyright (C) 2017-2021 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Contains the mapping specification model.

:author: P. Vennström (VTT)
:date:   1.6.2019
"""

from enum import Enum, unique
from distutils.util import strtobool
from PySide2.QtCore import Qt, QAbstractTableModel, Signal, QTimer
from spinetoolbox.helpers import color_from_index
from spinetoolbox.mvcmodels.shared import PARSED_ROLE
from spinetoolbox.spine_db_manager import SpineDBManager
from spinedb_api.parameter_value import (
    from_database,
    join_value_and_type,
    split_value_and_type,
    ParameterValueFormatError,
)
from spinedb_api.helpers import fix_name_ambiguity
from spinedb_api.mapping import Position, unflatten
from spinedb_api.import_mapping.import_mapping_compat import (
    parse_named_mapping_spec,
    unparse_named_mapping_spec,
    import_mapping_from_dict,
    parameter_mapping_from_dict,
    parameter_value_mapping_from_dict,
    parameter_default_value_mapping_from_dict,
)
from spinedb_api.import_mapping.import_mapping import (
    ImportMapping,
    ObjectClassMapping,
    ObjectGroupMapping,
    RelationshipClassMapping,
    RelationshipClassObjectClassMapping,
    RelationshipObjectMapping,
    AlternativeMapping,
    ScenarioMapping,
    ScenarioAlternativeMapping,
    ParameterValueListMapping,
    FeatureEntityClassMapping,
    ToolMapping,
    ToolFeatureEntityClassMapping,
    ToolFeatureMethodEntityClassMapping,
    ParameterDefinitionMapping,
    ParameterValueMapping,
    ParameterValueTypeMapping,
    ParameterValueIndexMapping,
    ParameterDefaultValueMapping,
    ParameterDefaultValueTypeMapping,
    ParameterDefaultValueIndexMapping,
    check_validity,
    IndexNameMapping,
    DefaultValueIndexNameMapping,
)
from spinedb_api.import_mapping.type_conversion import DateTimeConvertSpec, FloatConvertSpec, StringConvertSpec
from ..commands import SetComponentMappingReference, SetComponentMappingType
from ..mapping_colors import ERROR_COLOR


@unique
class MappingType(Enum):
    ObjectClass = "Object class"
    RelationshipClass = "Relationship class"
    ObjectGroup = "Object group"
    Alternative = "Alternative"
    Scenario = "Scenario"
    ScenarioAlternative = "Scenario alternative"
    ParameterValueList = "Parameter value list"
    Feature = "Feature"
    Tool = "Tool"
    ToolFeature = "Tool feature"
    ToolFeatureMethod = "Tool feature method"


VALUE_TYPES = {
    "Single value": "single_value",
    "Array": "array",
    "Map": "map",
    "Time series": "time_series",
    "Time pattern": "time_pattern",
}
DISPLAY_VALUE_TYPES = {v: k for k, v in VALUE_TYPES.items()}

DISPLAY_MAPPING_NAMES = {
    "ObjectClass": "Object class names",
    "Object": "Object names",
    "ObjectMetadata": "Object metadata",
    "ObjectGroup": "Member names",
    "RelationshipClass": "Relationship class names",
    "RelationshipClassObjectClass": "Object class names",
    "Relationship": None,
    "RelationshipObject": "Object names",
    "RelationshipMetadata": "Relationship metadata",
    "Alternative": "Alternative names",
    "Scenario": "Scenario names",
    "ScenarioActiveFlag": "Scenario active flags",
    "ScenarioAlternative": "Alternative names",
    "ScenarioBeforeAlternative": "Before alternative names",
    "ParameterValueList": "Value list names",
    "ParameterValueListValue": "Parameter values",
    "FeatureEntityClass": "Entity class names",
    "FeatureParameterDefinition": "Parameter names",
    "Tool": "Tool names",
    "ToolFeatureEntityClass": "Entity class names",
    "ToolFeatureParameterDefinition": "Parameter names",
    "ToolFeatureRequiredFlag": "Tool feature required flags",
    "ToolFeatureMethodEntityClass": "Entity class names",
    "ToolFeatureMethodParameterDefinition": "Parameter names",
    "ToolFeatureMethodMethod": "Tool feature methods",
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


class MappingSpecificationModel(QAbstractTableModel):
    """
    A model to hold a Mapping specification.
    """

    mapping_read_start_row_changed = Signal(int)
    """Emitted after mapping's read start row has been changed."""
    row_or_column_type_recommended = Signal(int, object, object)
    """Emitted when a change in mapping prompts for change in column or row type."""
    multi_column_type_recommended = Signal(object, object)
    """Emitted when all but given columns should be of given type."""
    about_to_undo = Signal(str, str)
    """Emitted before an undo/redo action."""
    mapping_changed = Signal()
    """Emitted whenever the user changes the mapping.
    Used to setup an index widget where the user can specify the type"""

    def __init__(self, table_name, mapping_name, mapping, undo_stack):
        """
        Args:
            table_name (str): source table name
            mapping_name (str): mapping name
            mapping (spinedb_api.ItemMappingBase): the item mapping to model
            undo_stack (QUndoStack): undo stack
        """
        super().__init__()
        self._component_names = []
        self._component_mappings = []
        self._logical_row = {}  # Mapping from visual to logical row
        self._colors = []
        self._root_mapping = None
        if mapping is not None:
            self.set_mapping(mapping)
        self._table_name = table_name
        self._mapping_name = mapping_name
        self._undo_stack = undo_stack
        self._row_issues = None

    @property
    def mapping(self):
        return self._root_mapping

    @property
    def mapping_name(self):
        return self._mapping_name

    @mapping_name.setter
    def mapping_name(self, name):
        self._mapping_name = name

    @property
    def source_table_name(self):
        return self._table_name

    @property
    def skip_columns(self):
        return self._root_mapping.skip_columns

    @property
    def map_type(self):
        if self._root_mapping is None:
            return None
        if isinstance(self._root_mapping, ObjectClassMapping):
            if any(isinstance(m, ObjectGroupMapping) for m in self._component_mappings):
                return MappingType.ObjectGroup
            return MappingType.ObjectClass
        if isinstance(self._root_mapping, RelationshipClassMapping):
            return MappingType.RelationshipClass
        if isinstance(self._root_mapping, AlternativeMapping):
            return MappingType.Alternative
        if isinstance(self._root_mapping, ScenarioMapping):
            if any(isinstance(self._root_mapping.child, ScenarioAlternativeMapping) for m in self._component_mappings):
                return MappingType.ScenarioAlternative
            return MappingType.Scenario
        if isinstance(self._root_mapping, ParameterValueListMapping):
            return MappingType.ParameterValueList
        if any(isinstance(m, FeatureEntityClassMapping) for m in self._component_mappings):
            return MappingType.Feature
        if isinstance(self._root_mapping, ToolMapping):
            if any(isinstance(m, ToolFeatureEntityClassMapping) for m in self._component_mappings):
                return MappingType.ToolFeature
            return MappingType.Tool
        if any(isinstance(m, ToolFeatureMethodEntityClassMapping) for m in self._component_mappings):
            return MappingType.ToolFeatureMethod

    def last_pivot_row(self):
        return self._root_mapping.last_pivot_row()

    def dimension_count(self):
        if self._root_mapping is None:
            return 0
        return len([m for m in self._component_mappings if isinstance(m, RelationshipClassObjectClassMapping)])

    def mapping_can_import_objects(self):
        return self.map_type in (MappingType.RelationshipClass, MappingType.ObjectGroup)

    def _import_objects_mappings(self):
        if not self.mapping_can_import_objects():
            return []
        return [m for m in self._component_mappings if hasattr(m, "import_objects")]

    @property
    def import_objects(self):
        return all(m.import_objects for m in self._import_objects_mappings())

    @property
    def parameter_mapping(self):
        return next((m for m in self._component_mappings if isinstance(m, ParameterDefinitionMapping)), None)

    @parameter_mapping.setter
    def parameter_mapping(self, parameter_mapping):
        m = self.parameter_mapping
        parent = m.parent if m is not None else self._component_mappings[-1]
        parent.child = parameter_mapping

    @property
    def value_mapping(self):
        value_mappings = (
            ParameterValueMapping,
            ParameterValueTypeMapping,
            ParameterDefaultValueMapping,
            ParameterDefaultValueTypeMapping,
        )
        return next((m for m in self._component_mappings if isinstance(m, value_mappings)), None)

    @value_mapping.setter
    def value_mapping(self, value_mapping):
        m = self.value_mapping
        if m is None or m.parent is None:
            return
        m.parent.child = value_mapping

    @property
    def parameter_type(self):
        if not self._root_mapping:
            return None
        if not self.mapping_has_parameters():
            return None
        if any(isinstance(m, (ParameterValueMapping, ParameterValueTypeMapping)) for m in self._component_mappings):
            return "Value"
        if any(isinstance(m, ParameterDefinitionMapping) for m in self._component_mappings):
            return "Definition"
        return "None"

    @property
    def value_type_label(self):
        if not self.mapping_has_values():
            return "None"
        m = self.value_mapping
        if isinstance(m, (ParameterValueTypeMapping, ParameterValueMapping)):
            return "Value"
        return "Default value"

    @property
    def value_type(self):
        if not self.mapping_has_values():
            return None
        m = self.value_mapping
        if isinstance(m, (ParameterDefaultValueTypeMapping, ParameterValueTypeMapping)):
            return DISPLAY_VALUE_TYPES.get(m.value, "Single value")
        return "Single value"

    def is_time_series_value(self):
        return self.value_type == "Time series"

    def is_map_value(self):
        return self.value_type == "Map"

    def map_dimension_count(self):
        if not self.is_map_value():
            return 1
        parameter_type = self.parameter_type
        index_mapping = ParameterValueIndexMapping if parameter_type == "Value" else ParameterDefaultValueIndexMapping
        return len([m for m in self._component_mappings if isinstance(m, index_mapping)])

    def mapping_has_dimensions(self):
        return isinstance(self._root_mapping, RelationshipClassMapping)

    def mapping_has_parameters(self):
        """Returns True if the item mapping has parameters."""
        return self.map_type in (MappingType.ObjectClass, MappingType.ObjectGroup, MappingType.RelationshipClass)

    def mapping_has_values(self):
        """Returns True if the parameter mapping has values."""
        return self.value_mapping is not None

    @property
    def is_pivoted(self):
        if self._root_mapping:
            return self._root_mapping.is_pivoted()
        return False

    @property
    def read_start_row(self):
        if self._root_mapping:
            return self._root_mapping.read_start_row
        return 0

    def set_read_start_row(self, row):
        if self._root_mapping:
            self._root_mapping.read_start_row = row
            self.mapping_read_start_row_changed.emit(row)

    def set_import_objects(self, flag):
        for m in self._import_objects_mappings():
            m.import_objects = bool(flag)

    def set_mapping(self, mapping):
        if not isinstance(mapping, ImportMapping):
            raise TypeError(f"mapping must be an instance of ImportMapping, instead got {type(mapping).__name__}")
        self.beginResetModel()
        self._root_mapping = mapping
        self.update_display_table()
        self.endResetModel()

    def mapping_dimension_count(self):
        return len([m for m in self._component_mappings if isinstance(m, RelationshipClassObjectClassMapping)])

    def last_object_class_mapping(self):
        return next(m for m in reversed(self._component_mappings) if isinstance(m, RelationshipClassObjectClassMapping))

    def last_object_mapping(self):
        return next(m for m in reversed(self._component_mappings) if isinstance(m, RelationshipObjectMapping))

    def set_dimension_count(self, dimension_count):
        if not self.mapping_has_dimensions():
            return None, None
        curr_dimension_count = self.mapping_dimension_count()
        if curr_dimension_count == dimension_count:
            return None, None
        last_cls_mapping = self.last_object_class_mapping()
        last_obj_mapping = self.last_object_mapping()
        last_cls_mapping_child = last_cls_mapping.child
        last_obj_mapping_child = last_obj_mapping.child
        removed_cls_mappings = []
        removed_obj_mappings = []
        self.beginResetModel()
        if dimension_count > curr_dimension_count:
            for _ in range(curr_dimension_count, dimension_count):
                last_cls_mapping.child = RelationshipClassObjectClassMapping(Position.hidden)
                last_cls_mapping = last_cls_mapping.child
                last_obj_mapping.child = RelationshipObjectMapping(Position.hidden)
                last_obj_mapping = last_obj_mapping.child
        else:
            for _ in range(dimension_count, curr_dimension_count):
                removed_cls_mappings.insert(0, last_cls_mapping)
                removed_obj_mappings.insert(0, last_obj_mapping)
                last_cls_mapping = last_cls_mapping.parent
                last_obj_mapping = last_obj_mapping.parent
        last_cls_mapping.child = last_cls_mapping_child
        last_obj_mapping.child = last_obj_mapping_child
        self.update_display_table()
        self.endResetModel()
        return removed_cls_mappings, removed_obj_mappings

    def restore_relationship_mappings(self, cls_mappings, obj_mappings):
        if not self.mapping_has_dimensions():
            return
        if not cls_mappings and not obj_mappings:
            return
        last_cls_mapping = self.last_object_class_mapping()
        last_obj_mapping = self.last_object_mapping()
        last_cls_mapping_child = last_cls_mapping.child
        last_obj_mapping_child = last_obj_mapping.child
        self.beginResetModel()
        for m in cls_mappings:
            last_cls_mapping.child = m
            last_cls_mapping = m
        for m in obj_mappings:
            last_obj_mapping.child = m
            last_obj_mapping = m
        last_cls_mapping.child = last_cls_mapping_child
        last_obj_mapping.child = last_obj_mapping_child
        self.update_display_table()
        self.endResetModel()

    def change_item_mapping_type(self, new_type):
        """
        Change item mapping's type.

        Args:
            new_type (str): name of the type
        """
        self.beginResetModel()
        map_type = {
            "Object class": "ObjectClass",
            "Relationship class": "RelationshipClass",
            "Object group": "ObjectGroup",
            "Alternative": "Alternative",
            "Scenario": "Scenario",
            "Scenario alternative": "ScenarioAlternative",
            "Parameter value list": "ParameterValueList",
            "Feature": "Feature",
            "Tool": "Tool",
            "Tool feature": "ToolFeature",
            "Tool feature method": "ToolFeatureMethod",
        }[new_type]
        self._root_mapping = import_mapping_from_dict({"map_type": map_type})
        # FIXME MAYBE: try to recycle fields from one mapping to another
        self.update_display_table()
        self.endResetModel()

    def change_parameter_type(self, new_type):
        """
        Change parameter type
        """
        if new_type == "None":
            new_param_def_mapping = None
        elif new_type == "Value":
            new_param_def_mapping = parameter_mapping_from_dict({"map_type": "ParameterValue"})
        elif new_type == "Definition":
            new_param_def_mapping = parameter_mapping_from_dict({"map_type": "ParameterDefinition"})
        self.beginResetModel()
        self.parameter_mapping = new_param_def_mapping
        self.update_display_table()
        self.endResetModel()

    def change_value_type(self, new_type):
        """
        Change value type
        """
        if not self.mapping_has_values():
            return
        self.beginResetModel()
        if new_type == "None":
            self.value_mapping = None
        else:
            value_type = VALUE_TYPES[new_type]
            if self.parameter_type == "Definition":
                self.value_mapping = parameter_default_value_mapping_from_dict({"value_type": value_type})
            elif self.parameter_type == "Value":
                self.value_mapping = parameter_value_mapping_from_dict({"value_type": value_type})
        self.update_display_table()
        self.endResetModel()

    def set_parameter_mapping(self, mapping):
        """
        Changes the parameter mapping.

        Args:
            mapping (ParameterDefinitionMapping): new mapping
        """
        self.beginResetModel()
        self.parameter_mapping = mapping
        self.update_display_table()
        self.endResetModel()

    def _component_name_from_type(self, component_type):
        if self.map_type == MappingType.ObjectGroup and component_type == "Object":
            return "Group names"
        if self.value_type == "Array" and component_type in ("ParameterValueIndex", "ParameterDefaultValueIndex"):
            return None
        return DISPLAY_MAPPING_NAMES[component_type]

    def _update_component_mappings(self):
        self._component_mappings = self._root_mapping.flatten()
        self._component_names = [self._component_name_from_type(m.MAP_TYPE) for m in self._component_mappings]
        self._logical_row.clear()
        display_row = 0
        invalid_rows = []
        for logical_row, name in enumerate(self._component_names):
            if name is None:
                invalid_rows.append(logical_row)
                continue
            self._logical_row[display_row] = logical_row
            display_row += 1
        for row in reversed(invalid_rows):
            self._component_names.pop(row)
        self._component_names = fix_name_ambiguity(self._component_names, prefix=" ")
        self._colors = self._make_colors()
        self._row_issues = None  # Force recomputing the issues

    def update_display_table(self):
        self._update_component_mappings()
        QTimer.singleShot(0, self.mapping_changed)

    def _make_colors(self):
        component_count = len(self._component_names)
        return [color_from_index(i, component_count).lighter() for i in range(component_count)]

    def get_map_type_display(self, mapping, name):
        if name.endswith("values") and self._root_mapping.is_pivoted():
            return "Pivoted"
        if mapping.position == Position.hidden:
            if mapping.value is None:
                return "None"
            return "Constant"
        if mapping.position == Position.header:
            if mapping.value is None:
                return "Headers"
            return "Column Header"
        if mapping.position == Position.table_name:
            return "Table Name"
        if mapping.position >= 0:
            return "Column"
        return "Row"

    def get_map_reference_display(self, mapping, name):
        # A) Handle two special cases for value mappings
        if name.endswith("values"):
            if self._root_mapping.is_pivoted():
                # 1. Pivoted values
                return "Pivoted values"
            if mapping.position == Position.hidden and mapping.value is not None:
                # 2. Constant value: we want special database value support
                try:
                    value = from_database(*split_value_and_type(mapping.value))
                    return SpineDBManager.display_data_from_parsed(value)
                except ParameterValueFormatError:
                    return None
        # B) Handle all other cases cases
        if mapping.position == Position.hidden:
            if name.endswith("flags") and not isinstance(mapping.value, bool):
                return bool(strtobool(mapping.value))
            return mapping.value
        if mapping.position == Position.header:
            if mapping.value is None:
                return "Headers"
            return mapping.value + 1
        if mapping.position == Position.table_name:
            return self.source_table_name
        if mapping.position >= 0:
            return mapping.position + 1
        return -(mapping.position + 1) + 1

    def data(self, index, role=Qt.DisplayRole):
        if role == PARSED_ROLE:
            # Only used for the ParameterValueEditor.
            # At this point, the delegate has already checked that it's a constant parameter (default) value mapping
            m = self._component_mappings[self._logical_row[index.row()]]
            try:
                return from_database(*split_value_and_type(m.value))
            except ParameterValueFormatError:
                return None
        column = index.column()
        if role in (Qt.DisplayRole, Qt.EditRole):
            name = self._component_names[index.row()]
            if column == 0:
                return name
            m = self._component_mappings[self._logical_row[index.row()]]
            if column == 1:
                return self.get_map_type_display(m, name)
            if column == 2:
                return self.get_map_reference_display(m, name)
            raise RuntimeError("Column out of bounds.")
        if role == Qt.BackgroundRole and column == 0:
            return self.get_color(index.row())
        if column == 2:
            if role == Qt.BackgroundRole:
                row = self._logical_row[index.row()]
                issues = self._get_row_issues().get(row)
                if issues is not None:
                    return ERROR_COLOR
                return None
            if role == Qt.ToolTipRole:
                row = self._logical_row[index.row()]
                issues = self._get_row_issues().get(row)
                if issues is not None:
                    return issues
                return None

    def get_component_mapping(self, visual_row):
        return self._component_mappings[self._logical_row[visual_row]]

    def get_color(self, visual_row):
        return self._colors[visual_row]

    def data_color(self, component_name):
        # FIXME: used only in tests
        visual_row = self._visual_row_from_component_name(component_name)
        return self._colors[visual_row]

    def get_value_color(self):
        row = next((k for k, name in enumerate(self._component_names) if name.endswith("values")), None)
        if row is None:
            return None
        return self._colors[row]

    def _get_row_issues(self):
        if self._row_issues is None:
            self._row_issues = {}
            for issue in check_validity(self._root_mapping):
                self._row_issues.setdefault(issue.rank, []).append(issue.msg)
        return self._row_issues

    def _is_optional(self, component_name):
        if component_name.endswith("metadata"):
            return True
        if component_name.startswith("Object names"):
            return not self.mapping_has_values()
        if component_name == "Alternative names":
            return self.map_type not in (MappingType.Alternative, MappingType.ScenarioAlternative)
        return False

    def rowCount(self, index=None):
        if not self._root_mapping:
            return 0
        return len(self._component_names)

    def columnCount(self, index=None):
        if not self._root_mapping:
            return 0
        return 3

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return ["Target", "Source type", "Source ref."][section]

    def flags(self, index):
        editable = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        non_editable = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if index.column() == 0:
            return non_editable
        mapping = self._component_mappings[self._logical_row[index.row()]]

        if self._root_mapping.is_pivoted():
            # special case where we have pivoted data, the values are columns under pivoted indexes
            if self._component_names[index.row()].endswith("values"):
                return non_editable

        if mapping.position == Position.hidden and mapping.value is None:
            if index.column() <= 2:
                return editable
            return non_editable

        if isinstance(mapping, str):
            if index.column() <= 2:
                return editable
            return non_editable
        if mapping.position == Position.header and mapping.value is None:
            if index.column() == 2:
                return non_editable
            return editable
        return editable

    def setData(self, index, value, role=Qt.DisplayRole):
        column = index.column()
        if column not in (1, 2):
            return False
        row = index.row()
        name = self._component_names[row]
        current_type = self.index(row, 1).data()
        current_reference = self.index(row, 2).data()
        if column == 1:
            self._undo_stack.push(SetComponentMappingType(name, self, value, current_type, current_reference))
            return False
        if current_type != "None":
            self._undo_stack.push(
                SetComponentMappingReference(name, self, current_type, value, current_type, current_reference)
            )
            return False
        # If type is "None", set it to something reasonable to try and help users
        try:
            value = int(value)
        except ValueError:
            pass
        if isinstance(value, int):
            self.change_component_mapping(name, "Column", value)
        elif isinstance(value, str):
            self.change_component_mapping(name, "Constant", value)
        return False

    def change_component_mapping(self, component_name, new_type, new_ref):
        """
        Pushes :class:`SetComponentMappingType` to the undo stack.

        Args:
            component_name (str): name of the component whose type to change
            new_type (str): name of the new type
            new_ref (str or int): component mapping reference
        """
        row = self._visual_row_from_component_name(component_name)
        previous_type = self.index(row, 1).data()
        previous_ref = self.index(row, 2).data()
        type_cmd = SetComponentMappingType(component_name, self, new_type, previous_type, previous_ref)
        ref_cmd = SetComponentMappingReference(component_name, self, new_type, new_ref, previous_type, previous_ref)
        if type_cmd.isObsolete() and ref_cmd.isObsolete():
            return
        self._undo_stack.beginMacro("mapping type and reference change")
        self._undo_stack.push(type_cmd)
        self._undo_stack.push(ref_cmd)
        self._undo_stack.endMacro()

    def set_type(self, name, new_type):
        """
        Changes the type of a component mapping.

        Args:
            name (str): component name
            new_type (str): mapping type name
        """
        self.about_to_undo.emit(self._table_name, self._mapping_name)
        mapping = self._get_component_mapping_from_name(name)
        if new_type in ("None", "", None):
            mapping.position = Position.hidden
            mapping.value = None
        elif new_type == "Constant":
            mapping.position = Position.hidden
            mapping.value = "constant"
        elif new_type == "Column":
            mapping.position = 0
            mapping.value = None
        elif new_type == "Column Header":
            mapping.position = Position.header
            mapping.value = 0
        elif new_type == "Headers":
            mapping.position = Position.header
            mapping.value = None
        elif new_type == "Row":
            mapping.position = -1
            mapping.value = None
        elif new_type == "Table Name":
            mapping.position = Position.table_name
        self._set_component_mapping_from_name(name, mapping)

    def set_reference(self, name, type_, ref):
        """
        Sets the reference for given mapping.

        Args:
            name (str): name of the mapping
            type_ (str): type of the mapping
            ref (int, str): a new ref

        Returns:
            bool: True if the reference was modified successfully, False otherwise.
        """
        self.about_to_undo.emit(self._table_name, self._mapping_name)
        mapping = self._get_component_mapping_from_name(name)
        if type_ == "Constant":
            mapping.value = ref
        elif type_ == "Column":
            mapping.position = ref - 1
        elif type_ == "Column Header":
            mapping.value = ref - 1
        elif type_ == "Row":
            mapping.position = -ref
        self._set_component_mapping_from_name(name, mapping)
        self._recommend_types(name, mapping)

    def _visual_row_from_component_name(self, name):
        return self._component_names.index(name)

    def _logical_row_from_component_name(self, name):
        return self._logical_row[self._visual_row_from_component_name(name)]

    def _get_component_mapping_from_name(self, name):
        if not self._root_mapping:
            return None
        row = self._visual_row_from_component_name(name)
        return self._component_mappings[self._logical_row[row]]

    def _set_component_mapping_from_name(self, name, mapping):
        if not self._root_mapping:
            return
        row = self._logical_row_from_component_name(name)
        top_left = self.index(row, 1)
        bottom_right = self.index(self.rowCount() - 1, 2)
        self._row_issues = None  # Force recomputing the issues
        self.dataChanged.emit(top_left, bottom_right, [Qt.BackgroundRole, Qt.DisplayRole, Qt.ToolTipRole])

    def _recommend_types(self, name, mapping):
        self._recommend_float_type_for_values()
        if name.endswith("indexes") and self.is_time_series_value():
            self._recommend_date_time_type(mapping)
        elif not name.endswith("values"):
            self._recommend_string_type(mapping)
        self.mapping_changed.emit()

    def _recommend_float_type_for_values(self):
        if not self.mapping_has_values():
            return
        visual_row = next((k for k, m in enumerate(self._component_names) if m.endswith("values")), None)
        if visual_row is None:
            return
        logical_row = self._logical_row[visual_row]
        mapping = self._component_mappings[logical_row]
        if not self._root_mapping.is_pivoted():
            self._recommend_float_type(mapping)
            return
        excluded_columns = self._root_mapping.non_pivoted_columns()
        self.multi_column_type_recommended.emit(excluded_columns, FloatConvertSpec())

    def _recommend_string_type(self, mapping):
        self._recommend_type(mapping, StringConvertSpec())

    def _recommend_float_type(self, mapping):
        self._recommend_type(mapping, FloatConvertSpec())

    def _recommend_date_time_type(self, mapping):
        self._recommend_type(mapping, DateTimeConvertSpec())

    def _recommend_type(self, mapping, convert_spec):
        if not isinstance(mapping.position, int):
            return
        if mapping.position >= 0:
            self.row_or_column_type_recommended.emit(mapping.position, convert_spec, Qt.Horizontal)
        else:
            self.row_or_column_type_recommended.emit(-(mapping.position + 1), convert_spec, Qt.Vertical)

    def set_skip_columns(self, columns=None):
        previous_skip_columns = self._root_mapping.skip_columns
        if columns is None:
            columns = []
        self._root_mapping.skip_columns = list(set(columns))
        if previous_skip_columns:
            if columns:
                min_column = min(min(previous_skip_columns), min(columns))
                max_column = max(max(previous_skip_columns), max(columns))
            else:
                min_column = min(previous_skip_columns)
                max_column = max(previous_skip_columns)
        else:
            if columns:
                min_column = min(columns)
                max_column = max(columns)
            else:
                return
        top_left = self.index(min_column, 0)
        bottom_right = self.index(max_column, self.rowCount() - 1)
        self.dataChanged.emit(top_left, bottom_right, [Qt.BackgroundRole])

    def set_time_series_repeat(self, repeat):
        """Toggles the repeat flag in the parameter's options."""
        if self._root_mapping is None:
            return
        if not self.is_time_series_value():
            return
        self.value_mapping.options["repeat"] = repeat

    def set_map_dimension_count(self, dimension_count):
        if self._root_mapping is None:
            return
        if not self.is_map_value():
            return
        previous_dimension_count = self.map_dimension_count()
        if dimension_count == previous_dimension_count:
            return
        name_mapping_cls = IndexNameMapping if self.parameter_type == "Value" else DefaultValueIndexNameMapping
        index_mapping_cls = (
            ParameterValueIndexMapping if self.parameter_type == "Value" else ParameterDefaultValueIndexMapping
        )
        last_index_mapping = next(m for m in reversed(self._component_mappings) if isinstance(m, index_mapping_cls))
        last_index_mapping_child = last_index_mapping.child
        removed_mappings = []
        self.beginResetModel()
        if dimension_count > previous_dimension_count:
            for _ in range(previous_dimension_count, dimension_count):
                name_mapping = name_mapping_cls(Position.hidden)
                last_index_mapping.child = name_mapping
                index_mapping = index_mapping_cls(Position.hidden)
                name_mapping.child = index_mapping
                last_index_mapping = index_mapping
        else:
            for _ in range(dimension_count, previous_dimension_count):
                removed_mappings.insert(0, last_index_mapping)
                name_mapping = last_index_mapping.parent
                removed_mappings.insert(0, name_mapping)
                last_index_mapping = name_mapping.parent
        last_index_mapping.child = last_index_mapping_child
        self.update_display_table()
        self.endResetModel()
        return removed_mappings

    def restore_index_mappings(self, mappings):
        if self._root_mapping is None:
            return
        if not self.is_map_value():
            return
        if not mappings:
            return
        factory = ParameterValueIndexMapping if self.parameter_type == "Value" else ParameterDefaultValueIndexMapping
        last_index_mapping = next(m for m in reversed(self._component_mappings) if isinstance(m, factory))
        last_index_mapping_child = last_index_mapping.child
        self.beginResetModel()
        for m in mappings:
            last_index_mapping.child = m
            last_index_mapping = m
        last_index_mapping.child = last_index_mapping_child
        self.update_display_table()
        self.endResetModel()

    def set_map_compress_flag(self, compress):
        """
        Sets the compress flag for Map type parameters.

        Args:
            compress (bool): flag value
        """
        if self._root_mapping is None or not self.is_map_value():
            return
        self.value_mapping.compress = compress

    def to_dict(self):
        """
        Serializes the mapping specification into a dict.

        Returns:
            dict: serialized specification
        """
        return unparse_named_mapping_spec(self._mapping_name, self._root_mapping)

    @staticmethod
    def from_dict(named_mapping_spec, table_name, undo_stack):
        """
        Restores a serialized mapping specification.

        Args:
            named_mapping_spec (dict): keys are mapping names, values are specs
            table_name (str): source table name
            undo_stack (QUndoStack): undo stack

        Returns:
            MappingSpecificationModel: mapping specification
        """
        name, mapping = parse_named_mapping_spec(named_mapping_spec)
        mapping = _insert_index_name_mappings(mapping)
        return MappingSpecificationModel(table_name, name, mapping, undo_stack)

    def duplicate(self, table_name, undo_stack):
        return self.from_dict(self.to_dict(), table_name, undo_stack)

    def get_set_data_delayed(self, index):
        """Returns a function that ParameterValueEditor can call to set data for the given index at any later time,
        even if the model changes.

        Args:
            index (QModelIndex)

        Returns:
            function
        """
        return lambda value_type_tup, index=index: self.setData(index, join_value_and_type(*value_type_tup))

    def index_name(self, index):
        return index.siblingAtColumn(0).data()


def _insert_index_name_mappings(mapping):
    """Inserts index name mappings if they are missing.

    This fixes some legacy mappings.

    Args:
        mapping (ImportMapping): root mapping

    Returns:
        ImportMapping: fixed mapping
    """
    flattened = mapping.flatten()
    if any(isinstance(m, (ParameterDefaultValueIndexMapping, ParameterValueIndexMapping)) for m in flattened) and all(
        not isinstance(m, (DefaultValueIndexNameMapping, IndexNameMapping)) for m in flattened
    ):
        fixed = list()
        for m in flattened:
            if isinstance(m, ParameterDefaultValueIndexMapping):
                fixed.append(DefaultValueIndexNameMapping(Position.hidden))
            elif isinstance(m, ParameterValueIndexMapping):
                fixed.append(IndexNameMapping(Position.hidden))
            fixed.append(m)
        mapping = unflatten(fixed)
    return mapping
