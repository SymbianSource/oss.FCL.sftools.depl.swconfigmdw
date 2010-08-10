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

import os
import sys
import logging
import logging.config
import re, fnmatch
from optparse import Option
import cone_tool


""" 
try to import cone and modify the sys.paths if it does not succeed.
This is done mainly for local installation and testing purposes. 
"""
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

try:
    from cone.public import api, settings, utils
except ImportError:
    sys.path.append(os.path.join(ROOT_PATH))
    sys.path.append(os.path.join(ROOT_PATH,'..'))
    from cone.public import api, settings, utils

# Common command line options used by all sub-actions
COMMON_OPTIONS = [
    Option("--print-settings",
           dest="print_settings",
           action="store_true",
           help="Print all the default settings from the current setting container.",
           default=False),
    
    Option("--print-supported-impls",
           action="store_true",
           help="Print all supported ImplML XML namespaces and file extensions.",
           default=False),
    
    Option("--print-runtime-info",
           action="store_true",
           help="Print runtime information about ConE.",
           default=False),
    
    Option("-v", "--verbose",\
          dest="verbose",\
          help="""Print error, warning and information on system out.
                  Possible choices: Default is 3. 
                                    NONE (all)    0
                                    CRITICAL      1
                                    ERROR         2
                                    WARNING       3
                                    INFO          4
                                    DEBUG         5""",
          metavar="LEVEL",
          default="3"),

    Option("--log-file",
           dest="log_file",
           action="store",
           type="string",
           help="Location of the used log file. Default is 'cone.log'",
           metavar="FILE",
           default="cone.log"),

    Option("--log-config",
           dest="log_conf",
           action="store",
           type="string",
           help="Location of the used logging configuration file. Default is 'logging.ini'",
           metavar="FILE"),
           
    Option("--username",
           dest="username",
           action="store",
           type="string",
           help="Username for webstorage operations. Not needed for filestorage or cpf storage. If the username \
           is not given, the tool will use the logged in username. "\
           "Example: cone export -p webstorage_url -r . -c sample.confml --username=admin --password=abc123.",
           metavar="USERNAME"),

    Option("--password",
           dest="password",
           action="store",
           type="string",
           help="Password for webstorage operations. Not needed for filestorage or cpf storage. If the password \
           is not given, the tool will prompt for password if needed. ",
           metavar="PASSWORD"),
]

def handle_common_options(options, settings=None):
    """
    Handle common command line options.
    @param options: The parsed command line options.
    @param settings: The settings to print if --print-settings is used.
    Can be None, in which case the default settings are printed.
    """
    if options.log_conf:
        open_log(options.verbose, options.log_file, options.log_conf)
    else:
        open_log(options.verbose, options.log_file)
    
    exit = False
    
    if options.print_settings:
        if settings == None:
            settings = get_settings([])
        print_settings(settings)
        exit = True
    
    if options.print_supported_impls:
        from cone.public import plugin
        print "Supported ImplML namespaces:"
        for ns in sorted(plugin.get_supported_namespaces()):
            print ns
        
        print ""
        print "Supported ImplML file extensions:"
        for ns in plugin.get_supported_file_extensions():
            print ns
        exit = True
    
    if options.print_runtime_info:
        print _get_runtime_info()
        print "\nsys.path contents:"
        print '\n'.join(sys.path)
        exit = True
    
    if exit: sys.exit()
    
def _get_runtime_info():
    if hasattr(sys, 'executable'):  executable = sys.executable
    else:                           executable = 'N/A'
    info = ["ConE version:    %s" % cone_tool.VERSION,
            "Python version:  %s" % sys.version,
            "Platform:        %s" % sys.platform,
            "Executable:      %s" % executable,
            "Command line:    %s" % ' '.join(sys.argv),
            "Working dir:     %s" % os.getcwd(),
            "Script location: %s" % ROOT_PATH]
    return '\n'.join(info)

def open_log(verbose, log_file, log_conf_file=os.path.join(ROOT_PATH, 'logging.ini')):
    try:
        # Convert the reference to the log file as a absolute path so that it would work in all scenarios
        log_file = repr(os.path.abspath(log_file))
        
        if log_file.startswith("'"):
            log_file = log_file.replace("'", '', 1)
        if log_file.endswith("'"):
            log_file = log_file.replace("'",'', 1)

        log_dir = os.path.dirname(log_file)
        if log_dir != '' and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        if (os.path.exists(log_conf_file)):
            defaults = {'logfile': log_file, 'level': get_log_level_for_config(verbose)}
            logging.config.fileConfig(log_conf_file, defaults)
        else:
            print "Failed to load logging configuration file: %s" % log_conf_file
        
        logger = logging.getLogger('cone')
        logger.info("Runtime info:\n%s" % _get_runtime_info())
        logger.debug("sys.path contents:\n%s" % '\n'.join(sys.path))
        
        def get_var(varname):
            try:                return os.environ[varname]
            except KeyError:    return 'N/A'
        logger.debug("PATH: %s" % get_var('PATH'))
        logger.debug("PYTHONPATH: %s" % get_var('PYTHONPATH'))
    except IOError, e:
        print "Cannot create log file. ", e

def get_settings(files):
    parser = settings.SettingsFactory.cone_parser()
    parser.read(files)
    return parser

def print_settings(parser):
    print_section(parser,"DEFAULT")
    for section in parser.sections():
        print_section(parser,section)

def print_section(parser, section):
    print "[%s]" % section
    for (name,value) in parser.items(section):
        print "  %s = %s" % (name,value)


def get_log_level(level):
    """
    Change the given user input log level to logging categorisation
    """
    # If the level is empty, revert to the default
    if level in ('', None):
        level = '3'
    
    if level == '0' : return logging.NOTSET
    elif level == '1' : return logging.CRITICAL
    elif level == '2' : return logging.ERROR
    elif level == '3' : return logging.WARNING
    elif level == '4' : return logging.INFO
    elif level == '5' : return logging.DEBUG
    else : return logging.NOTSET

def get_log_level_for_config(level):
    """
    Change the given user input to log level to logging configuration file
    """

    # If the level is empty, revert to the default
    if level in ('', None):
        level = 'WARNING'
    
    if level == '0' : return 'NOTSET'
    elif level == '1' : return 'CRITICAL'
    elif level == '2' : return 'ERROR'
    elif level == '3' : return 'WARNING'
    elif level == '4' : return 'INFO'
    elif level == '5' : return 'DEBUG'
    else : return 'NOTSET'


class ConfigurationNotFoundError(Exception):
    """
    Exception raised by get_config_list_from_project() if an invalid
    configuration is given.
    """
    pass

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
    @raise ConfigurationNotFoundError: A configuration specified in configs is not
        actually found in the project.
    """
    config_list = []
        
    configs_in_project = sorted(project.list_configurations())
    
    # Handle configurations specified with --configuration first
    for config in configs:
        if not project.get_storage().is_resource(utils.resourceref.norm(config)):
            raise ConfigurationNotFoundError("No such configuration: %s" % config)
        if config not in config_list:
            config_list.append(config)
    
    # Then handle wildcards
    if config_wildcards:
        for config in configs_in_project:
            for wildcard in config_wildcards:
                if fnmatch.fnmatch(config, wildcard):
                    if config not in config_list:
                        config_list.append(config)
    
    # Lastly handle regexes
    if config_regexes:
        for config in configs_in_project:
            for pattern in config_regexes:
                if re.match(pattern, config) is not None:
                    if config not in config_list:
                        config_list.append(config)
    
    return config_list