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

"""Unit tests for Exporter project item."""
import os.path
from unittest.mock import MagicMock, NonCallableMagicMock
from PySide6.QtWidgets import QApplication
import pytest
from spine_engine.project_item.project_item_resource import database_resource
from spine_engine.utils.helpers import shorten
from spine_items.data_store.data_store import DataStore
from spine_items.exporter.exporter import Exporter
from spine_items.exporter.exporter_factory import ExporterFactory
from spine_items.exporter.item_info import ItemInfo
from spine_items.exporter.specification import OutputFormat, Specification
from spine_items.utils import UrlDict, database_label
from spinedb_api import create_new_spine_database
from spinetoolbox.project_item.logging_connection import LoggingConnection
from tests.mock_helpers import (
    mock_finish_project_item_construction,
)


@pytest.fixture()
def exporter_and_properties_widget(spine_toolbox_with_project):
    toolbox = spine_toolbox_with_project
    mock_spec_model = toolbox.specification_model = MagicMock()
    mock_spec_model.find_specification.side_effect = lambda name: Specification(name, "spec description")
    factory = ExporterFactory()
    item_dict = {
        "type": "Exporter",
        "description": "item description",
        "specification": "exporter_spec",
        "cancel_on_error": True,
        "x": 0,
        "y": 0,
    }
    exporter = factory.make_item("exporter", item_dict, toolbox, toolbox.project())
    properties_widget = mock_finish_project_item_construction(factory, exporter, toolbox)
    return exporter, properties_widget


@pytest.fixture()
def exporter(exporter_and_properties_widget):
    return exporter_and_properties_widget[0]


@pytest.fixture()
def properties_widget(exporter_and_properties_widget):
    return exporter_and_properties_widget[1]


class TestExporter:
    def test_item_type(self):
        assert Exporter.item_type() == ItemInfo.item_type()

    def test_serialization(self, exporter, spine_toolbox_with_project):
        toolbox = spine_toolbox_with_project
        item_dict = exporter.item_dict()
        deserialized = Exporter.from_dict("new exporter", item_dict, toolbox, toolbox.project())
        assert deserialized.name == "new exporter"
        assert deserialized.description == "item description"

    def test_notify_destination(self, exporter, spine_toolbox_with_project):
        toolbox = spine_toolbox_with_project
        toolbox.msg = MagicMock()
        toolbox.msg_warning = MagicMock()
        source_item = NonCallableMagicMock()
        source_item.name = "source name"
        source_item.item_type = MagicMock(return_value="Data Connection")
        exporter.notify_destination(source_item)
        exporter.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a <b>Data Connection</b> and a <b>Exporter</b> has not been implemented yet."
        )
        source_item.item_type = MagicMock(return_value="Data Store")
        exporter.notify_destination(source_item)
        toolbox.msg.emit.assert_called_with(
            "Link established. You can now export the database in <b>source name</b> in <b>exporter</b>."
        )
        source_item.item_type = MagicMock(return_value="Data Transformer")
        exporter.notify_destination(source_item)
        toolbox.msg.emit.assert_called_with(
            "Link established. You can now export the database transformed by <b>source name</b> in <b>exporter</b>."
        )
        source_item.item_type = MagicMock(return_value="Exporter")
        exporter.notify_destination(source_item)
        exporter.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a <b>Exporter</b> and a <b>Exporter</b> has not been implemented yet."
        )
        source_item.item_type = MagicMock(return_value="Importer")
        exporter.notify_destination(source_item)
        exporter.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a <b>Importer</b> and a <b>Exporter</b> has not been implemented yet."
        )
        source_item.item_type = MagicMock(return_value="Tool")
        exporter.notify_destination(source_item)
        exporter.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a <b>Tool</b> and a <b>Exporter</b> has not been implemented yet."
        )
        source_item.item_type = MagicMock(return_value="View")
        exporter.notify_destination(source_item)
        exporter.logger.msg_warning.emit.assert_called_with(
            "Link established. Interaction between a <b>View</b> and a <b>Exporter</b> has not been implemented yet."
        )

    def test_rename(self, exporter, spine_toolbox_with_project):
        """Tests renaming an Importer."""
        exporter.activate()
        expected_name = "ABC"
        expected_short_name = shorten(expected_name)
        assert exporter.rename(expected_name, "")
        assert expected_name == exporter.name
        assert expected_name == exporter.get_icon().name()
        expected_data_dir = os.path.join(spine_toolbox_with_project.project().items_dir, expected_short_name)
        assert expected_data_dir == exporter.data_dir

    def test_upstream_resources_updated(self, exporter):
        exporter.activate()
        expected_out_labels = ["db_url@Data Store 1", "db_url@Data Store 2"]
        resources = [database_resource("provider", url) for url in expected_out_labels]
        exporter.upstream_resources_updated(resources)
        model = exporter.full_url_model()
        assert model.rowCount() == len(expected_out_labels)
        assert model.index(0, 0).data() in expected_out_labels
        assert model.index(1, 0).data() in expected_out_labels
        assert exporter._properties_ui.outputs_list_layout.count() == len(expected_out_labels)

    def test_notifications_when_not_configured(self, spine_toolbox_with_project):
        project = spine_toolbox_with_project.project()
        exporter = Exporter("Test exporter", "Exporter for unit testing", 0.0, 0.0, spine_toolbox_with_project, project)
        project.add_item(exporter)
        assert exporter.get_icon().exclamation_icon._notifications == ["Export specification missing."]

    def test_notifications_when_specification_is_set(self, spine_toolbox_with_project):
        toolbox = spine_toolbox_with_project
        project = toolbox.project()
        specification = Specification("Test spec", "Exporter specification for testing")
        project.add_specification(specification)
        exporter = Exporter("Test exporter", "Exporter for unit testing", 0.0, 0.0, toolbox, project, "Test spec")
        project.add_item(exporter)
        assert exporter.get_icon().exclamation_icon._notifications == []

    def test_notifications_when_output_file_name_extension_mismatches_with_specification_output_format(
        self, spine_toolbox_with_project, tmp_path
    ):
        toolbox = spine_toolbox_with_project
        project = toolbox.project()
        url = "sqlite:///" + str(tmp_path / "db.sqlite")
        create_new_spine_database(url)
        url_dict: UrlDict = {"dialect": "sqlite", "database": str(tmp_path / "db.sqlite")}
        data_store = DataStore("Dummy data store", "", 0.0, 0.0, toolbox, project, url_dict)
        project.add_item(data_store)
        while not data_store.is_url_validated():
            QApplication.processEvents()
        specification = Specification("Test spec", "Exporter specification for testing", output_format=OutputFormat.CSV)
        project.add_specification(specification)
        exporter = Exporter("Test exporter", "Exporter for unit testing", 0.0, 0.0, toolbox, project, "Test spec")
        project.add_item(exporter)
        connection = LoggingConnection("Dummy data store", "right", "Test exporter", "left", toolbox=toolbox)
        project.add_connection(connection)
        assert exporter.get_icon().exclamation_icon._notifications == []
        exporter.activate()
        exporter.set_out_label("exported_file.xlsx", database_label("Dummy data store"))
        assert exporter.get_icon().exclamation_icon._notifications == ["File extensions don't match the output format."]
