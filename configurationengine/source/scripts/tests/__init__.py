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

import unittest, os, sys

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
SOURCE_ROOT = os.path.normpath(os.path.join(ROOT_PATH, '../..'))
PLUGIN_SOURCE_ROOT = os.path.normpath(os.path.join(SOURCE_ROOT, 'plugins'))
assert os.path.split(SOURCE_ROOT)[1] == 'source'
assert os.path.split(PLUGIN_SOURCE_ROOT)[1] == 'plugins'

def _setup():
    """
    Set up everything so that running "python cone_tool.py" finds the ConE
    and plug-in modules.
    """
    from testautomation import plugin_utils
    
    # Collect all needed plug-in source directories (all in 'common')
    plugin_sources = plugin_utils.find_plugin_sources(os.path.join(PLUGIN_SOURCE_ROOT, 'common'))
    plugin_source_paths = [path for path, _ in plugin_sources]
    
    # Generate egg-info for the plug-ins if necessary
    from testautomation import build_egg_info
    for path in plugin_source_paths:
        build_egg_info.generate_egg_info(path)

_setup()

