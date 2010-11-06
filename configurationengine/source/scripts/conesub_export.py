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
import fnmatch
import logging
from optparse import OptionParser, OptionGroup
import cone_common
from cone.public import api, plugin, utils, exceptions


VERSION     = '1.0'
DEFAULT_EXT = '.cpf'
CONE_SCRIPT_PATTERN = 'conesub_*.py'
ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

logger    = logging.getLogger('cone')
DATA_NAME = 'confml/data.confml'

class  ExportFailedException(Exception):
    pass    

def main():
    """ Export configurations. """
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
    
    parser.add_option("-p", "--project",
                       dest="project",
                       help="defines the location of current project. Default is the "\
                            "current working directory.",\
                       default=".",
                       metavar="STORAGE")
    
    group = OptionGroup(parser, 'Export options',
                        'The export action is intended for exporting configurations '\
                        'from one project (storage) to another. A project can be a '\
                        'folder, a CPF or ZIP file, or a Carbon web storage URL. '\
                        # An ugly way to make newlines, someone should look into
                        # sub-classing optparse.HelpFormatter... 
                        '                                                                          '\
                        'Two different ways of exporting are supported: '\
                        '                                                                          '\
                        '1. Exporting multiple configurations into one new project using --remote '\
                        '                                                                          '\
                        '2. Exporting configurations into a number of new projects using --export-dir')
    
    group.add_option("-r", "--remote",
                   dest="remote",
                   help="Defines the location of remote storage. All configurations included using "\
                        "--configuration, --config-wildcard and --config-regex are exported into "\
                        "the storage. If the remote storage location is not given, the default "\
                        "location is determined based on the first included source configuration name. "\
                        "E.g. 'example.confml' would be exported into 'example.cpf'",
                   metavar="STORAGE")
    
    group.add_option("--export-dir",
                     help="Defines the directory where each included configuration is exported "\
                          "as a new project.",
                     default=None)
    
    group.add_option("--export-format",
                     help="Defines the format into which projects are exported when using "\
                          "--export-dir. Possible values are 'cpf' (the default) and 'dir'.",
                     default=None)
    
    group.add_option("-a","--add",
                   dest="added",
                   action="append",
                   type="string",
                   help="Adds a configuration layer to the given configuration as last element. "\
                        "The add operation can be used several times in a single command and it "\
                        "can create even an empty layer. "\
                        "Example --add foo/root.confml --add bar/root-confml.",
                   metavar="CONFIG",
                   default=None)

    group.add_option("--run-action",
                   dest="action",
                   action="append",
                   type="string",
                   help="Adds a execution of extra step that can manipulate the configuration before it is exported to external storage. "\
                        "The --run-action operation can be used several times in a single command and it "\
                        "will execute the actions in given order."\
                        "Example --run-action=fix, which would execute fix action during export.",
                   metavar="PLUGIN",
                   default=None)

    group.add_option("--exclude-folders",
                        dest="exclude_empty_folders",
                        action="store_true",
                        help="Excludes empty folders from export",
                        default=False)

    group.add_option("--exclude-content-filter",
                        dest="exclude_content_filter",
                        help="Filters out files and folders from content folder which matches with "\
                             "the given regular expression. Matching is case-insensitive. "\
                             "Example --exclude-content-filter=\".*\.sisx|.*\.sis|.*\.wgz|.*wgt\" "\
                             "Filters out all files with extension sis, sisx, wgz or wgt.",
                        default=None)

    group.add_option("--include-content-filter",
                        dest="include_content_filter",
                        help="Filters out files and folders from content folder which don't match with "\
                             "the given regular expression. Matching is case-insensitive. "\
                             "Example --include-content-filter=\".*(manual|configurator).*\" "\
                             "Filters out all content files which don't have manual or configurator in their path.",
                        default=None)

    
    parser.add_option_group(group)
    (options, args) = parser.parse_args()
    
    cone_common.handle_common_options(options)
    
    # Check options
    if options.export_format and options.export_dir is None:
        parser.error("--export-format can only be used in conjunction with --export-dir")
    if options.export_dir and options.remote:
        parser.error("--export-dir and --remote cannot be used at the same time")
    if options.export_format and options.export_format.lower() not in ('dir', 'cpf'):
        parser.error("Invalid export format '%s'" % options.export_format)
    if options.export_dir and not (options.configs or options.config_wildcards or options.config_regexes):
        parser.error("Use of --export-dir requires at least one configuration to be specified")
    if options.export_dir and os.path.isfile(options.export_dir):
        parser.error("Given export directory '%s' is a file")
    
    try:
        run_export(options)
    except ExportFailedException, e:
        parser.error(str(e))

    
    
def run_export(options):
    # Open the project and find out the active configuration
    storage = api.Storage.open(options.project, "r", username=options.username, password=options.password)
    project = api.Project(storage)
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
            raise ExportFailedException(str(e))
    
    # Use the active configuration if no configurations are specifically given
    if len(config_list) == 0:
        if active_root is None:
            raise ExportFailedException("No configurations given and the project does not have an active root")
        else:
            logger.info('No configurations given! Using active root configuration %s' % active_root)
            config_list = [active_root]
    
    # Perform the export
    if options.export_dir:
        _export_to_dir(project       = project,
                       export_dir    = options.export_dir,
                       export_format = options.export_format or 'cpf',
                       configs       = config_list,
                       added_layers  = options.added,
                       empty_folders = not options.exclude_empty_folders,
                       exclude_filters       = {"content": options.exclude_content_filter},
                       include_filters       = {"content": options.include_content_filter},
                       options               = options)
    else:
        _export_to_storage(project                 = project,
                           remote_project_location = options.remote,
                           configs                 = config_list,
                           added_layers            = options.added,
                           empty_folders           = not options.exclude_empty_folders,
                           exclude_filters         = {"content": options.exclude_content_filter},
						   include_filters         = {"content": options.include_content_filter},
                           options                 = options)
    

def _export_to_storage(project, remote_project_location, configs, added_layers, empty_folders, exclude_filters, include_filters, options):
    assert len(configs) > 0
    
    # If the remote storage is not given, determine it automatically based
    # on the first specified configuration name
    if not remote_project_location:
        remotename, ext = os.path.splitext(os.path.basename(configs[0]))
        remotename += DEFAULT_EXT
        logger.info('No remote storage given! Using source configuration name %s' % remotename)
        remote_project_location = remotename
    
    remote_project = api.Project(api.Storage.open(remote_project_location, "w", username=options.username, password=options.password))
    for config_path in configs:
        config = project.get_configuration(config_path)
        # immediate solution to run fixes during export
        if options.action:
            from cone.action import loader
            for action_name in options.action:
                try:
                    action_class = loader.get_class(action_name)
                    action = action_class(configuration=config,
                                          project=project)
                    action.run()
                except Exception,e:
                    logger.warning('Running plugin %s threw an exception: %s' % (action_name, e))
        project.export_configuration(config,
                                     remote_project.storage,
                                     empty_folders = empty_folders,
                                     exclude_filters = exclude_filters,
									 include_filters = include_filters)
        print "Export %s to %s done!" % (config_path, remote_project_location)
    
    # Setting first as active configuration if there are more than one configuration defined.
    configs = remote_project.list_configurations()
    if len(configs):
        try:
            remote_project.get_storage().set_active_configuration(configs[0])
        except AttributeError:
            pass
    
    remote_project.save()
    remote_project.close()
    
    _add_layers(project, remote_project_location, added_layers, empty_folders, exclude_filters, include_filters, options)
    
def _add_layers(source_project, remote_project_location, added_configs, empty_folders, exclude_filters, include_filters, options):
    """
    Add new configuration layers from source_project into 
    """
    if not added_configs:
        return
    
    target_project = api.Project(api.Storage.open(remote_project_location, "a"))
    for target_config_name in target_project.list_configurations():
        target_config = target_project.get_configuration(target_config_name)
        
        for added_config_name in added_configs:
            # Add layers only once
            if not target_project.storage.is_resource(added_config_name):
                logger.info('Adding configuration %s' % added_config_name)
                
                if source_project.storage.is_resource(added_config_name):
                    # The configuration exists in the source project, export it from there
                    existing_config = source_project.get_configuration(added_config_name)
                    source_project.export_configuration(existing_config,
                                                        target_project.storage,
                                                        empty_folders = empty_folders,
                                                        exclude_filters = exclude_filters,
                                                        include_filters = include_filters)
                else:
                    # The given configuration does not exist in the source project,
                    # create a new empty layer
                    logger.info("Creating new layer %s." % added_config_name)
                    new_config = target_project.create_configuration(added_config_name)
                    new_config.create_configuration(DATA_NAME)
            
            # Include the added configuration in the configuration root
            target_config.include_configuration(utils.resourceref.norm(added_config_name))
    
    target_project.save()
    target_project.close()

def _export_to_dir(project, export_dir, export_format, configs, added_layers, empty_folders, exclude_filters, include_filters, options):
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    for config in configs:
        remote_name, _ = os.path.splitext(os.path.basename(config))
        if export_format.lower() == 'cpf':
            remote_name += '.cpf'
        elif export_format.lower() == 'dir':
            remote_name += '/'
        
        remote_name = os.path.join(export_dir, remote_name)
        _export_to_storage(project, remote_name, [config], added_layers, empty_folders, exclude_filters, include_filters, options)

if __name__ == "__main__":
    main()
