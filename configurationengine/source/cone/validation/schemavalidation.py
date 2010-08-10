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

import sys, os
import logging
import StringIO
import pkg_resources
import jinja2
from cone.public import api, utils, exceptions
import cone.public.plugin

log = logging.getLogger('cone.schemavalidation')

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

CONFML_SCHEMA_DIR = 'confml_xsd'

SCHEMA_FILES_BY_NAMESPACE = {'http://www.s60.com/xml/confml/1': 'confml.xsd',
                             'http://www.s60.com/xml/confml/2': 'confml2.xsd'}

_schema_cache = {}

# ============================================================================

def validate_confml_file(config, ref):
    """
    Schema-validate the given ConfML file in a configuration.
    @param config: The configuration.
    @param ref: The resource reference of the file to validate.
    @return: A list of api.Problem objects.
    """
    return _validate_file(config, ref, validate_confml_data)

def validate_implml_file(config, ref):
    """
    Schema-validate the given ImplML file in a configuration.
    @param config: The configuration.
    @param ref: The resource reference of the file to validate.
    @return: A list of api.Problem objects.
    """
    return _validate_file(config, ref, validate_implml_data)

def validate_confml_data(data):
    """
    Schema-validate the given ConfML data.
    
    @raise ParseError: Something is wrong with the data (invalid XML,
        unsupported ConfML namespace or not conforming to the schema)
    """
    _validate_data(data, _get_confml_schema_for_namespace, 'xml.confml')

def validate_implml_data(data):
    """
    Schema-validate the given ImplML data.
    
    @raise ParseError: Something is wrong with the data (invalid XML,
        unsupported ImplML namespace or not conforming to the schema)
    """
    _validate_data(data, _get_implml_schema_for_namespace, 'xml.implml')

# ============================================================================

def _validate_file(config, ref, data_validator_func):
    res = config.get_resource(ref)
    try:        data = res.read()
    finally:    res.close()
    
    problem = None
    try:
        data_validator_func(data)
    except exceptions.ParseError, e:
        problem = api.Problem.from_exception(e)

    if problem:
        problem.file = ref
        return [problem]
    else:
        return []

def _parse_schema(filename, file_data_dict):
    """
    Parse a schema using a filename-data dictionary as the source.
    @param filename: Name of the schema file to parse.
    @param file_data_dict: Dictionary mapping file names to file data.
    @return: The parsed schema object.
    """
    if filename not in file_data_dict:
        raise RuntimeError("Could not parse XML schema file '%s', no such file" % filename)
    
    schema_data = file_data_dict[filename]
    
    import lxml.etree
    
    parser = lxml.etree.XMLParser()
    class Resolver(lxml.etree.Resolver):
        def resolve(self, url, id, context):
            if url not in file_data_dict:
                log.error("Could not resolve schema file '%s', no such file" % url)
                raise RuntimeError("No file named '%s'" % url)
            data = file_data_dict[url]
            return self.resolve_string(data, context)
    parser.resolvers.add(Resolver())
    
    try:
        schema_doc = lxml.etree.fromstring(schema_data, parser=parser)
        schema = lxml.etree.XMLSchema(schema_doc)
    except lxml.etree.LxmlError, e:
        raise RuntimeError(
            "Error parsing schema file '%s': %s: %s" \
            % (filename, e.__class__.__name__, str(e)))
    return schema

def _validate_data(data, schema_resolver_func, xml_parse_problem_type):
    """
    Validate the given XML data.
    @param data: The raw binary data to validate.
    @param schema_resolver_func: The function used to resolve the
        schema used for validation. The function is given the namespace
        of the root element and is supposed to return the schema object
        and problem type to use, or raise a ParseError.
    @param xml_parse_problem_type: Problem type to use if XML parsing
        fails of the data fails.
    
    @raise ParseError: Something is wrong with the data (invalid XML
        or not conforming to the schema)
    """
    # Find out the XML namespace in the root element
    try:
        namespace, _ = utils.xml.get_xml_root(StringIO.StringIO(data))
    except exceptions.XmlParseError, e:
        e.problem_type = xml_parse_problem_type
        raise e
    
    schema, problem_type = schema_resolver_func(namespace)
    
    # Parse the XML document
    import lxml.etree
    try:
        doc = lxml.etree.fromstring(data)
    except lxml.etree.XMLSyntaxError, e:
        raise exceptions.XmlParseError(
            "XML parse error on line %d: %s" % (e.position[0], e),
            problem_lineno  = e.position[0],
            problem_msg     = str(e),
            problem_type    = xml_parse_problem_type)
    
    # Validate the document against the schema
    if not schema.validate(doc):
        error = schema.error_log.last_error
        raise exceptions.XmlSchemaValidationError(
            "Line %d: %s" % (error.line, error.message),
            problem_lineno  = error.line,
            problem_msg     = error.message,
            problem_type    = problem_type)
    

class UnsupportedNamespaceError(exceptions.ParseError):
    pass

_confml_schema_file_cache = None
def get_confml_schema_files():
    global _confml_schema_file_cache
    if _confml_schema_file_cache is None:
        _confml_schema_file_cache = _load_confml_schema_files()
    return _confml_schema_file_cache

def get_schema_file_data(file):
    """
    Return the data of the given XML schema file.
    
    @raise ValueError: No such schema file exists.
    """
    resource_path = CONFML_SCHEMA_DIR + '/' + file
    if pkg_resources.resource_exists('cone.validation', resource_path):
        data = pkg_resources.resource_string('cone.validation', resource_path)
        return data
    else:
        msg = "Could not get schema file '%s': Package resource '%s' does not exist" \
            % (file, resource_path)
        raise ValueError(msg)

def get_schema_file_for_namespace(namespace):
    """
    Return the correct schema file name for the given namespace.
    
    @param namespace: The namespace for which to get the schema file.
    @return: The name of the schema file (suitable for calling
        get_schema_file_data() with), or None if no schema is associated
        with the namespace.
    """
    return SCHEMA_FILES_BY_NAMESPACE.get(namespace, None)


def _get_confml_schema_for_namespace(namespace):
    """
    Return the correct XML schema and problem type ID for
    the given ConfML namespace.
    @return: Tuple (schema, problem_type).
    """
    PROBLEM_TYPE = 'schema.confml'
    
    # Return a cached schema if possible
    if namespace in _schema_cache:
        return _schema_cache[namespace], PROBLEM_TYPE
    
    # Get the schema file and its raw byte data
    schema_file = get_schema_file_for_namespace(namespace)
    if schema_file is None:
        raise exceptions.ConfmlParseError(
            "Unsupported ConfML namespace '%s'" % namespace)
    schema_data = get_schema_file_data(schema_file)
    
    # Parse the schema
    import lxml.etree
    parser = lxml.etree.XMLParser()
    class PackageDataResolver(lxml.etree.Resolver):
        def resolve(self, url, id, context):
            data = get_schema_file_data(url)
            return self.resolve_string(data, context)
    parser.resolvers.add(PackageDataResolver())
    schema_doc = lxml.etree.fromstring(schema_data, parser=parser)
    schema = lxml.etree.XMLSchema(schema_doc)
    
    _schema_cache[namespace] = schema
    return schema, PROBLEM_TYPE

def _load_confml_schema_files():
    files = {}
    for name in pkg_resources.resource_listdir('cone.validation', CONFML_SCHEMA_DIR):
        path = CONFML_SCHEMA_DIR + '/' + name
        if path.lower().endswith('.xsd'):
            files[name] = pkg_resources.resource_string('cone.validation', path)
    return files

# ============================================================================
#
#
# ============================================================================

# Reader class list stored here so that it can be used to check if the reader
# class list changes, and reload the schema files in that case
_implml_reader_class_list = None

_implml_schema_file_cache = None
_implml_schema_cache = {}

def _check_reader_class_list():
    """
    Check if the reader class list has changed, and clear all caches if so.
    """
    global _implml_reader_class_list
    global _implml_schema_file_cache
    global _implml_schema_cache
    
    rc_list = cone.public.plugin.ImplFactory.get_reader_classes()
    if _implml_reader_class_list is not rc_list:
        _implml_reader_class_list = rc_list
        _implml_schema_file_cache = None
        _implml_schema_cache = {}

def dump_schema_files(dump_dir):
    CONFML_SCHEMA_DIR = os.path.join(dump_dir, 'confml')
    IMPLML_SCHEMA_DIR = os.path.join(dump_dir, 'implml')
    if not os.path.exists(CONFML_SCHEMA_DIR):
        os.makedirs(CONFML_SCHEMA_DIR)
    if not os.path.exists(IMPLML_SCHEMA_DIR):
        os.makedirs(IMPLML_SCHEMA_DIR)
    
    def dump_files(files, dir):
        for name, data in files.iteritems():
            path = os.path.join(dir, name)
            f = open(path, 'wb')
            try:        f.write(data)
            finally:    f.close()
    
    dump_files(get_confml_schema_files(), CONFML_SCHEMA_DIR)
    dump_files(get_implml_schema_files(), IMPLML_SCHEMA_DIR)

class _ImplmlReaderEntry(object):
    def __init__(self, id, namespace, data, root_elem_name, schema_problem_sub_id):
        self.id = id
        self.filename = id + '.xsd'
        self.namespace = namespace
        self.data = data
        self.root_elem_name = root_elem_name
        self.schema_problem_sub_id = schema_problem_sub_id

def get_implml_schema_files():
    """
    Return a dictionary of ImplML schema file data by file name.
    """
    global _implml_schema_file_cache
    
    _check_reader_class_list()
    if _implml_schema_file_cache is None:
        _implml_schema_file_cache = _load_implml_schema_files()
    return _implml_schema_file_cache

def _load_implml_schema_files():
    result = {}
    result['implml.xsd'] = _generate_implml_schema_data()
    
    result['XInclude.xsd'] = pkg_resources.resource_string(
        'cone.validation', CONFML_SCHEMA_DIR + '/XInclude.xsd')
    
    for entry in _get_implml_reader_entries():
        if entry.data is not None:
            result[entry.filename] = entry.data
        else:
            result[entry.filename] = _generate_default_schema_data(entry)
    return result

def _get_implml_reader_entries():
    entries = []
    for rc in cone.public.plugin.ImplFactory.get_reader_classes():
        # Skip ImplContainerReader
        if rc is cone.public.plugin.ImplContainerReader:
            continue
        
        entry = _ImplmlReaderEntry(rc.NAMESPACE_ID,
                                   rc.NAMESPACE,
                                   rc.get_schema_data(),
                                   rc.ROOT_ELEMENT_NAME,
                                   rc.SCHEMA_PROBLEM_SUB_ID)
        entries.append(entry)
    return entries

def _generate_implml_schema_data():
    template_data = pkg_resources.resource_string('cone.validation', 'implml_xsd/implml-template.xsd')
    template = jinja2.Template(template_data)
    data = template.render(data=_get_implml_reader_entries()).encode('utf-8')
    return data

def _generate_default_schema_data(entry):
    template_data = pkg_resources.resource_string('cone.validation', 'implml_xsd/default-impl-schema-template.xsd')
    template = jinja2.Template(template_data)
    data = template.render(entry=entry).encode('utf-8')
    return data

def _get_implml_schema_for_namespace(namespace):
    """
    Return the correct XML schema and problem type ID for
    the given ImplML namespace.
    @return: Tuple (schema, problem_type).
    """
    global _implml_schema_cache
    
    problem_type_sub_id = None
    filename = None
    if namespace == 'http://www.symbianfoundation.org/xml/implml/1':
        filename = 'implml.xsd'
        problem_type_sub_id = 'implml'
    else:
        for entry in _get_implml_reader_entries():
            if entry.namespace == namespace:
                filename = entry.filename
                problem_type_sub_id = entry.schema_problem_sub_id
                break
    if filename is None:
        raise exceptions.ImplmlParseError(
            "Unsupported ImplML namespace: %s" % namespace)
    
    # Check reader classes before trying to use the schema cache
    _check_reader_class_list()
    
    # Get the schema from cache if possible
    if filename in _implml_schema_cache:
        return _implml_schema_cache[filename]
    
    file_data_dict = get_implml_schema_files()
    if filename not in file_data_dict:
        raise exceptions.ImplmlParseError(
            "ImplML schema file '%s' does not exist!" % filename)
    
    schema = _parse_schema(filename, file_data_dict)
    problem_type = 'schema.implml'
    if problem_type_sub_id:
        problem_type += '.' + problem_type_sub_id
    return schema, problem_type

# ============================================================================
#
#
# ============================================================================

class SchemaValidationTestMixin(object):
    """
    Mix-in class for providing assertion methods for unittest.TestCase sub-classes
    testing schema validation.
    """
    
    def assert_schemavalidation_succeeds(self, type, dir, namespace=None):
        """
        Assert that schema validation succeeds for all the files in the given directory.
        @param type: Type of the schema validation to perform, can be 'confml' or 'implml'.
        @param dir: The directory containing the files to validate
        @param namespace: If not None, specifies the namespace that the root element
            in all the must have. If any of the files has a different namespace, the
            assertion fails.
        """
        errors = []
        for file in self._get_files(dir):
            f = open(file, 'rb')
            try:        data = f.read()
            finally:    f.close()
            
            if namespace is not None:
                self._check_root_element_namespace(file, data, namespace)
            
            validate_data = self._get_validator_function_for_type(type)
            try:
                validate_data(data)
            except Exception, e:
                errors.append(file)
                errors.append("Raised: %r" % e)
        
        if errors:
            self.fail('\n'.join(errors))
    
    def assert_schemavalidation_fails(self, type, dir, namespace=None, problem_type=None):
        """
        Assert that schema validation fails for all the files in the given directory.
        @param type: Type of the schema validation to perform, can be 'confml' or 'implml'.
        @param dir: The directory containing the files to validate
        @param namespace: If not None, specifies the namespace that the root element
            in all the must have. If any of the files has a different namespace, the
            assertion fails.
        @param: problem_type: If not None, specifies the problem type that the
            SchemaValidationError raised from validation must contain.
        """
        errors = []
        for file in self._get_files(dir):
            f = open(file, 'rb')
            try:        data = f.read()
            finally:    f.close()
            
            if namespace is not None:
                self._check_root_element_namespace(file, data, namespace)
            
            validate_data = self._get_validator_function_for_type(type)
            try:
                validate_data(data)
                errors.append(file)
            except exceptions.XmlSchemaValidationError, e:
                if problem_type is not None:
                    if e.problem_type != problem_type:
                        errors.append(file)
                        errors.append("Problem type was '%s', expected '%s'" % (e.problem_type, problem_type))
        
        if errors:
            self.fail('The following files were reported as valid when they should not have been:\n%s' % '\n'.join(errors))
    
    
    def _get_files(self, dir):
        """
        Return a list of all files in the given directory.
        @param dir: The directory.
        @return: List of all files in the dir. Each entry has the
            also the directory joined to it.
        """
        files = []
        for name in os.listdir(dir):
            path = os.path.join(dir, name)
            if os.path.isfile(path):
                files.append(path)
        return files
    
    def _check_root_element_namespace(self, file_path, data, expected_namespace):
        file_namespace, _ = utils.xml.get_xml_root(StringIO.StringIO(data))
        if file_namespace != expected_namespace:
            msg = "Error testing schema validation with file '%s': "\
                  "Root element namespace is not what was expected (expected '%s', got '%s')"\
                  % (file_path, expected_namespace, file_namespace)
            self.fail(msg)
    
    def _get_validator_function_for_type(self, type):
        if type == 'implml':
            return validate_implml_data
        elif type == 'confml':
            return validate_confml_data
        else:
            raise ValueError("Invalid schema validation type '%s', should be 'implml' or 'confml'" % type)
