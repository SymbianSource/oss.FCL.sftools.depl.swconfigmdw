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
import pkg_resources
import re
import logging

from legacyruleplugin import ruleml, relations
from cone.public import api, exceptions
from legacyruleplugin.evals import layer_utils
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

#logger = logging.getLogger("cone.ruleplugin.evals.layer_utils")
#logger.setLevel(logging.DEBUG)
#ch = logging.StreamHandler()
#ch.setLevel(logging.DEBUG)
#logger.addHandler(ch)

class TestLayerUtils(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_give_changed_layers(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'layerproject')))
        config = project.get_configuration('root.confml')
        dview = config.get_default_view()
        
        self.assertEquals(layer_utils.give_changed_layers(dview.get_feature("StringFeatureTest.Value1")), [True, True, True, True, True])
        self.assertEquals(layer_utils.give_changed_layers(dview.get_feature("StringFeatureTest.Value2")), [False, True, True, False, False])
        
    def test_changed_on_last_layer(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'layerproject')))
        config = project.get_configuration('root.confml')
        dview = config.get_default_view()
        
        self.assertTrue(layer_utils.changed_on_last_layer(dview.get_feature("StringFeatureTest.Value1")))
        self.assertFalse(layer_utils.changed_on_last_layer(dview.get_feature("StringFeatureTest.Value2")))

    def test_changed_on_layer(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'layerproject')))
        config = project.get_configuration('root.confml')
        dview = config.get_default_view()
        
        self.assertTrue(layer_utils.changed_on_layer(dview.get_feature("StringFeatureTest.Value1"),-1))
        self.assertTrue(layer_utils.changed_on_layer(dview.get_feature("StringFeatureTest.Value1"),0))
        self.assertTrue(layer_utils.changed_on_layer(dview.get_feature("StringFeatureTest.Value1"),1))
        self.assertTrue(layer_utils.changed_on_layer(dview.get_feature("StringFeatureTest.Value1"),2))
        self.assertTrue(layer_utils.changed_on_layer(dview.get_feature("StringFeatureTest.Value1"),3))
        self.assertTrue(layer_utils.changed_on_layer(dview.get_feature("StringFeatureTest.Value1"),4))
        self.assertFalse(layer_utils.changed_on_layer(dview.get_feature("StringFeatureTest.Value1"),5))
        self.assertFalse(layer_utils.changed_on_layer(dview.get_feature("StringFeatureTest.Value2"),-1))
        self.assertFalse(layer_utils.changed_on_layer(dview.get_feature("StringFeatureTest.Value2"),0))
        self.assertTrue(layer_utils.changed_on_layer(dview.get_feature("StringFeatureTest.Value2"),1))
        self.assertTrue(layer_utils.changed_on_layer(dview.get_feature("StringFeatureTest.Value2"),2))
        self.assertFalse(layer_utils.changed_on_layer(dview.get_feature("StringFeatureTest.Value2"),3))
        self.assertFalse(layer_utils.changed_on_layer(dview.get_feature("StringFeatureTest.Value2"),4))
        self.assertFalse(layer_utils.changed_on_layer(dview.get_feature("StringFeatureTest.Value2"),5))

    def test_changed_on_layers(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'layerproject')))
        config = project.get_configuration('root.confml')
        dview = config.get_default_view()
        
        self.assertTrue(layer_utils.changed_on_layers(dview.get_feature("StringFeatureTest.Value1"),0,4))
        self.assertTrue(layer_utils.changed_on_layers(dview.get_feature("StringFeatureTest.Value1"),2,3))
        self.assertTrue(layer_utils.changed_on_layers(dview.get_feature("StringFeatureTest.Value1"),2,2))
        self.assertTrue(layer_utils.changed_on_layers(dview.get_feature("StringFeatureTest.Value1"),1,7))
        self.assertFalse(layer_utils.changed_on_layers(dview.get_feature("StringFeatureTest.Value1"),8,9))
        self.assertFalse(layer_utils.changed_on_layers(dview.get_feature("StringFeatureTest.Value2"),0,1))
        self.assertTrue(layer_utils.changed_on_layers(dview.get_feature("StringFeatureTest.Value2"),1,5))

        
if __name__ == "__main__":
    unittest.main()
