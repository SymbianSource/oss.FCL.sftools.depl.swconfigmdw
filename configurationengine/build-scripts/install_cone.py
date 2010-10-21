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
#   Script for building and installing ConE into a specified directory.
#

import sys, os, shutil, subprocess, optparse
import logging
log = logging.getLogger()

import utils
utils.setup_logging('install_cone.log')

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

# The sub-directory of the main install directory where all required libraries
# etc. are installed
INSTALL_SUBDIR = 'configurationengine'

# The sub-directory for required libraries, platform-specific
if sys.platform == "win32":
    PLATFORM_SUBDIR = 'win'
else:
    PLATFORM_SUBDIR = 'linux'

PYTHON_EXECUTABLE = 'python'

SOURCE_ROOT = os.path.abspath(os.path.join(ROOT_PATH, '../source'))
assert os.path.isdir(SOURCE_ROOT)
SCRIPTS_SOURCE_ROOT = os.path.abspath(os.path.join(ROOT_PATH, '../source/scripts'))
assert os.path.isdir(SCRIPTS_SOURCE_ROOT)
PLUGIN_SOURCE_ROOT = os.path.abspath(os.path.join(ROOT_PATH, '../source/plugins'))
assert os.path.isdir(PLUGIN_SOURCE_ROOT)
TESTAUTOMATION_ROOT = os.path.abspath(os.path.join(SOURCE_ROOT, 'testautomation'))
assert os.path.isdir(TESTAUTOMATION_ROOT)

sys.path.insert(0, TESTAUTOMATION_ROOT)
sys.path.append(PLUGIN_SOURCE_ROOT)
from testautomation import plugin_utils

# Temporary directory where ConE eggs are built into
TEMP_CONE_EGG_DIR = os.path.join(ROOT_PATH, 'install-temp/cone-eggs')
# Temporary directory where dependency lib eggs are copied
TEMP_LIB_EGG_DIR = os.path.join(ROOT_PATH, 'install-temp/dep-eggs')

class BuildFailedError(RuntimeError):
    pass

def find_cone_egg_sources(plugin_package):
    """
    Return a list of paths to the source directories to install.
    """
    paths = [SOURCE_ROOT,
             SCRIPTS_SOURCE_ROOT]
    plugin_paths = plugin_utils.find_plugin_sources_by_package(PLUGIN_SOURCE_ROOT, plugin_package)
    paths.extend(plugin_paths)
    
    log.debug("ConE egg source paths:\n%s" % '\n'.join(paths))
    return paths
    

def build_cone_eggs(source_paths, python_executable):
    log.info("Cleaning temporary ConE egg dir...")
    utils.recreate_dir(TEMP_CONE_EGG_DIR)
    
    log.info("Building ConE eggs...")
    for source_path in source_paths:
        ok = utils.build_egg(source_path, TEMP_CONE_EGG_DIR, python_executable)
        if not ok:
            raise BuildFailedError()

def retrieve_dep_eggs(plugin_package):
    log.info("Cleaning temporary lib egg dir...")
    utils.recreate_dir(TEMP_LIB_EGG_DIR)
    
    log.info("Retrieving dependency eggs...")
    def copy_eggs(source_dir):
        log.debug("Copying eggs from '%s'..." % source_dir)
        for name in os.listdir(source_dir):
            if name.endswith('.egg'):
                if PLATFORM_SUBDIR == 'linux' and name.startswith('setuptools-0.6c11'):
                    continue
                else:
                    utils.copy_file(
                        source_path = os.path.join(source_dir, name),
                        target_path = TEMP_LIB_EGG_DIR)
   
    dep_dirs_by_package = [(None, os.path.join(ROOT_PATH, '../dep-eggs'))]
    dep_dirs_by_package.extend(plugin_utils.find_plugin_package_subpaths(PLUGIN_SOURCE_ROOT, 'dep-eggs', plugin_package))
    
    for package_name, dep_dir in dep_dirs_by_package:
        copy_eggs(dep_dir)

def init_target_dir(target_dir, python_version):
    BASE_DIR = os.path.normpath(os.path.join(target_dir, INSTALL_SUBDIR, PLATFORM_SUBDIR, python_version))
    LIB_DIR     = os.path.join(BASE_DIR, 'lib')
    SCRIPT_DIR  = os.path.join(BASE_DIR, 'scripts')
    
    utils.recreate_dir(BASE_DIR)
    utils.recreate_dir(LIB_DIR)
    utils.recreate_dir(SCRIPT_DIR)
    return LIB_DIR, SCRIPT_DIR

def install_cone_eggs(target_dir, python_version):
    """
    Install ConE eggs into the given target directory.
    """
    log.info("Installing ConE eggs...")
    LIB_DIR, SCRIPT_DIR = init_target_dir(target_dir, python_version)
    
    # Collect the eggs to install
    eggs = ['setuptools'] # Setuptools are needed
        
    for name in os.listdir(TEMP_CONE_EGG_DIR):
        if name.endswith('.egg'):
            eggs.append(TEMP_CONE_EGG_DIR + '/' + name)
    
    # Run easy_install to install the eggs
    for egg in eggs:
        log.debug(egg)
        
        command = ['easy_install-%s' % python_version,
                   '--find-links install-temp/dep-eggs',
                   '--install-dir "%s"' % LIB_DIR,
                   '--script-dir "%s"' % SCRIPT_DIR,
                   '--site-dirs "%s"' % LIB_DIR,
                   '--always-unzip']
        
        if PLATFORM_SUBDIR == 'win':
            # Use --always-copy on Windows to copy all needed libraries
            command.append('--always-copy')
        
        command.append('"' + egg + '"')
        command = ' '.join(command)
        
        log.debug(command)
        ok = utils.run_command(command, env_overrides={'PYTHONPATH': LIB_DIR})
        if not ok:
            raise BuildFailedError()

def develop_install_cone_sources(source_paths, target_dir, python_version, python_executable):
    log.info("Installing ConE sources in develop mode...")
    LIB_DIR, SCRIPT_DIR = init_target_dir(target_dir, python_version)
    
    orig_workdir = os.getcwd()
    try:
        for source_path in source_paths:
            os.chdir(source_path)
            command = ['%s setup.py develop' % python_executable,
                   '--find-links "%s"' % os.path.normpath(os.path.join(ROOT_PATH, 'install-temp/dep-eggs')),
                   '--install-dir "%s"' % LIB_DIR,
                   '--script-dir "%s"' % SCRIPT_DIR,
                   '--site-dirs "%s"' % LIB_DIR,
                   ]
            command = ' '.join(command)
            log.debug(command)
            ok = utils.run_command(command, env_overrides={'PYTHONPATH': LIB_DIR})
            if not ok:
                raise BuildFailedError()
    finally:
        os.chdir(orig_workdir)

def perform_build(target_dir, plugin_package, install_type, python_version, python_executable):
    log.info("Target directory:  %s" % target_dir)
    log.info("Plug-in package:   %r" % plugin_package)
    log.info("Python version:    %s" % python_version)
    log.info("Python executable: %s" % python_executable)

    # Retrieve dependencies to the correct location
    retrieve_dep_eggs(plugin_package)
    
    # Install the dependencies locally using either local copies or downloading from PyPi
    deps = ['Jinja2', 'lxml']
    for dep in deps:
        command = ['easy_install-%s' % python_version,
                   '--find-links install-temp/dep-eggs']

        command.append(dep)
        command = ' '.join(command)
        log.debug(command)
        ok = utils.run_command(command)
        if not ok:
            print "Warning: failed to run easy_install to install %s." % dep
        
        
    
    # Find paths to the sources to install
    source_paths = find_cone_egg_sources(plugin_package)
    
    log.info("Creating install directory...")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    if install_type == 'build':
        build_cone_eggs(source_paths, python_executable)
    if install_type == 'install':
        build_cone_eggs(source_paths, python_executable)
        install_cone_eggs(target_dir, python_version)
    else:
        develop_install_cone_sources(source_paths, target_dir, python_version, python_executable)
    
    # Copy RELEASE.txt
    utils.copy_file(
        source_path = os.path.join(SOURCE_ROOT, '..', 'RELEASE.TXT'),
        target_path = os.path.join(target_dir, INSTALL_SUBDIR, 'RELEASE.TXT'))
    
    # Copy cone.cmd or cone.sh, depending on the platform
    if sys.platform == "win32":
        sourcefile = targetfile = "cone.cmd"
    else:
        sourcefile = "cone.sh"
        targetfile = "cone"
    log.info("Copying %s" % sourcefile)
    utils.copy_file(
        source_path = os.path.join(SOURCE_ROOT, sourcefile),
        target_path = os.path.join(target_dir, targetfile))

def main():
    parser = optparse.OptionParser()
    parser.add_option("-t", "--target-dir",
                      help="The directory where ConE is to be installed.")
    parser.add_option("-p", "--plugin-package",\
                      help="The plug-in package to include in the installation.",\
                      default=None)
    parser.add_option("-i", "--install-type",\
                      help="The installation type, can be 'install' (the default) or 'develop'.",\
                      default='install')
    parser.add_option("--python-executable",\
                      help="The Python executable to run type, defaults to 'python'.",\
                      default='python')
    (options, args) = parser.parse_args()
    if options.target_dir is None:
        parser.error("Target directory must be given")
    if options.install_type not in ('install', 'build', 'develop'):
        parser.error("Invalid install type ('%s')" % options.install_type)
        
    if not utils.run_command("%s --help" % options.python_executable):
        log.critical("Could not run '%s'. Please make sure that you "\
                     "have Python installed and in your path." % options.python_executable)
        return 1
    
    python_version = utils.get_python_version(options.python_executable)
    
    easy_install_cmd = "easy_install-%s" % python_version
    if not utils.run_command("%s --help" % easy_install_cmd):
        log.critical("Could not run '%s'. Please make sure that you "\
                     "have setuptools installed and the Python scripts directory in your path."\
                     % easy_install_cmd)
        return 1
    
    
    
    try:
        perform_build(options.target_dir, options.plugin_package, options.install_type, python_version, options.python_executable)
    except BuildFailedError:
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
