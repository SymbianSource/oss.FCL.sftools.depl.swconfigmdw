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
import codecs

import cone_common
import time

from cone.public import api, plugin, utils, exceptions
from time import gmtime, strftime
from cone.report import report_util
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

VERSION = '1.0'

log = logging.getLogger('cone')

REPORT_SHORTCUTS = {
    'api': report_util.ReportShortcut(
        os.path.join(ROOT_PATH, 'compare_api_report_template.html'),
        'api_comparison.html',
        'Report changes in feature definitions'),
                       
    'ci': report_util.ReportShortcut(
        os.path.join(ROOT_PATH, 'compare_ci_report_template.html'),
        'ci_comparison.html',
        'Report changes in CustomisationInterface definitions'),

    'data': report_util.ReportShortcut(
        os.path.join(ROOT_PATH, 'compare_data_report_template.html'),
        'data_comparison.html',
        'Report changes in data values'),
                       
    'crml_dc': report_util.ReportShortcut(
        os.path.join(ROOT_PATH, 'crml_dc_report_template.html'),
        'crml_dc_report.html',
        'Report CRML data compatibility issues'),
                       
    'crml_dc_csv': report_util.ReportShortcut(
        os.path.join(ROOT_PATH, 'crml_dc_report_template.csv'),
        'crml_dc_report.csv',
        'Report CRML data compatibility issues (CSV format)'),
}
DEFAULT_SHORTCUT = 'data'

def main():
    """ Compare two configurations """
    shortcut_container = report_util.ReportShortcutContainer(REPORT_SHORTCUTS,
                                                             DEFAULT_SHORTCUT)
    
    gset = cone_common.get_settings([os.path.join(ROOT_PATH,'conesub_compare.cfg')])

    parser = OptionParser(version="%%prog %s" % VERSION)
    
    parser.add_options(cone_common.COMMON_OPTIONS)
    
    parser.add_option("-p", "--project",\
                       dest="project",\
                       help="defines the location of current project. Default is the current working directory.",\
                       default=".",\
                       metavar="STORAGE")
    
    group = OptionGroup(parser, 'Compare options',
                    'The generate function will create target files from a specific configuration.'\
                    'The generate will always work with read-only mode of the project, so no changes are saved to project')
    
    group.add_option("-s", "--sourceconfiguration",\
                        dest="sourceconfiguration",\
                        help="defines the name of the sourceconfiguration for the compare action. "\
                             "The configuration is expected to be located current storage.",\
                        metavar="CONFIG")
    
    group.add_option("-t", "--targetconfiguration",\
                        dest="targetconfiguration",\
                        help="defines the name of the target configuration for the compare action. "\
                             "The configuration can be located in the current storage or it the configuration"\
                             "definition can contain a path to a storage. The storage definition is given as a path"\
                             "before semicolon. e.g. x:\data\configproject;productx.confml, test.cpf;root.confml",\
                        metavar="CONFIG")

#    group.add_option("--compare-dict",\
#                   dest="compare_dict",\
#                   action="store",
#                   type="string",
#                   help="Compare elements as a dictionary",
#                   metavar="DICT",\
#                   default=None)

    group.add_option("--report",\
                   dest="report_file",\
                   action="store",
                   type="string",
                   help="The file where the comparison report is written."\
                        "By default this value is determined by the used "\
                        "report type. Example: --report report.html.",
                   metavar="FILE",\
                   default=None)

    group.add_option("--template",\
                   dest="template",\
                   action="store",
                   type="string",
                   help="Template used in a report generation. By default "\
                        "this value is determined by the used report type. "\
                        "Example: --template report_template.html.",
                   metavar="FILE",\
                   default=None)
    
    group.add_option("--report-type",
                   dest="report_type",
                   action="store",
                   type="string",
                   help="The type of the report to generate. This is a convenience "\
                        "switch for setting the used template.                     "\
                        "Possible values:\n                                      "\
                        + shortcut_container.get_shortcut_help_text(),
                   metavar="TYPE",\
                   default=None)
    
    group.add_option("--impl-filter",\
                   dest="impl_filter",\
                   action="store",
                   type="string",
                   help="The pattern used for filtering implementations for the "\
                        "comparison. See the switch --impl in action generate for "\
                        "more info. ",
                   metavar="PATTERN",\
                   default=None)
    
    start_time = time.time()
    
    parser.add_option_group(group)
    (options, args) = parser.parse_args()
    
    cone_common.handle_common_options(options, settings=gset)
    
    if not options.sourceconfiguration: parser.error("sourceconfiguration must be given")
    if not options.targetconfiguration: parser.error("targetconfiguration must be given")
    if options.report_type and options.template:
        parser.error("both --report-type and --template supplied; use only one of them")
    if not shortcut_container.is_valid_shortcut(options.report_type):
        parser.error("Invalid report type: %s" % options.report_type)
    
    template_file, report_file = shortcut_container.determine_template_and_report(
        options.report_type,
        options.template,
        options.report_file,
        'comparison')
    
    action = CompareAction(options.project,
                           options.sourceconfiguration,
                           options.targetconfiguration,
                           template    = template_file,
                           report_file = report_file,
                           impl_filter = options.impl_filter)
    result = action.run_action()
    
    resmap = {True: 0, False: 1}
    sys.exit(resmap[result])



class CompareAction(object):
    
    def __init__(self, current, sourceconfig, targetconfig, **kwargs):
        self.current = current
        self.sourceconfig = sourceconfig
        self.targetconfig = targetconfig
        self.reportfile = kwargs.get("report_file", 'compare.html')
        self.reporttemplate = kwargs.get('template', '')
        self.columns = kwargs.get('columns', None)
        self.impl_filter = kwargs.get('impl_filter',)

    def run_action(self):
        """
        Run the action.
        @return: True if successful, False if not.
        """
        
        currentprj = api.Project(api.Storage.open(self.current,"r"))
        targetprj = None
        (targetproject,targetconf) = self.parse_target_configuration(self.targetconfig)
        print "Compare %s <> %s in %s" % (self.sourceconfig, targetconf, targetproject)
        if targetproject != '':
            targetprj = api.Project(api.Storage.open(targetproject,"r"))
        else:
            # The comparison doesn't seem to work if the same project
            #    object is used
            #targetprj = currentprj
            targetprj = api.Project(api.Storage.open(self.current,"r"))
            
        source = currentprj.get_configuration(self.sourceconfig)
        target = targetprj.get_configuration(targetconf)

        print "Writing report to %s" % self.reportfile
        sourcedata = {}
        targetdata = {}
        sourcedata['name'] = self.sourceconfig
        targetdata['name'] = self.targetconfig
        sourcedata['features'] = self.get_feature_api_data(source)
        targetdata['features'] = self.get_feature_api_data(target)
        
        impl_comp_data_proxy = ImplComparisonDataProxy(source,
                                                       target,
                                                       self.impl_filter)
        
        template_data = {'sourcedata': sourcedata,
                         'targetdata': targetdata,
                         'impl_data':  impl_comp_data_proxy}
        
        result = report_util.generate_report(self.reporttemplate,
                                             self.reportfile,
                                             {'data': template_data})
        print "Done."
        return result
        
    def parse_target_configuration(self,configpath):
        """
        return tuple (storage, configpath) from storagepath;root.confml.
        returns ('', 'root.confml') from root.confml 
        """
        elems = configpath.rsplit(';',2)
        if len(elems) > 1:
            return (elems[0],elems[1])
        else:
            return ('',elems[0])

    def get_feature_api_data(self,config):
        # Traverse through all features in the api
        # and construct the data rows
        data = {}
        for elem in config.get_default_view().get_features('**'):
            data[elem.fqr] = elem._obj
        return data

class ImplComparisonDataProxy(object):
    """
    Proxy object for loading implementation comparison data on demand.
    """
    def __init__(self, sourceconfig, targetconfig, impl_filter):
        self.sourceconfig = sourceconfig
        self.targetconfig = targetconfig
        if impl_filter is None: self.impl_filter = '.*'
        else:                   self.impl_filter = impl_filter
        
        self._flat_data = None
    
    @property
    def flat(self):
        try:
            if self._flat_data is None:
                self._flat_data = self._get_flat_comparison_data()
            return self._flat_data
        except Exception, e:
            utils.log_exception(log, 'Error retrieving ImplComparisonDataProxy.flat!')
            raise
    
    def _get_flat_comparison_data(self):
        log.debug("Loading implementations for comparison (impl filter = '%s')..." % (self.impl_filter))
        
        try:
            source_impls = plugin.get_impl_set(self.sourceconfig, self.impl_filter)
            target_impls = plugin.get_impl_set(self.targetconfig, self.impl_filter)
        except Exception, e:
            utils.log_exception(log, 'Failed to load implementations!')
            raise
        
        log.debug("%d impl(s) in source." % len(source_impls))
        log.debug("%d impl(s) in target." % len(target_impls))
        
        log.debug("Generating flat comparison results...")
        result = source_impls.flat_compare(target_impls)
        log.debug("Generated %d result row(s)" % len(result))
        return result

if __name__ == "__main__":
    main()
