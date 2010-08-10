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
import logging

from cone.public import plugin,api
from ruleplugin import ruleml
from testautomation.base_testcase import BaseTestCase

# Hardcoded value of testdata folder that must be under the current working dir
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
testdata  = os.path.join(ROOT_PATH,'ruleproject')

class TestRulePlugin(unittest.TestCase):    
    def setUp(self):
        pass
      
    def tearDown(self):
        pass

class TestRulePluginOnFileStorage(BaseTestCase):
    def test_get_impl_container(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject/rules')))
        config = project.get_configuration('root.confml')
        implcontainer = plugin.get_impl_set(config, 'ruleml$')
        impl = implcontainer.get_implementations_by_file('implml/rules.ruleml')[0]
        
        EXPECTED_REFS = ['imaker.imagetarget',
                         'mms.imagesize',
                         'imakerapi.outputLocationY',
                         'operations.minus',
                         'operations.minus1',
                         'operations.minus4',
                         'operations.minus6',
                         'Foo.Bar']
        self.assertEquals(sorted(EXPECTED_REFS), sorted(impl.get_child_refs()))
        self.assertEquals([], impl.list_output_files())

    def test_rules_get_refs(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject/rules'), "a" ))
        config = project.get_configuration('root.confml')
        
        implcontainer = plugin.get_impl_set(config, 'ruleml$')
        ruleimpl = implcontainer.get_implementations_by_file('implml/container_with_rules.ruleml')[0]
        self.assertEquals(ruleimpl.get_child_refs(), [u'imakerapi.PRODUCT_NAME',
                                                      u'imaker.imagetarget'])
        self.assertEquals(len(ruleimpl.get_outputs()), 8)
        outputs = [output.name for output in ruleimpl.get_outputs()]
        self.assertEquals(outputs, [u'imakerapi.PRODUCT_NAME', 
                                    u'imakerapi.outputLocation', 
                                    u'StringConcatenationTest.Result1', 
                                    u'StringConcatenationTest.Result2', 
                                    u'StringConcatenationTest.Result3', 
                                    u'StringConcatenationTest.Result4', 
                                    u'StringConcatenationTest.Result5', 
                                    u'StringConcatenationTest.Result6'])
        inputs = []
        for output in ruleimpl.get_outputs():
            inputs += output.implementation.get_refs()
        self.assertEquals(inputs, [u'imakerapi.PRODUCT_NAME', 
                                   u'imaker.imagetarget'])
        impls_refs = []
        for output in ruleimpl.get_outputs():
            impls_refs.append("%s <= %s" % (output.name, output.implementation.implml.ref))
        self.assertEquals(impls_refs, [u'imakerapi.PRODUCT_NAME <= implml/container_with_rules.ruleml',
                                       u'imakerapi.outputLocation <= implml/container_with_rules.ruleml', 
                                       u'StringConcatenationTest.Result1 <= implml/container_with_rules.ruleml', 
                                       u'StringConcatenationTest.Result2 <= implml/container_with_rules.ruleml', 
                                       u'StringConcatenationTest.Result3 <= implml/container_with_rules.ruleml', 
                                       u'StringConcatenationTest.Result4 <= implml/container_with_rules.ruleml', 
                                       u'StringConcatenationTest.Result5 <= implml/container_with_rules.ruleml', 
                                       u'StringConcatenationTest.Result6 <= implml/container_with_rules.ruleml'])
        
        
    def test_impl_container_execute_pre_rules(self):
        
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject/rules'), "a" ))
        config = project.get_configuration('root.confml')
        
        implcontainer = plugin.get_impl_set(config, 'ruleml$')
        ruleimpl = implcontainer.get_implementations_by_file('implml/container_with_rules.ruleml')[0]
        context = plugin.GenerationContext(configuration=config)
        context.phase = "pre"
        ruleimpl.generate(context)
        
        lastconfig = config.get_last_configuration()
        self.assertEquals(lastconfig.get_path(), plugin.AUTOCONFIG_CONFML)
        self.assertEquals(lastconfig.list_all_datas(),['imakerapi', 
                                                       'imakerapi.outputLocation', 
                                                       'StringConcatenationTest', 
                                                       'StringConcatenationTest.Result1', 
                                                       'StringConcatenationTest.Result2'])
        
        self.assertEquals(lastconfig.get_data('imakerapi.outputLocation').get_ref(),'outputLocation')
        self.assertEquals(lastconfig.get_data('imakerapi.outputLocation').get_value(),'2')
        project.close()

    def test_impl_container_execute_rules(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject/rules'), "r" ))
        config = project.get_configuration('root.confml')
        
        implcontainer = plugin.get_impl_set(config, 'ruleml$')
        context = plugin.GenerationContext(configuration=config)
        implcontainer.generate(context)
        
        lastconfig = config.get_last_configuration()
        self.assertEquals(lastconfig.get_path(), plugin.AUTOCONFIG_CONFML)
        self.assertEquals(lastconfig.get_data('imakerapi.outputLocation').get_ref(),'outputLocation')
        self.assertEquals(lastconfig.get_data('imakerapi.outputLocation').get_value(),'2')
        project.close()
    
    def _prepare_log(self, log_file, level=logging.DEBUG, formatter="%(levelname)s - %(name)s - %(message)s", logger='cone'):
        FULL_PATH = os.path.join(ROOT_PATH, "temp", log_file)
        self.remove_if_exists(FULL_PATH)
        self.create_dir_for_file_path(FULL_PATH)
        
        handler = logging.FileHandler(FULL_PATH)
        handler.setLevel(level)
        frm = logging.Formatter(formatter)
        handler.setFormatter(frm)
        logger = logging.getLogger(logger)
        logger.addHandler(handler)
        
        return [FULL_PATH, handler, logger]
    
    def test_rule_debug_messages(self):
        log_file, handler, logger = self._prepare_log('debug_msg_test.log')
        project = None
        try:
            project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject/rules'), "r" ))
            config = project.get_configuration('root.confml')
            
            implcontainer = plugin.get_impl_set(config, r'rules\.ruleml$')
            context = plugin.GenerationContext(configuration=config)
            implcontainer.generate(context)
            
            self.assert_file_contains(log_file,
                ["Set imakerapi.outputLocationY = 'hello' from ConfigureRelation(ref='implml/rules.ruleml', lineno=8)",
                 "Set operations.minus = 18 from ConfigureRelation(ref='implml/rules.ruleml', lineno=9)",
                 "Set SequenceTest.Sequence1 = [['foo', 1], ['bar', 2], ['baz', 3]] from ConfigureRelation(ref='implml/rules.ruleml', lineno=23)"])
        finally:
            logger.removeHandler(handler)
            if project: project.close()
        
if __name__ == '__main__':
    unittest.main()
