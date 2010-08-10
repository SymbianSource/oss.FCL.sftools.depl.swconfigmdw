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
from time import strftime
from cone.public import api, exceptions, utils, plugin
from cone.confml import model
from cone.report import report_util 

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
SERIALISATION_FORMAT = 'pickle'

def save_report_data(rep_data, file_path):
    """
    Save report data into an intermediary report data file.
    """
    dir = os.path.dirname(file_path)
    if dir != '' and not os.path.exists(dir):
        os.makedirs(dir)
    f = open(file_path, 'wb')
    try:
        if SERIALISATION_FORMAT == 'yaml':
            yaml.dump(rep_data, f)
        elif SERIALISATION_FORMAT == 'pickle':
            pickle.dump(rep_data, f)
        elif SERIALISATION_FORMAT == 'pickle/2':
            pickle.dump(rep_data, f, 2)
    finally:    
        f.close()

def load_report_data(file_path):
    """
    Load report data from an intermediary report data file.
    """
    try:        
        f = open(file_path, "rb")
        if SERIALISATION_FORMAT == 'yaml':
            data = yaml.load(f)
        elif SERIALISATION_FORMAT == 'pickle':
            data = pickle.load(f)
        elif SERIALISATION_FORMAT == 'pickle/2':
            data = pickle.load(f)
    finally:
        f.close()
        
    data.label = get_generation_run_label(file_path)
    return data

def get_generation_run_label(datafile_path):
    filename = os.path.split(datafile_path)[1]
    filename_noext = os.path.splitext(filename)[0]
    return filename_noext

def _get_parent_sequence_or_self(feature):
    current = feature._parent
    while current is not None:
        if isinstance(current, api.FeatureSequence):
            return current
        current = current._parent
    return feature


def generate_report(rep_data, report_file_path, template_file_path=None, template_paths=[], report_options=[]):
    """
    Generate a generation report based on the given report data.
    @param rep_data: The report data.
    @param report_file_path: Path to the report file to generate.
    @param template_file_path: Path to the template file to use.
        If None, the default template is used.
    @param template_paths: the additional search paths for templates. The default location cone.report is 
    always included.   
    """
    # Determine the template file and directory to use
    if template_file_path is None:
        template_file_path = 'gen_report_template.html'
    contexts = [report_data.context for report_data in rep_data]
    report_data = {'rep_data' : rep_data, 
                   'report_options' : report_options,
                   'merged_context' : plugin.MergedContext(contexts)}
    report_util.generate_report(template_file_path, report_file_path, report_data, template_paths)

def normalize_slash(path):
    """
    Normalize backslashes to slashes to make testing easier (no differences
    between reports in linux and windows).
    """
    return path.replace('\\', '/')

class ReportData(object):
    """
    Data object that stores all information used in report generation.
    """
    
    def __init__(self):
        self.project = None
        self.generation_timestamp = time.time()
        self.generation_time = strftime("%d.%m.%Y %H:%M:%S")
        self.options = None
        self.duration = 0
        self.output_dir = os.getcwd()
        self.project_dir = ''
        self.context = None
        self.label = ''

    def set_output_dir(self, dir):
        self.output_dir = os.path.abspath(os.path.normpath(dir))
        
    def set_duration(self, duration):
        self.duration = duration
    
    def set_options(self, options):
        self.options = options
        self.project_dir = os.path.abspath(options.project)
        
    def set_report_filename(self, filename):
        self.report_filename = filename
        
    def __repr__(self):
        return "ReportData(%s)" % [self.generation_timestamp, 
                                   self.generation_time,
                                   self.options,
                                   self.duration,
                                   self.output_dir,
                                   self.project_dir]    


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
        self.config_path = normalize_slash(os.path.normpath(filename))
        

class ImplLine():
    def __init__(self, impl_file, impl_type, outputfiles, generation_runs=[]):
        self.name = normalize_slash(os.path.normpath(impl_file))
        self.type = impl_type
        files = []
        
        for outputfile in outputfiles:
            files.append(Outputfile(outputfile))
        
        self.outputfiles = files
        self.generation_runs = generation_runs
        
class Outputfile():
    def __init__(self, filename):
        self.filename = normalize_slash(os.path.normpath(filename))
        self.abs_filename = normalize_slash(os.path.abspath(filename))
        self.exists = os.path.isfile(self.abs_filename)
    
    def __eq__(self, other):
        if type(self) is type(other):
            return self.filename == other.filename
        else:
            return False
        
class DataLine():
    def __init__(self, layer, value):
        self.layer = normalize_slash(os.path.normpath(layer))
        self.value = value