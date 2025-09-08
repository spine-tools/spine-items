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
import multiprocessing
from unittest import mock
from spine_engine.project_item.project_item_resource import file_resource
from spine_items.importer.do_work import do_work
from spinedb_api import from_database
from spinedb_api.spine_db_client import SpineDBClient
from spinedb_api.spine_db_server import closing_spine_db_server
from spinedb_api.spine_io.importers.csv_reader import CSVReader


class MaybeIdle:
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class MockProcess:
    def __init__(self):
        self.maybe_idle = MaybeIdle()


class TestDoWork:
    def test_fixed_position_mapping_with_two_files(self, tmp_path):
        log_dir = tmp_path / "log"
        log_dir.mkdir()
        file_path_1 = tmp_path / "file1.csv"
        file_path_2 = tmp_path / "file2.csv"
        with open(file_path_1, "w") as out_file:
            out_file.writelines(["data1"])
        with open(file_path_2, "w") as out_file:
            out_file.writelines(["data2"])
        process = MockProcess()
        mapping = {
            "table_mappings": {
                "data": [
                    {
                        "Mapping 1": {
                            "mapping": [
                                {"map_type": "ParameterValueList", "position": "hidden", "value": "enum"},
                                {"map_type": "ParameterValueListValue", "position": "fixed", "value": "data: 0, 0"},
                            ]
                        }
                    }
                ]
            },
            "selected_tables": ["data"],
            "table_options": {
                "data": {
                    "skip": 0,
                    "encoding": "ascii",
                    "delimiter_custom": None,
                    "quotechar": '"',
                    "has_header": False,
                }
            },
            "table_types": {
                "data": {
                    "0": "string",
                }
            },
            "table_default_column_type": {},
            "table_row_types": {},
            "source_type": "CSVReader",
        }
        resources = [file_resource("provider item", str(file_path_1)), file_resource("provider item", str(file_path_2))]
        lock = multiprocessing.RLock()
        logger = mock.MagicMock()
        with closing_spine_db_server("sqlite://") as server_url:
            result = do_work(
                process, mapping, True, "merge", str(log_dir), resources, CSVReader(None), [server_url], lock, logger
            )
            assert result == (True,)
            client = SpineDBClient.from_server_url(server_url)
            result = client.call_method("find_list_values", parameter_value_list_name="enum")
            assert len(result["result"]) == 2
            assert from_database(result["result"][0]["value"], result["result"][0]["type"]) == "data1"
            assert from_database(result["result"][1]["value"], result["result"][1]["type"]) == "data2"
