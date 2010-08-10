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
A plugin implementation for image selection from ConfigurationLayers.
'''

import os
import logging
import pkg_resources

try:
    from cElementTree import ElementTree
except ImportError:
    try:    
        from elementtree import ElementTree
    except ImportError:
        try:
            from xml.etree import cElementTree as ElementTree
        except ImportError:
            from xml.etree import ElementTree
            


from cone.public import exceptions,plugin,utils,api
from imageplugin.generators import OutputGenerator,InputFile,InputDir,InvalidInputFileException

class ImageImpl(plugin.ImplBase):
    """
    ContentImpl plugin finds all image resources from each layer and copies
    them to the output correctly. It follows the Configuration project override
    rules, so that the topmost layer files override files on the previous layers.
    """
    
    IMPL_TYPE_ID = "imageml"
    
    def __init__(self,ref,configuration):
        """
        Overloading the default constructor
        """
        plugin.ImplBase.__init__(self,ref,configuration)
        self.include = {}
        self.exclude = {}
        self.input = ""
        self.desc = ""
        self.output_file = ""
        self.logger = logging.getLogger('cone.imageml(%s)' % self.ref)
        self.errors = False

    def get_include_pattern(self):
        include_pattern = ""
        if self.include.has_key('pattern'): 
            include_pattern = self.include['pattern'][0] 
        return include_pattern
    
    def get_exclude_pattern(self):
        exclude_pattern = ""
        if self.exclude.has_key('pattern'): 
            exclude_pattern = self.exclude['pattern'][0] 
        return exclude_pattern
    
    def list_output_files(self):
        """
        Return a list of output files as an array. 
        """
        return []
    
    def generate(self, context=None):
        """
        Generate the given implementation.
        """
        self.logger.info('Generating')
        ret = True
        for generator in self.generators:
            self.logger.info(generator)
            generator.subpath =  os.path.join(context.output,self.output)
            try:
                ret = generator.generate(context) and ret
                outfile = generator.get_outputpath()
                context.add_file(outfile, implementation=self)
            except InvalidInputFileException, e:
                self.logger.error(e)
        return ret
    
    def generate_layers(self,layers):
        """
        Generate the given Configuration layers.
        """
        return self.generate()
    
    def get_refs(self):
        refs = []
        for generator in self.generators:
            refs.extend(generator.get_refs())
        if refs:
            return utils.distinct_array(refs)
        else:
            return None


class ImageImplReader(plugin.ReaderBase):
    """
    Parses a single imageml implml file
    """ 
    NAMESPACE = 'http://www.s60.com/xml/imageml/1'
    NAMESPACE_ID = 'imageml'
    ROOT_ELEMENT_NAME = 'imageml'
    FILE_EXTENSIONS = ['imageml']
    
    INCLUDE_ATTR = ['pattern']
    EXCLUDE_ATTR = ['pattern']
    def __init__(self):
        self.desc = None
        self.output = None
        self.input_dir = None
        self.include = None
        self.exclude = None
        self.namespaces = [self.NAMESPACE]
    
    @classmethod
    def read_impl(cls, resource_ref, configuration, etree):
        reader = ImageImplReader()
        reader.desc = reader.parse_desc(etree)
        reader.outputgenerators = reader.parse_outputs(etree)

        impl = ImageImpl(resource_ref, configuration)
        impl.desc = reader.desc
        impl.generators = reader.outputgenerators
        for generator in impl.generators:
            generator.configuration = configuration
        
        return impl
    
    @classmethod
    def get_schema_data(cls):
        return pkg_resources.resource_string('imageplugin', 'xsd/imageml.xsd')
    
    def fromstring(self, xml_as_string):
        etree = ElementTree.fromstring(xml_as_string)
        self.desc = self.parse_desc(etree)
        self.outputgenerators = self.parse_outputs(etree)
        return

    def parse_desc(self,etree):
        desc = ""
        desc_elem = etree.find("{%s}desc" % self.namespaces[0])
        if desc_elem != None:
            desc = desc_elem.text
        return desc

    def parse_input_include(self,etree):
        include_elem = etree.findall("{%s}include" % self.namespaces[0])
        include = {}
        for f in include_elem:
            for key in self.INCLUDE_ATTR:
                # Add the attribute if it is found to include dict
                include[key] = []
                attr = f.get(key)
                if attr: include[key].append((attr))
        return include

    def parse_input_exclude(self,etree):
        elem = etree.findall("{%s}exclude" % self.namespaces[0])
        exclude = {}
        for f in elem:
            for key in self.EXCLUDE_ATTR:
                # Add the attribute if it is found
                exclude[key] = []
                attr = f.get(key)
                if attr: exclude[key].append((attr))
        return exclude

    def parse_inputs(self,etree):
        inputs = etree.findall("{%s}input" % self.namespaces[0])
        inputlist = []
        for input_elem in inputs:
            if input_elem.get('dir'):
                inputdir = InputDir(input_elem.get('dir'),**input_elem.attrib)
                inputdir.include = self.parse_input_include(input_elem)
                inputdir.exclude = self.parse_input_exclude(input_elem)
                inputlist.append(inputdir)
            elif input_elem.get('file'):
                inputlist.append(InputFile(input_elem.get('file'),**input_elem.attrib))
        return inputlist

    def parse_outputs(self,etree):
        outputs = etree.findall("{%s}output" % self.namespaces[0])
        outputpath = ""
        outputgenerators = []
        for output_elem in outputs:
            if output_elem.get('file'):
                outputpath = output_elem.get('file')
            generator = OutputGenerator(outputpath,**output_elem.attrib)
            generator.inputs = self.parse_inputs(output_elem)
            outputgenerators.append(generator)
        return outputgenerators

