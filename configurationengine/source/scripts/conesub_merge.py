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
import logging
from optparse import OptionParser, OptionGroup
import cone_common

from cone.public import api, utils, exceptions

VERSION = '1.0'

logger    = logging.getLogger('cone')

class MergeFailedException(Exception):
    """
    Exception raised if the merge failed for some reason.
    """
    pass

class MergePolicy(object):
    """
    Merge policy constants.
    """
    #: Replace/add files from the source layer into the
    #: target layer, preserving files in the target layer
    #: that do not exist in the source layer
    REPLACE_ADD = 'replace-add'
    
    #: Overwrite the entire target layer, so that it contains
    #: only the contents of the source layer
    OVERWRITE_LAYER = 'overwrite-layer'
    
    ALL = (REPLACE_ADD, OVERWRITE_LAYER)
    
    @classmethod
    def is_valid(cls, policy):
        return policy in cls.ALL

def get_new_layer_name(oldname,rootconfig):
    newpath = utils.resourceref.get_path(oldname)
    newpath+= "_" + utils.resourceref.remove_ext(utils.resourceref.get_filename(rootconfig))
    newpath+= "/" + utils.resourceref.get_filename(oldname)
    return newpath

def merge_configuration_layer(sourceconfig, targetconfig, merge_policy):
    """
    Merge the contents of the source layer into the target layer.
    @param sourceconfig: Source layer root configuration object.
    @param targetconfig: Target layer root configuration object.
    @param merge_policy: The used layer merge policy.
    """
    # If policy tells to entirely overwrite the layer, remove all
    # resources from the layer first
    if merge_policy == MergePolicy.OVERWRITE_LAYER:
        # Remove configurations from the layer root
        confs = targetconfig.list_configurations()
        for conf in confs:
            targetconfig.remove_configuration(conf)

        # Remove all related resources
        layerobj = targetconfig.get_layer()
        # Round one: remove all files
        resources = layerobj.list_all_related(empty_folders=False)
        for res in resources: layerobj.delete_resource(res)
        # Round two: remove any remaining empty directories
        resources = layerobj.list_all_related(empty_folders=True)
        for res in resources: layerobj.delete_folder(res)
    
    # Find all ConfML files
    confml_resources = sourceconfig.list_configurations()
    
    # Find all other related files and folders (content/, doc/ etc.)
    layerobj = sourceconfig.get_layer()
    targetobj = targetconfig.get_layer()
    other_resources = layerobj.list_all_related(empty_folders=True)
    
    # Copy the resources to the target configuration
    for res_path in confml_resources + other_resources:
        try:
            rres = layerobj.open_resource(res_path,"rb")
            wres = targetobj.open_resource(res_path,"wb")
            print "Copying %s" % rres.path
            logger.info('Copying layer resource %s to %s' % (rres.path, wres.path))
            wres.write(rres.read())
            wres.close()
            rres.close()
        except exceptions.NotResource:
            # If it isn't a resource (file), it's a folder
            targetobj.create_folder(res_path)
    
    # Remove all configurations from the target layer root
    already_included = targetconfig.list_configurations()
    for confml_path in already_included:
        targetconfig.remove_configuration(confml_path)
    
    # Include them back
    for confml_path in already_included:
        targetconfig.include_configuration(confml_path)
    
    # Include all added configurations
    for confml_path in confml_resources:
        if confml_path not in already_included:
            print "Including %s in layer root %s" % (confml_path, targetconfig.path)
            targetconfig.include_configuration(confml_path)

def find_layers_to_merge(layer_indices, rename, sourceconfig, targetconfig):
    """
    Return a list of layers to merge.
    
    @param layer_indices: List of layer indices to merge, can also be
        None to indicate that all layers are to be merged.
    @param rename: True if the layers should be renamed in the target
        config, False if not.
    @return: A list of tuples (layer_root, target_layer_root), where
        layer_root is the path to the layer root in the source
        configuration and target_layer_root the one in the target
        configuration.
    """
    # Get a list of all configurations to merge
    if layer_indices is None:
        mergeconfigs = sourceconfig.list_configurations()
    else:
        mergeconfigs = sort_mergeconfigs(layer_indices, sourceconfig.list_configurations())
    
    result = []
    if rename:
        for source_path in mergeconfigs:
            target_path = get_new_layer_name(source_path, targetconfig.path)
            result.append((source_path, target_path))
    else:
        for source_path in mergeconfigs:
            result.append((source_path, source_path))
    
    return result

def sort_mergeconfigs(layers, sourceconfigs):
    """
    Return a correctly sorted list of source configuration layers.
    @param layers: List of the indices of the layers to merg. Can be None, in
        which case all layers are returned.
    @param sourceconfigs: List of all configuration layer root paths in the
        source project.
    @return: List of configuration layer root paths.
    """
    sorted_configs = [None for _ in xrange(len(sourceconfigs))]
    for layer in layers:
        sorted_configs[layer]=sourceconfigs[layer]
    sorted_configs = filter(lambda x: x != None, sorted_configs)
    return sorted_configs

def merge_config_root_to_config_root(source_project, target_project,
                                     source_config, target_config,
                                     layer_indices, rename,
                                     merge_policy):
    """
    Merge the source configuration root to the target configuration root.
    @param layer_indices: List of layer indices to specify the layers
        to merge, can be None.
    @param rename: If True, the merged layers are renamed based on the
        name of the target configuration root.
    @param merge_policy: The used merge policy.
    """
    
    def get_active_root_if_necessary(project, configuration, name):
        if configuration:
            return configuration
        else:
            active_root = project.get_storage().get_active_configuration()
            if active_root == "":
                raise MergeFailedException("No %s configuration given and the project does not have an active root" % name)
            else:
                return active_root
    
    target_root = get_active_root_if_necessary(target_project, target_config, 'target')
    source_root = get_active_root_if_necessary(source_project, source_config, 'source')
    
    print "Target config:  %s" % target_root
    print "Source config:  %s" % source_root
    
    try:
        source_config = source_project.get_configuration(source_root)
    except exceptions.NotFound:
        raise MergeFailedException("Configuration root '%s' not found in source project" % source_root)
    
    
    # Create or get the target configuration root
    try:
        target_config = target_project.get_configuration(target_root)
    except exceptions.NotFound:
        logger.info('Creating new root configuration %s' % (target_config))
        target_config  = target_project.create_configuration(target_config)
        for sourcelayer_path in source_config.list_configurations():
            sourcelayer = source_config.get_configuration(sourcelayer_path)
            sourcelayer_path = sourcelayer.path
            if target_config.get_storage().is_resource(sourcelayer.path):
                logger.info('Including layer %s to root %s' % (sourcelayer_path, target_config.path))
                target_config.include_configuration(sourcelayer_path)
            else:
                logger.info('Creating new layer %s to root %s' % (sourcelayer_path, target_config.path))
                target_config.create_configuration(sourcelayer_path)
    
    # Collect a correctly sorted list of all layer paths to merge
    layers_to_merge = find_layers_to_merge(
        layer_indices   = layer_indices,
        rename          = rename,
        sourceconfig    = source_config,
        targetconfig    = target_config)
    
    print "Merging %d layer(s)..." % len(layers_to_merge)
    
    # Merge the layers
    for source_path, target_path in layers_to_merge:
        print "Merging %s -> %s" % (source_path, target_path)
        
        source_layer = source_project.get_configuration(source_path)
        
        if source_path != target_path:
            try:
                target_config.remove_configuration(source_path)
            except exceptions.NotFound:
                pass
            target_config.create_configuration(target_path)
        
        # Get or create the target configuration layer
        try:
            target_layer = target_config.get_configuration(target_path)
        except exceptions.NotFound:
            logger.info('Creating new layer configuration %s' % (target_path))
            target_layer = target_config.create_configuration(target_path)
        
        merge_configuration_layer(source_layer, target_layer, merge_policy)



def main(argv=sys.argv):
    parser = OptionParser(version="%%prog %s" % VERSION)
    
    parser.add_options(cone_common.COMMON_OPTIONS)
    
    parser.add_option("-c", "--configuration",\
                        dest="configuration",\
                        help="defines the name of the target configuration for the action",\
                        metavar="CONFIG")

    parser.add_option("-p", "--project",\
                       dest="project",\
                       help="defines the location of current project. Default is the current working directory.",\
                       default=".",\
                       metavar="STORAGE")
    
    group = OptionGroup(parser, 'Merge options',
                        'The merge functionality is meant to merge configurations/layers '
                        'from a remote project (defined with -r) to the current project (defined with -p). '
                        'Default value for the current project is the currently working directory. '
                        'A project can be either a folder or a cpf/zip file. There are two ways to '
                        'use merge: merge configuration roots (multiple layers), or specific layers. '
                        'See the ConE documentation for details and examples.')
    
    group.add_option("-r", "--remote",\
                   dest="remote",\
                   help="defines the location of remote storage",\
                   metavar="STORAGE")
    
    group.add_option("-s", "--sourceconfiguration",\
                        dest="sourceconfiguration",\
                        help="defines the name of the remote configuration inside the remote storage for the merge action. "\
                             "Default is the active root of the remote project.",\
                        metavar="CONFIG")
    
    group.add_option("--sourcelayer",
                     help="Defines a specific layer to use as the layer to merge "\
                          "from the remote project. Must be the layer root (ConfML file)."\
                          "For example: --sourcelayer assets/somelayer/root.confml",
                     metavar="LAYER_ROOT",
                     default=None)
    
    group.add_option("--targetlayer",
                     help="Defines a specific layer (root) to use as the layer to merge "\
                          "into the target project. Must be the layer root (ConfML file)."\
                          "For example: --targetlayer assets/somelayer/root.confml",
                     metavar="LAYER_ROOT",
                     default=None)

    group.add_option("--rename",\
                        action="store_true", 
                        dest="rename",\
                        help="defines that the merged layers need to be renamed",
                        default=False)

    group.add_option("--all",\
                        action="store_true", 
                        dest="all",\
                        help="Defines that the entire configuration (all layers) needs to be merged. "\
                             "This has no effect when merging layers directly using --sourcelayer and --targetlayer.",
                        default=False)

    group.add_option("-l", "--layer",\
                   dest="layers",\
                   type="int",
                   action="append",
                   help="Define the layers of the source configuration that are included to merge action. "\
                        "The layer operation can be used several times in a single command. "\
                        "Note that this can only be used when merging configuration roots, not "\
                        "specific layers using --sourcelayer and --targetlayer. "\
                        "Example -l -1 --layer=-2, which would append a layers -1 and -2 to the layers => layers = -1,-2",
                   metavar="LAYERS",\
                   default=None)
    
    group.add_option("--merge-policy",
                     help="Specifies the merge policy to use when merging layers. "\
                          "Possible values:                                                         "\
                          "replace-add - Add/replace files from source layer, but leave other files in the target as they are. "\
                          "                                                         "\
                          "overwrite-layer - Overwrite the entire layer (remove all previous content).",
                     default=MergePolicy.REPLACE_ADD)
    
    parser.add_option_group(group)
    (options, _) = parser.parse_args(argv)
    
    cone_common.handle_common_options(options)
    
    # Check the passed options
    if not MergePolicy.is_valid(options.merge_policy):
        parser.error("Invalid merge policy: %s\nMust be one of %s" % (options.merge_policy, '\n'.join(MergePolicy.ALL)))
    if not options.remote: parser.error("Remote project must be given")
    if options.layers and (options.sourcelayer or options.targetlayer):
        parser.error("Specifying layer indices using --layer is not supported when using --sourcelayer or --targetlayer!")
    if options.sourcelayer and not options.targetlayer:
        parser.error("Merging a layer into a configuration is not supported at the moment!")
    if options.sourcelayer and not options.sourcelayer.lower().endswith('.confml'):
        parser.error("Source layer root should be a .confml file")
    if options.targetlayer and not options.targetlayer.lower().endswith('.confml'):
        parser.error("Target layer root should be a .confml file")
    if not options.sourcelayer and options.targetlayer:
        parser.error("Cannot merge a configuration into a layer!")
    
    # If layers for configuration root merging are not specifically given,
    # the default is the last layer
    if options.layers is None:
        options.layers = [-1]
    
    target_project = api.Project(api.Storage.open(options.project,"a", username=options.username, password=options.password))
    source_project = api.Project(api.Storage.open(options.remote,"r", username=options.username, password=options.password))
    
    print "Target project: %s" % options.project
    print "Source project: %s" % options.remote
    
    target_config = None
    try:
        if options.sourcelayer and options.targetlayer:
            print "Target layer:   %s" % options.targetlayer
            print "Source layer:   %s" % options.sourcelayer
            
            try:
                source_config = source_project.get_configuration(options.sourcelayer)
            except exceptions.NotFound:
                raise MergeFailedException("Layer root '%s' not found in source project" % options.sourcelayer)
            
            try:
                target_config = target_project.get_configuration(options.targetlayer)
            except exceptions.NotFound:
                logger.info('Creating new layer %s' % (options.targetlayer))
                target_config  = target_project.create_configuration(options.targetlayer)
            
            print "Merging layers..."
            merge_configuration_layer(source_config, target_config, options.merge_policy)
        else:
            # Merging a configuration root into a configuration root
            
            if options.all: layer_indices = None
            else:           layer_indices = utils.distinct_array(options.layers)
            
            merge_config_root_to_config_root(
                source_project = source_project,
                target_project = target_project,
                source_config  = options.sourceconfiguration,
                target_config  = options.configuration,
                layer_indices  = layer_indices,
                rename         = options.rename,
                merge_policy   = options.merge_policy)
    except MergeFailedException, e:
        print "Could not merge: %s" % e
        sys.exit(2)
    else:
        # Merge successful, so save the target configuration and project
        # to persist the changes
        if target_config: target_config.save()
        target_project.save()
    
    target_project.close()
    source_project.close()
    

if __name__ == "__main__":
    main()



