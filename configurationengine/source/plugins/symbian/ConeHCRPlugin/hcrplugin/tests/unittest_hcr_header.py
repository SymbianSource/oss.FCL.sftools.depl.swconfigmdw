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
import os, shutil
import sys
import __init__

from testautomation.utils import hex_to_bindata

from hcrplugin import hcr_header
from hcrplugin.hcr_exceptions import InvalidHcrHeaderError


ROOT_PATH = os.path.dirname(os.path.abspath(__file__))


class TestHCRHeader(unittest.TestCase):
    def test_hcr_header_dumps_empty(self):
        hcrh = hcr_header.HcrHeader()
        self.assertEquals(len(hcrh.dumps()), 32)
        expected_data = hex_to_bindata(
            "48435266 0000 0000 00000000 00000000"+\
            "00000000 000000000000000000000000")
        self.assertEquals(hcrh.dumps(), expected_data)

    def test_hcr_header_loads_empty(self):
        hcrh = hcr_header.HcrHeader()
        try:
            hcrh.loads('')
            self.fail('parsing of empty string succeeded?')
        except InvalidHcrHeaderError:
            pass

    def test_hcr_header_loads_invalid_signature(self):
        hcrh = hcr_header.HcrHeader()
        try:
            hcrh.loads(32*' ')
            self.fail('parsing of empty string succeeded?')
        except InvalidHcrHeaderError:
            pass

    def test_hcr_header_loads_zero(self):
        hcrh = hcr_header.HcrHeader()
        header_data = hex_to_bindata(
            "48435266 0000 0000 00000000 00000000"+\
            "00000000 000000000000000000000000")
        hcrh.loads(header_data)
        self.assertEquals(hcrh.version, 0)
        self.assertEquals(hcrh.flags, 0)
        self.assertEquals(hcrh.nrecords, 0)
        self.assertEquals(hcrh.lsd_offset, 0)
        self.assertEquals(hcrh.lsd_size, 0)

    def test_hcr_header_dumps_some_data(self):
        hcrh = hcr_header.HcrHeader()
        hcrh.version = 5
        hcrh.flags = 6
        hcrh.nrecords = 10
        hcrh.lsd_offset = 18
        hcrh.lsd_size = 32
        expected_data = hex_to_bindata(
            "48435266 0500 0600 0A000000 12000000"+\
            "20000000 000000000000000000000000")
        self.assertEquals(hcrh.dumps(), expected_data)

    def test_hcr_header_loads_some_data(self):
        hcrh = hcr_header.HcrHeader()
        header_data = hex_to_bindata(
            "48435266 0500 0600 0A000000 12000000"+\
            "20000000 000000000000000000000000")
        hcrh.loads(header_data)
        self.assertEquals(hcrh.version, 5)
        self.assertEquals(hcrh.flags, 6)
        self.assertEquals(hcrh.nrecords, 10)
        self.assertEquals(hcrh.lsd_offset, 18)
        self.assertEquals(hcrh.lsd_size, 32)
