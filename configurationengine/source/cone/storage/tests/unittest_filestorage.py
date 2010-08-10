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
Test the CPF root file parsing routines
"""

import zipfile
import unittest
import string
import sys,os,shutil
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

from cone.public.exceptions import NotResource,StorageException
from cone.public import api 
from cone.storage import filestorage

datafolder= ROOT_PATH
datazip   = os.path.join(ROOT_PATH,"data.zip")
datafolder= os.path.join(ROOT_PATH,"data")


#class TestFileStorageCreation(unittest.TestCase):    
#    def setUp(self):
#        pass
#    def test_create_storage_on_non_existing_path_fails(self):
#        try:
#            storage = filestorage.FileStorage("dummydatafolder")
#            self.fail("opening on dummydatafolder succeeds?")
#        except StorageException,e:
#            self.assertTrue(True)
#
#    def test_create_storage_on_file_fails(self):
#        try:
#            storage = filestorage.FileStorage(datazip)
#            self.fail("opening on data file succeeds?")
#        except StorageException,e:
#            self.assertTrue(True)
#
#    def test_create_storage_on_new_directory(self):
#        storage = filestorage.FileStorage("dummytest/storage","w")
#        self.assertTrue(os.path.exists("dummytest/storage"))
#        shutil.rmtree("dummytest")
#
class TestFileStorage(unittest.TestCase):    
#    def setUp(self):
#        self.storage = filestorage.FileStorage(datafolder)
#
#    def test_supported_storage(self):        
#        self.assertTrue(filestorage.FileStorage.supported_storage("C:/GenerationRegressionTest/wc/genregtest_workdir/cone_vs_ct2/pf7132_020.006/config_project/"))
#        self.assertTrue(filestorage.FileStorage.supported_storage("C:/GenerationRegressionTest/wc/genregtest_workdir"))
#        self.assertFalse(filestorage.FileStorage.supported_storage("C:/GenerationRegressionTest/wc/genregtest_workdir.zip"))
#    
#    def test_open_resource_existing_file_for_reading(self):
#        res = self.storage.open_resource("simple.confml")
#        self.assertTrue(res)
#        self.assertTrue(isinstance(res,api.Resource))
#
#    def test_open_resource_new_file(self):
#        res = self.storage.open_resource("newfile.txt","w")
#        self.assertTrue(res)
#        self.assertTrue(isinstance(res,api.Resource))
#        res.close()
#        self.assertTrue(os.path.exists(datafolder+"/newfile.txt"))
#        os.remove(datafolder+"/newfile.txt")
#
#    def test_list_resources(self):
#        self.assertEquals(sorted(self.storage.list_resources(".")),
#                          sorted(['.metadata', 'morestuff.confml', 'prodX.confml', 'simple.confml']))
#        
#    def test_delete_resource(self):
#        tf = open(os.path.join(datafolder,"tempfile.txt"),"w")
#        tf.close()
#        res = self.storage.delete_resource("tempfile.txt")
#        self.assertFalse(os.path.exists(datafolder+"tempfile.txt"))
#        
#    def test_open_resource_nonexisting(self):
#        try:
#            res = self.storage.open_resource("iamnothere.txt")
#            self.fail("Opening of a non existing file succeeds!??")
#        except NotResource: 
#            self.assertTrue(True)
#
#    def test_list_resources_nonrecurse(self):
#        file_array = self.storage.list_resources("")
#        self.assertTrue(".metadata" in file_array)
#
#    def test_list_resources_nonrecurse_from_root(self):
#        file_array = self.storage.list_resources("/")
#        self.assertTrue(".metadata" in file_array)
#
#    def test_list_resources_recurse_from_root(self):
#        file_array = self.storage.list_resources("",True)
#        self.assertTrue(".metadata" in file_array)
#
#    def test_list_resources_from_subfolder(self):
#        file_array = self.storage.list_resources("familyX")
#        self.assertTrue("familyX/root.confml" in file_array)
#
#    def test_list_resources_recurse_from_subfolder(self):
#        file_array = self.storage.list_resources("familyX", True)
#        self.assertTrue("familyX/root.confml" in file_array)
#        # Count only non-SVN files
#        self.assertEquals(len(filter(lambda x: x.find('.svn') == -1, file_array)), 7)
#
#    def test_is_resource_true(self):
#        self.assertTrue(self.storage.is_resource("simple.confml"))
#
#    def test_is_resource_true_with_begin_slash(self):
#        self.assertTrue(self.storage.is_resource("/simple.confml"))
#
#    def test_is_resource_false(self):
#        self.assertFalse(self.storage.is_resource("data"))
#
#    def test_open_resource_existing_file_with_root(self):
#        res = self.storage.open_resource("/simple.confml")
#        self.assertTrue(res)
#        self.assertTrue(isinstance(res,api.Resource))
#
#
#    def test_create_folder(self):
#        store = filestorage.FileStorage("newtestfolder","w")
#        store.create_folder("subdir")
#        self.assertTrue(store.is_folder("subdir"))
#        self.assertTrue(os.path.exists("newtestfolder/subdir"))
#        store.create_folder('foo')
#        layer = api.Folder(store, "foo")
#        self.assertTrue(store.is_folder("foo"))
#        self.assertTrue(layer)
#        self.assertTrue(os.path.exists("newtestfolder/subdir"))
#        layer.create_folder("foosubdir")
#        self.assertTrue(store.is_folder("foo/foosubdir"))
#        self.assertTrue(os.path.exists("newtestfolder/foo/foosubdir"))
#        shutil.rmtree('newtestfolder')

    def test_metadata_writing(self):
        fs = filestorage.FileStorage("testtemp","w")
        fs.set_active_configuration('testing.confml')
        fs.close()
        fs = filestorage.FileStorage("testtemp","r")
        self.assertEquals(fs.get_active_configuration(),'testing.confml')
        fs.close()
        shutil.rmtree("testtemp")
       

if __name__ == '__main__':
    unittest.main()
