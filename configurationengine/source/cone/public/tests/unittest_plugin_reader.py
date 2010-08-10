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

from cone.public import *
from cone.public import _plugin_reader
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))


class MockImpl(plugin.ImplBase):
    def __init__(self, data):
        self.data = data
        self.generate_invoked = False
    
    @classmethod
    def create(cls, resource_ref, configuration, data):
        impl = cls(data)
        plugin.ImplBase.__init__(impl, resource_ref, configuration)
        return impl
    
    def generate(self, context=None):
        if context and hasattr(context,'objects'):
            context.objects.append(self) 
        self.generate_invoked = True
    
    def __repr__(self):
        return "MockImpl(%r)" % self.data
    
    def __eq__(self, other):
        if type(self) == type(other):
            return self.data == other.data
        else:
            return False
    
    def __ne__(self, other):
        return not (self == other)
        
    def __lt__(self, other):
        if type(self) == type(other):
            return self.data < other.data
        else:
            return False

class MockReaderBase(plugin.ReaderBase):
    @classmethod
    def read_impl(cls, resource_ref, configuration, root_elem):
        data = [cls.__name__, resource_ref]
        for elem in root_elem.findall('{%s}elem' % cls.NAMESPACE):
            data.append(elem.attrib)
        return MockImpl.create(resource_ref, configuration, data)

class MockReader(MockReaderBase):
    NAMESPACE = "http://www.test.com/xml/1"
    NAMESPACE_ID = "mock"
    ROOT_ELEMENT_NAME = "impl"
    FILE_EXTENSIONS = ['mockml']

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
        plugin.ImplFactory.set_reader_classes_override([MockReader])
    
    def tearDown(self):
        plugin.ImplFactory.set_reader_classes_override(None)
    
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
    
    def test_get_reader_for_namespace(self):
        self.assertEquals(plugin.ReaderBase.get_reader_for_namespace('http://www.symbianfoundation.org/Foo'), None)
        self.assertEquals(plugin.ReaderBase.get_reader_for_namespace('http://www.symbianfoundation.org/xml/implml/1'), 
                          plugin.ImplContainerReader)

    def test_read_container_via_common_readerbase(self):
        prj = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'testdata')))
        config = prj.create_configuration("test.confml", True)
        container = plugin.read_impl_from_location('layer1/implml/test.implml', config, 4)
        self.assertEquals(container.invocation_phase(), 'normal')
        self.assertEquals(container.path, 'layer1/implml/test.implml')
        self.assertEquals(container.lineno, 4)
        self.assertEquals(container[0].invocation_phase(), 'normal')
        self.assertEquals(container[0].path, 'layer1/implml/test.implml')
        self.assertEquals(container[0].lineno, 5)


    def test_read_containers_from_location(self):
        prj = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'testdata')))
        config = prj.create_configuration("test.confml", True)
        
        container = plugin.ImplContainerReader.read_impl_from_location('layer1/implml/test.implml', config, 4)
        self.assertEquals(container.invocation_phase(), 'normal')
        self.assertEquals(container.path, 'layer1/implml/test.implml')
        self.assertEquals(container.lineno, 4)
        self.assertEquals(container[0].invocation_phase(), 'normal')
        self.assertEquals(container[0].path, 'layer1/implml/test.implml')
        self.assertEquals(container[0].lineno, 5)

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
            <container xmlns="http://www.symbianfoundation.org/xml/implml/1">
              <mock xmlns="http://www.test.com/xml/1"/>
              <container>
                <mock xmlns="http://www.test.com/xml/1"/>
              </container>
              <container xmlns="http://www.symbianfoundation.org/xml/implml/1">
                <phase name="post"/>
                <mock xmlns="http://www.test.com/xml/1"/>
              </container>
            </container>
            """
        container = plugin.ImplContainerReader.read_implementation(xml_data)
        self.assertEquals(container[0].invocation_phase(), 'normal')
        self.assertEquals(container[1][0].invocation_phase(), 'normal')
        self.assertEquals(container[2][0].invocation_phase(), 'post')
    
    def test_containers_with_tags(self):
        xml_data = """<?xml version="1.0"?>
            <container xmlns="http://www.symbianfoundation.org/xml/implml/1">
              <tag name="target" value="rofs2"/>
              <tag name="foobar" value="test"/>
              
              <container>
                <mock xmlns="http://www.test.com/xml/1"/>
              </container>
              
              <container xmlns="http://www.symbianfoundation.org/xml/implml/1">
                <tag name="target" value="rofs3"/>
                <mock xmlns="http://www.test.com/xml/1"/>
              </container>
            </container>
            """
        container = plugin.ImplContainerReader.read_implementation(xml_data)
        self.assertEquals(container[0][0].get_tags(), {'target': ['rofs2'],
                                                       'foobar': ['test']})
        self.assertEquals(container[1][0].get_tags(), {'target': ['rofs3']})
    
    def test_read_container_impl_line_numbers(self):
        xml_data = """<?xml version="1.0"?>
            <container xmlns="http://www.symbianfoundation.org/xml/implml/1">
                <container>
                    <mock xmlns="http://www.test.com/xml/1"/>
                </container>
              
                <container>
                    <mock xmlns="http://www.test.com/xml/1"/>
                    <container>
                        <mock xmlns="http://www.test.com/xml/1"/>
                        <mock xmlns="http://www.test.com/xml/1"/>
                    </container>
                </container>
            </container>
        """
        container = plugin.ImplContainerReader.read_implementation(xml_data)
        self.assertEquals(container[0].lineno, 3)
        self.assertEquals(container[0][0].lineno, 4)
        self.assertEquals(container[1].lineno, 7)
        self.assertEquals(container[1][0].lineno, 8)
        self.assertEquals(container[1][1].lineno, 9)
        self.assertEquals(container[1][1][0].lineno, 10)
        self.assertEquals(container[1][1][1].lineno, 11)
    
    def test_container_common_element_inheritance(self):
        xml_data = """<?xml version="1.0"?>
            <container xmlns="http://www.symbianfoundation.org/xml/implml/1">
                
                <!-- [0] -->
                <mock xmlns="http://www.test.com/xml/1"/>
                
                <!-- [1] -->
                <container>
                    <tag name="target" value="rofs2"/>
                    <tag name="target" value="rofs3"/>
                    <tag name="foo" value="bar"/>
                    <phase name="post"/>
                    <settingRefsOverride>
                        <settingRef value="Foo.Bar"/>
                        <settingRef value="Foo.Baz"/>
                    </settingRefsOverride>
                    <outputRootDir value="/foo/root"/>
                    <outputSubDir value="foosubdir"/>
                    
                    <!-- [1][0] -->
                    <mock xmlns="http://www.test.com/xml/1"/>
                    
                    <!-- [1][1] -->
                    <container>
                        <!-- [1][1][0] -->
                        <mock xmlns="http://www.test.com/xml/1"/>
                        
                        <!-- [1][1][1] -->
                        <container>
                            <!-- [1][1][1][0] -->
                            <mock xmlns="http://www.test.com/xml/1"/>
                        </container>
                    </container>
                    
                    <!-- [1][2] -->
                    <container>
                        <tag name="target" value="core"/>
                        <tag name="foo" value="baz"/>
                        <phase name="pre"/>
                        <settingRefsOverride refsIrrelevant="true"/>
                        <outputRootDir value="/foo/root2"/>
                        <outputSubDir value="foosubdir2"/>
                        
                        <!-- [1][2][0] -->
                        <mock xmlns="http://www.test.com/xml/1"/>
                        
                        <!-- [1][2][1] -->
                        <container>
                            <!-- [1][2][1][0] -->
                            <mock xmlns="http://www.test.com/xml/1"/>
                        </container>
                    </container>
                </container>
            </container>
            """
        container = plugin.ImplContainerReader.read_implementation(xml_data)
        
        # First impl, with all defaults
        impl = container[0]
        self.assertEquals(impl.get_tags(), {})
        self.assertEquals(impl.invocation_phase(), 'normal')
        self.assertEquals(impl.get_refs(), None)
        self.assertEquals(impl.output, '')
        
        # The sub-container has things overridden, check that they
        # are all inherited correctly downwards in the implementation
        # tree
        def assert_is_expected(impl):
            self.assertEquals(impl.get_tags(), {'target': ['rofs2', 'rofs3'], 'foo': ['bar']})
            self.assertEquals(impl.invocation_phase(), 'post')
            self.assertEquals(impl.get_refs(), ['Foo.Bar', 'Foo.Baz'])
            self.assertEquals(impl.output, '/foo/root/foosubdir')
            self.assertEquals(impl.output_subdir, 'foosubdir')
        assert_is_expected(container[1][0])
        assert_is_expected(container[1][1][0])
        assert_is_expected(container[1][1][1][0])
        
        # The sub-container's second sub-container has things overridden
        # again, so check that those are correct
        def assert_is_expected_2(impl):
            self.assertEquals(impl.get_tags(), {'target': ['core'], 'foo': ['baz']})
            self.assertEquals(impl.invocation_phase(), 'pre')
            self.assertEquals(impl.get_refs(), None)
            self.assertEquals(impl.output, '/foo/root2/foosubdir2')
        assert_is_expected_2(container[1][2][0])
        assert_is_expected_2(container[1][2][1][0])

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
