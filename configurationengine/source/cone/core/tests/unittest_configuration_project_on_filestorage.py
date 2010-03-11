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
import sys,os
import shutil
import __init__
from testautomation.base_testcase import BaseTestCase

from cone.public import exceptions, api
from cone.confml.model import ConfmlMeta, ConfmlDescription
from cone.storage.filestorage import FileStorage
from cone.confml import model

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
temp_dir  = os.path.join(ROOT_PATH, "temp/project_on_filestorage")
datafolder= os.path.join(ROOT_PATH,"../../storage/tests/data")

class TestConeProjectOpen(unittest.TestCase):    
    def setUp(self):
        pass
    
    def test_open_storage(self):
        p = api.Storage.open(datafolder)
        self.assertTrue(p)
        
    def test_open_project_of_non_storage(self):
        fs = "foobar_dummy"
        try:
            p = api.Storage.open(fs)
            self.fail("Opening on top of non storage succeeds!!")
        except exceptions.StorageException:
            self.assertTrue(True)
        

class TestConeProjectMethodsRead(unittest.TestCase):    
    def setUp(self):
        self.project = api.Project(api.Storage.open(datafolder))

    def test_list_configurations(self):
        confs =  self.project.list_configurations()
        self.assertTrue(confs)
        self.assertEquals(confs[0],"morestuff.confml")

    def test_get_configuration(self):
        conf =  self.project.get_configuration("morestuff.confml")
        self.assertTrue(conf)
        self.assertTrue(isinstance(conf,api.ConfigurationProxy))

    def test_get_configuration_non_existing(self):
        try:
            conf =  self.project.get_configuration("foo.confml")
            self.fail("Opening non existing configuration succeeds!")
        except exceptions.NotFound,e:
            self.assertTrue(True)

    def test_get_configuration_and_list_layers(self):
        conf =  self.project.get_configuration("morestuff.confml")
        layers = conf.list_configurations()
        self.assertTrue(layers)
        self.assertEquals(layers[0],'platform/s60/root.confml')
        self.assertEquals(layers[1],'familyX/root.confml')

    def test_get_is_configuration(self):
        self.assertTrue(self.project.is_configuration("morestuff.confml"))
        # TODO: this is not working at the moment due to performance problem in
        # Project.list_all_configurations()
        #self.assertTrue(self.project.is_configuration("platform/s60/root.confml"))
        #self.assertFalse(self.project.is_configuration("platform/foo/root.confml"))

    def test_get_configuration_and_get_layer(self):
        conf =  self.project.get_configuration("morestuff.confml")
        s60layer = conf.get_configuration('platform/s60/root.confml')
        self.assertTrue(s60layer)
        self.assertTrue(isinstance(s60layer.get_layer(),api.Layer))
    
    def test_get_configuration_and_get_layer_path(self):
        conf =  self.project.get_configuration("morestuff.confml")
        s60layer = conf.get_configuration('platform/s60/root.confml')
        self.assertEquals(s60layer.get_path(),'platform/s60/root.confml')
    
    def test_get_configuration_and_get_layer_and_get_layer_resources(self):
        conf =  self.project.get_configuration("morestuff.confml")
        s60layer = conf.get_configuration('platform/s60/root.confml')
        files = s60layer.list_resources()
        self.assertEquals(files[0],'platform/s60/root.confml')
    
    def test_get_configuration_and_get_layer_and_get_a_layer_resource(self):
        conf =  self.project.get_configuration("morestuff.confml")
        s60layer = conf.get_configuration('platform/s60/root.confml')
        res = s60layer.get_resource('root.confml')
        self.assertTrue(res)
    
    def test_get_configuration_and_list_all_configuration_resources(self):
        conf =  self.project.get_configuration("morestuff.confml")
        resources = conf.list_resources()
        self.assertEquals(resources[0],'morestuff.confml')

    def test_get_configuration_and_get_first_layer_by_index(self):
        conf =  self.project.get_configuration("morestuff.confml")
        s60config = conf.get_configuration_by_index(0)
        self.assertEquals(s60config.get_path(),'platform/s60/root.confml')

    def test_get_configuration_and_get_last_layer_by_index(self):
        conf =  self.project.get_configuration("morestuff.confml")
        config = conf.get_configuration_by_index(-1)
        self.assertEquals(config.get_path(),'familyX/prodX/root.confml')
    
    def test_get_all_resources(self):
        conf =  self.project.get_configuration("morestuff.confml")
        resources = conf.get_all_resources()
        self.assertEquals(resources[0].get_path(),'morestuff.confml')
        self.assertEquals(resources[1].get_path(),'platform/s60/root.confml')

    def test_list_confmls(self):
        conf =  self.project.get_configuration("morestuff.confml")
        confmls = conf.list_resources()
        self.assertEquals(confmls[0],'morestuff.confml')
        self.assertEquals(confmls[1],'platform/s60/root.confml')
    
    def test_list_implmls(self):
        conf =  self.project.get_configuration("morestuff.confml")
        implmls = conf.get_configuration('platform/s60/root.confml').get_layer().list_implml()
        self.assertEquals(implmls[0],'implml/accessoryserver_1020505A.crml')

#    def test_list_content(self):
#        conf =  self.project.get_configuration("morestuff.confml")
#        contents = conf.list_content()
#        self.assertEquals(contents[0],'platform/s60/content/.svn/all-wcprops')
            
    def test_layered_content(self):
        conf =  self.project.get_configuration("morestuff.confml")
        contents = conf.layered_content()
        self.assertEquals(contents.get_value('test/s60.txt'),'platform/s60/content/test/s60.txt')
        self.assertEquals(contents.get_value('test/override.txt'),'familyX/content/test/override.txt')
        self.assertEquals(contents.get_value('test/shout.txt'),'familyX/content/test/shout.txt')

    def test_layer_name(self):
        conf =  self.project.get_configuration("morestuff.confml")
        s60layer = conf.get_configuration('platform/s60/root.confml')
        self.assertEquals(s60layer.get_ref(),'platform__s60__root_confml')


    def test_layered_content_with_one_layer(self):
        conf =  self.project.get_configuration("morestuff.confml")
        contents = conf.layered_content([-2])
        self.assertEquals(contents.get_value('test/override.txt'),'familyX/content/test/override.txt')
        self.assertEquals(contents.get_value('test/shout.txt'),'familyX/content/test/shout.txt')
        try:
            contents.get_value('test/s60.txt')
            self.fail("Fetching content from s60 layer succeeds!")
        except KeyError:
            pass

    def test_layered_content_with_two_layers(self):
        conf =  self.project.get_configuration("morestuff.confml")
        contents = conf.layered_content([-2,-1])
        self.assertEquals(contents.get_value('test/override.txt'),'familyX/content/test/override.txt')
        self.assertEquals(contents.get_value('test/shout.txt'),'familyX/content/test/shout.txt')
        self.assertEquals(contents.get_value('prodX/jee/ProdX_specific.txt'),'familyX/prodX/content/prodX/jee/ProdX_specific.txt')
        try:
            contents.get_value('test/s60.txt')
            self.fail("Fetching content from s60 layer succeeds!")
        except KeyError:
            pass



        
class TestConeProjectMethodsWrite(BaseTestCase):    
    def setUp(self):
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        if not os.path.exists('newtempproject'):
            os.mkdir('newtempproject')
        fs = api.Storage.open("newtempproject","a")
        self.project = api.Project(fs)

    def tearDown(self):
        self.project.close()
        shutil.rmtree('newtempproject')
        pass

    def test_create_configuration(self):
        conf = self.project.create_configuration("dummy.confml")
        self.assertTrue(conf)
        self.assertEquals(conf.get_ref(),'dummy_confml')
        self.assertTrue(isinstance(conf,api.Configuration))
        conf.close()
        
    def test_create_close_open_configuration(self):
        tempdir_orig = os.path.normpath(os.path.join(temp_dir, "temp1_orig"))
        tempdir_copy = os.path.normpath(os.path.join(temp_dir, "temp1_copy"))
        self.remove_if_exists([tempdir_orig, tempdir_copy])
        
        project = api.Project(api.Storage.open(tempdir_orig,"w"))
        conf = project.create_configuration("dummy2.confml")
        conf.set_name("dummy")
        prop1 = model.ConfmlMetaProperty('owner', 'some guy')
        prop2 = model.ConfmlMetaProperty('purpose', 'for testing')
        conf.meta = model.ConfmlMeta([prop1, prop2])
        conf.desc = "Testing to see a configuration created"
        conf.create_configuration("test/path/to/somewhere/r.confml")
        conf.create_configuration("test/path/to/elsewhere/r.confml")
        conf.save()
        project.save()
        project.close()
        
        # Make a copy of the created directory
        shutil.copytree(tempdir_orig, tempdir_copy)
        # If everything has been closed properly, the original directory
        # should now be removable
        shutil.rmtree(tempdir_orig)
        
        project2 = api.Project(api.Storage.open(tempdir_copy))
        conf2 = project2.get_configuration("dummy2.confml")
        
        self.assertEquals(conf.get_name(),conf2.get_name())
        self.assertEquals(conf2.get_name(),'dummy')
        self.assertEquals(conf2.meta[0].tag ,'owner')
        self.assertEquals(conf2.meta[0].value ,'some guy')
        self.assertEquals(conf.desc,conf2.desc)
        self.assertEquals(conf.list_configurations(),conf2.list_configurations())
        project2.close()
    
    def test_remove_configuration_non_existing(self):
        try:
            self.project.remove_configuration("dummystring.txt")
            self.fail("Removing non existing configuration succeds!")
        except exceptions.NotFound,e:
            self.assertTrue(True)
            
    def test_create_remove_configuration(self):
        conf = self.project.create_configuration("remove.confml")
        conf.save()
        conf.close()
        
        self.project.remove_configuration("remove.confml")
        try:
            conf =  self.project.get_configuration("remove.confml")
            self.fail("Opening of removed configuration succeeds!")
        except exceptions.NotFound,e:
            self.assertTrue(True)

    def test_create_configuration_in_sub_configuration(self):
        fs = api.Storage.open("newproject","w")
        project = api.Project(fs)
        conf = project.create_configuration("croot.confml")
        subconf = conf.create_configuration("test/root.confml")
        subconf.create_configuration('confml/data.confml')
        conf.save()
        self.assertTrue(project.get_storage().is_resource('test/confml/data.confml'))
        conf = project.get_configuration("croot.confml")
        subconf = conf.create_configuration("test2\\root.confml")
        subconf.create_configuration('confml/data.confml')
        subconf.close()
        conf.save()
        self.assertTrue(project.get_storage().is_resource('test2/confml/data.confml'))
        project.close()
        shutil.rmtree("newproject")

    
    
if __name__ == '__main__':
    unittest.main()
      
