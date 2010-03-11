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

CONE_PATH = os.path.join(ROOT_PATH, 'cone')
EGGS_PATH = os.path.join(ROOT_PATH, 'eggs')

def add_eggs_to_path(egg_path):
    if not os.path.isdir(egg_path):
        return
    
    for name in os.listdir(egg_path):
        if name.endswith('.egg'):
            path = os.path.normpath(os.path.join(egg_path, name))
            if path not in sys.path:
                print "Adding '%s' to path" % name
                sys.path.append(path)


def _collect_test_suite(base_dir, module_subdir):
    # Check that the directory exists
    module_dir = os.path.join(base_dir, module_subdir)
    if not os.path.exists(module_dir):
        raise RuntimeError("'%s' does not exist!" % module_dir)
    
    # Collect the names of all test modules (of the form "unittest_*.py")
    test_modules_names = []
    for name in os.listdir(module_dir):
        if re.match(r'^unittest_.*\.py$', name) != None:
            test_modules_names.append(name[:-3])
    
    # Import the modules
    sys.path.insert(0, base_dir)
    try:
        suite = unittest.TestSuite()
        for modname in test_modules_names:
            # Load the test module dynamically and add it to the test suite
            top_module = __import__(module_subdir + '.' + modname)
            
            # top_module contains now actually e.g. mymodule.unittest_sometest,
            # so get the actual unit test module
            module = getattr(top_module, modname)
            
            suite.addTests(unittest.TestLoader().loadTestsFromModule(module))
        return suite
    finally:
        del sys.path[0]

def _run_without_nose():
    suite = unittest.TestSuite()
    
    # Collect script test suite
    suite.addTest(_collect_test_suite(ROOT_PATH, 'tests'))
    
    # Collect test suites from the plugin-tests/ directory
    PLUGIN_TEST_DIR = os.path.join(ROOT_PATH, 'plugin-tests')
    if os.path.exists(PLUGIN_TEST_DIR):
        for name in os.listdir(PLUGIN_TEST_DIR):
            plugin_suite = _collect_test_suite(PLUGIN_TEST_DIR, name)
            suite.addTest(plugin_suite)
    
    # Run the tests
    unittest.TextTestRunner(verbosity=2).run(suite)

def _run_with_nose():
    import nose
    import nose.plugins.xunit
    
    # Configure nose
    plugins = nose.plugins.manager.DefaultPluginManager()
    allfiles = nose.config.all_config_files() + ['nose_bat.cfg']
    conf = nose.config.Config(files=allfiles, plugins=plugins)
    
    # Run the tests
    nose.run(config=conf, argv=sys.argv[:1])

def main():
    if 'CONE_PATH' not in os.environ:
        cone_path = os.path.join(ROOT_PATH, 'cone')
        print "Setting CONE_PATH to '%s'" % cone_path
        os.environ['CONE_PATH'] = cone_path
    
    add_eggs_to_path(EGGS_PATH)
    
    if '--with-nose' in sys.argv:
        _run_with_nose()
    else:
        _run_without_nose()
    return 0

if __name__ == "__main__":
    sys.exit(main())
