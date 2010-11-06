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

datafiles = ['cone_defaults.cfg',
             'conesub_generate.cfg',
             'imaker_variantdir.cfg',
             'cone.ini',
             'logging.ini',
             'cone_base.html',
             'gen_report_template.html',
             'compare_api_report_template.html',
             'compare_data_report_template.html',
             'compare_ci_report_template.html',
             'info_api_report_template.csv',
             'info_api_report_template.html',
             'info_impl_report_template.html',
             'info_content_report_template.html',
             'info_value_report_template.html',
             'info_value_report_template.csv',
             'info_ctr_report_template.csv',
             'info_ctr_report_template.html',
             'crml_dc_report_template.csv',
             'crml_dc_report_template.html',
             'validation_report_template.html',
             'validation_report_template.xml',
             'tablefilter.js',
             'popup.js'
             ]

setup(
    name = "cone-scripts",
    version = '1.0',
    scripts = ['cone_tool.py',
               'cone_common.py',
               'cone_subaction.py',
               'conesub_info.py',
               'conesub_fix.py',
               'conesub_export.py',
               'conesub_generate.py',
               'conesub_merge.py',
               'conesub_compare.py',
               #'conesub_import_browserbookmarks.py',
               'conesub_update.py',
               'conesub_report.py',
               'conesub_validate.py',
               'conesub_packvariant.py',
               'conesub_initvariant.py',
               'configroot2flat.py'] + 
               datafiles,

    author = "Teemu Rytkonen",
    author_email = "teemu.rytkonen@nokia.com",
    description = "Configuration Engine scripts",
    license = "Eclipse Public License v1.0",
    keywords = "cone. scripts",
    url = "http://developer.symbian.org/wiki/index.php/Software_Configuration_Middleware",
    zip_safe = False
)
