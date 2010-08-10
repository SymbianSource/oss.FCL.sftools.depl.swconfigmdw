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

from cone.public import api, exceptions, container, utils
from cone.confml import model

from cone.validation.confmlvalidation import ValidatorBase, FixerBase

class SettingValidatorBase(ValidatorBase):
    """
    Base class for validators that validate ConfML settings
    (sub-classes of cone.confml.model.ConfmlSetting).
    """
    def validate(self):
        for ref, feature in self.context.feature_dict.iteritems():
            if isinstance(feature._obj, model.ConfmlSetting):
                self.validate_setting(ref, feature)
    
    def validate_setting(self, ref, setting):
        raise NotImplementedError()

class LengthConstraintValidator(SettingValidatorBase):
    """
    Validator for validating xs:length, xs:minLength and xs:maxLength
    constraints on setting data values.
    """
    PROBLEM_TYPES = ['model.confml.invalid_value.length',
                     'model.confml.invalid_value.minlength',
                     'model.confml.invalid_value.maxlength']
    
    def validate_setting(self, ref, setting):
        if setting.length:
            value = setting.get_value()
            if isinstance(value, basestring) and len(value) != setting.length:
                self._add_problem(
                    setting = setting,
                    msg = "Setting %s: Exact number of characters must be %s (value has %s)" % (ref, setting.length, len(value)),
                    prob_type = self.PROBLEM_TYPES[0])
                
        if setting.minLength:
            value = setting.get_value()
            if isinstance(value, basestring) and len(value) < setting.minLength:
                self._add_problem(
                    setting = setting,
                    msg = "Setting %s: Minimum number of characters is %s (value has %s)" % (ref, setting.minLength, len(value)),
                    prob_type = self.PROBLEM_TYPES[1])
        
        if setting.maxLength:
            value = setting.get_value()
            if isinstance(value, basestring) and len(value) > setting.maxLength:
                self._add_problem(
                    setting = setting,
                    msg = "Setting %s: Maximum number of characters is %s (value has %s)" % (ref, setting.maxLength, len(value)),
                    prob_type = self.PROBLEM_TYPES[2])
   
    def _add_problem(self, setting, msg, prob_type):
        dataobj = setting.datas['data'][-1]
        prob = api.Problem(
            msg = msg,
            type = prob_type,
            line = dataobj.lineno,
            file = dataobj.get_configuration_path())
        self.context.problems.append(prob)

class MissingFeatureForDataValidator(ValidatorBase):
    """
    Validator for validating data elements that do not have a
    corresponding feature/setting in the configuration.
    """
    PROBLEM_TYPES = ['model.confml.missing_feature_for_data']
    
    def validate(self):
        for dataobj in self.context.configuration._traverse(type=api.Data):
            try:
                self.context.dview.get_feature(dataobj.fqr)
            except exceptions.NotFound:
                prob = api.Problem(
                    msg = "Feature '%s' not found" % dataobj.fqr,
                    type = self.PROBLEM_TYPES[0],
                    line = dataobj.lineno,
                    file = dataobj.get_configuration_path())
                self.context.problems.append(prob)

class MissingDescriptionValidator(SettingValidatorBase):
    """
    Validator for validating missing descriptions in feature/setting in the configuration.
    """
    PROBLEM_TYPES = ['model.confml.missing_desc']
    
    def validate_setting(self, ref, setting):
        print 'Validating missing desc!'
        if not setting.desc or setting.desc == '':
            prob = api.Problem(
                msg = "Setting/Feature %s: has no description" % (ref),
                type = self.PROBLEM_TYPES[0],
                line = setting.lineno,
                file = setting.get_configuration_path(),
                severity = api.Problem.SEVERITY_WARNING)
            self.context.problems.append(prob)

class DuplicateSettingValidator(ValidatorBase):
    """
    Validator for validating that there are no settings with same ref in given 
    configuration.
    """
    PROBLEM_TYPES = ['model.confml.duplicate.setting']
    
    def validate(self):
        settings_container = container.DataContainer()
        # Traverse through the configuration model and store each feature to 
        # the settings_container. 
        for setting in self.context.configuration._traverse(type=model.ConfmlSetting):
            settings_container.add_value(setting.fqr, setting)
        # Go though the settings_container to see if any features have more than one 
        # definition and report those as problems
        for fqr in settings_container.list_keys():
            if len(settings_container.get_values(fqr)) > 1:
                files = [setting.get_configuration_path() for setting in settings_container.get_values(fqr)]
                prob = api.Problem(
                    msg = "Feature %s has '%s' definitions in files %s" % (fqr, len(settings_container.get_values(fqr)), files),
                    type = self.PROBLEM_TYPES[0],
                    severity = api.Problem.SEVERITY_WARNING, 
                    line = settings_container.get_value(fqr).lineno,
                    file = files[-1],
                    problem_data = settings_container.get_values(fqr))
                self.context.problems.append(prob)

class DuplicateFeatureValidator(ValidatorBase):
    """
    Validator for validating that there are no features with same ref in given 
    configuration.
    """
    PROBLEM_TYPES = ['model.confml.duplicate.feature']
    
    def validate(self):
        settings_container = container.DataContainer()
        # Traverse through the configuration model and store each feature to 
        # the settings_container. 
        for setting in self.context.configuration._traverse(type=model.ConfmlFeature):
            settings_container.add_value(setting.fqr, setting)
        # Go though the settings_container to see if any features have more than one 
        # definition and report those as problems
        for fqr in settings_container.list_keys():
            if len(settings_container.get_values(fqr)) > 1:
                files = [setting.get_configuration_path() for setting in settings_container.get_values(fqr)]
                prob = api.Problem(
                    msg = "Feature %s has '%s' definitions in files %s" % (fqr, len(settings_container.get_values(fqr)), files),
                    type = self.PROBLEM_TYPES[0],
                    severity = api.Problem.SEVERITY_INFO,
                    line = settings_container.get_value(fqr).lineno,
                    file = files[-1],
                    problem_data = settings_container.get_values(fqr))
                self.context.problems.append(prob)

class DuplicateSettingFixer(FixerBase):
    """
    A Fix class for duplicate settings that removes all but the last definition of the element.
    """
    PROBLEM_TYPES = ['model.confml.duplicate.setting']

    def fix(self, context):
        for problem in self.filter_problems(context.problems, self.PROBLEM_TYPES[0]):
            logging.getLogger('cone.validation').info("Fixing problem %s" % problem.msg)
            context.fixes.append("Fixed problem: %s" % problem.msg)
            # The problem data is expected to have those duplicate settings and the 
            # actual setting as a last element
            for setting in problem.problem_data[0:-1]:
                parent_fea = setting.find_parent(type=api.Feature)
                logging.getLogger('cone.validation').info("Remove setting %s from %s" % (setting.fqr, parent_fea.get_configuration_path()))
                try:
                    parent_fea.remove_feature(setting.ref)
                except exceptions.NotFound:
                    logging.getLogger('cone.validation').info("Already removed %s from %s" % (setting.ref, parent_fea.get_configuration_path()))

class DuplicateFeatureFixer(FixerBase):
    """
    A Fix class for duplicate features that merges all setting under a duplicate feature 
    to the first instance of the feature and removes the duplicates.
    """
    PROBLEM_TYPES = ['model.confml.duplicate.feature']

    def fix(self, context):
        for problem in self.filter_problems(context.problems, self.PROBLEM_TYPES[0]):
            logging.getLogger('cone.validation').info("Fixing problem %s" % problem.msg)
            context.fixes.append("Fixed problem: %s" % problem.msg)
            # The problem data is expected to have those duplicate settings and the 
            # actual setting as a last element
            target_feature = problem.problem_data[0]
            target_config = target_feature.find_parent(type=api.Configuration)
            for feature in problem.problem_data[1:]:
                logging.getLogger('cone.validation').info("Move settings from Feature %s in %s to %s" % \
                                                          (feature.fqr, feature.get_configuration_path(), target_feature.get_configuration_path()))
                for setting_ref in feature.list_features():
                    setting = feature.get_feature(setting_ref)
                    # Get the path from feature to the parent of this setting
                    # (pathto,ref) = utils.dottedref.psplit_ref(setting_ref)
                    if target_feature.has_ref(setting_ref):
                        target_feature.remove_feature(setting_ref)
                    target_feature.add_feature(setting)
                    
                config = feature.find_parent(type=api.Configuration)
                logging.getLogger('cone.validation').info("Remove feature %s from %s" % (feature.fqr, config.get_full_path()))
                config.remove_feature(feature.ref)

                
#: List of all built-in ConfML validator classes
VALIDATOR_CLASSES = [
    MissingFeatureForDataValidator,
    LengthConstraintValidator,
    DuplicateSettingValidator,
    DuplicateFeatureValidator,
#    MissingDescriptionValidator,
]

#: List of all built-in ConfML fixer classes
FIXER_CLASSES = [
    DuplicateFeatureFixer,
]
