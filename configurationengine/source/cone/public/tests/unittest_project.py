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

"""
Test the CPF configuration
"""
import unittest
import string
import sys,os,shutil

from cone.public import *
from cone.storage import persistentdictionary

class TestProjectOpen(unittest.TestCase):    
    
    def test_open_project(self):
        
        p = api.Project(api.Storage(""))
        self.assertTrue(p)

    def test_open_project_of_non_storage(self):
        fs = ""
        try:
            p = api.Project("")
            self.fail("Opening on top of non storage succeeds!!")
        except exceptions.StorageException:
            self.assertTrue(True)

class TestProjectConfigurations(unittest.TestCase):    
    def setUp(self):
        self.prj = api.Project(api.Storage(""))
    
    def test_create_configuration(self):
        self.prj.create_configuration("test.confml")
        self.assertTrue(self.prj.test_confml)
        self.assertEquals(self.prj.test_confml.get_path(),"test.confml")

    def test_create_configuration_already_existing(self):
        self.prj.create_configuration("test.confml")
        try:
            self.prj.create_configuration("test.confml")
            self.fail("Succeeded to create already existing configuration")
        except exceptions.AlreadyExists:
            pass
        try:
            self.prj.add_configuration(api.Configuration("test.confml"))
            self.fail("Succeeded to create already existing configuration")
        except exceptions.AlreadyExists:
            pass

    def test_create_configuration_already_existing_with_overwrite(self):
        self.prj.create_configuration("test.confml")
        self.prj.create_configuration("test.confml", True)
        self.prj.add_configuration(api.Configuration("test.confml"), True)

        
    def test_create_and_getconfiguration(self):
        self.prj.create_configuration("test.confml")
        self.assertEquals(self.prj.get_configuration("test.confml").get_path(), "test.confml")

    def test_create_multi_and_list(self):
        self.prj.create_configuration("test1.confml")
        self.prj.create_configuration("test2.confml")
        self.prj.create_configuration("test3.confml")
        self.assertEquals(self.prj.list_configurations(), ["test1.confml",
                                                           "test2.confml",
                                                           "test3.confml"])
    
    def test_create_multi_and_list_with_filters(self):
        self.prj.create_configuration("test1.confml")
        self.prj.create_configuration("test2.confml")
        self.prj.create_configuration("test3.confml")
        self.prj.create_configuration("test4.confml")
        self.prj.create_configuration("foo1.confml")
        self.prj.create_configuration("foo2.confml")
        self.assertEquals(self.prj.list_configurations(r'test[24]\.confml'),
                          ["test2.confml",
                           "test4.confml"])
        self.assertEquals(self.prj.list_configurations([r'test[24]\.confml', r'foo\d\.confml']),
                          ["test2.confml",
                           "test4.confml",
                           "foo1.confml",
                           "foo2.confml"])

    def test_create_multi_and_remove_one(self):
        self.prj.create_configuration("test1.confml")
        self.prj.create_configuration("test2.confml")
        self.prj.create_configuration("test3.confml")
        self.prj.remove_configuration("test2.confml")
        self.assertEquals(self.prj.list_configurations(), ["test1.confml",
                                                           "test3.confml"])

    def test_create_multi_and_remove_all(self):
        self.prj.create_configuration("test1.confml")
        self.prj.create_configuration("test2.confml")
        self.prj.create_configuration("test3.confml")
        for c in self.prj.list_configurations():
            self.prj.remove_configuration(c)
        self.assertEquals(self.prj.list_configurations(), [])

    def test_create_multi_and_add_subconfigurations(self):
        self.prj.create_configuration("test1.confml")
        self.prj.create_configuration("test2.confml")
        self.prj.create_configuration("test3.confml")
        self.prj.test2_confml.create_configuration("foo/root.confml")
        conf = self.prj.test2_confml.create_configuration("fii/root.confml")
        conf.add_configuration(api.Configuration("confml/data.confml"))
        self.assertEquals(conf.get_full_path(),'fii/root.confml')
        self.assertEquals(conf.get_configuration("confml/data.confml").get_path(),'confml/data.confml')
        self.assertEquals(conf.get_configuration("confml/data.confml").get_full_path(),'fii/confml/data.confml')
        self.assertTrue(self.prj.is_configuration("test3.confml"))
        # TODO: this is not working at the moment due to performance problem in
        # Project.list_all_configurations()
        # self.assertTrue(self.prj.is_configuration("fii/root.confml"))
        
        self.assertEquals(self.prj.list_configurations(), ["test1.confml",
                                                           "test2.confml",
                                                           "test3.confml"])
        self.assertEquals(self.prj.list_all_configurations(), ['test1.confml', 
                                                               'test2.confml', 
                                                               'foo/root.confml', 
                                                               'fii/root.confml', 
                                                               'fii/confml/data.confml', 
                                                               'test3.confml'])
        self.assertEquals(self.prj.test2_confml.list_configurations(), ["foo/root.confml",
                                                                 "fii/root.confml",])
        self.assertEquals(self.prj.test2_confml.list_all_configurations(), ["foo/root.confml",
                                                                            "fii/root.confml",
                                                                            "fii/confml/data.confml"])

    def test_create_multi_and_add_subconfigurations_and_features(self):
        self.prj.create_configuration("test1.confml")
        self.prj.create_configuration("test2.confml")
        self.prj.create_configuration("test3.confml")
        self.prj.test2_confml.create_configuration("foo/root.confml")
        self.prj.test2_confml.create_configuration("fii/root.confml")
        self.prj.test2_confml.foo__root_confml.add_feature(api.Feature("testfea1"))
        self.prj.test2_confml.foo__root_confml.add_feature(api.Feature("testfea2"))
        self.prj.test2_confml.foo__root_confml.add_feature(api.Feature("testfea11"),"testfea1")
        self.prj.test2_confml.fii__root_confml.add_feature(api.Feature("testfea3"))
        self.prj.test2_confml.fii__root_confml.add_feature(api.Feature("testfea4"))
        self.prj.test2_confml.fii__root_confml.add_feature(api.Feature("testfea31"),"testfea3")
        self.assertEquals(self.prj.test2_confml.list_all_features(), ['testfea1',
                                                           'testfea1.testfea11',  
                                                           'testfea2', 
                                                           'testfea3', 
                                                           'testfea3.testfea31', 
                                                           'testfea4'])

class TestProjectConfigurationsStorage(unittest.TestCase):    
    def test_create_configuration_and_store_storage(self):
        prj = api.Project(api.Storage.open("temp/testproject.pk", "w"))
        prj.create_configuration("test.confml")
        prj.close()
        self.assertTrue(os.path.exists("temp/testproject.pk"))
        shutil.rmtree("temp")

    def test_create_configuration_and_store_storage_and_open(self):
        prj = api.Project(api.Storage.open("temp/testproject1.pk","w"))
        config = prj.create_configuration("test.confml")
        config.desc = "Descriptions"
        prj.save()
        prj.close()
        
        prj2 = api.Project(api.Storage.open("temp/testproject1.pk"))
        self.assertEquals(prj2.list_configurations(), ['test.confml'])
        self.assertEquals(prj2.test_confml.desc, "Descriptions")
        shutil.rmtree("temp")

    def test_create_configuration_hierarchy_and_store_storage_and_open(self):
        prj = api.Project(api.Storage.open("temp/testproject2.pk","w"))
        config = prj.create_configuration("test.confml")
        config.desc = "Descriptions"
        prj.test_confml.create_configuration("s60/root.confml")
        prj.test_confml.s60__root_confml.add_feature(api.Feature("feature1"))
        prj.test_confml.create_configuration("ncp/root.confml")
        prj.save()
        prj.close()
        
        prj2 = api.Project(api.Storage.open("temp/testproject2.pk"))
        self.assertEquals(prj2.list_configurations(), ['test.confml'])
        self.assertEquals(prj2.test_confml.desc, "Descriptions")
        self.assertEquals(prj2.test_confml.list_all_features(),['feature1'])
        prj2.close()
        shutil.rmtree("temp")

    def test_dump_configuration_with_include(self):
        prj = api.Project(api.Storage.open("temp/testprojectinc.pk","w"))
        config = prj.create_configuration("test.confml")
        config.include_configuration("foo/foo.confml")
        dumped = persistentdictionary.DictWriter().dumps(config)
        children = dumped['Configuration']['children']
        self.assertEquals(children,[{'ConfigurationProxy': {'dict': {'path': 'foo/foo.confml'}}}])
        prj.close()
        shutil.rmtree("temp")

    def test_create_configuration_project_with_includes_and_reopen_storage(self):
        prj = api.Project(api.Storage.open("temp/testprojectinc2.pk","w"))
        config = prj.create_configuration("test.confml")
        config.desc = "Descriptions"
        config2 = config.create_configuration("foo/foo.confml")
        config2.add_feature(api.Feature("feature1"))
        config2.save()        
        config2.close()        
        prj.test_confml.include_configuration("foo/foo.confml")
        prj.save()
        prj.close()
        
        prj2 = api.Project(api.Storage.open("temp/testprojectinc2.pk"))
        self.assertEquals(prj2.list_configurations(), ['test.confml'])
        self.assertEquals(prj2.test_confml.list_configurations(), ['foo/foo.confml'])
        foo = prj2.test_confml.get_configuration('foo/foo.confml')
        self.assertEquals(prj2.get_configuration('test.confml').list_all_features(), ['feature1'])
        self.assertEquals(prj2.test_confml.get_default_view().list_features(), ['feature1'])
        prj2.close()
        shutil.rmtree("temp")

    def test_create_configuration_project_with_multiincludes_and_reopen_storage(self):
        prj = api.Project(api.Storage.open("temp/testprojectinc3.pk","w"))
        config = prj.create_configuration("test.confml")
        prj.add_configuration(api.Configuration("s60/root.confml", namespace="com.nokia.s60"))
        prj.create_configuration("foo/foo.confml")
        prj.test_confml.include_configuration("foo/foo.confml")
        prj.test_confml.include_configuration("s60/root.confml")
        foofea = api.Feature("foofea")
        foofea.add_feature(api.Feature("foofea_setting1"))
        foofea.add_feature(api.Feature("foofea_setting2"))
        prj.test_confml.foo__foo_confml.add_feature(foofea)
        
        s60fea = api.Feature("s60fea")
        s60fea.add_feature(api.Feature("wlanset1"))
        s60fea.add_feature(api.Feature("wlan_set2"))
        prj.test_confml.s60__root_confml.add_feature(s60fea)
        dview = prj.test_confml.get_default_view()
        prj.save()
        
        prj2 = api.Project(api.Storage.open("temp/testprojectinc3.pk"))
        self.assertEquals(prj2.list_configurations(), ['test.confml'])

        dview2 = prj2.test_confml.get_default_view()
        self.assertEquals(dview.list_all_features(),
                          dview2.list_all_features())
        testconf = prj2.get_configuration('test.confml')
        my_view = testconf.get_default_view()
        my_view.com.nokia.s60.s60fea.wlanset1.data = 1
        prj2.close()
        shutil.rmtree("temp")

    def test_create_configuration_project_with_multiincludes_and_test_layer_actions(self):
        prj = api.Project(api.Storage.open("temp/testprojectlayers.pk","w"))
        config = prj.create_configuration("test.confml")
        prj.add_configuration(api.Configuration("s60/root.confml", namespace="com.nokia.s60"))
        prj.create_configuration("foo/foo.confml")
        prj.create_configuration("foo/confml/component.confml").close()
        prj.test_confml.include_configuration("foo/foo.confml")
        prj.test_confml.include_configuration("s60/root.confml")
        prj.test_confml.foo__foo_confml.create_configuration("data.confml")
        prj.test_confml.foo__foo_confml.add_configuration(api.Configuration("confml/test.confml"))
        foofea = api.Feature("foofea")
        foofea.add_feature(api.Feature("foofea_setting1"))
        foofea.add_feature(api.Feature("foofea_setting2"))
        prj.test_confml.foo__foo_confml.add_feature(foofea)
        prj.save()
        foo_config = prj.test_confml.get_configuration("foo/foo.confml")
        layer = foo_config.get_layer()
        res = layer.open_resource("confml/component1.confml","w")
        res.write("foo.conf")
        res.close()
        res = layer.content_folder().open_resource("foobar.txt","w")
        res.write("foo bar")
        res.close()
        self.assertEquals(layer.list_confml(), ['confml/component.confml', 'confml/component1.confml', 'confml/test.confml'])
        self.assertEquals(layer.list_content(), ['content/foobar.txt'])
        self.assertEquals(layer.list_all_resources(), ['confml/component.confml', 'confml/component1.confml', 'confml/test.confml', 'content/foobar.txt'])
        self.assertEquals(foo_config.list_resources(), ['foo/foo.confml',
                                                        'foo/data.confml', 
                                                        'foo/confml/test.confml', 
                                                        'foo/confml/component.confml', 
                                                        'foo/confml/component1.confml', 
                                                        'foo/content/foobar.txt'])
        self.assertEquals(prj.test_confml.list_resources(), ['test.confml',
                                                      'foo/foo.confml',
                                                      'foo/data.confml',
                                                      'foo/confml/test.confml',
                                                      's60/root.confml',
                                                      'foo/confml/component.confml', 
                                                      'foo/confml/component1.confml', 
                                                      'foo/content/foobar.txt'])
        
        
        s60_config = prj.test_confml.get_configuration("s60/root.confml")
        layer = s60_config.get_layer()
        res = layer.open_resource("confml/component1.confml","w")
        res.write("foo.conf")
        res.close()
        res = layer.content_folder().open_resource("s60.txt","w")
        res.write("foo bar")
        res.close()
        res = layer.content_folder().open_resource("foobar.txt","w")
        res.write("foo bar")
        res.close()
        self.assertEquals(layer.list_confml(), ['confml/component1.confml'])
        self.assertEquals(layer.list_content(), ['content/foobar.txt', 'content/s60.txt'])
        self.assertEquals(prj.test_confml.layered_content().list_keys(), ['foobar.txt', 's60.txt'])
        self.assertEquals(prj.test_confml.layered_content().get_values('foobar.txt'), ['foo/content/foobar.txt', 's60/content/foobar.txt'])
        prj.close()
        shutil.rmtree("temp")


if __name__ == '__main__':
    unittest.main()
      
