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

import logging
import __init__
  

from struct import pack, unpack

from cone.public import exceptions,plugin,utils,api
from hcrplugin.hcrrepository import HcrRecord
from hcrplugin.hcr_exceptions import *
from hcrplugin.hcr_header import HcrHeader

# Dictionary for mapping the HCRML value types to their
# implementation values
VALUE_TYPE_MAP = {
    HcrRecord.VALTYPE_INT32         : 0x00000001,
    HcrRecord.VALTYPE_INT16         : 0x00000002,
    HcrRecord.VALTYPE_INT8          : 0x00000004,
    HcrRecord.VALTYPE_BOOL          : 0x00000008,
    HcrRecord.VALTYPE_UINT32        : 0x00000010,
    HcrRecord.VALTYPE_UINT16        : 0x00000020,
    HcrRecord.VALTYPE_UINT8         : 0x00000040,
    HcrRecord.VALTYPE_LIN_ADDR      : 0x00000100,
    HcrRecord.VALTYPE_BIN_DATA      : 0x00010000,
    HcrRecord.VALTYPE_TEXT8         : 0x00020000,
    HcrRecord.VALTYPE_ARRAY_INT32   : 0x00040000,
    HcrRecord.VALTYPE_ARRAY_UINT32  : 0x00080000,
    HcrRecord.VALTYPE_INT64         : 0x01000000,
    HcrRecord.VALTYPE_UINT64        : 0x02000000,
    }


VALUE_TYPES_WITH_LSD = [
    HcrRecord.VALTYPE_BIN_DATA,
    HcrRecord.VALTYPE_TEXT8,
    HcrRecord.VALTYPE_ARRAY_INT32,
    HcrRecord.VALTYPE_ARRAY_UINT32,
    HcrRecord.VALTYPE_INT64,
    HcrRecord.VALTYPE_UINT64
    ]

VALUE_TYPES_UNSIGNED_INT = [
    HcrRecord.VALTYPE_UINT32,
    HcrRecord.VALTYPE_UINT16,
    HcrRecord.VALTYPE_UINT8,
    HcrRecord.VALTYPE_LIN_ADDR,
    HcrRecord.VALTYPE_UINT64,
    ]

NUMERIC_VALUE_RANGES = {
    HcrRecord.VALTYPE_INT32         : (-2**31,  2**31-1),
    HcrRecord.VALTYPE_INT16         : (-2**15,  2**15-1),
    HcrRecord.VALTYPE_INT8          : (-2**7,   2**7-1),
    HcrRecord.VALTYPE_UINT32        : (0,       2**32-1),
    HcrRecord.VALTYPE_UINT16        : (0,       2**16-1),
    HcrRecord.VALTYPE_UINT8         : (0,       2**8-1),
    HcrRecord.VALTYPE_LIN_ADDR      : (0,       2**32-1),
    HcrRecord.VALTYPE_INT64         : (-2**63,  2**63-1),
    HcrRecord.VALTYPE_UINT64        : (0,       2**64-1),
    HcrRecord.VALTYPE_ARRAY_INT32   : (-2**31,  2**31-1),
    HcrRecord.VALTYPE_ARRAY_UINT32  : (0,       2**32-1),
}



class HcrWriter(object):
    
    # Maximum size of LSD section data for one record
    LSD_MAX_SIZE_PER_RECORD = 512
    
    def get_record_setting_id(self, record):
        """
        Return the setting ID value used for sorting the records in the repository.
        """
        return (record.category_id, record.element_id)
    
    def get_repository_bindata(self, repository):
        """
        @return: The binary data to write into a file for the given repository.
        """
        dup_ids = repository.get_duplicate_record_ids()
        if len(dup_ids) > 0:
            raise DuplicateRecordError("The repository contains the following duplicate records (category ID, element ID): %r" % dup_ids)
        
        header_data   = None
        header_size   = 32
        record_data   = []
        records_size  = 0
        lsd_data      = []
        lsd_size      = 0
        lsd_offset    = None
        
        # Generate the record and LSD section data
        records = sorted(repository.records, key=self.get_record_setting_id)
        for record in records:
            lsd_pos = None
            lsd = self.get_record_lsd_bindata(record)
            if lsd != None:
                # Store the position before adding the padding,
                # because it shouldn't include the padding bytes
                lsd_pos = (lsd_size, len(lsd))
                lsd += self._get_padding(len(lsd))
                lsd_data.append(lsd)
                lsd_size += len(lsd)
            
            rdata = self.get_record_bindata(record, lsd_pos)
            record_data.append(rdata)
            records_size += len(rdata)
        
        lsd_offset = header_size + records_size
        
        header = HcrHeader()
        header.version = repository.version
        header.flags = repository.flags
        header.nrecords = len(repository.records)
        header.lsd_offset = lsd_offset
        header.lsd_size = lsd_size
        
        header_data = header.dumps()
        if len(header_data) != header_size:
            raise RuntimeError("Internal logic error! Header size is %d and not %d as it should be!" % (len(header_data), header_size))
        
        output = []
        output.append(header_data)
        output.extend(record_data)
        output.extend(lsd_data)
        output = ''.join(output)
        if len(output) % 4 != 0:
            raise RuntimeError("Internal logic error! Output size is not divisible by 4 (%d)" % (len(output)))
        
        return output
    
    def _get_padding(self, size, padding_char='\x00'):
        if size % 4 == 0:   amount = 0
        else:               amount = 4 - (size % 4)
        return amount * padding_char
    
    
    def get_record_bindata(self, record, lsd_pos=None):
        """
        @param lsd_pos: The position of the record's data in the Large
            Setting Data section. Should be a tuple: (offset, size).
        @return: The binary data to write for the given record object.
        """
        self._check_value_range(record)
        
        if record.type in VALUE_TYPES_WITH_LSD:
            RECORD_FMT = "<IIIHHI"
            return pack(RECORD_FMT,record.category_id,record.element_id,VALUE_TYPE_MAP[record.type],record.flags,lsd_pos[1],lsd_pos[0])
        else:
            if record.type in VALUE_TYPES_UNSIGNED_INT:
                RECORD_FMT = "<IIIHHI"
            else:
                RECORD_FMT = "<IIIHHi"
            return pack(RECORD_FMT,record.category_id,record.element_id,VALUE_TYPE_MAP[record.type],record.flags,0,record.value)
        
    
    def get_record_lsd_bindata(self, record):
        """
        @return: The binary data to write into the Large Setting Data
            section for the given setting, or None if an entry in the
            LSD section is not necessary.
        """
        result = None
        
        if record.type == HcrRecord.VALTYPE_TEXT8:
            result = record.value.encode("utf-8")
        
        elif record.type == HcrRecord.VALTYPE_BIN_DATA:
            result = record.value 

        elif record.type == HcrRecord.VALTYPE_ARRAY_INT32:
            result = pack("<%di"%len(record.value),*record.value)

        elif record.type == HcrRecord.VALTYPE_ARRAY_UINT32:
            result = pack("<%dI"%len(record.value),*record.value)

        elif record.type == HcrRecord.VALTYPE_INT64:
            result = pack("<q",record.value)

        elif record.type == HcrRecord.VALTYPE_UINT64:
            result = pack("<Q",record.value)
        
        if result != None:
            if len(result) > self.LSD_MAX_SIZE_PER_RECORD:
                msg = "Data size for value in record (category=%d, element=%d) is too large: size %d bytes, but maximum is %d bytes" \
                    % (record.category_id, record.element_id, len(result), self.LSD_MAX_SIZE_PER_RECORD)
                raise TooLargeLsdDataError(msg)
        return result
    
    def _check_value_range(self, record):
        if record.type in NUMERIC_VALUE_RANGES:
            range = NUMERIC_VALUE_RANGES[record.type]
            
            values = record.value
            if not isinstance(values, list): values = [values]
            
            for val in values:
                if val < range[0] or val > range[1]:
                    msg = "Value in record (category=%d, element=%d) is invalid for its type ('%s'): %d is not in the range %d-%d" \
                        % (record.category_id, record.element_id, record.type, val, range[0], range[1])
                    raise ValueNotInRangeError(msg)
