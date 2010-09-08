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
#!/usr/bin/env python
## 
# @author Teemu Rytkonen

import os, shutil

import unittest
from cone.action import configroot2flat
from cone.public import api

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))


class TestConfigRootFlat(unittest.TestCase):
    def test_get_flat_configuration_with_empty_config(self):
        conf = api.Configuration('foo.confml')
        self.assertEquals(configroot2flat.get_flat_includes(conf), [])
        
    def test_get_flat_configuration_with_single_config_hierarchy(self):
        conf = api.Configuration('foo.confml')
        conf.include_configuration('test1/root.confml')
        conf.include_configuration('test2/root.confml')
        conf.include_configuration('test3/root.confml')
        self.assertEquals(configroot2flat.get_flat_includes(conf), ['test1/root.confml',
                                                                    'test2/root.confml',
                                                                    'test3/root.confml'])
    
    def test_get_flat_configuration_with_two_level_config_hierarchy(self):
        prj = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'temp'), 'w'))
        rootconf1 = prj.create_configuration('product1_root.confml', True)
        rootconf2 = prj.create_configuration('product2_root.confml', True)
        prj.create_configuration('test/one/root.confml', True)
        fooconf = prj.create_configuration('test/foo.confml', True)
        rootconf1.create_configuration('layer1/root.confml')
        rootconf1.create_configuration('layer2/root.confml')
        rootconf1.create_configuration('layer3/root.confml')
        fooconf.include_configuration('/product1_root.confml')
        fooconf.include_configuration('/product2_root.confml')
        fooconf.include_configuration('/test/one/root.confml')
        rootconf1.create_configuration('layer5/root.confml')
        rootconf1.create_configuration('layer6/root.confml')
        prj.save()
        self.assertEquals(configroot2flat.get_flat_includes(fooconf), ['layer1/root.confml',
                                                                       'layer2/root.confml',
                                                                       'layer3/root.confml',
                                                                       'layer5/root.confml',
                                                                       'layer6/root.confml',
                                                                       'test/one/root.confml'])
    
    def test_get_flat_configuration_with_nonexistent_files(self):
        TEMP_DIR = os.path.join(ROOT_PATH,'temp2')
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        
        # Create a configuration with some non-existent layers
        prj = api.Project(api.Storage.open(TEMP_DIR, 'w'))
        prj.create_configuration('test/one/root.confml', True)
        
        rootconf1 = prj.create_configuration('product1_root.confml', True)
        rootconf1.create_configuration('layer1/root.confml')
        rootconf1.include_configuration('nonexistent1/root.confml')
        
        rootconf2 = prj.create_configuration('product2_root.confml', True)
        rootconf2.create_configuration('layer3/root.confml')
        rootconf2.include_configuration('nonexistent2/root.confml')
        
        fooconf = prj.create_configuration('test/foo.confml', True)
        fooconf.include_configuration('/product1_root.confml')
        fooconf.include_configuration('/product2_root.confml')
        rootconf1.include_configuration('/nonexistent_product_root.confml')
        fooconf.include_configuration('/test/one/root.confml')
        fooconf.include_configuration('nonexistent3/root.confml')
        prj.save()
        prj.close()
        
        action = configroot2flat.ConeConfigroot2FlatAction(
            project=TEMP_DIR,
            configs=['test/foo.confml'])
        action.run()
        
        prj = api.Project(api.Storage.open(TEMP_DIR, 'r'))
        fooconf = prj.get_configuration('foo.confml')
        self.assertEquals(fooconf.list_configurations(),
            ['layer1/root.confml',
             'nonexistent1/root.confml',
             'layer3/root.confml',
             'nonexistent2/root.confml',
             'test/one/root.confml',
             'nonexistent3/root.confml'])
        