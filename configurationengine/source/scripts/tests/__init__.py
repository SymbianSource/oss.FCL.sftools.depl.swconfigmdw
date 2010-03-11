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
    sys.path.append(SOURCE_ROOT)
    sys.path.append(os.path.join(SOURCE_ROOT, 'testautomation'))
    
    # Import the plugin_utils module from plugins/
    sys.path.append(PLUGIN_SOURCE_ROOT)
    import plugin_utils
    del sys.path[-1]
    
    # Collect all needed plug-in source directories (all in 'common')
    plugin_sources = plugin_utils.find_plugin_sources(os.path.join(PLUGIN_SOURCE_ROOT, 'common'))
    plugin_source_paths = [path for path, _ in plugin_sources]
    
    paths = []
    paths.append(SOURCE_ROOT)
    paths.extend(plugin_source_paths)
    os.environ['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + ';' + ';'.join(paths)
    
    # Generate egg-info for the plug-ins if necessary
    import build_egg_info
    for path in plugin_source_paths:
        build_egg_info.generate_egg_info(path)

_setup()

# Find all unittest_*.py files in this folder
import re
__all__ = filter(lambda name: re.match(r'^unittest_.*\.py$', name) != None, os.listdir(ROOT_PATH))
# Strip .py endings
__all__ = map(lambda name: name[:-3], __all__)

def collect_suite():  
    suite = unittest.TestSuite()
    for test_module in __all__:
        # Load the test module dynamically and add it to the test suite
        module = __import__(test_module)
        suite.addTests(unittest.TestLoader().loadTestsFromModule(module))
    return suite

def runtests():
    unittest.TextTestRunner(verbosity=2).run(collect_suite())

if __name__ == '__main__':
    runtests()
