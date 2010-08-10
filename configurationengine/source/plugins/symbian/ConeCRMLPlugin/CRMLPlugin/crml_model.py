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

class _CrmlObjectBase(object):
    """
    Common utility base class for all CRML objects for implementing
    operations like repr(), copy() etc.
    """
    
    # Variable names used in simple object equality comparison
    SIMPLE_EQ_VARNAMES = []

    def __repr__(self):
        return "%s(**%r)" % (self.__class__.__name__, vars(self))
    
    def __get_filtered_dict(self, source_dict, allowed_keys):
        result = {}
        for key in allowed_keys:
            if key in source_dict:
                result[key] = source_dict[key]
        return result
    
    def __eq__(self, other):
        # 1. Compare type
        if type(self) is not type(other):
            return False
        
        # 2. Compare all members that can be simply compared using ==
        varnames = self.__class__.SIMPLE_EQ_VARNAMES
        dict_self   = self.__get_filtered_dict(vars(self), varnames)
        dict_other  = self.__get_filtered_dict(vars(other), varnames)
        if dict_self != dict_other:
            return False
        
        # 3. Do any extra comparing
        if not self._do_extra_eq_handling(other):
            return False
        
        return True
    
    def __ne__(self, other):
        return not (self == other)
    
    def _do_extra_eq_handling(self, other):
        """
        If sub-classes need to do any extra handling in __eq__(), they
        should implement this method and do it here.
        @return: True if self is equal to other, False if not.
        """
        return True
    
    def copy(self):
        """
        Return a deep copy of this object.
        """
        new_obj = self.__class__(**vars(self))
        self._do_extra_copy_handling(new_obj)
        return new_obj
    
    def _do_extra_copy_handling(self, new_object):
        """
        If sub-classes need to do any extra handling in copy(), they
        should implement this method and do it here.
        @param new_object: The new copied object, a shallow copy at this point.
        """
        return

class CrmlAccess(_CrmlObjectBase):
    SIMPLE_EQ_VARNAMES = ['cap_rd', 'cap_wr', 'sid_rd', 'sid_wr']

    def __init__(self, **kwargs):
        self.cap_rd = kwargs.get('cap_rd')
        self.cap_wr = kwargs.get('cap_wr')
        self.sid_rd = kwargs.get('sid_rd')
        self.sid_wr = kwargs.get('sid_wr')
        self.line_rd = kwargs.get('line_rd')
        self.line_wr = kwargs.get('line_wr')


class CrmlRepository(_CrmlObjectBase):
    SIMPLE_EQ_VARNAMES = ['uid_value', 'uid_name', 'owner', 'backup', 'rfs', 'access', 'keys', 'version']
    
    def __init__(self, **kwargs):
        self.uid_value  = kwargs.get('uid_value')
        self.uid_name   = kwargs.get('uid_name')
        self.owner      = kwargs.get('owner')
        self.backup     = kwargs.get('backup', False)
        self.rfs        = kwargs.get('rfs', False)
        self.access     = kwargs.get('access', CrmlAccess())
        self.keys       = kwargs.get('keys', [])
        self.version    = kwargs.get('version', '1')

    def _do_extra_copy_handling(self, new_object):
        new_keys = []
        for key in new_object.keys:
            new_keys.append(key.copy())
        new_object.keys = new_keys
        
        self.access = new_object.access.copy()
    
    def get_refs(self):
        result = []
        for key in self.keys:
            result.extend(key.get_refs())
        return result

class CrmlKeyBase(object):
    def __init__(self, **kwargs):
        self.ref        = kwargs.get('ref')
        self.name       = kwargs.get('name')
        self.backup     = kwargs.get('backup', False)
        self.read_only  = kwargs.get('read_only', False)
        self.access     = kwargs.get('access', CrmlAccess())
        self.line       = kwargs.get('line', None)

class CrmlSimpleKey(CrmlKeyBase, _CrmlObjectBase):
    SIMPLE_EQ_VARNAMES = ['ref', 'name', 'int', 'type', 'backup', 'read_only', 'access']
    
    def __init__(self, **kwargs):
        CrmlKeyBase.__init__(self, **kwargs)
        try:
            self.ref    = kwargs['ref']
            self.int    = kwargs['int']
            self.type   = kwargs.get('type', 'int')
        except KeyError, e:
            raise ValueError("Mandatory argument '%s' not given!" % e.message)
    
    def _do_extra_copy_handling(self, new_object):
        self.access = new_object.access.copy()
    
    def get_refs(self):
        return [self.ref]

class CrmlBitmaskKey(CrmlKeyBase, _CrmlObjectBase):
    SIMPLE_EQ_VARNAMES = ['int', 'type', 'backup', 'read_only', 'access', 'name', 'bits']
    
    def __init__(self, **kwargs):
        CrmlKeyBase.__init__(self, **kwargs)
        try:
            self.int    = kwargs['int']
            self.type   = kwargs.get('type', 'int')
            self.bits   = kwargs.get('bits', [])
        except KeyError, e:
            raise ValueError("Mandatory argument '%s' not given!" % e.message)
    
    def _do_extra_copy_handling(self, new_object):
        new_bits = []
        for bit in new_object.bits:
            new_bits.append(bit.copy())
        new_object.bits = new_bits
        
        self.access = new_object.access.copy()
    
    def get_refs(self):
        return [bit.ref for bit in self.bits]

class CrmlBit(_CrmlObjectBase):
    SIMPLE_EQ_VARNAMES = ['ref', 'index', 'invert']
    
    def __init__(self, **kwargs):
        try:
            self.ref    = kwargs['ref']
            self.index  = kwargs['index']
            self.invert = kwargs.get('invert', False)
        except KeyError, e:
            raise ValueError("Mandatory argument '%s' not given!" % e.message)
        self.line = kwargs.get('line')

class CrmlKeyRange(CrmlKeyBase, _CrmlObjectBase):
    SIMPLE_EQ_VARNAMES = ['ref', 'name', 'first_int', 'last_int', 'first_index', 'index_bits', 'count_int', 'backup', 'read_only', 'access', 'subkeys']
    
    def __init__(self, **kwargs):
        CrmlKeyBase.__init__(self, **kwargs)
        try:
            self.first_int      = kwargs['first_int']
            self.last_int       = kwargs['last_int']
            self.first_index    = kwargs.get('first_index', 0)
            self.index_bits     = kwargs.get('index_bits')
            self.count_int      = kwargs.get('count_int')
            self.subkeys        = kwargs.get('subkeys', [])
        except KeyError, e:
            raise ValueError("Mandatory argument '%s' not given!" % e.message)
    
    def _do_extra_copy_handling(self, new_object):
        new_subkeys = []
        for subkey in new_object.subkeys:
            new_subkeys.append(subkey.copy())
        new_object.subkeys = new_subkeys
        
        self.access = new_object.access.copy()
    
    def get_refs(self):
        if self.ref is not None:
            refs = [self.ref]
            for sk in self.subkeys:
                refs.append(self.ref + '.' + sk.ref)
            return refs
        else:
            return []
            

class CrmlKeyRangeSubKey(_CrmlObjectBase):
    SIMPLE_EQ_VARNAMES = ['ref', 'name', 'type', 'int']

    def __init__(self, **kwargs):
        try:
            self.ref    = kwargs['ref']
            self.type   = kwargs['type']
            self.int    = kwargs['int']
            self.name   = kwargs.get('name')
        except KeyError, e:
            raise ValueError("Mandatory argument '%s' not given!" % e.message)
        self.line = kwargs.get('line')
    