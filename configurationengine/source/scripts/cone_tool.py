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
import cone_common
from cone.public import settings, utils

logger              = logging.getLogger('cone')
VERSION             = cone.__version__
if cone._svnrevision not in ("", "exported"):
    VERSION += " (SVN %s)" % cone._svnrevision


def format_actions(actions, filter=None):
    action_names = []
    for act in actions:
        if not filter or filter(act):
            action_names.append(act.name)
    
    action_names.sort()
    ret = ''
    for act in action_names:
        help =  actions[act].short_help()
        ret += '    %s : %s\n' % (act, help)
    return ret

def get_cone_configs(paths):
    static_paths =  [os.path.expanduser('~'),
                     os.getcwd()]
    all_paths = [ROOT_PATH]
    all_paths += static_paths
    all_paths += paths
    
    configs = cone_subaction.get_cfg_files(all_paths, 'cone.ini')
    return configs

def get_actions(configs):
    return cone_subaction.get_actions(configs)


def get_help(actions):
    helpstr = \
"""
Use %%prog [action] -h to get action specific help.

Available actions 
Main actions for one or more configurations. 
%s

Actions related to the configuration project maintenance. 
%s

extensions:
%s
""" % (format_actions(actions, lambda x: x.type=='configuration'),
       format_actions(actions, lambda x: x.type=='project'),
       format_actions(actions, lambda x: x.type=='extension'))
    return helpstr

def main():
    # Get the operating system name to pass it on the the cmdsplit..
    os_name = os.name
    if os.getenv('CONE_CMDARG'):
        sys.argv = [sys.argv[0]]
        sys.argv += utils.cmdsplit(os.getenv('CONE_CMDARG'), os_name)
    if os.getenv('CONE_CMD_APPEND'):
        sys.argv.append( utils.cmdsplit(os.getenv('CONE_CMD_APPEND'), os_name) )

    CONE_USAGE = "%prog [action] [options]."
    configs = get_cone_configs([])
    actions = get_actions(configs)
    
    # Set the path for cone .cfg files to the same directory as this script
    settings.SettingsFactory.configpath = ROOT_PATH
    
    try:
        action = sys.argv[1]
        subaction = actions[action]
        print "Running action %s" % subaction.name
    except (IndexError, KeyError):
        CONE_ACTION_HELP = get_help(actions)
        parser = OptionParser(usage="%s\n\n%s" % (CONE_USAGE,CONE_ACTION_HELP),
                              version="%%prog %s" % VERSION,
                              prog="ConE")
        (options, args) = parser.parse_args()
        parser.error("Action must be given! See --help.")
    
    subaction.run()


if __name__ == "__main__":
    main()
