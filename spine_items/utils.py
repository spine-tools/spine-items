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
Contains utilities shared between project items.

:authors: A. Soininen (VTT)
:date:    1.4.2020
"""

from dataclasses import dataclass
from datetime import datetime
from itertools import dropwhile
import json
import os.path
from pathlib import Path
from time import time
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL, make_url
import spinedb_api
from spinedb_api.filters.scenario_filter import scenario_name_from_dict
from spine_engine.utils.queue_logger import SuppressedMessage
from spine_engine.project_item.project_item_resource import file_resource_in_pack, transient_file_resource


EXPORTED_PATHS_FILE_NAME = ".exported.json"
"""Name of the file that stores exporter's internal state."""
EXPORTER_EXECUTION_MANIFEST_FILE_PREFIX = ".export-manifest"
"""Prefix for the temporary files that exporter's executable uses to communicate output paths."""


def database_label(provider_name):
    """Creates a standardized label for database resources.

    Args:
        provider_name (str): resource provider's name

    Returns:
        str: resource label
    """
    return "db_url@" + provider_name


@dataclass
class Database:
    """
    Database specific export settings.
    """

    url: str = ""
    """Database URL."""
    output_file_name: str = ""
    """Output file name; relative to item's data dir."""

    def to_dict(self):
        """
        Serializes :class:`Database` into a dictionary.

        Returns:
            dict: serialized :class:`Database`
        """
        return {"output_file_name": self.output_file_name}

    @staticmethod
    def from_dict(database_dict):
        """
        Deserializes :class:`Database` from a dictionary.

        Args:
            database_dict (dict): serialized :class:`Database`

        Returns:
            Database: deserialized instance
        """
        db = Database()
        db.output_file_name = database_dict["output_file_name"]
        return db


def subdirectory_for_fork(output_file_name, data_dir, output_time_stamps, filter_id_hash):
    """
    Creates scenario/tool based output directory for forked workflow.

    Args:
        output_file_name (str): file name
        data_dir (str): project item's data directory
        output_time_stamps (bool): True if time stamp data should be included in the output path
        filter_id_hash (str): hashed filter id

    Returns:
        str: absolute output path
    """
    if output_time_stamps:
        stamp = datetime.fromtimestamp(time())
        time_stamp = "run@" + stamp.isoformat(timespec="seconds").replace(":", ".")
    else:
        time_stamp = ""
    if filter_id_hash:
        if time_stamp:
            path = os.path.join(data_dir, filter_id_hash + "_" + time_stamp, output_file_name)
        else:
            path = os.path.join(data_dir, filter_id_hash, output_file_name)
    else:
        path = os.path.join(data_dir, time_stamp, output_file_name)
    return path


def exported_files_as_resources(item_name, exported_files, data_dir, databases):
    """Collects exported files from 'export manifests'.

    Args:
        item_name (str): item's name
        exported_files (dict, optional): item's exported files cache
        data_dir (str): item's data directory
        databases (Iterable of Database): item's upstream databases

    Returns:
        tuple: output resources and updated exported files cache
    """
    manifests = collect_execution_manifests(data_dir)
    if manifests is not None:
        names = {db.output_file_name for db in databases}
        manifests = {
            out_file_name: files
            for out_file_name, files in collect_execution_manifests(data_dir).items()
            if out_file_name in names
        }
        exported_files = {name: [str(Path(data_dir, f)) for f in files] for name, files in manifests.items()}
    resources = list()
    if exported_files is not None:
        for db in databases:
            if db.output_file_name:
                files = {f for f in exported_files.get(db.output_file_name, []) if Path(f).exists()}
                if files:
                    resources = [file_resource_in_pack(item_name, db.output_file_name, f) for f in files]
                else:
                    resources.append(transient_file_resource(item_name, db.output_file_name))
    else:
        for db in databases:
            if db.output_file_name:
                resources.append(transient_file_resource(item_name, db.output_file_name))
    return resources, exported_files


def collect_execution_manifests(data_dir):
    """Collects output file names from export manifest files written by exporter's executable item.

    Args:
        data_dir (str): item's data directory

    Returns:
        dict: mapping from output label to list of file paths, or None if no manifest files were found
    """
    manifests = None
    for path in Path(data_dir).iterdir():
        if path.name.startswith(EXPORTER_EXECUTION_MANIFEST_FILE_PREFIX) and path.suffix == ".json":
            with open(path) as manifest_file:
                manifest = json.load(manifest_file)
            for out_file_name, paths in manifest.items():
                relative_paths = list()
                for file_path in paths:
                    p = Path(file_path)
                    if p.is_absolute():
                        # Legacy manifests had absolute paths
                        try:
                            relative_paths.append(p.relative_to(data_dir))
                        except ValueError:
                            # Project may have been moved to another directory (or system)
                            # so data_dir is differs from manifest file content.
                            # Try resolving the relative path manually.
                            parts = tuple(dropwhile(lambda part: part != "output", p.parts))
                            relative_paths.append(str(Path(*parts)))
                    else:
                        relative_paths.append(file_path)
                if manifests is None:
                    manifests = dict()
                manifests.setdefault(out_file_name, list()).extend(paths)
    return manifests


def convert_to_sqlalchemy_url(urllib_url, item_name="", logger=None):
    """Returns a sqlalchemy url from the url or None if not valid."""
    selections = f"<b>{item_name}</b> selections" if item_name else "selections"
    if logger is None:
        logger = _NoLogger()
    if not urllib_url:
        logger.msg_error.emit(f"No URL specified for <b>{item_name}</b>. Please specify one and try again")
        return None
    try:
        url = {key: value for key, value in urllib_url.items() if value}
        dialect = url.pop("dialect")
        if not dialect:
            logger.msg_error.emit(f"Unable to generate URL from {selections}: invalid dialect {dialect}.")
            return None
        if dialect == "sqlite":
            sa_url = URL("sqlite", **url)  # pylint: disable=unexpected-keyword-arg
        else:
            db_api = spinedb_api.SUPPORTED_DIALECTS[dialect]
            drivername = f"{dialect}+{db_api}"
            sa_url = URL(drivername, **url)  # pylint: disable=unexpected-keyword-arg
    except Exception as e:  # pylint: disable=broad-except
        # This is in case one of the keys has invalid format
        logger.msg_error.emit(f"Unable to generate URL from {selections}: {e}")
        return None
    if not sa_url.database:
        logger.msg_error.emit(f"Unable to generate URL from {selections}: database missing.")
        return None
    # Final check
    try:
        engine = create_engine(sa_url)
        with engine.connect():
            pass
    except Exception as e:  # pylint: disable=broad-except
        logger.msg_error.emit(f"Unable to generate URL from {selections}: {e}")
        return None
    return sa_url


class _NoLogger:
    def __getattr__(self, _name):
        return SuppressedMessage()


def split_url_credentials(url):
    """Pops username and password information from URL.

    Args:
        url (str): a URL

    Returns:
        tuple: URL without credentials and a tuple containing username, password pair
    """
    sa_url = make_url(url)
    connect_args = sa_url.translate_connect_args()
    username = connect_args.pop("username", None)
    password = connect_args.pop("password", None)
    new_sa_url = URL(sa_url.drivername, **connect_args)
    return str(new_sa_url), (username, password)


def unsplit_url_credentials(url, credentials):
    """Inserts username and password into a URL.

    Args:
        url (str): a URL
        credentials (tuple of str): username, password pair

    Returns:
        str: URL with credential information
    """
    sa_url = make_url(url)
    connect_args = sa_url.translate_connect_args()
    connect_args["username"], connect_args["password"] = credentials
    new_sa_url = URL(sa_url.drivername, **connect_args)
    return str(new_sa_url)


def generate_filter_subdirectory_name(resources, filter_id_hash):
    """Generates an output directory name based on applied filters.

    Args:
        resources (Iterable of ProjectItemResource): item's forward resources
        filter_id_hash (str): hashed filter id string

    Returns:
        str: subdirectory name
    """
    subdirectory = filter_id_hash
    if subdirectory:
        scenario_name = _single_scenario_name_or_none(resources)
        if scenario_name is not None:
            subdirectory = scenario_name[:15] + "_" + subdirectory
    return subdirectory


def _single_scenario_name_or_none(resources):
    """Figures out if given resources have a single common scenario filter.

    Args:
        resources (Iterable of ProjectItemResource): resources to investigate

    Returns:
        str: scenario name or None
    """
    scenario_name = None
    for resource in resources:
        try:
            filter_stack = resource.metadata["filter_stack"]
        except KeyError:
            continue
        for filter_config in filter_stack:
            name = scenario_name_from_dict(filter_config)
            if name is None:
                continue
            if scenario_name is None:
                scenario_name = name
            elif name != scenario_name:
                return None
    return scenario_name


def _ids_for_item_type(db_map, item_type):
    """Queries ids for given database item type.

    Args:
        db_map (DatabaseMapping): database map
        item_type (str): database item type

    Returns:
        set of int: item ids
    """
    return {row.id for row in db_map.query(getattr(db_map, item_type + "_sq"))}


def purge(db_map, purge_settings, cancel_on_error, logger):
    """Removes items from database.

    Args:
        db_map (DatabaseMapping): target database mapping
        purge_settings (dict, optional): mapping from item type to purge flag
        cancel_on_error (bool): if True, cancel operation on error, otherwise keep going
        logger (LoggerInterface): logger

    Returns:
        bool: True if operation was successful, False otherwise
    """
    if purge_settings is None:
        # Legacy Importers/Mergers didn't have explicit purge settings.
        purge_settings = {item_type: True for item_type in spinedb_api.DatabaseMapping.ITEM_TYPES}
    removable_db_map_data = {
        item_type: _ids_for_item_type(db_map, item_type) for item_type, checked in purge_settings.items() if checked
    }
    removable_db_map_data = {item_type: ids for item_type, ids in removable_db_map_data.items() if ids}
    if removable_db_map_data:
        try:
            logger.msg.emit("Purging database.")
            db_map.cascade_remove_items(**removable_db_map_data)
        except spinedb_api.SpineDBAPIError:
            logger.msg_error.emit("Failed to purge database.")
            if cancel_on_error:
                logger.msg_error.emit("Cancel on error is set. Bailing out.")
                return False
    return True
