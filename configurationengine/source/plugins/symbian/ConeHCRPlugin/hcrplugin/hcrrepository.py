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



class HcrRepository(object):
    FLAG_READ_ONLY    = 1
    FLAG_NON_VOLATILE = 2
    FLAG_BOOT_ONLY    = 4
    
    def __init__(self, records, version=1, flags=FLAG_READ_ONLY):
        self.records = records
        self.version = version
        self.flags   = flags
    
    def count_records(self, category_id, element_id):
        """
        Return the number of records in the repository with the given
        setting ID (category ID - element ID pair).
        """
        count = 0
        for r in self.records:
            if r.category_id == category_id and r.element_id == element_id:
                count += 1
        return count
    
    def get_duplicate_record_ids(self):
        """
        Return a list of duplicate record IDs in the repository.
        The list contains tuples of the form (category_id, element_id).
        """
        result = []
        for r in self.records:
            count = self.count_records(r.category_id, r.element_id)
            record_id = (r.category_id, r.element_id)
            if count > 1 and record_id not in result:
                result.append(record_id)
        return result
    
    def __repr__(self):
        buf = ["HcrRepository(version=%r, flags=%r, records=[" % (self.version, self.flags)]
        if len(self.records) > 0:
            buf.append('\n')
            for record in sorted(self.records):
                buf.append("    %r,\n" % record)
        buf.append('])')
        return ''.join(buf)
    
    def __eq__(self, other):
        return sorted(self.records) == sorted(other.records) \
            and self.version == other.version \
            and self.flags == other.flags
    
    def __ne__(self, other):
        return not self.__eq__(other)

class HcrRecord(object):
    # Record value types used in HCRML
    VALTYPE_INT32           = 'int32'
    VALTYPE_INT16           = 'int16'
    VALTYPE_INT8            = 'int8'
    VALTYPE_BOOL            = 'bool'
    VALTYPE_UINT32          = 'uint32'
    VALTYPE_UINT16          = 'uint16'
    VALTYPE_UINT8           = 'uint8'
    VALTYPE_LIN_ADDR        = 'linaddr'
    VALTYPE_BIN_DATA        = 'bindata'
    VALTYPE_TEXT8           = 'text8'
    VALTYPE_ARRAY_INT32     = 'arrayint32'
    VALTYPE_ARRAY_UINT32    = 'arrayuint32'
    VALTYPE_INT64           = 'int64'
    VALTYPE_UINT64          = 'uint64'
    
    FLAG_UNINITIALIZED = 1
    FLAG_MODIFIABLE    = 2
    FLAG_PERSISTENT    = 4


    def __init__(self, type, value, category_id, element_id, flags=0):
        # Check the value type
        val_types = []
        for name, val in self.__class__.__dict__.iteritems():
            if name.startswith('VALTYPE_'):
                val_types.append(val)
        if type not in val_types:
            raise ValueError("Invalid HCRML record type '%s'" % type)
        
        self.type           = type
        self.value          = value
        self.category_id    = category_id
        self.element_id     = element_id
        self.flags          = flags

    def __repr__(self):
        return 'HcrRecord(type=%r, value=%r, category_id=%r, element_id=%r, flags=%r)' \
            % (self.type, self.value, self.category_id, self.element_id, self.flags)
    
    def __lt__(self, other):
        # Note:
        # The < operator is implemented purely for the sake of sorting records
        # in unit tests for comparison, the sorting is NOT the one used when
        # actually writing the records to file
        attrs_to_check = ['type', 'value', 'category_id', 'element_id', 'flags']
        for attr_name in attrs_to_check:
            x = getattr(self, attr_name)
            y = getattr(other, attr_name)
            if x < y:       return True
            elif x == y:    continue # Equal, so need to check the next one
            else:           return False
        return False
    
    def __eq__(self, other):
        attrs_to_check = ['type', 'value', 'category_id', 'element_id', 'flags']
        for attr_name in attrs_to_check:
            x = getattr(self, attr_name)
            y = getattr(other, attr_name)
            if x != y: return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)
