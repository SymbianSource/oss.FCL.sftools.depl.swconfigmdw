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

import sys, os, unittest, re
import build_egg_info

# Path to the directory where this file is located
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

# Path to the source/ directory
SOURCE_ROOT = os.path.normpath(os.path.join(ROOT_PATH, '..'))
assert os.path.split(SOURCE_ROOT)[1] == 'source'

# Path to the source/plugins directory
PLUGIN_SOURCE_ROOT = os.path.normpath(os.path.join(SOURCE_ROOT, 'plugins'))
assert os.path.isdir(PLUGIN_SOURCE_ROOT)

def plugin_test_init(root_path, plugin_source_relative_path='../..'):
    """
    Initialize things so that plug-in unit tests can be run.
    
    @param root_path: Path of the __init__.py file calling this function. 
    @param plugin_source_relative_path: Path to the plug-in's source root relative
        to root_path. Usually this should be '../..', since this function is intended
        to be called from a plug-in's tests/__init__.py file.
    
    """
    # Add paths so that the unit tests work
    # -------------------------------------
    extra_paths = [
        # For module 'cone'
        SOURCE_ROOT,
        
        # For module 'testautomation'
        os.path.join(SOURCE_ROOT, 'testautomation'),
        
        # For the plug-in module.
        # Since the method is expected to be called from e.g.
        # source/plugins/ConeSomePlugin/someplugin/tests/__init__.py, this will then be
        # source/plugins/ConeSomePlugin, in which case the module 'someplugin' can be
        # imported
        os.path.join(root_path, plugin_source_relative_path)
    ]
    for p in extra_paths:
        p = os.path.normpath(p)
        if p not in sys.path: sys.path.append(p)
    
    # Generate egg-info for the plug-in.
    # The egg-info needs to be up-to-date, or the plug-in framework will not be able
    # to find the plug-in's ImplML reader classes
    plugin_path = os.path.normpath(os.path.join(root_path, plugin_source_relative_path))
    assert 'setup.py' in os.listdir(plugin_path), "Path '%s' does not contain 'setup.py" % plugin_path
    build_egg_info.generate_egg_info(plugin_path)

def integration_test_init(root_path):
    """
    Initialize things so that integration tests can be run.
    
    This function is intended to be called from a sub-package's integration-test/__init__.py file.
    @param root_path: Path of the __init__.py file calling this function.
    """
    # Add paths so that the unit tests work
    # -------------------------------------
    extra_paths = [
        # For module 'cone' (may be needed in some tests for e.g. asserts)
        SOURCE_ROOT,
        
        # For module 'testautomation'
        os.path.join(SOURCE_ROOT, 'testautomation'),
    ]
    for p in extra_paths:
        p = os.path.normpath(p)
        if p not in sys.path: sys.path.append(p)
    
    # Collect plug-in source paths (common + current)
    temp = []
    temp += [path for path, _ in find_plugin_sources(os.path.join(PLUGIN_SOURCE_ROOT, 'common'))]
    temp += [path for path, _ in find_plugin_sources(os.path.normpath(os.path.join(root_path, '..')))]
    plugin_paths = []
    for p in temp:
        if p not in plugin_paths: plugin_paths.append(p)
    
    # Add things to PYTHONPATH so that running cone_tool.py works
    paths = []
    paths.append(SOURCE_ROOT) # For module 'cone'
    paths.extend(plugin_paths)
    os.environ['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + ';' + ';'.join(paths)
    
    # Generate egg-info for the plug-ins.
    # The egg-info needs to be up-to-date, or the plug-in framework will not be able
    # to find the plug-in's ImplML reader classes
    for p in plugin_paths:
        assert 'setup.py' in os.listdir(p), "Path '%s' does not contain 'setup.py" % p
        build_egg_info.generate_egg_info(p)

def init_all():
    """
    Add all plug-ins to sys.path and PYTHONPATH so that running all
    plug-in unit tests and integration tests work.
    """
    # Find all plug-in source directories
    plugin_paths = []
    temp = find_all_plugin_sources(os.path.join(PLUGIN_SOURCE_ROOT))
    for package_name, sources in temp.iteritems():
        for path, modname in sources:
            plugin_paths.append(path)
    
    # Add paths so that the unit tests work
    # -------------------------------------
    extra_paths = [
        # For module 'cone' (may be needed in some tests for e.g. asserts)
        SOURCE_ROOT,
        
        # For module 'testautomation'
        os.path.join(SOURCE_ROOT, 'testautomation'),
    ] + plugin_paths
    for p in extra_paths:
        p = os.path.normpath(p)
        if p not in sys.path: sys.path.append(p)
    
    # Add things to PYTHONPATH so that running cone_tool.py works
    paths = []
    paths.append(SOURCE_ROOT) # For module 'cone'
    paths.extend(plugin_paths)
    os.environ['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + ';' + ';'.join(paths)
    
    # Generate egg-info for the plug-ins.
    # The egg-info needs to be up-to-date, or the plug-in framework will not be able
    # to find the plug-in's ImplML reader classes
    for p in plugin_paths:
        assert 'setup.py' in os.listdir(p), "Path '%s' does not contain 'setup.py" % p
        build_egg_info.generate_egg_info(p)

def collect_test_suite_from_dir(root_path):
    """
    Return a test suite containing all tests in 'unittest_*.py' files under the given directory.
    """
    # Find all unittest_*.py files in the folder
    test_modules = filter(lambda name: re.match(r'^unittest_.*\.py$', name) != None, os.listdir(root_path))
    # Strip .py endings
    test_modules = map(lambda name: name[:-3], test_modules)
    
    # Add the root path as the first one in sys.path, so that
    # __import__() checks that first when attempting to import a module 
    sys.path.insert(0, root_path)
    
    try:
        suite = unittest.TestSuite()
        for test_module in test_modules:
            # Load the test module dynamically and add it to the test suite
            module = __import__(test_module)
            suite.addTests(unittest.TestLoader().loadTestsFromModule(module))
        return suite
    finally:
        # Remove root_path from sys.path
        del sys.path[0]

def collect_suite_from_source_list(paths_and_modnames):
    suite = unittest.TestSuite()
    
    # Add the source paths to sys.path
    for path, modname in paths_and_modnames:
        if path not in sys.path:
            sys.path.append(path)
    
    # Import the tests in a separate loop, because otherwise the ImplML reader classes
    # could be loaded before all plug-ins are in sys.path
    for path, modname in paths_and_modnames:
        try:
            m = __import__(modname + '.tests')
            suite.addTests(m.tests.collect_suite())
        except ImportError:
            print "Tests for '%s' not added, no 'tests' module found" % path
    
    return suite

def get_plugin_module_name(plugin_src_path):
    """
    Return the name of the plug-in's module under given plug-in source path.
    
    >>> get_tests_module('source/plugins/common/ConeContentPlugin')
    'contentplugin'
    >>> get_tests_module('foo')
    None
    """
    if not os.path.isdir(plugin_src_path):
        return None
    
    for name in os.listdir(plugin_src_path):
        path = os.path.join(plugin_src_path, name)
        if os.path.isdir(path) and '__init__.py' in os.listdir(path):
            return name
    return None

def find_plugin_sources(subpackage_root_path):
    """
    Return ConE plug-in source directories from the given path.
    
    All sub-directories in subpackage_root_path of the form Cone*Plugin/ containing
    a sub-directory that is a python module are returned.
    
    @param path: The directory from where to find the entries.
    @return: A list of tuples, each containing (<source_dir>, <module_name>).
    """
    pattern = re.compile(r'^Cone.*Plugin$')
    
    # Collect a list of plug-in source paths and plug-in module names
    result = []
    for name in os.listdir(subpackage_root_path):
        path = os.path.join(subpackage_root_path, name)
        if pattern.match(name) is not None:
            modname = get_plugin_module_name(path)
            if modname is not None:
                result.append((path, modname))
    return result

def find_all_plugin_sources(plugins_root_path):
    """
    Return all ConE plug-in source directories from the plugins/ root
    directory.
    @return: A dictionary containing the output of find_plugin_sources() by
        plug-in sub-packages.
    >>> find_all_plugin_sources('C:/work/cone-trunk/source/plugins')
    {'common': [('C:/work/cone-trunk/source/plugins/common/ConeContentPlugin', 'contentplugin'),
                ('C:/work/cone-trunk/source/plugins/common/ConeTemplatePlugin', 'templatemlplugin')],
     'example': [('C:/work/cone-trunk/source/plugins/example/ConeExamplePlugin', 'examplemlplugin')]}
    """
    result = {}
    for name in os.listdir(plugins_root_path):
        path = os.path.join(plugins_root_path, name)
        if os.path.isdir(path):
            sources = find_plugin_sources(path)
            if sources: result[name] = sources
    return result

def find_plugin_package_subpaths(subpath, package_name=None):
    """
    Return a list of plug-in package sub-paths based on the given plug-in package name.
    
    The returned list always contains the sub-path for common plug-ins, and
    additionally for an extra plug-in package based on the given package name.
    
    This function can be used to find specifically named files or directories
    under the plug-in paths. E.g. find all 'integration-test' directories:
    
    >>> find_plugin_package_subpaths('integration-test', 'symbian')
    [('common',  'C:\\cone\\trunk\\sources\\plugins\\common\\integration-test'),
     ('symbian', 'C:\\cone\\trunk\\sources\\plugins\\symbian\\integration-test')]
    
    @param package_name: Name of the extra plug-in package. Can be None, '',
        'common' or an existing plug-in package.
    @return: List of tuples (package_name, subpath).
    
    @raise ValueError: The given package_name was invalid.
    """
    result = []
    
    def add(package_name):
        package_dir = os.path.join(PLUGIN_SOURCE_ROOT, package_name)
        
        if not os.path.exists(package_dir):
            raise ValueError("Invalid plug-in package name: '%s'" % package_name)
        
        path = os.path.normpath(os.path.join(package_dir, subpath))
        if os.path.exists(path):
            result.append((package_name, path))
    
    add('common')
    if package_name not in (None, '', 'common'):
        add(package_name)
    
    return result
    

def find_plugin_sources_by_package(package_name=None):
    """
    Return a list of plug-in source paths based on the given plug-in package name.
    
    The returned list always contains sources of common plug-ins, and
    additionally extra plug-in sources based on the given package name.
    
    @param package_name: Name of the extra plug-in package. Can be None, '',
        'common' or an existing plug-in package.
    @raise ValueError: The given package_name was invalid.
    """
    result = []
    
    # Find all plug-in sources
    sources = find_all_plugin_sources(PLUGIN_SOURCE_ROOT)
    
    # Always return common plug-ins
    if 'common' in sources:
        for path, modname in sources['common']:
            result.append(path)
    
    # Return extra plug-ins if necessary
    if package_name not in (None, '', 'common'):
        if package_name not in sources:
            raise ValueError("Invalid plug-in package name: '%s'" % package_name)
        else:
            for path, modname in sources[package_name]:
                result.append(path)
    
    return result
