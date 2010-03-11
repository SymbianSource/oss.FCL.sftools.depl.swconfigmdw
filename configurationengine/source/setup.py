#
# Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
# All rights reserved.
# This component and the accompanying materials are made available
# under the terms of "Eclipse Public License v1.0"
# which accompanies this distribution, and is available
# at the URL "http://www.eclipse.org/legal/epl-v10.html".
#
# Initial Contributors:
# Nokia Corporation - initial contribution.
#
# Contributors:
#
# Description: 
#

import os, os.path
from pkg_resources import require
require("setuptools")
from setuptools import setup, find_packages
from cone import __version__

setup(
    name = "cone",
    version = __version__,
    packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data = {'cone.validation': ['confml_xsd/*.xsd', 'implml_xsd/*.xsd']},
    install_requires = ['Jinja2>=2.1.1', 'simplejson>=2.0.9', 'lxml>=2.2.2'], #FIX THIS: not to try load cone from web


    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    #install_requires = ['zipfile'],
    test_suite = "cone.tests.runtests.collect_suite",
    # metadata for upload to PyPI
    author = "Teemu Rytkonen",
    author_email = "teemu.rytkonen@nokia.com",
    description = "Configuration Engine",
    license = "Eclipse Public License v1.0",
    keywords = "cone",
    url = "http://developer.symbian.org/wiki/index.php/Software_Configuration_Middleware", 
    zip_safe = True
)
