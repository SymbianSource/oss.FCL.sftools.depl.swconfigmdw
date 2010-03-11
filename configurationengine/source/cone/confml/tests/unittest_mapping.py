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
import string
import sys
import os
import shutil
import __init__

from cone.public import api, exceptions
from cone.confml import model, mapping
from cone.carbon import persistentjson, model as carbonmodel
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class TestGetMapper(unittest.TestCase):
    def test_get_mapper(self):
        mapper = model.get_mapper('carbon')
        self.assertTrue(isinstance(mapper, mapping.Confml2carbon))

    def test_get_mapper_from_object(self):
        s = model.ConfmlSetting("test")
        mapper = s._get_mapper('carbon')
        self.assertTrue(isinstance(mapper, mapping.Confml2carbon))


class TestCarbon2confml(unittest.TestCase):
    def test_map_carbon_configuration(self):
        mapper = model.get_mapper('carbon')
        c1 = model.ConfmlConfiguration("test")
        c2 = mapper.configuration(c1)
        c3 = c1._get_mapper('carbon').map_object(c1)
        self.assertTrue(isinstance(c2, carbonmodel.CarbonConfiguration))
        c2 = mapper.map_object(c1)
        self.assertTrue(isinstance(c2, carbonmodel.CarbonConfiguration))
        self.assertTrue(isinstance(c3, carbonmodel.CarbonConfiguration))

    def test_map_carbon_featurelist(self):
        mapper = model.get_mapper('carbon')
        c1 = model.ConfmlConfiguration(name="test")
        c1.meta = {}
        c1.meta.add('type','featurelist')
        c2 = mapper.configuration(c1)
        self.assertTrue(isinstance(c2, carbonmodel.FeatureList))
        c2 = mapper.map_object(c1)
        self.assertTrue(isinstance(c2, carbonmodel.FeatureList))

    def test_map_carbon_featurelist_with_features(self):
        mapper = model.get_mapper('carbon')
        c1 = model.ConfmlConfiguration(name="test")
        c1.add_feature(model.ConfmlFeature('Group'))
        c1.meta = {}
        c1.meta.add('type','featurelist')
        c2 = mapper.configuration(c1)
        self.assertTrue(isinstance(c2, carbonmodel.FeatureList))
        c2 = mapper.map_object(c1)
        self.assertTrue(isinstance(c2, carbonmodel.FeatureList))
#        self.assertEquals(c2.list_features(), ['Group'])

    def test_map_carbon_configuration_with_data(self):
        mapper = model.get_mapper('carbon')
        c1 = model.ConfmlConfiguration("test")
        c1.name = "test.confml"
        c1.namespace = "com.nokia"
        c2 = mapper.map_object(c1)
        self.assertTrue(isinstance(c2, carbonmodel.CarbonConfiguration))
        self.assertEquals(c2.name, "test.confml")
        self.assertEquals(c2.namespace, "com.nokia")
        self.assertEquals(c2.path, "test")

    def test_map_carbon_setting_with_data(self):
        mapper = model.get_mapper('carbon')
        c1 = model.ConfmlSetting("test")
        c2 = mapper.map_object(c1)
        self.assertTrue(isinstance(c2, carbonmodel.CarbonSetting))
        self.assertEquals(c2.name, "test")
        self.assertEquals(c2.ref, "test")

    def test_map_carbon_setting_with_desc(self):
        mapper = model.get_mapper('carbon')
        c1 = model.ConfmlSetting("test")
        c1.desc = 'Testing man'
        c2 = mapper.map_object(c1)
        self.assertTrue(isinstance(c2, carbonmodel.CarbonSetting))
        self.assertEquals(c2.name, "test")
        self.assertEquals(c2.ref, "test")
        self.assertEquals(c2.desc, "Testing man")
        
    def test_map_carbon_int_setting_with_data(self):
        mapper = model.get_mapper('carbon')
        c1 = model.ConfmlIntSetting("test")
        c2 = mapper.map_object(c1)
        self.assertTrue(isinstance(c2, carbonmodel.CarbonIntSetting))
        self.assertEquals(c2.name, "test")
        self.assertEquals(c2.ref, "test")

    def test_map_carbon_setting_with_data(self):
        mapper = model.get_mapper('carbon')
        c1 = model.ConfmlBooleanSetting("test")
        c2 = mapper.map_object(c1)
        self.assertTrue(isinstance(c2, carbonmodel.CarbonBooleanSetting))
        self.assertEquals(c2.name, "test")
        self.assertEquals(c2.ref, "test")

    def test_map_carbon_setting_with_data(self):
        mapper = model.get_mapper('carbon')
        c1 = model.ConfmlSelectionSetting("test")
        c2 = mapper.map_object(c1)
        self.assertTrue(isinstance(c2, carbonmodel.CarbonSelectionSetting))
        self.assertEquals(c2.name, "test")
        self.assertEquals(c2.ref, "test")

    def test_map_carbon_feature(self):
        mapper = model.get_mapper('carbon')
        c1 = model.ConfmlFeature("test")
        c2 = mapper.map_object(c1)
        self.assertTrue(isinstance(c2, carbonmodel.CarbonFeature))
        self.assertEquals(c2.name, "test")
        self.assertEquals(c2.ref, "test")
