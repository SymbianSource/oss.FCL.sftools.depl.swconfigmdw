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

from setuptools import setup, find_packages

setup(
    name = "cone-tests",
    version = "1.0",
    packages = find_packages(),
    scripts = ['runtests.py'],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    #install_requires = ['zipfile'],
    #test_suite = "cone.tests.runtests.collect_suite",

    package_data = {
        'configproject': ['*.*'],
    },

    # metadata for upload to PyPI
    author = "Teemu Rytkonen",
    author_email = "teemu.rytkonen@nokia.com",
    description = "Configuration Engine test module",
    license = "Symbian Foundation License v1.0",
    keywords = "cone test",
    url = "http://developer.symbian.org/wiki/index.php/Software_Configuration_Middleware",

    # could also include long_description, download_url, classifiers, etc.
)
