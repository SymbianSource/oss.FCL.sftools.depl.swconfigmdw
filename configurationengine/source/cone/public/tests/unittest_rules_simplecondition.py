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
import os
import re
import logging

from cone.public import *
from cone.public.rules import DefaultContext, ASTInterpreter
from cone.confml import model 
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class TestContext(DefaultContext):
    """ DefaultContext implements ConE specific context for handling rules
    """
    def __init__(self, data):
        self.data = data

    def eval(self, ast, expression, value):
        pass

    def get_keys(self, refs):
        return ASTInterpreter.extract_refs(refs)

    def get_children_for_reference(self, reference):
        # implement ConE specific children expansion
        pass

    def handle_terminal(self, expression):
        return self.data[expression]

class TestPluginCondition(unittest.TestCase):
    
    def test_create_plugin_condition(self):
        condition = rules.SimpleCondition("${foo.bar}", "True")
        self.assertTrue(isinstance(condition.left, rules.ReferenceTerminal))
        self.assertEquals(str(condition),'(${foo.bar} => None) == True')

    def test_create_plugin_and_eval_booleans(self):
        context = TestContext(None)
        condition = rules.SimpleCondition("1", "True")
        self.assertTrue(condition.eval(context))
        condition = rules.SimpleCondition("0", True)
        self.assertFalse(condition.eval(context))
    
    def test_create_plugin_and_eval_none(self):
        context = TestContext(None)
        condition = rules.SimpleCondition("None", "None")
        self.assertTrue(condition.eval(context))
        condition = rules.SimpleCondition("None", None)
        self.assertTrue(condition.eval(context))
        condition = rules.SimpleCondition(None, "None")
        self.assertTrue(condition.eval(context))
        condition = rules.SimpleCondition(None, None)
        self.assertTrue(condition.eval(context))
        
        condition = rules.SimpleCondition("True", None)
        self.assertFalse(condition.eval(context))
        condition = rules.SimpleCondition(None, "True")
        self.assertFalse(condition.eval(context))
    
    def test_create_plugin_and_eval_none_from_ref(self):
        context = TestContext({'Foo.Bar': None})
        condition = rules.SimpleCondition("${Foo.Bar}", None)
        self.assertTrue(condition.eval(context))
    
    def test_create_plugin_and_eval_unicode(self):
        context = TestContext({'Foo.Bar': u"foo\u20ac"})
        condition = rules.SimpleCondition("${Foo.Bar}", u"foo\u20ac")
        self.assertTrue(condition.eval(context))
    
    def test_create_plugin_and_eval_number_against_string(self):
        context = TestContext({'Foo.Int': 123,
                               'Foo.Real': 123.4})
        condition = rules.SimpleCondition("${Foo.Int}", "foo")
        self.assertFalse(condition.eval(context))
        condition = rules.SimpleCondition("${Foo.Real}", "foo")
        self.assertFalse(condition.eval(context))
        
        condition = rules.SimpleCondition("${Foo.Int}", "123")
        self.assertTrue(condition.eval(context))
        condition = rules.SimpleCondition("${Foo.Real}", "123.4")
        self.assertTrue(condition.eval(context))

    def xtest_selection_setting(self):
        conf =  api.Configuration("test.confml", namespace="com.nokia.s60")
        
        context = TestContext(None)
        context.configuration = conf
        fea= api.Feature("foo")
        fea.add_feature(api.Feature("child1",type='selection'))
        fea.child1.create_option('one','1')
        fea.child1.create_option('two','2')
        
        conf.add_feature(fea)
        
        fea.child1.add_data(api.Data(value="2"))
        
        condition = rules.SimpleCondition("${fea.child1}", "2")
        self.assertTrue(condition.eval(context))

    def test_sequence_setting(self):
        context = plugin.GenerationContext()
        context.configuration = api.Configuration()
        fea = model.ConfmlSequenceSetting("test")
        fea.add_feature(model.ConfmlIntSetting('child1'))
        fea.add_feature(model.ConfmlIntSetting('child2'))
        fea.add_feature(model.ConfmlIntSetting('child3'))
        context.configuration.add_feature(fea)
        seq = context.configuration.get_default_view().get_feature('test')
        seq.add_sequence(['1','2','3'])
        seq.add_sequence(['4','5','6'])
        seq.add_sequence(['7','8','9'])

        condition = rules.SimpleCondition("${test}", [[1,2,3], [4,5,6], [7,8,9]])
        self.assertTrue(condition.eval(context))

        condition = rules.SimpleCondition("${test}", [['11','22','33'], ['44','55','66'], ['77','88','99']])
        self.assertFalse(condition.eval(context))

    def test_boolean_setting(self):
        context = plugin.GenerationContext()
        context.configuration = api.Configuration()
        context.configuration.add_feature(model.ConfmlBooleanSetting("test"))
        
        context.configuration.get_default_view().test.value = True

        condition = rules.SimpleCondition("${test}", True)
        self.assertTrue(condition.eval(context))

        condition = rules.SimpleCondition("${test}", "zoobar")
        self.assertFalse(condition.eval(context))
        
        condition = rules.SimpleCondition("${test}", "1")
        self.assertFalse(condition.eval(context))

        condition = rules.SimpleCondition("${test}", "true")
        self.assertTrue(condition.eval(context))

        condition = rules.SimpleCondition("${test}", "0")
        self.assertFalse(condition.eval(context))

        condition = rules.SimpleCondition("${test}", "")
        self.assertFalse(condition.eval(context))

        condition = rules.SimpleCondition("${test}", None)
        self.assertFalse(condition.eval(context))

    def test_string_setting(self):
        context = plugin.GenerationContext()
        context.configuration = api.Configuration()
        context.configuration.add_feature(model.ConfmlStringSetting("test"))
        
        context.configuration.get_default_view().test.value = "foobar"

        condition = rules.SimpleCondition("${test}", "foobar")
        self.assertTrue(condition.eval(context))

        condition = rules.SimpleCondition("${test}", "zoobar")
        self.assertFalse(condition.eval(context))
        
        condition = rules.SimpleCondition("${test}", "1")
        self.assertFalse(condition.eval(context))

        condition = rules.SimpleCondition("${test}", "true")
        self.assertFalse(condition.eval(context))

        condition = rules.SimpleCondition("${test}", "false")
        self.assertFalse(condition.eval(context))

        condition = rules.SimpleCondition("${test}", "0")
        self.assertFalse(condition.eval(context))

        condition = rules.SimpleCondition("${test}", "")
        self.assertFalse(condition.eval(context))

        condition = rules.SimpleCondition("${test}", None)
        self.assertFalse(condition.eval(context))

    def test_int_setting(self):
        context = plugin.GenerationContext()
        context.configuration = api.Configuration()
        context.configuration.add_feature(model.ConfmlIntSetting("test"))
        
        context.configuration.get_default_view().test.value = "1"

        condition = rules.SimpleCondition("${test}", "1")
        self.assertTrue(condition.eval(context))

        condition = rules.SimpleCondition("${test}", 2)
        self.assertFalse(condition.eval(context))

        condition = rules.SimpleCondition("${test}", True)
        self.assertTrue(condition.eval(context))

        condition = rules.SimpleCondition("${test}", False)
        self.assertFalse(condition.eval(context))

        condition = rules.SimpleCondition("${test}", 0)
        self.assertFalse(condition.eval(context))

        condition = rules.SimpleCondition("${test}", "zoobar")
        try:
            self.assertFalse(condition.eval(context))
            self.fail("Exception expected.")
        except Exception:
            pass
        
        condition = rules.SimpleCondition("${test}", "")
        try:
            self.assertFalse(condition.eval(context))
            self.fail("Exception expected.")
        except Exception:
            pass

        condition = rules.SimpleCondition("${test}", None)
        self.assertFalse(condition.eval(context))

        context.configuration.get_default_view().test.value = "-1"
        
        condition = rules.SimpleCondition("${test}", -1)
        self.assertTrue(condition.eval(context))
        
        condition = rules.SimpleCondition("${test}", 0)
        self.assertFalse(condition.eval(context))
        
    def test_selection_setting_true(self):
        context = plugin.GenerationContext()
        context.configuration = api.Configuration()
        context.configuration.add_feature(model.ConfmlSelectionSetting("test"))
        
        context.configuration.get_default_view().test.value = "True"

        condition = rules.SimpleCondition("${test}", "True")
        self.assertTrue(condition.eval(context))

        condition = rules.SimpleCondition("${test}", True)
        self.assertTrue(condition.eval(context))
        
        condition = rules.SimpleCondition("${test}", "1")
        self.assertFalse(condition.eval(context))

    def test_selection_setting_false(self):
        context = plugin.GenerationContext()
        context.configuration = api.Configuration()
        context.configuration.add_feature(model.ConfmlSelectionSetting("test"))
        
        context.configuration.get_default_view().test.value = "False"

        condition = rules.SimpleCondition("${test}", False)
        self.assertTrue(condition.eval(context))
        
        condition = rules.SimpleCondition("${test}", "False")
        self.assertTrue(condition.eval(context))
        
        condition = rules.SimpleCondition("${test}", "0")
        self.assertFalse(condition.eval(context))

        condition = rules.SimpleCondition("False", "0")
        self.assertFalse(condition.eval(context))

    def test_selection_setting_int(self):
        context = plugin.GenerationContext()
        context.configuration = api.Configuration()
        context.configuration.add_feature(model.ConfmlSelectionSetting("test"))

        context.configuration.get_default_view().test.value = "2"
        
        condition = rules.SimpleCondition("${test}", "2")
        self.assertTrue(condition.eval(context))

        condition = rules.SimpleCondition("${test}", 2)
        self.assertTrue(condition.eval(context))

    def test_create_plugin_and_eval_integers(self):
        context = TestContext(None)
        condition = rules.SimpleCondition("1", "2")
        self.assertFalse(condition.eval(context))
        condition = rules.SimpleCondition("112", "2")
        self.assertFalse(condition.eval(context))
        condition = rules.SimpleCondition("2", "2")
        self.assertTrue(condition.eval(context))
        condition = rules.SimpleCondition("2", 2)
        self.assertTrue(condition.eval(context))
        condition = rules.SimpleCondition(2, 2)
        self.assertTrue(condition.eval(context))
        condition = rules.SimpleCondition("-2", -2)
        self.assertTrue(condition.eval(context))

    def test_create_plugin_and_eval_string(self):
        context = TestContext(None)
        condition = plugin.rules.SimpleCondition("test", "foo")
        self.assertFalse(condition.eval(context))
        condition = rules.SimpleCondition("test", "")
        self.assertFalse(condition.eval(context))
        condition = rules.SimpleCondition("test foo", "test foo")
        self.assertTrue(condition.eval(context))

    def test_create_plugin_and_eval_data_reference(self):
        context = TestContext({'test' : 1, 'foo' : 2, 'bar' : True})
        condition = rules.SimpleCondition("${test}", 1)
        condition.eval(context)
        self.assertTrue(condition.eval(context))
        condition = rules.SimpleCondition("${test}", False)
        self.assertFalse(condition.eval(context))
        condition = rules.SimpleCondition("${test}", "${foo}")
        self.assertFalse(condition.eval(context))
        condition = rules.SimpleCondition("${test}", "${bar}")
        self.assertTrue(condition.eval(context))
        
    def test_create_plugin_and_eval_data_reference_on_generation_context(self):
        context = plugin.GenerationContext()
        context.configuration = api.Configuration()
        context.configuration.add_feature(api.Feature("test"))
        context.configuration.add_feature(api.Feature("stringsub"),"test")
        context.configuration.add_feature(api.Feature("intsub"),"test")
        condition = rules.SimpleCondition("${test}", None)
        self.assertTrue(condition.eval(context))
        condition = rules.SimpleCondition("${test.stringsub}", "None")
        condition.eval(context)
        self.assertTrue(condition.eval(context))
        condition = rules.SimpleCondition("${test.intsub}", "None")
        self.assertTrue(condition.eval(context))
        context.configuration.get_default_view().test.value = True
        context.configuration.get_default_view().test.stringsub.value = "stringval"
        context.configuration.get_default_view().test.intsub.value = 2
        condition = rules.SimpleCondition("${test}", "true")
        self.assertTrue(condition.eval(context))
        condition = rules.SimpleCondition("${test}", "false")
        self.assertFalse(condition.eval(context))
        condition = rules.SimpleCondition("${test.stringsub}", "tes")
        self.assertFalse(condition.eval(context))
        condition = rules.SimpleCondition("${test.stringsub}", "stringval")
        self.assertTrue(condition.eval(context))
        condition = rules.SimpleCondition("${test.intsub}", "1")
        self.assertFalse(condition.eval(context))
        condition = rules.SimpleCondition("${test.intsub}", "2")
        self.assertTrue(condition.eval(context))
        condition = rules.SimpleCondition("${test.intsub}", 2)
        self.assertTrue(condition.eval(context))
        condition = rules.SimpleCondition("${test.intsub}", 1)
        self.assertFalse(condition.eval(context))
        try:
            condition = rules.SimpleCondition("${boo}", "false")
            self.fail("access of non existing elements succeds?")
        except:
            pass

if __name__ == '__main__':
    unittest.main()
