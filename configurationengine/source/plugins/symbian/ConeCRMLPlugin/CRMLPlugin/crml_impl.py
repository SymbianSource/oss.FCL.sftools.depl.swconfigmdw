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

from cone.public import exceptions, plugin, utils, api
import crml_writer, crml_comparator
from crml_model import *

class CrmlImpl(plugin.ImplBase):
    IMPL_TYPE_ID = 'crml'
    
    RFS_RECORDS_LIST_VARNAME = 'crml_cenrep_rfs_records_list'
    RFS_TXT_GENERATED_VARNAME = 'crml_cenrep_rfs_txt_generated'

    def __init__(self, resource_ref, configuration, repository):
        plugin.ImplBase.__init__(self, resource_ref, configuration)
        self.resource_ref = resource_ref
        self.configuration = configuration
        self.logger = logging.getLogger('cone.crml(%s)' % self.resource_ref)
        self.repository = repository

    def __getstate__(self):
        state = super(CrmlImpl, self).__getstate__()
        state['repository'] = self.__dict__.get('repository',None)
        return state

            
    def generate(self, context=None):
        # Quick fix 
        if context:
            self.generation_context = context
        
        # See if delta CenReps should be generated
        delta_cenrep = context and context.changed_refs is not None \
            and 'deltacenrep' in context.tags.get('crml', [])
        
        changed_refs = None
        if delta_cenrep:
            changed_refs = context.changed_refs
            
            # Hard-coded output for delta CenReps for now
            self.output_subdir = 'deltacenreps'
            self.plugin_output = ''
        
        file_path = self._get_cenrep_txt_file_path()
        self.logger.debug("Generating file '%s'..." % file_path)
        
        # Generate CenRep text data and write it to the output file
        writer = crml_writer.CrmlTxtWriter(context, self.logger)
        data = writer.get_cenrep_txt_data(self.repository, changed_refs).encode('UTF-16')
        self._write_to_file(file_path, data)
        
        # Add to the generated files list
        KEY = 'crml_generated_cenrep_files'
        lst = context.impl_data_dict.setdefault(KEY, [])
        lst.append((os.path.basename(file_path), os.path.abspath(file_path)))
        
        
        # Collect the record for cenrep_rfs.txt generation in post_generate()
        if self.generation_context is not None:
            rfs_record = writer.get_cenrep_rfs_record(self.repository)
            if rfs_record:
                # Add the record to the dictionary
                data_dict = self.generation_context.impl_data_dict
                VARNAME = self.RFS_RECORDS_LIST_VARNAME
                if VARNAME not in data_dict:
                    data_dict[VARNAME] = []
                data_dict[VARNAME].append(rfs_record)
    
    def post_generate(self, context=None):
        # Quick fix 
        if context:
            self.generation_context = context
        if self._is_cenrep_rfs_txt_to_be_generated():
            # Generate CenRep RFS text file if not already generated
            data_dict = self.generation_context.impl_data_dict
            if self.RFS_TXT_GENERATED_VARNAME not in data_dict:
                rfs_records = data_dict.get(self.RFS_RECORDS_LIST_VARNAME, [])
                
                file_path = self._get_cenrep_rfs_txt_file_path()
                writer = crml_writer.CrmlTxtWriter(self.configuration, self.logger)
                data = writer.get_cenrep_rfs_txt_data(rfs_records).encode('UTF-16')
                self._write_to_file(file_path, data)
            
                data_dict[self.RFS_TXT_GENERATED_VARNAME] = True

    def list_output_files(self):
        """
        Return a list of output files as an array. 
        """
        files = [self._get_cenrep_txt_file_path()]
        if self._is_cenrep_rfs_txt_to_be_generated():
            files.append(self._get_cenrep_rfs_txt_file_path())
        return files

    def get_refs(self):
        if self.repository is None:
            return []
        else:
            return self.repository.get_refs()
    
    def get_flat_comparison_id(self):
        return crml_comparator.CrmlComparator.get_flat_comparison_id(self.repository)
    
    def get_flat_comparison_extra_data(self):
        return crml_comparator.CrmlComparator.get_flat_comparison_extra_data(self.repository)
    
    @classmethod
    def get_flat_comparison_impl_type_id(cls):
        return 'crml'
    
    def flat_compare(self, other):
        comparator = crml_comparator.CrmlComparator(self.resource_ref, self.repository)
        return comparator.flat_compare(other.resource_ref, other.repository)
    
    def _get_cenrep_txt_file_path(self):
        """
        Return the full path to the CenRep text file generated by this implementation
        """
        uid = self.repository.uid_value
        if uid.startswith('0x'):    uid = uid[2:]
        return os.path.normpath(os.path.join(self.output, uid + '.txt'))
    
    def _get_cenrep_rfs_txt_file_path(self):
        """
        Return the full path to the CenRep RFS text file
        """
        # cenrep_rfs.txt goes to a different place than the rest of
        # the CenRep files, so temporarily override plugin_output
        # for that purpose
        orig_pluginoutput = self.plugin_output
        self.plugin_output = 'private/100059C9'
        rfs_txt_path = os.path.normpath(os.path.join(self.output, 'cenrep_rfs.txt'))
        self.plugin_output = orig_pluginoutput
        return rfs_txt_path
    
    def _is_cenrep_rfs_txt_to_be_generated(self):
        """
        Return whether the CenRep RFS text file is to be generated.
        """
        if self.generation_context is None:
            return False
        
        targets = self.generation_context.tags.get('target', [])
        return 'core' in targets or 'rofs2' in targets
    
    def _write_to_file(self, file_path, data):
        
        # Write data
        f = self.generation_context.create_file(file_path, implementation=self)
        try:        f.write(data)
        finally:    f.close()
