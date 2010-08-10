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

from cone.public import api, exceptions
from cone.validation.implmlvalidation import ImplValidatorBase
from CRMLPlugin import crml_impl
from CRMLPlugin import crml_model

class CrmlValidatorBase(ImplValidatorBase):
    SUPPORTED_IMPL_CLASSES = crml_impl.CrmlImpl

class CrmlReferenceValidator(CrmlValidatorBase):
    PROBLEM_TYPES = ['model.implml.crml.invalid_ref']
    
    def validate(self):
        self.dview = self.context.configuration.get_default_view()
        
        for key in self.impl.repository.keys:
            if isinstance(key, crml_model.CrmlSimpleKey):
                self._check_ref(key.ref, key.line)
            elif isinstance(key, crml_model.CrmlBitmaskKey):
                for bit in key.bits:
                    self._check_ref(bit.ref, bit.line)
            elif isinstance(key, crml_model.CrmlKeyRange):
                for subkey in key.subkeys:
                    fullref = "%s.%s" % (key.ref, subkey.ref)
                    self._check_ref(fullref, subkey.line)
    
    def _check_ref(self, ref, line):
        self.check_feature_reference(ref, line, self.PROBLEM_TYPES[0])

class CrmlDuplicateUidValidator(CrmlValidatorBase):
    PROBLEM_TYPES = ['model.implml.crml.duplicate_uid']
    
    def validate(self):
        # Collect a dictionary of CRML keys by UID
        keys_by_uid = {}
        for key in self.impl.repository.keys:
            if isinstance(key, (crml_model.CrmlSimpleKey, crml_model.CrmlBitmaskKey)):
                try:
                    try:
                        uid = long(key.int)
                    except ValueError:
                        uid = long(key.int, 16)
                except ValueError:
                    # Silently ignore non-numeric UID values (they should be caught
                    # by other validation)
                    continue
                keys = keys_by_uid.get(uid, [])
                keys.append(key)
                keys_by_uid[uid] = keys
        
        # Check for duplicates
        for uid, keys in keys_by_uid.iteritems():
            if len(keys) > 1:
                if len(keys) > 2:
                    key_lst = "keys on lines %s" % ', '.join([str(key.line) for key in keys[:-2]])
                    key_lst += ' and %s' % keys[-2].line
                else:
                    key_lst = "key on line %s" % keys[-2].line
                prob = api.Problem(
                    msg = "Duplicate key UID 0x%08X (duplicate with %s)" % (uid, key_lst),
                    type = self.PROBLEM_TYPES[0],
                    line = keys[-1].line,
                    file = self.impl.ref)
                self.context.problems.append(prob)


VALIDATOR_CLASSES = [CrmlReferenceValidator, CrmlDuplicateUidValidator]
