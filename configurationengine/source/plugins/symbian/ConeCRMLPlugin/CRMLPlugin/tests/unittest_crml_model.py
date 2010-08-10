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

from cone.public import api, exceptions
from CRMLPlugin.crml_model import *

class TestCrmlAccess(unittest.TestCase):
    def test_create_access_object(self):
        acc = CrmlAccess()
        self.assertEquals(acc.cap_rd, None)
        self.assertEquals(acc.cap_wr, None)
        self.assertEquals(acc.sid_rd, None)
        self.assertEquals(acc.sid_wr, None)
        
        acc = CrmlAccess(cap_rd='AlwaysPass', cap_wr='WriteUserData', sid_rd='0x12345678', sid_wr='0x87654321')
        self.assertEquals(acc.cap_rd, 'AlwaysPass')
        self.assertEquals(acc.cap_wr, 'WriteUserData')
        self.assertEquals(acc.sid_rd, '0x12345678')
        self.assertEquals(acc.sid_wr, '0x87654321')
    
    def test_clone_access_object(self):
        acc1 = CrmlAccess(cap_rd='AlwaysPass', cap_wr='WriteUserData', sid_rd='0x12345678', sid_wr='0x87654321')
        acc2 = acc1.copy()
        self.assertFalse(acc1 is acc2)
        self.assertTrue(acc1 == acc2)
        self.assertFalse(acc1 != acc2)
    
    def test_compare_access_objects(self):
        acc1 = CrmlAccess(cap_rd='AlwaysPass', cap_wr='WriteUserData', sid_rd='0x12345678', sid_wr='0x87654321')
        acc2 = acc1.copy()
        self.assertTrue(acc1 == acc2)
        self.assertFalse(acc1 != acc2)
        
        def check(attrname, value):
            acc2 = acc1.copy()
            setattr(acc1, attrname, value)
            self.assertFalse(acc1 == acc2)
            self.assertTrue(acc1 != acc2)
        
        # Check that changing each individual attribute makes the comparison fail
        check('cap_rd', 'ReadDeviceData')
        check('cap_wr', 'WriteDeviceData')
        check('sid_rd', '0x11223344')
        check('sid_wr', '0x44332211')

        subkeys = [
            CrmlKeyRangeSubKey(ref='Sub1', name='Sub-key 1', type='int', int='0x1'),
            CrmlKeyRangeSubKey(ref='Sub2', name='Sub-key 2', type='real', int='0x2'),
            CrmlKeyRangeSubKey(ref='Sub3', name='Sub-key 3', type='string', int='0x3'),
        ]
        self.keyrange = CrmlKeyRange(
            first_int   = '0x10000000',
            last_int    = '0x1FFFFFFF',
            first_index = 2,
            index_bits  = 0x0ff0,
            backup      = True,
            read_only   = True,
            access      = CrmlAccess(cap_rd='ReadUserData'),
            subkeys     = subkeys)
    
    def test_create_keyrange_object(self):
        self.assertRaises(ValueError, CrmlKeyRange)
        self.assertRaises(ValueError, CrmlKeyRange, first_int='0x10')
        self.assertRaises(ValueError, CrmlKeyRange, last_int='0x1F')
        
        keyrange = CrmlKeyRange(first_int='0x10', last_int='0x1F')

class TestCrmlRepository(unittest.TestCase):

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
            version     = '2',
            access      = CrmlAccess(cap_rd='ReadUserData'),
            keys        = keys)

    def test_create_empty_repo(self):
        repo = CrmlRepository()
        self.assertEquals(repo.get_refs(), [])

    def test_create_repo_object(self):
        repo = CrmlRepository()
        self.assertEquals(repo.uid_value,   None)
        self.assertEquals(repo.uid_name,    None)
        self.assertEquals(repo.owner,       None)
        self.assertEquals(repo.backup,      False)
        self.assertEquals(repo.rfs,         False)
        self.assertEquals(repo.access,      CrmlAccess())
        self.assertEquals(repo.keys,        [])


        keys = [
            CrmlSimpleKey(ref='Foo.Bar', int='0x1'),
            CrmlBitmaskKey(int='0x2', bits=[CrmlBit(ref='Foo.Bit1', index=1),
                                            CrmlBit(ref='Foo.Bit2', index=2),
                                            CrmlBit(ref='Foo.Bit4', index=4, invert=True)]),
            CrmlKeyRange(first_int='0x10000000', last_int='0x1FFFFFFF', ref="Foo.Seq",
                         subkeys=[CrmlKeyRangeSubKey(ref='Sub1', name='Sub-key 1', type='int', int='0x1'),
                                  CrmlKeyRangeSubKey(ref='Sub2', name='Sub-key 2', type='real', int='0x2')]),
        ]
        
        repo = self.repo
        self.assertEquals(repo.uid_value,   '0x10203040')
        self.assertEquals(repo.uid_name,    'KCrUidTest')
        self.assertEquals(repo.owner,       '0x11223344')
        self.assertEquals(repo.backup,      True)
        self.assertEquals(repo.rfs,         True)
        self.assertEquals(repo.version,     '2')
        self.assertEquals(repo.access,      CrmlAccess(cap_rd='ReadUserData'))
        self.assertEquals(repo.keys,        keys)
    
    def test_clone_repo_object(self):
        repo1 = self.repo
        repo2 = repo1.copy()
        self.assertFalse(repo1 is repo2)
        self.assertTrue(repo1 == repo2)
        self.assertFalse(repo1 != repo2)
        
        # Assert that the keys have been deep-copied
        self.assertFalse(repo1.keys is repo2.keys)
        self.assertEquals(repo1.keys, repo2.keys)
        for i in xrange(len(repo1.keys)):
            self.assertFalse(repo1.keys[i] is repo2.keys[i])
    
    def test_compare_repo_objects(self):
        repo1 = CrmlRepository()
        repo2 = repo1.copy()
        self.assertTrue(repo1 == repo2)
        self.assertFalse(repo1 != repo2)
        
        def check(attrname, value):
            repo1 = self.repo
            repo2 = repo1.copy()
            setattr(repo2, attrname, value)
            self.assertFalse(repo1 == repo2)
            self.assertTrue(repo1 != repo2)
        
        # Check that changing each individual attribute makes the comparison fail
        check('uid_value',  '0xbaadf00d')
        check('uid_name',   'KFooUid')
        check('owner',      '0xbeef')
        check('backup',     False)
        check('rfs',        False)
        check('access',     CrmlAccess(cap_wr='WriteUserData'))
        check('keys',       ['foo'])
        check('version',    '3')
        
        def check2(mod_func):
            repo1 = self.repo
            repo2 = repo1.copy()
            mod_func(repo2)
            self.assertFalse(repo1 == repo2)
            self.assertTrue(repo1 != repo2)
        
        # Check that changing the keys makes the comparison fail
        check2(lambda r: setattr(r.keys[0], 'name', 'foo'))
        check2(lambda r: setattr(r.keys[1], 'type', 'binary'))
        check2(lambda r: setattr(r.keys[2], 'index_bits', 0x00ffff00))
    
    def test_get_repo_refs(self):
        self.assertEquals([], CrmlRepository(uid_value='0x1').get_refs())
        
        expected = ['Foo.Bar',
                    'Foo.Bit1',
                    'Foo.Bit2',
                    'Foo.Bit4',
                    'Foo.Seq',
                    'Foo.Seq.Sub1',
                    'Foo.Seq.Sub2']
        self.assertEquals(sorted(expected), sorted(self.repo.get_refs()))


class TestCrmlSimpleKey(unittest.TestCase):
    def setUp(self):
        self.key = CrmlSimpleKey(
            ref         = 'Foo.Bar',
            name        = 'Foobar',
            int         = '0x1020',
            type        = 'real',
            backup      = True,
            read_only   = True,
            access      = CrmlAccess(cap_rd='ReadUserData'))
    
    def test_create_key_object(self):
        # Not specifying ref or index should make the constructor fail
        self.assertRaises(ValueError, CrmlSimpleKey)
        self.assertRaises(ValueError, CrmlSimpleKey, ref='Foo.Bar')
        self.assertRaises(ValueError, CrmlSimpleKey, int='0x1')
        
        key = CrmlSimpleKey(ref='Foo.Bar', int='0x1')
        self.assertEquals(key.ref,          'Foo.Bar')
        self.assertEquals(key.name,         None)
        self.assertEquals(key.int,          '0x1')
        self.assertEquals(key.type,         'int')
        self.assertEquals(key.backup,       False)
        self.assertEquals(key.read_only,    False)
        self.assertEquals(key.access,       CrmlAccess())
        
        key = self.key
        self.assertEquals(key.ref,          'Foo.Bar')
        self.assertEquals(key.name,         'Foobar')
        self.assertEquals(key.int,          '0x1020')
        self.assertEquals(key.type,         'real')
        self.assertEquals(key.backup,       True)
        self.assertEquals(key.read_only,    True)
        self.assertEquals(key.access,       CrmlAccess(cap_rd='ReadUserData'))
    
    def test_clone_key_object(self):
        key1 = self.key
        key2 = key1.copy()
        self.assertFalse(key1 is key2)
        self.assertTrue(key1 == key2)
        self.assertFalse(key1 != key2)
    
    def test_compare_key_objects(self):
        def check(attrname, value):
            key1 = self.key
            key2 = key1.copy()
            setattr(key2, attrname, value)
            self.assertFalse(key1 == key2)
            self.assertTrue(key1 != key2)
        
        # Check that changing each individual attribute makes the comparison fail
        check('ref',        'Foo.Bar.Baz')
        check('name',       'Testing')
        check('int',        'KFooUid')
        check('type',       'selection')
        check('backup',     False)
        check('read_only',  False)
        check('access',     CrmlAccess(cap_wr='WriteUserData'))
    
    def test_get_key_refs(self):
        self.assertEquals(['Foo.Bar'], self.key.get_refs())

class TestCrmlBit(unittest.TestCase):
    def test_create_bit_object(self):
        # Not specifying ref or index should make the constructor fail
        self.assertRaises(ValueError, CrmlBit)
        self.assertRaises(ValueError, CrmlBit, ref='Foo.Bar')
        self.assertRaises(ValueError, CrmlBit, index='3')
        
        bit = CrmlBit(ref='Foo.Bar', index=1)
        self.assertEquals(bit.ref,      'Foo.Bar')
        self.assertEquals(bit.index,    1)
        self.assertEquals(bit.invert,   False)
        
        bit = CrmlBit(ref='Foo.Bar.Baz', index=2, invert=True)
        self.assertEquals(bit.ref,      'Foo.Bar.Baz')
        self.assertEquals(bit.index,    2)
        self.assertEquals(bit.invert,   True)
    
    def test_clone_bit_object(self):
        bit1 = CrmlBit(ref='Foo.Bar.Baz', index=2, invert=True)
        bit2 = bit1.copy()
        self.assertFalse(bit1 is bit2)
        self.assertTrue(bit1 == bit2)
        self.assertFalse(bit1 != bit2)
    
    def test_compare_bit_objects(self):
        bit1 = CrmlBit(ref='Foo.Bar.Baz', index=2, invert=True)
        
        def check(attrname, value):
            bit2 = bit1.copy()
            setattr(bit1, attrname, value)
            self.assertFalse(bit1 == bit2)
            self.assertTrue(bit1 != bit2)
        
        check('ref',    'Foo.Bar')
        check('index',  5)
        check('invert', False)

class TestCrmlBitmaskKey(unittest.TestCase):
    def setUp(self):
        bits = [
            CrmlBit(ref='Foo.Bit1', index=1),
            CrmlBit(ref='Foo.Bit2', index=2),
            CrmlBit(ref='Foo.Bit4', index=4, invert=True),
        ]
        self.bm = CrmlBitmaskKey(
            int         = '0x500',
            type        = 'int',
            backup      = True,
            read_only   = True,
            access      = CrmlAccess(cap_rd='ReadUserData'),
            bits        = bits)
    
    def test_create_bitmask_object(self):
        self.assertRaises(ValueError, CrmlBitmaskKey)
        
        bm = CrmlBitmaskKey(int='0x2')
        self.assertEquals(bm.int,       '0x2')
        self.assertEquals(bm.type,      'int')
        self.assertEquals(bm.backup,    False)
        self.assertEquals(bm.read_only, False)
        self.assertEquals(bm.access,    CrmlAccess())
        self.assertEquals(bm.bits,      [])
        
        bm = self.bm
        self.assertEquals(bm.int,       '0x500')
        self.assertEquals(bm.type,      'int')
        self.assertEquals(bm.backup,    True)
        self.assertEquals(bm.read_only, True)
        self.assertEquals(bm.access,    CrmlAccess(cap_rd='ReadUserData'))
        self.assertEquals(bm.bits,      [CrmlBit(ref='Foo.Bit1', index=1),
                                         CrmlBit(ref='Foo.Bit2', index=2),
                                         CrmlBit(ref='Foo.Bit4', index=4, invert=True)])
    
    def test_clone_bitmask_object(self):
        bm1 = self.bm
        bm2 = bm1.copy()
        self.assertFalse(bm1 is bm2)
        self.assertTrue(bm1 == bm2)
        self.assertFalse(bm1 != bm2)
        
        # Assert that the bits have been deep-copied
        self.assertFalse(bm1.bits is bm2.bits)
        self.assertEquals(bm1.bits, bm2.bits)
        for i in xrange(len(bm1.bits)):
            self.assertFalse(bm1.bits[i] is bm2.bits[i])
    
    def test_compare_bitmask_objects(self):
        def check(attrname, value):
            bm1 = self.bm
            bm2 = bm1.copy()
            setattr(bm2, attrname, value)
            self.assertFalse(bm1 == bm2)
            self.assertTrue(bm1 != bm2)
        
        check('int',        '0x600')
        check('type',       'binary')
        check('backup',     False)
        check('read_only',  False)
        check('access',     CrmlAccess(cap_rd='ReadDeviceData'))
        check('bits',       [CrmlBit(ref='Foo.Bit7', index=7),
                             CrmlBit(ref='Foo.Bit9', index=9)])
    
    def test_get_bitmask_refs(self):
        self.assertEquals([], CrmlBitmaskKey(int='0x1').get_refs())
        
        expected = ['Foo.Bit1',
                    'Foo.Bit2',
                    'Foo.Bit4',]
        self.assertEquals(sorted(expected), sorted(self.bm.get_refs()))
 
class TestCrmlKeyRangeSubKey(unittest.TestCase):

    def setUp(self):
        self.subkey = CrmlKeyRangeSubKey(ref='Foo.Bar', name='Foobar', type='int', int='0x1')

    def test_create_subkey_object(self):
        self.assertRaises(ValueError, CrmlKeyRangeSubKey)
        self.assertRaises(ValueError, CrmlKeyRangeSubKey, ref='Foo.Bar')
        self.assertRaises(ValueError, CrmlKeyRangeSubKey, type='int')
        self.assertRaises(ValueError, CrmlKeyRangeSubKey, int='0x1')
        
        subkey = self.subkey
        self.assertEquals(subkey.ref,   'Foo.Bar')
        self.assertEquals(subkey.name,  'Foobar')
        self.assertEquals(subkey.type,  'int')
        self.assertEquals(subkey.int,   '0x1')
    
    def test_clone_subkey_object(self):
        subkey1 = self.subkey
        subkey2 = subkey1.copy()
        self.assertFalse(subkey1 is subkey2)
        self.assertTrue(subkey1 == subkey2)
        self.assertFalse(subkey1 != subkey2)
    
    def test_compare_subkey_objects(self):
        def check(attrname, value):
            subkey1 = self.subkey
            subkey2 = subkey1.copy()
            setattr(subkey2, attrname, value)
            self.assertFalse(subkey1 == subkey2)
            self.assertTrue(subkey1 != subkey2)
        
        check('ref',    'Foo.Bar.Baz')
        check('name',   'Test')
        check('int',    '0x2')
        check('type',   'binary')

class TestCrmlKeyRange(unittest.TestCase):
    def setUp(self):
        subkeys = [
            CrmlKeyRangeSubKey(ref='Sub1', name='Sub-key 1', type='int', int='0x1'),
            CrmlKeyRangeSubKey(ref='Sub2', name='Sub-key 2', type='real', int='0x2'),
            CrmlKeyRangeSubKey(ref='Sub3', name='Sub-key 3', type='string', int='0x3'),
        ]
        self.keyrange = CrmlKeyRange(
            ref         = 'Foo.Seq',
            first_int   = '0x10000000',
            last_int    = '0x1FFFFFFF',
            first_index = 2,
            index_bits  = 0x0ff0,
            backup      = True,
            read_only   = True,
            access      = CrmlAccess(cap_rd='ReadUserData'),
            subkeys     = subkeys)
    
    def test_create_keyrange_object(self):
        self.assertRaises(ValueError, CrmlKeyRange)
        self.assertRaises(ValueError, CrmlKeyRange, first_int='0x10')
        self.assertRaises(ValueError, CrmlKeyRange, last_int='0x1F')
        
        keyrange = CrmlKeyRange(first_int='0x10', last_int='0x1F')
        self.assertEquals(keyrange.first_int,   '0x10')
        self.assertEquals(keyrange.last_int,    '0x1F')
        self.assertEquals(keyrange.first_index, 0)
        self.assertEquals(keyrange.index_bits,  None)
        self.assertEquals(keyrange.backup,      False)
        self.assertEquals(keyrange.read_only,   False)
        self.assertEquals(keyrange.access,      CrmlAccess())
        self.assertEquals(keyrange.subkeys,     [])
    
        keyrange = self.keyrange
        self.assertEquals(keyrange.first_int,   '0x10000000')
        self.assertEquals(keyrange.last_int,    '0x1FFFFFFF')
        self.assertEquals(keyrange.first_index, 2)
        self.assertEquals(keyrange.index_bits,  0x0ff0)
        self.assertEquals(keyrange.backup,      True)
        self.assertEquals(keyrange.read_only,   True)
        self.assertEquals(keyrange.access,      CrmlAccess(cap_rd='ReadUserData'))
        self.assertEquals(keyrange.subkeys,     [
            CrmlKeyRangeSubKey(ref='Sub1', name='Sub-key 1', type='int', int='0x1'),
            CrmlKeyRangeSubKey(ref='Sub2', name='Sub-key 2', type='real', int='0x2'),
            CrmlKeyRangeSubKey(ref='Sub3', name='Sub-key 3', type='string', int='0x3')])
        
    
    def test_clone_keyrange_object(self):
        keyrange1 = self.keyrange
        keyrange2 = keyrange1.copy()
        self.assertFalse(keyrange1 is keyrange2)
        self.assertTrue(keyrange1 == keyrange2)
        self.assertFalse(keyrange1 != keyrange2)
        
        # Assert that the sub-keys have been deep-copied
        self.assertFalse(keyrange1.subkeys is keyrange2.subkeys)
        self.assertEquals(keyrange1.subkeys, keyrange2.subkeys)
        for i in xrange(len(keyrange1.subkeys)):
            self.assertFalse(keyrange1.subkeys[i] is keyrange2.subkeys[i])
    
    def test_compare_keyrange_objects(self):
        def check(attrname, value):
            keyrange1 = self.keyrange
            keyrange2 = keyrange1.copy()
            setattr(keyrange2, attrname, value)
            self.assertFalse(keyrange1 == keyrange2)
            self.assertTrue(keyrange1 != keyrange2)
        
        check('first_int',      '0x20000000')
        check('last_int',       '0x2FFFFFFF')
        check('first_index',    3)
        check('index_bits',     0xf00)
        check('backup',         False)
        check('read_only',      False)
        check('access',         CrmlAccess(cap_rd='ReadDeviceData'))
        check('subkeys',        [
            CrmlKeyRangeSubKey(ref='Sub0x100', name='Sub-key 0x100', type='string', int='0x100'),
            CrmlKeyRangeSubKey(ref='Sub0x200', name='Sub-key 0x200', type='binary', int='0x200')])
    
    def test_get_keyrange_refs(self):
        self.assertEquals([], CrmlKeyRange(first_int='0x1', last_int='0x2').get_refs())
        
        expected = ['Foo.Seq',
                    'Foo.Seq.Sub1',
                    'Foo.Seq.Sub2',
                    'Foo.Seq.Sub3',]
        self.assertEquals(sorted(expected), sorted(self.keyrange.get_refs()))

if __name__ == "__main__":
    unittest.main()