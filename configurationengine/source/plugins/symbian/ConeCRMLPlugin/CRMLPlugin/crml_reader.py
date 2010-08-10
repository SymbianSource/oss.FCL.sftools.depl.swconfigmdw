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
import pkg_resources
from cone.public import exceptions, plugin, utils
import crml_impl
from crml_model import *


def get_required_attr(elem, attrname):
    """
    Get a required attribute from an XML element or raise an exception.
    """
    attr = elem.get(attrname)
    if attr is None:
        raise exceptions.ParseError("<%s> element does not have the required '%s' attribute!" % (elem.tag, attrname))
    return attr

def convert_num(string):
    """
    Convert the given string into a number.
    
    - The number can be in decimal or hexadecimal format.
    - If None is passed, None is also returned.
    """
    if string in ('', None):
        return None
    try:
        return long(string)
    except ValueError:
        return long(string, 16)

class CrmlReader(plugin.ReaderBase):
    NAMESPACE = 'http://www.s60.com/xml/cenrep/1'
    NAMESPACE_ID = 'crml'
    ROOT_ELEMENT_NAME = 'repository'
    FILE_EXTENSIONS = ['crml']
    
    @classmethod
    def read_impl(cls, resource_ref, configuration, etree):
        reader = CrmlReader()
        repository = reader.read_repository(etree)
        return crml_impl.CrmlImpl(resource_ref, configuration, repository)
    
    @classmethod
    def get_schema_data(cls):
        return pkg_resources.resource_string('CRMLPlugin', 'xsd/crml.xsd')
    
    def read_repository(self, elem):
        """
        Read a CrmlRepository object from the given XML element.
        """
        # Read repository attributes
        repo = CrmlRepository(
            uid_value = elem.get('uidValue'),
            uid_name  = elem.get('uidName'),
            owner     = elem.get('owner'),
            version   = elem.get('initialisationFileVersion', '1'),
            access    = self.read_access(elem))
        if elem.get('backup') == 'true':    repo.backup = True
        if elem.get('rfs') == 'true':       repo.rfs = True
        
        # Read all keys
        for sub_elem in elem:
            key_obj = self.read_key(sub_elem)
            
            if key_obj is not None:
                # Read-only keys have always cap_wr=AlwaysFail.
                # the isinstance() check is for CT2 output compatibility
                if not isinstance(key_obj, CrmlKeyRange):
                    if key_obj.read_only:
                        key_obj.access.cap_wr = 'AlwaysFail'
                        key_obj.access.sid_wr = None
                
                repo.keys.append(key_obj)
        
        if repo.access == CrmlAccess(cap_rd='AlwaysPass') and len(repo.keys) == 0:
            repo.access.cap_rd = None
        
        return repo
    
    def read_access(self, elem):
        """
        Read a CrmlAccess object from the given XML element.
        @param elem: The element from which to parse an access definition. Should be any
            element that can contain an access definition (i.e. 'repository', 'key', or 'keyRange').
        """
        access = CrmlAccess()
        read_cap_found = False
        write_cap_found = False
        for access_elem in elem.findall('{%s}access' % self.NAMESPACE):
            type = access_elem.get('type')
            if type == 'R' and not read_cap_found:
                access.cap_rd = access_elem.get('capabilities')
                access.sid_rd = access_elem.get('sid')
                access.line_rd = utils.etree.get_lineno(access_elem)
                read_cap_found = True
            elif type == 'W' and not write_cap_found:
                access.cap_wr = access_elem.get('capabilities')
                access.sid_wr = access_elem.get('sid')
                access.line_wr = utils.etree.get_lineno(access_elem)
                write_cap_found = True
        
        return access
    
    def read_common_key_attrs(self, key_elem, key_obj):
        """
        Read common attributes into an object of class CrmlKeyBase from an XML element.
        """
        if not isinstance(key_obj, CrmlKeyBase):
            raise ValueError("Expected object of type %s" % CrmlKeyBase.__name__)
        
        if key_elem.get('readOnly') == 'true':  key_obj.read_only = True
        if key_elem.get('backup') == 'true':    key_obj.backup = True
        key_obj.access = self.read_access(key_elem)
        key_obj.name = key_elem.get('name')
    
    def read_key(self, key_elem):
        key_obj = None
        if key_elem.tag == '{%s}key' % self.NAMESPACE:
            # Determine whether the key is a normal key or a bitmask key
            # based on the presence of <bit> elements
            tags = [e.tag for e in key_elem]
            if '{%s}bit' % self.NAMESPACE in tags:
                key_obj = self.read_bitmask_key(key_elem)
            else:
                key_obj = self.read_simple_key(key_elem)
        elif key_elem.tag == '{%s}keyRange' % self.NAMESPACE:
            key_obj = self.read_key_range(key_elem)
        
        return key_obj
    
    def read_simple_key(self, key_elem):
        """
        Read a CrmlSimpleKey object from the given XML element.
        """
        expected_tag = '{%s}key' % self.NAMESPACE
        if key_elem.tag != expected_tag:
            raise RuntimeError("Incorrect XML element passed to read_simple_key(): %s, expected %s" % (key_elem.tag, expected_tag))
        
        key = CrmlSimpleKey(
            ref  = get_required_attr(key_elem, 'ref').replace('/', '.'),
            int  = get_required_attr(key_elem, 'int'),
            type = key_elem.get('type', 'int'),
            line = utils.etree.get_lineno(key_elem))
        self.read_common_key_attrs(key_elem, key)
        
        return key
    
    def read_bitmask_key(self, key_elem):
        """
        Read a CrmlBitmaskKey object from the given XML element.
        """
        expected_tag = '{%s}key' % self.NAMESPACE
        if key_elem.tag != expected_tag:
            raise RuntimeError("Incorrect XML element passed to read_bitmask_key(): %s, expected %s" % (key_elem.tag, expected_tag))
        
        # Read attributes
        key = CrmlBitmaskKey(
            int  = get_required_attr(key_elem, 'int'),
            type = key_elem.get('type', 'int'),
            line = utils.etree.get_lineno(key_elem))
        self.read_common_key_attrs(key_elem, key)
        
        # Read bits
        for bit_elem in key_elem.findall('{%s}bit' % self.NAMESPACE):
            ref = get_required_attr(bit_elem, 'ref').replace('/', '.')
            if bit_elem.get('value') == 'false':    invert = True
            else:                                   invert = False
            index = int(bit_elem.text.strip())
            
            key.bits.append(CrmlBit(ref=ref, index=index, type=type, invert=invert,
                                    line=utils.etree.get_lineno(bit_elem)))
        
        return key
    
    def read_key_range(self, key_range_elem):
        """
        Read a CrmlKeyRange object from the given XML element.
        """
        expected_tag = '{%s}keyRange' % self.NAMESPACE
        if key_range_elem.tag != expected_tag:
            raise RuntimeError("Incorrect XML element passed to read_key_range(): %s, expected %s" % (key_range_elem.tag, expected_tag))
        
        # Read attributes
        ref = key_range_elem.get('ref')
        if ref is not None: ref = ref.replace('/', '.')
        key_range = CrmlKeyRange(
            ref         = ref,
            first_int   = get_required_attr(key_range_elem, "firstInt"),
            last_int    = get_required_attr(key_range_elem, "lastInt"),
            count_int   = key_range_elem.get('countInt'),
            first_index = convert_num(key_range_elem.get('firstIndex', '0')),
            index_bits  = convert_num(key_range_elem.get('indexBits')),
            line        = utils.etree.get_lineno(key_range_elem))
        self.read_common_key_attrs(key_range_elem, key_range)
        
        # Read sub-keys
        for subkey_elem in key_range_elem.findall('{%s}key' % self.NAMESPACE):
            ref = get_required_attr(subkey_elem, 'ref').replace('/', '.')
            int = get_required_attr(subkey_elem, 'int')
            name = subkey_elem.get('name')
            type = subkey_elem.get('type', 'int')
            key_range.subkeys.append(CrmlKeyRangeSubKey(ref=ref, int=int, name=name, type=type,
                                                        line=utils.etree.get_lineno(subkey_elem)))
        
        return key_range