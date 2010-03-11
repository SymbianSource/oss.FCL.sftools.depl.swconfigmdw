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
Template plugin for ConE that handles templateml files. Utilizes Jinja template engine.
'''

import re
import os
import sys
import logging
import codecs
import xml.parsers.expat
from jinja2 import Environment, PackageLoader, FileSystemLoader, Template, DictLoader
import traceback
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

try:
    from cElementTree import ElementInclude
except ImportError:
    try:    
        from elementtree import ElementInclude
    except ImportError:
        try:
            from xml.etree import cElementInclude as ElementInclude
        except ImportError:
            from xml.etree import ElementInclude

import __init__

from cone.public import exceptions,plugin,utils,api 
from cone.confml import persistentconfml

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class TemplatemlImpl(plugin.ImplBase):
    
    context = None
    
    """
    Implementation class of template plugin.
    """
    
    IMPL_TYPE_ID = "templateml" 
    
    
    def __init__(self,ref,configuration, reader=None):
        """
        Overloading the default constructor
        """
        plugin.ImplBase.__init__(self,ref,configuration)
        self.logger = logging.getLogger('cone.templateml(%s)' % self.ref)
        self.errors = False
        self.reader = reader
        if self.reader and self.reader.tags:
            self.set_tags(self.reader.tags)

    def get_context(self):
        if TemplatemlImpl.context == None:
            TemplatemlImpl.context = self.create_dict()
        
        return TemplatemlImpl.context
    
    def generate(self, context=None):
        """
        Generate the given implementation.
        """

        self.create_output()
        return 
    
    def create_output(self, layers=None):
        generator = Generator(self.reader.outputs, self.reader.filters, self.get_context(), self.configuration)
        generator.generate(self.output, self.ref)
        return
    
    def get_refs(self):
        refs = []
        for output in self.reader.outputs:
            template = output.template.template
            refs.extend(self._extract_refs_from_template(template))
        return refs
    
    @classmethod
    def _extract_refs_from_template(cls, template_text):
        refs = []
        pattern = re.compile(r'feat_tree\.((?:\.?\w+)*)', re.UNICODE)
        for m in re.finditer(pattern, template_text):
            ref = m.group(1)
            
            # ref may now be e.g. 'MyFeature.MySetting._value', so
            # remove the last part if it starts with an underscore 
            index = ref.rfind('.')
            if index != -1 and index < len(ref) and ref[index + 1] == '_':
                ref = ref[:index]
            
            refs.append(ref)
        return refs
    
    def has_ref(self, refs):
        """
        @returns True if the implementation uses the given ref as input value.
        Otherwise return False.
        """
        
        # Does not support template inheritance
        
        if not isinstance(refs, list):
            refs = [refs] 
        
        for output in self.reader.outputs:
            if re.search("feat_list.*", output.template.template) != None:
                return True
        
        refs_in_templates = self.get_refs()
            
        for ref in refs:
            if ref in refs_in_templates:
                return True
        return False
    
    
    def list_output_files(self):
        """ Return a list of output files as an array. """
        result = []
        for output in self.reader.outputs:
            result.append(os.path.normpath(os.path.join(self.output, output.path, output.filename)))
        return result
    
    def create_dict(self):
        """
        Creates dict from configuration that can be passed to template engine.
        """
        
        context_dict = {}
        
        if self.configuration:
            dview = self.configuration.get_default_view()
            feat_list = []
            feat_tree = {}
            
            def add_feature(feature, feature_dict):
                fea_dict = FeatureDictProxy(feature)
                feat_list.append(fea_dict)
                feature_dict[feature.ref] = fea_dict
                
                # Recursively add sub-features
                for sfeat in feature.list_features():
                    add_feature(feature.get_feature(sfeat), fea_dict)
            
            for fea in dview.list_features():
                add_feature(dview.get_feature(fea), feat_tree)
                
            context_dict['feat_list'] = feat_list
            context_dict['feat_tree'] = feat_tree
            context_dict['configuration'] = self.configuration

        return context_dict

def _expand_refs(text, config):
    if config is not None:
        return utils.expand_refs_by_default_view(text, config.get_default_view())
    else:
        return text

def _read_relative_file(configuration, relative_path, file_path):
    """
    Read data from a file relative to the given other file path.
    """
    # Get the actual path (relative to the current file)
    base_path = os.path.dirname(file_path)
    tempfile_path = os.path.normpath(os.path.join(base_path, relative_path)).replace('\\', '/')
    
    # Read the file
    resource = configuration.get_resource(tempfile_path)
    try:        return resource.read()
    finally:    resource.close()

class TemplatemlImplReader(plugin.ReaderBase):
    """
    Parses a single templateml file
    """ 
    NAMESPACE = 'http://www.s60.com/xml/templateml/1'
    FILE_EXTENSIONS = ['templateml']
    
    def __init__(self, resource_ref=None, configuration=None):
        self.desc = None
        self.namespaces = [self.NAMESPACE]
        self.outputs = None
        self.filters = None
        self.tags = None
        self.resource_ref = resource_ref
        self.configuration = configuration
        
    
    @classmethod
    def read_impl(cls, resource_ref, configuration, etree):
        reader = TemplatemlImplReader(resource_ref, configuration)
        reader.from_elementtree(etree)
        return TemplatemlImpl(resource_ref, configuration, reader)
    
    def fromstring(self, xml_string):
        etree = ElementTree.fromstring(xml_string)
        self.from_elementtree(etree)
    
    def from_elementtree(self, etree):
        ElementInclude.include(etree)
        self.desc = self.parse_desc(etree)
        self.outputs = self.parse_outputs(etree)
        self.filters = self.parse_filters(etree)
        self.tags = self.parse_tags(etree)
         
    def parse_desc(self,etree):
        desc = ""
        desc_elem = etree.find("{%s}desc" % self.namespaces[0])
        if desc_elem != None:
            desc = desc_elem.text
        return desc

    def parse_filters(self, etree):
        filters = []
        filter_elems = etree.findall("{%s}filter" % self.namespaces[0])
        for filter_elem in filter_elems:
            if filter_elem != None:
                filter = Filter()
                
                if filter_elem.get('name') != None:
                    name = filter_elem.get('name')
                    if self.configuration != None:
                        name = utils.expand_refs_by_default_view(name, self.configuration.get_default_view())
                    filter.set_name(name)
                if filter_elem.get('file') != None:
                    file = filter_elem.get('file')
                    if self.configuration != None:
                        file = utils.expand_refs_by_default_view(file, self.configuration.get_default_view())
                    filter.set_path(file)
                if filter_elem.text != None:
                    filter.set_code(filter_elem.text)
                    if filter_elem.get('file') != None:
                        logging.getLogger('cone.templateml').warning("In filter element file attribute and text defined. Using filter found from file attribute.")
                filters.append(filter)
        return filters
    
    def parse_tags(self, etree):
        tags = {}
        for tag in etree.getiterator("{%s}tag" % self.namespaces[0]):
            tagname = tag.get('name','')
            tagvalue = tag.get('value')
            values = tags.get(tagname,[])
            values.append(tagvalue)
            tags[tagname] = values
        return tags
    
    def parse_template(self, output_elem):
        tempfile = TempFile()
        template_elems = output_elem.findall("{%s}template" % self.namespaces[0])
        
        for template_elem in template_elems:
            if template_elem.text != None:
                tempfile.set_template(template_elem.text)
            else:
                for selem in template_elem:
                    tempfile.set_template(selem.text)
                    
            if template_elem.get('file') != None:
                file = template_elem.get('file')
                if template_elem.text != None: 
                    logging.getLogger('cone.templateml').warning("In template element file attribute and text defined. Using template found from file attribute.")
                template_text = _read_relative_file(self.configuration, file, self.resource_ref)
                tempfile.set_template(template_text)
        return tempfile
    
    def parse_outputs(self, etree):
        outputs = []
        output_elems = etree.findall("{%s}output" % self.namespaces[0])
        for output_elem in output_elems:
            if output_elem != None:
                outputfile = OutputFile()
                if output_elem.get('encoding') != None:
                    encoding = output_elem.get('encoding')
                    # Check the encoding
                    try:
                        codecs.lookup(encoding)
                    except LookupError:
                        raise exceptions.ParseError("Invalid output encoding: %s" % encoding)
                    
                    if self.configuration != None:
                        encoding = utils.expand_refs_by_default_view(encoding, self.configuration.get_default_view())
                    outputfile.set_encoding(encoding)
                if output_elem.get('file') != None:
                    file = output_elem.get('file')
                    
                    if self.configuration != None:
                        file = utils.expand_refs_by_default_view(file, self.configuration.get_default_view())
                    outputfile.set_filename(file)
                if output_elem.get('dir') != None:
                    dir = output_elem.get('dir')
                    if self.configuration != None:
                        dir = utils.expand_refs_by_default_view(dir, self.configuration.get_default_view())
                    outputfile.set_path(dir)
                if output_elem.get('ref'):
                    # Fetch the output value from a configuration reference
                    fea = self.configuration.get_default_view().get_feature(output_elem.get('ref'))
                    outputfile.set_filename(fea.value) 
                if output_elem.get('bom'):
                    outputfile.bom = output_elem.get('bom').lower() in ('1', 'true', 't', 'yes', 'y')
                outputfile.set_template(self.parse_template(output_elem))
                outputfile.set_filters(self.parse_filters(output_elem))
                outputs.append(outputfile)
        return outputs

class Generator(object):
    """
    Class that generates
    """
    
    def __init__(self, outputs, filters, context, configuration=None):
        self.outputs = outputs
        self.filters = filters
        self.context = context
        self.configuration = configuration
    
    def generate(self, output_path, ref):
        """ 
        Generates output based on templates 
        """
        if self.outputs != None:
        
            for output in self.outputs:
                try:
                    logging.getLogger('cone.templateml').debug(output)
                    out_path = os.path.abspath(os.path.join(output_path, output.path))
                    if out_path != '':
                        if not os.path.exists(out_path):
                            os.makedirs(out_path)
                    
                    out_file = open(os.path.join(out_path, output.filename), 'wb')
                    
                    if output.template.path:
                        output.template.template = _read_relative_file(self.configuration, output.template.path, ref)
                    
                    dict_loader = DictLoader({'template': output.template.template})
                    env = Environment(loader=dict_loader)

                    # Common filters
                    for filter in self.filters:
                        
                        if filter.path:
                            filter.code = _read_relative_file(self.configuration, filter.path, ref)
                        
                        if not filter.code:
                            logging.getLogger('cone.templateml').warning("Skipping empty filter definition.")
                        else:
                            env.filters[str(filter.name)] = eval(filter.code)
                    
                    # Output file specific filters
                    for filter in output.filters:
                        if filter.path:
                           filter.code = _read_relative_file(self.configuration, filter.path, ref)
                        
                        if not filter.code:
                            logging.getLogger('cone.templateml').warning("Skipping empty filter definition.")
                        else:
                            env.filters[str(filter.name)] = eval(filter.code)
                    
                    template = env.get_template('template')
                    
                    file_string = template.render(self.context)
                    out_file.write(self._encode_data(file_string, output.encoding, output.bom))
                    out_file.close()
                    
                except Exception, e:
                    logging.getLogger('cone.templateml').error('Failed to generate template: %s %s\n%s' % (type(e), e, traceback.format_exc()) )
        else:
            logging.getLogger('cone.templateml').info('No (valid) templates found.')
    
    def _encode_data(self, data, encoding, write_bom):
        """
        Encode the given data using the given encoding and BOM definition.
        @param data: The data to encode.
        @param encoding: The encoding to use.
        @param write_bom: True or False to define whether the BOM should be written
            for Unicode encodings, None for default.
        """
        data = data.encode(encoding)
        
        # Check if we need to do special handling for BOM
        if write_bom is not None:
            BOM_MAPPING = {'utf-8'      : codecs.BOM_UTF8,
                           'utf-16'     : codecs.BOM_UTF16,
                           'utf-16-be'  : codecs.BOM_UTF16_BE,
                           'utf-16-le'  : codecs.BOM_UTF16_LE}
            
            # Use the name from a CodecInfo object to account for
            # aliases (e.g. U8 and UTF-8 both map to utf-8)
            codec_info = codecs.lookup(encoding)
            if codec_info.name in BOM_MAPPING:
                # Add or remove as necessary
                BOM = BOM_MAPPING[codec_info.name]
                if write_bom == True and not data.startswith(BOM):
                    data = BOM + data
                elif write_bom == False and data.startswith(BOM):
                    data = data[len(BOM):]
        return data
        

class OutputFile(object):
    def __init__(self):
        self.filename = ''
        self.path = ''
        self.encoding = "utf-8"
        self.template = TempFile()
        self.filters = []
        self.bom = None

    def set_filename(self, filename):
        self.filename = filename
    
    def set_path(self, path):
        self.path = path
        
    def set_encoding(self, encoding):
        self.encoding = encoding
        
    def set_template(self, template):
        self.template = template

    def add_filter(self, filter):
        self.filters.append(filters)
    
    def set_filters(self, filters):
        self.filters = filters
    
    def __eq__(self, other):
        if (self.template == other.template and self.encoding == other.encoding and self.path == other.path and self.filename == other.filename and self.filters == other.filters):
            return True
        return False
    
    def __repr__(self):
        return "OutputFile(filename=%r, path=%r, encoding=%r, template=%r, filters=%r" % (self.filename, self.path, self.encoding, self.template, self.filters)

class TempFile(object):
    def __init__(self):
        self.template = ""
        self.extensions = []
        self.filters = []
        self.path = ''
    
    def set_path(self, path):
        self.path = path
    
    def set_template(self, template):
        self.template = template
        
    def add_extension(self, extension):
        self.extensions.append(extension)
        
    def add_filter(self, filter):
        self.filters.append(filter)
    
    def add_filter2(self, name, code):
        self.filters.append(Filter(name, code))
        
    def __eq__(self, other):
        if self.template == other.template and self.filters == other.filters and self.extensions == other.extensions and self.path == other.path:
            return True
        return False
        
class Filter(object):
    def __init__(self, name, code):
        self.name = name
        self.code = code
        self.path = None
    
    def __init__(self):
        self.name = None
        self.code = None
        self.path = None
    
    def set_path(self, path):
        self.path = path
    
    def set_name(self, name):
        self.name = name
    
    def set_code(self, code):
        self.code = code
    
    def __eq__(self, other):
        if self.name == other.name and self.code == other.code and self.path == other.path:
            return True
        return False

class FeatureDictProxy(object):
    """
    Proxy class that behaves like a dictionary, but loads attributes from
    the Feature object it proxies only when they are requested.
    """
    def __init__(self, feature):
        self._feature = feature
        self._children = {}
    
    def _get_dict(self):
        result = {
            '_name'        : self._feature.name,
            '_namespace'   : self._feature.namespace,
            '_value'       : self._feature.get_value(),
            '_fqr'         : self._feature.fqr,
            '_type'        : self._feature.type}
        for ref, obj in self._children.iteritems():
            result[ref] = obj
        return result
    
    def items(self):
        return self._get_dict().items()
    
    def iteritems(self):
        return self._get_dict().iteritems()
    
    def __getitem__(self, name):
        if name == '_name':         return self._feature.name        
        elif name == '_namespace':  return self._feature.namespace
        elif name == '_value':      return self._feature.get_value()
        elif name == '_fqr':        return self._feature.fqr
        elif name == '_type':       return self._feature.type
        else:                       return self._children[name]
    
    def __setitem__(self, name, value):
        self._children[name] = value
    
    def __len__(self):
        return len(self._get_dict())
    
    def __eq__(self, other):
        if not isinstance(other, dict):
            return False
        else:
            return self._get_dict() == other
    
    def __ne__(self, other):
        return not (self == other)
