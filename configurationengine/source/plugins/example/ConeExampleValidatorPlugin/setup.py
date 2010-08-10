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
from setuptools import setup, find_packages
from examplemlplugin import __version__

setup(
    name = "coneexamplevalidatorplugin",
    version = __version__,
    packages = find_packages(exclude=["*.tests"]),
    test_suite = "examplevalidatorplugin.tests.collect_suite",

    # metadata for upload to PyPI
    author = "<author>",
    author_email = "authors.email@example.com",
    description = "Configuration Engine ExampleML plugin",
    license = "Eclipse Public License v1.0",
    keywords = "cone",
    url = "http://developer.symbian.org/wiki/index.php/Software_Configuration_Middleware",
    zip_safe = True,
    
    entry_points = {
        'cone.plugins.confmlvalidators': [
            'example = examplevalidatorplugin.validators:VALIDATOR_CLASSES'
        ],
    }
)
