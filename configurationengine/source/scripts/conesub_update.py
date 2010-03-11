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
import re
import fnmatch
import logging
from optparse import OptionParser, OptionGroup

import cone_common
from cone.public import api, plugin, utils, exceptions


VERSION     = '1.0'
DEFAULT_EXT = '.cpf'
CPF_NAMESPACE  = "http://www.nokia.com/xml/cpf-id/1"
CPF_META_TAG = "configuration-property"

logger    = logging.getLogger('cone')

def main():
    parser = OptionParser(version="%%prog %s" % VERSION)
    
    parser.add_options(cone_common.COMMON_OPTIONS)
    
    parser.add_option("-c", "--configuration",
                        dest="configs",
                        action="append",
                        help="Defines the name of the configuration for the action, can be "\
                             "specified multiple times to include multiple configurations.",
                        metavar="CONFIG",
                        default=[])
    
    parser.add_option("--config-wildcard",
                      action="append",
                      dest="config_wildcards",
                      help="Wildcard pattern for including configurations, e.g. "\
                           "product_langpack_*_root.confml",
                      metavar="WILDCARD",
                      default=[])
    
    parser.add_option("--config-regex",
                      action="append",
                      dest="config_regexes",
                      help="Regular expression for including configurations, e.g. "\
                           "product_langpack_\\d{2}_root.confml",
                      metavar="REGEX",
                      default=[])
  
    parser.add_option("-p", "--project",\
                       dest="project",\
                       help="defines the location of current project. Default is the current working directory.",\
                       default=".",\
                       metavar="STORAGE")
    
    group = OptionGroup(parser, 'Update options',
                        'The update functionality is meant for ConfML manipulation '
                        'in current project (defined with -p). '
                        'Default value for the current project is the currently working directory. '
                        'A project can be either a folder or a cpf/zip file.')
    
    
    group.add_option("-m","--add-meta",\
                   dest="meta",\
                   action="append",
                   type="string",
                   help="Add given metadata to defined configuration."\
                        "Example --add-meta \"owner=John Cone\" -m product=E75",
                   default=None)    

    group.add_option("--add-cpf-meta",\
                   dest="cpfmeta",\
                   action="append",
                   type="string",
                   help="Add given CPF identification metadata to defined configuration."\
                        "Example --add-cpf-meta \"coreplat_name=Platform1\"",
                   default=None)
    
    group.add_option("-d","--add-desc",\
                   dest="desc",\
                   type="string",\
                   help="Add given description to defined configuration."\
                        "Example --add-desc \"Customer one CPF\" -d Description1",
                   default=None)
    
    group.add_option("--remove-meta",\
                   dest="remove_meta",\
                   action="append",
                   type="string",
                   help="Removes given metadata from defined configuration."\
                        "Example --remove-meta owner --remove-meta coreplat_name",
                   metavar="META",\
                   default=None)

    group.add_option("--remove-desc",\
                   dest="remove_desc",\
                   action="store_true",\
                   help="Removes description from defined configuration."\
                        "Example --remove-desc",
                   default=False)    

    group.add_option("--add-data",\
                   dest="data",\
                   action="append",
                   type="string",
                   help="Add given ConfML data to defined configuration."\
                        "Example --add-data \"KCRUidAvkon.KAknDefaultAppOrientation=1\"",
                   default=None) 

    parser.add_option_group(group)
    (options, args) = parser.parse_args()
    
    cone_common.handle_common_options(options)
    
    # Open the project and find out the active configuration
    project = api.Project(api.Storage.open(options.project, "a"))
    try:
        active_root = project.get_storage().get_active_configuration()
    except AttributeError:
        active_root = None
    
    # Collect the list of configurations specified from the command line
    config_list = []
    if options.configs or options.config_wildcards or options.config_regexes:
        try:
            config_list = cone_common.get_config_list_from_project(
                project          = project,
                configs          = options.configs,
                config_wildcards = options.config_wildcards,
                config_regexes   = options.config_regexes)
        except cone_common.ConfigurationNotFoundError, e:
            parser.error(str(e))
    
    # Use the active configuration if no configurations are specifically given
    if len(config_list) == 0:
        if active_root is None:
            parser.error("No configurations given and the project does not have an active root")
        else:
            logger.info('No configurations given! Using active root configuration %s' % active_root)
            config_list = [active_root]
    
    
    
    # Parse added meta and data definitions
    added_meta = _parse_name_value_pairs(options.meta, 'metadata')
    added_cpf_meta = _parse_name_value_pairs(options.cpfmeta, 'CPF metadata')
    added_data = _parse_name_value_pairs(options.data, 'data')
    
    for config_name in config_list:
        print "Updating %s" % config_name
        config = project.get_configuration(config_name)
        
        # Handle metadata and data additions
        if added_meta:      _add_meta(config, added_meta)
        if added_cpf_meta:  _add_cpf_meta(config, added_cpf_meta)
        if added_data:      _add_data(config, added_data)
          
        # Handle description  
        if options.desc:        
            logger.info("Setting description to %s" % options.desc)
            config.desc = options.desc
        if options.remove_desc:
            if config.desc:
                logger.info("Removing description")
                del config.desc
        
        # Handle metadata removals
        if options.remove_meta:
            for remove_meta in options.remove_meta:
                if config.meta:
                    index = config.meta.find_by_tag(remove_meta)
                    if index != -1:
                        del config.meta[index]
                        logger.info("Removed %s" % remove_meta)
                    else:
                        index = config.meta.find_by_attribute("name", remove_meta)
                        if index != -1:
                            del config.meta[index]
                            logger.info("Removed %s" % remove_meta)
                else:
                    logger.info("Could not remove metadata entry %s: not found." % remove_meta)
    
    project.save()
    project.close()

def _parse_name_value_pairs(entries, entry_type_name):
    """
    Parse a list of 'name=value' pairs into a dictionary.
    @param entries: The list of entries to parse.
    @param entry_type_name: Entry type name shown in the error message if an entry
        could not be parsed into a name-value pair.
    """
    if not entries:
        return {}
    
    result = {}
    pattern = re.compile("(.+)=(.+)")
    for entry in entries:
        mo = pattern.search(entry)
        if mo:
            name = mo.group(1)
            value = mo.group(2)
            result[name] = value
        else:
            logger.error("Illegal %s definition: %s" % (entry_name, entry))
    return result

def _add_meta(config, added_meta):
    if not config.meta:
        config.meta = []
    
    for tag, value in added_meta.iteritems():
        index = config.meta.find_by_tag(tag)
        if index != -1:
            logger.info("Replacing %s's value %s with %s" % \
                        (tag, config.meta[index].value, value))
            config.meta.replace(index, tag, value)
        else:
            logger.info("Adding value %s for %s." % (value, tag))                
            config.meta.add(tag, value)

def _add_cpf_meta(config, added_cpf_meta):
    if not config.meta:
        config.meta = []
    for attrName, attrValue in added_cpf_meta.iteritems():
        index = config.meta.find_by_attribute("name", attrName)
        if index != -1:
            logger.info("Replacing %s's value %s with %s" % \
                        (attrName, config.meta[index].attrs["value"], attrValue))
            config.meta.replace(index, CPF_META_TAG, None, CPF_NAMESPACE, {"name": attrName, "value": attrValue})
        else:
            logger.info("Adding value %s for %s." % \
                        (attrName, attrValue))                
            config.meta.add(CPF_META_TAG, None, CPF_NAMESPACE, {"name": attrName, "value": attrValue})

def _add_data(config, added_data):
    for ref, value in added_data.iteritems():
        if value.startswith("["):
            value = eval(value)
            for value_item in value:
                config.get_default_view().get_feature(ref).add_sequence(value_item, 0)
                logger.info("Set %s=%s" % (ref, repr(value)))
        else:
            config.get_default_view().get_feature(ref).set_value(value)
            logger.info("Set %s=%s" % (ref, value))

if __name__ == "__main__":
    main()



