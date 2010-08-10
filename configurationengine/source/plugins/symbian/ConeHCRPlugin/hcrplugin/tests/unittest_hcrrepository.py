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

from hcrplugin.hcrrepository import HcrRepository, HcrRecord


ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class TestHcrRepository(unittest.TestCase):
    def test_repository_equality(self):
        self.assertTrue(HcrRepository([], 1, 1) == HcrRepository([], 1, 1))
        self.assertFalse(HcrRepository([], 1, 1) == HcrRepository([], 2, 1))
        self.assertFalse(HcrRepository([], 1, 1) == HcrRepository([], 1, 2))
        
        self.assertTrue(HcrRepository([], 1, 1) != HcrRepository([], 1, 2))
        
        # Records the same, but in different order
        r1 = HcrRepository([
                HcrRecord(HcrRecord.VALTYPE_INT8,       10, 20, 30, 93),
                HcrRecord(HcrRecord.VALTYPE_INT8,       25, 20, 62, 41),
                HcrRecord(HcrRecord.VALTYPE_BIN_DATA,   10, 20, 31, 40),
                HcrRecord(HcrRecord.VALTYPE_INT8,       10, 20, 83, 41),
                HcrRecord(HcrRecord.VALTYPE_UINT64,     10, 21, 30, 40)],
                version=1, flags=1)
        r2 = HcrRepository([
                HcrRecord(HcrRecord.VALTYPE_UINT64,     10, 21, 30, 40),
                HcrRecord(HcrRecord.VALTYPE_INT8,       10, 20, 30, 93),
                HcrRecord(HcrRecord.VALTYPE_INT8,       10, 20, 83, 41),
                HcrRecord(HcrRecord.VALTYPE_BIN_DATA,   10, 20, 31, 40),
                HcrRecord(HcrRecord.VALTYPE_INT8,       25, 20, 62, 41),
                ],
                version=1, flags=1)
        self.assertTrue(r1 == r2)
        self.assertEquals(repr(r1), repr(r2))
        
        r1.version = 2
        self.assertFalse(r1 == r2)
        r1.version = 1
        self.assertTrue(r1 == r2)
        r1.flags = 3
        self.assertFalse(r1 == r2)
        r1.flags = 1
        self.assertTrue(r1 == r2)
        
        r1.records.append(HcrRecord(HcrRecord.VALTYPE_LIN_ADDR, 1, 2, 3, 4))
        self.assertFalse(r1 == r2)
        
    def test_get_duplicate_records(self):
        r = HcrRepository([
                HcrRecord(HcrRecord.VALTYPE_INT8, 162, 1, 1, 93),
                HcrRecord(HcrRecord.VALTYPE_INT8, 172, 1, 2, 41),
                HcrRecord(HcrRecord.VALTYPE_TEXT8, 182, 1, 3, 40),
                HcrRecord(HcrRecord.VALTYPE_INT8, 192, 2, 1, 41),
                HcrRecord(HcrRecord.VALTYPE_UINT32, 202, 2, 2, 40)],
                version=1, flags=1)
        
        self.assertEquals(r.get_duplicate_record_ids(), [])
        
        r.records.append(HcrRecord(HcrRecord.VALTYPE_UINT16, 212, 1, 1, 142))
        self.assertEquals(r.get_duplicate_record_ids(), [(1, 1)])
        
        r.records.append(HcrRecord(HcrRecord.VALTYPE_UINT64, 105, 1, 1, 142))
        self.assertEquals(r.get_duplicate_record_ids(), [(1, 1)])
        
        r.records.append(HcrRecord(HcrRecord.VALTYPE_UINT64, 222, 2, 2, 32))
        self.assertEquals(r.get_duplicate_record_ids(), [(1, 1), (2, 2)])
        
        r.records.append(HcrRecord(HcrRecord.VALTYPE_TEXT8, 232, 3, 1, 32))
        self.assertEquals(r.get_duplicate_record_ids(), [(1, 1), (2, 2)])

class TestHCRRecord(unittest.TestCase):

    def test_create_record_with_valid_type(self):
        r = HcrRecord(HcrRecord.VALTYPE_INT16, 1234, 1, 2, 3)
        self.assertEquals(r.type, HcrRecord.VALTYPE_INT16)
        self.assertEquals(r.value, 1234)
        self.assertEquals(r.category_id, 1)
        self.assertEquals(r.element_id, 2)
        self.assertEquals(r.flags, 3)

    def test_create_record_with_invalid_type(self):
        try:
            r = HcrRecord('foobar_type', 0, 0, 0, 0)
            self.fail("Creating a foobar_type record succeeded!")
        except ValueError:
            pass
    
    def test_record_equality(self):
        self.assertTrue(HcrRecord(HcrRecord.VALTYPE_INT8, 10, 20, 30, 93)  == HcrRecord(HcrRecord.VALTYPE_INT8, 10, 20, 30, 93))
        
        self.assertFalse(HcrRecord(HcrRecord.VALTYPE_INT8, 10, 20, 30, 93) == HcrRecord(HcrRecord.VALTYPE_INT16, 10, 20, 30, 93))
        self.assertFalse(HcrRecord(HcrRecord.VALTYPE_INT8, 10, 20, 30, 93) == HcrRecord(HcrRecord.VALTYPE_INT8,   2, 20, 30, 93))
        self.assertFalse(HcrRecord(HcrRecord.VALTYPE_INT8, 10, 20, 30, 93) == HcrRecord(HcrRecord.VALTYPE_INT8,  10,  2, 30, 93))
        self.assertFalse(HcrRecord(HcrRecord.VALTYPE_INT8, 10, 20, 30, 93) == HcrRecord(HcrRecord.VALTYPE_INT8,  10, 20,  2, 93))
        self.assertFalse(HcrRecord(HcrRecord.VALTYPE_INT8, 10, 20, 30, 93) == HcrRecord(HcrRecord.VALTYPE_INT8,  10, 20, 30, 2))
        
        self.assertTrue(HcrRecord(HcrRecord.VALTYPE_INT8, 10, 20, 30, 93) != HcrRecord(HcrRecord.VALTYPE_INT8,  10, 20, 30, 2))
        
        r1 = HcrRecord(HcrRecord.VALTYPE_INT8, 10, 20, 30, 93)
        r2 = HcrRecord(HcrRecord.VALTYPE_INT8, 10, 20, 30, 93)
        self.assertEquals(repr(r1), repr(r2))
        r2.value = 12
        self.assertNotEquals(repr(r1), repr(r2))
    
    def test_record_sorting(self):
        records1 = [
            HcrRecord(HcrRecord.VALTYPE_INT8,       10, 20, 30, 93),
            HcrRecord(HcrRecord.VALTYPE_INT8,       25, 20, 62, 41),
            HcrRecord(HcrRecord.VALTYPE_INT8,       10, 20, 30, 93),
            HcrRecord(HcrRecord.VALTYPE_BIN_DATA,   10, 20, 31, 40),
            HcrRecord(HcrRecord.VALTYPE_INT8,       10, 20, 83, 41),
            HcrRecord(HcrRecord.VALTYPE_UINT64,     10, 21, 30, 40),
            ]

        records2 = [
            HcrRecord(HcrRecord.VALTYPE_BIN_DATA,   10, 20, 31, 40),
            HcrRecord(HcrRecord.VALTYPE_INT8,       25, 20, 62, 41),
            HcrRecord(HcrRecord.VALTYPE_UINT64,     10, 21, 30, 40),
            HcrRecord(HcrRecord.VALTYPE_INT8,       10, 20, 83, 41),
            HcrRecord(HcrRecord.VALTYPE_INT8,       10, 20, 30, 93),
            HcrRecord(HcrRecord.VALTYPE_INT8,       10, 20, 30, 93),
            ]
        
        self.assertNotEquals(records1, records2)
        self.assertEquals(sorted(records1), sorted(records2))
