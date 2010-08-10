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

import unittest

from cone.confml import model
from cone.public import api
from cone.validation.confmlvalidation import ValidationContext
from cone.validation.builtinvalidators import confml 

class TestConfmlDuplicateSettingFix(unittest.TestCase):
    def test_duplicate_setting_fix_with_duplicates(self):
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
        valid = confml.DuplicateSettingValidator(context)
        valid.validate()
        self.assertEquals(len(context.problems),1, context.problems)
        self.assertEquals(context.problems[0].msg,"Feature fea1.setting1 has '2' definitions in files ['conf1.confml', 'conf2.confml']", context.problems)
        fixer = confml.DuplicateSettingFixer()
        fixer.fix(context)
        
        # revalidation should now report no problems
        context = ValidationContext(root)
        valid = confml.DuplicateSettingValidator(context)
        valid.validate()
        self.assertEquals(len(context.problems),0, context.problems)

        
class TestConfmlDuplicateFeatureFix(unittest.TestCase):
    def test_duplicate_setting_fix_with_duplicates(self):
        root = model.ConfmlConfiguration("dummy_conf")
        conf1 = root.create_configuration("conf1.confml")
        fea = conf1.create_feature("fea1")
        set1 = model.ConfmlStringSetting("setting1", desc="description one", name="setting")
        fea.add_feature(set1)
        conf2 = root.create_configuration("conf2.confml")
        fea = conf2.create_feature("fea1")
        set2 = model.ConfmlStringSetting("setting2", desc="description two", name="setting new")
        fea.add_feature(set2)
        self.assertEquals(conf1.list_all_features(),['fea1','fea1.setting1'])
        
        context = ValidationContext(root)
        valid = confml.DuplicateFeatureValidator(context)
        valid.validate()
        self.assertEquals(len(context.problems),1, context.problems)
        self.assertEquals(context.problems[0].msg,"Feature fea1 has '2' definitions in files ['conf1.confml', 'conf2.confml']", context.problems)
        fixer = confml.DuplicateFeatureFixer()
        fixer.fix(context)
        
        # revalidation should now report no problems
        context = ValidationContext(root)
        valid = confml.DuplicateFeatureValidator(context)
        valid.validate()
        self.assertEquals(len(context.problems),0, context.problems)
        self.assertEquals(conf1.list_all_features(),['fea1','fea1.setting1','fea1.setting2'])
        self.assertEquals(conf2.list_all_features(),[])


    def test_duplicate_setting_fix_with_duplicates_with_options(self):
        root = model.ConfmlConfiguration("dummy_conf")
        conf1 = root.create_configuration("conf1.confml")
        fea = conf1.create_feature("fea1")
        set1 = model.ConfmlStringSetting("setting1", desc="description one", name="setting")
        set1.add(api.Option('op1','val1'))
        set1.add(api.Option('op2','val2'))
        fea.add_feature(set1)
        conf2 = root.create_configuration("conf2.confml")
        fea = conf2.create_feature("fea1")
        set2 = model.ConfmlStringSetting("setting1", desc="description two", name="setting new")
        set2.add(api.Option('op3','val3'))
        set2.add(api.Option('op4','val4'))
        fea.add_feature(set2)
        
        context = ValidationContext(root)
        valid = confml.DuplicateFeatureValidator(context)
        valid.validate()
        fixer = confml.DuplicateFeatureFixer()
        fixer.fix(context)
                
        set1 = conf1.get_feature('fea1').get_feature('setting1')
        options = set1.options
        self.assertEquals(len(options),2,'After fix only options from new setting should be preserved')
        self.assertEquals(options['val3'].name,'op3')
        self.assertEquals(options['val4'].name,'op4')
        

    def test_duplicate_feature_fixer_with_sequence_duplicates(self):
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
        valid = confml.DuplicateFeatureValidator(context)
        valid.validate()

        self.assertEquals(len(context.problems),1, context.problems)
        self.assertEquals(context.problems[0].msg,"Feature fea1 has '2' definitions in files ['conf1.confml', 'conf2.confml']", context.problems)
        fixer = confml.DuplicateFeatureFixer()
        fixer.fix(context)
        
        # revalidation should now report no problems
        context = ValidationContext(root)
        valid = confml.DuplicateFeatureValidator(context)
        valid.validate()
        self.assertEquals(len(context.problems),0, context.problems)
        self.assertEquals(conf1.list_all_features(),['fea1',
                                                     'fea1.setting1',
                                                     'fea1.setting1.sub_setting1'])
        self.assertEquals(conf2.list_all_features(),[])
        
        