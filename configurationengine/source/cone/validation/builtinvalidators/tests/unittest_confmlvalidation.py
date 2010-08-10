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

import os
import unittest

from cone.confml import model
from cone.public import api
from cone.validation.confmlvalidation import ValidationContext, get_validator_classes
from cone.validation.builtinvalidators.confml import  LengthConstraintValidator, DuplicateSettingValidator, DuplicateFeatureValidator

class TestConfmlValidation(unittest.TestCase):
    def test_validations_for_duplicate_setting(self):
        root = model.ConfmlConfiguration("dummy_conf")
        conf1 = root.create_configuration("conf1.confml")
        fea = conf1.create_feature("fea1")
        set1 = model.ConfmlStringSetting("setting1", desc="description one", name="setting")
        fea.add_feature(set1)
        conf2 = root.create_configuration("conf2.confml")
        fea = conf2.create_feature("fea1")
        set2 = model.ConfmlStringSetting("setting1", desc="description two", name="setting new")
        fea.add_feature(set2)

        validator_classes = get_validator_classes()
    
        context = ValidationContext(root)
        validators = [vc(context) for vc in validator_classes]
        for validator in validators:
            validator.validate()
        self.assertEquals(len(context.problems),2, context.problems)
        self.assertEquals(context.problems[0].msg,"Feature fea1.setting1 has '2' definitions in files ['conf1.confml', 'conf2.confml']", context.problems)

    def test_validations_for_lenght_and_duplicate_setting(self):
        root = model.ConfmlConfiguration("dummy_conf")
        conf1 = root.create_configuration("conf1.confml")
        fea = conf1.create_feature("fea1")
        set1 = model.ConfmlStringSetting("setting1", desc="description one", name="setting", length="4")
        fea.add_feature(set1)
        set1.value = "abcdefg"
        conf2 = root.create_configuration("conf2.confml")
        fea = conf2.create_feature("fea1")
        set2 = model.ConfmlStringSetting("setting1", desc="description two", name="setting new")
        fea.add_feature(set2)

        validator_classes = get_validator_classes()
    
        context = ValidationContext(root)
        validators = [vc(context) for vc in validator_classes]
        for validator in validators:
            validator.validate()
        self.assertEquals(len(context.problems),3, context.problems)
        self.assertEquals(context.problems[0].msg,"Setting fea1.setting1: Exact number of characters must be 4 (value has 7)", context.problems)
        self.assertEquals(context.problems[1].msg,"Feature fea1.setting1 has '2' definitions in files ['conf1.confml', 'conf2.confml']", context.problems)


class TestConfmlLenghtValidation(unittest.TestCase):
    def test_length_constraint_validator_with_empty_context(self):
        context = ValidationContext(api.Configuration("foo"))
        valid = LengthConstraintValidator(context)
        valid.validate()
        self.assertEquals(context.problems,[])
        
    def test_length_constraint_validator_with_singe_feature(self):
        conf = model.ConfmlConfiguration("foo")
        fea = model.ConfmlStringSetting("test", length="4")
        conf.add_feature(fea)
        # Test lenght validation
        fea.value= "test mee"
        context = ValidationContext(conf)
        valid = LengthConstraintValidator(context)
        valid.validate()
        self.assertEquals(context.problems[0].type,'model.confml.invalid_value.length')
        # Test minLenght validation
        context.problems = []
        del fea.length
        fea.minLength = 10
        valid.validate()
        self.assertEquals(context.problems[0].type,'model.confml.invalid_value.minlength', context.problems[0])
        # Test maxLenght validation
        context.problems = []
        del fea.minLength
        fea.maxLength = 4
        valid.validate()
        self.assertEquals(context.problems[0].type,'model.confml.invalid_value.maxlength', context.problems[0])
        

class TestConfmlDuplicateSettingValidation(unittest.TestCase):
    def test_duplicate_setting_validator_with_no_duplicates(self):
        conf = model.ConfmlConfiguration("dummy_conf")
        fea = conf.create_feature("fea1")
        set1 = model.ConfmlStringSetting("setting1", desc="description one", name="setting")
        set2 = model.ConfmlStringSetting("setting2", desc="description two", name="setting")
        fea.add_feature(set1)
        fea.add_feature(set2)

        context = ValidationContext(conf)
        valid = DuplicateSettingValidator(context)
        valid.validate()
        self.assertEquals(context.problems,[])

    def test_duplicate_setting_validator_with_duplicates(self):
        root = model.ConfmlConfiguration("dummy_conf")
        conf1 = root.create_configuration("conf1.confml")
        fea = conf1.create_feature("fea1")
        set1 = model.ConfmlStringSetting("setting1", desc="description one", name="setting")
        fea.add_feature(set1)
        conf2 = root.create_configuration("conf2.confml")
        fea = conf2.create_feature("fea1")
        set2 = model.ConfmlStringSetting("setting1", desc="description two", name="setting new")
        fea.add_feature(set2)

        context = ValidationContext(root)
        valid = DuplicateSettingValidator(context)
        valid.validate()
        self.assertEquals(len(context.problems),1, context.problems)
        self.assertEquals(context.problems[0].msg,"Feature fea1.setting1 has '2' definitions in files ['conf1.confml', 'conf2.confml']", context.problems)

class TestConfmlDuplicateFeatureValidation(unittest.TestCase):
    def test_duplicate_feature_validator_with_no_duplicates(self):
        conf = model.ConfmlConfiguration("dummy_conf")
        fea = conf.create_feature("fea1")
        set1 = model.ConfmlStringSetting("setting1", desc="description one", name="setting")
        set2 = model.ConfmlStringSetting("setting2", desc="description two", name="setting")
        fea.add_feature(set1)
        fea.add_feature(set2)

        context = ValidationContext(conf)
        valid = DuplicateFeatureValidator(context)
        valid.validate()
        self.assertEquals(context.problems,[])
    
    def test_duplicate_feature_validator_with_duplicates(self):
        root = model.ConfmlConfiguration("dummy_conf")
        conf1 = root.create_configuration("conf1.confml")
        fea = conf1.create_feature("fea1")
        set1 = model.ConfmlStringSetting("setting1", desc="description one", name="setting")
        fea.add_feature(set1)
        conf2 = root.create_configuration("conf2.confml")
        fea = conf2.create_feature("fea1")
        set2 = model.ConfmlStringSetting("setting2", desc="description two", name="setting new")
        fea.add_feature(set2)

        context = ValidationContext(root)
        valid = DuplicateFeatureValidator(context)
        valid.validate()
        self.assertEquals(len(context.problems),1, context.problems)
        self.assertEquals(context.problems[0].msg,"Feature fea1 has '2' definitions in files ['conf1.confml', 'conf2.confml']", context.problems)

    def test_duplicate_feature_validator_with_sequence_duplicates(self):
        root = model.ConfmlConfiguration("dummy_conf")
        conf1 = root.create_configuration("conf1.confml")
        fea = conf1.create_feature("fea1")
        set1 = model.ConfmlSequenceSetting("setting1", desc="description one", name="setting")
        set1.add_feature(model.ConfmlSetting("sub_setting1", desc="description one", name="sub_setting one"))
        fea.add_feature(set1)
        conf2 = root.create_configuration("conf2.confml")
        fea = conf2.create_feature("fea1")
        set2 = model.ConfmlSequenceSetting("setting1", desc="description one", name="setting")
        set2.add_feature(model.ConfmlSetting("sub_setting1", desc="description two", name="sub_setting two"))
        fea.add_feature(set2)

        context = ValidationContext(root)
        valid = DuplicateFeatureValidator(context)
        valid.validate()
        self.assertEquals(len(context.problems),1, context.problems)
        self.assertEquals(context.problems[0].msg,"Feature fea1 has '2' definitions in files ['conf1.confml', 'conf2.confml']", context.problems)
