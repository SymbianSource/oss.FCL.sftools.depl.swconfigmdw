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
'''
A plugin implementation for content selection from ConfigurationLayers.
'''


import re
import os
import sys
import logging
import shutil
import pkg_resources
            
import __init__

from cone.public import exceptions,plugin,utils,api,container
from contentplugin import contentmlparser

class ContentImpl(plugin.ImplBase):
    """
    ContentImpl plugin finds all content resources from each layer and copies
    them to the output correctly. It follows the Configuration project override
    rules, so that the topmost layer files override files on the previous layers.
    """
    
    IMPL_TYPE_ID = 'content'
    
    def __init__(self,ref,configuration):
        """
        Overloading the default constructor
        """
        plugin.ImplBase.__init__(self,ref,configuration)
        self.desc = ""
        self.logger = logging.getLogger('cone.content(%s)' % self.ref)
        self.errors = False
        self.context = plugin.GenerationContext(configuration=configuration)


    def list_output_files(self):
        """
        Return a list of output files as an array. 
        """
        if not self.errors:
            copylist = self.get_full_copy_list()
            outputfiles = [entry[1] for entry in copylist]
            return outputfiles
        else:
            return []
    
    def get_refs(self):
        refs = []
        for output in self.outputs:
            refs.extend(output.get_refs())
        if refs:
            return refs
        else:
            return None
    
    def get_full_copy_list(self, print_info=False):
        fullcopylist = []
        for output in self.outputs:
            for input in output.inputs:
                copylist = []
                if print_info:
                    self.logger.info('Content copy items from %s to %s' % (input.dir,os.path.join(self.output,output.dir)))
                
                if input.__class__.__name__ == "ContentInput":
                    copylist = self.create_copy_list(content=self.configuration.layered_content(empty_folders=True),
                                                     input=input.dir,
                                                     output=os.path.join(self.output,output.dir),
                                                     include_pattern=input.get_include_pattern(),
                                                     exclude_pattern=input.get_exclude_pattern(),
                                                     files=input.get_filelist(),
                                                     flatten=output.flatten,
                                                     output_file=output.file)
                elif input.__class__.__name__ == "ExternalContentInput":
                    #Handling external inputs separately
                    if input.dir != None:
                        fulldir = os.path.abspath(os.path.join(self.configuration.get_project().get_storage().get_path(),input.dir))
                    else:
                        fulldir = self.configuration.get_project().get_storage().get_path()
                    
                    data = container.DataContainer()
                    for root, dirs, files in os.walk(fulldir):
                        for f in files:
                            filepath = utils.resourceref.norm(os.path.join(root, f))
                            key = utils.resourceref.replace_dir(filepath,fulldir,"")
                            data.add_value(key,filepath)
                        
                        # If the root contains no directories and no files, it is
                        # an empty directory and needs to be added
                        if not dirs and not files:
                            filepath = utils.resourceref.norm(root)
                            key = utils.resourceref.replace_dir(filepath,fulldir,"")
                            data.add_value(key,filepath)
                    
                    copylist = self.create_copy_list(content=data,
                                                     input=input.dir,
                                                     output=os.path.join(self.output,output.dir),
                                                     include_pattern=input.get_include_pattern(),
                                                     exclude_pattern=input.get_exclude_pattern(),
                                                     files=input.get_filelist(),
                                                     flatten=output.flatten,
                                                     output_file=output.file,
                                                     external=True)
                else:
                    logging.getLogger('cone.content').warning("Unknown input %s" % (input.__class__.__name__))
                
                fullcopylist += copylist
        
        # Sort to make automated testing easier (list always in same order)
        fullcopylist.sort()
        
        return fullcopylist

    def generate(self, context=None):
        """
        Generate the given implementation.
        """
        #assert context, "No Context given for generation!"
        self.context = context
        self.logger.info('Generating')
        self.create_output()
        return 

    def create_output(self,layers=None):
        """
        Create the output directory from the content folder files
        """
        if not self.errors:
            copylist = self.get_full_copy_list(True)
            for copy_item in copylist:
                source_path = copy_item[0]
                target_path = copy_item[1]
                external = copy_item[2]
                
                self.logger.info('Copy from %s to %s' % (source_path,target_path))
                
                # Open file resource if the source is a file
                file_res = None
                if not external and not self.configuration.get_storage().is_folder(source_path):
                    file_res = self.configuration.get_storage().open_resource(source_path, "rb")
                elif external and os.path.isfile(source_path):
                    file_res = open(source_path, 'rb')
                
                # Copy file or create empty directory
                if file_res:
                    try:        self._copy_file(file_res, target_path)
                    finally:    file_res.close()
                else:
                    path = os.path.join(self.context.output, target_path)
                    if not os.path.exists(path): os.makedirs(path)
            return 
        else:
            self.logger.error('Plugin had errors! Bailing out!')
    
    def _copy_file(self, source_file, target_file_path):
        outfile = self.context.create_file(target_file_path, implementation=self)
        try:
            # Copy data in chunks of max 2 MB to avoid
            # memory errors with very large files
            while True:
                data = source_file.read(2 * 1024 * 1024)
                if data:    outfile.write(data)
                else:       break
        finally:
            outfile.close()

    def create_copy_list(self, **kwargs):
        """
        Return a list copy list where each element is a (from, to, is_external) tuple 
        """
        datacontainer = kwargs.get('content',None)
        input_dir     = kwargs.get('input','')
        output_dir    = kwargs.get('output','')
        output_file   = kwargs.get('output_file','')        
        include_filter= kwargs.get('include_pattern','')
        exclude_filter= kwargs.get('exclude_pattern','')
        files         = kwargs.get('files',[])
        flatten       = kwargs.get('flatten',False)
        external      = kwargs.get('external',False)
        copylist = []
        contentfiles = datacontainer.list_keys()      
        """ 
        First get only the files list from content files.
        Then apply the possible filters. 
        """
        if input_dir == None:
            self.logger.warning("Input dir is none!")

        
        if files != []:
            for f in files:
                if f in contentfiles:
                    pass
                elif f not in  contentfiles:
                    self.logger.info("File: %s not found in content" % f)   
            

        if files != []:
            filesfunc = lambda x: x.lower() in [f.lower() for f in files]
            contentfiles = filter(filesfunc, contentfiles)
        if include_filter != "":
            filter_regexp = include_filter
            filter_regexp = filter_regexp.replace('.','\.')         
            filter_regexp = filter_regexp.replace('*','.*')         
            self.logger.info("filtering with include %s" % filter_regexp)   
            contentfiles = utils.resourceref.filter_resources(contentfiles,filter_regexp)
        if exclude_filter != "":
            filter_regexp = exclude_filter
            filter_regexp = filter_regexp.replace('.','\.')            
            filter_regexp = filter_regexp.replace('*','.*')         
            self.logger.info("filtering with exclude %s" % filter_regexp)   
            contentfiles = utils.resourceref.neg_filter_resources(contentfiles,filter_regexp)
        for outfile in contentfiles:
            sourcefile = ""
            targetfile = ""
            
            # For the startswith() check, make sure that input dir has a trailing slash
            if input_dir and input_dir[-1] != '/':  input_dir_check = input_dir + '/'
            else:                                   input_dir_check = input_dir
            
            if input_dir != None and (input_dir == outfile or outfile.startswith(input_dir_check)):
                sourcefile = datacontainer.get_value(outfile)
                if flatten:
                    targetfile = utils.resourceref.join_refs([output_dir, os.path.basename(outfile)])
                    targetfile = utils.resourceref.norm(targetfile)
                else:
                    targetfile = utils.resourceref.replace_dir(outfile,input_dir,output_dir)
            elif external:
                #External inputs
                sourcefile = utils.resourceref.norm(datacontainer.get_value(outfile))
                                
                if flatten:
                    targetfile = utils.resourceref.join_refs([output_dir, os.path.basename(sourcefile)])
                    targetfile = utils.resourceref.norm(targetfile)
                else:
                    fulldir = os.path.abspath(os.path.join(self.configuration.get_project().get_storage().get_path(),input_dir))
                    targetfile = utils.resourceref.replace_dir(sourcefile,fulldir,output_dir)
                
            if output_file:
                #Renaming output if defined
                targetfile = targetfile.replace(os.path.basename(targetfile), output_file)
                
            if sourcefile and targetfile:
                copylist.append((sourcefile,targetfile,external))
        return copylist
    
    def uses_layer(self, layer):
        layered_content = layer.layered_content().list_keys()
        for f in self.get_full_copy_list():
            for file in layered_content:
                if utils.resourceref.norm(os.path.join(utils.resourceref.get_path(layer.get_path()), 'content', file)) == f[0]:
                    return True
        return False
    
    def uses_layers(self, layers, context):
        # Use the base implementation to check with refs first
        if super(ContentImpl, self).uses_layers(layers, context):
            return True
        
        # Then check if any of the files in the copy list come from the layers
        copy_list = self.get_full_copy_list()
        for layer in layers:
            layered_content = layer.layered_content().list_keys()
            for f in copy_list:
                for file in layered_content:
                    if utils.resourceref.norm(os.path.join(utils.resourceref.get_path(layer.get_path()), 'content', file)) == f[0]:
                        return True
        return False
    
    
class ContentImplReaderBase(object):
    FILE_EXTENSIONS = ['content', 'contentml']
    
    @classmethod
    def read_impl(cls, resource_ref, configuration, etree):
        parser = cls.parser_class()
        
        desc = parser.parse_desc(etree)
        outputs = parser.parse_outputs(etree)
        phase = parser.parse_phase(etree)
        tags = parser.parse_tags(etree)
        
        impl = ContentImpl(resource_ref, configuration)
        impl.desc = desc
        impl.outputs = outputs
        if tags:
            impl.set_tags(tags)
        for output in impl.outputs:
            output.set_configuration(configuration)
        if phase != None:
            impl.set_invocation_phase(phase)
            
        return impl

class ContentImplReader1(ContentImplReaderBase, plugin.ReaderBase):
    NAMESPACE = 'http://www.s60.com/xml/content/1'
    NAMESPACE_ID = 'contentml1'
    ROOT_ELEMENT_NAME = 'content'
    parser_class = contentmlparser.Content1Parser
    
    @classmethod
    def get_schema_data(cls):
        return pkg_resources.resource_string('contentplugin', 'xsd/contentml.xsd')

class ContentImplReader2(ContentImplReaderBase, plugin.ReaderBase):
    NAMESPACE = 'http://www.s60.com/xml/content/2'
    NAMESPACE_ID = 'contentml2'
    ROOT_ELEMENT_NAME = 'content'
    parser_class = contentmlparser.Content2Parser
    
    @classmethod
    def get_schema_data(cls):
        return pkg_resources.resource_string('contentplugin', 'xsd/contentml2.xsd')
