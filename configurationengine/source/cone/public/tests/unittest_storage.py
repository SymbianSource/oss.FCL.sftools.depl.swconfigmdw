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
Test Respource
"""
import unittest
import string
import sys,os
import pickle

from cone.public import api, exceptions, utils

ROOT_PATH       = os.path.dirname(os.path.abspath(__file__))
temp_dir        = os.path.join(ROOT_PATH, "temp/storage")
storage_path    = os.path.join(temp_dir, "layertest.pk")

class TestStorage(unittest.TestCase):    
    def setUp(self):
        pass

    def test_create_storage(self):
        res = api.Storage("")
        self.assertTrue(res)

    def test_get_root(self):
        path = os.path.join(temp_dir, "foo/faa.pk")
        store = api.Storage.open(path,"w")
        self.assertEquals(store.get_path(),path)

    def test_set_path(self):
        path = os.path.join(temp_dir, "foo/faa.pk")
        store = api.Storage.open(path,"w")
        self.assertEquals(store.get_path(),path)
        store.set_current_path("faa")
        self.assertEquals(store.get_current_path(),"faa")

    def test_get_more_read(self):
        storage = api.Storage("")
        self.assertEquals(storage.get_mode("r"),storage.MODE_READ)
        self.assertEquals(storage.get_mode("rb"),storage.MODE_READ)
        
    def test_get_more_write(self):
        storage = api.Storage("")
        self.assertEquals(storage.get_mode("w"),storage.MODE_WRITE)
        self.assertEquals(storage.get_mode("wb"),storage.MODE_WRITE)

    def test_get_more_append(self):
        storage = api.Storage("")
        self.assertEquals(storage.get_mode("a"),storage.MODE_APPEND)
        self.assertEquals(storage.get_mode("ab"),storage.MODE_APPEND)

    def test_get_more_unknown(self):
        storage = api.Storage("")
        self.assertEquals(storage.get_mode("1"),storage.MODE_UNKNOWN)
        self.assertEquals(storage.get_mode("2b"),storage.MODE_UNKNOWN)

class TestStorageGeneric(unittest.TestCase):
    def test_list_resources(self):
        store = api.Storage.open(storage_path,"w")
        self.assertTrue(store)
        self.assertEquals(store.list_resources(""), [])

    def test_open_resource_nonexisting(self):
        store = api.Storage.open(storage_path,"w")
        self.assertTrue(store)
        try:
            res = store.open_resource("test")
            res.close()
            self.fail("Opening non existing resource succeeds")
        except exceptions.NotResource,e:
            pass

    def test_is_resource_nonexisting(self):
        store = api.Storage.open(storage_path,"w")
        self.assertTrue(store)
        self.assertFalse(store.is_resource("test"))

    def test_open_resource_is_resource(self):
        store = api.Storage.open(storage_path,"w")
        self.assertTrue(store)
        res = store.open_resource("test","w")
        res.write("Testing writing more")
        res.close()
        self.assertTrue(store.is_resource('test'))

    def test_open_resource_write_and_write(self):
        store = api.Storage.open(storage_path,"w")
        self.assertTrue(store)
        res = store.open_resource("test","w")
        res.write("Testing writing more")
        res.close()
        res = store.open_resource("test","w")
        res.write("writing")
        res.close()
        self.assertEquals(store._get('test').data, 'writing')
    
    def test_get_size_on_write_only_resource_fails(self):
        store = api.Storage.open(storage_path,"w")
        self.assertTrue(store)
        res = store.open_resource("test","w")
        res.write("Writing foobar")
        self.assertRaises(exceptions.StorageException, res.get_size)
        res.close()
    
    def test_open_resource_and_get_size(self):
        store = api.Storage.open(storage_path,"w")
        self.assertTrue(store)
        res = store.open_resource("test","w")
        res.write("Writing foobar")
        res.close()
        
        res = store.open_resource("test","r")
        self.assertEquals(res.get_size(), 14)
        res.close()
    
    def test_write_fails_on_read_mode(self):
        store = api.Storage.open(storage_path, "w")
        self.assertTrue(store)
        res = store.open_resource("test","w")
        res.write("Testing writing more")
        res.close()
        resr = store.open_resource("test","r")
        try:
            resr.write("Testing writing more")
            resr.close()
            self.fail("Writing succeeds on read mode?")
        except exceptions.StorageException, e:
            pass

    def test_open_resource_append(self):
        store = api.Storage.open(storage_path,"w")
        self.assertTrue(store)
        res = store.open_resource("test","a")
        res.write("Testing append.\n")
        res.close()
        res = store.open_resource("test","a")
        res.write("appending!")
        res.close()
        self.assertEquals(store.test.data, 'Testing append.\nappending!')
    
    def test_open_multiple_no_close_and_write_closed(self):
        store = api.Storage.open(storage_path,"w")
        self.assertTrue(store)
        res1 = store.open_resource("test","a")
        res1.write("Testing append.\n")
        res1.close()
        res2 = store.open_resource("test","a")
        res2.write("appending!")
        res2.close()
        try:
            res2.write("sss")
            self.fail("writing on closed object succeeds?")
        except ValueError:
            pass
        self.assertEquals(store.test.data, 'Testing append.\nappending!')

    def test_open_many_to_one(self):
        store = api.Storage.open(storage_path,"w")
        self.assertTrue(store)
        res1 = store.open_resource("test/foo.txt","a")
        res1.write("Testing\n")
        res1.close()
        res1 = store.open_resource("test/foo.txt","w")
        res1.close()
        self.assertEquals(store.list_resources('', recurse=True),['test/foo.txt'])

    def test_open_many(self):
        store = api.Storage.open(storage_path,"w")
        self.assertTrue(store)
        res1 = store.open_resource("test/foo.txt","a")
        res1.write("Testing\n")
        res1.close()
        res2 = store.open_resource("test/bar.txt","a")
        res2.write("Writing bar!")
        res2.close()
        self.assertEquals(store.test.foo.data, 'Testing\n')
        self.assertEquals(store.test.bar.data, 'Writing bar!')

    def test_open_many_to_a_hierarchy_and_list_folders(self):
        store = api.Storage.open(storage_path,"w")
        self.assertTrue(store)
        root= store.open_resource("root.txt","a")
        root.write("root\n")
        root.close()
        res1 = store.open_resource("test/foo.txt","a")
        res1.write("Testing\n")
        res1.close()
        res2 = store.open_resource("test/bar.txt","a")
        res2.write("Writing bar!")
        res2.close()
        self.assertEquals(store.list_resources('/'), ['root.txt'])
        self.assertEquals(store.list_resources('/test'), ['test/bar.txt',
                                                          'test/foo.txt'])
        self.assertEquals(store.list_resources('/',recurse=True), ['root.txt',
                                                           'test/bar.txt',
                                                           'test/foo.txt'])

    def test_open_resource_and_delete(self):
        store = api.Storage.open(storage_path,"w")
        self.assertTrue(store)
        res = store.open_resource("test1.txt","a")
        res.write("Testing append.\n")
        res.close()
        res = store.open_resource("test2.txt","w")
        res.write("Testing append.\n")
        res.close()
        res = store.open_resource("test3.txt","w")
        res.write("Testing append.\n")
        res.close()
        for res in store.list_resources(''):
            store.delete_resource(res)
        self.assertEquals(store.list_resources(''), [])

    def test_open_resources_and_read(self):
        store = api.Storage.open(storage_path,"w")
        self.assertTrue(store)
        res = store.open_resource("test1.txt","w")
        res.write("Testing reading.\n")
        res.close()
        res = store.open_resource("test2.txt","w")
        res.write("Testing reading.\n")
        res.close()
        res = store.open_resource("test3.txt","w")
        res.write("Testing reading.\n")
        res.close()
        for res in store.list_resources(''):
            res = store.open_resource(res)
            self.assertEquals(res.read(), "Testing reading.\n")
    
    def test_open_resources_and_save_and_dump(self):
        temp_file = os.path.join(temp_dir, "FooStore.pk")
        store = api.Storage.open(temp_file, "w")
        self.assertTrue(store)
        res1 = store.open_resource("test1.txt","w")
        res1.write("Testing reading.\n")
        res2 = store.open_resource("test2.txt","w")
        res2.write("Testing reading.\n")
        res3 = store.open_resource("test3.txt","w")
        res3.write("Testing reading.\n")
        store.save()
        
    def test_open_resources_and_load(self):
        temp_file = os.path.join(temp_dir, "store.pk")
        store = api.Storage.open(temp_file,"w")
        self.assertTrue(store)
        res1 = store.open_resource("test1.txt","w")
        res1.write("Testing reading.\n")
        res2 = store.open_resource("test2.txt","w")
        res2.write("Testing reading.\n")
        res3 = store.open_resource("test3.txt","w")
        res3.write("Testing reading.\n")
        store.close()
        store2 = api.Storage.open(temp_file)
        self.assertEquals(store2.list_resources(''), ['test1.txt',
                                                     'test2.txt',
                                                     'test3.txt'])
        self.assertEquals(store2.open_resource("test1.txt").read(),'Testing reading.\n')
        self.assertEquals(store2.open_resource("test2.txt").read(),'Testing reading.\n')
        self.assertEquals(store2.open_resource("test3.txt").read(),'Testing reading.\n')

    def test_import_resources(self):
        temp_file = os.path.join(temp_dir, "importsource.pk")
        store = api.Storage.open(temp_file, "w")
        self.assertTrue(store)
        res1 = store.open_resource("test1.txt","w")
        res1.write("Testing reading.\n")
        res2 = store.open_resource("test2.txt","w")
        res2.write("Testing reading.\n")
        res3 = store.open_resource("test3.txt","w")
        res3.write("Testing reading.\n")
        store.save()
        res3.close()
        store2 = api.Storage.open(temp_file, "w")
        store2.import_resources(store.list_resources(''), store)
        self.assertEquals(store2.open_resource("test1.txt").read(),store.open_resource('test1.txt').read())
        self.assertEquals(store2.open_resource("test2.txt").read(),store.open_resource('test2.txt').read())
        self.assertEquals(store2.open_resource("test3.txt").read(),store.open_resource('test3.txt').read())
        store2.close()
        
    def test_export_resources(self):
        temp_file = os.path.join(temp_dir, "exportsource.pk")
        store = api.Storage.open(temp_file, "w")
        self.assertTrue(store)
        res1 = store.open_resource("test1.txt","w")
        res1.write("Testing reading.\n")
        res2 = store.open_resource("test2.txt","w")
        res2.write("Testing reading.\n")
        res3 = store.open_resource("test3.txt","w")
        res3.write("Testing reading.\n")
        store.save()
        store2 = api.Storage.open(temp_file, "w")
        store.export_resources(store.list_resources(''), store2)
        res2 = store2.open_resource("test1.txt")
        res1 = store.open_resource('test1.txt')
        self.assertEquals(res1.read(),res2.read())
        self.assertEquals(store2.open_resource("test2.txt").read(),store.open_resource('test2.txt').read())
        self.assertEquals(store2.open_resource("test3.txt").read(),store.open_resource('test3.txt').read())
        store2.close()

    def test_export_modify_and_close_and_open(self):
        temp_file = os.path.join(temp_dir, "exportsource.pk")
        store = api.Storage.open(temp_file,"w")
        self.assertTrue(store)
        res1 = store.open_resource("test1.txt","w")
        res1.write("Testing reading.\n")
        res1.close()
        
        res2 = store.open_resource("test2.txt","w")
        res2.write("Testing reading.\n")
        res3 = store.open_resource("test3.txt","w")
        res3.write("Testing reading.\n")
        
        res1 = store.open_resource("test1.txt","w")
        res1.write("Testing reading too.\n")
        res1.close()
        
        store.close()
        
        modified_temp_file = os.path.join(temp_dir, "modified.pk")
        store2 = api.Storage.open(modified_temp_file, "w")
        store.export_resources(store.list_resources(''), store2)
        store2.delete_resource('test3.txt')
        resr = store2.open_resource('test2.txt')
        resw = store2.open_resource('test2.txt','w')
        resw.write("Now this sould be different")
        store2.close()
        store3 = api.Storage.open(modified_temp_file)
        self.assertEquals(store3.list_resources(''), ['test1.txt',
                                                     'test2.txt'])
        self.assertEquals(store3.open_resource("test2.txt").read(),'Now this sould be different')
        self.assertEquals(store3.open_resource("test1.txt").read(),'Testing reading too.\n')
        

    def test_get_path_set_path(self):
        temp_file = os.path.join(temp_dir, "subpath.pk")
        store = api.Storage.open(temp_file,"w")
        self.assertEquals(store.get_path(),temp_file)
        self.assertEquals(store.get_current_path(),"")
        store.set_current_path("subdir")
        self.assertEquals(store.get_current_path(),"subdir")

    def test_set_path_open_resource(self):
        temp_file = os.path.join(temp_dir, "subpath.pk")
        if os.path.exists(temp_file): os.unlink(temp_file)
        
        store = api.Storage.open(temp_file,"w")
        self.assertEquals(store.get_path(),temp_file)
        store.set_current_path("subdir")
        self.assertEquals(store.get_current_path(),"subdir")
        res = store.open_resource("foo.txt","w")
        res.write("foo")
        res.close()
        self.assertEquals(store.list_resources(""), ["foo.txt"])
        store.set_current_path("/")
        self.assertEquals(store.list_resources("", recurse=True), ["subdir/foo.txt"])
        store.close()
        os.unlink(temp_file)

    def test_create_folder(self):
        temp_file = os.path.join(temp_dir, "subpath.pk")
        store = api.Storage.open(temp_file,"w")
        store.create_folder("subdir/test")
        self.assertTrue(store.is_folder("subdir/test"))

    def test_create_folder_and_delete_folder(self):
        temp_file = os.path.join(temp_dir, "subpath.pk")
        store = api.Storage.open(temp_file,"w")
        store.create_folder("subdir/test")
        self.assertTrue(store.is_folder("subdir/test"))
        store.delete_folder("subdir/test")
        self.assertFalse(store.is_folder("subdir/test"))
        self.assertTrue(store.is_folder("subdir"))

class TestFolder(unittest.TestCase):    

    def test_create_folder(self):
        store = api.Storage.open(storage_path,"w")
        layer = api.Folder(store, "foo")
        self.assertTrue(layer)

    def test_get_path(self):
        store = api.Storage.open(storage_path,"w")
        layer = api.Folder(store, "foo")
        self.assertTrue(layer)
        self.assertEquals(layer.get_current_path(),"foo")

    def test_open_resource(self):
        store = api.Storage.open(storage_path,"w")
        layer = api.Folder(store, "foo")
        self.assertTrue(layer)
        res = layer.open_resource("confml/test.confml","w")
        res.write("foo.conf")
        res.close()
        self.assertEquals(layer.list_resources("", recurse=True),["confml/test.confml"])
        self.assertEquals(store.list_resources("", recurse=True),["foo/confml/test.confml"])

    def test_create_two_layers_and_open_resource(self):
        store = api.Storage.open(storage_path,"w")
        foo_layer = api.Folder(store, "foo")
        bar_layer = api.Folder(store, "bar")
        res = foo_layer.open_resource("confml/test.confml","w")
        res.write("foo.conf")
        res.close()
        res = foo_layer.open_resource("root.confml","w")
        res.close()
        res = bar_layer.open_resource("confml/root.confml","w")
        res.write("foo.conf")
        res.close()
        self.assertEquals(foo_layer.list_resources("", recurse=True),['root.confml', 'confml/test.confml'])
        self.assertEquals(store.list_resources("", recurse=True),['bar/confml/root.confml',
                                                                  'foo/root.confml',
                                                                  'foo/confml/test.confml'])
        
        foo_layer.delete_resource("confml/test.confml")
        self.assertEquals(foo_layer.list_resources("", recurse=True),["root.confml"])
        self.assertEquals(store.list_resources("", recurse=True),["bar/confml/root.confml",
                                                                  "foo/root.confml"])


if __name__ == '__main__':
    unittest.main()
      
