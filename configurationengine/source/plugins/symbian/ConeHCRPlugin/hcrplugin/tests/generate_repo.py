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
Script for generating expected data for the tests where output
is written to a file.
"""

import os, unittest

from testautomation.utils import hex_to_bindata

from hcrplugin.hcrrepository import HcrRepository, HcrRecord
from hcrplugin.hcr_writer import HcrWriter
from hcrplugin import hcr_exceptions
    
def generate_repository(file_path, records):
    dir = os.path.dirname(file_path)
    if dir != '' and not os.path.exists(dir):
        os.makedirs(dir)
    
    writer = HcrWriter()
    repo = HcrRepository(records)
    f = open(file_path, "wb")
    try:        f.write(writer.get_repository_bindata(repo))
    finally:    f.close()
    
    print "Generated '%s' with %d records" % (file_path, len(records))

def generate_expected_data():
    records = []
    category = 0x10001234
    records.append(HcrRecord(HcrRecord.VALTYPE_INT32, 0, category, 0))
    records.append(HcrRecord(HcrRecord.VALTYPE_INT32, 0, category, 1))
    records.append(HcrRecord(HcrRecord.VALTYPE_INT32, 0, category, 2))

    generate_repository("generated/expected/project/hcr.dat", records)
    
    # --------------------------------------------------------------
    
    records = []
    category = 0x10001234
    records.append(HcrRecord(HcrRecord.VALTYPE_INT8, 125, category, 0))
    records.append(HcrRecord(HcrRecord.VALTYPE_UINT32, 4000000000, category, 1))
    records.append(HcrRecord(HcrRecord.VALTYPE_ARRAY_INT32, [-1, -20, -300, -4000, -50000], category, 2))
    records.append(HcrRecord(HcrRecord.VALTYPE_BIN_DATA, hex_to_bindata('00112233 DEADBEEF CAFE 50'), category, 3))
    
    category = 0x20001234
    records.append(HcrRecord(HcrRecord.VALTYPE_LIN_ADDR, 0x10203040, category, 0))
    records.append(HcrRecord(HcrRecord.VALTYPE_INT64, 1234567890123456789, category, 1))
    records.append(HcrRecord(HcrRecord.VALTYPE_ARRAY_UINT32, [1, 20, 300, 4000, 50000], category, 2))
    records.append(HcrRecord(HcrRecord.VALTYPE_TEXT8, u'100\u20ac', category, 3))
    
    category = 0x30001234
    records.append(HcrRecord(HcrRecord.VALTYPE_BOOL, False, category, 0))

    generate_repository("generated/expected/multifile_project/hcr.dat", records)

if __name__ == "__main__":
    generate_expected_data()
