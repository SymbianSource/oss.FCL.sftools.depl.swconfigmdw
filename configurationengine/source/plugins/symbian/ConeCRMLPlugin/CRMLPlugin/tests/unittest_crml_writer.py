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

import sys, os, unittest, logging
import __init__

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

from cone.public import exceptions, plugin, api, container

from CRMLPlugin.crml_model import *
from CRMLPlugin.crml_writer import CrmlTxtWriter

log = logging.getLogger('unittest_crml_writer')

FEATURES = {
#   Ref                    Type         Value (+ optionally orig. value) 
    'Foo.Int'           : ('int',       5,      '5'),
    'Foo.Real'          : ('real',      5.5,    '5.5'),
    'Foo.String'        : ('string',    'Test'),
    'Foo.UnicodeString' : ('string',    u'100\u20ac'),
    'Foo.Bit1'          : ('boolean',   True,   'true'),
    'Foo.Bit2'          : ('boolean',   False,  'false'),
    'Foo.Bit3'          : ('boolean',   True,   '1'),
    'Foo.Bit4'          : ('boolean',   False,  '0'),
    'Foo.Bit5'          : ('boolean',   True,   '1'),
    'Foo.Bit6'          : ('boolean',   False,  '0'),
    'Foo.Seq.Int'       : ('int',       ['1', '2', '3']),
    'Foo.Seq.Real'      : ('real',      ['0.1', '0.2', '0.3']),
    'Foo.Seq.String'    : ('string',    ['Test1', 'Test2', 'Test3']),
}

class Mock(object):
    pass

class MockFeature(object):
    def __init__(self, ref):
        self.ref = ref
    def get_value(self):
        return FEATURES[self.ref][1]
    def get_original_value(self):
        val = FEATURES[self.ref]
        if len(val) == 3:   return val[2]
        else:               return val[1]
    def get_type(self):
        return FEATURES[self.ref][0]

class MockConfiguration(object):
    def get_default_view(self):
        dview = Mock()
        dview.get_feature = lambda ref: MockFeature(ref)
        return dview

class TestCrmlTxtWriter(unittest.TestCase):
    def setUp(self):
        self.writer = CrmlTxtWriter(MockConfiguration(), log)
    
    def test_write_access(self):
        def check(acc, expected):
            actual = self.writer.get_access_line(acc)
            self.assertEquals(expected, actual)
        
        check(CrmlAccess(), '')
        check(CrmlAccess(cap_rd="AlwaysPass"), 'cap_rd=alwayspass')
        check(CrmlAccess(cap_wr="AlwaysPass"), 'cap_wr=alwayspass')
        check(CrmlAccess(cap_rd="ReadDeviceData", cap_wr="WriteDeviceData"),
              'cap_rd=ReadDeviceData cap_wr=WriteDeviceData')
        check(CrmlAccess(sid_rd="0x12345678", sid_wr="0x87654321"),
              'sid_rd=0x12345678 sid_wr=0x87654321')
        check(CrmlAccess(cap_rd="ReadDeviceData", cap_wr="WriteDeviceData", sid_rd="0x12345678", sid_wr="0x87654321"),
              'sid_rd=0x12345678 cap_rd=ReadDeviceData sid_wr=0x87654321 cap_wr=WriteDeviceData')
    
    def test_write_simple_key(self):
        def check(key, expected):
            key_line = self.writer.get_cenrep_entries(key)[0]
            actual = self.writer.get_cenrep_entry_line(key_line)
            self.assertEquals(expected, actual)
    
        check(CrmlSimpleKey(ref='Foo.Int', int='0x01020304'),
              '0x1020304 int 5 0')
        check(CrmlSimpleKey(ref='Foo.Int', int='0x01020304', backup=True),
              '0x1020304 int 5 16777216')
        check(CrmlSimpleKey(ref='Foo.Int', int='0x01020304', backup=True, access=CrmlAccess(cap_rd='AlwaysPass', cap_wr='AlwaysFail')),
              '0x1020304 int 5 16777216 cap_rd=alwayspass cap_wr=alwaysfail')


class TestKeyRange(unittest.TestCase):
    
    def test_get_shift_count_with_small_range(self):
        self.assertEquals(CrmlTxtWriter.get_range_shift(0xff00), 8)

    def test_get_shift_count_with_medium_range(self):
        self.assertEquals(CrmlTxtWriter.get_range_shift(0xff000), 12)

    def test_get_shift_count_with_larger_range(self):
        self.assertEquals(CrmlTxtWriter.get_range_shift(0xff0000), 16)

    def test_get_shift_count_with_split_range(self):
        self.assertEquals(CrmlTxtWriter.get_range_shift(0xfc00), 10)

    def test_get_range_with_larger_range(self):
        self.assertEquals(CrmlTxtWriter.get_range(0xff0000), 0xffff)
        self.assertEquals(CrmlTxtWriter.get_range(0xff000), 0xfff)
        self.assertEquals(CrmlTxtWriter.get_range(0xff00), 0xff)
        self.assertEquals(CrmlTxtWriter.get_range(0xfc0000), 0x3ffff)

    def test_get_index_with_whole_range_00(self):
        self.assertEquals(CrmlTxtWriter.get_index(0x0,2, 0xff0000,0,0), 0x20000)
        self.assertEquals(CrmlTxtWriter.get_index(0x0,2, 0xff0000,0,1), 0x20001)
        self.assertEquals(CrmlTxtWriter.get_index(0x0,2, 0xff0000,0,2), 0x20002)
        self.assertEquals(CrmlTxtWriter.get_index(0x0,2, 0xff0000,0,3), 0x20003)
        self.assertEquals(CrmlTxtWriter.get_index(0x0,2, 0xff0000,0,4), 0x20004)
        self.assertEquals(CrmlTxtWriter.get_index(0x0,2, 0xff0000,0,5), 0x20005)

    def test_get_index_with_whole_range_10(self):
        self.assertEquals(CrmlTxtWriter.get_index(0x0,2, 0xff0000,1,0), 0x30000)
        self.assertEquals(CrmlTxtWriter.get_index(0x0,2, 0xff0000,1,1), 0x30001)
        self.assertEquals(CrmlTxtWriter.get_index(0x0,2, 0xff0000,1,2), 0x30002)
        self.assertEquals(CrmlTxtWriter.get_index(0x0,2, 0xff0000,1,3), 0x30003)
        self.assertEquals(CrmlTxtWriter.get_index(0x0,2, 0xff0000,1,4), 0x30004)
        self.assertEquals(CrmlTxtWriter.get_index(0x0,2, 0xff0000,1,5), 0x30005)

    def test_get_index_with_whole_range_f(self):
        self.assertEquals(CrmlTxtWriter.get_index(0x0,2, 0xff0000,16,0), 0x120000)
        self.assertEquals(CrmlTxtWriter.get_index(0x0,2, 0xff0000,16,1), 0x120001)
        self.assertEquals(CrmlTxtWriter.get_index(0x0,2, 0xff0000,16,2), 0x120002)
        self.assertEquals(CrmlTxtWriter.get_index(0x0,2, 0xff0000,16,3), 0x120003)
        self.assertEquals(CrmlTxtWriter.get_index(0x0,2, 0xff0000,16,4), 0x120004)
        
    def test_get_seqid_with_whole_range_00(self):
        self.assertEquals(CrmlTxtWriter.get_seqid(0x0,2, 0xff0000,0x20000), 0)
        self.assertEquals(CrmlTxtWriter.get_seqid(0x0,2, 0xff0000,0x20004), 0)
        self.assertEquals(CrmlTxtWriter.get_seqid(0x0,2, 0xff0000,0x30001), 1)
        self.assertEquals(CrmlTxtWriter.get_seqid(0x0,2, 0xff0000,0x120000), 16)

    def test_get_subseqid(self):
        self.assertEquals(CrmlTxtWriter.get_subseqid(0x0,0, 0xff0000,0x4), 4)
        self.assertEquals(CrmlTxtWriter.get_subseqid(0x0,2, 0xff0000,0x120004), 4)
        self.assertEquals(CrmlTxtWriter.get_subseqid(0x0,2, 0xff0000,0x120012), 18)
        self.assertEquals(CrmlTxtWriter.get_subseqid(0xcf000002,2, 0xff0000,0xcf000002), 0)
        self.assertEquals(CrmlTxtWriter.get_subseqid(0xcf000002,2, 0xff0000,0xcf000006), 4)
        self.assertEquals(CrmlTxtWriter.get_subseqid(0xcf000002,2, 0xff0000,0xcf00000f), 13)
        self.assertEquals(CrmlTxtWriter.get_subseqid(0xcf000002,2, 0xff0000,0xcf020002), 0)

    def test_get_index_with_example_range_f(self):
        self.assertEquals(CrmlTxtWriter.get_index(0xcf000002,2, 0xff0000,0,0), 0xcf020002)
        self.assertEquals(CrmlTxtWriter.get_index(0xcf000002,2, 0xff0000,0,1), 0xcf020003)
        self.assertEquals(CrmlTxtWriter.get_index(0xcf000002,2, 0xff0000,0,2), 0xcf020004)
        self.assertEquals(CrmlTxtWriter.get_index(0xcf000002,2, 0xff0000,0,3), 0xcf020005)
        self.assertEquals(CrmlTxtWriter.get_index(0xcf000002,2, 0xff0000,0,4), 0xcf020006)
        self.assertEquals(CrmlTxtWriter.get_index(0xcf000002,2, 0xff0000,0,5), 0xcf020007)
        self.assertEquals(CrmlTxtWriter.get_index(0xcf000002,2, 0xff0000,1,0), 0xcf030002)
        self.assertEquals(CrmlTxtWriter.get_index(0xcf000002,2, 0xff0000,1,3), 0xcf030005)
        self.assertEquals(CrmlTxtWriter.get_index(0xcf000002,2, 0xff0000,1,5), 0xcf030007)
        self.assertEquals(CrmlTxtWriter.get_index(0xcf000002,2, 0xff0000,16,0), 0xcf120002)
        self.assertEquals(CrmlTxtWriter.get_index(0xcf000002,2, 0xff0000,16,3), 0xcf120005)
        self.assertEquals(CrmlTxtWriter.get_index(0xcf000002,2, 0xff0000,16,5), 0xcf120007)
        