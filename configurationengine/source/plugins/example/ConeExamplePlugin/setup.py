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
    name = "coneexamplemlplugin",
    version = __version__,
    packages = find_packages(exclude=["*.tests"]),
    test_suite = "examplemlplugin.tests.collect_suite",

    # metadata for upload to PyPI
    author = "<author>",
    author_email = "authors.email@example.com",
    description = "Configuration Engine ExampleML plugin",
    license = "Eclipse Public License v1.0",
    keywords = "cone",
    url = "http://developer.symbian.org/wiki/index.php/Software_Configuration_Middleware",
    zip_safe = True,
    
    # Entry point info.
    # Plug-ins can register ImplML reader classes by adding entry points
    # pointing to reader classes under 'cone.plugins.implmlreaders'
    entry_points = {
        'cone.plugins.implmlreaders': [
            'exampleml = examplemlplugin.exampleml_reader:ExamplemlReader',
             # More readers (e.g. different versions of the same ImplML)
             # could also be registered:
             #'exampleml_v2 = examplemlplugin.exampleml_reader:ExamplemlReader2',
        ]
    }
)
