#!/usr/bin/env python
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

import sys

if sys.version_info[0] >= 3 or sys.version_info[0] <= 1:
    print("WARNING: You are using not officially supported Python version:", sys.version_info[0], ".", sys.version_info[1], ".", sys.version_info[2])
    print("Officially supported versions are 2.5 and 2.6")
    sys.exit(1)
elif sys.version_info[0] == 2:
    if sys.version_info[1] == 5 or sys.version_info[1] == 6:
        pass
    elif sys.version_info[1] == 4 or sys.version_info[1] >= 7:
        print("WARNING: You are using not officially supported Python version:", sys.version_info[0], ".", sys.version_info[1], ".", sys.version_info[2])
        print("Officially supported versions are 2.5 and 2.6")
    else:
        print("WARNING: You are using not officially supported Python version:", sys.version_info[0], ".", sys.version_info[1], ".", sys.version_info[2])
        print("Officially supported versions are 2.5 and 2.6")
        sys.exit(1)

import os
import fnmatch 
import re
import logging
from optparse import OptionParser, OptionGroup

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

import cone
import cone_subaction
from cone.public import settings

CONE_SCRIPT_PATTERN = 'conesub_*.py'
ROOT_PATH           = os.path.dirname(os.path.abspath(__file__))
SUBS                = cone_subaction.get_subactions(ROOT_PATH, CONE_SCRIPT_PATTERN)
ACTIONS             = [sub for sub in SUBS]
logger              = logging.getLogger('cone')
VERSION             = cone.__version__
if cone._svnrevision not in ("", "exported"):
    VERSION += " (SVN %s)" % cone._svnrevision
CONE_USAGE          = "%prog [action] [options]."
CONE_ACTIONS        = '\n'
for act in ACTIONS:
     CONE_ACTIONS += '    %s\n' % act
CONE_ACTION_HELP    = "Available actions %s\nUse %%prog [action] -h to get action specific help." % CONE_ACTIONS

def main():
    parser = OptionParser(usage="%s\n\n%s" % (CONE_USAGE,CONE_ACTION_HELP),
                          version="%%prog %s" % VERSION,
                          prog="ConE")
    
    # Set the path for cone .cfg files to the same directory as this script
    settings.SettingsFactory.configpath = ROOT_PATH
    
    try:
        action = sys.argv[1]
        subaction = SUBS[action]
        print "Running action %s" % subaction.name
    except (IndexError, KeyError):
        (options, args) = parser.parse_args()
        parser.error("Action must be given! See --help.")
    
    subaction.run()


if __name__ == "__main__":
    main()
