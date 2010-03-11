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
import __init__
from cone.public import plugin
from CRMLPlugin.crml_model import *
from CRMLPlugin.crml_comparator import CrmlComparator
from cone.public.plugin import FlatComparisonResultEntry as Entry

class TestComparator(unittest.TestCase):
    def setUp(self):
        keys = [
            CrmlSimpleKey(ref='Foo.Bar', int='0x1'),
            CrmlBitmaskKey(int='0x2', bits=[CrmlBit(ref='Foo.Bit1', index=1),
                                            CrmlBit(ref='Foo.Bit2', index=2),
                                            CrmlBit(ref='Foo.Bit4', index=4, invert=True)]),
            CrmlKeyRange(first_int='0x10000000', last_int='0x1FFFFFFF', ref="Foo.Seq",
                         subkeys=[CrmlKeyRangeSubKey(ref='Sub1', name='Sub-key 1', type='int', int='0x1'),
                                  CrmlKeyRangeSubKey(ref='Sub2', name='Sub-key 2', type='real', int='0x2')]),
        ]
    
        self.repo = CrmlRepository(
            uid_value   = '0x10203040',
            uid_name    = 'KCrUidTest',
            owner       = '0x11223344',
            backup      = True,
            rfs         = True,
            access      = CrmlAccess(),
            keys        = keys)
        
        self.comparator = CrmlComparator('test.crml', self.repo)
    
    
    def assert_comparison_result_after_change_equals(self,
        modification_code, added=[], removed=[], modified=[],
        check_keys_in_entry_data=True,
        target_resource_ref='test.crml'):
        # Make a copy of the test repo and modify it using the given code
        repo = self.repo.copy()
        exec(modification_code)
        
        expected_result = plugin.FlatComparisonResult(only_in_source = removed,
                                                      only_in_target = added,
                                                      modified       = modified)
        
        comparator = CrmlComparator('test.crml', self.repo)
        actual_result = comparator.flat_compare(target_resource_ref, repo)
        self.assertEquals(expected_result, actual_result)
        
        # Assert that all comparison result entries have references to the
        # repository objects 
        for entry in actual_result.only_in_source:
            self.assertTrue(isinstance(entry.data['repo'], CrmlRepository))
        for entry in actual_result.only_in_target:
            self.assertTrue(isinstance(entry.data['repo'], CrmlRepository))
        for entry in actual_result.modified:
            self.assertTrue(isinstance(entry.data['source_repo'], CrmlRepository))
            self.assertTrue(isinstance(entry.data['target_repo'], CrmlRepository))
        
        # Check also references to CRML key objects if specified
        if check_keys_in_entry_data:
            for entry in actual_result.only_in_source:
                self.assertTrue(isinstance(entry.data['key'], CrmlKeyBase))
            for entry in actual_result.only_in_target:
                self.assertTrue(isinstance(entry.data['key'], CrmlKeyBase))
            for entry in actual_result.modified:
                self.assertTrue(isinstance(entry.data['source_key'], CrmlKeyBase))
                self.assertTrue(isinstance(entry.data['target_key'], CrmlKeyBase))
    
    def test_simple_key_changed(self):
        def check(attrname, value_id, old_value, new_value):
            self.assert_comparison_result_after_change_equals(
                'repo.keys[0].%s = %r' % (attrname, new_value),
                modified=[Entry(sub_id       = '0x00000001',
                                value_id     = value_id,
                                source_value = old_value,
                                target_value = new_value)])
        
        check('ref',            'ref',          'Foo.Bar',  'Foo.Baz')
        check('name',           'name',         None,       'Foobar')
        check('backup',         'backup',       False,      True)
        check('read_only',      'read_only',    False,      True)
        check('access.cap_rd',  'cap_rd',       None,       'FooCapability')
        check('access.cap_wr',  'cap_wr',       None,       'FooCapability')
        check('access.sid_rd',  'sid_rd',       None,       '0x12345678')
        check('access.sid_wr',  'sid_wr',       None,       '0x12345678')
        
        
        self.assert_comparison_result_after_change_equals(
            'repo.keys[0].int = "0x5"',
            added   = [Entry(sub_id='0x00000005')],
            removed = [Entry(sub_id='0x00000001')])
    
    def test_bitmask_key_changed(self):
        def check(attrname, value_id, old_value, new_value):
            self.assert_comparison_result_after_change_equals(
                'repo.keys[1].%s = %r' % (attrname, new_value),
                modified=[Entry(sub_id       = '0x00000002',
                                value_id     = value_id,
                                source_value = old_value,
                                target_value = new_value)])
        
        check('name',           'name',         None,       'Foobar')
        check('backup',         'backup',       False,      True)
        check('read_only',      'read_only',    False,      True)
        check('access.cap_rd',  'cap_rd',       None,       'FooCapability')
        check('access.cap_wr',  'cap_wr',       None,       'FooCapability')
        check('access.sid_rd',  'sid_rd',       None,       '0x12345678')
        check('access.sid_wr',  'sid_wr',       None,       '0x12345678')
    
        self.assert_comparison_result_after_change_equals(
            'repo.keys[1].int = "0x5"',
            added   = [Entry(sub_id='0x00000005')],
            removed = [Entry(sub_id='0x00000002')])
    
    def test_bitmask_key_bit_changed(self):    
        def check(attrname, value_id, old_value, new_value):
            self.assert_comparison_result_after_change_equals(
                'repo.keys[1].bits[0].%s = %r' % (attrname, new_value),
                modified = [Entry(sub_id       = '0x00000002 (bit 1)',
                                  value_id     = value_id,
                                  source_value = old_value,
                                  target_value = new_value)])
        
        check('ref',    'ref',      'Foo.Bit1', 'Foo.Bar.Bit')
        check('invert', 'invert',   False,      True)
        
        self.assert_comparison_result_after_change_equals(
            'repo.keys[1].bits[0].index = 6',
            added   = [Entry(sub_id='0x00000002 (bit 6)')],
            removed = [Entry(sub_id='0x00000002 (bit 1)')])
        
    
    def test_key_range_changed(self):
        def check(attrname, value_id, old_value, new_value):
            self.assert_comparison_result_after_change_equals(
                'repo.keys[2].%s = %r' % (attrname, new_value),
                modified=[Entry(sub_id       = '0x10000000-0x1FFFFFFF',
                                value_id     = value_id,
                                source_value = old_value,
                                target_value = new_value)])
        
        check('ref',            'ref',          'Foo.Seq',  'Foo.Bar')
        check('name',           'name',         None,       'Foobar')
        check('backup',         'backup',       False,      True)
        check('read_only',      'read_only',    False,      True)
        check('access.cap_rd',  'cap_rd',       None,       'FooCapability')
        check('access.cap_wr',  'cap_wr',       None,       'FooCapability')
        check('access.sid_rd',  'sid_rd',       None,       '0x12345678')
        check('access.sid_wr',  'sid_wr',       None,       '0x12345678')
        
        def check(attrname, new_value, old_id, new_id):
            self.assert_comparison_result_after_change_equals(
                'repo.keys[2].%s = %r' % (attrname, new_value),
            added   = [Entry(sub_id=new_id)],
            removed = [Entry(sub_id=old_id)])
        
        check('first_int',  '0x00000000',   '0x10000000-0x1FFFFFFF', '0x00000000-0x1FFFFFFF')
        check('last_int',   '0x20000000',   '0x10000000-0x1FFFFFFF', '0x10000000-0x20000000')
    
    def test_key_range_subkey_changed(self):
        def check(attrname, old_value, new_value):
            self.assert_comparison_result_after_change_equals(
                'repo.keys[2].subkeys[0].%s = %r' % (attrname, new_value),
                modified = [Entry(sub_id       = '0x10000000-0x1FFFFFFF (sub-key 0x00000001)',
                                  value_id     = attrname,
                                  source_value = old_value,
                                  target_value = new_value)])
        
        check('ref', 'Sub1', 'FooSub')
        check('name', 'Sub-key 1', 'Foo')
        check('type', 'int', 'real')
        
        self.assert_comparison_result_after_change_equals(
            'repo.keys[2].subkeys[0].int = "0xA"',
            added   = [Entry(sub_id='0x10000000-0x1FFFFFFF (sub-key 0x0000000A)')],
            removed = [Entry(sub_id='0x10000000-0x1FFFFFFF (sub-key 0x00000001)')])
    
    def test_key_type_changed(self):
        # Change a bitmask key into a simple key
        self.assert_comparison_result_after_change_equals(
            "repo.keys[1] = CrmlSimpleKey(ref='Foo.Bar', name='Foo', int='0x2')",
            modified = [Entry(sub_id       = '0x00000002',
                              value_id     = 'key_type',
                              source_value = 'bitmask_key',
                              target_value = 'simple_key'),
                        Entry(sub_id       = '0x00000002',
                              value_id     = 'name',
                              source_value = None,
                              target_value = 'Foo')])
        
        # Change a simple key into a bitmask key
        self.assert_comparison_result_after_change_equals(
            "repo.keys[0] = CrmlBitmaskKey(int='0x1', name='Foo', bits=[CrmlBit(ref='Foo.Bit1', index=1)])",
            modified = [Entry(sub_id       = '0x00000001',
                              value_id     = 'key_type',
                              source_value = 'simple_key',
                              target_value = 'bitmask_key'),
                        Entry(sub_id       = '0x00000001',
                              value_id     = 'name',
                              source_value = None,
                              target_value = 'Foo')])
    
    def test_repository_attrs_changed(self):
        def check(attrname, value_id, old_value, new_value):
            self.assert_comparison_result_after_change_equals(
                'repo.%s = %r' % (attrname, new_value),
                modified=[Entry(sub_id       = None,
                                value_id     = value_id,
                                source_value = old_value,
                                target_value = new_value)],
                check_keys_in_entry_data=False)
        
        check('uid_name',       'uid_name',     'KCrUidTest',   'Foobar')
        check('owner',          'owner',        '0x11223344',   '0xAABBCCDD')
        check('backup',         'backup',       True,           False)
        check('rfs',            'rfs',          True,           False)
        check('access.cap_rd',  'cap_rd',       None,           'FooCapability')
        check('access.cap_wr',  'cap_wr',       None,           'FooCapability')
        check('access.sid_rd',  'sid_rd',       None,           '0x12345678')
        check('access.sid_wr',  'sid_wr',       None,           '0x12345678')
    
    def test_repository_file_changed(self):
        self.assert_comparison_result_after_change_equals(
            '', # Make no modifications in the repository
            modified=[Entry(sub_id       = None,
                            value_id     = 'file',
                            source_value = 'test.crml',
                            target_value = 'xyz.crml')],
            target_resource_ref = 'xyz.crml',
            check_keys_in_entry_data = False)

if __name__ == '__main__':
    unittest.main()