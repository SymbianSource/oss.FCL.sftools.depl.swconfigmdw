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
import logging
import pickle
from optparse import OptionParser, OptionGroup
import cone_common
import generation_report
from cone.public import api, plugin, utils, exceptions


VERSION     = '1.0'

logger    = logging.getLogger('cone')

def main():
    parser = OptionParser(version="%%prog %s" % VERSION)
    
    parser.add_options(cone_common.COMMON_OPTIONS)
    
    group = OptionGroup(parser, 'Report options',
                        'The report function generates a report using previously generated '\
                        'intermediary report data as input.')
    
    group.add_option("-i", "--input-data",\
                        action="append",\
                        help="Defines an input file for report generation. "\
                             "If specified more than once, the data of all specified "\
                             "report data files is merged.",
                        metavar="FILE",
                        default=[])
    
    group.add_option("-d", "--input-data-dir",\
                        help="Defines a directory containing the data files to use for "\
                             "generating the report. This is an alternative to specifying "\
                             "a number of --input-data files. The order of the data files "\
                             "is determined by the generation time stamps found in the data "\
                             "files.",
                        metavar="DIR",
                        default=None)
    
    group.add_option("-r", "--report",\
                   dest="report",\
                   action="store",
                   type="string",
                   help="Specifies the report file to create."\
                        "Example -r report.html.",
                   metavar="FILE",\
                   default="report.html")
    
    group.add_option("-t", "--template",\
                   dest="template",\
                   action="store",
                   type="string",
                   help="Template used in report generation."\
                        "Example -t report_template.html.",
                   metavar="FILE",\
                   default=None)
    
    parser.add_option_group(group)
    (options, args) = parser.parse_args()
    
    cone_common.handle_common_options(options)
    
    if len(options.input_data) == 0 and not options.input_data_dir:
        parser.error("Input data must be specified with either --input-data or --input-data-dir")
    if len(options.input_data) > 0 and options.input_data_dir:
        parser.error("Both --input-data and --input-data-dir specified, use one or the other.")
    if options.input_data_dir and not os.path.isdir(options.input_data_dir):
        parser.error('Given --input-data-dir does not exist or is not a directory.')
    
    if options.input_data:
        files = options.input_data
    else:
        files = get_input_data_files(options.input_data_dir)
    
    if len(files) == 0:
        parser.error("At least one input data file must be specified.")
    
    
    class DataEntry(object):
        def __init__(self, label, data):
            self.label = label
            self.data = data
    
    # Load all data files
    data_entries = []
    for data_file in files:
        print "Loading data file '%s'" % data_file
        label = get_generation_run_label(data_file)
        data = generation_report.load_report_data(data_file)
        data_entries.append(DataEntry(label, data))
    
    # Sort by time stamp
    data_entries.sort(key=lambda entry: entry.data.generation_timestamp)
    
    # Use the first data object as the main report data
    main_entry = data_entries[0]
    
    # Merge the rest of the data objects into the main data
    if len(data_entries) > 1:
        # Update the generation_runs attribute of all implementations
        # in the main data
        for line in main_entry.data.lines:
            for impl in line.impls:
                impl.generation_runs = [main_entry.label]
         
        # Load other report data files and merge them to the main data object
        for i in xrange(len(data_entries) - 1):
            entry = data_entries[i + 1]
            print "Merging data for '%s'" % entry.label
            merge_report_data(main_entry.data, entry.data, entry.label)
 
    # Generate the report
    main_entry.data.report_filename = options.report
    generation_report.generate_report(main_entry.data, options.report, options.template)
    
    print "Generated report to '%s'" % options.report

def get_input_data_files(directory):
    files = []
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        if os.path.isfile(path):
            files.append(path)
    return files
    

def get_generation_run_label(datafile_path):
    filename = os.path.split(datafile_path)[1]
    filename_noext = os.path.splitext(filename)[0]
    return filename_noext

def get_feature(rep_data, ref):
    for feat in rep_data.lines:
        if feat.ref == ref:
            return feat
    raise RuntimeError("Feature '%s' not found in refs with impl" % ref)

def get_impl(rep_data, ref, impl_name):
    feat = get_feature(rep_data, ref)
    for impl in feat.impls:
        if impl.name == impl_name:
            return impl
    raise RuntimeError("Impl '%s' not found for feature '%s'" % (impl_name, ref))

def merge_report_data(data, data_to_merge, generation_run_label):
    impls_by_ref = {}
    for feat in data.lines:
        impls_dict = {}
        impls_by_ref[feat.ref] = impls_dict
        for impl in feat.impls:
            impls_dict[impl.name] = impl
    
    for feat in data_to_merge.lines:
        if feat.ref in impls_by_ref:
            # Feature has implementations in both report data objects
            # -------------------------------------------------------
            impls_dict = impls_by_ref[feat.ref]
            
            for impl in feat.impls:
                if impl.name in impls_dict:
                    # Same implementation in both: add the generation run to merge to the impl
                    impl = get_impl(data, feat.ref, impl.name)
                    impl.generation_runs.append(generation_run_label)
                else:
                    # Implementation only in the data to merge: add to the main data
                    impl = get_impl(data_to_merge, feat.ref, impl.name)
                    impl.generation_runs = [generation_run_label]
                    feat = get_feature(data, feat.ref)
                    feat.impls.append(impl)
                    feat.nbr_impls += 1
        else:
            # Feature has implementations only in the data to merge
            # -----------------------------------------------------
            
            # Add the feature and impls to the main data
            feat = get_feature(data_to_merge, feat.ref)
            for impl in feat.impls:
                impl.generation_runs = [generation_run_label]
            data.lines.append(feat)
            data.nbr_of_refs += 1
            
            # Remove from features with no impl in the main data
            for i, noimpl_feat in enumerate(data.ref_noimpl):
                if feat.ref == noimpl_feat.ref:
                    del data.ref_noimpl[i]
                    data.nbr_of_refs_noimpl -= 1
                    break

if __name__ == "__main__":
    main()
