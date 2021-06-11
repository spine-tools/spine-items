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
Setup script for Python's setuptools.

:author: A. Soininen (VTT)
:date:   3.10.2019
"""

from setuptools import setup, find_packages

from spine_items.version import (
    __version__,
    REQUIRED_SPINEDB_API_VERSION,
    REQUIRED_SPINE_ENGINE_VERSION,
    REQUIRED_SPINE_TOOLBOX_VERSION,
)


with open("README.md", encoding="utf8") as readme_file:
    readme = readme_file.read()

setup(
    name="spine_items",
    version=__version__,
    description="Spine project items",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Spine Project consortium",
    author_email="spine_info@vtt.fi",
    url="https://github.com/Spine-project/spine-items",
    packages=find_packages(exclude=("tests", "tests.*")),
    install_requires=[
        "spinedb_api >={}".format(REQUIRED_SPINEDB_API_VERSION),
        "spine_engine >={}".format(REQUIRED_SPINE_ENGINE_VERSION),
        "spinetoolbox >={}".format(REQUIRED_SPINE_TOOLBOX_VERSION),
    ],
    include_package_data=True,
    license="LGPL-3.0-or-later",
    zip_safe=False,
    keywords="",
    python_requires=">=3.6, <3.9",
    test_suite="tests",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Issue Tracker": "https://github.com/Spine-project/Spine-Toolbox/issues",
        "Documentation": "https://spine-toolbox.readthedocs.io/en/latest/project_items.html",
    },
)
