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
import os, shutil, random
import sys
import __init__

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

from testautomation.utils import hex_to_bindata

from hcrplugin.hcrrepository import HcrRepository, HcrRecord
from hcrplugin.hcr_writer import HcrWriter
from hcrplugin.hcr_reader import HcrReader
from hcrplugin import hcr_exceptions

class TestReadWriteHcrRepository(unittest.TestCase):

    def setUp(self):
        self.writer = HcrWriter()
        self.reader = HcrReader()

    def write_repo_assertion_failure_files(self, actual_data, expected_data, failure_report_dir, filename):
        dir = os.path.join(ROOT_PATH, 'temp/repo_assertion_failure')
        dir = os.path.normpath(os.path.join(dir, failure_report_dir))
        if not os.path.exists(dir):
            os.makedirs(dir)
        
        f = open(os.path.join(dir, "actual_" + filename), "wb")
        try:        f.write(actual_data)
        finally:    f.close()
        
        f = open(os.path.join(dir, "expected_" + filename), "wb")
        try:        f.write(expected_data)
        finally:    f.close()
        
        return dir
    
    def _run_test_read_write_repository(self, repo, repo_data, failure_report_dir):
        """
        Test reading and writing the repository using the given data.
        
        In case of a failure, the actual and expected data are written
        to the given directory, so that they can be compared using e.g.
        Beyond Compare.
        
        @param repo: The repository object to test.
        @param repo_data: The expected binary data corresponding to the repository object.
        @param failure_report_dir: The directory where files are written in case of
            a failure. Note that this should be just e.g. 'empty_repo', the parent dirs
            are appended automatically.
        """
        # Test writing
        expected_data = repo_data
        actual_data = self.writer.get_repository_bindata(repo)
        if actual_data != expected_data:
            dir = self.write_repo_assertion_failure_files(
                actual_data, expected_data,
                failure_report_dir, 'repo.dat')
            self.fail("Actual and expected repository data are not equal!\n"+\
                "See the files in '%s'" % dir)
        
        
        # Test reading
        expected_repo = repo
        actual_repo = self.reader.parse_repository_from_bindata(repo_data)
        if actual_repo != expected_repo:
            dir = self.write_repo_assertion_failure_files(
                repr(actual_repo), repr(expected_repo),
                failure_report_dir, 'repo.txt')
            self.fail("Actual and expected repository objects are not equal!\n"+\
                "See the files in '%s'" % dir)
    
    # -------------------------------------------------------------------------
    #
    # -------------------------------------------------------------------------
    
    def test_read_write_empty_repository_1(self):
        repo = HcrRepository([], version=2, flags=3)
        repo_data = hex_to_bindata(
            "48435266 0200 0300 00000000 20000000"+\
            "00000000 000000000000000000000000")
        
        self._run_test_read_write_repository(repo, repo_data, 'empty_repo_1')
        
    def test_read_write_empty_repository_2(self):    
        repo = HcrRepository([], version=0xBEEF, flags=0xCAFE)
        repo_data = hex_to_bindata(
            "48435266 EFBE FECA 00000000 20000000"+\
            "00000000 000000000000000000000000")
        
        self._run_test_read_write_repository(repo, repo_data, 'empty_repo_2')
    
    # -------------------------------------------------------------------------
    #
    # -------------------------------------------------------------------------
    
    def test_read_write_repository_without_lsd(self):
        records = [
            HcrRecord(HcrRecord.VALTYPE_BOOL,       True,        1, 1, 0),
            HcrRecord(HcrRecord.VALTYPE_INT8,       -123,        1, 2, 0),
            HcrRecord(HcrRecord.VALTYPE_UINT8,      204,         1, 3, 0),
            HcrRecord(HcrRecord.VALTYPE_INT16,      -13423,      2, 1, 0),
            HcrRecord(HcrRecord.VALTYPE_UINT16,     54321,       2, 2, 0),
            HcrRecord(HcrRecord.VALTYPE_INT32,      -1000000000, 2, 3, 0),
            HcrRecord(HcrRecord.VALTYPE_UINT32,     4000000000,  3, 1, 0),
            HcrRecord(HcrRecord.VALTYPE_LIN_ADDR,   0xAABBCCDD,  3, 2, 0),
        ]
        # Shuffle the records to make sure that they are sorted properly when writing
        random.shuffle(records)
        repo = HcrRepository(records, version=2, flags=3)
        
        h = hex_to_bindata
        data = [
            # Header
            h("48435266 0200 0300 08000000 C0000000"),
            h("00000000 000000000000000000000000"),
            # Record section
            h("01000000 01000000 08000000 0000 0000 01000000"), # bool
            h("01000000 02000000 04000000 0000 0000 85FFFFFF"), # int8
            h("01000000 03000000 40000000 0000 0000 CC000000"), # uint8
            h("02000000 01000000 02000000 0000 0000 91CBFFFF"), # int16
            h("02000000 02000000 20000000 0000 0000 31D40000"), # uint16
            h("02000000 03000000 01000000 0000 0000 003665C4"), # int32
            h("03000000 01000000 10000000 0000 0000 00286BEE"), # uint32
            h("03000000 02000000 00010000 0000 0000 DDCCBBAA"), # linaddr
        ]
        repo_data = ''.join(data)
        
        self._run_test_read_write_repository(repo, repo_data, 'repo_without_lsd')
    
    # -------------------------------------------------------------------------
    #
    # -------------------------------------------------------------------------
    
    def test_read_write_repository_with_lsd(self):
        records = [
            HcrRecord(HcrRecord.VALTYPE_INT64,        9211026413402420220,  1, 1, 0),
            HcrRecord(HcrRecord.VALTYPE_UINT64,       10746170304040729876, 1, 2, 0),
            HcrRecord(HcrRecord.VALTYPE_TEXT8,        u'Cost 100€',         1, 3, 0),
            HcrRecord(HcrRecord.VALTYPE_BIN_DATA,     'test test',          2, 1, 0),
            HcrRecord(HcrRecord.VALTYPE_ARRAY_INT32,  [-2**31, 0, 2**31-1], 2, 2, 0),
            HcrRecord(HcrRecord.VALTYPE_ARRAY_UINT32, [0, 100000, 2**32-1], 2, 3, 0),
        ]
        # Shuffle the records to make sure that they are sorted properly when writing
        random.shuffle(records)
        repo = HcrRepository(records, version=2, flags=3)
        
        
        # Record section size: 6 * 20 = 120
        # LSD offset: 32 + 120 = 152
        # LSD size:   8 + 8 + 12 + 12 + 12 + 12 = 64
        h = hex_to_bindata
        data = [
            # Header
            h("48435266 0200 0300 06000000 98000000"),
            h("40000000 000000000000000000000000"),
            # Record section
            h("01000000 01000000 00000001 0000 0800 00000000"), # int64, lsd pos = (0, 8)
            h("01000000 02000000 00000002 0000 0800 08000000"), # uint64, lsd pos = (8, 8)
            h("01000000 03000000 00000200 0000 0B00 10000000"), # text8, lsd pos = (8 + 8, 11)
            h("02000000 01000000 00000100 0000 0900 1C000000"), # bindata, lsd pos = (8 + 8 + 12, 9)
            h("02000000 02000000 00000400 0000 0C00 28000000"), # arrayint32, lsd pos = (8 + 8 + 12 + 12, 12)
            h("02000000 03000000 00000800 0000 0C00 34000000"), # arrayuint32, lsd pos = (8 + 8 + 12 + 12 + 12, 12)
            # LSD section
            h("FC73 978B B823 D47F"),          # 8 bytes
            h("14FD 32B4 F410 2295"),          # 8 bytes
            "Cost 100" + h("E2 82 AC 00"),     # 12 bytes
            "test test" + h("00 00 00"),       # 12 bytes
            h("00000080 00000000 FFFFFF7F"),   # 12 bytes
            h("00000000 A0860100 FFFFFFFF"),   # 12 bytes
        ]
        
        repo_data = ''.join(data)
        
        self._run_test_read_write_repository(repo, repo_data, 'repo_with_lsd')
    
    # -------------------------------------------------------------------------
    #
    # -------------------------------------------------------------------------
    
    def test_read_write_repository_with_all_record_types(self):
        records = [
            HcrRecord(HcrRecord.VALTYPE_BOOL,         True,                 1, 1, 0),
            HcrRecord(HcrRecord.VALTYPE_INT8,         -123,                 1, 2, 0),
            HcrRecord(HcrRecord.VALTYPE_UINT8,        204,                  1, 3, 0),
            HcrRecord(HcrRecord.VALTYPE_INT16,        -13423,               2, 1, 0),
            HcrRecord(HcrRecord.VALTYPE_UINT16,       54321,                2, 2, 0),
            HcrRecord(HcrRecord.VALTYPE_INT32,        -1000000000,          2, 3, 0),
            HcrRecord(HcrRecord.VALTYPE_UINT32,       4000000000,           3, 1, 0),
            HcrRecord(HcrRecord.VALTYPE_LIN_ADDR,     0xAABBCCDD,           3, 2, 0),
            
            HcrRecord(HcrRecord.VALTYPE_INT64,        9211026413402420220,  4, 1, 0),
            HcrRecord(HcrRecord.VALTYPE_UINT64,       10746170304040729876, 4, 2, 0),
            HcrRecord(HcrRecord.VALTYPE_TEXT8,        u'Cost 100€',         4, 3, 0),
            HcrRecord(HcrRecord.VALTYPE_TEXT8,        '',                   5, 1, 0),
            HcrRecord(HcrRecord.VALTYPE_BIN_DATA,     'test test',          5, 2, 0),
            HcrRecord(HcrRecord.VALTYPE_BIN_DATA,     '',                   5, 3, 0),
            HcrRecord(HcrRecord.VALTYPE_ARRAY_INT32,  [-2**31, 0, 2**31-1], 6, 1, 0),
            HcrRecord(HcrRecord.VALTYPE_ARRAY_INT32,  [],                   6, 2, 0),
            HcrRecord(HcrRecord.VALTYPE_ARRAY_UINT32, [0, 100000, 2**32-1], 6, 3, 0),
            HcrRecord(HcrRecord.VALTYPE_ARRAY_UINT32, [],                   7, 1, 0),
            
            HcrRecord(HcrRecord.VALTYPE_BOOL,         False,                8, 1, 0),
            HcrRecord(HcrRecord.VALTYPE_TEXT8,        u'Hello world!!!',    8, 2, 0),
            HcrRecord(HcrRecord.VALTYPE_TEXT8,        u'unpadded',          8, 3, 0),
        ]
        # Shuffle the records to make sure that they are sorted properly when writing
        random.shuffle(records)
        repo = HcrRepository(records, version=2, flags=3)
        
        # Record section size: 21 * 20 = 420
        # LSD offset: 32 + 420 = 452
        # LSD size:   8 + 8 + 12 + 12 + 12 + 12 + 16 + 8 = 88
        h = hex_to_bindata
        data = [
            # Header
            h("48435266 0200 0300 15000000 C4010000"),
            h("58000000 000000000000000000000000"),
            
            # Record section
            h("01000000 01000000 08000000 0000 0000 01000000"), # bool
            h("01000000 02000000 04000000 0000 0000 85FFFFFF"), # int8
            h("01000000 03000000 40000000 0000 0000 CC000000"), # uint8
            h("02000000 01000000 02000000 0000 0000 91CBFFFF"), # int16
            h("02000000 02000000 20000000 0000 0000 31D40000"), # uint16
            h("02000000 03000000 01000000 0000 0000 003665C4"), # int32
            h("03000000 01000000 10000000 0000 0000 00286BEE"), # uint32
            h("03000000 02000000 00010000 0000 0000 DDCCBBAA"), # linaddr
            
            h("04000000 01000000 00000001 0000 0800 00000000"), # int64, lsd pos = (0, 8)
            h("04000000 02000000 00000002 0000 0800 08000000"), # uint64, lsd pos = (8, 8)
            h("04000000 03000000 00000200 0000 0B00 10000000"), # text8, lsd pos = (8 + 8, 11)
            h("05000000 01000000 00000200 0000 0000 1C000000"), # text8, lsd pos = (8 + 8 + 12, 0)
            h("05000000 02000000 00000100 0000 0900 1C000000"), # bindata, lsd pos = (8 + 8 + 12, 9)
            h("05000000 03000000 00000100 0000 0000 28000000"), # bindata, lsd pos = (8 + 8 + 12 + 12, 0)
            h("06000000 01000000 00000400 0000 0C00 28000000"), # arrayint32, lsd pos = (8 + 8 + 12 + 12, 12)
            h("06000000 02000000 00000400 0000 0000 34000000"), # arrayint32, lsd pos = (8 + 8 + 12 + 12 + 12, 0)
            h("06000000 03000000 00000800 0000 0C00 34000000"), # arrayuint32, lsd pos = (8 + 8 + 12 + 12 + 12, 12)
            h("07000000 01000000 00000800 0000 0000 40000000"), # arrayuint32, lsd pos = (8 + 8 + 12 + 12 + 12 + 12, 0)
            
            h("08000000 01000000 08000000 0000 0000 00000000"), # bool
            h("08000000 02000000 00000200 0000 0E00 40000000"), # text8, lsd pos = (8 + 8 + 12 + 12 + 12 + 12, 14)
            h("08000000 03000000 00000200 0000 0800 50000000"), # text8, lsd pos = (8 + 8 + 12 + 12 + 12 + 12 + 16, 8)
            
            # LSD section
            h("FC73 978B B823 D47F"),          # 8 bytes
            h("14FD 32B4 F410 2295"),          # 8 bytes
            "Cost 100" + h("E2 82 AC 00"),     # 12 bytes
            "",
            "test test" + h("00 00 00"),       # 12 bytes
            "",
            h("00000080 00000000 FFFFFF7F"),   # 12 bytes
            "",
            h("00000000 A0860100 FFFFFFFF"),   # 12 bytes
            "",
            "Hello world!!!" + h("00 00"),     # 16 bytes
            "unpadded",                        # 8 bytes
        ]
        repo_data = ''.join(data)
        
        self._run_test_read_write_repository(repo, repo_data, 'repo_with_all_record_types')
