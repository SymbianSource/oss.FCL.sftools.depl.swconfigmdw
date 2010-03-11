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

import os, os.path,sys
from setuptools import setup, find_packages
from genconfmlplugin import __version__

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(ROOT_PATH,'lib'))

setup(
    name = "conegenconfmlplugin",
    version = __version__,
    packages = find_packages(exclude=["*.tests"]),
    test_suite = "genconfml.tests.collect_suite",
	install_requires = ['lxml>=2.2.2'],

    # metadata for upload to PyPI
    author = "Teemu Rytkonen",
    author_email = "teemu.rytkonen@nokia.com",
    description = "Configuration Engine Configuration Tool GenConfml plugin",
    license = "Eclipse Public License v1.0",
    keywords = "cone",
    url = "http://developer.symbian.org/wiki/index.php/Software_Configuration_Middleware",
    zip_safe = True,
    
    # entrypoint info
    entry_points={'cone.plugins.implmlreaders': ['gcfml = genconfmlplugin.genconfmlplugin:GenconfmlImplReader']}
)
