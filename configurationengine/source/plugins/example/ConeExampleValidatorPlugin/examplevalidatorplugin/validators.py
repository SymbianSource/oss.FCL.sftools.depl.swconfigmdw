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

from cone.public import api
from cone.confml import model
from cone.validation.confmlvalidation import ValidatorBase

class ExampleValidator(ValidatorBase):
    PROBLEM_TYPES = ['model.confml.foo_missing']
    
    def validate(self):
        for ref, feature in self.context.feature_dict.iteritems():
            if isinstance(feature._obj, model.ConfmlStringSetting) and feature.ref.startswith('FOO_'):
                value = feature.get_value()
                if isinstance(value, basestring) and 'foo' not in value:
                    dataobj = feature.datas['data'][-1]
                    
                    prob = api.Problem(
                        msg = "String 'foo' missing from value of feature '%s'" % ref,
                        type = self.PROBLEM_TYPES[0],
                        line = dataobj.lineno,
                        file = dataobj.get_configuration_path(),
                        severity = api.Problem.SEVERITY_WARNING)
                    self.context.problems.append(prob)

VALIDATOR_CLASSES = [ExampleValidator]
