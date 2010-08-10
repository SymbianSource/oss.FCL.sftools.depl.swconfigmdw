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

from hcrplugin.hcr_exceptions import *
from hcrplugin.hcrml_parser import HcrmlReader

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




ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

NAMESPACE = 'http://www.symbianfoundation.org/xml/hcrml/1'


class DummyConfiguration(object):
    RESOURCES = {
        'layer1/dummy.hcrml'    : '<hcr xmlns="%s"><category name="Cat0" uid="0"/></hcr>' % NAMESPACE,
        'layer1/dummy1.hcrml'   : '<hcr xmlns="%s"><category name="Cat1" uid="1"/></hcr>' % NAMESPACE,
        'layer2/dummy2.hcrml'   : '<hcr xmlns="%s"><category name="Cat2" uid="2"/></hcr>' % NAMESPACE,
        'layer2/dummy3.hcrml'   : '<hcr xmlns="%s"><category name="Cat3" uid="3"/></hcr>' % NAMESPACE,
        'layer3/dummy.gcfml'    : '',
        'layer3/dummy.crml'     : '',
        'layer4/dummy.ruleml'   : '',
        'layer4/hcr_dat.hcrml'  : '<hcr xmlns="%s"><output file="some/test/hcr.dat" type="hcr"><include ref="*.hcrml"/></output></hcr>' % NAMESPACE,
    }
    
    def list_resources(self):
        return sorted(self.RESOURCES.keys())
    
    def get_resource(self, res_ref):
        class DummyResource(object):
            def __init__(self, data):   self.data = data
            def read(self):             return self.data
            def close(self):            pass
        return DummyResource(self.RESOURCES[res_ref])


class TestHCRHeader(unittest.TestCase):

    def setUp(self):
        self.reader = HcrmlReader(None, None)

    def test_read_hcrml_output(self):
        xml = '<hcr xmlns="%s"><output file="some/test/file.h" type="header"/></hcr>' % NAMESPACE
        self.reader.doc = ElementTree.fromstring(xml)
        output = self.reader.read_hcrml_output()
        self.assertEquals(output.type, 'header')
        self.assertEquals(output.file, 'some/test/file.h')
        self.assertEquals(output.version, None)
        self.assertEquals(output.read_only, None)
        self.assertEquals(output.categories, [])
    
    def _run_test_read_invalid_hcrml_output(self, xml, expected_exception):
        try:
            self.reader.doc = ElementTree.fromstring(xml)
            self.reader.read_hcrml_output()
            self.fail("Expected exception not raised!")
        except expected_exception:
            pass
    
    def test_read_invalid_hcrml_output(self):
        xml = '<hcr xmlns="%s"><output file="some/test/file.h"/></hcr>' % NAMESPACE
        self._run_test_read_invalid_hcrml_output(xml, NoTypeDefinedInOutPutTagError)
        
        xml = '<hcr xmlns="%s"><output file="some/test/file.h" type="foobar"/></hcr>' % NAMESPACE
        self._run_test_read_invalid_hcrml_output(xml, InvalidTypeDefinedInOutPutTagError)
        
    
    def test_read_hcrml_output_with_include(self):
        config = DummyConfiguration()
        resource_ref =  'layer4/hcr_dat.hcrml'
        
        self.reader = HcrmlReader(resource_ref, config)
        self.reader.doc = ElementTree.fromstring(config.get_resource(resource_ref).read())
        output = self.reader.read_hcrml_output()
        self.assertEquals(output.type, 'hcr')
        self.assertEquals(output.file, 'some/test/hcr.dat')
        self.assertEquals(
            sorted([cat.category_uid for cat in output.categories]),
            sorted([0, 1, 2, 3]))

    
    def test_read_hcrml_output_with_overlapping_includes(self):
        config = DummyConfiguration()
        resource_ref =  'layer4/hcr_dat.hcrml'
        
        XML = """<hcr xmlns="%s">
            <output file="hcr.dat" type="hcr">
                <include ref="dummy.hcrml"/>
                <include ref="dummy2.hcrml"/>
                <include ref="layer1/*.hcrml"/>
            </output>
        </hcr>
        """% NAMESPACE
        
        self.reader = HcrmlReader(resource_ref, config)
        self.reader.doc = ElementTree.fromstring(XML)
        output = self.reader.read_hcrml_output()
        self.assertEquals(output.type, 'hcr')
        self.assertEquals(output.file, 'hcr.dat')
        self.assertEquals(
            sorted([cat.category_uid for cat in output.categories]),
            sorted([0, 1, 2]))

    def test_read_hcrml_category(self):
        xml = '<category name="KCatGPIO" uid="0x10001234"/>'
        etree = ElementTree.fromstring(xml)
        category = self.reader.read_hrcml_category(etree)
        self.assertEquals(category.name, 'KCatGPIO')
        self.assertEquals(category.category_uid, 0x10001234)
    
    def _run_test_read_invalid_hcrml_category(self, xml, expected_exception):
        try:
            etree = ElementTree.fromstring(xml)
            setting = self.reader.read_hrcml_category(etree)
            self.fail("Expected exception not raised!")
        except expected_exception:
            pass
    
    def test_read_invalid_hcrml_category(self):
        xml = '<category name="KCatGPIO"/>'
        self._run_test_read_invalid_hcrml_category(xml, NoCategoryUIDInHcrmlFileError)
        xml = '<category uid="0x10001234"/>'
        self._run_test_read_invalid_hcrml_category(xml, NoCategoryNameInHcrmlFileError)

    def test_read_hcrml_setting(self):
        xml = '<setting ref="hcrexample.DebounceInterval" name="KElmGPIO_DebounceInterval" type="int32" id="0"/>'
        etree = ElementTree.fromstring(xml)
        setting = self.reader.read_hcrml_setting(etree)
        self.assertEquals(setting.ref, 'hcrexample.DebounceInterval')
        self.assertEquals(setting.name, 'KElmGPIO_DebounceInterval')
        self.assertEquals(setting.type, 'int32')
        self.assertEquals(setting.id, 0)
    
    def _run_test_read_invalid_hcrml_setting(self, xml, expected_exception):
        try:
            etree = ElementTree.fromstring(xml)
            setting = self.reader.read_hcrml_setting(etree)
            self.fail("Expected exception not raised!")
        except expected_exception:
            pass
    
    def test_read_invalid_hcrml_setting(self):
        xml = '<setting name="xyz" type="int32" id="0"/>'
        self._run_test_read_invalid_hcrml_setting(xml, NoRefInHcrmlFileError)
        
        xml = '<setting ref="x.y" name="xyz" id="0"/>'
        self._run_test_read_invalid_hcrml_setting(xml, NoTypeAttributeInSettingHcrmlFileError)
        
        xml = '<setting ref="x.y" type="int32" id="0"/>'
        self._run_test_read_invalid_hcrml_setting(xml, NoNameAttributeInSettingHcrmlFileError)
        
        xml = '<setting ref="x.y" name="xyz" type="int32"/>'
        self._run_test_read_invalid_hcrml_setting(xml, NoIdAttributeInSettingHcrmlFileError)

        

    def test_read_hcrml_flag(self):
        xml = '<flags Uninitialised="0" Modifiable="0" Persistent="0"/>'
        etree = ElementTree.fromstring(xml)
        flag = self.reader.read_hrcml_flags(etree)
        self.assertEquals(flag.Uninitialised, '0')
        self.assertEquals(flag.Modifiable, '0')
        self.assertEquals(flag.Persistent, '0')
        
    def test_filter_file_list_by_include_ref(self):
        lst = [
            'layer1/dummy.hcrml',
            'dummy.hcrml',
            'layer1/dummy1.hcrml',
            'layer2/dummy2.hcrml',
            'layer2/dummy3.hcrml',
            'layer3/test_dummy.hcrml',
            'layer3/dummy.gcfml',
            'layer3/dummy.crml',
            'layer4/hcr_dat.hcrml',
        ]
        
        filt = self.reader.filter_file_list_by_include_ref
        
        self.assertEquals(sorted(filt(lst, '*.hcrml')), sorted([
            'dummy.hcrml',
            'layer1/dummy.hcrml',
            'layer1/dummy1.hcrml',
            'layer2/dummy2.hcrml',
            'layer2/dummy3.hcrml',
            'layer3/test_dummy.hcrml',
            'layer4/hcr_dat.hcrml',]))
        
        self.assertEquals(sorted(filt(lst, 'dummy.hcrml')), sorted([
            'dummy.hcrml',
            'layer1/dummy.hcrml',]))
        
        self.assertEquals(sorted(filt(lst, 'dummy*.hcrml')), sorted([
            'dummy.hcrml',
            'layer1/dummy.hcrml',
            'layer1/dummy1.hcrml',
            'layer2/dummy2.hcrml',
            'layer2/dummy3.hcrml',]))
        
        self.assertEquals(sorted(filt(lst, 'layer1/*')), sorted([
            'layer1/dummy.hcrml',
            'layer1/dummy1.hcrml',]))
        
        self.assertEquals(sorted(filt(lst, 'layer4/*')), sorted([
            'layer4/hcr_dat.hcrml']))
        
        self.assertEquals(sorted(filt(lst, 'hcr_dat.hcrml')), sorted([
            'layer4/hcr_dat.hcrml']))
