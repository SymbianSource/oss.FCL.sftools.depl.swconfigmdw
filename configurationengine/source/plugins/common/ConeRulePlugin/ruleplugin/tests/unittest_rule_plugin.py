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
import logging
import __init__

from cone.public import exceptions,plugin,api,container
from cone.storage import filestorage
from ruleplugin import ruleml

# Hardcoded value of testdata folder that must be under the current working dir
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
testdata  = os.path.join(ROOT_PATH,'ruleproject')

class TestRulePlugin(unittest.TestCase):    
    def setUp(self):
        pass
      
    def tearDown(self):
        pass

class TestRulePluginOnFileStorage(unittest.TestCase):    
    def test_get_impl_container(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject/rules')))
        config = project.get_configuration('root.confml')
        implcontainer = plugin.get_impl_set(config, 'ruleml$')
        impl = implcontainer.get_implementations_by_file('implml/rules.ruleml')[0]
        
        self.assertEquals(None, impl.get_refs())
        self.assertEquals([], impl.list_output_files())

    def test_impl_container_execute_pre_rules(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject/rules'), "a" ))
        config = project.get_configuration('root.confml')
        
        implcontainer = plugin.get_impl_set(config, 'ruleml$')
        ruleimpl = implcontainer.get_implementations_by_file('implml/container_with_rules.ruleml')[0]
        context = plugin.GenerationContext()
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
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject/rules'), "a" ))
        config = project.get_configuration('root.confml')
        
        implcontainer = plugin.get_impl_set(config, 'ruleml$')
        implcontainer.generate()
        
        lastconfig = config.get_last_configuration()
        self.assertEquals(lastconfig.get_path(), plugin.AUTOCONFIG_CONFML)
        self.assertEquals(lastconfig.get_data('imakerapi.outputLocation').get_ref(),'outputLocation')
        self.assertEquals(lastconfig.get_data('imakerapi.outputLocation').get_value(),'2')
        project.close()
        
        
if __name__ == '__main__':
    unittest.main()
