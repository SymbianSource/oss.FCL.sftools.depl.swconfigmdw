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
#!/usr/bin/env python
## 
# @author Teemu Rytkonen

import os, re, fnmatch, logging
from cone.public import api, utils, exceptions
from cone.confml import model as confml_model

logger = logging.getLogger('cone')

def get_config_list_from_project(project, configs, config_wildcards, config_regexes):
    """
    Return a list of configuration root names based on the given parameters.
    @param project: The project from which to get the configuration list.
    @param configs: List of configuration names to add. All of these should exist
        in the project, or a ConfigurationNotFoundError is raised.
    @param config_wildcards: List of wildcard patterns for including configurations.
    @param config_regexs: List of regular expression patters for including configurations.
    @return: A distinct list of configuration names matched by the given parameters. The
        list contains matched configurations in the following order:
            1. Configurations specified in configs
            2. Configurations matched by wildcard patterns
            3. Configurations matched by regular expressions
        If a configuration is matched by more than one of these, the first match determines
        its placement in the list.
    @raise Exception: A configuration specified in configs is not
        actually found in the project.
    """
    config_list = []
    
    # Handle configurations specified with --configuration first
    for config in configs:
        if not project.get_storage().is_resource(utils.resourceref.norm(config)):
            raise Exception("No such configuration: %s" % config)
        if config not in config_list:
            config_list.append(config)
    
    # Then handle wildcards
    #print "wilds %s" % config_wildcards
    if config_wildcards:
        for path in project.get_storage().list_resources('.', recurse=True):
            for wildcard in config_wildcards:
                if fnmatch.fnmatch(path, wildcard):
                    if path not in config_list:
                        config_list.append(path)
    
    # Lastly handle regexes
    #print "regexes %s" % config_regexes
    if config_regexes:
        for path in project.get_storage().list_resources('.', recurse=True):
            for pattern in config_regexes:
                if re.search(pattern, path) is not None:
                    if path not in config_list:
                        config_list.append(path)
    
    return config_list

def get_flat_includes(config):
    """
    get a flat list of configuration in which each include of configuration root is expanded.
    The mechanism assumes all includes that end with /root.confml to be layer includes that 
    are layers that are not expanded
    @param config: the configuration object to process. 
    """
    includes = []
    for include in config.list_configurations():
        if include.endswith('/root.confml'):
            includes.append(utils.resourceref.remove_begin_slash(include))
        else:
            subconfig = config.get_configuration(include)
            includes += get_flat_includes(subconfig)
    return includes

def get_nested_meta(config, recursion_depth=-1):
    """
    Get the nested meta data for the given configuration constructed from metadata of all sub configuration meta.
    @param config: the configuration object to fetch the metadata for
    @param recursion_depth: the depth of the recursive nested metadata calls. default value -1 will go through 
    all configurations.
    @return: a ConfmlMeta object 
    """
    
    meta = confml_model.ConfmlMeta()
    if recursion_depth != 0:
        # First recurse through all subconfigurations to get their meta     
        for subconfig_name in config.list_configurations():
            subconfig = config.get_configuration(subconfig_name)
            submeta = get_nested_meta(subconfig, recursion_depth-1)
            
            meta.update( submeta )
    
    # lastly, update the meta data of the root configuration
    if config.meta:
        meta.update(config.meta)
    return meta


class Configroot2FlatFailed(exceptions.ConeException):
    pass

class ConeConfigroot2FlatAction(object):
    def __init__(self, **kwargs):
        self.project = kwargs.get('project')
        self.configs = kwargs.get('configs')
        self.config_wildcards = kwargs.get('config_wildcards')
        self.config_regexes = kwargs.get('config_regexes')
        self._project = None
        
    def run(self):
        self._project = api.Project(api.Storage.open(self.project, 'a'))
        prj = self._project
        
        configs = []
        if self.configs or self.config_wildcards or self.config_regexes:
            configs = get_config_list_from_project(
                project          = prj,
                configs          = self.configs,
                config_wildcards = self.config_wildcards,
                config_regexes   = self.config_regexes)
    
        if not configs:
            raise Configroot2FlatFailed("At least one configuration must be given!")
        
        print "Processing configurations %s" % configs
        for source_config in configs:
            target_config= os.path.basename(source_config)
            if source_config == target_config:
                print "Cannot flatten configuration because the source path is the same as target!"
            config = prj.get_configuration(source_config)
            
            print "opened %s for flattening" % source_config
            
            print "Creating a new configuration root '%s' for flattening" % target_config
            tconf = prj.create_configuration(target_config, True)
            # add the includes
            for config_include in get_flat_includes(config):
                tconf.include_configuration(config_include)
            # add the metadata with hardcoded recursion depth count
            newmeta = get_nested_meta(config, 2)
            tconf.meta = newmeta
            tconf.name = config.name
            tconf.save()
        
        return True

    def save(self):
        if self._project: self._project.save()
        
    def close(self):
        if self._project: self._project.close()


def get_class():
    return ConeConfigroot2FlatAction
