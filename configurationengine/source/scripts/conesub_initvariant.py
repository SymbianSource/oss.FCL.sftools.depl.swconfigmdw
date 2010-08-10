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
import tempfile
import os, re
import shutil
                          
from optparse import OptionParser, OptionGroup
import cone_common

from cone.public import api, utils

from conesub_merge import merge_config_root_to_config_root,\
                          get_active_root_if_necessary,\
                          MergePolicy, MergeFailedException
                          
from conesub_export import run_export

VERSION = '1.0'

logger    = logging.getLogger('cone')

class  MetaNotFoundException(Exception):
    pass    

def find_variant_layers_to_merge(source_config, target_config, find_pattern):
    """
    Find all layers in the configuration that contain custvariant* in
    their path name and return a list containing source->target mappings.
    @param source_config: The source configuration object.
    @param target_config: The target configuration object.
    @param new_name: The new name to replace custvariant* in the
        target path name with.
    @return: A list of (source_layer, target_layer) tuples.
    """
    pattern = re.compile(find_pattern)
    
    result = []
    for src in source_config.list_configurations():
        m = pattern.match(src)
        if m:
            result.append(src)
            
    print "Found layers %r" % result
    return result        

def main(argv=sys.argv):
    """ Initialize a variant from a cpf. """
    parser = OptionParser(version="%%prog %s" % VERSION)
    
    parser.add_options(cone_common.COMMON_OPTIONS)

    parser.add_option("-p", "--project",
                       dest="project",
                       help="Defines the location of current project. Default is the current working directory.",
                       default=".",
                       metavar="STORAGE")
    
    group = OptionGroup(parser, 'Initvariant options',
                        'The initvariant action is intended for merging a variant CPF back into the '
                        'configuration project, or creating a new empty variant based on an existing '
                        'configuration. It merges all customer variant layers (layers with '
                        'custvariant* in their path name) and renames them based on the variant ID '
                        'and variant name ("custvariant_<id>_<name>").')
    
    group.add_option("-c", "--configuration",
                        dest="configuration",
                        help="Defines the name of the target configuration. By default the "
                             "configuration file name is composed of product name, variant ID "
                             "and variant name like this: <product>_custvariant_<id>_<name>_root.confml",
                        metavar="CONFIG")
    
    group.add_option("-r", "--remote",
                   dest="remote",
                   help="Defines the location of remote storage (CPF)",
                   metavar="STORAGE")
    
    group.add_option("-s", "--sourceconfiguration",
                        dest="sourceconfiguration",
                        help="Defines the name of the remote configuration inside the remote storage. "
                             "Default is the active root of the remote project.",
                        metavar="CONFIG")
    
    group.add_option("--variant-id", help="Variant ID, mandatory.")
    group.add_option("--variant-name", help="Variant name, optional.")
    group.add_option("--product-name",
                     help="Product name, taken from the configuration data by default "
                          "(i.e. defaults to '${imakerapi.productname}')",
                     default="${imakerapi.productname}")
    
    group.add_option("--set-active-root",
                     action="store_true",
                     help="Set the newly created (or update) configuration root as the "
                          "project's active root after the merge is done.")
    
    group.add_option("-b","--based-on-configuration",
                     dest="boconfig",
                   help="Defines the configuration root which is used as a base "
                        "configuration for the new empty variant.")
    
    group.add_option("--find-layer-regexp",
                     dest="find_pattern",
                     default='.*/manual/.*|.*/configurator/.*',
                     help="Defines the pattern which is used to find the layers "
                          "from source configuration that will be merged"
                          "Default: '.*/manual/.*|.*/configurator/.*' " )
        
    parser.add_option_group(group)
    (options, _) = parser.parse_args(argv)
    
    cone_common.handle_common_options(options)
    
    # Check the passed options
    if not options.remote and not options.boconfig:
        parser.error("Remote project or based-on-configuration must be given")
    if options.remote and options.boconfig:
        parser.error("Only either remote project or based-on-configuration can be given, but not both")
    if not options.variant_id:  parser.error("Variant ID must be given")
    
    temp_cpf_folder = None
    
    if options.boconfig:   
        class ExportOptions(object):
            pass
            
        path = ''
        coreplat_name = ''
        product = ''
        
        project = api.Project(api.Storage.open(options.project,"a", username=options.username, password=options.password))
        config = project.get_configuration(options.boconfig)
        meta = config.meta
        
        if meta:
            for prop in meta.array:
                if 'name' in prop.attrs and 'value' in prop.attrs:
                    name = prop.attrs['name']
                    if name == 'coreplat_name':
                        coreplat_name =  prop.attrs['value']
                    if name == 'product_name':
                        product = prop.attrs['value']
        
        if not coreplat_name or not product:
            print >>sys.stderr, "Could not find coreplat_name or product_name from meta data."
            print >>sys.stderr, "Are you sure the given based-on-configuration is valid?"
            sys.exit(2)
        
        path = coreplat_name + '/' + product        
                    
        temp_cpf_folder = tempfile.mkdtemp()
        
        export_options = ExportOptions()
        export_options.project = options.project
        export_options.remote = os.path.join(temp_cpf_folder, 'temp.cpf')
        export_options.configs = [options.boconfig]
        export_options.username = options.username
        export_options.password = options.password
        export_options.config_wildcards = None
        export_options.config_regexes   = None
        export_options.export_dir = None
        export_options.exclude_content_filter = None
        export_options.added = [path + '/customer/custvariant/manual/root.confml',
                                path + '/customer/custvariant/configurator/root.confml']
        export_options.exclude_empty_folders = False
        export_options.action = None
                
        options.remote = export_options.remote
        
        print "Exporting variant CPF to a temporary directory"
        run_export(export_options)

    target_project = api.Project(api.Storage.open(options.project,"a", username=options.username, password=options.password))
    source_project = api.Project(api.Storage.open(options.remote,"r", username=options.username, password=options.password))

    print "Target project: %s" % options.project
    print "Source project: %s" % options.remote
    replace_dict = {"VAR_ID": options.variant_id, "VAR_NAME": options.variant_name}    
    
    try:
        # Open the source configuration
        source_config = get_active_root_if_necessary(source_project, options.sourceconfiguration, 'source')
        source_config = source_project.get_configuration(source_config)
        
        # Determine the new name of the layer part (replaces 'custvariant[^/]*')
        if options.variant_name:
            new_name = "custvariant_%s_%s" % (options.variant_id, options.variant_name)
        else:
            new_name = "custvariant_%s" % options.variant_id
        
        # Determine the target configuration
        if options.configuration:
            target_config = options.configuration
        else:
            # Target configuration not given explicitly, automatically
            # determine the name based on the product name and the new
            # layer name
            try:
                product_name = utils.expand_refs_by_default_view(
                    options.product_name,
                    source_config.get_default_view(),
                    catch_not_found = False)
            except Exception, e:
                print "Could not determine product name: %s" % e
                sys.exit(2)
            print "Product name:   %s" % product_name
            target_config = "%s_%s_root.confml" % (product_name, new_name)
        
        
        def find_layers(source_config, target_config):
            ret_list = []
            
            layers = find_variant_layers_to_merge(source_config,
                                                target_config,
                                                options.find_pattern)            
            p = re.compile(r'custvariant[^/]*')
            for layer in layers:
                tgt_layer = p.sub(new_name, layer) 
                ret_list.append((layer, tgt_layer))
            
            return ret_list
        
        # Perform the merge
        merge_config_root_to_config_root(
            source_project      = source_project,
            target_project      = target_project,
            source_config       = options.sourceconfiguration,
            target_config       = target_config,
            layer_finder_func   = find_layers,
            merge_policy        = MergePolicy.OVERWRITE_LAYER)
        
        if options.set_active_root:
            target_project.get_storage().set_active_configuration(target_config)
    except MergeFailedException, e:
        print "Could not initialize variant: %s" % e
        sys.exit(2)
    else:
        # Merge successful, so save the target project
        # to persist the changes
        target_project.save()
    
    target_project.close()
    source_project.close()
    
    if temp_cpf_folder:
        logger.debug("Removing temporary CPF directory '%s'" % temp_cpf_folder)
        shutil.rmtree(temp_cpf_folder)
    

if __name__ == "__main__":
    main()
