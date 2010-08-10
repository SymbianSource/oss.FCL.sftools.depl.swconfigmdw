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

import cone.validation.common

class ValidationContext(object):
    def __init__(self, configuration):
        #: The configuration being validated
        self.configuration = configuration
        
        self._dview = None
        #: The list of validation problems
        self.problems = []
        #: The list of fixes executed in the context
        self.fixes = []
        

    @property
    def dview(self):
        """ 
        The configuration's default view 
        """
        if not self._dview:
            self._dview = self.configuration.get_default_view()
        return self._dview
        
    @property
    def feature_dict(self):
        """
        All the configuration's features as a ref -> feature dictionary. 
        """
        if not hasattr(self, '_feature_dict'):
            self._feature_dict = {}
            for fea in self.dview.get_features('**'):
                self._feature_dict[fea.fqr] = fea
        return self._feature_dict

class ValidatorBase(object):
    #: Types of the problems this validator produces
    PROBLEM_TYPES = None
    
    def __init__(self, context):
        self.context = context
    
    def validate(self):
        """
        Method called to validate a configuration.
        """
        raise NotImplementedError()

class FixerBase(object):
    def fix(self, context):
        """
        The fix functions takes ValidationContext that is expected to contain a 
        list of Problem objects that it will traverse through and it will try to 
        fix any problem that matches its category.
        @param context: The ValidationContext object from which problems should be fixed.  
        """
        raise NotImplementedError()

    def filter_problems(self, problems, problem_type):
        """
        A filtering function that returns a list of problems that match to the 
        given problem_type.
        @param problems: a list of api.Problem objects
        @param problem_type: a string that represents the problem name. e
        .g. 'model.confml.duplicate.setting'.
        """
        return [problem for problem in problems if problem.type == problem_type]

def get_validator_classes(problem_type_filter=None):
    """
    Return a list of all ConfML validator classes that match the given
    problem type filter (i.e. all validator classes that yield problems
    that will not be filtered out).
    
    @param problem_type_filter: The filter, if None, all validator
        classes will be returned.
    """
    classes = []
    
    # Validators from plug-in entry points
    classes.extend(cone.validation.common.load_plugin_classes(
        'cone.plugins.confmlvalidators',
        ValidatorBase))
    
    # Built-in validators
    from cone.validation.builtinvalidators.confml import VALIDATOR_CLASSES
    classes.extend(VALIDATOR_CLASSES)
    
    return cone.validation.common.filter_classes(classes, problem_type_filter)

def get_fixer_classes(problem_type_filter=None):
    """
    Return a list of all ConfML fixer classes that match the given
    problem type filter (i.e. all fixer classes that yield problems
    that will not be filtered out).
    
    @param problem_type_filter: The filter, if None, all fixer
        classes will be returned.
    """
    classes = []
    
    # Validators from plug-in entry points 
    classes.extend(cone.validation.common.load_plugin_classes(
        'cone.plugins.confmlfixers',
        FixerBase))
    
    # Built-in validators 
    from cone.validation.builtinvalidators.confml import FIXER_CLASSES
    classes.extend(FIXER_CLASSES)
    
    return cone.validation.common.filter_classes(classes, problem_type_filter)

def validate_configuration(configuration, validator_classes=None):
    """
    Validate the given configuration.
    @param configuration: The configuration to validate.
    @param validator_classes: The validator classes to use for the validation.
        If None, all validator classes will be used.
    @return: A ValidationContext objects, which contains a list of Problem objects in 
    member variable problems.
    """
    
    if validator_classes is None:
        validator_classes = get_validator_classes()
    
    context = ValidationContext(configuration)
    validators = [vc(context) for vc in validator_classes]
    for validator in validators:
        try:
            validator.validate()
        except Exception, e:
            from cone.public import utils
            utils.log_exception(logging.getLogger('cone'),
                                "Error validating configuration: %s: %s" \
                                % (e.__class__.__name__, e))
    return context

def fix_configuration(configuration, context=None, fixer_classes=None):
    """
    Validate the given configuration.
    @param configuration: The configuration to validate.
    @param context:  The ValidationContext if it has been alread created. With value None
        The ValidationContext will be created and validated fisrt
    @param fixer_classes: The fixer classes to use for the validation.
        If None, all fixer classes will be used.
    @return:  A ValidationContext objects, which contains a list of messaages of fixes that
    were executed.
    """
    
    try:
        conf = configuration.get_configuration('duplicate_settings1.confml')
        data1 = conf.data
    except Exception:
        pass
    if context is None:
        context = validate_configuration(configuration)
    if fixer_classes is None:
        fixer_classes = get_fixer_classes()

    try:
        conf = configuration.get_configuration('duplicate_settings1.confml')
        data2 = conf.data
    except Exception:
        pass
    for fixer in fixer_classes:
        try:
            fixer().fix(context)
        except Exception, e:
            from cone.public import utils
            utils.log_exception(logging.getLogger('cone'),
                                "Error fixing configuration: %s: %s" \
                                % (e.__class__.__name__, e))
    return context
