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
import logging
import codecs
import pkg_resources
from jinja2 import Environment, DictLoader
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


from cone.public import exceptions,plugin,utils 

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
    
    def __getstate__(self):
        state = super(TemplatemlImpl, self).__getstate__()
        state['reader'] = self.reader
        return state

    def get_context(self, generation_context):
        ddict = generation_context.impl_data_dict 
        if ddict.get('templateml_context', None) is None:
            ddict['templateml_context'] = self.create_dict()
        return ddict['templateml_context']
    
    def generate(self, context=None):
        """
        Generate the given implementation.
        """
        self.context = context
        self.logger.debug('Generating from %s:%s' % (self.ref, self.lineno))
        self.create_output(context)
        return 
    
    def create_output(self, generation_context):
        templateml_context = self.get_context(generation_context)
        templateml_context['gen_context'] = generation_context
        if not generation_context.configuration:
            generation_context.configuration = self.configuration
        self.reader.expand_output_refs_by_default_view()
        generator = Generator(self.reader.outputs, self.reader.filters, templateml_context, self)
        generator.generate(generation_context, self.ref)
        return
    
    def get_refs(self):
        refs = []
        for output in self.reader.outputs:
            template = output.template.template
            refs.extend(self._extract_refs_from_template(template))
            refs_oa = self._extract_refs_from_output_attribs(output)
            for r in refs_oa:
                if refs.count(r) < 1:
                    refs.append(r)
        return refs
    
    def _extract_refs_from_output_attribs(self, output):
        refs = [] 
        pattern = re.compile(r'\$\{(.*)\}', re.UNICODE)
        for key, value in vars(output).iteritems():
            m = pattern.search(str(value))
            if m:
                ref = m.group(1)
                refs.append(ref)
            if key == 'ref':
                refs.append(value)
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
        return plugin.uses_ref(refs, self.get_refs())
    
    
    def list_output_files(self):
        """ Return a list of output files as an array. """
        result = []
        for output in self.reader.outputs:
            filename = ""
            if output.fearef != None:
                filename = self.configuration.get_default_view().get_feature(output.fearef).value
            else:
                filename = output.filename
            result.append(os.path.normpath(os.path.join(self.output, output.path, filename)))
        return result
    
    def create_dict(self):
        """
        Creates dict from configuration that can be passed to template engine.
        """
        
        context_dict = {}
        
        if self.configuration:
            dview = self.configuration.get_default_view()
            feat_list = []
            feat_tree = FeatureDictProxy(None)
            
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
    NAMESPACE_ID = 'templateml'
    ROOT_ELEMENT_NAME = 'templateml'
    FILE_EXTENSIONS = ['templateml']
    NEWLINE_WIN_PARSE_OPTIONS = ['win', 'windows', 'dos', 'symbian', 'symbianos', 'cr+lf', 'crlf']
    
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
    
    @classmethod
    def get_schema_data(cls):
        return pkg_resources.resource_string('templatemlplugin', 'xsd/templateml.xsd')
    
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
        
        filters_elems = etree.findall("{%s}filters" % self.namespaces[0])
        for filters_elem in filters_elems:
            if filters_elem != None:
                filter = Filter()
                if filters_elem.get('file') != None:
                    file = filters_elem.get('file')
                    if self.configuration != None:
                        file = utils.expand_refs_by_default_view(file, self.configuration.get_default_view())
                    filter.set_path(file)
                if filters_elem.text != None:
                    filter.set_code(filters_elem.text)
                    if filters_elem.get('file') != None:
                        logging.getLogger('cone.templateml'). warning("In filters element file attribute and text defined. Using filters found from file attribute.")
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
                outputfile.set_output_elem(output_elem)
                if output_elem.get('encoding') != None:
                    encoding = output_elem.get('encoding')
                    outputfile.set_encoding(encoding)
                if output_elem.get('file') != None:
                    file = output_elem.get('file')
                    outputfile.set_filename(file)
                if output_elem.get('dir') != None:
                    dir = output_elem.get('dir')
                    outputfile.set_path(dir)
                if output_elem.get('ref'):
                    # Fetch the output value from a configuration reference
                    outputfile.set_fearef(output_elem.get('ref'))
                if output_elem.get('bom'):
                    outputfile.set_bom(output_elem.get('bom'))
                if output_elem.get('newline', ''):
                    outputfile.set_newline(output_elem.get('newline', ''))
                
                outputfile.set_template(self.parse_template(output_elem))
                outputfile.set_filters(self.parse_filters(output_elem))
                outputs.append(outputfile)
                            
        return outputs

    def expand_output_refs_by_default_view(self):
        for output in self.outputs:     
            if output.encoding:
                if self.configuration != None:
                    output.set_encoding(utils.expand_refs_by_default_view(output.encoding, self.configuration.get_default_view()))
                try:
                    codecs.lookup(output.encoding)
                except LookupError:
                    raise exceptions.ParseError("Invalid output encoding: %s" % output.encoding)
            if output.filename:
                if self.configuration != None:
                    output.set_filename(utils.expand_refs_by_default_view(output.filename, self.configuration.get_default_view()))
            if output.path:
                if self.configuration != None:
                    output.set_path(utils.expand_refs_by_default_view(output.path, self.configuration.get_default_view()))
            if output.newline:
                newline = output.newline
                if self.configuration != None:
                    newline = utils.expand_refs_by_default_view(output.newline, self.configuration.get_default_view())
                if newline.lower() in self.NEWLINE_WIN_PARSE_OPTIONS:
                    output.set_newline(OutputFile.NEWLINE_WIN)
            if output.bom:
                bom = output.bom
                if self.configuration != None:
                    bom = utils.expand_refs_by_default_view(output.bom, self.configuration.get_default_view())
                output.bom = bom.lower() in ('1', 'true', 't', 'yes', 'y')
            if output.fearef:
                if self.configuration != None:
                    fea = self.configuration.get_default_view().get_feature(output.fearef)
                    output.set_filename(fea.value)

class Generator(object):
    """
    Class that generates
    """
    
    def __init__(self, outputs, filters, context, implementation=None):
        self.outputs = outputs
        self.filters = filters
        self.context = context
        self.implementation = implementation
    
    def generate(self, generation_context, ref):
        """ 
        Generates output based on templates 
        """
        if self.outputs != None:
        
            for output in self.outputs:
                try:
                    out_path = output.path
                    out_filepath = os.path.join(out_path, output.filename)
                    logging.getLogger('cone.templateml').debug("Output file '%s', encoding '%s'" % (out_filepath, output.encoding))
                    
                    out_file = generation_context.create_file(out_filepath, implementation=self.implementation)
                    
                    if output.template.path:
                        output.template.template = _read_relative_file(generation_context.configuration, output.template.path, ref)
                    
                    dict_loader = DictLoader({'template': output.template.template})
                    
                    if output.newline == OutputFile.NEWLINE_WIN:
                        env = Environment(loader=dict_loader, newline_sequence='\r\n')
                    else:
                        env = Environment(loader=dict_loader)

                    # Common filters
                    for filter in self.filters:
                        if filter.path:
                            filter.code = _read_relative_file(generation_context.configuration, filter.path, ref)
                        
                        if not filter.code:
                            logging.getLogger('cone.templateml').warning("Skipping empty filter definition.")
                        else:
                            # filter elements (lambda functions) have names
                            if filter.name:
                                env.filters[str(filter.name)] = eval(filter.code.replace('\r', ''))
                            # filters elements (any python functions) do not have names
                            else:
                                funcs = {}
                                exec(filter.code.strip().replace('\r', ''), funcs)
                                for k,v in funcs.items():
                                    env.filters[k] = v
                    
                    # Output file specific filters
                    for filter in output.filters:
                        if filter.path:
                            filter.code = _read_relative_file(generation_context.configuration, filter.path, ref)
                        
                        if not filter.code:
                            logging.getLogger('cone.templateml').warning("Skipping empty filter definition.")
                        else:
                            if filter.name:
                                env.filters[str(filter.name)] = eval(filter.code.replace('\r', ''))
                            else:
                                funcs = {}
                                exec(filter.code.strip().replace('\r', ''), funcs)
                                for k,v in funcs.items():
                                    env.filters[k] = v
                    
                    template = env.get_template('template')
                    
                    file_string = template.render(self.context)
                    out_file.write(self._encode_data(file_string, output.encoding, output.bom))
                    out_file.close()
                    
                except Exception, e:
                    utils.log_exception(
                        logging.getLogger('cone.templateml'),
                        '%r: Failed to generate output: %s: %s' % (self.implementation, type(e).__name__, e))
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
    NEWLINE_UNIX = "unix"
    NEWLINE_WIN = "win" 
    
    def __init__(self):
        self.filename = ''
        self.path = ''
        self.encoding = "utf-8"
        self.template = TempFile()
        self.filters = []
        self.bom = None
        self.newline = self.NEWLINE_UNIX
        self.fearef = None
        self.output_elem = None

    def set_newline(self, newline):
        self.newline = newline

    def set_filename(self, filename):
        self.filename = filename
    
    def set_path(self, path):
        self.path = path
        
    def set_encoding(self, encoding):
        self.encoding = encoding
        
    def set_template(self, template):
        self.template = template

    def add_filter(self, filter):
        self.filters.append(filter)
    
    def set_filters(self, filters):
        self.filters = filters
    
    def set_bom(self, bom):
        self.bom = bom
        
    def set_fearef(self, ref):
        self.fearef = ref
        
    def set_output_elem(self, output_elem):
        self.output_elem = output_elem
    
    def __eq__(self, other):
        if other:
            if (self.template == other.template and self.newline == other.newline and self.encoding == other.encoding and self.path == other.path and self.filename == other.filename and self.filters == other.filters):
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
        if other:
            if self.template == other.template and self.filters == other.filters and self.extensions == other.extensions and self.path == other.path:
                return True
        return False
    
        
class Filter(object):
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
        result = {}
        if self._feature is not None:
            result.update({
                '_name'        : self._feature.name,
                '_namespace'   : self._feature.namespace,
                '_value'       : self._feature.get_value(),
                '_fqr'         : self._feature.fqr,
                '_type'        : self._feature.type})
        result.update(self._children)
        return result
    
    def items(self):
        return self._get_dict().items()
    
    def iteritems(self):
        return self._get_dict().iteritems()
    
    def __getitem__(self, name):
        if self._feature is not None:
            if name == '_name':         return self._feature.name
            elif name == '_namespace':  return self._feature.namespace
            elif name == '_value':      return self._feature.get_value()
            elif name == '_fqr':        return self._feature.fqr
            elif name == '_type':       return self._feature.type
        
        try:
            return self._children[name]
        except KeyError:
            if self._feature:
                msg = "Feature '%s.%s' not found" % (self._feature.fqr, name)
            else:
                msg = "Feature '%s' not found" % name
            raise exceptions.NotFound(msg)
    
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
