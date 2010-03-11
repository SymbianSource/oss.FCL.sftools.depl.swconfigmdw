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
import re
from cone.public import exceptions
import crml_reader
from crml_model import *

class CenRepEntry(object):
    """
    Class representing an entry in a CenRep text file.
    """
    def __init__(self, **kwargs):
        self.int            = kwargs.get('int')
        self.crml_type      = kwargs.get('crml_type')
        self.confml_type    = kwargs.get('confml_type')
        self.value          = kwargs.get('value')
        self.orig_value     = kwargs.get('orig_value')
        self.access         = kwargs.get('access')
        self.backup         = kwargs.get('backup', False)
    
    @property
    def metadata(self):
        return _get_metadata(self.backup)
    
    def __lt__(self, other):
        return crml_reader.convert_num(self.int) < crml_reader.convert_num(other.int)

class CenRepRfsRecord(object):
    """
    Class representing an entry in the CenRep RFS text file.
    """
    def __init__(self, repo_uid, key_uids=None):
        self.repo_uid = repo_uid
        self.key_uids = key_uids or []
    
    def __eq__(self, other):
        if type(self) == type(other):   return self.repo_uid == other.repo_uid
        else:                           return False
    
    def __ne__(self, other):
        return not (self == other)
    
    def __lt__(self, other):
        return  self.repo_uid < other.repo_uid
    
    def __repr__(self):
        return "CenRepRfsRecord(repo_uid=%s, key_uids=%r)" % (self.repo_uid, self.key_uids)
        

class CrmlTxtWriter(object):
    """
    Writer class for generating CenRep .txt files based on a CRML model.
    """
    
    def __init__(self, configuration, log):
        self.configuration = configuration
        self.log = log
    
    def get_cenrep_txt_data(self, repository):
        """
        Return the text data for the CenRep txt generated based on the given
        CRML repository model.
        @return: Text data for the CenRep text file.
        """
        data = []
        
        # Generate header lines 
        data.extend(self.get_header_lines(repository))
        
        self._check_repository_attrs(repository)
        
        # Generate CenRep entries for all keys
        cenrep_entries = []
        for key in repository.keys:
            cenrep_entries.extend(self.get_cenrep_entries(key))
        
        # Generate entry lines based on the entries
        cenrep_entries.sort()
        for entry in cenrep_entries:
            data.append(self.get_cenrep_entry_line(entry))
        
        data.append('')
        
        # Remove Nones from the line list
        data = filter(lambda val: val is not None, data)
        
        return '\r\n'.join(data)
    
    def get_cenrep_rfs_txt_data(self, rfs_records):
        """
        Return the text data for the CenRep RFS txt generated based on the given
        CenRep RFS record list.
        """
        data = []
        
        # Make a distinct and sorted array of the records
        records = []
        for r in rfs_records:
            if r not in records: records.append(r)
        records.sort()
        
        for record in records:
            repo_uid = record.repo_uid
            
            # Add padding zeros to the UID
            if len(repo_uid) < 8:
                repo_uid = (8 - (len(repo_uid) % 8)) * '0' + repo_uid
            temp = "CR %s" % repo_uid
            if record.key_uids:
                temp += " %s" % ' '.join(record.key_uids)
            data.append(temp)
        
        return '\r\n'.join(data)
    
    def get_cenrep_rfs_record(self, repository):
        """
        Return the RFS record for the given CRML repository.
        
        @return: A CenRepRfsRecord object if the repository should be listed
            in cenrep_rfs.txt, None if not.
        """
        # Get the UID as a hex value without the leading 0x
        repo_uid = _translate_key_uid(repository.uid_value)[2:]
        
        # Check if the whole repository has RFS=true
        if repository.rfs:
            return CenRepRfsRecord(repo_uid)
        
        # Collect the UIDs of the keys that should be listed
        rfs_key_uids = []
        for key in repository.keys:
            if self._key_is_rfs(key) and key.int:
                # Get the UID as a hex value without the leading 0x
                uid = _translate_key_uid(key.int)[2:]
                rfs_key_uids.append(uid)
                    
        if rfs_key_uids:
            return CenRepRfsRecord(repo_uid, rfs_key_uids)
        else:
            return None
    
    def _key_is_rfs(self, key):
        """
        @return: True if the key UID should be listed in cenrep_rfs.txt
        """
        if isinstance(key, CrmlSimpleKey):
            return bool(self._get_rfs_value(key.ref))
        elif isinstance(key, CrmlBitmaskKey):
            for bit in key.bits:
                if self._get_rfs_value(bit.ref):
                    return True
        else:
            return False
    
    def _get_rfs_value(self, ref):
        """
        @return: The RFS value for the given setting, or None if not available.
        """
        if ref is None: return
        
        try:
            feature = self._get_feature(ref)
        except exceptions.NotFound:
            # Feature not found in the configuration
            return None
        
        return feature.get_value(attr='rfs')
    
    def get_header_lines(self, repository):
        """
        Return a list of lines to be written in the header section of the CenRep text file.
        """
        data = ['cenrep',
                'version %s' % repository.version]
        
        if repository.owner:
            data.append('[owner]')
            data.append(repository.owner)
        
        data.append('[defaultmeta]')
        data.append(' %d' % _get_metadata(repository.backup))
        for key in repository.keys:
            data.append(self.get_defaultmeta_line(key))
        
        data.append('[platsec]')
        acc_text = self.get_access_line(repository.access)
        if acc_text: acc_text = ' ' + acc_text
        data.append(acc_text)
        for key in repository.keys:
                data.append(self.get_platsec_line(key, repository))
        
        
        data.append('[Main]')
        return data
    
    def get_cenrep_entries(self, key):
        """
        Generate CenRep entries based on the given CRML key object.
        @return: A list of CenRepEntry objects.
        """
        if isinstance(key, CrmlSimpleKey):
            feature = self._get_feature(key.ref)
            entry = CenRepEntry(int          = key.int,
                                crml_type    = key.type,
                                confml_type  = feature.get_type(),
                                value        = feature.get_value(),
                                orig_value   = feature.get_original_value(),
                                backup       = key.backup,
                                access       = key.access)
            return [entry]
        elif isinstance(key, CrmlBitmaskKey):
            return self.get_bitmask_key_cenrep_entries(key)
        elif isinstance(key, CrmlKeyRange):
            return self.get_key_range_cenrep_entries(key)
        else:
            raise TypeError("Unsupported CRML key object type %s" % type(key))
    
    def get_key_range_cenrep_entries(self, key_range):
        """
        Generate CenRep entries based on the given CrmlKeyRange object.
        @return: A list of CenRepEntry objects.
        """
        entries = []
        count = 0
        
        # Generate the countInt entry if necessary
        if key_range.count_int is not None and key_range.ref is not None:
            try:
                feature = self._get_feature(key_range.ref)
                
                # For CT2 output compatibility
                if feature.get_type() != 'sequence':
                    return []
                
                values = feature.get_value()
            except exceptions.NotFound:
                values = []
            
            count = len(values)
                
            entry = CenRepEntry(int         = key_range.count_int,
                                crml_type   = 'int',
                                confml_type = 'int',
                                value       = count,
                                backup      = key_range.backup,
                                access      = key_range.access)
            entries.append(entry)
        
        # Generate entries based on the sequence values
        for subkey in key_range.subkeys:
            full_ref = "%s.%s"% (key_range.ref, subkey.ref)
            
            try:
                feature = self._get_feature(full_ref)
                values = feature.get_value()
                confml_type = feature.get_type()
                backup = key_range.backup
            except exceptions.NotFound:
                # For CT2 output compatibility
                values = ['null' for i in xrange(count)]
                confml_type = None
                backup = False
                
            for i, value in enumerate(values):
                # Calculate the index of the entry
                index = self.get_index(crml_reader.convert_num(key_range.first_int),
                                       crml_reader.convert_num(key_range.first_index),
                                       crml_reader.convert_num(key_range.index_bits),
                                       i,
                                       crml_reader.convert_num(subkey.int))
                
                entry = CenRepEntry(int         = "0x%x" % index,
                                    crml_type   = subkey.type,
                                    confml_type = confml_type,
                                    value       = value,
                                    orig_value  = value,
                                    backup      = backup,
                                    access      = key_range.access)
                entries.append(entry)
        
        return entries
    
    def get_bitmask_key_cenrep_entries(self, key):
        """
        Generate CenRep entries based on the given CrmlBitmaskKey object.
        @return: A list of CenRepEntry objects.
        """
        # Calculate the value based on the bit values
        # -------------------------------------------
        value = 0
        for bit in key.bits:
            feature = self._get_feature(bit.ref)
            bit_value = feature.get_value()
            if bit.invert:  bit_value = not bit_value
            if bit_value:   value |= 1 << (bit.index - 1)
        
        # Generate the textual representation of the bitmask value.
        # This is done at this point because in get_cenrep_entry_line()
        # we don't know anymore if the key was a bitmask key or a
        # simple key.
        # -------------------------------------------------------------
        if key.type == 'binary':
            orig_value = "%X" % value
            # Add padding zeroes so that the number of digits
            # is divisible by 8 (done manually since the length
            # of a binary bitmask is unbounded).
            padding_zeroes = (8 - len(orig_value) % 8) * '0' 
            # 4 is a special case for CT2 output compatibility
            if len(orig_value) != 4:
                orig_value = padding_zeroes + orig_value
        else:
            orig_value = str(value)
        
        entry = CenRepEntry(int         = key.int,
                            crml_type   = key.type,
                            confml_type = 'int',
                            value       = value,
                            orig_value  = orig_value,
                            backup      = key.backup,
                            access      = key.access)
        return [entry]
    
    def get_defaultmeta_line(self, key):
        """
        Return the defaultmeta section line for the given CRML key object.
        """
        if not isinstance(key, CrmlKeyRange): return None
        
        return "%s %s %d" % (key.first_int,
                             key.last_int,
                             _get_metadata(key.backup))
    
    def get_platsec_line(self, key, repository):
        """
        Return the platsec section line for the given CRML key object.
        """
        if not isinstance(key, CrmlKeyRange): return None
        
        # In a key range platsec entry something must be present, so if
        # the access object is empty, use cap_rd and cap_wr from the repository's
        # global access definition
        access = key.access.copy()
        is_empty = True
        for attrname in ('sid_rd', 'cap_rd', 'sid_wr', 'cap_wr'):
            if getattr(access, attrname) not in ('', None):
                is_empty = False
        if is_empty:
            access.cap_rd = repository.access.cap_rd
            access.cap_wr = repository.access.cap_wr
        
        acc_text = self.get_access_line(access)
        if acc_text: acc_text = ' ' + acc_text
        
        return "%s %s%s" % (key.first_int,
                             key.last_int,
                             acc_text)
        
    
    def get_cenrep_entry_line(self, entry):
        """
        Return the text line for a CenRepEntry object.
        """
        value = None
        if entry.crml_type in ('string', 'string8'):
            if entry.confml_type is None:
                pass
            else:
                if entry.orig_value is None:
                    value = '""'
                else:
                    value = '"%s"' % entry.orig_value
        elif entry.crml_type == 'int':
            if entry.confml_type == 'boolean':
                if entry.value: value = '1'
                else:           value = '0'
            else:
                value = entry.orig_value
        elif entry.crml_type == 'real':
            value = entry.orig_value or ''
        elif entry.crml_type == 'binary':
            # Empty binary values are denoted by a single dash
            value = entry.orig_value or '-'
            
            if value != '-':
                # Make sure that the number of digits is divisible by two
                if len(value) % 2 != 0:
                    value = '0' + value
        
        if value is None:
            value = unicode(entry.value)
        
        self._check_value(entry, value)
        
        acc_text = self.get_access_line(entry.access)
        if acc_text: acc_text = ' ' + acc_text
        
        return '%s %s %s %d%s' % (_translate_key_uid(entry.int),
                                  entry.crml_type,
                                  value,
                                  entry.metadata,
                                  acc_text)
    def _check_value(self, entry, value):
        """
        Check that the given value is valid for the given CenRep entry,
        and log a warning if it is not.
        """
        if entry.crml_type == 'int':
            # Check if the value is a string, since it may already
            # be an integer
            if not isinstance(value, basestring):
                return
            
            try:
                value = value.strip()
                if value.lower().startswith('0x'):
                    long(value, 16)
                else:
                    long(value)
            except ValueError:
                self.log.warn("Key %s: Invalid integer value '%s'" % (entry.int, value))
        elif entry.crml_type == 'real':
            try:
                float(value)
            except ValueError:
                self.log.warn("Key %s: Invalid real value '%s'" % (entry.int, value))
        elif entry.crml_type == 'binary':
            if value != '-' and re.match(r'^(0[xX])?[0-9a-fA-F]+$', value) is None:
                self.log.warn("Key %s: Invalid binary value '%s'" % (entry.int, value))
    
    def _check_repository_attrs(self, repository):
        """
        Check that the attributes of the given repository are valid and
        log warnings if not.
        """
        if repository.owner is not None:
            owner = repository.owner.strip()
            # An empty owner UID is OK, it doesn't generate anything
            # invalid into the output
            if owner != '':
                try:
                    if owner.lower().startswith('0x'):
                        long(owner, 16)
                    else:
                        long(owner)
                except ValueError:
                    self.log.warn("Invalid owner UID '%s'" % owner)
    
    def get_access_line(self, access):
        """
        Generate a line containing access information based on a CrmlAccess object.
        """
        # Write the access information in a specific order, because it
        # won't work otherwise
        var_order = ['sid_rd', 'cap_rd', 'sid_wr', 'cap_wr']
        data = []
        for varname in var_order:
            val = getattr(access, varname)
            if val not in ('', None):
                # Using _translate_capability_string() on all, since a SID should
                # not contain anything that could be messed up by the function
                data.append('%s=%s' % (varname, _translate_capability_string(val)))
        
        return ' '.join(data)
    
    def _get_feature(self, ref):
        return self.configuration.get_default_view().get_feature(ref)
    
    @classmethod
    def get_index(cls,firstInt,firstIndex,indexBits,seqIndex, subIndex):
        """
        @param firstIndex: The first value available in the keyrange 
        @param lastInt: The last value available in the keyrange 
        @param indexBits: The index bits or mask for sequence index
        @param seqIndex: The sequence index
        @param subIndex: The sequence sub element index
        @return: an numeric value for the encoded index
        """
        rangeshift = cls.get_range_shift(indexBits)
        return (((seqIndex+firstIndex) << rangeshift) + firstInt) + subIndex

    @classmethod
    def get_seqid(cls,firstInt,firstIndex,indexBits,cenrepkey):
        """
        @param firstIndex: The first value available in the keyrange 
        @param lastInt: The last value available in the keyrange 
        @param indexBits: The index bits or mask for sequence index
        @param cenrepkey: Crml key id
        @return: an numeric value for the encoded index
        """
        rangeshift = cls.get_range_shift(indexBits)
        return (((cenrepkey & indexBits) -firstInt) >> rangeshift)-firstIndex

    @classmethod
    def get_subseqid(cls,firstInt,firstIndex,indexBits,cenrepkey):
        """
        @param firstIndex: The first value available in the keyrange 
        @param lastInt: The last value available in the keyrange 
        @param indexBits: The index bits or mask for sequence index
        @param cenrepkey: Crml key id
        @return: an numeric value for the encoded index
        """
        range = cls.get_range(indexBits)
        return (cenrepkey - firstInt) & range

    @classmethod
    def get_range_shift(cls,indexBits):
        """ Get the bit left to the """
        seqrange = cls.get_range(indexBits)
        shiftamount = 0
        for i in range(0,32):
            if (seqrange >> i)  == 0:
                shiftamount = i
                break
        return shiftamount

    @classmethod
    def get_range(cls,indexBits):
        """ Get the bit left to the """
        indexshift = 0 
        for i in range(0,32):
            if (indexBits >> i)  == 0:
                indexshift = i
                break
        return ((0x1 << indexshift) - indexBits)-1


# =============================================================================
# Utility functions
# =============================================================================

def _get_metadata(backup):
    metadata = 0
    if backup: metadata |= 0x1000000
    return metadata
        
def _translate_key_uid(uid):
    """Translate a key UID given in CRML so that it matches the output of CT2."""
    if uid.lower().startswith("0x"):
        prefix = uid[:2]
        temp = uid[2:]
        if int(temp, 16) == 0:  return prefix + "0"
        else:                   return prefix + uid[2:].lstrip('0')
    else:
        if int(uid) == 0:       return "0"
        else:                   return uid.lstrip('0')

def _translate_capability_string(cap_str):
    """
    Translate a capability string so that it is
    suitable for writing to a CenRep txt file.
    """
    cap_str = cap_str.replace('AlwaysPass', 'alwayspass').replace('AlwaysFail', 'alwaysfail')
    
    # The capability string can be a list separated either by
    # whitespace or commas
    if ',' in cap_str:  caps = cap_str.split(',')
    else:               caps = cap_str.split()
    
    # The output must always be comma-separated
    return ','.join(caps)

