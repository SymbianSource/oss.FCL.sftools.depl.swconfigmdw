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

from cone.public import api
from ruleplugin.evals import layer_utils
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
        
        self.assertFalse(layer_utils.changed_on_layers(dview.get_feature("StringFeatureTest.Value2"),3,5))
        self.assertFalse(layer_utils.changed_on_layers(dview.get_feature("StringFeatureTest.Value2"),5,3))
        self.assertFalse(layer_utils.changed_on_layers(dview.get_feature("StringFeatureTest.Value2"),-2,-1))
        self.assertFalse(layer_utils.changed_on_layers(dview.get_feature("StringFeatureTest.Value2"),-1,-2))
        
        self.assertTrue(layer_utils.changed_on_layers(dview.get_feature("StringFeatureTest.Value2"),2,5))
        self.assertTrue(layer_utils.changed_on_layers(dview.get_feature("StringFeatureTest.Value2"),5,2))
        self.assertTrue(layer_utils.changed_on_layers(dview.get_feature("StringFeatureTest.Value2"),-3,-1))
        self.assertTrue(layer_utils.changed_on_layers(dview.get_feature("StringFeatureTest.Value2"),-1,-3))
        
        self.assertFalse(layer_utils.changed_on_layers(dview.get_feature("StringFeatureTest.Value2"),3,1000))
        self.assertFalse(layer_utils.changed_on_layers(dview.get_feature("StringFeatureTest.Value2"),-1000,1))
        self.assertTrue(layer_utils.changed_on_layers(dview.get_feature("StringFeatureTest.Value2"),-1000,1000))

    def test_layers_used_single_layer(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'layer_filtering_project')))
        root_config = project.get_configuration('root.confml')
        
        layer_base_config = root_config.get_configuration_by_index(0)
        layer1_config = root_config.get_configuration_by_index(1)
        layer2_config = root_config.get_configuration_by_index(2)
        layer3_config = root_config.get_configuration_by_index(3)
        layer4_config = root_config.get_configuration_by_index(4)
        layer5_config = root_config.get_configuration_by_index(5)
        layer6_config = root_config.get_configuration_by_index(6)
        layer7_config = root_config.get_configuration_by_index(7)
        layer8_config = root_config.get_configuration_by_index(8)
        layer9_config = root_config.get_configuration_by_index(9)
        layer10_config = root_config.get_configuration_by_index(10)
        layer11_config = root_config.get_configuration_by_index(11)
        
        self.assertTrue(layer_utils.layers_used(root_config, [root_config], {'target' : ['uda']}))
        self.assertTrue(layer_utils.layers_used(root_config, [root_config], {'target' : ['rofs2']}))
        
        self.assertTrue( layer_utils.layers_used(root_config, [layer_base_config], {'target' : ['uda']}))
        self.assertTrue( layer_utils.layers_used(root_config, [layer1_config], {'target' : ['uda']}))
        self.assertFalse(layer_utils.layers_used(root_config, [layer2_config], {'target' : ['uda']}))
        self.assertFalse(layer_utils.layers_used(root_config, [layer3_config], {'target' : ['uda']}))
        self.assertTrue( layer_utils.layers_used(root_config, [layer4_config], {'target' : ['uda']}))
        self.assertFalse(layer_utils.layers_used(root_config, [layer5_config], {'target' : ['uda']}))

        self.assertTrue( layer_utils.layers_used(root_config, [layer_base_config], {'target' : ['rofs2']}))
        self.assertFalse(layer_utils.layers_used(root_config, [layer1_config], {'target' : ['rofs2']}))
        self.assertTrue( layer_utils.layers_used(root_config, [layer2_config], {'target' : ['rofs2']}))
        self.assertFalse(layer_utils.layers_used(root_config, [layer3_config], {'target' : ['rofs2']}))
        
        self.assertTrue( layer_utils.layers_used(root_config, [layer5_config], {'target' : ['rofs3']}))
        self.assertFalse(layer_utils.layers_used(root_config, [layer5_config], {'target' : ['uda']}))
        
        self.assertFalse(layer_utils.layers_used(root_config, [layer6_config], {'target' : ['rofs2']}))
        self.assertTrue( layer_utils.layers_used(root_config, [layer6_config], {'target' : ['rofs3']}))
        self.assertTrue( layer_utils.layers_used(root_config, [layer6_config], {'target' : ['uda']}))
        
        self.assertFalse(layer_utils.layers_used(root_config, [layer7_config], {'target' : ['rofs3']}))
        self.assertTrue( layer_utils.layers_used(root_config, [layer7_config], {'target' : ['uda']}))
        
        self.assertFalse(layer_utils.layers_used(root_config, [layer8_config], {'target' : ['rofs3']}))
        self.assertFalse(layer_utils.layers_used(root_config, [layer8_config], {'target' : ['uda']}))
        
        self.assertFalse(layer_utils.layers_used(root_config, [layer9_config], {'target' : ['rofs3']}))
        self.assertTrue( layer_utils.layers_used(root_config, [layer9_config], {'target' : ['uda']}))
        
        self.assertFalse(layer_utils.layers_used(root_config, [layer10_config], {'target' : ['rofs3']}))
        self.assertTrue( layer_utils.layers_used(root_config, [layer10_config], {'target' : ['uda']}))
        
        self.assertFalse(layer_utils.layers_used(root_config, [layer11_config], {'target' : ['rofs3']}))
        self.assertTrue( layer_utils.layers_used(root_config, [layer11_config], {'target' : ['uda']}))

    def test_layers_used_regex(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'layer_filtering_project')))
        root_config = project.get_configuration('root.confml')
        
        self.assertTrue(layer_utils.layers_used(root_config, r'/base/', {'target' : ['uda']}))
        self.assertTrue(layer_utils.layers_used(root_config, r'/base/', {'target' : ['rofs2']}))
        
        self.assertTrue( layer_utils.layers_used(root_config, r'/base/', {'target' : ['uda']}))
        self.assertTrue( layer_utils.layers_used(root_config, r'/layer1/', {'target' : ['uda']}))
        self.assertFalse(layer_utils.layers_used(root_config, r'/layer2/', {'target' : ['uda']}))
        self.assertFalse(layer_utils.layers_used(root_config, r'/layer3/', {'target' : ['uda']}))
        self.assertTrue( layer_utils.layers_used(root_config, r'/layer4/', {'target' : ['uda']}))
        self.assertFalse(layer_utils.layers_used(root_config, r'/layer5/', {'target' : ['uda']}))

        self.assertTrue( layer_utils.layers_used(root_config, r'/base/', {'target' : ['rofs2']}))
        self.assertFalse(layer_utils.layers_used(root_config, r'/layer1/', {'target' : ['rofs2']}))
        self.assertTrue( layer_utils.layers_used(root_config, r'/layer2/', {'target' : ['rofs2']}))
        self.assertFalse(layer_utils.layers_used(root_config, r'/layer3/', {'target' : ['rofs2']}))

        self.assertTrue( layer_utils.layers_used(root_config, r'/layer5/', {'target' : ['rofs3']}))
        self.assertFalse(layer_utils.layers_used(root_config, r'/layer5/', {'target' : ['uda']}))
        
        self.assertFalse(layer_utils.layers_used(root_config, r'/layer6/', {'target' : ['rofs2']}))
        self.assertTrue( layer_utils.layers_used(root_config, r'/layer6/', {'target' : ['rofs3']}))
        self.assertTrue( layer_utils.layers_used(root_config, r'/layer6/', {'target' : ['uda']}))
        
        self.assertFalse(layer_utils.layers_used(root_config, r'/layer7/', {'target' : ['rofs3']}))
        self.assertTrue( layer_utils.layers_used(root_config, r'/layer7/', {'target' : ['uda']}))
        
        self.assertFalse(layer_utils.layers_used(root_config, r'/layer8/', {'target' : ['rofs3']}))
        self.assertFalse(layer_utils.layers_used(root_config, r'/layer8/', {'target' : ['uda']}))
        
        self.assertFalse(layer_utils.layers_used(root_config, r'/layer9/', {'target' : ['rofs3']}))
        self.assertTrue( layer_utils.layers_used(root_config, r'/layer9/', {'target' : ['uda']}))
        
        self.assertFalse(layer_utils.layers_used(root_config, r'/layer10/', {'target' : ['rofs3']}))
        self.assertTrue( layer_utils.layers_used(root_config, r'/layer10/', {'target' : ['uda']}))
    
    def test_changed_on_layers_regex(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH, 'layerproject')))
        config = project.get_configuration('foobar_root.confml')
        dview = config.get_default_view()
        
        def check(regex, feature, expected):
            self.assertEquals(layer_utils.changed_on_layers_regex(dview.get_feature(feature), regex),
                              expected)
        
        check(r'.*', 'TestFeature.CustvariantManual', True)
        
        regex = r'/custvariant(_.*)?/manual/'
        check(regex, 'TestFeature.CustvariantManual', True)
        check(regex, 'TestFeature.CustvariantConfigurator', False)
        check(regex, 'TestFeature.Rnd', False)
        
        regex = r'/custvariant(_.*)?/configurator/'
        check(regex, 'TestFeature.CustvariantManual', False)
        check(regex, 'TestFeature.CustvariantConfigurator', True)
        check(regex, 'TestFeature.Rnd', False)
        
        regex = r'/custvariant(_.*)?/'
        check(regex, 'TestFeature.CustvariantManual', True)
        check(regex, 'TestFeature.CustvariantConfigurator', True)
        check(regex, 'TestFeature.Rnd', False)
        
        regex = r'foo/bar/'
        check(regex, 'StringFeatureTest.Value1', False)
        check(regex, 'TestFeature.CustvariantManual', True)
        check(regex, 'TestFeature.CustvariantConfigurator', True)
        check(regex, 'TestFeature.Rnd', True)
        
        regex = r'/rnd/'
        check(regex, 'TestFeature.CustvariantManual', False)
        check(regex, 'TestFeature.CustvariantConfigurator', False)
        check(regex, 'TestFeature.Rnd', True)
    
    def test_changed_on_custvariant_layer(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH, 'layerproject')))
        config = project.get_configuration('foobar_root.confml')
        dview = config.get_default_view()
        
        def check(feature, expected):
            self.assertEquals(layer_utils.changed_on_custvariant_layer(dview.get_feature(feature)),
                              expected)
        check('StringFeatureTest.Value1', False)
        check('StringFeatureTest.Value2', False)
        check('TestFeature.CustvariantManual', True)
        check('TestFeature.CustvariantConfigurator', True)
        check('TestFeature.Rnd', False)

if __name__ == "__main__":
    unittest.main()
