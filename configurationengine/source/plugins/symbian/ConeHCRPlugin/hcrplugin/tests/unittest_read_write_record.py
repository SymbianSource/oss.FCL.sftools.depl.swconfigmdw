# *-* coding: utf-8 *-*
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

"""
When editing the hex data in the test cases, this may come in handy:

1. Start the Python command line interpreter
2. Paste the following lines there:

from struct import pack, unpack
bin2hex = lambda d: ''.join("%02X" % ord(c) for c in d)
hexpack = lambda fmt, *args: bin2hex(pack(fmt, *args))
hex2bin = lambda h: ''.join([chr(int(h[i*2:i*2+2], 16)) for i in xrange(len(h)/2)])
hexunpack = lambda fmt, data: unpack(fmt, hex2bin(data))

Now you can get the hex representation for any format supported by
struct.pack() easily. For example, formatting a little-endian unsigned short:

>>> hexpack('<H', 1234)
'D204'

...and conversely:

>>> hexunpack('<H', 'D204')
(1234,)
"""

import unittest
import os, shutil
import sys
import __init__

from testautomation.utils import hex_to_bindata

from hcrplugin.hcrrepository import HcrRepository, HcrRecord
from hcrplugin.hcr_writer import HcrWriter
from hcrplugin.hcr_reader import HcrReader

class TestReadWriteHcrRecords(unittest.TestCase):
    
    def setUp(self):
        self.writer = HcrWriter()
        self.reader = HcrReader()
    
    def _run_test_read_write_record_no_lsd(self, record, record_bindata):
        self.assertEquals(self.writer.get_record_bindata(record, None), record_bindata)
        self.assertEquals(self.writer.get_record_lsd_bindata(record), None)
        
        parsed_record, parsed_lsd_pos = self.reader.parse_record_from_bindata(record_bindata)
        self.assertEquals(parsed_record.type,           record.type)
        self.assertEquals(parsed_record.value,          record.value)
        self.assertEquals(parsed_record.category_id,    record.category_id)
        self.assertEquals(parsed_record.element_id,     record.element_id)
        self.assertEquals(parsed_record.flags,          record.flags)
        self.assertEquals(parsed_lsd_pos,               None)
        
        self.assertEquals(self.reader.parse_record_value_from_lsd_bindata(parsed_record.type, None), None)
    
    def _run_test_read_write_record_with_lsd(self, record, record_bindata, lsd_pos, lsd_bindata):
        self.assertEquals(self.writer.get_record_bindata(record, lsd_pos), record_bindata)
        self.assertEquals(self.writer.get_record_lsd_bindata(record), lsd_bindata)
        
        
        parsed_record, parsed_lsd_pos = self.reader.parse_record_from_bindata(record_bindata)
        self.assertEquals(parsed_record.type,           record.type)
        self.assertEquals(parsed_record.category_id,    record.category_id)
        self.assertEquals(parsed_record.element_id,     record.element_id)
        self.assertEquals(parsed_record.flags,          record.flags)
        self.assertEquals(parsed_lsd_pos,               lsd_pos)
        
        self.assertEquals(self.reader.parse_record_value_from_lsd_bindata(record.type, lsd_bindata), record.value)
    
    # -------------------------------------------------------------------------
    #
    # -------------------------------------------------------------------------

    def test_read_write_bool(self):
        r = HcrRecord(HcrRecord.VALTYPE_BOOL, False, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 08000000 0500 0000 00000000")
        self._run_test_read_write_record_no_lsd(r, d)
        
        r = HcrRecord(HcrRecord.VALTYPE_BOOL, True, 0xDEADBEEF, 0xBAADF00D, 0xCAFE)
        d = hex_to_bindata("EFBEADDE 0DF0ADBA 08000000 FECA 0000 01000000")
        self._run_test_read_write_record_no_lsd(r, d)
    
    def test_read_write_int8(self):
        r = HcrRecord(HcrRecord.VALTYPE_INT8, -2**7, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 04000000 0500 0000 80FFFFFF")
        self._run_test_read_write_record_no_lsd(r, d)
        
        r = HcrRecord(HcrRecord.VALTYPE_INT8, 122, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 04000000 0500 0000 7A000000")
        self._run_test_read_write_record_no_lsd(r, d)
        
        r = HcrRecord(HcrRecord.VALTYPE_INT8, 2**7-1, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 04000000 0500 0000 7F000000")
        self._run_test_read_write_record_no_lsd(r, d)
    
    def test_read_write_uint8(self):
        r = HcrRecord(HcrRecord.VALTYPE_UINT8, 0, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 40000000 0500 0000 00000000")
        self._run_test_read_write_record_no_lsd(r, d)
        
        r = HcrRecord(HcrRecord.VALTYPE_UINT8, 234, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 40000000 0500 0000 EA000000")
        self._run_test_read_write_record_no_lsd(r, d)
        
        r = HcrRecord(HcrRecord.VALTYPE_UINT8, 2**8-1, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 40000000 0500 0000 FF000000")
        self._run_test_read_write_record_no_lsd(r, d)
    
    def test_read_write_int16(self):
        r = HcrRecord(HcrRecord.VALTYPE_INT16, -2**15, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 02000000 0500 0000 0080FFFF")
        self._run_test_read_write_record_no_lsd(r, d)
        
        r = HcrRecord(HcrRecord.VALTYPE_INT16, 12345, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 02000000 0500 0000 39300000")
        self._run_test_read_write_record_no_lsd(r, d)
        
        r = HcrRecord(HcrRecord.VALTYPE_INT16, 2**15-1, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 02000000 0500 0000 FF7F0000")
        self._run_test_read_write_record_no_lsd(r, d)

    def test_read_write_uint16(self):
        r = HcrRecord(HcrRecord.VALTYPE_UINT16, 0, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 20000000 0500 0000 00000000")
        self._run_test_read_write_record_no_lsd(r, d)
        
        r = HcrRecord(HcrRecord.VALTYPE_UINT16, 43215, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 20000000 0500 0000 CFA80000")
        self._run_test_read_write_record_no_lsd(r, d)
        
        r = HcrRecord(HcrRecord.VALTYPE_UINT16, 2**16-1, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 20000000 0500 0000 FFFF0000")
        self._run_test_read_write_record_no_lsd(r, d)
    
    def test_read_write_int32(self):
        r = HcrRecord(HcrRecord.VALTYPE_INT32, -2**31, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 01000000 0500 0000 00000080")
        self._run_test_read_write_record_no_lsd(r, d)
        
        r = HcrRecord(HcrRecord.VALTYPE_INT32, 1234567890, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 01000000 0500 0000 D2029649")
        self._run_test_read_write_record_no_lsd(r, d)
        
        r = HcrRecord(HcrRecord.VALTYPE_INT32, 2**31-1, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 01000000 0500 0000 FFFFFF7F")
        self._run_test_read_write_record_no_lsd(r, d)
    
    def test_read_write_uint32(self):
        r = HcrRecord(HcrRecord.VALTYPE_UINT32, 0, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 10000000 0500 0000 00000000")
        self._run_test_read_write_record_no_lsd(r, d)
        
        r = HcrRecord(HcrRecord.VALTYPE_UINT32, 3123456789, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 10000000 0500 0000 152B2CBA")
        self._run_test_read_write_record_no_lsd(r, d)
        
        r = HcrRecord(HcrRecord.VALTYPE_UINT32, 2**32-1, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 10000000 0500 0000 FFFFFFFF")
        self._run_test_read_write_record_no_lsd(r, d)
    
    def test_read_write_linaddr(self):
        r = HcrRecord(HcrRecord.VALTYPE_LIN_ADDR, 0, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 00010000 0500 0000 00000000")
        self._run_test_read_write_record_no_lsd(r, d)
        
        r = HcrRecord(HcrRecord.VALTYPE_LIN_ADDR, 3123456789, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 00010000 0500 0000 152B2CBA")
        self._run_test_read_write_record_no_lsd(r, d)
        
        r = HcrRecord(HcrRecord.VALTYPE_LIN_ADDR, 2**32-1, 12, 43, 5)
        d = hex_to_bindata("0C000000 2B000000 00010000 0500 0000 FFFFFFFF")
        self._run_test_read_write_record_no_lsd(r, d)



    def test_read_write_int64(self):
        lsd_pos = (1234, 8)

        record = HcrRecord(HcrRecord.VALTYPE_INT64, -2**63, 12, 43, 5)
        rec_data = hex_to_bindata("0C000000 2B000000 00000001 0500 0800 D2040000")
        lsd_data = hex_to_bindata("0000 0000 0000 0080")
        self._run_test_read_write_record_with_lsd(record, rec_data, lsd_pos, lsd_data)

        record = HcrRecord(HcrRecord.VALTYPE_INT64, 9211026413402420220, 12, 43, 5)
        rec_data = hex_to_bindata("0C000000 2B000000 00000001 0500 0800 D2040000")
        lsd_data = hex_to_bindata("FC73 978B B823 D47F")
        self._run_test_read_write_record_with_lsd(record, rec_data, lsd_pos, lsd_data)

        record = HcrRecord(HcrRecord.VALTYPE_INT64, 2**63-1, 12, 43, 5)
        rec_data = hex_to_bindata("0C000000 2B000000 00000001 0500 0800 D2040000")
        lsd_data = hex_to_bindata("FFFF FFFF FFFF FF7F")
        self._run_test_read_write_record_with_lsd(record, rec_data, lsd_pos, lsd_data)
    
    def test_read_write_uint64(self):
        lsd_pos = (1234, 8)
        record = HcrRecord(HcrRecord.VALTYPE_UINT64, 0, 12, 43, 5)
        rec_data = hex_to_bindata("0C000000 2B000000 00000002 0500 0800 D2040000")
        lsd_data = hex_to_bindata("0000 0000 0000 0000")
        self._run_test_read_write_record_with_lsd(record, rec_data, lsd_pos, lsd_data)

        record = HcrRecord(HcrRecord.VALTYPE_UINT64, 10746170304040729876, 12, 43, 5)
        rec_data = hex_to_bindata("0C000000 2B000000 00000002 0500 0800 D2040000")
        lsd_data = hex_to_bindata("14FD 32B4 F410 2295")
        self._run_test_read_write_record_with_lsd(record, rec_data, lsd_pos, lsd_data)

        record = HcrRecord(HcrRecord.VALTYPE_UINT64, 2**64-1, 12, 43, 5)
        rec_data = hex_to_bindata("0C000000 2B000000 00000002 0500 0800 D2040000")
        lsd_data = hex_to_bindata("FFFF FFFF FFFF FFFF")
        self._run_test_read_write_record_with_lsd(record, rec_data, lsd_pos, lsd_data)

    def test_read_write_arrayint32(self):
        arr = []
        lsd_pos = (1234, 0)
        record = HcrRecord(HcrRecord.VALTYPE_ARRAY_INT32, arr, 12, 43, 5)
        rec_data = hex_to_bindata("0C000000 2B000000 00000400 0500 0000 D2040000")
        lsd_data = ""
        self._run_test_read_write_record_with_lsd(record, rec_data, lsd_pos, lsd_data)

        arr = [1234]
        lsd_pos = (1234, 4)
        record = HcrRecord(HcrRecord.VALTYPE_ARRAY_INT32, arr, 12, 43, 5)
        rec_data = hex_to_bindata("0C000000 2B000000 00000400 0500 0400 D2040000")
        lsd_data = hex_to_bindata("D2040000")
        self._run_test_read_write_record_with_lsd(record, rec_data, lsd_pos, lsd_data)

        arr = [-2**31, 0, 1234567890, 2**31-1]
        lsd_pos = (1234, 4*3)
        record = HcrRecord(HcrRecord.VALTYPE_ARRAY_INT32, arr, 12, 43, 5)
        rec_data = hex_to_bindata("0C000000 2B000000 00000400 0500 0C00 D2040000")
        lsd_data = hex_to_bindata("00000080 00000000 D2029649 FFFFFF7F")
        self._run_test_read_write_record_with_lsd(record, rec_data, lsd_pos, lsd_data)
    
    def test_read_write_arrayuint32(self):
        arr = []
        lsd_pos = (1234, 0)
        record = HcrRecord(HcrRecord.VALTYPE_ARRAY_UINT32, arr, 12, 43, 5)
        rec_data = hex_to_bindata("0C000000 2B000000 00000800 0500 0000 D2040000")
        lsd_data = ""
        self._run_test_read_write_record_with_lsd(record, rec_data, lsd_pos, lsd_data)

        arr = [1234]
        lsd_pos = (1234, 4)
        record = HcrRecord(HcrRecord.VALTYPE_ARRAY_UINT32, arr, 12, 43, 5)
        rec_data = hex_to_bindata("0C000000 2B000000 00000800 0500 0400 D2040000")
        lsd_data = hex_to_bindata("D2040000")
        self._run_test_read_write_record_with_lsd(record, rec_data, lsd_pos, lsd_data)

        arr = [0, 3123456789, 2**32-1]
        lsd_pos = (1234, 4*3)
        record = HcrRecord(HcrRecord.VALTYPE_ARRAY_UINT32, arr, 12, 43, 5)
        rec_data = hex_to_bindata("0C000000 2B000000 00000800 0500 0C00 D2040000")
        lsd_data = hex_to_bindata("00000000 152B2CBA FFFFFFFF")
        self._run_test_read_write_record_with_lsd(record, rec_data, lsd_pos, lsd_data)

    def test_read_write_text8(self):
        string = ''
        lsd_pos = (1234, 0)
        record = HcrRecord(HcrRecord.VALTYPE_TEXT8, string, 12, 43, 5)
        rec_data = hex_to_bindata("0C000000 2B000000 00000200 0500 0000 D2040000")
        lsd_data = ""
        self._run_test_read_write_record_with_lsd(record, rec_data, lsd_pos, lsd_data)

        string = 'Hello world!!'
        lsd_pos = (1234, 13)
        record = HcrRecord(HcrRecord.VALTYPE_TEXT8, string, 12, 43, 5)
        rec_data = hex_to_bindata("0C000000 2B000000 00000200 0500 0D00 D2040000")
        lsd_data = "Hello world!!"
        self._run_test_read_write_record_with_lsd(record, rec_data, lsd_pos, lsd_data)

        string = u'Cost 100€'
        lsd_pos = (1234, 11)
        record = HcrRecord(HcrRecord.VALTYPE_TEXT8, string, 12, 43, 5)
        rec_data = hex_to_bindata("0C000000 2B000000 00000200 0500 0B00 D2040000")
        lsd_data = "Cost 100" + hex_to_bindata("E2 82 AC")
        self._run_test_read_write_record_with_lsd(record, rec_data, lsd_pos, lsd_data)
    
    def test_read_write_bindata(self):
        data = ''
        lsd_pos = (1234, 0)
        record = HcrRecord(HcrRecord.VALTYPE_BIN_DATA, data, 12, 43, 5)
        rec_data = hex_to_bindata("0C000000 2B000000 00000100 0500 0000 D2040000")
        lsd_data = ""
        self._run_test_read_write_record_with_lsd(record, rec_data, lsd_pos, lsd_data)

        data = hex_to_bindata('00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF')
        lsd_pos = (1234, 16)
        record = HcrRecord(HcrRecord.VALTYPE_BIN_DATA, data, 12, 43, 5)
        rec_data = hex_to_bindata("0C000000 2B000000 00000100 0500 1000 D2040000")
        lsd_data = hex_to_bindata('00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF')
        self._run_test_read_write_record_with_lsd(record, rec_data, lsd_pos, lsd_data)
        
