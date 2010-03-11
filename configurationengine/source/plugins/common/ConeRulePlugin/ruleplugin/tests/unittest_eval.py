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
import re

import __init__

from ruleplugin import ruleml, relations
from cone.public import api, exceptions
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class MockObject(object):
    pass

class MockFeature(object):
    def __init__(self, ref, feature_values):
        self.ref = ref
        self.feature_values = feature_values
    
    def get_value(self):
        return self.feature_values[self.ref]
    
    def set_value(self, value):
        self.feature_values[self.ref] = value

class MockConfigurationContext(object):
    def __init__(self, feature_values):
        self.data = MockObject()
        default_view = MockObject()
        default_view.get_feature = lambda ref: MockFeature(ref, feature_values)
        self.data.get_default_view = lambda: default_view
        self.ref_eval_callback = None

class MockExpression(object):
    def __init__(self, expression):
        self.expression = repr(expression)

class TestEvalExpression(unittest.TestCase):
    def test_extract_refs(self):
        ee = relations.EvalExpression(
            None, MockExpression("'%05d 0x%08X %d' % (${Feature1.Setting1}.get_value(), ${Feature1.Setting2}.get_value(), ${Feature2.Setting1}.get_value())"))
        self.assertEquals(sorted(ee.extract_refs()), sorted(["Feature1.Setting1", "Feature1.Setting2", "Feature2.Setting1"]))
        
        ee = relations.EvalExpression(None, MockExpression("'%05d 0x%08X %d' % (1, 2, 3)"))
        self.assertEquals(ee.extract_refs(), [])
        
        ee = relations.EvalExpression(None, MockExpression(u"${ударения.ελληνικά}"))
        self.assertEquals(ee.extract_refs(), [u'ударения.ελληνικά'])
    
    def test_execute(self):
        feature_values = {
            "Feature1.Setting1":  16,
            "Feature1.Setting2":  32,
            "Feature2.Setting1":  64,
            u'ударения.ελληνικά': 100,
        }
        context = MockConfigurationContext(feature_values)
        
        ee = relations.EvalExpression(None,
            MockExpression("'%05d 0x%08X %d' % (@{Feature1.Setting1}.get_value(), @{Feature1.Setting2}.get_value(), @{Feature2.Setting1}.get_value())"))
        self.assertEquals(ee.eval(context), "00016 0x00000020 64")
        
        ee = relations.EvalExpression(None, MockExpression("'%05d 0x%08X %d' % (1, 2, 3)"))
        self.assertEquals(ee.eval(context), "00001 0x00000002 3")
        
        ee = relations.EvalExpression(None, MockExpression(u"'%d' % @{ударения.ελληνικά}.get_value()"))
        self.assertEquals(ee.eval(context), "100")

class TestReplaceEvalBlocks(unittest.TestCase):
    def test_replace_eval_blocks(self):
        replace = ruleml.RuleImplReader2._replace_eval_blocks
        
        orig = """some.setting configures x = y"""
        self.assertEquals(replace(orig), orig)
        
        orig = """some.setting configures x = {% do_something(@{Fea.Set}) %}"""
        self.assertEquals(replace(orig), """some.setting configures x = __eval__ 'do_something(@{Fea.Set})'""")
        
        orig = """{% 'test' %}"""
        self.assertEquals(replace(orig), '''__eval__ "'test'"''')
        orig = """{%'test'%}"""
        self.assertEquals(replace(orig), '''__eval__ "'test'"''')
        
        orig = """{% len(@{Fea.Set}.get_value()) %} == 3 configures x = {% do_something('test') %}"""
        self.assertEquals(replace(orig), '''__eval__ 'len(@{Fea.Set}.get_value())' == 3 configures x = __eval__ "do_something('test')"''')
        
        orig = u"True configures X.Y = {% len(@{ударения.ελληνικά}.get_value()) %}"
        self.assertEquals(replace(orig), u"True configures X.Y = __eval__ %r" % u"len(@{ударения.ελληνικά}.get_value())")
        
if __name__ == "__main__":
    unittest.main()
