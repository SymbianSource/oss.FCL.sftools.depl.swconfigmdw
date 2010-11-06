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

import sys, os, shutil, imp
import logging
from optparse import OptionParser

log = logging.getLogger()

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
SOURCE_ROOT = os.path.normpath(os.path.join(ROOT_PATH, '../source'))
SCRIPTS_SOURCE_ROOT = os.path.normpath(os.path.join(SOURCE_ROOT, 'scripts'))
PLUGIN_SOURCE_ROOT = os.path.normpath(os.path.join(SOURCE_ROOT, 'plugins'))
TESTAUTOMATION_ROOT = os.path.normpath(os.path.join(SOURCE_ROOT, 'testautomation'))
assert os.path.exists(SOURCE_ROOT)
assert os.path.exists(SCRIPTS_SOURCE_ROOT)
assert os.path.exists(PLUGIN_SOURCE_ROOT)
assert os.path.exists(TESTAUTOMATION_ROOT)



sys.path.append(TESTAUTOMATION_ROOT)
import testautomation
from testautomation.copy_dir import copy_dir
from testautomation import plugin_utils
import utils
utils.setup_logging('export_bat.log')


def read_export_function_from_file(file_path):
    if not os.path.exists(file_path):
        return None
    
    m = imp.load_source(
        file_path.replace('\\', '__')
                 .replace('/', '__')
                 .replace(':', '_')
                 .replace('.', '_')
                 .replace(' ', '_'),
        file_path)
    
    try:
        return m.export_standalone
    except AttributeError:
        return None

def find_egg_file(dir, name, python_version):
    """
    Returns the name of an egg file in the given directory that starts with the
    given name and is for the given Python version.
    
    >>> find_egg_file('dep-eggs', 'simplejson', '2.5')
    'simplejson-2.0.9-py2.5-win32.egg'
    >>> find_egg_file('dep-eggs', 'simplejson', '2.6')
    'simplejson-2.0.9-py2.6-win32.egg'
    """
    for filename in os.listdir(dir):
        if filename.startswith(name) and 'py' + python_version in filename:
            return filename
    return None

def main(argv):
    # -----------
    # Parse args
    # -----------
    
    parser = OptionParser()
    parser.add_option("-t", "--target-dir",
                      help="The directory where the test are to be exported.")
    parser.add_option("-p", "--plugin-package",
                      help="The plug-in package for exporting plug-in integration tests.",
                      default=None)
    (options, args) = parser.parse_args()
    if options.target_dir is None:
        parser.error("Target directory must be given")
    
    PYTHON_VERSION = utils.get_python_version()
    
    TARGET_PATH = options.target_dir
    PLUGIN_PACKAGE = options.plugin_package
    log.info("Target directory: %s" % TARGET_PATH)
    log.info("Plug-in package:  %r" % PLUGIN_PACKAGE)
    log.info("Python version:   %s" % PYTHON_VERSION)
    
    log.info("Cleaning target directory...")
    utils.recreate_dir(TARGET_PATH)
    
    
    # -------------------------
    # Export script test files
    # -------------------------
    
    log.info("Copying script test files...")
    SCRIPT_TESTS_DIR = os.path.join(SCRIPTS_SOURCE_ROOT, 'tests')
    assert os.path.exists(SCRIPT_TESTS_DIR)
    copy_dir(source_dir             = SCRIPT_TESTS_DIR,
             target_dir             = os.path.join(TARGET_PATH, 'tests'),
             dir_ignore_functions   = [lambda d: d in ('.svn', 'temp', 'export_standalone')],
             file_ignore_functions  = [lambda f: f == 'cone.log' or f.endswith('.pyc')])
    
    log.info("Copying script test overlay files...")
    copy_dir(source_dir = os.path.join(ROOT_PATH, "export-bat/scripts-tests-overlay"),
             target_dir = TARGET_PATH,
             dir_ignore_functions = [lambda d: d  == '.svn'])
    
    
    
    # --------------------------------------
    # Export plug-in integration test files
    # --------------------------------------
    
    log.info("Exporting plug-in integration test files...")
    subpaths_by_package = plugin_utils.find_plugin_package_subpaths(PLUGIN_SOURCE_ROOT, 'integration-test', PLUGIN_PACKAGE)
    for package_name, tests_path in subpaths_by_package:
        log.debug("  Package: %s" % package_name)
        log.debug("  Path:    %s" % tests_path)
        
        log.debug("  Copying test files...")
        target_path = os.path.join(TARGET_PATH, 'plugin-tests', package_name + '_tests')
        copy_dir(source_dir             = tests_path,
                 target_dir             = target_path,
                 dir_ignore_functions   = [lambda d: d in ('.svn', 'temp')],
                 file_ignore_functions  = [lambda f: f in ('cone.log', 'export_standalone.py') or f.endswith('.pyc')])
        
        log.debug("  Copying overlay files...")
        overlay_path = os.path.join('export-bat/plugin-integration-test-overlay')
        copy_dir(source_dir             = overlay_path,
                 target_dir             = target_path,
                 dir_ignore_functions   = [lambda d: d == '.svn'])
        
        log.debug("  Exporting extra data...")
        func = read_export_function_from_file(os.path.join(tests_path, 'export_standalone.py'))
        if func:
            log.debug("  Executing export function...")
            func(target_path)
    
    
    TARGET_EGGS_DIR = os.path.join(TARGET_PATH, 'eggs')
    
    # ---------------------------
    # Copy needed dependency eggs
    # ---------------------------
    
    log.info("Copying library eggs...")
    DEP_EGGS_DIR = os.path.normpath(os.path.join(ROOT_PATH, '../dep-eggs'))
    assert os.path.isdir(DEP_EGGS_DIR)
    DEPENDENCIES = ['simplejson']
    for dep in DEPENDENCIES:
        egg_file_name = find_egg_file(DEP_EGGS_DIR, dep, PYTHON_VERSION)
        if egg_file_name is None:
            log.critical("Could not find egg file for dependency '%s' from '%s'" % (dep, DEP_EGGS_DIR))
            return 1
        source_path = os.path.join(DEP_EGGS_DIR, egg_file_name)
        target_path = os.path.join(TARGET_EGGS_DIR, egg_file_name)
        utils.copy_file(source_path, target_path)
    
    
    # ------------------
    # Build needed eggs
    # ------------------
    
    log.info("Building eggs...")
    utils.build_egg(os.path.join(SOURCE_ROOT), TARGET_EGGS_DIR)
    utils.build_egg(os.path.join(SOURCE_ROOT, 'testautomation'), TARGET_EGGS_DIR)
    
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
