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

from hcrplugin.hcrrepository import HcrRepository, HcrRecord
from hcrplugin.hcr_writer import HcrWriter
from hcrplugin import hcr_exceptions

class TestHcrWriter(unittest.TestCase):
    def setUp(self):
        self.writer = HcrWriter()
    
    def test_write_repo_with_duplicate_record(self):
        records = [
            HcrRecord(HcrRecord.VALTYPE_INT8, -123, 1, 1, 0),
            HcrRecord(HcrRecord.VALTYPE_INT8, 124,  2, 1, 0),
            HcrRecord(HcrRecord.VALTYPE_INT8, 66,   3, 1, 0),
            HcrRecord(HcrRecord.VALTYPE_INT8, -72,  1, 1, 0),
            HcrRecord(HcrRecord.VALTYPE_INT8, 171,  1, 2, 0),
        ]
        repo = HcrRepository(records, version=2, flags=3)
        
        try:
            self.writer.get_repository_bindata(repo)
        except hcr_exceptions.DuplicateRecordError:
            pass

    def test_record_sorting_by_setting_id(self):
        records = [
            HcrRecord(HcrRecord.VALTYPE_INT8, 10, 3, 1, 0),
            HcrRecord(HcrRecord.VALTYPE_INT8, 10, 1, 1, 0),
            HcrRecord(HcrRecord.VALTYPE_INT8, 10, 2, 2, 0),
            HcrRecord(HcrRecord.VALTYPE_INT8, 10, 2, 1, 0),
            HcrRecord(HcrRecord.VALTYPE_INT8, 10, 1, 2, 0),
            
            ]

        expected = [
            HcrRecord(HcrRecord.VALTYPE_INT8, 10, 1, 1, 0),
            HcrRecord(HcrRecord.VALTYPE_INT8, 10, 1, 2, 0),
            HcrRecord(HcrRecord.VALTYPE_INT8, 10, 2, 1, 0),
            HcrRecord(HcrRecord.VALTYPE_INT8, 10, 2, 2, 0),
            HcrRecord(HcrRecord.VALTYPE_INT8, 10, 3, 1, 0),
            ]
        
        self.assertEquals(sorted(records, key=self.writer.get_record_setting_id), expected)

    def _run_test_write_record_with_invalid_value(self, record_type, record_value):
        try:
            record = HcrRecord(record_type, record_value, 0, 0, 0)
            self.writer.get_record_bindata(record, (0, 0))
            self.fail("Expected exception not thrown!")
        except hcr_exceptions.ValueNotInRangeError, e:
            pass

    def test_write_numeric_record_with_invalid_value(self):
        def test(record_type, bits, unsigned):
            if unsigned:
                value1 = -1
                value2 = 2**bits
            else:
                value1 = -(2**(bits-1) + 1)
                value2 = 2**(bits-1)
            
            if record_type in (HcrRecord.VALTYPE_ARRAY_INT32, HcrRecord.VALTYPE_ARRAY_UINT32):
                value1 = [1, value1, 2]
                value2 = [1, value2, 2]
            
            self._run_test_write_record_with_invalid_value(record_type, value1)
            self._run_test_write_record_with_invalid_value(record_type, value2)
        
        test(HcrRecord.VALTYPE_INT8,            8,  False)
        test(HcrRecord.VALTYPE_UINT8,           8,  True)
        test(HcrRecord.VALTYPE_INT16,           16, False)
        test(HcrRecord.VALTYPE_UINT16,          16, True)
        test(HcrRecord.VALTYPE_INT32,           32, False)
        test(HcrRecord.VALTYPE_UINT32,          32, True)
        test(HcrRecord.VALTYPE_LIN_ADDR,        32, True)
        test(HcrRecord.VALTYPE_INT64,           64, False)
        test(HcrRecord.VALTYPE_UINT64,          64, True)
        test(HcrRecord.VALTYPE_ARRAY_INT32,     32, False)
        test(HcrRecord.VALTYPE_ARRAY_UINT32,    32, True)
    
    def test_write_value_with_too_large_lsd_data(self):
        def test(record_type, value):
            try:
                record = HcrRecord(record_type, value, 0, 0, 0)
                self.writer.get_record_lsd_bindata(record)
                self.fail("Expected exception not raised!")
            except hcr_exceptions.TooLargeLsdDataError:
                pass
        
        test(HcrRecord.VALTYPE_ARRAY_INT32, [i for i in xrange(150)])
        test(HcrRecord.VALTYPE_ARRAY_UINT32, [i for i in xrange(150)])
        test(HcrRecord.VALTYPE_BIN_DATA, 513 * ' ')
        test(HcrRecord.VALTYPE_TEXT8, 200 * u'\u20ac')
