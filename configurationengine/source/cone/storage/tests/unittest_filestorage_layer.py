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
Test the configuration
"""
import unittest
import string
import sys,os, shutil
import __init__

from cone.public import api,exceptions,utils
from cone.storage import filestorage

class TestLayer(unittest.TestCase):    
    storage_class = filestorage.FileStorage

    def test_create_layer(self):
        store = self.storage_class("temp/layertest","w")
        layer = api.Layer(store, "foo")
        self.assertTrue(layer)
        shutil.rmtree("temp/layertest")

#    def test_create_layer_with_kwargs(self):
#        store = self.storage_class("temp/layertest","w")
#        layer = api.Layer(store, "foo",confml_path="foobar", implml_path="")
#        self.assertTrue(layer)
#        self.assertEquals(layer.confml_folder.get_current_path(),"foo/foobar")
#        self.assertEquals(layer.implml_folder.get_current_path(),"foo")
#        layer = api.Layer(store, "foo",confml_path="f", implml_path="test", content_path="data", doc_path="foo")
#        self.assertEquals(layer.confml_folder.get_current_path(),"foo/f")
#        self.assertEquals(layer.implml_folder.get_current_path(),"foo/test")
#        self.assertEquals(layer.content_folder.get_current_path(),"foo/data")
#        self.assertEquals(layer.doc_folder.get_current_path(),"foo/foo")
#        layer = api.Layer(store, "foo")
#        self.assertEquals(layer.confml_folder.get_current_path(),"foo/confml")
#        self.assertEquals(layer.implml_folder.get_current_path(),"foo/implml")
#        self.assertEquals(layer.content_folder.get_current_path(),"foo/content")
#        self.assertEquals(layer.doc_folder.get_current_path(),"foo/doc")
#        shutil.rmtree("temp/layertest")

    def test_get_path(self):
        store = self.storage_class("temp/layertest","w")
        layer = api.Layer(store, "foo")
        self.assertTrue(layer)
        self.assertEquals(layer.get_current_path(),"foo")
        shutil.rmtree("temp/layertest")

    def test_open_resource(self):
        store = self.storage_class("temp/layertest","w")
        layer = api.Layer(store, "foo")
        self.assertTrue(layer)
        res = layer.open_resource("confml/test.confml","w")
        res.write("foo.conf")
        res.close()
        self.assertEquals(layer.list_resources("", True),["confml/test.confml"])
        self.assertEquals(store.list_resources("", True),["foo/confml/test.confml"])
        shutil.rmtree("temp/layertest")

    def test_create_two_layers_and_open_resource(self):
        store = self.storage_class("temp/layertest","w")
        foo_layer = api.Layer(store, "foo")
        bar_layer = api.Layer(store, "bar")
        res = foo_layer.open_resource("confml/test.confml","w")
        res.write("foo.conf")
        res.close()
        res = foo_layer.open_resource("root.confml","w")
        res.close()
        res = bar_layer.open_resource("confml/root.confml","w")
        res.write("foo.conf")
        res.close()
        self.assertEquals(foo_layer.list_resources("", True),['root.confml', 'confml/test.confml'])
        self.assertEquals(store.list_resources("", True),['bar/confml/root.confml','foo/root.confml','foo/confml/test.confml'])
        foo_layer.delete_resource("confml/test.confml")
        self.assertEquals(foo_layer.list_resources("", True),["root.confml"])
        self.assertEquals(store.list_resources("", True),["bar/confml/root.confml","foo/root.confml"])
        shutil.rmtree("temp/layertest")

    def test_list_confml(self):
        store = self.storage_class("temp/layertest","w")
        layer = api.Layer(store, "foo")
        res = layer.open_resource("confml/test.confml","w")
        res.write("foo.conf")
        res.close()
        res = layer.open_resource("confml/foo.confml","w")
        res.write("foo.conf")
        res.close()
        res = layer.open_resource("root.confml","w")
        res.write("foo.conf")
        res.close()
        self.assertEquals(layer.list_confml(),['confml/foo.confml', 'confml/test.confml'])
        shutil.rmtree("temp/layertest")

    def test_list_implml(self):
        store = self.storage_class("temp/layertest","w")
        layer = api.Layer(store, "foo")
        res = layer.open_resource("implml/stuff/test.confml","w")
        res.write("foo.conf")
        res.close()
        res = layer.open_resource("confml/foo.confml","w")
        res.write("foo.conf")
        res.close()
        res = layer.open_resource("root.confml","w")
        res.write("foo.conf")
        res.close()
        self.assertEquals(layer.list_implml(),['implml/stuff/test.confml'])
        shutil.rmtree("temp/layertest")

    def test_list_content(self):
        store = self.storage_class("temp/layertest","w")
        layer = api.Layer(store, "foo")
        res = layer.open_resource("content/bar/test.txt","w")
        res.write("foo.conf")
        res.close()
        res = layer.open_resource("content/foo.confml","w")
        res.write("foo.conf")
        res.close()
        res = layer.open_resource("root.confml","w")
        res.write("foo.conf")
        res.close()
        self.assertEquals(layer.list_content(),['content/foo.confml', 'content/bar/test.txt'])
        shutil.rmtree("temp/layertest")

    def test_list_doc(self):
        store = self.storage_class("temp/layertest","w")
        layer = api.Layer(store, "foo")
        res = layer.open_resource("doc/bar/test.txt","w")
        res.write("foo.conf")
        res.close()
        res = layer.open_resource("doc/foo.confml","w")
        res.write("foo.conf")
        res.close()
        res = layer.open_resource("root.confml","w")
        res.write("foo.conf")
        res.close()
        self.assertEquals(layer.list_doc(),['doc/foo.confml', 'doc/bar/test.txt'])
        shutil.rmtree("temp/layertest")

if __name__ == '__main__':
      unittest.main()
      
