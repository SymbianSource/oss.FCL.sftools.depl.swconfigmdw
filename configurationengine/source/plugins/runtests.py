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
import plugin_utils

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

if __name__ == "__main__":
    # Collect a list of plug-in source paths and plug-in module names
    sources = plugin_utils.find_all_plugin_sources(ROOT_PATH)
    
    # Flatten the source list
    flattened_sources = []
    for subpackage_name, paths_and_modnames in sources.iteritems():
        flattened_sources.extend(paths_and_modnames)
    
    # Create a test suite from them
    suite = plugin_utils.collect_suite_from_source_list(flattened_sources)
    
    # Run the suite
    unittest.TextTestRunner(verbosity=2).run(suite)
