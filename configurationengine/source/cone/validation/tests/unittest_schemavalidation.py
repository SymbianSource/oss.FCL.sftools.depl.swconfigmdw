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

import unittest
import os
import StringIO

from testautomation.base_testcase import BaseTestCase
from cone.public import api, plugin, utils, exceptions
from cone.validation import schemavalidation 

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

CONFML1_NAMESPACE = 'http://www.s60.com/xml/confml/1'
CONFML2_NAMESPACE = 'http://www.s60.com/xml/confml/2'

class DummyResource(object):
    def __init__(self, data):
        self.data = data
    def read(self):
        return self.data
    def close(self):
        pass

class DummyConfiguration(object):
    def __init__(self, resources):
        self.resources = resources
    
    def get_resource(self, ref):
        if ref in self.resources:
            return DummyResource(self.resources[ref])
        else:
            raise exceptions.NotFound("No such resource '%s'!" % ref)

class TestConfmlSchemaValidation(BaseTestCase, schemavalidation.SchemaValidationTestMixin):
    
    def test_valid_confml2_files(self):
        self.assert_schemavalidation_succeeds(
            type = 'confml',
            dir = os.path.join(ROOT_PATH, 'testdata/schema/confml2/valid'),
            namespace = CONFML2_NAMESPACE)
    
    def test_invalid_confml2_files(self):
        self.assert_schemavalidation_fails(
            type = 'confml',
            dir = os.path.join(ROOT_PATH, 'testdata/schema/confml2/invalid'),
            namespace = CONFML2_NAMESPACE)
    
    def test_valid_confml1_files(self):
        self.assert_schemavalidation_succeeds(
            type = 'confml',
            dir = os.path.join(ROOT_PATH, 'testdata/schema/confml1/valid'),
            namespace = CONFML1_NAMESPACE)
    
    def test_invalid_confml1_files(self):
        self.assert_schemavalidation_fails(
            type = 'confml',
            dir = os.path.join(ROOT_PATH, 'testdata/schema/confml1/invalid'),
            namespace = CONFML1_NAMESPACE)
    
    def test_validate_confml_invalid_xml_data(self):
        config = DummyConfiguration({'foo.confml': 'foo'})
        problems = schemavalidation.validate_confml_file(config, 'foo.confml')
        self.assertEquals(len(problems), 1)
        prob = problems[0]
        #self.assertEquals(prob.type, api.Problem.TYPE_XML_PROBLEM)
        self.assertEquals(prob.severity, api.Problem.SEVERITY_ERROR)
        self.assertEquals(prob.line, 1)
    
    def test_validate_confml_invalid_xml_data_but_valid_root(self):
        REF = 'test.confml'
        DATA = """<?xml version="1.0" encoding="UTF-8"?>
            <configuration xmlns="http://www.s60.com/xml/confml/2">
            <test someattr/>
            </configuration>""".encode('utf-8')
        config = DummyConfiguration({REF: DATA})
        problems = schemavalidation.validate_confml_file(config, REF)
        self.assertEquals(len(problems), 1)
        prob = problems[0]
        #self.assertEquals(prob.type, api.Problem.TYPE_XML_PROBLEM)
        self.assertEquals(prob.severity, api.Problem.SEVERITY_ERROR)
        self.assertEquals(prob.line, 3)
    
    def test_validate_confml_unsupported_namespace(self):
        DATA = """<?xml version="1.0" encoding="UTF-8"?>
            <unsupported xmlns="http://www.test.com/xml/unsupported">
                <test someattr="yay"/>
            </unsupported>""".encode('utf-8')
        self.assertRaises(exceptions.ConfmlParseError, schemavalidation.validate_confml_data, DATA)




class TestImplmlSchemaValidation(BaseTestCase, schemavalidation.SchemaValidationTestMixin):
    
    DUMMY1_XSD_DATA = """<?xml version="1.0" encoding="UTF-8"?>
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
               targetNamespace="http://www.dummy.com/dummy1"
               elementFormDefault="qualified">
        
        <xs:element name="dummy1">
            <xs:complexType>
                <xs:choice minOccurs="0" maxOccurs="unbounded">
                    <xs:element name="myElem" type="xs:string" minOccurs="0" maxOccurs="unbounded"/>
                </xs:choice>
            </xs:complexType>
        </xs:element>
    </xs:schema>"""
    
    DUMMY2_XSD_DATA = """<?xml version="1.0" encoding="UTF-8"?>
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
               targetNamespace="http://www.dummy.com/dummy2"
               elementFormDefault="qualified">
        
        <xs:element name="dummy2">
            <xs:complexType>
                <xs:choice minOccurs="0" maxOccurs="unbounded">
                    <xs:element name="someElem" type="xs:string" minOccurs="0" maxOccurs="unbounded"/>
                </xs:choice>
            </xs:complexType>
        </xs:element>
    </xs:schema>"""
    
    def setUp(self):
        class MockReader1(plugin.ReaderBase):
            NAMESPACE = "http://www.dummy.com/dummy1"
            NAMESPACE_ID = "dummy1ml"
            FILE_EXTENSIONS = ['dummy1ml']
            ROOT_ELEMENT_NAME = 'dummy1'
            @classmethod
            def get_schema_data(cls):
                return self.DUMMY1_XSD_DATA
        class MockReader2(plugin.ReaderBase):
            NAMESPACE = "http://www.dummy.com/dummy2"
            NAMESPACE_ID = "dummy2ml"
            FILE_EXTENSIONS = ['dummy2ml']
            ROOT_ELEMENT_NAME = 'dummy2'
            @classmethod
            def get_schema_data(cls):
                return self.DUMMY2_XSD_DATA
        class MockReader3(plugin.ReaderBase):
            NAMESPACE = "http://www.dummy.com/dummy3"
            NAMESPACE_ID = "dummy3ml"
            FILE_EXTENSIONS = ['dummy3ml']
            ROOT_ELEMENT_NAME = 'dummy3'
        plugin.ImplFactory.set_reader_classes_override([MockReader1, MockReader2, MockReader3])
    
    def tearDown(self):
        plugin.ImplFactory.set_reader_classes_override(None)
    
    def test_valid_implml_files(self):
        self.assert_schemavalidation_succeeds(
            type = 'implml',
            dir = os.path.join(ROOT_PATH, 'testdata/schema/implml/valid'))
    
    def test_invalid_implml_files(self):
        self.assert_schemavalidation_fails(
            type = 'implml',
            dir = os.path.join(ROOT_PATH, 'testdata/schema/implml/invalid'))
    
    def test_validate_implml_invalid_xml_data(self):
        self.assertRaises(exceptions.XmlParseError, schemavalidation.validate_implml_data, "foo")
    
    def test_validate_implml_invalid_xml_data_but_valid_root(self):
        DATA = """<?xml version="1.0" encoding="UTF-8"?>
            <implml>
            <test someattr/>
            </implml>""".encode('utf-8')
        self.assertRaises(exceptions.ImplmlParseError, schemavalidation.validate_implml_data, DATA)
    
    def test_validate_implml_unsupported_namespace(self):
        DATA = """<?xml version="1.0" encoding="UTF-8"?>
            <unsupported xmlns="http://www.test.com/xml/unsupported">
                <test someattr="yay"/>
            </unsupported>""".encode('utf-8')
        self.assertRaises(exceptions.ImplmlParseError, schemavalidation.validate_implml_data, DATA)

if __name__ == '__main__':
    unittest.main()
