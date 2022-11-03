######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Contains the :class:`Exporter` project item.

:authors: A. Soininen (VTT)
:date:    10.12.2020
"""
from dataclasses import dataclass
from itertools import combinations, zip_longest
from pathlib import Path

from PySide2.QtCore import Slot, Qt
from spinetoolbox.project_item.project_item import ProjectItem
from spine_engine.utils.serialization import deserialize_path
from spinedb_api import clear_filter_configs
from .export_manifest import exported_files_as_resources
from ..utils import EXPORTER_EXECUTION_MANIFEST_FILE_PREFIX
from ..item_base import ExporterBase
from .widgets.export_list_item import ExportListItem
from .item_info import ItemInfo
from .executable_item import ExecutableItem
from .commands import UpdateOutLabel
from .output_channel import OutputChannel


@dataclass
class _Notifications:
    """Holds flags for different exporter error conditions."""

    duplicate_out_label: bool = False
    missing_out_label: bool = False
    missing_specification: bool = False


class Exporter(ExporterBase):
    """Exporter project item."""

    def __init__(
        self,
        name,
        description,
        x,
        y,
        toolbox,
        project,
        specification_name=None,
        output_channels=None,
        output_time_stamps=False,
        cancel_on_error=True,
    ):
        """
        Args:
            name (str): item's name
            description (str): item's description
            x (float): Initial X coordinate of item icon
            y (float): Initial Y coordinate of item icon
            toolbox (QWidget): parent window
            project (SpineToolboxProject): the project this item belongs to
            specification_name (str, optional): exporter specification
            output_channels (list of OutputChannel, optional): input and output labels
            output_time_stamps (bool): True to include time stamps to output directory names
            cancel_on_error (bool): True to fail execution in case of non-fatal errors
        """
        super().__init__(name, description, x, y, toolbox, project, output_time_stamps, cancel_on_error)
        self._notifications = _Notifications()
        self._output_channels = []
        if output_channels is None:
            output_channels = []
        self._inactive_output_channels = output_channels
        self._specification_name = specification_name
        self._specification = self._project.get_specification(specification_name)
        if specification_name and not self._specification:
            self._toolbox.msg_error.emit(
                f"Exporter <b>{self.name}</b> should have a specification <b>{specification_name}</b> but it was not found"
            )
        self.do_set_specification(self._specification)

    @staticmethod
    def item_type():
        """See base class."""
        return ItemInfo.item_type()

    @staticmethod
    def item_category():
        """See base class."""
        return ItemInfo.item_category()

    @property
    def executable_class(self):
        return ExecutableItem

    def _update_properties_tab(self):
        """Updates the labels list in the properties tab."""
        outputs_layout = self._properties_ui.outputs_list_layout
        while not outputs_layout.isEmpty():
            widget_to_remove = outputs_layout.takeAt(0)
            widget_to_remove.widget().deleteLater()
        self._export_list_items.clear()
        for channel in self._output_channels:
            item = self._export_list_items[channel.in_label] = ExportListItem(channel.in_label, channel.out_label)
            outputs_layout.addWidget(item)
            item.out_label_changed.connect(self._update_out_label)
        self._properties_ui.output_time_stamps_check_box.setCheckState(
            Qt.Checked if self._append_output_time_stamps else Qt.Unchecked
        )
        self._properties_ui.cancel_on_error_check_box.setCheckState(
            Qt.Checked if self._cancel_on_error else Qt.Unchecked
        )

    def upstream_resources_updated(self, resources):
        """See base class."""
        database_resources = [r for r in resources if r.type_ == "database"]
        resources_by_labels = {r.label: r for r in database_resources}  # legacy: when in_label was url
        in_labels = set(r.label for r in database_resources)
        inactive_channels = {c.in_label: c for c in self._output_channels}
        old_output_channels = self._output_channels
        self._output_channels = []
        inactive_channels.update({c.in_label: c for c in self._inactive_output_channels})
        for in_label in in_labels:
            inactive = inactive_channels.pop(in_label, None)
            if inactive is not None:
                self._output_channels.append(inactive)
            else:
                url = clear_filter_configs(resources_by_labels[in_label].url)
                if url in inactive_channels:
                    # legacy: when in_label was url
                    # we actually have out_label already
                    inactive = inactive_channels.pop(url)
                    self._output_channels.append(OutputChannel(in_label, inactive.out_label))
                else:
                    self._output_channels.append(OutputChannel(in_label))
        self._inactive_output_channels = list(inactive_channels.values())
        self._full_url_model.set_urls(set(r.url for r in database_resources))
        if self._output_channels != old_output_channels:
            self._resources_to_successors_changed()
        if self._active:
            self._update_properties_tab()
        self._check_notifications()

    def replace_resources_from_upstream(self, old, new):
        """See base class."""
        for old_resource, new_resource in zip(old, new):
            if old_resource.type_ != "database":
                continue
            for channel in self._output_channels:
                if channel.in_label == old_resource.label:
                    channel.in_label = new_resource.label
                    break
            self._full_url_model.update_url(old_resource.url, new_resource.url)

    def _check_notifications(self):
        """See base class."""
        self._check_missing_out_labels()
        self._check_duplicate_out_labels()
        self._check_missing_specification()
        self._report_notifications()

    def _report_notifications(self):
        """Updates the exclamation icon and notifications labels."""
        if self._icon is None:
            return
        self.clear_notifications()
        if self._notifications.duplicate_out_label:
            self.add_notification("Duplicate output labels.")
        if self._notifications.missing_out_label:
            self.add_notification("Output label(s) missing.")
        if self._notifications.missing_specification:
            self.add_notification("Export specification missing.")

    def _check_missing_out_labels(self):
        """Checks the status of out labels"""
        self._notifications.missing_output_file_name = not all(bool(c.out_label) for c in self._output_channels)

    def _check_duplicate_out_labels(self):
        """Checks for duplicate output file names."""
        self._notifications.duplicate_out_label = any(
            c1.out_label == c2.out_label for c1, c2 in combinations(self._output_channels, 2) if c1 and c2
        )

    @Slot(str, str)
    def _update_out_label(self, out_label, in_label):
        """Pushes UpdateOutLabel command to undo stack.

        Args:
            out_label (str): new out label
            in_label (str): associated in label
        """
        previous = next(c for c in self._output_channels if c.in_label == in_label)
        self._toolbox.undo_stack.push(UpdateOutLabel(self, out_label, in_label, previous.out_label))

    def set_out_label(self, out_label, in_label):
        """Updates the output label.

        Args:
            out_label (str): output label
            in_label (str): corresponding input label
        """
        if self._active:
            export_list_item = self._export_list_items[in_label]
            export_list_item.out_label_edit.setText(out_label)
        channel = next(c for c in self._output_channels if c.in_label == in_label)
        old_out_label = channel.out_label
        old_resources = self.resources_for_direct_successors() if old_out_label else []
        channel.out_label = out_label
        self._check_missing_out_labels()
        self._check_duplicate_out_labels()
        self._report_notifications()
        if self._exported_files is not None:
            exported_files = self._exported_files.pop(old_out_label, None)
            if exported_files is not None and out_label:
                self._exported_files[out_label] = exported_files
        if not old_out_label or not out_label:
            self._resources_to_successors_changed()
        else:
            new_resources = self.resources_for_direct_successors()
            olds = [resource for resource in old_resources if resource.label == old_out_label]
            news = [resource for resource in new_resources if resource.label == out_label]
            self._resources_to_successors_replaced(olds, news)

    def item_dict(self):
        """See base class."""
        serialized = super().item_dict()
        serialized["output_labels"] = sorted([c.to_dict() for c in self._output_channels], key=lambda d: d["in_label"])
        serialized["specification"] = self._specification_name
        return serialized

    def resources_for_direct_successors(self):
        """See base class."""
        resources, self._exported_files = exported_files_as_resources(
            self.name, self._exported_files, self.data_dir, self._output_channels
        )
        return resources

    @staticmethod
    def from_dict(name, item_dict, toolbox, project):
        """See base class."""
        description, x, y = ProjectItem.parse_item_dict(item_dict)
        output_channels = [OutputChannel.from_dict(d) for d in item_dict.get("output_labels", [])]
        for db_dict in item_dict.get("databases", []):
            # Legacy item dict.
            out_label = db_dict["output_file_name"]
            url = clear_filter_configs(deserialize_path(db_dict["database_url"], project.project_dir))
            output_channels.append(OutputChannel(url, out_label))
        output_time_stamps = item_dict.get("output_time_stamps", False)
        cancel_on_error = item_dict.get("cancel_on_error", True)
        specification_name = item_dict.get("specification", "")
        specification = project.get_specification(specification_name)
        if specification_name and not specification:
            toolbox.msg_error.emit(f"Exporter <b>{name}</b> specification <b>{specification_name}</b> not found.")
        return Exporter(
            name,
            description,
            x,
            y,
            toolbox,
            project,
            specification_name,
            output_channels,
            output_time_stamps,
            cancel_on_error,
        )

    def rename(self, new_name, rename_data_dir_message):
        """See base class."""
        if not super().rename(new_name, rename_data_dir_message):
            return False
        for path in Path(self.data_dir).iterdir():
            if path.name.startswith(EXPORTER_EXECUTION_MANIFEST_FILE_PREFIX) and path.suffix == ".json":
                path.unlink()
        if self._exported_files is not None:
            data_dir_parts = Path(self.data_dir).parts
            for label, file_list in self._exported_files.items():
                new_file_list = list()
                for file_path in file_list:
                    new_file_path = Path()
                    for old_part, new_part in zip_longest(Path(file_path).parts, data_dir_parts):
                        if new_part is None:
                            new_file_path = new_file_path / old_part
                        else:
                            new_file_path = new_file_path / new_part
                    new_file_list.append(str(new_file_path))
                self._exported_files[label] = new_file_list
        return True

    def make_signal_handler_dict(self):
        """Returns a dictionary of all shared signals and their handlers.
        This is to enable simpler connecting and disconnecting."""
        s = super().make_signal_handler_dict()
        s[self._properties_ui.specification_button.clicked] = self.show_specification_window
        s[self._properties_ui.specification_combo_box.textActivated] = self._change_specification
        return s

    def _check_missing_specification(self):
        """Checks specification's status."""
        self._notifications.missing_specification = not self._specification_name

    def do_set_specification(self, specification):
        """see base class"""
        if not super().do_set_specification(specification):
            return False
        if specification is None:
            if self._active:
                self._properties_ui.specification_combo_box.setCurrentIndex(-1)
            return True
        self._specification_name = specification.name
        self._check_notifications()
        if self._active:
            self._properties_ui.specification_combo_box.setCurrentText(self._specification_name)
        return True

    @Slot(bool)
    def show_specification_window(self, _=True):
        """Opens the settings window."""
        self._toolbox.show_specification_form(self.item_type(), self.specification(), self)

    def notify_destination(self, source_item):
        """See base class."""
        if source_item.item_type() == "Data Store":
            self._toolbox.msg.emit(
                "Link established. You can now export the database in "
                f"<b>{source_item.name}</b> in <b>{self.name}</b>."
            )
        elif source_item.item_type() == "Data Transformer":
            self._toolbox.msg.emit(
                f"Link established. You can now export the database transformed by <b>{source_item.name}</b> "
                f"in <b>{self.name}</b>."
            )
        else:
            super().notify_destination(source_item)

    @Slot(str)
    def _change_specification(self, specification_name):
        """
        Pushes a set specification command to the undo stack.

        Args:
            specification_name (str): new specification name
        """
        specification = self._project.get_specification(specification_name)
        self.set_specification(specification)

    def restore_selections(self):
        """See base class."""
        super().restore_selections()
        if self._specification_name:
            self._properties_ui.specification_combo_box.setCurrentText(self._specification_name)
        else:
            self._properties_ui.specification_combo_box.setCurrentIndex(-1)
