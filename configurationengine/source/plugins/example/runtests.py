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

import sys, os, re, unittest

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

PLUGINS_ROOT = os.path.normpath(os.path.join(ROOT_PATH, '..'))
assert os.path.split(PLUGINS_ROOT)[1] == 'plugins'
if PLUGINS_ROOT not in sys.path: sys.path.append(PLUGINS_ROOT)
import plugin_utils

if __name__ == "__main__":
    # Collect a list of plug-in source paths and plug-in module names
    paths_and_modnames = plugin_utils.find_plugin_sources(ROOT_PATH)
    # Create a test suite from them
    suite = plugin_utils.collect_suite_from_source_list(paths_and_modnames)
    # Run the suite
    unittest.TextTestRunner(verbosity=2).run(suite)
