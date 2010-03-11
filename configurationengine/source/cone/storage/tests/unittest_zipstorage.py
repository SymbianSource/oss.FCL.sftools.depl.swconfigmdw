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

import __init__
from cone.public import exceptions, api
from cone.storage import zipstorage

datazip   = os.path.join(ROOT_PATH,"data.zip")

#class TestZipStorageDummy(unittest.TestCase): 
#    def test_open_storage(self):
#        storage = zipstorage.ZipStorage("TestProlog.zip","r")
#        res = storage.open_resource("TestProlog")
#        storage.close()

class TestZipStorage(unittest.TestCase): 
    def test_create_new_storage(self):
        storage = zipstorage.ZipStorage("new.zip","w")
        storage.close()
        self.assertTrue(os.path.exists("new.zip"))
        os.unlink("new.zip")
        
    def test_open_existing_storage(self):
        storage = zipstorage.ZipStorage(datazip,"r")
        storage.close()

    def test_open_existing_storage_and_close_twice(self):
        storage = zipstorage.ZipStorage(datazip,"r")
        storage.close()
        try:
            storage.close()
            self.fail('closing twice succeeds!')
        except exceptions.StorageException:
            pass

    def test_open_nonexisting_storage_fails(self):
        try:
            storage = zipstorage.ZipStorage("foo.zip","r")
            storage.close()
            self.fail("opening a non existing ZipStorage succeeded?")
        except zipstorage.ZipException:
            self.assertTrue(True)
  
    def test_open_a_non_zipfile_fails(self):
        try:
            storage = zipstorage.ZipStorage("data/onefile/test.txt","r")
            storage.close()
            self.fail("opening a non zipfile for ZipStorage succeeded?")
        except zipstorage.ZipException,e:
            self.assertTrue(True)

class TestStorage(unittest.TestCase):
    def setUp(self):
        shutil.copyfile(datazip,"temptests.zip")
        self.storage = zipstorage.ZipStorage("temptests.zip","a")

    def tearDown(self):
        self.storage.close()
        os.unlink("temptests.zip")

    def test_open_resource_existing_file_for_reading(self):
        res = self.storage.open_resource("data/simple.confml","w")
        self.assertTrue(res)
        self.assertTrue(isinstance(res,api.Resource))

    def test_open_resource_new_file(self):
        storage = zipstorage.ZipStorage("testnewfile.zip","w")
        res = storage.open_resource("data/newfile.txt","w")
        res.write("test write")
        self.assertTrue(res)
        self.assertTrue(isinstance(res,api.Resource))
        res.close()
        self.assertEquals(storage.list_resources("",True), ['data/newfile.txt'])
        storage.close()
        os.unlink("testnewfile.zip")
        

    def test_open_resource_nonexisting(self):
        try:
            res = self.storage.open_resource("iamnothere.txt")
            self.fail("Opening of a non existing file succeeds!??")
        except exceptions.NotResource: 
            self.assertTrue(True)

    def test_list_resources_nonrecurse(self):
        storage = zipstorage.ZipStorage("testnonrecurse.zip","w")
        res = storage.open_resource("data/morestuff.confml","w")
        res.close()
        res = storage.open_resource("data/prodX.confml","w")
        res.close()
        file_array = storage.list_resources("data")
        self.assertEquals(file_array[0],"data/morestuff.confml")
        self.assertEquals(file_array[1],"data/prodX.confml")
        storage.close()
        os.unlink("testnonrecurse.zip")

    def test_list_resources_recurse(self):
        storage = zipstorage.ZipStorage("testrecurse.zip","w")
        res = storage.open_resource("data/foo/morestuff.confml","w")
        res.close()
        res = storage.open_resource("data/prodX.confml","w")
        res.close()
        res = storage.open_resource("data/ncp11/confml/jallaa.confml","w")
        res.close()
        file_array = storage.list_resources("data",True)
        self.assertEquals(file_array,['data/foo/morestuff.confml', 'data/prodX.confml', 'data/ncp11/confml/jallaa.confml'])
        storage.close()
        os.unlink("testrecurse.zip")

    def test_is_resource_true(self):
        res = self.storage.open_resource("data/simple.confml","w")
        res.close()
        self.assertTrue(self.storage.is_resource("data/simple.confml"))

    def test_is_resource_true_for_dotted_file(self):
        res = self.storage.open_resource(".metadata","w")
        res.close()
        self.assertTrue(self.storage.is_resource(".metadata"))

    def test_is_resource_true_with_slash(self):
        res = self.storage.open_resource("data/simple.confml","w")
        res.close()
        self.assertTrue(self.storage.is_resource("/data/simple.confml"))

    def test_is_resource_false(self):
        self.assertFalse(self.storage.is_resource("data"))

    def test_metadata_writing(self):
        fs = zipstorage.ZipStorage("testtemp.zip","w")
        fs.set_active_configuration('testing.confml')
        fs.close()
        fs = zipstorage.ZipStorage("testtemp.zip","r")
        self.assertEquals(fs.get_active_configuration(),'testing.confml')
        fs.close()
        os.unlink("testtemp.zip")

    def test_open_resource_new_file_and_overwrite(self):
        storage = api.Storage.open("testoverwrite.zip","w")
        res = storage.open_resource("data/newfile.txt","w")
        res.write("test write")
        self.assertTrue(res)
        self.assertTrue(isinstance(res,api.Resource))
        res.close()
        res = storage.open_resource("data/newfile.txt","w")
        res.write("Hahaaa")
        res.close()
        storage.close()
        storage = api.Storage.open("testoverwrite.zip","r")
        self.assertEquals(storage.open_resource("data/newfile.txt").read(), "Hahaaa")
        storage.close()
        os.unlink("testoverwrite.zip")

    def test_delete_resource(self):
        storage = api.Storage.open("testdelete.zip","w")
        res = storage.open_resource("data/newfile.txt","w")
        res.write("test write")
        res.close()
        res = storage.open_resource("readme.txt","w")
        res.write("test 2")
        res.close()
        storage.close()
        storage2 = api.Storage.open("testdelete.zip","a")
        #self.assertEquals(storage2.list_resources("",True), ['.metadata', 'data/newfile.txt', 'readme.txt'])
        self.assertEquals(storage2.open_resource("data/newfile.txt").read(),"test write")
        storage2.delete_resource("data/newfile.txt")
        self.assertEquals(len(storage2.list_resources("",True)),2)
        storage2.close()
        storage3 = api.Storage.open("testdelete.zip","a")
        self.assertEquals(storage3.list_resources("",True), ['readme.txt','.metadata'])
        storage3.close()
        os.unlink("testdelete.zip")
        

    def test_create_folder(self):        
        storage = api.Storage.open("empty_folder.zip","w")
        res = storage.open_resource("test.txt","w")
        res.write('test')
        res.close()
        storage.create_folder("data")
        storage.create_folder("data2/folder1")
        storage.create_folder("data3\\")
        storage.close()
        
        storage2 = api.Storage.open("empty_folder.zip","a")
        self.assertEquals(storage2.is_folder("data"),True)
        self.assertEquals(storage2.is_folder("data2/folder1"),True)
        self.assertEquals(storage2.is_folder("data3"),True)
        self.assertEquals(storage2.list_resources('.',True),['test.txt','.metadata'])
        self.assertEquals(storage2.list_resources(''),['test.txt','.metadata'])
        storage2.close()
        os.unlink("empty_folder.zip")

class TestZipStorageListResources(unittest.TestCase):
    
    def _run_test_list_resources(self, zip_file):
        full_path = os.path.join(ROOT_PATH, 'list_resources_data', zip_file)
        zs = zipstorage.ZipStorage(full_path, 'r')
        res_list = zs.list_resources('/', recurse=True, empty_folders=True)
        
        expected = [
            ('folder',      'test'),
            ('folder',      'test/layer'),
            ('folder',      'test/layer/confml'),
            ('folder',      'test/layer/content'),
            ('folder',      'test/layer/content/empty'),
            ('folder',      'test/layer/content/something'),
            ('resource',    'test/layer/content/something/x.txt'),
            ('folder',      'test/layer/doc'),
            ('folder',      'test/layer/implml'),
            ('resource',    'test/layer/root.confml'),
            ('resource',    'test/root.confml')]
        for type, res in expected:
            if type == 'resource':
                self.assertTrue(zs.is_resource(res), "zs.is_resource('%s') returns False" % res)
            elif type == 'folder':
                self.assertTrue(zs.is_folder(res), "zs.is_folder('%s') returns False" % res)
            else:
                raise RuntimeError('Invalid type')
    
    def test_list_resources_7zip_zipped(self):
        self._run_test_list_resources('7zip.zip')
    
    def test_list_resources_winzip_zipped(self):
        self._run_test_list_resources('winzip.zip')
    
    def test_list_resources_carbide_ct_zipped(self):
        self._run_test_list_resources('carbide.ct.cpf')
    
if __name__ == '__main__':
      unittest.main()
