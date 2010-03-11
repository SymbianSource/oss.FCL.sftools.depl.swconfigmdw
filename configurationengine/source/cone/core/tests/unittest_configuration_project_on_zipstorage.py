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
import sys,os, shutil
import __init__

from cone.public import exceptions, api
from cone.core import *
from testautomation.base_testcase import BaseTestCase
from cone.confml import model

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
temp_dir  = os.path.join(ROOT_PATH, "temp/project_on_zipstorage")
datazip   = os.path.join(ROOT_PATH,"testdata/test_project.cpf")

class TestConeProjectOpenZip(unittest.TestCase):    
    def test_open_project(self):        
        fs = api.Storage.open(datazip,"r")
        p = api.Project(fs)
        self.assertTrue(p)
        
    def test_open_project_of_non_storage(self):
        fs = ""
        try:
            p = api.Project(fs)
            self.fail("Opening on top of non storage succeeds!!")
        except exceptions.StorageException:
            self.assertTrue(True)
      

class TestConeProjectMethodsReadZip(unittest.TestCase):
    def setUp(self):
        fs = api.Storage.open(datazip,"r")
        self.project = api.Project(fs)
        
    def test_list_configurations(self):
        confs =  self.project.list_configurations()
        self.assertEquals(
            sorted(confs),
            ["root1.confml",
             "root2.confml",
             "root3.confml",
             "root4.confml",
             "root5.confml"])
        
    def test_get_configuration(self):
        conf =  self.project.get_configuration("/root5.confml")
        self.assertTrue(conf)
        self.assertTrue(isinstance(conf,api.ConfigurationProxy))
            
    def test_get_configuration_non_existing(self):
        try:
            conf =  self.project.get_configuration("foo")
            self.fail("Opening non existing configuration succeeds!")
        except exceptions.NotFound,e:
            self.assertTrue(True)

    def test_get_configuration_and_list_layers(self):
        conf =  self.project.get_configuration("root5.confml")
        layers = conf.list_configurations()    
        self.assertEquals(
            layers,
            ['Layer1/root.confml',
             'Layer2/root.confml',
             'Layer3/root.confml',
             'Layer4/root.confml',
             'Layer5/root.confml'])

    def test_get_configuration_and_get_layer(self):
        conf =  self.project.get_configuration("root5.confml")
        layer1 = conf.get_configuration('Layer1/root.confml')
        self.assertTrue(layer1)
        self.assertTrue(isinstance(layer1,api.ConfigurationProxy))

    def test_get_configuration_and_get_layer_path(self):
        conf =  self.project.get_configuration("root5.confml")
        layer1 = conf.get_configuration('Layer1/root.confml')
        self.assertEquals(layer1.get_path(),'Layer1/root.confml')
    
    def test_get_configuration_and_get_layer_and_get_layer_resources(self):
        conf =  self.project.get_configuration("root5.confml")
        layer1 = conf.get_configuration('Layer1/root.confml')
        files = layer1.list_resources()
        self.assertTrue('Layer1/root.confml' in files)
        self.assertTrue('Layer1/confml/feature1.confml' in files)
        self.assertTrue('Layer1/implml/feature1_12341001.crml' in files)
        self.assertTrue('Layer1/content/default_file.txt' in files)

    def test_get_configuration_and_get_layer_and_get_a_layer_resource(self):
        conf =  self.project.get_configuration("root5.confml")
        layer1 = conf.get_configuration('Layer1/root.confml')
        res = layer1.get_resource('implml/feature1_12341001.crml')
        self.assertTrue(res)

    def test_get_configuration_and_list_all_configuration_resources(self):
        conf =  self.project.get_configuration("root5.confml")
        resources = conf.list_resources()
        self.assertTrue('root5.confml' in resources)
        self.assertTrue('Layer1/root.confml' in resources)
        self.assertTrue('Layer2/root.confml' in resources)
        self.assertTrue('Layer3/root.confml' in resources)
        self.assertTrue('Layer4/root.confml' in resources)
        self.assertTrue('Layer5/root.confml' in resources)
        self.assertTrue('Layer1/confml/feature1.confml' in resources)
        self.assertTrue('Layer1/implml/feature1_12341001.crml' in resources)
        self.assertTrue('Layer1/content/default_file.txt' in resources)
        self.assertTrue('Layer2/content/layer2_file.txt' in resources)

class TestConeProjectMethodsWriteZip(BaseTestCase):
    def setUp(self):
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
    def test_create_configuration(self):
        tempzip = os.path.normpath(os.path.join(temp_dir, "temp1.zip"))
        self.remove_if_exists(tempzip)
        
        prj = None
        conf = None
        try:
            prj = api.Project(api.Storage.open(tempzip,"w"))
            conf = prj.create_configuration("dummy.confml")
            conf.set_name("dummy")
            self.assertTrue(conf)
            self.assertEquals(conf.get_name(),'dummy')
            self.assertTrue(isinstance(conf,api.Configuration))
        finally:
            if conf != None: conf.close()
            if prj != None:  prj.close()

    def test_create_close_open_configuration(self):
        tempzip_orig = os.path.normpath(os.path.join(temp_dir, "temp2_orig.zip"))
        tempzip_copy = os.path.normpath(os.path.join(temp_dir, "temp2_copy.zip"))
        self.remove_if_exists([tempzip_orig, tempzip_copy])
        
        prj = api.Project(api.Storage.open(tempzip_orig,"w"))
        conf = prj.create_configuration("dummy2.confml")
        conf.set_name("dummy")
        prop1 = model.ConfmlMetaProperty('owner', 'teemu rytkonen', 'http://www.s60.com/xml/confml/2')
        prop2 = model.ConfmlMetaProperty('purpose', 'for testing', 'http://www.s60.com/xml/confml/2')
        conf.meta = model.ConfmlMeta([prop1, prop2])        
        conf.desc = "Testing to see a configuration created"
        conf.create_configuration("test/path/to/somewhere/r.confml")
        conf.create_configuration("test/path/to/elsewhere/r.confml")
        conf.save()
        prj.save()
        prj.close()
        
        # Make a copy of the created zip file
        shutil.copy2(tempzip_orig, tempzip_copy)
        # If everything has been closed properly, the original zip file
        # should now be removable
        os.remove(tempzip_orig)
        
        # Read back data from the copy
        prj = api.Project(api.Storage.open(tempzip_copy,"r"))
        conf2 = prj.get_configuration("dummy2.confml")        
        self.assertEquals(conf.get_name(),conf2.get_name())
        self.assertEquals(conf.meta,conf2.meta)
        self.assertEquals(conf.desc,conf2.desc)
        self.assertEquals(conf.list_configurations(),conf2.list_configurations())
    
if __name__ == '__main__':
    unittest.main()
