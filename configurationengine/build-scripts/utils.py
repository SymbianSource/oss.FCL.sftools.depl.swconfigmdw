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
#   Utility functions for use in build scripts.
#

import sys, os, subprocess, shutil, logging

log = logging.getLogger()

def run_command(cmd, env_overrides={}):
    env = os.environ.copy()
    for key, val in env_overrides.iteritems():
        env[key] = val
    
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, env=env)
    out, err = p.communicate()
    if p.returncode != 0:
        log.error("Could not execute command (%s)" % cmd)
        log.debug("Output:\n%s" % out)
        return False
    else:
        return True

def recreate_dir(path):
    log.debug('recreate_dir(%s)' % path)
    if os.path.exists(path):
        for name in os.listdir(path):
            p = os.path.join(path, name)
            if os.path.isdir(p):    shutil.rmtree(p)
            else:                   os.remove(p)
    else:
        os.makedirs(path)

def build_egg(source_dir, target_dir):
    """
    Build an egg file from the given source directory (must contain a setup.py)
    into the given target directory.
    """
    log.debug("Building egg from '%s'" % source_dir)
    
    orig_workdir = os.getcwd()
    os.chdir(source_dir)
    try:
        cmd = 'python setup.py bdist_egg --dist-dir "%s"' % target_dir
        return run_command(cmd)
    finally:
        os.chdir(orig_workdir)

def copy_file(source_path, target_path):
    log.debug("Copying '%s' -> '%s'" % (source_path, target_path))
    target_dir = os.path.dirname(target_path)
    if target_dir != '' and not os.path.exists(target_dir):
        os.makedirs(target_dir)
    shutil.copy2(source_path, target_path)

def get_python_version():
    """
    Return the version of the Python that is run when the command 'python'
    is run (not the Python where this script is executing).
    """
    p = subprocess.Popen('python -c "import sys; print sys.version[:3]"', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    out, err = p.communicate()
    if p.returncode != 0:
        log.critical("Failed to get python version")
        log.critical("Command output: %s" % out)
        return 1
    
    return out.strip()

def setup_logging(logfile):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))    
    root_logger.addHandler(console_handler)
    
    file_handler = logging.FileHandler(logfile, mode='w')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    root_logger.addHandler(file_handler)
