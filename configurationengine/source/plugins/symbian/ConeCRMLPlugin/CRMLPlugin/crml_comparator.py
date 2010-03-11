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
from cone.public import plugin
from crml_model import *

class CrmlComparator(object):
    def __init__(self, resource_ref, repo):
        self.logger = logging.getLogger('cone.crml.comparator(%s)' % resource_ref)
        self.resource_ref = resource_ref
        self.repo = repo
    
    @classmethod
    def get_flat_comparison_id(cls, repo):
        """
        Return the flat comparison ID for the given repository.
        """
        return cls._num_to_str(repo.uid_value)
    
    @classmethod
    def get_flat_comparison_extra_data(cls, repo):
        return {'repo': repo}
    
    @classmethod
    def _num_to_str(cls, number):
        if isinstance(number, basestring):
            try:
                number = long(number, 10)
            except ValueError:
                number = long(number, 16)
        return "0x%08X" % number
    
    def flat_compare(self, target_resource_ref, target_repo):
        """
        Compare two CRML repository models.
        @return: A plugin.FlatComparisonResult object.
        """
        source_repo = self.repo
        
        result = plugin.FlatComparisonResult()
        
        source_repo_uid = self._num_to_str(source_repo.uid_value)
        target_repo_uid = self._num_to_str(target_repo.uid_value)
        
        if source_repo_uid != target_repo_uid:
            raise RuntimeError("Comparing CRML implementations instances that don't have the same repository UID (%r vs. %r)" % (source_repo_uid, target_repo_uid))
        
        # Default field contents for new entries
        default_field_content = {
            'data'      : {}}
        
        Entry = plugin.FlatComparisonResultEntry
        
        if self.resource_ref != target_resource_ref:
            result.modified.append(Entry(value_id       = 'file',
                                         source_value   = self.resource_ref,
                                         target_value   = target_resource_ref,
                                         data           = {'source_repo': source_repo,
                                                           'target_repo': target_repo}))
        
        # Compare repository attributes
        # -----------------------------
        repo_mods = self._flat_compare_object_attrs(
            key_id      = None,
            source_obj  = source_repo,
            target_obj  = target_repo,
            varnames    = ('uid_name', 'owner', 'backup', 'rfs', 'access'))
        content = default_field_content.copy()
        content['data'] = {'source_repo': source_repo,
                           'target_repo': target_repo}
        self._fill_in_entry_fields(repo_mods, content)
        result.modified.extend(repo_mods)
        
        source_data = self._get_flat_comparison_data(source_repo)
        target_data = self._get_flat_comparison_data(target_repo)
        
        # Find entries only in source
        # ---------------------------
        for id, crml_key in source_data.iteritems():
            if id not in target_data:
                data = {'repo': source_repo,
                        'key':  crml_key}
                result.only_in_source.append(Entry(sub_id=id, data=data))
        
        # Find entries only in target
        # ---------------------------
        for id, crml_key in target_data.iteritems():
            if id not in source_data:
                data = {'repo': source_repo,
                        'key':  crml_key}
                result.only_in_target.append(Entry(sub_id=id, data=data))
        
        # Find differing entries
        # ----------------------
        for id, source_key in source_data.iteritems():
            if id not in target_data: continue
            target_key = target_data[id]
            if source_key == target_key: continue
            
            # Get the comparison result for the key
            comp_result = self._get_flat_key_comparison_result(id, source_key, target_key)
            
            # Fill in the missing fields of the result entries
            content = default_field_content.copy()
            content['data'] = {'repo'   : source_repo,
                               'key'    : source_key}
            self._fill_in_entry_fields(comp_result.only_in_source, content)
            
            content = default_field_content.copy()
            content['data'] = {'repo'   : target_repo,
                               'key'    : target_key}
            self._fill_in_entry_fields(comp_result.only_in_target,  content)
            
            content = default_field_content.copy()
            content['data'] = {'source_repo'    : source_repo,
                               'target_repo'    : target_repo,
                               'source_key'     : source_key,
                               'target_key'     : target_key}
            self._fill_in_entry_fields(comp_result.modified, content)
            
            result.extend(comp_result)
        
        return result
    
    def _fill_in_entry_fields(self, entry_list, field_contents):
        for entry in entry_list:
            for varname, value in field_contents.iteritems():
                if getattr(entry, varname) is None:
                    setattr(entry, varname, value)
    
    def _get_flat_comparison_data(self, repository):
        """
        Return a dictionary containing all keys in the repository.
        
        The dictionary will have the CRML key UIDs as the dictionary keys and
        the CRML key objects as the values.
        """
        data = {}
        for key in repository.keys:
            if isinstance(key, (CrmlSimpleKey, CrmlBitmaskKey)):
                id = self._num_to_str(key.int)
            elif isinstance(key, CrmlKeyRange):
                id = self._num_to_str(key.first_int) + '-' + self._num_to_str(key.last_int)
            data[id] = key
        return data
    
    def _get_flat_key_comparison_result(self, key_id, source_key, target_key):
        """
        Return a flat comparison result for a source and target CRML key pair.
        
        @param key_id: The ID of the key, e.g. '0x00000001' for a simple key or
            '0x00001000-0x00001FFF' for a key range.
        @param source_key: The source key object.
        @param target_key: The target key object.
        @return: A plugin.FlatComparisonResult object.
        """
        result = plugin.FlatComparisonResult()
        
        if type(source_key) == type(target_key):
            comp_funcs = {CrmlSimpleKey:   self._flat_compare_simple_keys,
                          CrmlBitmaskKey:  self._flat_compare_bitmask_keys,
                          CrmlKeyRange:    self._flat_compare_key_ranges}
            func = comp_funcs[type(source_key)]
            result.extend(func(key_id, source_key, target_key))
        else:
            # Perform base key comparison
            result.modified.extend(self._flat_compare_base_keys(key_id, source_key, target_key))
            
            # Add an entry for key type change
            type_ids = {CrmlSimpleKey:  'simple_key',
                        CrmlBitmaskKey: 'bitmask_key',
                        CrmlKeyRange:   'key_range'}
            entry = plugin.FlatComparisonResultEntry(
                sub_id       = key_id,
                value_id     = 'key_type',
                source_value = type_ids[type(source_key)],
                target_value = type_ids[type(target_key)])
            result.modified.append(entry)
        
        return result
    
    def _flat_compare_object_attrs(self, key_id, source_obj, target_obj, varnames):
        result = []
        for varname in varnames:
            sval = getattr(source_obj, varname)
            tval = getattr(target_obj, varname)
            
            if sval != tval:
                if isinstance(sval, CrmlAccess):
                    result.extend(self._flat_compare_object_attrs(
                          key_id, sval, tval,
                          ('cap_rd', 'cap_wr', 'sid_rd', 'sid_wr')))
                else:
                    entry = plugin.FlatComparisonResultEntry(
                        sub_id       = key_id,
                        value_id     = varname,
                        source_value = sval,
                        target_value = tval)
                    result.append(entry)
        return result
    
    def _flat_compare_base_keys(self, key_id, source_key, target_key, extra_varnames=[]):
        varnames = ['name', 'backup', 'read_only', 'access']
        varnames.extend(extra_varnames)
        return self._flat_compare_object_attrs(key_id, source_key, target_key, varnames)
    
    def _flat_compare_simple_keys(self, key_id, source_key, target_key):
        mod = self._flat_compare_base_keys(key_id, source_key, target_key,
                                           extra_varnames=['ref', 'type'])
        return plugin.FlatComparisonResult(modified=mod)
    
    def _flat_compare_bitmask_keys(self, key_id, source_key, target_key):
        mod = self._flat_compare_base_keys(key_id, source_key, target_key,
                                           extra_varnames=['type'])
        only_in_source = []
        only_in_target = []
        
        def get_bits_dict(key):
            bits = {}
            for bit in key.bits:
                bits[bit.index] = bit
            return bits
        
        src_bits = get_bits_dict(source_key)
        tgt_bits = get_bits_dict(target_key)
        
        # Find bits only in source
        # ------------------------
        for index in src_bits.iterkeys():
            if index not in tgt_bits:
                entry = plugin.FlatComparisonResultEntry(
                    sub_id = "%s (bit %s)" % (key_id, index))
                only_in_source.append(entry)
        
        # Find bits only in target
        # ------------------------
        for index in tgt_bits.iterkeys():
            if index not in src_bits:
                entry = plugin.FlatComparisonResultEntry(
                    sub_id = "%s (bit %s)" % (key_id, index))
                only_in_target.append(entry)
        
        # Find modified bits
        # ------------------
        for index, src_bit in src_bits.iteritems():
            if index not in tgt_bits: continue
            tgt_bit = tgt_bits[index]
            
            mod.extend(self._flat_compare_object_attrs(
                key_id      = "%s (bit %s)" % (key_id, index),
                source_obj  = src_bit,
                target_obj  = tgt_bit,
                varnames    = ('ref', 'invert')))
        
        return plugin.FlatComparisonResult(modified         = mod,
                                           only_in_source   = only_in_source,
                                           only_in_target   = only_in_target)
    
    def _flat_compare_key_ranges(self, key_id, source_key, target_key):
        mod = self._flat_compare_base_keys(key_id, source_key, target_key,
                                           extra_varnames=['ref', 'index_bits', 'first_index'])
        only_in_source = []
        only_in_target = []
        
        # Use hexadecimal format for index bits
        for entry in mod:
            if entry.value_id == 'index_bits':
                entry.source_value = self._num_to_str(entry.source_value)
                entry.target_value = self._num_to_str(entry.target_value)
        
        def get_subkeys_dict(key):
            subkeys = {}
            for sk in key.subkeys:
                subkeys[sk.int] = sk
            return subkeys
        
        src_subkeys = get_subkeys_dict(source_key)
        tgt_subkeys = get_subkeys_dict(target_key)
        
        # Find sub-keys only in source
        # ----------------------------
        for uid in src_subkeys.iterkeys():
            if uid not in tgt_subkeys:
                entry = plugin.FlatComparisonResultEntry(
                    sub_id = "%s (sub-key %s)" % (key_id, self._num_to_str(uid)))
                only_in_source.append(entry)
        
        # Find sub-keys only in target
        # ----------------------------
        for uid in tgt_subkeys.iterkeys():
            if uid not in src_subkeys:
                entry = plugin.FlatComparisonResultEntry(
                    sub_id = "%s (sub-key %s)" % (key_id, self._num_to_str(uid)))
                only_in_target.append(entry)
        
        # Find modified bits
        # ------------------
        for uid, src_subkey in src_subkeys.iteritems():
            if uid not in tgt_subkeys: continue
            tgt_subkey = tgt_subkeys[uid]
            
            mod.extend(self._flat_compare_object_attrs(
                key_id      = "%s (sub-key %s)" % (key_id, self._num_to_str(uid)),
                source_obj  = src_subkey,
                target_obj  = tgt_subkey,
                varnames    = ('ref', 'type', 'name')))
        
        return plugin.FlatComparisonResult(modified         = mod,
                                           only_in_source   = only_in_source,
                                           only_in_target   = only_in_target)
