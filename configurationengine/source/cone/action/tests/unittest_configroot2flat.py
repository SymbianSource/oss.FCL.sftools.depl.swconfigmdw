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

import os

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
                