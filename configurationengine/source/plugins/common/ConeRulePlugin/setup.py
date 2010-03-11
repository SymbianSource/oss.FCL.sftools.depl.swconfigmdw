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
from ruleplugin import __version__

setup(
    name = "coneruleplugin",
    version = __version__,
    packages = find_packages(exclude=["*.tests"]),
    test_suite = "ruleplugin.tests.collect_suite",

    # metadata for upload to PyPI
    author = "Teemu Rytkonen",
    author_email = "teemu.rytkonen@nokia.com",
    description = "Configuration Engine rule plugin",
    license = "Eclipse Public License v1.0",
    keywords = "cone",
    url = "http://developer.symbian.org/wiki/index.php/Software_Configuration_Middleware",   # project home page, if any
    zip_safe = True,
    
    # entrypoint info
    entry_points={'cone.plugins.implmlreaders': ['ruleml_1 = ruleplugin.ruleml:RuleImplReader1',
                                                 'ruleml_2 = ruleplugin.ruleml:RuleImplReader2']}
)