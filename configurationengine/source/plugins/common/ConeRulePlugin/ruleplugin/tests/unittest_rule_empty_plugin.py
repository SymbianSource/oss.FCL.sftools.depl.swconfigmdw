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

from cone.public import exceptions,plugin,api,container
from cone.storage import filestorage
from ruleplugin import ruleml

# Hardcoded value of testdata folder that must be under the current working dir
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
testdata  = os.path.join(ROOT_PATH,'rule')

class TestRuleEmptyPlugin(unittest.TestCase):    
    def setUp(self):
        pass
      
    def tearDown(self):
        pass
        
        
    def test_rule_with_empty_value1(self):
        return
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject/rules'), "a" ))
        config = project.get_configuration('root.confml')
        implcontainer = plugin.get_impl_set(config)
        implcontainer.generate()
        lastconfig = config.get_last_configuration()
        self.assertEquals(lastconfig.get_path(),ruleml.RuleImpl.AUTOCONFIGURATION_CONFML)
        self.assertEquals(lastconfig.get_data('imakerapi.outputLocation').get_ref(),'outputLocation')
        self.assertEquals(lastconfig.get_data('imakerapi.outputLocation').get_value(),'2')
        self.assertEquals(lastconfig.get_data('imakerapi.outputLocationY').get_value(),'hello')
        self.assertEquals(lastconfig.get_data('operations.minus').get_value(),'18')
        self.assertEquals(lastconfig.get_data('operations.minus1').get_value(),'35')
        self.assertEquals(lastconfig.get_data('operations.minus4').get_value(),'5')
        project.close()
    
        
    def test_rule_with_empty_value2(self):
        return
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'rule/config_project/platforms/customsw'), "a" ))
        config = project.get_configuration('root.confml')
        implcontainer = plugin.get_impl_set(config)
        implcontainer.generate()
        lastconfig = config.get_last_configuration()
        self.assertEquals(lastconfig.get_data('operations.minus').get_value(),'18')
        self.assertEquals(lastconfig.get_data('operations.minus1').get_value(),'35')
        self.assertEquals(lastconfig.get_data('operations.minus4').get_value(),'5')
        self.assertEquals(lastconfig.get_data('operations.minus6').get_value(),'19')
        self.assertEquals(lastconfig.get_data('operations.string1').get_value(),'HelloWorld')
        project.close()
        
        
if __name__ == '__main__':
    unittest.main()
