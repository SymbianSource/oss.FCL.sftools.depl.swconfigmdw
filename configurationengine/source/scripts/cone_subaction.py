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
import ConfigParser


def get_cfg_files(paths, filename):
    """ Find out the cone subscripts that are present in the"""
    files = []
    for path in paths:
        cfgfile = os.path.join(path, filename)
        if os.path.exists(cfgfile):
            files.append(cfgfile)
    return files

def get_config(cfgfiles):
    config = ConfigParser.ConfigParser()
    config.read(cfgfiles)
    return config

def get_actions(cfgfiles):
    """ Find out the cone subscripts that are present in the"""
    subacts = ActionContainer()
    config = get_config(cfgfiles)
    actions_section = 'actions'
    if not config.has_section(actions_section):
        raise Exception('The cone.ini does not have any %s section.' % actions_section)
    for (name, section) in config.items(actions_section):
        subacts += get_subactions_from_configs(cfgfiles, section)     
    return subacts

def get_subactions_from_configs(cfgfiles, section):
    """ Find out the cone subscripts that are present in the"""
    subacts = ActionContainer()
    config = get_config(cfgfiles)
    paths = [os.path.dirname(cfgfile) for cfgfile in cfgfiles]
    if not config.has_section(section):
        raise Exception('The cone.ini does not have any %s section.' % section)
    for (commandname, path) in config.items(section):
        subacts.append(ConeAction(commandname, path, type=section, paths=paths))
    
    return subacts

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

class ActionContainer(list):
    pass

#    def __init__(self):
#        self._actions = {}
#
#    def __len__(self):
#        return len(self._actions)
#
    def __getitem__(self, key):
        for item in self:
            if item.name == key:
                return item
        raise KeyError('Key %s not found in %s'  % (key, self))
#
#    def __setitem__( self, key, value):
#        self._actions[key] = value
#
#    def __delitem__( self, key):
#        del self._actions[key]
#
#    def __iter__( self):
#        return self._actions.__iter__()

class ConeAction(object):
    def __init__(self, name, path, **kwargs):
        self.name = name
        self.path = path
        self.type = kwargs.get('type', '')
        self.paths = kwargs.get('paths', [])
        self._module = None

    @property
    def module_name(self):
        return os.path.basename(self.path)

    @property
    def module_path(self):
        return os.path.dirname(self.path)

    @property
    def module(self):
        if not self._module:
            paths = [os.path.join(pth, self.module_path) for pth in self.paths]
            paths.append(self.module_path)
            sys.path += paths
            try:
                self._module  = __import__(self.module_name)
            finally:
                del sys.path[-len(paths):]
        return self._module
    
    def short_help(self):
        if hasattr(self.module, 'short_help'):
            return self.module.short_help
        elif hasattr(self.module, 'main'):
            helpstr = self.module.main.__doc__ or '<None>'
            return helpstr.replace('\n', '').strip(' ')[:50]
        else:
            return 'Not a valid module!!'
        
    def run(self):
        self.module.main()


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
