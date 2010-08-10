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
import sys,os
import pickle
import time

from cone.public import api, exceptions
from cone.storage import webstorage
from cone.carbon import model, persistentjson
import simplewebserver

featurelist = {
    "featurelist": {
        "features": [
            {
                "status": "APPROVED", 
                "value_type": "", 
                "description": "None", 
                "title": "TestGroup", 
                "ref": "testgroup", 
                "type": "featuregroup", 
                "id": 11749, 
                "children": [
                    {
                        "status": "APPROVED", 
                        "value_type": "boolean", 
                        "description": "None", 
                        "title": "Child1", 
                        "ref": "child1", 
                        "type": "feature", 
                        "id": 11750, 
                        "children": []
                    }, 
                    {
                        "status": "APPROVED", 
                        "value_type": "boolean", 
                        "description": "None", 
                        "title": "Child1", 
                        "ref": "child1_1", 
                        "type": "feature", 
                        "id": 11751, 
                        "children": []
                    }, 
                    {
                        "status": "APPROVED", 
                        "value_type": "boolean", 
                        "description": "None", 
                        "title": "Child1", 
                        "ref": "child1_2", 
                        "type": "feature", 
                        "id": 11753, 
                        "children": []
                    }, 
                    {
                        "status": "APPROVED", 
                        "value_type": "boolean", 
                        "description": "Needs description", 
                        "title": "Child1", 
                        "ref": "child1_3", 
                        "type": "feature", 
                        "id": 11756, 
                        "children": []
                    }, 
                    {
                        "status": "APPROVED", 
                        "value_type": "boolean", 
                        "description": "Needs description", 
                        "title": "Child1", 
                        "ref": "child1_4", 
                        "type": "feature", 
                        "id": 11759, 
                        "children": []
                    }, 
                    {
                        "status": "APPROVED", 
                        "value_type": "boolean", 
                        "description": "None", 
                        "title": "Child2", 
                        "ref": "child2", 
                        "type": "feature", 
                        "id": 11754, 
                        "children": []
                    }, 
                    {
                        "status": "APPROVED", 
                        "value_type": "boolean", 
                        "description": "Needs description", 
                        "title": "Child2", 
                        "ref": "child2_1", 
                        "type": "feature", 
                        "id": 11757, 
                        "children": []
                    }, 
                    {
                        "status": "APPROVED", 
                        "value_type": "boolean", 
                        "description": "Needs description", 
                        "title": "Child2", 
                        "ref": "child2_2", 
                        "type": "feature", 
                        "id": 11760, 
                        "children": []
                    }
                ]
            }, 
            {
                "status": "APPROVED", 
                "value_type": "", 
                "description": "Needs description", 
                "title": "TestGroup", 
                "ref": "testgroup_3", 
                "type": "featuregroup", 
                "id": 11758, 
                "children": []
            }, 
            {
                "status": "APPROVED", 
                "value_type": "", 
                "description": "None", 
                "title": "TestGroup", 
                "ref": "testgroup_1", 
                "type": "featuregroup", 
                "id": 11752, 
                "children": []
            }, 
            {
                "status": "APPROVED", 
                "value_type": "", 
                "description": "Needs description", 
                "title": "TestGroup", 
                "ref": "testgroup_2", 
                "type": "featuregroup", 
                "id": 11755, 
                "children": []
            }
        ], 
        "list_version_id": 34, 
        "expanded": True, 
        "version_identifier": "WORKING", 
        "is_latest_version": True, 
        "list_id": 37, 
        "path": "TEST4", 
        "version_title": "TEST4 (WORKING)", 
        "can_be_released": True, 
        "type": "featurelist", 
        "has_external_relations": False
    }
}
ROOT_PATH   = os.path.dirname(os.path.abspath(__file__))
#class TestWebStorage(unittest.TestCase):
#    def setUp(self):
#        self.store = webstorage.WebStorage('http://localhost:8000/extapi')
#        
#    def test_create_and_list_resources(self):
#        files = self.store.list_resources('/')
#        print files
#        self.assertTrue(len(files)>0)
##
#    def test_create_and_list_resources_with_non_existing_folder(self):
#        files = self.store.list_resources('foo')
#        self.assertEquals(files,[])
#        files = self.store.list_resources('foo/')
#        self.assertEquals(files,[])
#        files = self.store.list_resources('foo/bar')
#        self.assertEquals(files,[])
#
#    def test_get_resource(self):
#        res = self.store.open_resource('Zoom.confml')
##        resdata = res.read()
##        self.assertTrue(len(resdata) > 0)
#
#    def test_get_resource_fails(self):
#        try:
#            res = self.store.open_resource('Zoomi.confml')
#            self.fail('Opening non existing resource succeeds')
#            
#        except exceptions.NotResource, e:
#            pass
#
#    def test_is_resource(self):
#        ret = self.store.is_resource('Zoom.confml')
#        self.assertTrue(ret)
#
#    def test_is_resource_false(self):
#        ret = self.store.is_resource('Foobar.confml')
#        self.assertFalse(ret)

class TestCarbonExtapi(unittest.TestCase):
    def setUp(self):
        pass

#    def test_create_feature(self):
#        extapi = webstorage.CarbonExtapi('http://localhost:8000/extapi')
#        self.assertTrue(extapi.create_feature('TEST4.featurelist',model.CarbonSetting('TestGroup')))
#        self.assertTrue(extapi.create_feature('TEST4.featurelist',model.CarbonBooleanSetting('Child1'), 'TestGroup'))
#        self.assertTrue(extapi.create_feature('TEST4.featurelist',model.CarbonBooleanSetting('Child2'), 'TestGroup'))
#
#    def test_create_feature_fails(self):
#        extapi = webstorage.CarbonExtapi('http://localhost:8000/extapi')
#        self.assertFalse(extapi.create_feature('TEST4.featurelist',model.CarbonSetting('Foobar2'), 'TestGroup'))
#
#    def test_create_featurelist(self):
#        extapi = webstorage.CarbonExtapi('http://localhost:8000/extapi')
#        self.assertTrue(extapi.create_featurelist('TEST.featurelist',model.FeatureList(name='TEST9')))

#    def test_update_featurelist(self):
#        extapi = webstorage.CarbonExtapi('http://localhost:8000/extapi', password='terytkone09')
#        fl = model.FeatureList(name='TEST9')
#        fl.add_feature(model.CarbonFeature('Test1'))
#        data = persistentjson.dumps(fl)
#        data = {"features" :[],
#                "version_identifier": "WORKING", 
#                "flv_description": "Needs description", 
#                "path": "TEST9.confml", 
#                "type": "featurelist", 
#                "name": "TEST9"}
#        print "data %s" % data
#        self.assertTrue(extapi.update_resource('TEST9.featurelist',data))

#    def test_create_configuration(self):
#        extapi = webstorage.CarbonExtapi('http://localhost:8000/extapi', password='terytkone09')
#        conf = model.CarbonConfiguration(path='Testing3.confml')
#        (success,conf)= extapi.create_configuration('Testing3.configuration',conf)
#        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()

