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

import os, unittest

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

from cone.public import exceptions, plugin, api, container, utils

from CRMLPlugin.crml_model import *
from CRMLPlugin.crml_reader import CrmlReader

class TestCrmlReader(unittest.TestCase):
    
    NAMESPACE = CrmlReader.NAMESPACE
    
    def setUp(self):
        self.reader = CrmlReader()
    
    def assert_read_access_equals(self, data, expected):
        etree = utils.etree.fromstring(data)
        access = self.reader.read_access(etree)
        self.assertEquals(expected, access)
    
    def test_read_access(self):
        data = """<?xml version="1.0"?><test/>"""
        self.assert_read_access_equals(data, CrmlAccess())
        
        data = """<?xml version="1.0"?>
                <test xmlns='%s'>
                    <access type='R' capabilities="AlwaysPass" sid="0x12345678"/>
                    <access type='W' capabilities="WriteDeviceData" sid="0x87654321"/>
                </test>
                """ % self.NAMESPACE
        self.assert_read_access_equals(data,
            CrmlAccess(cap_rd='AlwaysPass', cap_wr='WriteDeviceData', sid_rd='0x12345678', sid_wr='0x87654321'))

    def test_get_refs(self):
        data = """<?xml version="1.0"?>
                <repository xmlns='%s'>
                    <access type='R' capabilities="AlwaysPass" sid="0x12345678"/>
                    <access type='W' capabilities="WriteDeviceData" sid="0x87654321"/>
                    <key ref="Feature1/IntSetting" name="Int setting" int="0x00000001" type="int" readOnly="false" backup="true">
                        <access type="R" capabilities="AlwaysPass"/>
                    </key>
                </repository>
                """ % self.NAMESPACE
        etree = utils.etree.fromstring(data)
        repo = self.reader.read_repository(etree)
        self.assertEquals(repo.get_refs(), ['Feature1.IntSetting'])
        
        data = """<?xml version="1.0"?>
                <repository xmlns='%s'>
                    <access type='R' capabilities="AlwaysPass" sid="0x12345678"/>
                    <access type='W' capabilities="WriteDeviceData" sid="0x87654321"/>
                </repository>
                """ % self.NAMESPACE
        etree = utils.etree.fromstring(data)
        repo = self.reader.read_repository(etree)
        self.assertEquals(repo.get_refs(), [])
        

        
    def test_read_duplicate_access(self):
        data = """<?xml version="1.0"?>
                <test xmlns='%s'>
                    <access type='R' capabilities="ReadDeviceData" sid="0x12345678"/>
                    <access type='W' capabilities="WriteDeviceData" sid="0x87654321"/>
                    <access type='R' capabilities="TCB" sid="0x11223344"/>
                    <access type='W' capabilities="DRM" sid="0x44332211"/>
                </test>
                """ % self.NAMESPACE
        self.assert_read_access_equals(data,
            CrmlAccess(cap_rd='ReadDeviceData', cap_wr='WriteDeviceData', sid_rd='0x12345678', sid_wr='0x87654321'))
    
    
    def read_key_from_xml(self, data):
        etree = utils.etree.fromstring(data)
        return self.reader.read_key(etree)
        
    def assert_read_key_equals(self, data, expected):
        self.assertEquals(expected, self.read_key_from_xml(data))
    
    def test_read_key(self):
        data = """<?xml version="1.0"?>
                <key xmlns='%s' ref="Foo/Bar" name="Foobar setting" int="0x01020304" type="real" readOnly="true" backup="true">
                    <access type='R' capabilities="AlwaysPass" sid="0x12345678"/>
                    <access type='W' capabilities="WriteDeviceData" sid="0x87654321"/>
                </key>""" % self.NAMESPACE
        self.assert_read_key_equals(data,
            CrmlSimpleKey(ref='Foo.Bar', name='Foobar setting', int='0x01020304', type='real', read_only=True, backup=True,
                          access=CrmlAccess(cap_rd='AlwaysPass', cap_wr='WriteDeviceData', sid_rd='0x12345678', sid_wr='0x87654321')))
        
    def test_read_invalid_key(self):
        # Required attribute 'ref' missing
        data = '<key xmlns="%s" name="Foobar setting" int="0x01020304" type="real"/>' % self.NAMESPACE
        self.assertRaises(exceptions.ParseError, self.read_key_from_xml, data)
    
    def assert_read_bitmask_key_equals(self, data, expected):
        etree = utils.etree.fromstring(data)
        key = self.reader.read_bitmask_key(etree)
        self.assertEquals(expected, key)
    
    def test_read_bitmask_key(self):
        data = """
        <key xmlns='%s' name="Bitmask" type="binary" int="0x00000001" readOnly="true" backup="true">
            <access type="R" capabilities="ReadDeviceData"/>
            <bit ref="BitmaskTest/Bit0">1</bit>
            <bit ref="BitmaskTest/Bit3">4</bit>
            <bit ref="BitmaskTest/Bit5" value='false'>6</bit>
        </key>
        """ % self.NAMESPACE
        
        self.assert_read_bitmask_key_equals(data,
            CrmlBitmaskKey(name      = 'Bitmask',
                           type      = 'binary',
                           int       = '0x00000001',
                           read_only = True,
                           backup    = True,
                           access    = CrmlAccess(cap_rd='ReadDeviceData'),
                           bits      = [CrmlBit(ref='BitmaskTest.Bit0', index=1),
                                        CrmlBit(ref='BitmaskTest.Bit3', index=4),
                                        CrmlBit(ref='BitmaskTest.Bit5', index=6, invert=True)]))
    
    def assert_read_key_range_equals(self, data, expected):
        etree = utils.etree.fromstring(data)
        key = self.reader.read_key_range(etree)
        self.assertEquals(expected, key)
    
    def test_read_key_range(self):
        data = """
            <keyRange xmlns='%s' firstInt="0x00004000" lastInt="0x00004FFF" readOnly="true" backup="false">
                <access type="R" capabilities="TCB"/>
            </keyRange>
            """ % self.NAMESPACE
        self.assert_read_key_range_equals(data,
            CrmlKeyRange(first_int='0x00004000', last_int='0x00004FFF', read_only=True, backup=False,
                         access=CrmlAccess(cap_rd='TCB')))
        
        data = """
            <keyRange xmlns='%s' ref="KeyRangeTest/SequenceSetting" backup="true" name="Sequence setting"
                firstInt="0x1001" lastInt="0x1fff" indexBits="0x0ff0" firstIndex="1" countInt="0x1000">
                <access type="R" capabilities="AlwaysPass"/>
                <access type="W" capabilities="WriteDeviceData"/>
                <key ref="StringSubSetting" name="String" int="0x0001" type="string8"/>
                <key ref="IntSubSetting" name="Int" int="0x0002" type="int"/>
                <key ref="IntSubSetting2" name="Int2" int="0x0003"/>
            </keyRange>
            """ % self.NAMESPACE
        self.assert_read_key_range_equals(data,
            CrmlKeyRange(first_int='0x1001', last_int='0x1fff', index_bits=0x0ff0,
                         count_int='0x1000', first_index=1,
                         ref='KeyRangeTest.SequenceSetting',
                         name='Sequence setting', backup=True, read_only=False,
                         access=CrmlAccess(cap_rd='AlwaysPass', cap_wr='WriteDeviceData'),
                         subkeys=[CrmlKeyRangeSubKey(ref='StringSubSetting', name='String', int='0x0001', type='string8'),
                                  CrmlKeyRangeSubKey(ref='IntSubSetting', name='Int', int='0x0002', type='int'),
                                  CrmlKeyRangeSubKey(ref='IntSubSetting2', name='Int2', int='0x0003', type='int')]))
    
    def assert_read_repo_equals(self, data, expected):
        etree = utils.etree.fromstring(data)
        key = self.reader.read_repository(etree)
        self.assertEquals(expected, key)
    
    def test_read_empty_repository(self):
        data = """<?xml version="1.0"?>
            <repository xmlns="%s" uidName="EmptyRepo" uidValue="0x000000E1"
                owner="0xABCDDCBA" backup="true" rfs="true" initialisationFileVersion="2">
            </repository>
            """ % self.NAMESPACE
        self.assert_read_repo_equals(data,
            CrmlRepository(uid_name  = 'EmptyRepo',
                           uid_value = '0x000000E1',
                           owner     = '0xABCDDCBA',
                           backup    = True,
                           rfs       = True,
                           version   = '2'))
    
    def test_read_simple_repository(self):
        data = """<?xml version="1.0"?>
            <repository xmlns="%s" uidName="SimpleRepo" uidValue="0x000000E2"
                owner="0xF00DBEEF" backup="true" rfs="true">
                <key ref="Foo/Key1" name="Fookey 1" int="0x00000001" type="int" readOnly="true" backup="true"/>
                <key ref="Foo/Key2" name="Fookey 2" int="0x00000002" type="real" readOnly="false" backup="true"/>
                <key ref="Foo/Key3" name="Fookey 3" int="0x00000003" type="string" readOnly="true" backup="false"/>
            </repository>
            """ % self.NAMESPACE
        self.assert_read_repo_equals(data,
            CrmlRepository(
                uid_name  = 'SimpleRepo',
                uid_value = '0x000000E2',
                owner     = '0xF00DBEEF',
                backup    = True,
                rfs       = True,
                version   = '1',
                keys      = [CrmlSimpleKey(ref='Foo.Key1', name='Fookey 1', int='0x00000001', type='int', read_only=True, backup=True, access=CrmlAccess(cap_wr='AlwaysFail')),
                             CrmlSimpleKey(ref='Foo.Key2', name='Fookey 2', int='0x00000002', type='real', read_only=False, backup=True),
                             CrmlSimpleKey(ref='Foo.Key3', name='Fookey 3', int='0x00000003', type='string', read_only=True, backup=False, access=CrmlAccess(cap_wr='AlwaysFail')),]))


if __name__ == "__main__":
    unittest.main()