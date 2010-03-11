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
PLUGIN_SOURCE_ROOT = os.path.normpath(os.path.join(ROOT_PATH, '../..'))
assert os.path.split(PLUGIN_SOURCE_ROOT)[1] == 'plugins'

# Import plugin_utils from the plug-in sources root
if PLUGIN_SOURCE_ROOT not in sys.path: sys.path.append(PLUGIN_SOURCE_ROOT)
import plugin_utils

# Run integration test initialization
plugin_utils.integration_test_init(ROOT_PATH)

def collect_suite():
    return plugin_utils.collect_test_suite_from_dir(ROOT_PATH)

def runtests():
    unittest.TextTestRunner(verbosity=2).run(collect_suite())

if __name__ == '__main__':
    runtests()
