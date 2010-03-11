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
from testautomation import utils

class TestHexToBinData(unittest.TestCase):
    def test_hex_to_bindata(self):
        try:    utils.hex_to_bindata('102')
        except ValueError: pass
        
        try:    utils.hex_to_bindata('asdfgh')
        except ValueError: pass
        
        self.assertEquals(utils.hex_to_bindata('  00 11 22 33 44 55 66 77 88 99 aA bB cC dD eE fF   '),
                          '\x00\x11\x22\x33\x44\x55\x66\x77\x88\x99\xaa\xbb\xcc\xdd\xee\xff')
        
        DATA = """
        00 11 22 33 44 55
        66 77 88 99
        aA bB cC dD eE fF
        """
        self.assertEquals(utils.hex_to_bindata(DATA),
                          '\x00\x11\x22\x33\x44\x55\x66\x77\x88\x99\xaa\xbb\xcc\xdd\xee\xff')
