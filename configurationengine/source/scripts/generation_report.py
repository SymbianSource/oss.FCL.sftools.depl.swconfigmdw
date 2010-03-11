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

import os, logging, pickle
import time
from time import gmtime, strftime
from jinja2 import Environment, PackageLoader, FileSystemLoader, Template
from cone.public import api, exceptions, utils, plugin
from cone.confml import model
import report_util

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

def save_report_data(rep_data, file_path):
    """
    Save report data into an intermediary report data file.
    """
    dir = os.path.dirname(file_path)
    if dir != '' and not os.path.exists(dir):
        os.makedirs(dir)
    
    pickle_data = pickle.dumps(rep_data)
    f = open(file_path, 'wb')
    try:        f.write(pickle_data)
    finally:    f.close()

def load_report_data(file_path):
    """
    Load report data from an intermediary report data file.
    """
    f = open(file_path, "rb")
    try:        data = f.read()
    finally:    f.close()
    
    return pickle.loads(data)

def _get_parent_sequence_or_self(feature):
    current = feature._parent
    while current is not None:
        if isinstance(current, api.FeatureSequence):
            return current
        current = current._parent
    return feature

def collect_report_data(config, options, all_refs, impl_set, rule_exec_results):
    """
    Collect data for report generation.
    """
    impls = impl_set.get_all_implementations()
    impls.sort(key=lambda impl: (impl.ref, impl.index))
    rep_data = ReportData()
    
    # Sort the rule results for unit testing purposes
    rep_data.rule_exec_results = sorted(rule_exec_results, key=lambda e: (e.source, e.index))
    
    # Collect a dictionary that maps refs shown in the report to a list of
    # actual sub-refs used in the generation.
    # This is done because for sequence settings only an entry for the main
    # sequence setting is shown, but the actual refs used in generation point
    # to the individual sub-settings (and possibly even under them).
    # An example entry in the dictionary could be
    #   'MyFeature.MySequence' : ['MyFeature.MySequence.Name',
    #                             'MyFeature.MySequence.File.localPath',
    #                             'MyFeature.MySequence.File.targetPath']
    dview = config.get_default_view()
    refs_dict = {}
    for ref in all_refs:
        try:
            feature = dview.get_feature(ref)
        except exceptions.NotFound:
            logging.getLogger('cone.generation_report').warning("Feature for data ref not found: %s" % ref)
            continue
        
        feature = _get_parent_sequence_or_self(feature._obj)
        ref_to_report = feature.fqr
        
        if ref_to_report not in refs_dict:
            refs_dict[ref_to_report] = []
        refs_dict[ref_to_report].append(ref)
    
#    msg = []
#    for ref, sub_refs in refs_dict.iteritems():
#        msg.append("Ref: %s\nSub-refs:\n%s" % (ref, '\n'.join(sub_refs)))
#    logging.getLogger('cone').debug('\n--------------------------------------\n'.join(msg))
    
    # Go through the refs and create report data entries
    for ref in sorted(refs_dict.iterkeys()):
        sub_refs = refs_dict[ref]
        
        #print "Ref: %s" % ref
        try:
            feat = dview.get_feature(ref)
            
            # Skip imaker-internal settings
            if isinstance(feat._obj, model.ConfmlSetting):
                try:
                    prop = feat.get_property('cone-report-ignore')
                    if prop.value.lower() in ('1', 'true'):
                        continue
                except exceptions.NotFound:
                    pass
            
            #print "Still %s" % ref
            
            found_output = False
            line = RefLine(ref, feat.get_type())
            
            if plugin.is_temp_feature(feat):
                line.is_temp_feature = True

            if feat.get_type() == 'sequence':
                for f in feat.list_all_features():
                    line.add_sequence(feat.get_feature(f).get_name(), feat.get_feature(f).get_value())
            else:
                if isinstance(feat.get_datas(), list): 
                    for d in feat.get_datas():
                        line.add_data(d.find_parent(type=api.Configuration).get_full_path(), d.get_value())
                else:
                    line.add_data(feat.get_data().find_parent(type=api.Configuration).get_full_path(), feat.get_value())
            
            
            # Impl and output files
            has_impl = False
            for impl in impls:
                # Check for implementations using the actual sub-refs
                if impl.has_ref(sub_refs):
                    has_impl = True
                    line.add_impl(impl.ref, impl.IMPL_TYPE_ID, impl.list_output_files())
            if has_impl:    rep_data.add_line(line)
            else:           rep_data.add_ref_noimpl(line)
                
            
            # For localPath and targetPath, the name should be the one from its parent file/folder setting
            if isinstance(feat._obj, (model.ConfmlLocalPath, model.ConfmlTargetPath)):
                name = feat._obj._parent.name
            else:
                name = feat.name
            
            line.set_feat_name(name)
            line.set_config_path( feat._obj.find_parent(type=api.Configuration).get_full_path())
            
        except Exception, e:
            utils.log_exception(logging.getLogger('cone'), 'Failed to collect data for report. Exception: %s' % e)
        
    # create one list of not generated files
    for myline in rep_data.lines:
        for myimpl in myline.impls:
            for output_file in myimpl.outputfiles:
                if not output_file.exists and output_file not in rep_data.missing_output_files:
                    rep_data.missing_output_files.append(output_file)
    
    rep_data.set_options(options)
    rep_data.set_output_dir(options.output)
    rep_data.update_nbr_of_refs()
    rep_data.update_nbr_of_refs_noimpl()
    
    return rep_data

def generate_report(rep_data, report_file_path, template_file_path=None):
    """
    Generate a generation report based on the given report data.
    @param rep_data: The report data.
    @param report_file_path: Path to the report file to generate.
    @param template_file_path: Path to the template file to use.
        If None, the default template is used.
    """
    # Determine the template file and directory to use
    if template_file_path is None:
        template_file_path = os.path.join(ROOT_PATH, 'gen_report_template.html')
    
    report_util.generate_report(template_file_path, report_file_path, {'rep_data' : rep_data})

class ReportData(object):
    """
    Data object that stores all information used in report generation.
    """
    
    def __init__(self):
        self.generation_timestamp = time.time()
        self.generation_time = strftime("%d.%m.%Y %H:%M:%S")
        self.options = None
        self.lines = []
        self.nbr_of_refs = 0
        self.nbr_of_refs_noimpl = 0
        self.cwd = os.getcwd()
        self.ref_noimpl = []
        self.duration = 0
        self.output_dir = os.getcwd()
        self.project_dir = ''
        self.rule_exec_results = []
        self.missing_output_files = []    
    
    def set_output_dir(self, dir):
        self.output_dir = os.path.abspath(os.path.normpath(dir))
    
    def add_line(self, line):
        self.lines.append(line)
    
    def set_duration(self, duration):
        self.duration = duration
    
    def set_options(self, options):
        self.options = options
        self.project_dir = os.path.abspath(options.project)
        
    def set_report_filename(self, filename):
        self.report_filename = filename
        
    def add_ref_noimpl(self, ref):
        self.ref_noimpl.append(ref)
        
    def update_nbr_of_refs(self):
        self.nbr_of_refs = len(self.lines)
    
    def update_nbr_of_refs_noimpl(self):
        self.nbr_of_refs_noimpl = len(self.ref_noimpl)
    
    def __repr__(self):
        return "ReportData(%s)" % [self.generation_timestamp, 
                                   self.generation_time,
                                   self.options,
                                   self.lines,
                                   self.nbr_of_refs,
                                   self.nbr_of_refs_noimpl,
                                   self.cwd,
                                   self.ref_noimpl,
                                   self.duration,
                                   self.output_dir,
                                   self.project_dir,
                                   self.rule_exec_results,
                                   self.missing_output_files]    
    
class RefLine(object):
    """
    Data object that stores information for one ref in report generation.
    """
    
    def __init__(self, ref, type):
        self.ref = ref
        self.feat_type = type 
        self.feat_name = None
        self.feat_value = None
        self.config_path = None
        self.impls = []
        self.output = None
        self.nbr_impls = 0
        self.nbr_outputfiles = 0
        self.datas = []
        self.nbr_of_datas = 0
        self.nbr_of_rows = 0
        self.seq_data = []
        self.is_temp_feature = False
        
    def add_impl(self, impl_file, impl_type, outputfiles):
        self.impls.append(ImplLine(impl_file, impl_type, outputfiles))
        self.nbr_impls = len(self.impls)
        self.nbr_outputfiles = len(outputfiles) + self.nbr_outputfiles

    def add_data(self, layer, value):
        self.datas.append(DataLine(layer,value))
        self.nbr_of_datas = len(self.datas)
        
    def add_sequence(self, subsetting, values):
        self.seq_data.append([subsetting, values])
        
    def set_feat_name(self, name):
        self.feat_name = name
        
    def set_feat_value(self, value):
        self.feat_value = value
        
    def set_config_path(self, filename):
        self.config_path = os.path.normpath(filename)
        
class ImplLine():
    def __init__(self, impl_file, impl_type, outputfiles, generation_runs=[]):
        self.name = os.path.normpath(impl_file)
        self.type = impl_type
        files = []
        
        for outputfile in outputfiles:
            files.append(Outputfile(outputfile))
        
        self.outputfiles = files
        self.generation_runs = generation_runs
        
class Outputfile():
    def __init__(self, filename):
        self.filename = os.path.normpath(filename)
        self.abs_filename = os.path.abspath(filename)
        self.exists = os.path.isfile(self.abs_filename)
    
    def __eq__(self, other):
        if type(self) is type(other):
            return self.filename == other.filename
        else:
            return False
        
class DataLine():
    def __init__(self, layer, value):
        self.layer = os.path.normpath(layer)
        self.value = value