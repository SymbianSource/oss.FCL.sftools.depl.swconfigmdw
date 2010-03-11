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
import __init__
from cone.public import *
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class TestContext(object):
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
        try:
            m = re.match("\${(.*)}", expression)
            if m:
                return self.data[m.group(1)]
            elif expression in ['true','1','True']:
                return True
            elif expression in ['false','0','False']:
                return False
            else:
                return eval(expression)
        except:
            return expression

class TestPluginCondition(unittest.TestCase):
    
    def test_create_plugin_condition(self):
        condition = rules.SimpleCondition("foo.bar", "True")

    def test_create_plugin_and_eval_booleans(self):
        context = TestContext(None)
        condition = rules.SimpleCondition("1", "True")
        self.assertTrue(condition.eval(context))
        condition = rules.SimpleCondition("0", True)
        self.assertFalse(condition.eval(context))

    def test_create_plugin_and_eval_integers(self):
        context = TestContext(None)
        condition = rules.SimpleCondition("1", "2")
        self.assertFalse(condition.eval(context))
        condition = rules.SimpleCondition("112", "2")
        self.assertFalse(condition.eval(context))
        condition = rules.SimpleCondition("2", "2")
        self.assertTrue(condition.eval(context))
        condition = rules.SimpleCondition(2, 2)
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
