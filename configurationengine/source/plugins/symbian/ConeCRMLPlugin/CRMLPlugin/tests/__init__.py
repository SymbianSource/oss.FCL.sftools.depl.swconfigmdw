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
import sys, os, unittest

# Path to the directory where this file is located
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

# Import common plug-in initialization
PLUGINS_ROOT = os.path.normpath(os.path.join(ROOT_PATH, '../../../..'))
assert os.path.split(PLUGINS_ROOT)[1] == 'plugins'
if PLUGINS_ROOT not in sys.path: sys.path.append(PLUGINS_ROOT)
import plugin_utils

plugin_utils.plugin_test_init(ROOT_PATH)

SCRIPTS_ROOT = os.path.normpath(os.path.join(ROOT_PATH, '../../../../..', "scripts"))
assert os.path.exists(SCRIPTS_ROOT)
os.environ['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + ';' + SCRIPTS_ROOT + ';' + PLUGINS_ROOT

def collect_suite():
    return plugin_utils.collect_test_suite_from_dir(ROOT_PATH)

def runtests():
    unittest.TextTestRunner(verbosity=2).run(collect_suite())

if __name__ == '__main__':
    runtests()
