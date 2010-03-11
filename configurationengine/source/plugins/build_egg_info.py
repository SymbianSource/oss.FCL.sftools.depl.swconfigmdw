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

# Script for generating the egg-info directories for all needed plug-ins.
#
# This is needed, because running some of the tests from Eclipse or
# command line requires the egg-info dirs to be present for the plug-ins
# to be found.

import sys, os, subprocess, shutil

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DEBUG = False

def generate_egg_info(path):
    """Generate egg-info for the given plug-in path if possible and necessary."""
    if not os.path.isdir(path) or "setup.py" not in os.listdir(path):
        return
    
    # Check if egg-info has already been generated
    for name in os.listdir(path):
        egg_info_path = os.path.join(path, name)
        if os.path.isdir(egg_info_path) and name.endswith('.egg-info'):
            # xxx.egg-info is present in the directory, check if it is old
            setup_py_path = os.path.join(path, 'setup.py')
            if os.stat(setup_py_path).st_mtime < os.stat(egg_info_path).st_mtime:
                if DEBUG: print "No need to generate egg-info for '%s'" % path
                return
            else:
                if DEBUG: print "egg-info for '%s' is out of date, removing old and generating new" % path
                shutil.rmtree(egg_info_path)
    
    # Run the egg-info generation command
    orig_workdir = os.getcwd()
    try:
        if DEBUG: print "Generating egg-info for '%s'..." % path
        os.chdir(path)
        p = subprocess.Popen("python setup.py egg_info", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if p.returncode != 0:
            print >>sys.stderr, "Could not generate egg-info for '%s'!" % path
            print >>sys.stderr, "Command stdout output:"
            print >>sys.stderr, out
            print >>sys.stderr, "Command stderr output:"
            print >>sys.stderr, err
        else:
            if DEBUG:
                print "Done"
                print "Command output:"
                print out
    finally:
        os.chdir(orig_workdir)
