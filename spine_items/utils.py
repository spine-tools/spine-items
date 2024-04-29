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

""" Contains utilities shared between project items. """
import os.path
from contextlib import suppress
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL, make_url
import spinedb_api
from spinedb_api.filters.scenario_filter import scenario_name_from_dict
from spine_engine.utils.queue_logger import SuppressedMessage
from spinedb_api.helpers import remove_credentials_from_url, SUPPORTED_DIALECTS, UNSUPPORTED_DIALECTS


class URLError(Exception):
    """Exception for errors in URL dicts."""


def database_label(provider_name):
    """Creates a standardized label for database resources.

    Args:
        provider_name (str): resource provider's name

    Returns:
        str: resource label
    """
    return "db_url@" + provider_name


def convert_to_sqlalchemy_url(url, item_name="", logger=None):
    """Returns a sqlalchemy url from url dict or None if not valid.

    Args:
        url (dict): URL to convert
        item_name (str): project item name for logging
        logger (LoggerInterface, optional): a logger

    Returns:
        URL: SqlAlchemy URL
    """
    selections = f"<b>{item_name}</b> selections" if item_name else "selections"
    if logger is None:
        logger = _NoLogger()
    if not url:
        logger.msg_error.emit(f"No URL specified for {selections}. Please specify one and try again.")
        return None
    try:
        sa_url = _convert_url(url)
        _validate_sa_url(sa_url, url["dialect"])
        return sa_url
    except URLError as error:
        logger.msg_error.emit(f"Unable to generate URL from {selections}: {error}")
        return None


def _convert_url(url):
    """Converts URL dict to SqlAlchemy URL.

    Args:
        url (dict): URL dictionary

    Returns:
        URL: SqlAlchemy URL
    """
    try:
        url = {key: value for key, value in url.items() if value}
        dialect = url.pop("dialect", None)
        with suppress(KeyError):
            del url["schema"]
        if not dialect:
            raise URLError(f"missing dialect")
        if dialect not in set(SUPPORTED_DIALECTS) | set(UNSUPPORTED_DIALECTS):
            raise URLError(f"invalid dialect '{dialect}'")
        if dialect == "sqlite":
            database = url.get("database", "")
            if database:
                url["database"] = os.path.abspath(database)
            return URL("sqlite", **url)  # pylint: disable=unexpected-keyword-arg
        db_api = spinedb_api.SUPPORTED_DIALECTS.get(dialect)
        if db_api is None:
            db_api = spinedb_api.helpers.UNSUPPORTED_DIALECTS[dialect]
        driver_name = f"{dialect}+{db_api}"
        return URL(driver_name, **url)  # pylint: disable=unexpected-keyword-arg
    except Exception as error:
        raise URLError(str(error)) from error


def _validate_sa_url(sa_url, dialect):
    """Validates SqlAlchemy URL.

    Args:
        sa_url (URL): SqlAlchemy URL to validate
        dialect (str): dialect

    Raises:
        URLError: raised if given URL is invalid
    """
    if not sa_url.database:
        raise URLError(f"database missing")
    if dialect != "sqlite":
        if sa_url.host is None:
            raise URLError(f"missing host")
        if sa_url.port is None:
            raise URLError(f"missing port")
        if sa_url.username is None:
            raise URLError(f"missing username")
        if sa_url.password is None:
            raise URLError(f"missing password")


def convert_url_to_safe_string(url):
    """Converts dict-style database URL to string without credentials.

    Args:
        url (dict): URL to convert

    Returns:
        str: URL as string
    """
    return remove_credentials_from_url(str(_convert_url(url)))


def check_database_url(sa_url):
    """Checks if URL points to a real database.

    Args:
        sa_url (URL): SQLAlchemy URL

    Returns:
        str: error message or None if URL works fine
    """
    try:
        engine = create_engine(sa_url)
        with engine.connect():
            pass
    except Exception as error:  # pylint: disable=broad-except
        return str(error)
    else:
        return None


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
            subdirectory = scenario_name[:20] + "_" + subdirectory
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


def escape_backward_slashes(string):
    """Escapes Windows directory separators.

    Args:
        string (str): string to escape

    Returns:
        str: escaped string
    """
    return string.replace("\\", "\\\\")
