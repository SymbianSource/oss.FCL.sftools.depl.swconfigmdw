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
import logging
import __init__
from cone.public import *
from cone.public import _plugin_reader
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class ImplTest(plugin.ImplBase):
    def __init__(self,ref,configuration):
        plugin.ImplBase.__init__(self,ref,configuration)
        self.generate_invoked = False
        self.refs = ["dummy1.too"]
        self.output_files = []
    def generate(self, context=None):
        self.generate_invoked = True
        if context and hasattr(context, 'objects'):
            context.objects.append(self)

    def get_refs(self):
        return self.refs

    def list_output_files(self):
        return self.output_files


class TestPluginReader(unittest.TestCase):
    def setUp(self):
        pass

class TestCommonNamespaceHandling(unittest.TestCase):
    
    def setUp(self):
        pass
        
        
    def tearDown(self):
        pass
    
    def test_implcontainer_reader_get_condition(self):
        root = utils.etree.fromstring("<container/>")
        self.assertEquals(plugin.ImplContainerReader.get_condition(root), None)
        
        root = utils.etree.fromstring("<container condition='test'/>")
        condition = plugin.ImplContainerReader.get_condition(root)
        self.assertTrue(isinstance(condition, rules.SimpleCondition))
        self.assertEquals(condition.left.expression, "test")
        self.assertEquals(condition.right.expression, "true")
        
        root = utils.etree.fromstring("<container condition='${feature.one}' value='2'/>")
        condition = plugin.ImplContainerReader.get_condition(root)
        self.assertTrue(isinstance(condition, rules.SimpleCondition))
        self.assertEquals(condition.left.expression, "${feature.one}")
        self.assertEquals(condition.right.expression, "2")


    def test_implcontainer_reader_get_reader_classes(self):
        classes = plugin.ImplContainerReader.get_reader_classes()
        self.assertTrue(classes.has_key('http://www.symbianfoundation.org/xml/implml/1'))
        
    def test_get_test_container(self):
        xml_data = """<?xml version="1.0"?>
            <container xmlns="http://www.symbianfoundation.org/xml/implml/1">
            </container>
            """
        container = plugin.ImplContainerReader.read_implementation(xml_data)
        self.assertTrue(isinstance(container, plugin.ImplContainer))

    def test_get_test_container_with_sub_containers(self):
        xml_data = """<?xml version="1.0"?>
            <container xmlns="http://www.symbianfoundation.org/xml/implml/1">
              <container />
              <container />
              <container xmlns="http://www.symbianfoundation.org/xml/implml/1">
                <container />
              </container>
            </container>
            """
        container = plugin.ImplContainerReader.read_implementation(xml_data)
        self.assertTrue(isinstance(container, plugin.ImplContainer))
        self.assertEquals(len(container), 3)
    
    def test_containers_with_phases(self):
        xml_data = """<?xml version="1.0"?>
            <implml:container xmlns:implml="http://www.symbianfoundation.org/xml/implml/1">
              <implml:container />
              <implml:container />
              <container xmlns="http://www.symbianfoundation.org/xml/implml/1">
                <phase name="post"/>
              </container>
            </implml:container>
            """
        container = plugin.ImplContainerReader.read_implementation(xml_data)
        self.assertEquals(container.invocation_phase(), ['post','normal'])
        self.assertEquals(container[2].invocation_phase(), ['post'])
    
    def test_containers_with_tags(self):
        xml_data = """<?xml version="1.0"?>
            <container xmlns="http://www.symbianfoundation.org/xml/implml/1">
              <tag name="target" value="rofs2"/>
              <tag name="foobar" value="test"/>
              <container />
              <container />
              <container xmlns="http://www.symbianfoundation.org/xml/implml/1">
                <tag name="target" value="rofs3"/>
                <phase name="post"/>
              </container>
            </container>
            """
        container = plugin.ImplContainerReader.read_implementation(xml_data)
        self.assertEquals(container[2].get_tags(), {'target': ['rofs3']})
        self.assertEquals(container.get_tags(), {'target': ['rofs2','rofs3'],
                                                 'foobar': ['test']})

    def test_tempfeature_definitions(self):
        xml_data = """<?xml version="1.0"?>
            <container xmlns="http://www.symbianfoundation.org/xml/implml/1">
                <tempVariable ref="TempFeature.root" value="true"/>
                <container>
                    <tempVariable ref="TempFeature.String"   type="string"   value="testing"/>
                    <tempVariable ref="TempFeature.Int"      type="int"      value="500"/>
                    <tempVariable ref="TempFeature.Real"     type="real"     value="1.5"/>
                    <tempVariable ref="TempFeature.Boolean"  type="boolean"  value="true"/>
                    <tempVariable ref="TempFeature.Defaults"/>
                    
                    <tempVariableSequence ref="TempFeature.Seq">
                        <tempVariable ref="String"   type="string"/>
                        <tempVariable ref="Int"      type="int"/>
                        <tempVariable ref="Real"     type="real"/>
                        <tempVariable ref="Boolean"  type="boolean"/>
                        <tempVariable ref="DefaultType"/>
                    </tempVariableSequence>
                </container>
            </container>
            """
        
        Tfd = _plugin_reader.TempVariableDefinition
        Tsfd = _plugin_reader.TempVariableSequenceDefinition
        expected_1 = [
            Tfd('TempFeature.String', 'string', 'testing'),
            Tfd('TempFeature.Int', 'int', '500'),
            Tfd('TempFeature.Real', 'real', '1.5'),
            Tfd('TempFeature.Boolean', 'boolean', 'true'),
            Tfd('TempFeature.Defaults', 'string', ''),
            Tsfd('TempFeature.Seq', [('String', 'string'),
                                     ('Int', 'int',),
                                     ('Real', 'real'),
                                     ('Boolean', 'boolean'),
                                     ('DefaultType', 'string')]),
        ]
        expected_2 = [Tfd('TempFeature.root', 'string', value='true')] + expected_1
        
        container = plugin.ImplContainerReader.read_implementation(xml_data)
        self.assertEquals(container[0].get_temp_variable_definitions(), expected_1)
        self.assertEquals(container.get_temp_variable_definitions(), expected_2)

    def test_get_test_container_with_condition(self):
        xml_data = """<?xml version="1.0"?>
            <container xmlns="http://www.symbianfoundation.org/xml/implml/1"
                       condition="${feature.test}">
            </container>
            """
        container = plugin.ImplContainerReader.read_implementation(xml_data)
        self.assertTrue(isinstance(container.condition, rules.SimpleCondition))
        self.assertEquals(container.condition.left.expression, "${feature.test}")
        self.assertEquals(container.condition.right.expression, "true")

        xml_data = """<?xml version="1.0"?>
            <container xmlns="http://www.symbianfoundation.org/xml/implml/1"
                       condition="${feature.test}"
                       value="false">
            </container>
            """
        container = plugin.ImplContainerReader.read_implementation(xml_data)
        self.assertTrue(isinstance(container.condition, rules.SimpleCondition))
        self.assertEquals(container.condition.left.expression, "${feature.test}")
        self.assertEquals(container.condition.right.expression, "false")

    def test_impl_container_with_condition(self):
        context = plugin.GenerationContext()
        context.configuration = api.Configuration()
        context.configuration.add_feature(api.Feature("test"))
        context.configuration.get_default_view().test.value = True

        xml_data = """<?xml version="1.0"?>
            <container xmlns="http://www.symbianfoundation.org/xml/implml/1"
                       condition="${test}"
                       value="false">
            </container>
            """
        container = plugin.ImplContainerReader.read_implementation(xml_data)
        imp1  = ImplTest("implml/test.content",None)
        container.append(imp1)
        container.generate(context)
        self.assertFalse(imp1.generate_invoked)
        context.configuration.get_default_view().test.value = False
        container.generate(context)
        self.assertTrue(imp1.generate_invoked)
