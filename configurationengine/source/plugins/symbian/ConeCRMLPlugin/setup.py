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
from CRMLPlugin import __version__

setup(
    name = "conecrmlplugin",
    version = __version__,
    packages = find_packages(exclude=["*.tests"]),
    package_data = {'CRMLPlugin': ['xsd/*.xsd']},
    test_suite = "crmlplugin.tests.collect_suite",
     
    # metadata for upload to PyPI
    author = "Teemu Rytkonen",
    author_email = "teemu.rytkonen@nokia.com",
    description = "Configuration Engine Configuration Tool CRML plugin",
    license = "Eclipse Public License v1.0",
    keywords = "cone",
    url = "http://developer.symbian.org/wiki/index.php/Software_Configuration_Middleware",   # project home page, if any
    zip_safe = True,
    
    # entrypoint info
    entry_points={'cone.plugins.implmlreaders':  ['crml = CRMLPlugin.crml_reader:CrmlReader'],
                  'cone.plugins.implvalidators': ['crml = CRMLPlugin.crml_validators:VALIDATOR_CLASSES']}
)
