# *-* coding: utf-8 *-*
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
import os, shutil
import sys
# import legacyruleplugin_testinit

from legacyruleplugin import ruleml
from cone.public import api, plugin
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class TestRuleExecutes(unittest.TestCase):
    
    def setUp(self):
        self.project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject/rules')))
        self.config = self.project.get_configuration('root.confml')
    
    def tearDown(self):
        self.project.close()
    
    def _execute_rules(self, impl_filter):
        implcontainer = plugin.get_impl_set(self.config, impl_filter)
        context = plugin.GenerationContext(configuration=self.config)
        implcontainer.generate(context)
        return context.generation_output
    
    def test_arithmetic_operations(self):
        self._execute_rules(r'^implml/arithmetic\.ruleml$')
        
        # Values used in the ConfML (the calculations are duplicated here to make
        # the tests more readable)
        value1 = 5
        value2 = 20
        config = self.config
        self.assert_setting_equals(config, 'Arithmetic.AdditionResult1', 2 + 6)
        self.assert_setting_equals(config, 'Arithmetic.AdditionResult2', value1 + 6)
        self.assert_setting_equals(config, 'Arithmetic.AdditionResult3', 2 + value2)
        self.assert_setting_equals(config, 'Arithmetic.AdditionResult4', value1 + value2)
        
        self.assert_setting_equals(config, 'Arithmetic.SubtractionResult1', 2 - 6)
        self.assert_setting_equals(config, 'Arithmetic.SubtractionResult2', value1 - 6)
        self.assert_setting_equals(config, 'Arithmetic.SubtractionResult3', 2 - value2)
        self.assert_setting_equals(config, 'Arithmetic.SubtractionResult4', value1 - value2)
        
        self.assert_setting_equals(config, 'Arithmetic.MultiplicationResult1', 2 * 6)
        self.assert_setting_equals(config, 'Arithmetic.MultiplicationResult2', value1 * 6)
        self.assert_setting_equals(config, 'Arithmetic.MultiplicationResult3', 2 * value2)
        self.assert_setting_equals(config, 'Arithmetic.MultiplicationResult4', value1 * value2)
        
        self.assert_setting_equals(config, 'Arithmetic.DivisionResult1', 6 / 2)
        self.assert_setting_equals(config, 'Arithmetic.DivisionResult2', value2 / 4)
        self.assert_setting_equals(config, 'Arithmetic.DivisionResult3', 10 / value1)
        self.assert_setting_equals(config, 'Arithmetic.DivisionResult4', value2 / value1)
        
        self.assert_setting_equals(config, 'Arithmetic.MixedResult1', (6 / 2 + 3 * 9) - 7)
        self.assert_setting_equals(config, 'Arithmetic.MixedResult2', (6 / 2 + value1 * 9) - 7)
        self.assert_setting_equals(config, 'Arithmetic.MixedResult3', (value2 / 2 + value1 * 9) - 7)
        self.assert_setting_equals(config, 'Arithmetic.MixedResult4', (value2 / value1 + value1 * value1) - value2)
        self.assert_setting_equals(config, 'Arithmetic.MixedResult5', 4 + 6 / 2 - 3 * 9 + 10 / 5 - 8)
        
        rvalue1 = float(value1)
        rvalue2 = float(value2)
        self.assert_setting_equals(config, 'Arithmetic.RealResult1', 5.0 / 2.0)
        self.assert_setting_equals(config, 'Arithmetic.RealResult2', rvalue1 / 2.0)
        self.assert_setting_equals(config, 'Arithmetic.RealResult3', 0.25 * rvalue2)
        self.assert_setting_equals(config, 'Arithmetic.RealResult4', rvalue1 / 2.0 * rvalue2)
#
        self.assert_setting_equals(config, 'Arithmetic.RealCalcIntoIntResult', int(0.25 * rvalue1))
        self.assert_setting_equals(config, 'Arithmetic.IntCalcIntoRealResult', float(3 * value1))
    
    def test_string_concatenation(self):
        self._execute_rules(r'^implml/rules\.ruleml$')
        
        config = self.config
        self.assert_setting_equals(config, 'StringConcatenationTest.Result1', 'Test test')
        self.assert_setting_equals(config, 'StringConcatenationTest.Result2', 'String 1 Literal 2')
        self.assert_setting_equals(config, 'StringConcatenationTest.Result3', 'Literal 1 String 2')
        self.assert_setting_equals(config, 'StringConcatenationTest.Result4', 'String 1String 2')
        self.assert_setting_equals(config, 'StringConcatenationTest.Result5', 'String 1 & String 2')
        self.assert_setting_equals(config, 'StringConcatenationTest.Result6', u'String 1 € カタカナ')
        
        self.assert_setting_equals(config, u'ударения.ελληνικά', u'カタカナ € カタカナ')
        
    
    def test_filenamejoin(self):
        self._execute_rules(r'^implml/filename_rules\.ruleml$')
        
        config = self.config
        self.assert_setting_equals(config, 'FilenamejoinTest.Result1', r'Z:\\data\\file1.txt')
        self.assert_setting_equals(config, 'FilenamejoinTest.Result2', r'some/content/dir/file1.txt')
        self.assert_setting_equals(config, 'FilenamejoinTest.Result3', r'some/content/dir/file1.txt')
        self.assert_setting_equals(config, 'FilenamejoinTest.Result4', r'some\content\dir\file1.txt')
        self.assert_setting_equals(config, 'FilenamejoinTest.Result5', r'some\content\dir\file1.txt')
        self.assert_setting_equals(config, 'FilenamejoinTest.Result6', r'Z:\\some\\content\\dir\\file1.txt')
        self.assert_setting_equals(config, 'FilenamejoinTest.Result7', r'Z:\\some\\content\\dir\\file1.txt')
        self.assert_setting_equals(config, 'FilenamejoinTest.Result8', r'somedir/file1.txt')
        self.assert_setting_equals(config, 'FilenamejoinTest.Result9', r'somedir/somefile.txt')
        self.assert_setting_equals(config, 'FilenamejoinTest.Result10', r'somedir/somefile.txt;Z:\\some\\dir\\file1.txt')
        self.assert_setting_equals(config, 'FilenamejoinTest.Result11', r'somedir/somefile.txt')
    
    def test_comparison_operators(self):
        self._execute_rules(r'^implml/comparison_operators\.ruleml$')
        
        for i in xrange(1, 8):
            ref = 'CompOperTest.LiteralsResult%d' % i
            self.assert_setting_equals(self.config, ref, True, "Setting %s is not True" % ref)
        
        for i in xrange(1, 8):
            ref = 'CompOperTest.RefsResult%d' % i
            self.assert_setting_equals(self.config, ref, True, "Setting %s is not True" % ref)
    
    def test_eval(self):
        config = self.config
        
        self.assert_setting_equals(config, 'EvalTest.FullSequence',
            [['Full 1', 10, 1.5, True],
             ['Full 2', 20, 2.5, False]])
        
        self._execute_rules(r'^implml/eval\.ruleml$')
        
        self.assert_setting_equals(config, 'EvalTest.StringLenResult', 8)
        self.assert_setting_equals(config, 'EvalTest.EvalConstantResult', 12345)
        self.assert_setting_equals(config, 'EvalTest.EvalFileImport', 12346)
        self.assert_setting_equals(config, 'EvalTest.UnchangedValue', 0)
        self.assert_setting_equals(config, 'EvalTest.UnicodeResult1', u'100€')
        self.assert_setting_equals(config, 'EvalTest.UnicodeResult2', u'カタカナ')
        self.assert_setting_equals(config, 'EvalTest.Bit0Result', False)
        self.assert_setting_equals(config, 'EvalTest.Bit1Result', True)
        self.assert_setting_equals(config, 'EvalTest.Bit2Result', False)
        self.assert_setting_equals(config, 'EvalTest.Bit3Result', True)
        self.assert_setting_equals(config, 'EvalTest.FullSequence',
            [['Full 1', 10, 1.5, True],
             ['Full 2', 20, 2.5, False],
             ['Stripped 1', 1, 0.1, False],
             ['Stripped 2', 2, 0.1, False]])
        self.assert_setting_equals(config, 'EvalTest.EvalBuiltinResult', 'ruleml_test_config')
    
    def assert_setting_equals(self, config, setting, expected_value, msg=None):
        if msg == None:
            self.assertEquals(config.get_default_view().get_feature(setting).get_value(), expected_value)
        else:
            self.assertEquals(config.get_default_view().get_feature(setting).get_value(), expected_value, msg)
    
    def test_rule_execution_results(self):
        results = self._execute_rules(r'^implml/rules\.ruleml$')
        
        outputs = [(output.name, output.implementation.get_refs()) for output in results if output.type == 'ref']  
        self.assertEquals(outputs, [(u'imakerapi.outputLocation', [u'imaker.imagetarget']), 
                                   (u'imakerapi.outputLocationY', [u'imakerapi.outputLocationY']), 
                                   (u'operations.minus', [u'operations.minus']), 
                                   (u'operations.minus1', [u'operations.minus1']), 
                                   (u'operations.minus4', [u'operations.minus4']), 
                                   (u'operations.minus6', [u'operations.minus6']), 
                                   (u'StringConcatenationTest.Result1', []), 
                                   (u'StringConcatenationTest.Result2', []), 
                                   (u'StringConcatenationTest.Result3', []), 
                                   (u'StringConcatenationTest.Result4', []), 
                                   (u'StringConcatenationTest.Result5', []), 
                                   (u'StringConcatenationTest.Result6', []), 
                                   (u'\u0443\u0434\u0430\u0440\u0435\u043d\u0438\u044f.\u03b5\u03bb\u03bb\u03b7\u03bd\u03b9\u03ba\u03ac', [])]) 
            
if __name__ == '__main__':
    unittest.main()
