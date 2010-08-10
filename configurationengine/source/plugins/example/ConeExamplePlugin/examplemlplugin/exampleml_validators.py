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


import codecs

from cone.public import api, exceptions, utils
from cone.validation.implmlvalidation import ImplValidatorBase
from examplemlplugin import exampleml_impl

class ExamplemlValidatorBase(ImplValidatorBase):
    SUPPORTED_IMPL_CLASSES = exampleml_impl.ExamplemlImpl

class ExamplemlReferenceValidator(ExamplemlValidatorBase):
    PROBLEM_TYPES = ['model.implml.exampleml.invalid_ref']
    
    def validate(self):
        for output in self.impl.output_objects:
            # Collect all refs
            refs = set()
            for ref in utils.extract_delimited_tokens(output.text):     refs.add(ref)
            for ref in utils.extract_delimited_tokens(output.encoding): refs.add(ref)
            for ref in utils.extract_delimited_tokens(output.file):     refs.add(ref)
            
            for ref in refs:
                self.check_feature_reference(ref, output.lineno, self.PROBLEM_TYPES[0])

class ExamplemlEncodingValidator(ExamplemlValidatorBase):
    PROBLEM_TYPES = ['model.implml.exampleml.invalid_encoding']
    
    def validate(self):
        for output in self.impl.output_objects:
            encoding = None
            try:
                encoding = utils.expand_refs_by_default_view(
                    output.encoding,
                    self.context.configuration.get_default_view(),
                    catch_not_found=False)
            except exceptions.NotFound:
                # Ignore invalid setting references, they are validated
                # in another validator
                continue
            
            if encoding is not None:
                # Check the encoding
                try:
                    codecs.lookup(encoding)
                except LookupError:
                    prob = api.Problem(
                        msg = u"Invalid encoding '%s'" % encoding,
                        type = self.PROBLEM_TYPES[0],
                        line = output.lineno,
                        file = self.impl.ref)
                    self.context.problems.append(prob)

VALIDATOR_CLASSES = [ExamplemlReferenceValidator, ExamplemlEncodingValidator]
