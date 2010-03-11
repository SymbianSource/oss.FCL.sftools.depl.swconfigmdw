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
from optparse import OptionParser

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
SOURCE_ROOT = os.path.normpath(os.path.join(ROOT_PATH, '../../..'))
PLUGIN_SOURCE_ROOT = os.path.normpath(os.path.join(SOURCE_ROOT, 'plugins'))
assert os.path.split(SOURCE_ROOT)[1] == 'source'
assert os.path.split(PLUGIN_SOURCE_ROOT)[1] == 'plugins'

sys.path.append(os.path.normpath(os.path.join(SOURCE_ROOT, 'testautomation')))
import testautomation
from testautomation.copy_dir import copy_dir

def build_egg(dir, target_dir):
    orig_workdir = os.getcwd()
    os.chdir(dir)
    try:
        os.system('python setup.py bdist_egg --dist-dir "%s"' % target_dir)
    finally:
        os.chdir(orig_workdir)

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

def main(argv):
    # Parse args
    parser = OptionParser()
    parser.add_option("--target-dir",
                      help="The directory where the test are to be exported.",
                      metavar="COMMAND")
    parser.add_option("--plugin-subpackage",\
                      help="The plug-in package for exporting plug-in integration tests.",\
                      default=None,\
                      metavar="SUBPACKAGE")
    (options, args) = parser.parse_args()
    if options.target_dir is None:
        parser.error("Target directory must be given")
    if options.plugin_subpackage is None:
        parser.error("Plug-in sub-package name must be given")
    
    TARGET_PATH = options.target_dir
    PLUGIN_PACKAGES = ['common']
    if options.plugin_subpackage.lower() not in ('', 'common'):
       PLUGIN_PACKAGES.append(options.plugin_subpackage)
    
    print "(Re)creating dir '%s'..." % TARGET_PATH
    if os.path.exists(TARGET_PATH):
        shutil.rmtree(TARGET_PATH)
    os.makedirs(TARGET_PATH)
    
    
    print "Copying script test files..."
    copy_dir(source_dir             = os.path.join(ROOT_PATH, '..'),
             target_dir             = os.path.join(TARGET_PATH, 'tests'),
             dir_ignore_functions   = [lambda d: d in ('.svn', 'temp', 'export_standalone')],
             file_ignore_functions  = [lambda f: f == 'cone.log' or f.endswith('.pyc')])
    
    print "Copying plug-in integration test files..."
    for name in PLUGIN_PACKAGES:
        print "  Processing plug-in package '%s'..." % name
        
        package_path = os.path.join(PLUGIN_SOURCE_ROOT, name)
        if not os.path.isdir(package_path):
            print "    '%s' does not exist or is not a directory!" % package_path
            return 1
        
        tests_path = os.path.join(package_path, 'integration-test')
        if not os.path.isdir(tests_path):
            print "    No 'integration-test' directory, skipping"
            continue
        
        print "    Copying test files..."
        target_path = os.path.join(TARGET_PATH, 'plugin-tests', name + '_tests')
        copy_dir(source_dir             = tests_path,
                 target_dir             = target_path,
                 dir_ignore_functions   = [lambda d: d in ('.svn', 'temp')],
                 file_ignore_functions  = [lambda f: f in ('cone.log', 'export_standalone.py') or f.endswith('.pyc')])
        
        print "    Overwriting __init__.py..."
        f = open(os.path.join(target_path, '__init__.py'), 'wb')
        f.close()
        
        print "    Exporting extra data..."
        func = read_export_function_from_file(os.path.join(tests_path, 'export_standalone.py'))
        if func:
            print "      Executing export function..."
            func(target_path)
    
    print "Copying overlay files..."
    copy_dir(source_dir = os.path.join(ROOT_PATH, "overlay"),
             target_dir = TARGET_PATH,
             dir_ignore_functions   = [lambda d: d  == '.svn'])
    
    
    print "Building eggs..."
    eggs_dir = os.path.join(TARGET_PATH, 'eggs')
    build_egg(os.path.join(SOURCE_ROOT), eggs_dir)
    build_egg(os.path.join(SOURCE_ROOT, 'testautomation'), eggs_dir)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
