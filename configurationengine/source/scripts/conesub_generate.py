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
import logging
from optparse import OptionParser, OptionGroup
import cone_common
import time
from os import path 
from cone.public import api, plugin, utils, exceptions
import generation_report
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

VERSION = '1.0'


def main():    
    parser = OptionParser(version="%%prog %s" % VERSION)
    
    parser.add_options(cone_common.COMMON_OPTIONS)
    
    parser.add_option("-c", "--configuration",\
                        dest="configuration",\
                        help="defines the name of the configuration for the action",\
                        metavar="CONFIG")

    parser.add_option("-p", "--project",\
                       dest="project",\
                       help="defines the location of current project. Default is the current working directory.",\
                       default=".",\
                       metavar="STORAGE")
    
    gen_group = OptionGroup(parser, 'Generate options',
                    'The generate function will create target files from a specific configuration.'\
                    'The generate will always work with read-only mode of the project, so no changes are saved to project')
  
    gen_group.add_option("-o", "--output",\
                   dest="output",\
                   help="defines the target folder where the files are is generated or copied",\
                   metavar="FOLDER",\
                   default="output")

    gen_group.add_option("-l", "--layer",\
                   dest="layers",\
                   type="int",
                   action="append",
                   help="define layers of the configuration that are included to the output. "\
                        "The layer operation can be used several times in a single command."\
                        "Example -l -1 --layer=-2, which would append a layers -1 and -2 to the layers => layers = -1,-2",
                   metavar="LAYER",\
                   default=None)
    
    gen_group.add_option("--all-layers",
                   dest="all_layers",
                   action="store_true",
                   help="Include all layers in generation. This switch overrides all other layer "\
                        "configurations (iMaker API and using the --layer parameter)",
                   default=False)

    gen_group.add_option("-i", "--impl",\
                   dest="impls",\
                   action="append",
                   help=\
"""Define a Python regular expression filter for actual ImplML plugin(s) that needs to be executed. The whole path to ImplML filename is used in the regexp matching.
The impl operation can be used several times in a single command.
                                                                        
Example1 --impl crml => matches for any ImplML file that has a CrML string in the path.
Example2 --impl makeml$ => matches for ImplML file that has ends with MakeML string.
""",
                   metavar="IMPLS",\
                   default=None)

    gen_group.add_option("--impl-tag",\
                   dest="tags",\
                   type="string",
                   action="append",
                   help="define a tag for the implementations that are included to the output. "\
                        "A tag is name value pair and has the following format: name:value, e.g. target:rofs3."\
                        "Example --impl-tag=target:uda --impl-tag=target:content, which would include impls include both tags.",
                   metavar="TAG",\
                   default=None)

    gen_group.add_option("--impl-tag-policy",\
                   dest="tags_policy",\
                   type="string",
                   action="append",
                   help="Policy for implementation tags. May have one of the following values: --impl-tag-policy=AND, --impl-tag-policy=OR. "\
                   "Default is OR.",
                   metavar="TAGS_POLICY",\
                   default=None)
    
    gen_group.add_option("-s", "--set",\
                   dest="overrides",\
                   action="append",
                   type="string",
                   help="Override a ConfML reference in the execution."\
                        "The set operation can be used several times in a single command."\
                        "Example -s foo.bar=10 -s foo.fea='test'.",
                   metavar="SET",\
                   default=None)

    gen_group.add_option("--add",\
                   dest="added",\
                   action="append",
                   type="string",
                   help="Add a given configuration to the given configuration as last element."\
                        "The add operation can be used several times in a single command."\
                        "Example --add foo/root.confml --add bar/root-confml.",
                   metavar="CONF",\
                   default=None)

    gen_group.add_option("-r", "--report",\
                   dest="report",\
                   action="store",
                   type="string",
                   help="Generates a report about settings that are properly generated."\
                        "Example -r report.html.",
                   metavar="FILE",\
                   default=None)

    gen_group.add_option("-t", "--template",\
                   dest="template",\
                   action="store",
                   type="string",
                   help="Template used in report generation."\
                        "Example -t report_template.html.",
                   metavar="FILE",\
                   default=None)
    
    gen_group.add_option("--report-data-output",\
                   type="string",
                   help="Specifies a file where intermediary report data is generated.",
                   metavar="FILE",\
                   default=None)

    gen_group.add_option("-n", "--dryrun",\
                   dest="dryrun",\
                   action="store_true",
                   help="Executes generation without generation output.",
                   default=False)

    gen_group.add_option("--add-setting-file",\
                   dest="settings",\
                   action="append",
                   type="string",
                   help="Generate specific settings in ini format."\
                        "Example -o my_generate_settings.cfg.",
                   metavar="FILE",\
                   default=None)
    
    layers = None
    current = None
    remote = None
    
    start_time = time.time()
    
    parser.add_option_group(gen_group)
    (options, args) = parser.parse_args()

    settinglist = [os.path.join(ROOT_PATH,'conesub_generate.cfg')]
    if options.settings:
        for setting_file in options.settings:
            settinglist.append(os.path.normpath(os.path.join(ROOT_PATH, setting_file)))            
    gset = cone_common.get_settings(settinglist)
    
    cone_common.handle_common_options(options, settings=gset)
          
    current = api.Project(api.Storage.open(options.project,"r"))
    active_root = current.get_storage().get_active_configuration()
    if not options.configuration:
        if active_root == "":
            parser.error("configuration must be given")
        else:
            logging.getLogger('cone').info('No configuration given! Using active root configuration %s' % active_root)
            options.configuration = active_root
    try:
        config  = current.get_configuration(options.configuration)
    except exceptions.NotFound:
        parser.error("No such configuration: %s" % options.configuration)
    reffilters = None
    implfilters = None
    impltags = None
    
    # Include possible additional configurations
    if options.added:
        for configname in options.added:
            logging.getLogger('cone').info('Adding configuration %s' % configname) 
            config.include_configuration(utils.resourceref.norm(configname))
    
    # Get defs from configuration         
    try:
        layer_str_list = (config.get_default_view().get_feature('imakerapi.cone_layers').get_value() or '').split(',')
        # Make sure that empty layers definitions are ignored
        layer_str_list = utils.distinct_array(layer_str_list)
        if '' in layer_str_list:
            layer_str_list.remove('')
        # converting layrs identifiers from strings to int
        layerdefs = []
        for layerstr in layer_str_list:
            try:
                layerdefs.append(int(layerstr))
            except ValueError, e:
                logging.getLogger('cone').error('Invalid layer filter %s' % layerstr)
        implfilters = (config.get_default_view().get_feature('imakerapi.cone_impls').get_value() or '').split(',')
    except exceptions.NotFound:
        layerdefs = []
        implfilters = []
        pass

    # Get filters from command line if they exist => cmd overrides configuration
    if options.layers:
        layerdefs = options.layers
    if options.impls:
        implfilters = options.impls
    if options.tags and len(options.tags) > 0:
        impltags = {}
        for tag in options.tags:
            (name,value) = tag.split(':',2)
            existingvalue = impltags.get(name,[])
            existingvalue.append(value)
            impltags[name] = existingvalue
        logging.getLogger('cone').info('Tag filter %s' % impltags)
    else:
        impltags = None
    
    tags_policy = 'OR'
    if options.tags_policy:
        tags_policy = options.tags_policy[0]
    
    # Finally, --all-layers overrides all other layer settings
    if options.all_layers:
        layerdefs = []
    
    logging.getLogger('cone').info('Layer filter %s' % layerdefs)
    
    # Add reffilters only if the given layerids are somehow reasonable    
    if len(layerdefs) > 0:
        # get the data references from given layers
        logging.getLogger('cone').info('Getting layer specific data reference from %s' % layerdefs)
        reffilters = []
        for layerid in utils.distinct_array(layerdefs): 
            logging.getLogger('cone').info('Searching layer %s' % layerid)            
            layer = config.get_configuration_by_index(layerid)
            refs = _get_new_refs(reffilters, layer.list_leaf_datas())
            logging.getLogger('cone').info("Refs from layer '%s'\n%s" % (layer.get_path(), '\n'.join(refs)))
            reffilters += refs
    

    if options.overrides:
        config.add_configuration(api.Configuration('tempdata.confml'))
        for override in options.overrides:
            (ref,value) = override.split('=',1) 
            config.get_default_view().get_feature(ref).set_value(value)
            
    # Make sure that the output folder exists
    if not os.path.exists(options.output):
        os.makedirs(options.output)

    impls = plugin.filtered_impl_set(config,implfilters)
    impls.output = options.output
    
    logging.getLogger('cone').info("Supported implementation file extensions: %r" % plugin.get_supported_file_extensions())
    
#    logging.getLogger('cone').debug('Loaded implementations:')
#    for impl in impls:
#        msg = "File '%s', impl. type '%s', class '%s', phase '%s'" % \
#              (impl.ref, impl.IMPL_TYPE_ID, type(impl).__name__, impl.invocation_phase())
#        logging.getLogger('cone').debug(msg)
    
    
    # Create temporary variables
    temp_feature_refs = impls.create_temp_features(config)
    if reffilters is not None:
        reffilters.extend(temp_feature_refs)
        logging.getLogger('cone').info('Refs from temporary variables:\n%s' % '\n'.join(temp_feature_refs))
    
    
    
    # ---------------
    # Generate output
    # ---------------
    
    rule_exec_results = []
    
    # Create an implementation container with all the relevant implementations
    all_impls = impls.filter_implementations(tags=impltags, policy=tags_policy)
    
    # Implementations taking part in output generation
    gen_impls = plugin.ImplSet()
    context = plugin.GenerationContext()
    context.configuration = config
    log = logging.getLogger('cone')
    for phase in plugin.ImplSet.INVOCATION_PHASES:
        phase_impls = all_impls.filter_implementations(phase=phase)
        log.info("Generating phase '%s', %d implementation(s)" % (phase, len(phase_impls)))
        
        context.phase = phase
        # No use going any further if there are no implementations
        # for the phase at all
        if len(phase_impls) == 0:
            continue
        
        # Load and execute rules for this phase
        # -------------------------------------
#        relation_container = phase_impls.get_relation_container()
#        log.info("%d rule(s) for phase '%s'" % (relation_container.get_relation_count(), phase))
#        if relation_container.get_relation_count() > 0:
#            log.info("Executing rules...")
#            results = relation_container.execute()
#            log.info("Got %d execution result(s)" % len(results))
#            rule_exec_results.extend(results)
        
        
        # Create an implementation container for the phase with
        # the new reffilters and generate output with it
        # -----------------------------------------------------
        impls = phase_impls.filter_implementations(refs=reffilters)
        log.info("%d implementation(s) after filtering for phase '%s'" % (len(impls), phase))
        if len(impls) > 0:
            if impltags != None:
                context.tags = impltags
                context.tags_policy = tags_policy
            impls.output = options.output
            log.info("Generating output...")
            impls.generate(context)
            impls.post_generate(context)
            
            # Add new refs after generation
#            if reffilters != None and len(reffilters) > 0:
#                layer = config.get_configuration_by_index(-1)
#                new_refs = _get_new_refs(reffilters, layer.list_leaf_datas())
#                log.info('Added %d ref(s) after generation:\n%s' % (len(new_refs), '\n'.join(new_refs)))
#                reffilters += new_refs
            
        # Add new references after each phase execution
        # ---------------------------------------
        if reffilters != None and len(reffilters) > 0:
            layer = config.get_configuration_by_index(-1)
            new_refs = _get_new_refs(reffilters, layer.list_leaf_datas())
            log.info('Added %d ref(s) after phase %s execution:\n%s' % (len(new_refs), phase, '\n'.join(new_refs)))
            reffilters += new_refs
        
        # Add the implementations to the set of implementations participating
        # in output generation (used in the report)
        for impl in impls:
            for actual_impl in impl.get_all_implementations():
                logging.getLogger('cone').info('Adding impl %s' % impl)
                gen_impls.add(actual_impl)
    
    rule_exec_results = context.results
    print "Generated %s to %s!" % (options.configuration, impls.output)
    
    
    # ---------------
    # Generate report
    # ---------------
    
    # If reporting is enabled collect data for report
    if options.report != None or options.report_data_output != None:
        logging.getLogger('cone').info('Collecting data for report.')
        all_refs = reffilters or utils.distinct_array(config.get_configuration_by_index(-1).list_leaf_datas())
        logging.getLogger('cone').info('Collecting data found refs %s' % all_refs)
        logging.getLogger('cone').info('Collecting data found gen_impls %s' % gen_impls)
        rep_data = generation_report.collect_report_data(config, options, all_refs, gen_impls, rule_exec_results)
        logging.getLogger('cone').info('Collecting data found rep_data  %s' % rep_data)
        
        duration = str("%.3f" % (time.time() - start_time) )
        rep_data.set_duration( duration )
        
        # Save intermediary report data file if necessary
        if options.report_data_output != None:
            logging.getLogger('cone').info('Dumping report data to %s' % options.report_data_output)
            print "Dumping report data to '%s'" % options.report_data_output
            generation_report.save_report_data(rep_data, options.report_data_output)
        
        # Generate the report if necessary
        if options.report != None:
            generation_report.generate_report(rep_data, options.report, options.template)
            print_summary(rep_data)
    
    if current: current.close()

def _get_new_refs(old_refs, new_refs):
    """
    Return a distinct array of refs in ``new_refs`` that are not present in ``old_refs``.
    """
    result = []
    for ref in new_refs:
        if ref not in old_refs and ref not in result:
            result.append(ref)
    return result

def print_summary(rep_data):
    """ Prints generation summary to logger and console. """
    print "\nGENERATION SUMMARY:"
    print "--------------------"
    print "Refs in files: %s" % rep_data.nbr_of_refs
    print "Refs with no implementation: %s" % rep_data.nbr_of_refs_noimpl
    print "Generation duration: %s" % rep_data.duration
    print "\n\n"
    

if __name__ == "__main__":
    main()
