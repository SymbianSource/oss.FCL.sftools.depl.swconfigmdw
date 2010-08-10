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

from cone.public import api, plugin
from cone.validation.implmlvalidation import GlobalValidatorBase

class DuplicateTempFeatureRefValidator(GlobalValidatorBase):
    """
    Validator for checking for duplicate refs in temporary variable
    definitions.
    """
    PROBLEM_TYPES = ['model.implml.container.duplicate_tempvar']
    
    def validate(self):
        # Collect a dictionary of all temporary variable locations,
        # i.e. (file, lineno) tuples
        tempvar_locations_by_ref = {}
        for impl in self.context.all_impls:
            if isinstance(impl, plugin.ImplContainer):
                for td in impl._tempvar_defs:
                    lst = tempvar_locations_by_ref.get(td.ref, [])
                    lst.append((impl.ref, td.lineno))
                    tempvar_locations_by_ref[td.ref] = lst
        
        # Check for duplicates
        for ref, locations in tempvar_locations_by_ref.iteritems():
            if len(locations) > 1:
                for impl_file, lineno in locations:
                    prob = api.Problem(
                        msg = "Duplicate temporary variable ref '%s'" % ref,
                        type = self.PROBLEM_TYPES[0],
                        line = lineno,
                        file = impl_file)
                    self.context.problems.append(prob)

#: List of all built-in ImplML validator classes
VALIDATOR_CLASSES = [
    DuplicateTempFeatureRefValidator,
]
