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
from optparse import OptionParser, OptionGroup
import cone_common
from cone.report import generation_report


VERSION     = '1.0'
ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

logger    = logging.getLogger('cone')

def main():
    """ Create report of existing report data. """
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
    
    group.add_option("--report-option",\
                   action="append",
                   help="Specifies the report verbose options, that defines "\
                        "what data is included to the report. The option can be "\
                        "used multiple times."\
                        "choises=[default|all]"\
                        "Example --report-option=all",
                   metavar="OPTION",\
                   default=[])

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
    
    
    
    # Load all data files
    data_reports = []
    for data_file in files:
        print "Loading data file '%s'" % data_file
        data = generation_report.load_report_data(data_file)
        data_reports.append(data)
    
    # Sort by time stamp
    data_reports.sort(key=lambda entry: entry.generation_timestamp)
    
    # Generate the report
    print "Generating report to '%s'" % options.report
    generation_report.generate_report(data_reports, options.report, options.template, [ROOT_PATH], options.report_option)
    
    print "Done!'"

def get_input_data_files(directory):
    files = []
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        if os.path.isfile(path):
            files.append(path)
    return files


if __name__ == "__main__":
    main()
