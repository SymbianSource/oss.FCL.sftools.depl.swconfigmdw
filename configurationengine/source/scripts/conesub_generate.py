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

import os, re, fnmatch
import logging
from optparse import OptionParser, OptionGroup
import cone_common
import time
from distutils.dir_util import mkpath, DistutilsFileError
from cone.public import api, plugin, utils, exceptions
from cone.report import generation_report
from cone.confml import persistentconfml
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

VERSION = '1.0'

log = logging.getLogger('cone')

def main():
    """ Generate a configuration. """
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

    gen_group.add_option("--report-option",\
                   action="append",
                   help="Specifies the report verbose options, that defines "\
                        "what data is included to the report. The option can be "\
                        "used multiple times."\
                        "choises=[default|all]"\
                        "Example --report-option=all",
                   metavar="OPTION",\
                   default=[])

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
    gen_group.add_option("--dump-autodata",\
                   dest="dump_autodata",\
                   action="store",
                   type="string",
                   metavar="FILE",
                   help="Specifies a confml file for storing autodata.confml permanently.",
                   default=None)
    gen_group.add_option("-w", "--what",\
                   dest="what",\
                   action="store",
                   type="string",
                   metavar="FILE",
                   help="List output files to a txt file",
                   default=None)
    
    lf_group = OptionGroup(parser, 'Layer filtering options',
                    'Layer filtering options define configuration layers to be used for filtering '\
                    'the implementations that are used to generate output. Filtering by a layer means that '\
                    'only implementations that generate their output based on settings changed on that layer '\
                    'are included in the generation.')
    
    lf_group.add_option("-l", "--layer",\
                   dest="layers",\
                   type="int",
                   action="append",
                   help="Define a layer by giving its index in the root configuration. "\
                        "0 is first, 1 the second, -1 the last, -2 the second to last and so on. "\
                        "The layer operation can be used several times in a single command. "\
                        "Example -l -1 --layer=-2, which would append a layers -1 and -2 to the layers => layers = -1,-2",
                   metavar="LAYER",\
                   default=None)
    
    lf_group.add_option("--layer-regex",
                   dest="layer_regexes",
                   action="append",
                   help="Define a regular expression for including layers into the generation process, "\
                        "e.g. --layer-regex layer[0-9]/root.confml. The pattern is matched against the layer root "\
                        "path, which could be e.g. 'assets/layer1/root.confml'.",
                   metavar="REGEX",)
    
    lf_group.add_option("--layer-wildcard",
                   dest="layer_wildcards",
                   action="append",
                   help="Define a wildcard for including layers into the generation process, e.g "\
                        "--layer-wildcard layer*",
                   metavar="WILDCARD",)
    
    lf_group.add_option("--all-layers",
                   dest="all_layers",
                   action="store_true",
                   help="Include all layers in generation. This switch overrides all other layer "\
                        "configurations (iMaker API and using the --layer, --layer-regex and --layer-wildcard parameters)",
                   default=False)
    
    
    start_time = time.time()
    
    parser.add_option_group(gen_group)
    parser.add_option_group(lf_group)
    (options, _) = parser.parse_args()

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
    
    # Get implementation filters from configuration
    try:
        implfilters = (config.get_default_view().get_feature('imakerapi.cone_impls').get_value() or '').split(',')
    except exceptions.NotFound:
        implfilters = []
    
    # Get filters from command line if they exist => cmd overrides configuration
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
    
    
    layerdefs = _get_included_layers(config, options, parser)
    filter_by_refs = _filter_by_refs(config, options, parser)
    
    if layerdefs:
        logging.getLogger('cone').info('Included layers:\n%s' % '\n'.join(layerdefs))
    else:
        logging.getLogger('cone').info('Including all layers')
    
    dview = config.get_default_view()
    # Add data references if included layers are defined
    if len(layerdefs) > 0:
        # get the data references from given layers
        logging.getLogger('cone').info('Getting layer specific data reference from %s' % layerdefs)
        reffilters = []
        for layer_path in utils.distinct_array(layerdefs):
            logging.getLogger('cone').info('Searching layer %s' % layer_path)
            layer = config.get_configuration(layer_path)
            refs = _get_new_refs(reffilters, layer.list_leaf_datas())
            # reduce the refs of sequences to single reference of the sequence feature
            layerrefs = set() 
            for fea in dview.get_features(refs):
                layerrefs.add(fea.fqr)
                if fea.is_sequence():
                    layerrefs.add(fea.get_sequence_parent().fqr)
            
            refs = sorted(list(layerrefs))
            #logging.getLogger('cone').info("Refs from layer '%s'\n%s" % (layer.get_path(), '\n'.join(refs)))
            reffilters += refs
          
    # Make sure that the output folder exists
    if not os.path.exists(options.output):
        os.makedirs(options.output)
        
    impls = plugin.filtered_impl_set(config,implfilters)
    impls.output = options.output
    
    log.info("Parsed %s implementation(s)" % len(impls))
    
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
    
    # Set overrides only after temp variables are created, so that
    # they can also be modified from the command line
    if options.overrides:
        # Make sure that the last layer is the autodata layer
        plugin.get_autoconfig(config)
        for override in options.overrides:
            (ref,value) = override.split('=',1)
            config.get_default_view().get_feature(ref).set_value(value)
    
    
    # ---------------
    # Generate output
    # ---------------
    
    context = plugin.GenerationContext(configuration = config,
                                       tags = impltags or {},
                                       tags_policy = tags_policy,
                                       output = options.output,
                                       impl_set = impls,
                                       temp_features = temp_feature_refs,
                                       filter_by_refs = filter_by_refs)
    context.changed_refs = reffilters
    context.output = options.output

    impls.output = options.output
    for phase in impls.INVOCATION_PHASES:
        log.info("Generating phase '%s'" % phase)
        context.phase = phase
        impls.generate(context)
        impls.post_generate(context)
     
    if options.what:
        log.info("Write output files to '%s'" % options.what)
        output_files = []
        for op in context.get_output():
            # Only append once
            if op.type == 'file' and output_files.count(op.abspath) < 1:
                output_files.append(op.abspath)       
        try:
            mkpath(os.path.dirname(os.path.abspath(options.what)))
            what_fh = open(os.path.abspath(options.what), 'w')
            try:
                [what_fh.write('%s\n' % ofile) for ofile in output_files]
                print "Wrote output file list to '%s'" % options.what
            finally:
                what_fh.close()
        except Exception:
            log.info("Could not create directory for '%s'" % options.what)
    
    print "Generated %s to %s!" % (options.configuration, impls.output)
    
    # Store temporary rule execution outputs to a new configuration
    if options.dump_autodata:
        # Make sure autodata layer is the one we're dealing with     
        plugin.get_autoconfig(config)
        lastconfig = config.get_last_configuration()
        lastconfig.set_name(utils.resourceref.to_objref(utils.resourceref.get_filename(utils.resourceref.norm(options.dump_autodata))))
        data = persistentconfml.dumps(lastconfig)
        try:
            mkpath(utils.resourceref.get_path(utils.resourceref.norm(options.dump_autodata)))
            fh = open(options.dump_autodata, 'w')
            try:        fh.write(data)
            finally:    fh.close()
            print 'Saved autodata to %s' % options.dump_autodata
        except DistutilsFileError:
            log.info('Unable to dump autodata')
        
    
    # ---------------
    # Generate report
    # ---------------

    # If reporting is enabled collect data for report
    if options.report != None or options.report_data_output != None:
        logging.getLogger('cone').info('Collecting data for report.')
        
        rep_data = generation_report.ReportData() 
        rep_data.context = context
        rep_data.context.log_file = os.path.abspath(options.log_file)
        rep_data.context.log = _read_log(options.log_file)
        rep_data.project_dir = options.project
        logging.getLogger('cone').info('Collecting data found rep_data  %s' % rep_data)
        
        duration = str("%.3f" % (time.time() - start_time) )
        rep_data.set_duration( duration )
        rep_data.options = options
        
        # Save intermediary report data file if necessary
        if options.report_data_output != None:
            logging.getLogger('cone').info('Dumping report data to %s' % options.report_data_output)
            print "Dumping report data to '%s'" % options.report_data_output
            generation_report.save_report_data(rep_data, options.report_data_output)
        
        # Generate the report if necessary
        if options.report != None:
            generation_report.generate_report([rep_data], options.report, options.template, [ROOT_PATH], options.report_option)
            print_summary(rep_data)
    
    if current: current.close()

def _read_log(log_file):
    logf = open(log_file)
    # strip endlines
    return [line.strip('\n') for line in logf.readlines()]
    
def _get_new_refs(old_refs, new_refs):
    """
    Return a distinct array of refs in ``new_refs`` that are not present in ``old_refs``.
    """
    result = []
    for ref in new_refs:
        if ref not in old_refs and ref not in result:
            result.append(ref)
    return result


def _filter_by_refs(config, options, parser):
    """
    """
    filter_by_refs = True
    if options.all_layers:
        filter_by_refs = False 
    elif not options.layers and not options.layer_regexes and not options.layer_wildcards:
        filter_by_refs = False
    return filter_by_refs

def _get_included_layers(config, options, parser):
    """
    Collect a list of included layer root paths from the config based on the
    given parameters in options.
    @return: A list of layer configuration paths (empty if all layers
        should be generated).
    """
    # --all-layers overrides all other definitions
    if options.all_layers:
        options.layers = [i for i in range(len(config.list_configurations()))] 
    elif not options.layers and not options.layer_regexes and not options.layer_wildcards:
        options.layers = [i for i in range(len(config.list_configurations()))]
    
    # Command line definitions override others
    if options.layers or options.layer_regexes or options.layer_wildcards:
        layer_paths = []
        all_layers = config.list_configurations()
        
        for layer_index in options.layers or []:
            try:
                layer_paths.append(all_layers[int(layer_index)])
            except (IndexError, ValueError):
                parser.error("Invalid layer index: %s" % layer_index)
        
        for regex in options.layer_regexes or []:
            for layer_path in all_layers:
                if re.search(regex, layer_path):
                    layer_paths.append(layer_path)
        
        for wildcard in options.layer_wildcards or []:
            for layer_path in all_layers:
                if fnmatch.fnmatch(layer_path, wildcard):
                    layer_paths.append(layer_path)
        
        if not layer_paths:
            parser.error('No layers matched by layer patterns')
        
        return utils.distinct_array(layer_paths)
    
    # Use iMaker API definitions if no others have been specified
    return _get_included_layers_from_imaker_api(config, parser)

def _get_included_layers_from_imaker_api(config, parser):
    try:
        layer_str_list = (config.get_default_view().get_feature('imakerapi.cone_layers').get_value() or '').split(',')
        # Make sure that empty layers definitions are ignored
        layer_str_list = utils.distinct_array(layer_str_list)
        if '' in layer_str_list:
            layer_str_list.remove('')
        
        all_layers = config.list_configurations()
        layerdefs = []
        for layerstr in layer_str_list:
            try:
                layerdefs.append(all_layers[int(layerstr)])
            except (ValueError, IndexError):
                parser.error("Invalid layer index from iMaker API: %s" % layerstr)
        return layerdefs
    except exceptions.NotFound:
        return []

def print_summary(rep_data):
    """ Prints generation summary to logger and console. """
    print "\nGENERATION SUMMARY:"
    print "--------------------"
    print "Refs in files: %s" % len(rep_data.context.changed_refs)
    print "Refs with no implementation: %s" % len(rep_data.context.get_refs_with_no_output())
    print "Generation duration: %s" % rep_data.duration
    print "\n\n"
    

if __name__ == "__main__":
    main()
