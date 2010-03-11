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
## 
# @author Teemu Rytkonen
'''
A plugin implementation for content selection from ConfigurationLayers.
'''


import re
import os
import sys
import logging
import shutil
import copy
import xml.parsers.expat

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

class ContentOutput(object):
    def __init__(self, **kwargs):
        self._dir = kwargs.get('dir',None)
        self._file = kwargs.get('file',None)
        self.flatten = kwargs.get('flatten',False)
        self.inputs = kwargs.get('inputs', [])
        self.configuration = None

    def set_configuration(self, configuration):
        self.configuration = configuration
        for input in self.inputs:
            input.configuration = self.configuration

    def get_configuration(self, configuration):
        self.configuration = configuration

    def path_convert(self, path):
        (drive, tail) = os.path.splitdrive(path)
        return tail.lstrip('\\/')

    def get_dir(self):
        if self.configuration and ConfmlRefs.is_confml_ref(self._dir):
            parts = self._dir.split(ConfmlRefs.ref_separator)
            for (index, part) in enumerate(parts):
                if ConfmlRefs.is_confml_ref(part):
                    ref = ConfmlRefs.get_confml_ref(part)
                    parts[index] = self.configuration.get_default_view().get_feature(ref).value
                    parts[index] = self.path_convert(parts[index])
                else:
                    parts[index] = part
            return (os.sep).join(parts)
        else:
            return self.path_convert(self._dir)

    def set_dir(self, dir):
        self._dir = dir

    def get_file(self):
        if self.configuration and self._file != None and ConfmlRefs.is_confml_ref(self._file):
            parts = self._file.split(ConfmlRefs.ref_separator)
            for (index, part) in enumerate(parts):
                if ConfmlRefs.is_confml_ref(part):
                    ref = ConfmlRefs.get_confml_ref(part)
                    parts[index] = self.configuration.get_default_view().get_feature(ref).value
                    parts[index] = self.path_convert(parts[index])
                else:
                    parts[index] = part
            return (os.sep).join(parts)
        else:
            return self._file

    def set_file(self, file):
        self._file = file

    dir = property(get_dir, set_dir)
    file = property(get_file, set_file)
    
    def get_refs(self):
        refs = []
        for input in self.inputs:
            refs.extend(input.get_refs())
        return refs


class ContentInput(object):
    def __init__(self, **kwargs):
        self._dir = kwargs.get('dir',None)
        self._file = kwargs.get('file',None)
        self._include = kwargs.get('include', {})
        self._exclude = kwargs.get('exclude', {})
        self.configuration = None

    @property 
    def dir(self):
        
        if self.configuration and ConfmlRefs.is_confml_ref(self._dir):
            cref = ConfmlRefs.get_confml_ref(self._dir)
            return self.configuration.get_default_view().get_feature(cref).value
        else:
            return self._dir

    @property 
    def file(self):
        
        if self._file and self.configuration and ConfmlRefs.is_confml_ref(self._file):
            cref = ConfmlRefs.get_confml_ref(self._file)
            return self.configuration.get_default_view().get_feature(cref).value
        else:
            return self._file


    def _dereference_dict(self, data):
        if self.configuration:
            # Make a deep copy of the data, or otherwise get_refs() will
            # return the correct refs only on the first call, as the
            # references are replaced here
            data = copy.deepcopy(data)
            
            dview = self.configuration.get_default_view()
            for key in data:
                key_list = data.get(key)
                for (index,elem) in enumerate(key_list):
                    if ConfmlRefs.is_confml_ref(elem):
                        cref = ConfmlRefs.get_confml_ref(elem)
                        try:
                            # change None value to empty string
                            cvalue = dview.get_feature(cref).value or ''
                            if utils.is_list(cvalue):
                                cvalue = ", ".join(cvalue)
                            key_list[index] = cvalue
                        except exceptions.NotFound:
                            logging.getLogger('cone.content').error("Feature ref '%s' in include key '%s' not found." % (cref,key))
        return data

    @property
    def include(self):
        return self._dereference_dict(self._include)

    @property
    def exclude(self):
        return self._dereference_dict(self._exclude)

    def get_filelist(self):
        filelist = []
        if self.file:
            filelist.append(self.file)
        for elem in self.include.get('files',[]):
            elem = elem.lower().split(',')
            filelist += [selem.strip() for selem in elem]
        return filelist

    def get_include_pattern(self):
        return self.include.get('pattern',[''])[0]

    def get_exclude_pattern(self):
        return self.exclude.get('pattern',[''])[0]
    
    def get_refs(self):
        refs = []
        if self._dir is not None:
            refs.extend(utils.extract_delimited_tokens(self._dir))
        if self._file is not None:
            refs.extend(utils.extract_delimited_tokens(self._file))
        for value_list in self._include.itervalues():
            for value in value_list:
                refs.extend(utils.extract_delimited_tokens(value))
        for value_list in self._exclude.itervalues():
            for value in value_list:
                refs.extend(utils.extract_delimited_tokens(value))
        return refs


class ExternalContentInput(ContentInput):
    def __init__(self, **kwargs):
        super(ExternalContentInput,self).__init__(**kwargs)        

class ContentParserBase(object):
    """
    Parses a single content implml file
    """ 
    NAMESPACES = ['http://www.s60.com/xml/content/1']
    INCLUDE_ATTR = ['pattern']
    EXCLUDE_ATTR = ['pattern']
    def __init__(self):
        self.namespaces = self.NAMESPACES

    def parse_phase(self,etree):
        phase = ""
        phase = etree.get('phase')
        return phase

    def parse_desc(self,etree):
        desc = ""
        desc_elem = etree.find("{%s}desc" % self.namespaces[0])
        if desc_elem != None:
            desc = desc_elem.text
        return desc

    def parse_tags(self,etree):
        tags = {}
        for tag in etree.getiterator("{%s}tag" % self.namespaces[0]):
            tagname = tag.get('name','')
            tagvalue = tag.get('value')
            values = tags.get(tagname,[])
            values.append(tagvalue)
            tags[tagname] = values
        return tags

    def parse_input_include(self,etree):
        include_elem = etree.getiterator("{%s}include" % self.namespaces[0])
        include = {}
        for f in include_elem:
            for key in f.keys():
                # Add the attribute if it is found to include dict
                include[key] = []
                include[key].append(f.get(key))
        return include

    def parse_input_exclude(self,etree):
        elem = etree.getiterator("{%s}exclude" % self.namespaces[0])
        exclude = {}
        for f in elem:
            for key in f.keys():
                # Add the attribute if it is found
                exclude[key] = []
                exclude[key].append(f.get(key))
        return exclude

class Content1Parser(ContentParserBase):
    """
    Parses a single content implml file
    """ 
    NAMESPACES = ['http://www.s60.com/xml/content/1']
    def __init__(self):
        super(ContentParserBase,self).__init__()
        self.namespaces = self.NAMESPACES

    def parse_input(self,etree):
        input_elem = etree.find("{%s}input" % self.namespaces[0])
        input_dir = ""
        input_file = ""
        if input_elem != None:
            if input_elem.get('dir'):
                input_dir = input_elem.get('dir')
            if input_elem.get('file'):
                input_dir = input_elem.get('file')
            includes = self.parse_input_include(etree)
            excludes = self.parse_input_exclude(etree)
            return ContentInput(dir=input_dir, include=includes, exclude=excludes, file=input_file)
        return None

    def parse_outputs(self,etree):
        output_elem = etree.find("{%s}output" % self.namespaces[0])
        output_dir = ""        
        output_flatten = False
        inputs = []
        if output_elem != None:
            output_dir = output_elem.get('dir','')
            output_flatten = output_elem.get('flatten','') == "true"
        input = self.parse_input(etree)
        if input:
            inputs.append(input)
        return [ContentOutput(dir=output_dir, flatten=output_flatten, inputs=inputs)]

class Content2Parser(ContentParserBase):
    """
    Parses a single content implml file
    """ 
    NAMESPACES = ['http://www.s60.com/xml/content/2']
    def __init__(self):
        super(ContentParserBase,self).__init__()
        self.namespaces = self.NAMESPACES
            

    def parse_input(self,input_elem):
        input = None
        input_dir = ''
        input_file = ''
        if input_elem != None:
            if input_elem.get('dir'):
                input_dir = input_elem.get('dir')
            if input_elem.get('file'):
                input_file= input_elem.get('file')
            includes = self.parse_input_include(input_elem)
            excludes = self.parse_input_exclude(input_elem)
            input = ContentInput(dir=input_dir, include=includes, exclude=excludes, file=input_file)
        return input
    
    def parse_external_input(self,input_elem):
        input = None
        input_dir = ''
        if input_elem != None:
            if input_elem.get('dir'):
                input_dir = input_elem.get('dir')
            includes = self.parse_input_include(input_elem)
            excludes = self.parse_input_exclude(input_elem)
            input = ExternalContentInput(dir=input_dir, include=includes, exclude=excludes)
        return input

    def parse_outputs(self,etree):
        outputs = []
        for output_elem in etree.getiterator("{%s}output" % self.namespaces[0]):
            inputs = []
            output_dir = output_elem.get('dir','')
            output_file = output_elem.get('file','')
            output_flatten = output_elem.get('flatten','') == "true"
            for input_elem in output_elem.getiterator("{%s}input" % self.namespaces[0]):
                inputs.append(self.parse_input(input_elem))
            for input_elem in output_elem.getiterator("{%s}externalinput" % self.namespaces[0]):
                inputs.append(self.parse_external_input(input_elem))
            outputs.append(ContentOutput(dir=output_dir, flatten=output_flatten, inputs=inputs, file=output_file))
        return outputs


class ContentImplReader(object):
    """
    Parses a single content implml file
    """ 
    PARSERS = {'http://www.s60.com/xml/content/1' : Content1Parser,
              'http://www.s60.com/xml/content/2' : Content2Parser}
    def __init__(self):
        self.desc = None
        self.outputs = None
        self.phase = None

    def fromstring(self, xml_as_string):
        etree = ElementTree.fromstring(xml_as_string)
        # Loop through parsers and try to find a match
        (namespace,elemname) = get_elemname(etree.tag)
        pclass = self.PARSERS.get(namespace, None)
        self.parser = pclass()
        self.desc = self.parser.parse_desc(etree)
        self.outputs = self.parser.parse_outputs(etree)
        self.phase = self.parser.parse_phase(etree)
        self.tags = self.parser.parse_tags(etree)
        return

namespace_pattern = re.compile("{(.*)}(.*)")
nonamespace_pattern = re.compile("(.*)")

def get_elemname(tag):
    
    ns = namespace_pattern.match(tag)
    nn = nonamespace_pattern.match(tag)
    if ns:
        namespace = ns.group(1)
        elemname = ns.group(2)
        return (namespace,elemname)
    elif nn:
        namespace = ""
        elemname = nn.group(1)
        return (namespace,elemname)
    else:
        raise exceptions.ParseError("Could not parse tag %s" % tag)

class ConfmlRefs(object):
    
    ref_pattern = re.compile('^\$\{(.*)\}$')
    cref_pattern = re.compile('.+\..+')
    ref_separator = '/'
       
    @classmethod
    def is_ref_like(cls, variableref):
        """
        
        Returns true if the given variable represents a ref
        """
        return cls.cref_pattern.match(variableref) != None
    
    @classmethod
    def is_confml_ref(cls, variableref):
        """
        
        Returns true if the given variable ref is a confml reference
        """
        
        pos = variableref.find(cls.ref_separator)
        if pos == -1:
            return cls.ref_pattern.match(variableref) != None
        else:
            return cls.is_confml_refs(variableref)
                
    @classmethod
    def is_confml_refs(cls, variableref):
        """
        
        Returns true if the given variable ref is a confml reference
        """
        ret = False
        parts = variableref.split(cls.ref_separator)
        for p in parts:
            if cls.is_confml_ref(p) == True:
                ret = True
        return ret
                

    @classmethod
    def get_confml_ref(cls, variableref):
        """
        
        Returns true if the given variable ref is a confml reference
        """
        pos = variableref.find(cls.ref_separator)
        if pos == -1:
            matchref = cls.ref_pattern.match(variableref)
            if matchref:
                return matchref.group(1)
        else:
            return cls.get_confml_refs(variableref)

    @classmethod
    def get_confml_refs(cls, variableref):
        """
        
        Returns an array of confml refs based on variableref
        """
        parts = variableref.split(cls.ref_separator)
        ret = []
        for p in parts:
            matchref = cls.ref_pattern.match(p)
            if matchref:
                ref = matchref.group(1)
                if not ref in ret:
                    ret.append(matchref.group(1))
            else:
				ret.append(p)
        return ret