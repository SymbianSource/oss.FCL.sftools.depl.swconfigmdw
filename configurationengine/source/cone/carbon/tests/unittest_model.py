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
import datetime

from cone.public import api, exceptions
from cone.carbon import persistentjson, model
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class TestConfigurationResource(unittest.TestCase):
    def test_create(self):
        c = model.ConfigurationResource(configuration_name='test')
        self.assertTrue(c)
        self.assertEquals(c.name, 'test')

    def test_create_from_dict(self):
        confdict = {'parent_config': 'hessu', 'path': 'Testing', 'version_identifier': '0.1', 'configuration_name': 'Testing'}
        c = model.ConfigurationResource(**confdict)
        self.assertTrue(c)
        self.assertEquals(c.name, 'Testing')
        self.assertEquals(c.path, 'Testing')
        self.assertEquals(c.parent_config, 'hessu')
        self.assertEquals(c.version, '0.1')
        self.assertEquals(c.get_path(), 'Testing/root.confml')

class TestFeatureListResource(unittest.TestCase):
    def test_create(self):
        c = model.FeatureListResource(path='test', list_id=1, list_version_id=1)
        self.assertTrue(c)
        self.assertEquals(c.path, 'test')
        self.assertEquals(c.list_id, 1)
        self.assertEquals(c.list_version_id, 1)

    def test_create_from_dict(self):
        fldict = {
            "list_version_id": 30, 
            "expanded": True, 
            "version_identifier": "working", 
            "is_latest_version": True, 
            "list_id": 33, 
            "path": "ESTART", 
            "version_title": "ESTART (working)", 
            "can_be_released": True, 
            "type": "featurelist", 
            "has_external_relations": False
        }
        c = model.FeatureListResource(**fldict)
        self.assertTrue(c)
        self.assertEquals(c.list_version_id, 30)
        self.assertEquals(c.expanded, True)
        self.assertEquals(c.version_identifier, "working")
        self.assertEquals(c.is_latest_version, True)
        self.assertEquals(c.list_id, 33)
        self.assertEquals(c.path, 'ESTART')
        self.assertEquals(c.version_title, "ESTART (working)")
        self.assertEquals(c.can_be_released, True)
        self.assertEquals(c.type, "featurelist")
        self.assertEquals(c.has_external_relations, False)


class TestCarbonConfiguration(unittest.TestCase):
    def test_create_carbon_configuration(self):
        config = model.CarbonConfiguration(path='foo/bar/test.confml', version_identifier='testing')
        self.assertEquals(config.version_identifier,'testing')
        self.assertEquals(config.path,'foo/bar/test.confml')
        self.assertEquals(config.ref,'foo__bar__test_confml')
        self.assertEquals(config.name,'test')

        config = model.CarbonConfiguration(ref='foo/bar/test.confml')
        self.assertEquals(config.path,'foo/bar/test.confml')
        self.assertEquals(config.ref,'foo__bar__test_confml')
        self.assertEquals(config.name,'test')

    def test_create_carbon_configuration_with_current_week_version(self):
        config = model.CarbonConfiguration(path='foo/bar/test.confml')
        dt = datetime.datetime.today()
        self.assertEquals(config.version_identifier,"%dwk%02d" % dt.isocalendar()[0:2])

class TestResourceList(unittest.TestCase):
    def test_create_resource_list(self):
        rl = model.ResourceList()
        self.assertTrue(rl != None)

    def test_add_resource(self):
        rl = model.ResourceList()
        c = model.ConfigurationResource(**{'parent_config': 'hessu', 'path': 'Testing', 'version_identifier': '0.1', 'configuration_name': 'Testing'})
        rl.add_resource(c)

    def test_list_resources(self):
        rl = model.ResourceList()
        rl.add_resource(model.ConfigurationResource(**{'parent_config': 'hessu', 'path': 'Testing', 'version_identifier': '0.1', 'configuration_name': 'Testing'}))
        rl.add_resource(model.ConfigurationResource(**{'parent_config': 'hessu', 'path': 'Foobar', 'version_identifier': '0.1', 'configuration_name': 'Foobar'}))
        self.assertEquals(rl.list_resources(),['Testing/root.confml','Foobar/root.confml'])

    def test_iterate_resources(self):
        rl = model.ResourceList()
        rl.add_resource(model.ConfigurationResource(**{'parent_config': 'hessu', 'path': 'Testing', 'version_identifier': '0.1', 'configuration_name': 'Testing'}))
        rl.add_resource(model.ConfigurationResource(**{'parent_config': 'hessu', 'path': 'Foobar', 'version_identifier': '0.1', 'configuration_name': 'Foobar'}))
        for res in rl:
            self.assertTrue(isinstance(res,model.ConfigurationResource))

class TestFeatureList(unittest.TestCase):
    def test_create(self):
        c = model.FeatureList(name='test')
        self.assertTrue(c)
        self.assertEquals(c.name, 'test')
        self.assertEquals(c.meta.get('type'), 'featurelist')
        self.assertEquals(c.path, 'test.confml')

    def test_create_with_path(self):
        c = model.FeatureList(path='featurelists/test.confml')
        self.assertTrue(c)
        self.assertEquals(c.name, '')
        self.assertEquals(c.meta.get('type'), 'featurelist')
        self.assertEquals(c.path, 'featurelists/test.confml')
        self.assertEquals(c.version_identifier, 'WORKING')

class TestFeature(unittest.TestCase):
    def test_create(self):
        c = model.CarbonFeature(ref='test')
        self.assertTrue(c)
        self.assertEquals(c.name, 'test')
        self.assertEquals(c.ref, 'test')
