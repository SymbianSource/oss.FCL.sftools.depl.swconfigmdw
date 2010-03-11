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
try:
    from cElementTree import ElementTree
except ImportError:
    try:    
        from elementtree import ElementTree
    except ImportError:
        try:
            from xml.etree import cElementTree as ElementTree
        except ImportError:
            from xml.etree import ElementTree

import __init__

from ruleplugin import ruleml, relations
from cone.public import api, exceptions, utils, plugin
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

ruleml_string = \
'''<?xml version="1.0" encoding="UTF-8"?>
<ruleml xmlns="http://www.s60.com/xml/ruleml/2">
  <rule>imaker.imagetarget configures imakerapi.outputLocation = imaker.imagetarget</rule>
  <rule>imaker.imagename configures imakerapi.outputLocation = imaker.imagename</rule>
</ruleml>
'''

class TestParseRuleimpl(unittest.TestCase):    
    def setUp(self):    relations.register()
    def tearDown(self): relations.unregister()
    
    def test_parse_rules(self):
        etree = ElementTree.fromstring(ruleml_string)
        reader = ruleml.RuleImplReader2(None, None)
        rules = reader.parse_rules(etree)
        self.assertTrue(isinstance(rules[0],relations.ConfigureRelation))
        self.assertTrue(isinstance(rules[1],relations.ConfigureRelation))
        self.assertTrue(rules[0].has_ref('imaker.imagetarget'))
        self.assertFalse(rules[0].has_ref('imakerapi.imagename'))
        self.assertTrue(rules[0].has_ref('imakerapi.outputLocation'))


class TestRulemlFromFile(unittest.TestCase):
    def setUp(self):    pass
    def tearDown(self): relations.unregister()
    
    def test_create_from_file(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject/rules')))
        config = project.get_configuration('root.confml')
        ruleimpl = plugin.ImplFactory.get_impls_from_file('implml/rules.ruleml', config)[0]
        relation_container = ruleimpl.get_relation_container()
        self.assertTrue(isinstance(relation_container, plugin.RelationContainer))
        self.assertEquals(relation_container.get_relation_count(), 17)

    def test_create_from_file_with_common_container(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject/rules')))
        config = project.get_configuration('root.confml')
        ruleimpl = plugin.ImplFactory.get_impls_from_file('implml/container_with_rules.ruleml', config)[0]
        relation_container = ruleimpl.get_relation_container()
        self.assertTrue(isinstance(relation_container, plugin.RelationContainer))
        self.assertEquals(relation_container.get_relation_count(), 7)

    def test_create_from_file_filename(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject/rules')))
        config = project.get_configuration('root.confml')
        ruleimpl = plugin.ImplFactory.get_impls_from_file('implml/filename_rules.ruleml', config)[0]
        relation_container = ruleimpl.get_relation_container()
        self.assertTrue(isinstance(relation_container, plugin.RelationContainer))
        self.assertEquals(relation_container.get_relation_count(), 11)

    def test_parse_eval(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'ruleproject/rules')))
        config = project.get_configuration('root.confml')
        ruleimpl = plugin.ImplFactory.get_impls_from_file('implml/eval.ruleml', config)[0]
        relation_container = ruleimpl.get_relation_container()
        self.assertTrue(isinstance(relation_container, plugin.RelationContainer))
        self.assertEquals(relation_container.get_relation_count(), 12)

if __name__ == '__main__':
    unittest.main()
