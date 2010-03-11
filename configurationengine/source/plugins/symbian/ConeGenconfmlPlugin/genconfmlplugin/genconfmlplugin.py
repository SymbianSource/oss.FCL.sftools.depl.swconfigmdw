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
GenConfml plugin for ConE
'''

import re
import os
import sys
import logging
import xml.parsers.expat
import confflattener
import xslttransformer
import codecs
import tempfile
import tempfile

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

import __init__

from cone.public import exceptions,plugin,utils,api
from cone.confml import persistentconfml

class GenconfmlImpl(plugin.ImplBase):
    """
    GenConfml plugin implementation
    """
    
    IMPL_TYPE_ID = "gcfml"
    
    
    def __init__(self,ref,configuration, output='output', linesep=os.linesep, reader=None):
        """
        Overloading the default constructor
        """
        plugin.ImplBase.__init__(self,ref,configuration)
        self.logger = logging.getLogger('cone.gcfml(%s)' % self.ref)
        self.errors = False
        self.xstl_etree = None
        self.xslt_temp_file_name = os.path.join(tempfile.gettempdir(), "genconfml_temp_%i.xslt" % os.getpid())
        self.set_output_root(output)
        self.linesep = linesep
        self._flatconfig = None
        self.temp_confml_file = os.path.join(tempfile.gettempdir(),'temp_flatted_%i.confml' % os.getpid())
        self.reader = reader

    def generate(self, context=None):
        """
        Generate the given implementation.
        """
        self.create_output()
        return 
    
    def get_refs(self):
        result = []
        for ref in self.reader.settings:
            # Process the reference, so that it will work with has_ref().
            # E.g. 'MyFeature/MySetting' -> 'MyFeature.MySetting'
            #      'MyFeature/*          -> 'MyFeature'
            ref = ref.replace('/', '.')
            if ref.endswith('.*'):
                ref = ref[:-2]
            result.append(ref)
        return result
      
    def list_output_files(self):
        """ Return a list of output files as an array. """
        return [self.get_output_filename()]
        
    def get_output_filename(self):
        """ Return a output file name. """
        
        name = self.reader.name
        if name == None: name = ""
        target = self.reader.target
        if target == None: target = ""
        output = self.output
        if self.output == None: output = ""
        
        # Make sure that target file is generated under output
        target = utils.resourceref.remove_begin_slash(utils.resourceref.norm(target))
        subdir = self.reader.subdir
        if subdir == None: 
            self.output_subdir = subdir
        output_file = os.path.normpath(os.path.join(output, target, name))
        
        return output_file
    
    def create_output(self, layers=None):
        """ Generate all output """
        resource = self.configuration.get_resource(self.ref)
        write_element_enc(self.reader.stylesheet_elem, self.xslt_temp_file_name, self.reader.stylesheet_output_enc)
        gen = Generator()
        
        target = self.reader.target
        if target == None: target = ""
        
        output_file = self.get_output_filename()
        # Don't create the dirs here, since the output file may be filtered out
        # if it is empty
        #if not os.path.exists(os.path.dirname(output_file)):
        #    os.makedirs(os.path.dirname(output_file))
        
        self.logger.info('Generating %s' % output_file)
        
        flatted_conf_as_element = persistentconfml.ConfmlWriter().dumps(self.flatconfig)
        postprocessed_element = self.post_process_flattening(flatted_conf_as_element)
        write_element_enc(postprocessed_element, self.temp_confml_file, self.reader.stylesheet_output_enc)
        gen.generate(self.configuration, resource, output_file, self.xslt_temp_file_name, self.reader.settings, self.reader.stylesheet_output_enc)
      
    def post_process_flattening(self, element):
        """
        Pick just data element and build document out of it
        """
        
        data_element = element.find("data")
        if data_element == None:
            self.logger.warning('No data to generate!!')
            new_doc = "<?xml version=\"1.0\"?><configuration>" + "</configuration>"
        else:
            new_doc = "<?xml version=\"1.0\"?><configuration>" + ElementTree.tostring(data_element) + "</configuration>"
        return ElementTree.fromstring(new_doc)

    @property
    def flatconfig(self):
      """ 
      Create a flat configuration from the current configuration with the given setting refs.
      Take the last configuration element, which will contain the data elements
      """ 
      if not self._flatconfig:
          try:
              cf = confflattener.ConfigurationFlattener()
              self._flatconfig = api.Configuration()
              cf.flat(self.configuration, self.reader.settings, self._flatconfig)
          except (exceptions.ConeException, TypeError, Exception), e:
              utils.log_exception(self.logger, 'Failed to flat configuration with settings %s. Exception: %s' % (self.reader.settings, e))
              raise exceptions.ConeException('Failed to flat configuration. Exception: %s' % e)
      return self._flatconfig


def write_element(element, output, linesep=os.linesep):
    """
    """
    if element != None and ElementTree.iselement(element):
        enc = None
        
       
        try:
            out_file = open(output, 'w')
            out_string = ElementTree.tostring(element)
            out_string = out_string.replace('\r\n', linesep)
            out_string = out_string.replace('\n', linesep)
            out_file.write(out_string)
            out_file.close()
        except Exception, e:
            raise exceptions.ConeException('Cannot write Element to file (%s). Exception: %s' % (output, e))
    else:
        raise exceptions.ConeException('Cannot write element to file, because None element passed or not Element passed.')
    
def remove_namespace(doc, namespace):
    """Remove namespace in the passed document in place."""
    ns = u'{%s}' % namespace
    nsl = len(ns)
    for elem in doc.getiterator():
        if elem.tag.startswith(ns):
            elem.tag = elem.tag[nsl:]

def write_element_enc(element, output, enc, linesep=os.linesep):
    """
    Writes element to file
    """
    if element != None and ElementTree.iselement(element):
        enc = None
        
       
        try:
            remove_namespace(element, 'http://www.s60.com/xml/genconfml/1')
            
            
            out_file = codecs.open(output, 'w', enc)
            output_string = ElementTree.tostring(element)
            output_string = output_string.replace('\r\n', linesep)
            output_string = output_string.replace('\n', linesep)
            out_file.write(output_string)
            out_file.close()
        except Exception, e:
            raise exceptions.ConeException('Cannot write Element to file (%s). Exception: %s' % (output, e))
    else:
        raise exceptions.ConeException('Cannot write element to file, because None element passed or not Element passed.')

    
def write_element_tempfile(element, tempfile):
    """
    Writes element to temp file
    """
    if element != None and ElementTree.iselement(element):
        
        try:
            tempfile.write(ElementTree.tostring(element))
        except Exception, e:
            raise exceptions.ConeException('Cannot write Element to file (%s). Exception: %s' % (output, e))
    else:
        raise exceptions.ConeException('Cannot write element to file, because None element passed or not Element passed.')
    
class GenconfmlImplReader(plugin.ReaderBase):
    """
    Parses a single gcfml file
    """ 
    NAMESPACE = 'http://www.s60.com/xml/genconfml/1'
    IGNORED_NAMESPACES = ['http://www.w3.org/1999/XSL/Transform', 
                          'http://www.w3.org/2001/xinclude']
    FILE_EXTENSIONS = ['gcfml']
    
    def __init__(self):
        self.stylesheet = None
        self.namespaces = self.IGNORED_NAMESPACES + [self.NAMESPACE]
        self.settings = None
        self.name = None
        self.subdir = None
        self.target = None
        self.stylesheet_elem = None
        self.stylesheet_output_enc = None
        self.nss = None
    
    @classmethod
    def read_impl(cls, resource_ref, configuration, etree):
        
        reader = GenconfmlImplReader()
        reader.from_etree(etree)
        return GenconfmlImpl(resource_ref, configuration, reader=reader)
            
    def from_etree(self, etree):
        self.stylesheet = self.parse_stylesheet(etree)
        self.settings = self.parse_settings(etree)
        self.name = self.parse_name(etree)
        self.subdir = self.parse_subdir(etree)        
        self.target = self.parse_target(etree)
        self.stylesheet_elem = self.parse_stylesheet_elem(etree)
        self.stylesheet_output_enc = self.parse_stylesheet_output_enc(etree)
        self.nss = self.parse_stylesheet_nss(etree)
        
        return

    def parse_target(self, etree):
        """
        Parses target from etree
        """
        
        target = ""
        for elem in etree.getiterator("{%s}file" % self.namespaces[2]):
          if elem != None:
              target = elem.get('target')
        
        return target
    
    def parse_name(self, etree):
        """
        Parses name from etree
        """
        
        name = ""
        for elem in etree.getiterator("{%s}file" % self.namespaces[2]):
          if elem != None:
              name = elem.get('name')
        
        return name

    def parse_subdir(self, etree):
        """
        Parses subdir from etree
        """
        
        subdir = ""
        for elem in etree.getiterator("{%s}file" % self.namespaces[2]):
          if elem != None:
              subdir = elem.get('subdir')
        if subdir == None:
            subdir = ""
        
        return subdir

        
    def parse_stylesheet(self,etree):
        """
        Parses stylesheet from getree
        """
        
        stylesheet = ""
        stylesheet_elem = etree.find("{%s}stylesheet" % self.namespaces[0])
        if stylesheet_elem != None:
            stylesheet = ElementTree.tostring(stylesheet_elem)
        return stylesheet

    def parse_stylesheet_output_enc(self, etree):
        enc = ""
        ss_elem = etree.find("{%s}stylesheet" % self.namespaces[0])
        if ss_elem != None:
            children = ss_elem.getchildren()
            for child in children:
                if child.tag == '{%s}output' % self.namespaces[0]: 
                    enc = child.attrib.get('encoding')
        return enc

    def parse_stylesheet_nss(self, etree):
        nss = None
        
        for elem in etree.getiterator():
            name = elem.tag
            if name[0] == "{":
                uri, tag = name[1:].split("}")
                if tag == "stylesheet":
                    nss = uri
        return nss

    def parse_stylesheet_elem(self,etree):
        """
        Parses stylesheet element from getree
        """
        
        return etree.find("{%s}stylesheet" % self.namespaces[0])

    def parse_settings(self,etree):
        """
        Parses settings from etree
        """
        
        settings = []
        
        for elem in etree.getiterator("{%s}file" % self.namespaces[2]):
          if elem != None:
              setting_elems = elem.findall("{%s}setting" % self.namespaces[2])
              for setting_elem in setting_elems:
                  if setting_elem != None:
                      settings.append(setting_elem.get('ref'))
        
        return settings
    
class Generator(object):
    """
    Genconfml generator
    """ 
    def __init__(self):
        self.temp_confml_file = os.path.join(tempfile.gettempdir(),'temp_flatted_%i.confml' % os.getpid())
        pass

    def post_process_flattening(self, element):
        """
        Pick just data element and build document out of it
        """
        
        data_element = element.find("data")
        if data_element == None:
            self.logger.warning('No data to generate!!')
            new_doc = "<?xml version=\"1.0\"?><configuration>" + "</configuration>"
        else:
            new_doc = "<?xml version=\"1.0\"?><configuration>" + ElementTree.tostring(data_element) + "</configuration>"
        return ElementTree.fromstring(new_doc)


    def generate(self, configuration, input, output, xslt, settings, enc=sys.getdefaultencoding()):
        """
        Generates output
        """
        self.logger = logging.getLogger('cone.gcfml{%s}' % input.path)

        
        try:
            tf = xslttransformer.XsltTransformer()
            tf.transform_lxml(os.path.abspath(self.temp_confml_file), os.path.abspath(xslt), output, enc)
            #tf.transform_4s(os.path.abspath(self.temp_confml_file), os.path.abspath(xslt), output, enc)
        except (exceptions.ConeException, TypeError, Exception), e:
            logging.getLogger('cone.gcfml').warning('Failed to do XSLT tranformation. Exception: %s' % e)
            raise exceptions.ConeException('Failed to do XSLT tranformation. Exception: %s' % e)

        """ Removes template files """
        if not logging.getLogger('cone').getEffectiveLevel() != 10:
            os.remove(os.path.abspath(self.temp_confml_file))
            os.remove(os.path.abspath(xslt))
