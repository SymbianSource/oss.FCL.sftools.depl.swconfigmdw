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

from cone.public import api, exceptions, plugin, utils, parsecontext
from cone.validation.parsecontext import ValidationParseContext
import cone.validation.common

class ValidationContext(object):
    def __init__(self, configuration):
        self.configuration = configuration
        self.problems = []
        
        #: Flat list of all implementations, including containers
        self.all_impls = []

class ValidatorBase(object):
    """
    Base class for implementation validators.
    
    NOTE THAT THIS CLASS SHOULD NOT BE DIRECTLY SUB-CLASSED.
    Sub-class either ImplValidatorBase or GlobalValidatorBase
    instead.
    """
    PROBLEM_TYPES = None
    
    def __init__(self, context):
        self.context = context

class ImplValidatorBase(ValidatorBase):
    """
    Base class for validators that validate only a single implementation.
    """
    SUPPORTED_IMPL_CLASSES = []
    
    def __init__(self, context, impl):
        self.context = context
        self.impl = impl
    
    def validate(self):
        """
        Called to validate an implementation instance.
        """
        pass

    def check_feature_reference(self, ref, line, problem_type):
        """
        Check that a feature with the given reference exists, and if
        not, add a problem.
        
        @param ref: The feature reference to check.
        @param line: The line number to set to the created problem.
        @param line: The problem type to set to the created problem.
        """
        dview = self.context.configuration.get_default_view()
        try:
            dview.get_feature(ref)
        except exceptions.NotFound:
            prob = api.Problem(
                msg = u"Setting '%s' not found in configuration" % ref,
                type = problem_type,
                line = line,
                file = self.impl.ref)
            self.context.problems.append(prob)

class GlobalValidatorBase(ValidatorBase):
    """
    Base class for validators that validate the entire implementation set at once.
    """
    def validate(self):
        pass

def get_validator_classes(problem_type_filter=None):
    """
    Return a list of all ImplML validator classes that match the given
    problem type filter (i.e. all validator classes that yield problems
    that will not be filtered out).
    
    @param problem_type_filter: The filter, if None, all validator
        classes will be returned.
    """
    classes = []
    
    # Validators from plug-in entry points 
    classes.extend(cone.validation.common.load_plugin_classes(
        'cone.plugins.implvalidators',
        ValidatorBase))
    
    # Built-in validators
    from cone.validation.builtinvalidators.implml import VALIDATOR_CLASSES
    classes.extend(VALIDATOR_CLASSES)
    
    return cone.validation.common.filter_classes(classes, problem_type_filter)

def validate_impl_set(impl_set, configuration, validator_classes=None):
    """
    Validate the given implementation set.
    @param impl_set: The implementations to validate.
    @param configuration: The configuration used in the validation.
    @param validator_classes: The validator classes to use for the validation.
        If None, all validator classes will be used.
    @return: A list of Problem objects.
    """
    context = ValidationContext(configuration)
    context.all_impls = _get_flat_impl_list(impl_set)
    
    if validator_classes is None:
        validator_classes = get_validator_classes()
    
    # Run global validation first
    for vc in validator_classes:
        if issubclass(vc, GlobalValidatorBase):
            try:
                validator = vc(context)
                validator.validate()
            except Exception, e:
                utils.log_exception(logging.getLogger('cone'),
                                    "Error while validating: %s: %s" \
                                    % (e.__class__.__name__, e))
    
    # Then run validation for individual implementations
    for impl in context.all_impls:
        for vc in validator_classes:
            if issubclass(vc, ImplValidatorBase) and isinstance(impl, vc.SUPPORTED_IMPL_CLASSES):
                try:
                    validator = vc(context, impl)
                    validator.validate()
                except Exception, e:
                    utils.log_exception(logging.getLogger('cone'),
                                        "Error validating '%s': %s: %s" \
                                        % (impl, e.__class__.__name__, e))
    return context.problems

def _get_flat_impl_list(impl_set):
    """
    Return a flat list of all implementations in the given set.
    """
    result = []
    def add_to_result(impl):
        result.append(impl)
        if isinstance(impl, plugin.ImplContainer):
            for sub_impl in impl.impls:
                add_to_result(sub_impl)
    for impl in impl_set:
        add_to_result(impl)
    return result

def validate_impls(configuration, filter='.*', validator_classes=None):
    """
    Validate all implementations in the given configuration.
    @param filter: Regex for filtering the implementations to validate.
    @param validator_classes: The validator classes to use for the validation.
        If None, all validator classes will be used.
    """
    # Set up the parse context to collect problems from the parsing phase
    context = ValidationParseContext()
    parsecontext.set_implml_context(context)
    
    impl_set = plugin.get_impl_set(configuration, filter=filter)
    problems = validate_impl_set(impl_set, configuration, validator_classes)
    
    return context.problems + problems
