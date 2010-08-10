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

from cone.storage import webstorage
from cone.carbon import model
import simplewebserver

ROOT_PATH   = os.path.dirname(os.path.abspath(__file__))
#TEST_SERVER = simplewebserver.SimpleWebServer(os.path.join(ROOT_PATH,'carbondata'), 8001)
#
#def runserver():
#    if not TEST_SERVER.active:
#        TEST_SERVER.start()
#        time.sleep(1)
#
#def stopserver():
#    if TEST_SERVER.active:
#        TEST_SERVER.stop()
#
#class TestWebStorage(unittest.TestCase):
#    def setUp(self):
#        runserver()
#
#    def __del__(self):
#        stopserver()
#
#    def test_create_web_storage(self):
#        store = webstorage.WebStorage('localhost:8001/extapp')
#
#
#    def test__get_stringio_from_path(self):
#        store = webstorage.WebStorage('localhost:8001/extapp')
#        strio = store._get_stringio_from_path('alvin.confml')
#        self.assertTrue(len(strio.getvalue()) > 0)
#
#    def test__get_stringio_from_path_fails(self):
#        
#        store = webstorage.WebStorage('localhost:8001/extapp')
#        try:
#            strio = store._get_stringio_from_path('foobar.confml')
#            self.fail('Getting nonexistent file succeeds?')
#        except exceptions.NotResource:
#            pass
#
#
#    def test_get_resource_from_path(self):
#        store = webstorage.WebStorage('localhost:8001/extapp')
#        wres = store.open_resource('test/empty.confml')
#        self.assertTrue(len(wres.read()) == 0)
#
#    def test_get_resource_fails(self):
#        store = webstorage.WebStorage('localhost:8001/extapp')
#        try:
#            wres = store.open_resource('foobar.confml')
#            self.fail('test')
#        except exceptions.NotResource:
#            pass

class TestResourceCache(unittest.TestCase):
#    def test_create_resource_cache_add_configurations(self):
#        rc = webstorage.ResourceCache()
#        conf = model.ConfigurationResource(**{'parent_config': 'hessu', 'path': 'NCP/Testing', 'version_identifier': '0.1', 'configuration_name': 'Testing'})
#        rc.add_configuration(conf)
#        self.assertEquals(rc.list_resources('/'), ['Testing.confml'])
#        self.assertEquals(rc.list_resources('/', True), ['Testing.confml', 'NCP/Testing/root.confml'])
#        self.assertEquals(rc.get_resource('Testing.confml').name, 'Testing_confml')
#        self.assertEquals(isinstance(rc.get_resource('Testing.confml'),model.CarbonConfiguration),True)
#        self.assertEquals(rc.get_resource('Testing.confml').list_configurations(),['NCP/Testing/root.confml'])

    def test_create_resource_cache_from_resource_list(self):
        reslist = ['test.configurationroot',
                   'test.configurationlayer',
                   'test.featurelist']
        rc = webstorage.ResourceCache()
        for res in reslist:
            rc.add_resource(res)
        self.assertEquals(rc.list_resources('/'), ['test.confml'])
        self.assertEquals(rc.list_resources('/', True), ['test/root.confml',
                                                   'featurelists/test.confml',
                                                   'test.confml'])
        self.assertEquals(rc.get_resource_link('test.confml'), 'test.configurationroot')
        self.assertEquals(rc.get_resource_link('featurelists/test.confml'), 'test.featurelist')
        self.assertEquals(rc.get_resource_link('test/root.confml'), 'test.configurationlayer')


class TestCarbonExtapi(unittest.TestCase):
    def test_username_password(self):
        extapi = webstorage.CarbonExtapi("/")
        self.assertNotEqual(extapi,None)
        self.assertNotEqual(extapi.get_username(),"")
    

if __name__ == '__main__':
    unittest.main()

