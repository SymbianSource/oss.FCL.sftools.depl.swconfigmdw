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

from testautomation.utils import hex_to_bindata

from hcrplugin.hcr_reader import HcrReader
from hcrplugin import hcr_exceptions
from hcrplugin.hcrrepository import HcrRecord


class TestHcrReader(unittest.TestCase):
    def setUp(self):
        self.reader = HcrReader()
        
    def test_read_repo_with_invalid_record_section_size(self):
        # Record section size: 4 * 20 = 80
        # LSD offset: 32 + 80 = 112
        # LSD size:   0
        data =  [
            # Header
            # Record count should be 4, but is 6 here
            "48435266 0200 0300 06000000 70000000",
            "00000000 000000000000000000000000",
            # Record section
            "01000000 01000000 08000000 0000 0000 01000000", # bool
            "02000000 01000000 04000000 0000 0000 85FFFFFF", # int8
            "03000000 01000000 40000000 0000 0000 CC000000", # uint8
            "01000000 02000000 02000000 0000 0000 91CBFFFF", # int16
        ]
        data = ''.join(map(lambda x: hex_to_bindata(x), data))
        
        try:
            self.reader.parse_repository_from_bindata(data)
            self.fail("Expected exception not raised")
        except hcr_exceptions.InvalidHcrDataSizeError:
            pass
    
    def test_read_repo_with_invalid_lsd_section_size(self):
        # Record section size: 4 * 20 = 80
        # LSD offset: 32 + 80 = 112
        # LSD size:   0
        data =  [
            # Header
            # LSD section size should be 0, but is 40 here
            "48435266 0200 0300 04000000 70000000",
            "28000000 000000000000000000000000",
            # Record section
            "01000000 01000000 08000000 0000 0000 01000000", # bool
            "02000000 01000000 04000000 0000 0000 85FFFFFF", # int8
            "03000000 01000000 40000000 0000 0000 CC000000", # uint8
            "01000000 02000000 02000000 0000 0000 91CBFFFF", # int16
        ]
        data = ''.join(map(lambda x: hex_to_bindata(x), data))
        
        try:
            self.reader.parse_repository_from_bindata(data)
            self.fail("Expected exception not raised")
        except hcr_exceptions.InvalidHcrDataSizeError:
            pass
    
    def test_read_repo_with_invalid_lsd_section_offset(self):
        # Record section size: 2 * 20 = 40
        # LSD offset: 32 + 40 = 72
        # LSD size:   8 + 8 = 16
        data = [
            # Header, LSD offset here is 60
            "48435266 0200 0300 02000000 3C000000",
            "10000000 000000000000000000000000",
            # Record section
            "01000000 01000000 00000001 0000 0800 00000000", # int64, lsd pos = (0, 8)
            "02000000 01000000 00000002 0000 0800 08000000", # uint64, lsd pos = (8, 8)
            # LSD section
            "FC73 978B B823 D47F",          # 8 bytes
            "14FD 32B4 F410 2295",          # 8 bytes
        ]
        data = ''.join(map(lambda x: hex_to_bindata(x), data))
        
        try:
            self.reader.parse_repository_from_bindata(data)
            self.fail("Expected exception not raised")
        except hcr_exceptions.InvalidLsdSectionOffsetError:
            pass
    
    def test_read_repo_with_invalid_lsd_pos_in_record(self):
        # Record section size: 2 * 20 = 40
        # LSD offset: 32 + 40 = 72
        # LSD size:   8 + 8 = 16
        data = [
            # Header
            "48435266 0200 0300 02000000 48000000",
            "10000000 000000000000000000000000",
            # Record section
            "01000000 01000000 00000001 0000 0800 00000000", # int64, lsd pos = (0, 8)
            "02000000 01000000 00000002 0000 0800 0C000000", # uint64, lsd pos = (12, 8), should be (8, 8)
            # LSD section
            "FC73 978B B823 D47F",          # 8 bytes
            "14FD 32B4 F410 2295",          # 8 bytes
        ]
        data = ''.join(map(lambda x: hex_to_bindata(x), data))
        
        try:
            self.reader.parse_repository_from_bindata(data)
            self.fail("Expected exception not raised")
        except hcr_exceptions.InvalidRecordLsdPositionError:
            pass
    
    def test_read_repo_with_invalid_record_value_type(self):
        # Record section size: 2 * 20 = 40
        # LSD offset: 32 + 40 = 72
        # LSD size:   8 + 8 = 16
        data = [
            # Header
            "48435266 0200 0300 02000000 48000000",
            "10000000 000000000000000000000000",
            # Record section
            "01000000 01000000 00000001 0000 0800 00000000", # int64, lsd pos = (0, 8)
            "02000000 01000000 DEADBEEF 0000 0800 0C000000", # invalid type
            # LSD section
            "FC73 978B B823 D47F",          # 8 bytes
            "14FD 32B4 F410 2295",          # 8 bytes
        ]
        data = ''.join(map(lambda x: hex_to_bindata(x), data))
        
        try:
            self.reader.parse_repository_from_bindata(data)
            self.fail("Expected exception not raised")
        except hcr_exceptions.InvalidRecordValueTypeError:
            pass
    
    def _run_test_read_record_with_invalid_lsd_size(self, value_type, lsd_data):
        try:
            self.reader.parse_record_value_from_lsd_bindata(value_type, lsd_data)
            self.fail("Expected exception not raised")
        except hcr_exceptions.InvalidRecordLsdPositionError:
            pass
    
    def test_read_record_with_invalid_lsd_size_int64(self):
        data = hex_to_bindata("0000 0000 0000 00")
        self._run_test_read_record_with_invalid_lsd_size(HcrRecord.VALTYPE_INT64, data)
    
    def test_read_record_with_invalid_lsd_size_uint64(self):
        data = hex_to_bindata("0000 0000 0000 00")
        self._run_test_read_record_with_invalid_lsd_size(HcrRecord.VALTYPE_UINT64, data)
    
    def test_read_record_with_invalid_lsd_size_arrayint32(self):
        data = hex_to_bindata("0000 0000 0000 00")
        self._run_test_read_record_with_invalid_lsd_size(HcrRecord.VALTYPE_ARRAY_INT32, data)
    
    def test_read_record_with_invalid_lsd_size_arrayuint32(self):
        data = hex_to_bindata("0000 0000 0000 00")
        self._run_test_read_record_with_invalid_lsd_size(HcrRecord.VALTYPE_ARRAY_UINT32, data)
    
    
    def test_read_record_with_invalid_data_size(self):
        try:
            self.reader.parse_record_from_bindata('1234')
            self.fail("Parsing invalid record data succeeded!")
        except hcr_exceptions.HcrReaderError:
            pass
    
    def test_read_signed_integer_in_record(self):
        #Test that padding bytes don't matter when reading the type
        def check(record, data):
            self.assertEquals(self.reader.parse_record_from_bindata(data)[0], record)
        
        r = HcrRecord(HcrRecord.VALTYPE_INT8, -123, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 04000000 0500 0000 85FFFFFF")
        check(r, d)
        d = hex_to_bindata("0C000000 2B000000 04000000 0500 0000 85000000")
        check(r, d)
        
        r = HcrRecord(HcrRecord.VALTYPE_INT16, -12345, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 02000000 0500 0000 C7CFFFFF")
        check(r, d)
        d = hex_to_bindata("0C000000 2B000000 02000000 0500 0000 C7CF0000")
        check(r, d)
        
    