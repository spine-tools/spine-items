######################################################################################################################
# Copyright (C) 2017-2021 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Exporter's execute kernel (do_work), as target for a multiprocess.Process

:authors: A. Soininen (VTT)
:date:    14.12.2020
"""
from copy import copy
from pathlib import Path
from spinedb_api.spine_io.exporters.writer import write, WriterException
from spinedb_api.spine_io.exporters.csv_writer import CsvWriter
from spinedb_api.spine_io.exporters.excel_writer import ExcelWriter
from spinedb_api import clear_filter_configs, DatabaseMapping, SpineDBAPIError
from spine_items.utils import subdirectory_for_fork
from .specification import Specification, OutputFormat


def do_work(specification, output_time_stamps, cancel_on_error, out_dir, databases, forks, logger):
    """
    Exports databases using given specification as export mapping.

    Args:
        specification (dict): export specification dictionary
        output_time_stamps (bool): if True, puts output files into time stamped subdirectories
        cancel_on_error (bool): if True, bails out on non-fatal errors
        out_dir (str): base output directory
        databases (dict): databases to export
        forks (dict): mapping from base database URL to a set of fork names
        logger (LoggerInterface): a logger

    Returns:
        tuple: boolean success flag, dictionary of output files
    """
    specification = Specification.from_dict(specification)
    successes = list()
    written_files = dict()
    for url, output_file_name in databases.items():
        out_path = subdirectory_for_fork(
            output_file_name, out_dir, output_time_stamps, forks[clear_filter_configs(url)]
        )
        try:
            database_map = DatabaseMapping(url)
        except SpineDBAPIError as error:
            logger.msg_error.emit(f"Failed to export <b>{url}</b>: {error}")
            if cancel_on_error:
                return False, written_files
            successes.append(False)
            continue
        try:
            try:
                file = Path(out_path)
                file.parent.mkdir(parents=True, exist_ok=True)
                if file.exists():
                    file.unlink()
                writer = make_writer(specification.output_format, out_path)
                for mapping_specification in specification.mapping_specifications().values():
                    mapping = copy(mapping_specification.root)
                    mapping.drop_non_positioned_tail()
                    write(database_map, writer, mapping)
            except (PermissionError, WriterException) as e:
                logger.msg_error.emit(str(e))
                if cancel_on_error:
                    return False, written_files
                successes.append(False)
            else:
                if isinstance(writer, CsvWriter):
                    files = writer.output_files()
                else:
                    files = [out_path]
                written_files[output_file_name] = files
                if len(files) > 1:
                    anchors = list()
                    for path in (Path(f) for f in files):
                        anchors.append(
                            f"<a style='color:#BB99FF;' title='{path}' href='file:///{path}'>{path.name}</a>"
                        )
                    logger.msg_success.emit(f"Wrote multiple files:<br>{'<br>'.join(anchors)}")
                else:
                    file_anchor = f"<a style='color:#BB99FF;' title='{file}' href='file:///{file}'>{file.name}</a>"
                    logger.msg_success.emit(f"File {file_anchor} written.")
                successes.append(True)
        finally:
            database_map.connection.close()
    return all(successes), written_files


def make_writer(output_format, out_path):
    """
    Constructs a writer.

    Args:
        output_format (OutputFormat): output format
        out_path (str): path to output file.

    Returns:
        Writer: a writer
    """
    if output_format == OutputFormat.CSV:
        path = Path(out_path)
        return CsvWriter(path.parent, path.name)
    return ExcelWriter(out_path)
