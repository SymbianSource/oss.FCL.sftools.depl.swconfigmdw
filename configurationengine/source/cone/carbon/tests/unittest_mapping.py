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

from cone.public import api, exceptions
from cone.confml import model as confmlmodel
from cone.carbon import persistentjson, model, mapping
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class TestGetMapper(unittest.TestCase):
    def test_get_mapper(self):
        mapper = model.get_mapper('confml')
        self.assertTrue(isinstance(mapper, mapping.Carbon2confml))

    def test_get_mapper_from_object(self):
        s = model.CarbonSetting("test")
        mapper = s._get_mapper('confml')
        self.assertTrue(isinstance(mapper, mapping.Carbon2confml))


class TestCarbon2confml(unittest.TestCase):
    def test_map_carbon_configuration(self):
        mapper = model.get_mapper('confml')
        c1 = model.CarbonConfiguration("test")
        c2 = mapper.configuration(c1)
        self.assertTrue(isinstance(c2, confmlmodel.ConfmlConfiguration))
        c2 = mapper.map_object(c1)
        self.assertTrue(isinstance(c2, confmlmodel.ConfmlConfiguration))

    def test_map_carbon_featurelist(self):
        mapper = model.get_mapper('confml')
        c1 = model.FeatureList(name="test")
        c2 = mapper.configuration(c1)
        self.assertTrue(isinstance(c2, confmlmodel.ConfmlConfiguration))
        c2 = mapper.map_object(c1)
        self.assertTrue(isinstance(c2, confmlmodel.ConfmlConfiguration))
        
    def test_map_carbon_configuration_with_data(self):
        mapper = model.get_mapper('confml')
        c1 = model.CarbonConfiguration("test")
        c1.name = "test.confml"
        c1.namespace = "com.nokia"
        c2 = mapper.map_object(c1)
        self.assertTrue(isinstance(c2, confmlmodel.ConfmlConfiguration))
        self.assertEquals(c2.name, "test.confml")
        self.assertEquals(c2.namespace, "com.nokia")
        self.assertEquals(c2.path, "test")

    def test_map_carbon_setting_with_data(self):
        mapper = model.get_mapper('confml')
        c1 = model.CarbonSetting("test")
        c2 = mapper.map_object(c1)
        self.assertTrue(isinstance(c2, confmlmodel.ConfmlSetting))
        self.assertEquals(c2.name, None)
        self.assertEquals(c2.ref, "test")

    def test_map_carbon_int_setting_with_data(self):
        mapper = model.get_mapper('confml')
        c1 = model.CarbonIntSetting("test")
        c2 = mapper.map_object(c1)
        self.assertTrue(isinstance(c2, confmlmodel.ConfmlIntSetting))
        self.assertEquals(c2.name, None)
        self.assertEquals(c2.ref, "test")

    def test_map_carbon_boolean_setting_with_data(self):
        mapper = model.get_mapper('confml')
        c1 = model.CarbonBooleanSetting("test")
        c2 = mapper.map_object(c1)
        self.assertTrue(isinstance(c2, confmlmodel.ConfmlBooleanSetting))
        self.assertEquals(c2.name, None)
        self.assertEquals(c2.ref, "test")

    def test_map_carbon_selection_setting_with_data(self):
        mapper = model.get_mapper('confml')
        c1 = model.CarbonSelectionSetting("test")
        c2 = mapper.map_object(c1)
        self.assertTrue(isinstance(c2, confmlmodel.ConfmlSelectionSetting))
        self.assertEquals(c2.name, None)
        self.assertEquals(c2.ref, "test")
