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

import os
import sys
import fnmatch 
import re
import logging


def get_subactions(path,pattern):
    """ Find out the cone subscripts that are present in the ROOT_PATH """
    subacts = ActionContainer()
    for file in os.listdir(path):
        if fnmatch.fnmatch(file, pattern):
            sact = SubAction(file,pattern)
            subacts[sact.name] = sact
    return subacts

def get_log_level(level):
    """
    Change the given user input log level to logging categorisation
    """
    if level == 0 : return logging.NOTSET
    elif level == 1 : return logging.CRITICAL
    elif level == 2 : return logging.ERROR
    elif level == 3 : return logging.WARNING
    elif level == 4 : return logging.INFO
    elif level == 5 : return logging.DEBUG
    else : return logging.NOTSET

class ActionContainer(object):
    def __init__(self):
        self._actions = {}

    def __len__(self):
        return len(self._actions)

    def __getitem__(self, key):
        return self._actions[key]

    def __setitem__( self, key, value):
        self._actions[key] = value

    def __delitem__( self, key):
        del self._actions[key]

    def __iter__( self):
        return self._actions.__iter__()

class SubAction(object):
    def __init__(self, scriptname, pattern):
        self._scriptname = scriptname
        self._pattern = pattern

    @property
    def name(self):
        """ translate the pattern """
        pattern = fnmatch.translate(self._pattern).replace('.*', '(.*)')
        m = re.match(pattern, self._scriptname)
        return m.group(1)

    def run(self):
        module = __import__(self._scriptname.replace('.py',''))
        module.main()
