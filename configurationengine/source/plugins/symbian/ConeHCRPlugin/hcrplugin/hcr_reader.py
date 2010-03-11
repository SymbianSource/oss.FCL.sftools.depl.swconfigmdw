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
from hcrplugin.hcrrepository import HcrRecord, HcrRepository
from struct import pack, unpack
from hcrplugin.hcr_writer import VALUE_TYPE_MAP,VALUE_TYPES_WITH_LSD,VALUE_TYPES_UNSIGNED_INT
from hcrplugin.hcr_header import HcrHeader
from hcrplugin.hcr_exceptions import *


class HcrReader(object):
    
    def parse_repository_from_bindata(self, data):
        """
        @return: HcrRepository object constructed from the given binary data.
        """
        header_data = data[:32]
        header = HcrHeader()
        header.loads(header_data)
        
        expected_len = 32 + header.nrecords * 20 + header.lsd_size
        if len(data) < expected_len:
            raise InvalidHcrDataSizeError("File size is %d, expected at least %d based on header" \
                                          % (len(data), expected_len))
        
        expected_lsd_offset = 32 + header.nrecords * 20
        if header.lsd_offset != expected_lsd_offset: 
            raise InvalidLsdSectionOffsetError("LSD offset is %d, expected %d" \
                                               % (header.lsd_offset, expected_lsd_offset))
        
        records = []
        for i in xrange(header.nrecords):
            record_offset =  32 + i * 20
            record_data = data[record_offset:record_offset+20]
            record,lsd_pos = self.parse_record_from_bindata(record_data)
            if lsd_pos != None:
                if lsd_pos[0] > header.lsd_size or (lsd_pos[0] + lsd_pos[1]) > header.lsd_size:
                    raise InvalidRecordLsdPositionError(
                        "LSD offset of record %d (category=%d, element=%d) is %r, but LSD section size is %d" \
                        % (i, record.category_id, record.element_id, lsd_pos, header.lsd_size))
                lsd_offset = lsd_pos[0] + header.lsd_offset
                lsd_data = data[lsd_offset:lsd_offset+lsd_pos[1]]
                record.value = self.parse_record_value_from_lsd_bindata(record.type,lsd_data)
            records.append(record)
                
        return HcrRepository(records,header.version,header.flags)

    def parse_record_from_bindata(self, data):
        """
        @return: Tuple: (record, lsd_pos) where
            record  = HcrRecord object constructed from the given binary data.
            lsd_pos = The position of the record's data in the LSD section in the
                      form of a tuple (offset, size), or None if the record does
                      not have any data in the LSD section.
        """
        
        if len(data) != 20:
            raise HcrReaderError("Invalid record length: %d, expected 20" % len(data))
        
        result = unpack("<IIIHH",data[:16])
        
        category_id = result[0]
        element_id = result[1]
        value_type = result[2]
        flag = result[3]
        lsd_len = result[4]
        
        
        
        for key,val in VALUE_TYPE_MAP.iteritems():
            if val == value_type:
                value_type = key
                break
        if value_type not in VALUE_TYPE_MAP:
            raise InvalidRecordValueTypeError("Invalid value type:%X" % value_type)
        
        value = None
        lsd_pos = None
        if value_type in VALUE_TYPES_WITH_LSD:
            lsd_offset = unpack("<I",data[16:])[0]
            lsd_pos = (lsd_offset,lsd_len)
        else:
            if value_type in VALUE_TYPES_UNSIGNED_INT:
                format = "<I"
            elif value_type == HcrRecord.VALTYPE_INT8:
                format = "<bxxx"
            elif value_type == HcrRecord.VALTYPE_INT16:
                format = "<hxx"
            else:
                format = "<i"
            
            value = unpack(format, data[16:])[0]
                
            if value_type == HcrRecord.VALTYPE_BOOL:
                value = bool(value)
                
            
        
        record = HcrRecord(value_type,value,category_id,element_id,flag)

        return record,lsd_pos
        
    
    def parse_record_value_from_lsd_bindata(self, record_type, data):
        """
        @return: The record value parsed from the given binary data in the LSD section.
        @param type: The HCRML type of the record whose LSD data is to be parsed.
        """
        if record_type == HcrRecord.VALTYPE_TEXT8:
            return data.decode("utf-8")
        
        elif record_type == HcrRecord.VALTYPE_BIN_DATA:
            return data 

        elif record_type == HcrRecord.VALTYPE_ARRAY_INT32:
            if len(data) % 4 != 0:
                raise InvalidRecordLsdPositionError("Int32 array requires an amount of LSD data that is divisible by 4 (data with size %d was given)" % len(data))
            return list(unpack("<%di"%(len(data)/4), data))

        elif record_type == HcrRecord.VALTYPE_ARRAY_UINT32:
            if len(data) % 4 != 0:
                raise InvalidRecordLsdPositionError("Uint32 array requires an amount of LSD data that is divisible by 4 (data with size %d was given)" % len(data))
            return list(unpack("<%dI"%(len(data)/4), data))

        elif record_type == HcrRecord.VALTYPE_INT64:
            if len(data) != 8:
                raise InvalidRecordLsdPositionError("Int64 requires LSD data size to be 8 bytes (%d given)" % len(data))
            return unpack("<q",data)[0]

        elif record_type == HcrRecord.VALTYPE_UINT64:
            if len(data) != 8:
                raise InvalidRecordLsdPositionError("Uint64 requires LSD data size to be 8 bytes (%d given)" % len(data))
            return unpack("<Q",data)[0]
        
        else:
            return None
