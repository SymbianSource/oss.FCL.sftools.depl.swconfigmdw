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
# Script for running all ConE unit tests (cone, plug-ins and scripts).
#

import os, sys, re, imp
import unittest

# Path to the directory where this file is located
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

# For module 'testautomation'
sys.path.append(os.path.join(ROOT_PATH, 'testautomation'))

from testautomation import testcli
import cone
import cone.public.plugin

def _load_module(path):
    if not path.endswith('.py'):
        raise ValueError("Given parameter ('%s') is not a .py file" % path)
    
    dir = os.path.dirname(path)
    sys.path.insert(0, dir)
    try:
        modname = path.replace('.', '_')
        return imp.load_source(modname, path)
    finally:
        del sys.path[0]
        # Since the module name __init__ is needed in many places,
        # but its contents may differ, remove it from sys.modules
        # in order to force reloading every time
        if '__init__' in sys.modules:
            del sys.modules['__init__']

def _collect_unittest_suite_from_file(file_path):
    suite = unittest.TestSuite()
    module = _load_module(file_path)
    suite.addTests(unittest.TestLoader().loadTestsFromModule(module))
    return suite


def _find_unittest_files(path, recursive=True):
    """
    Find all unittest_*.py files under the given directory.
    """
    pattern = re.compile(r'^unittest_.*\.py$')
    unittest_files = []
    if recursive:
        for root, dirs, files in os.walk(path, topdown=True):
            for filename in files:
                if pattern.match(filename) != None:
                    filepath = os.path.abspath(os.path.join(root, filename))
                    unittest_files.append(filepath)
    else:
        for filename in os.listdir(path):
            if pattern.match(filename) != None:
                filepath = os.path.abspath(os.path.join(path, filename))
                unittest_files.append(filepath)
    
    return unittest_files

def _collect_unittest_suite_from_path(path, recursive=True):
    """
    Collect a test suite containing all test cases loaded from
    unittest_*.py files in the given directory.
    """
    path = os.path.abspath(path)
    
    # Collect the list of .py files containing unit tests
    unittest_files = _find_unittest_files(path, recursive)
    
    # Load the files as modules and load tests from them
    suite = unittest.TestSuite()
    for file in unittest_files:
        module = _load_module(file)
        suite.addTests(unittest.TestLoader().loadTestsFromModule(module))
    return suite

def _collect_suite():
    def get_suite(path):
        return _collect_unittest_suite_from_path(os.path.join(ROOT_PATH, path))
    def get_suite_from_file(file_path):
        return _collect_unittest_suite_from_file(os.path.join(ROOT_PATH, file_path))
    
    suite = unittest.TestSuite()
    suite.addTests(get_suite('cone'))
    suite.addTests(get_suite('scripts/tests'))
    suite.addTests(get_suite('plugins'))
    suite.addTests(get_suite('testautomation'))
    
    # Tests can also be loaded from a file:
    #suite.addTests(get_suite_from_file('cone/public/tests/unittest_rules_on_configuration.py'))
    
    
    # Force-reload all ConE plug-in reader classes, since the __init__.py
    # files in the imported test cases have added plug-in sources to sys.path
    cone.public.plugin.ImplFactory.force_reload_reader_classes()
    
    return suite

def _run_without_nose():
    suite = _collect_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)

def _run_with_nose():
    # Call plugin_utils.init_all() so that all plug-ins are loaded
    # (otherwise script tests, plug-in unit tests and plug-in integration
    # tests would not work)
    PLUGIN_SOURCE_ROOT = os.path.normpath(os.path.join(ROOT_PATH, 'plugins'))
    assert os.path.isdir(PLUGIN_SOURCE_ROOT)
    sys.path.append(PLUGIN_SOURCE_ROOT)
    import plugin_utils
    plugin_utils.init_all()
    
    # Find all unittest_*.py files
    test_files = []
    def add_tests(path):
        test_files.extend(_find_unittest_files(os.path.join(ROOT_PATH, path)))
    add_tests('cone')
    add_tests('scripts/tests')
    add_tests('plugins')
    add_tests('testautomation')
    
    
    # Configure nose
    import nose
    plugins = nose.plugins.manager.DefaultPluginManager()
    conf = nose.config.Config(plugins=plugins, testNames=test_files)
    
    # Run the tests
    args = ['--verbosity=3',
            '--with-xunit',
            '--xunit-file=cone-alltests.xml',
            #'--collect-only',
            ]
    nose.run(config=conf, argv=[sys.argv[0]] + args)

def main():
    if '--with-nose' in sys.argv:
        _run_with_nose()
    else:
        _run_without_nose()

if __name__ == '__main__':
    main()
