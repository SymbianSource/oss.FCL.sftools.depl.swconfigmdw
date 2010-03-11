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
import sys,os
import __init__

from cone.public import api,exceptions,utils
from cone.storage import stringstorage

class TestLayer(unittest.TestCase):    
    storage_class = stringstorage.StringStorage

    def test_create_layer(self):
        store = self.storage_class.open("temp/layertest.pk","w")
        layer = api.Layer(store, "foo")
        self.assertTrue(layer)

#    def test_create_layer_with_kwargs(self):
#        store = self.storage_class.open("temp/layertest.pk","w")
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

    def test_get_path(self):
        store = self.storage_class.open("temp/layertest.pk","w")
        layer = api.Layer(store, "foo")
        self.assertTrue(layer)
        self.assertEquals(layer.get_current_path(),"foo")

    def test_open_resource(self):
        store = self.storage_class.open("temp/layertest.pk","w")
        layer = api.Layer(store, "foo")
        self.assertTrue(layer)
        res = layer.open_resource("confml/test.confml","w")
        res.write("foo.conf")
        res.close()
        self.assertEquals(layer.list_resources("", True),["confml/test.confml"])
        self.assertEquals(store.list_resources("", True),["foo/confml/test.confml"])

    def test_create_two_layers_and_open_resource(self):
        store = self.storage_class.open("temp/layertest.pk","w")
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
        self.assertEquals(foo_layer.list_resources("", True),['confml/test.confml', 'root.confml'])
        self.assertEquals(store.list_resources("", True),['bar/confml/root.confml','foo/confml/test.confml','foo/root.confml'])        
        foo_layer.delete_resource("confml/test.confml")
        self.assertEquals(foo_layer.list_resources("", True),["root.confml"])
        self.assertEquals(store.list_resources("", True),["bar/confml/root.confml","foo/root.confml"])

    def test_list_confml(self):
        store = self.storage_class.open("temp/layertest.pk","w")
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

    def test_list_implml(self):
        store = self.storage_class.open("temp/layertest.pk","w")
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

    def test_list_content(self):
        store = self.storage_class.open("temp/layertest.pk","w")
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
        self.assertEquals(layer.list_content(),['content/bar/test.txt', 'content/foo.confml'])

    def test_list_doc(self):
        store = self.storage_class.open("temp/layertest.pk","w")
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
        self.assertEquals(layer.list_doc(),['doc/bar/test.txt', 'doc/foo.confml'])

    def test_list_layer_resources(self):
        store = self.storage_class.open("temp/layertest.pk","w")
        layer = api.Layer(store, "foo")
        res = layer.open_resource("doc/bar/test.txt","w")
        res.write("foo.conf")
        res.close()
        res = layer.open_resource("confml/foo.confml","w")
        res.write("foo.conf")
        res.close()
        res = layer.open_resource("confml/bar.confml","w")
        res.write("foo.conf")
        res.close()
        res = layer.open_resource("content/data/abc.txt","w")
        res.write("foo.conf")
        res.close()
        res = layer.open_resource("foo.txt","w")
        res.write("foo.conf")
        res.close()
        self.assertEquals(layer.list_all_resources(),['confml/bar.confml', 
                                                        'confml/foo.confml', 
                                                        'content/data/abc.txt', 
                                                        'doc/bar/test.txt'])

    def test_list_layer_with_sublayer(self):
        store = self.storage_class.open("temp/layertest.pk","w")
        layer = api.Layer(store, "foo", layers=[api.Layer(store, "bar")])
        res = layer.open_resource("doc/bar/test.txt","w")
        res.write("foo.conf")
        res.close()
        res = layer.open_resource("confml/foo.confml","w")
        res.write("foo.conf")
        res.close()
        res = layer.open_resource("confml/bar.confml","w")
        res.write("foo.conf")
        res.close()
        res = layer.open_resource("content/data/abc.txt","w")
        res.write("foo.conf")
        res.close()
        res = layer.open_resource("foo.txt","w")
        res.write("foo.conf")
        res.close()
        barlayer = layer.get_layer('bar')
        res = barlayer.open_resource("content/barcode.txt","w")
        res.write("foo.conf")
        res.close()
        res = barlayer.open_resource("confml/hooo.confml","w")
        res.write("foo.conf")
        res.close()
        
        self.assertEquals(layer.list_all_resources(),['confml/bar.confml', 
                                                        'confml/foo.confml', 
                                                        'content/data/abc.txt', 
                                                        'doc/bar/test.txt',
                                                        'bar/confml/hooo.confml',
                                                        'bar/content/barcode.txt'])
        
        self.assertEquals(layer.list_implml(),[])
        self.assertEquals(layer.list_confml(),['confml/bar.confml',
                                               'confml/foo.confml',
                                               'bar/confml/hooo.confml'])
        self.assertEquals(layer.list_content(),['content/data/abc.txt', 'bar/content/barcode.txt'])
        self.assertEquals(layer.list_doc(),['doc/bar/test.txt'])

class TestCompositeLayer(unittest.TestCase):    
    storage_class = stringstorage.StringStorage

    def test_create_compositelayer(self):
        store = self.storage_class.open("temp/layertestcomposite.pk","w")
        clayer = api.CompositeLayer()
        self.assertTrue(clayer)

    def test_create_with_layer(self):
        store = self.storage_class.open("temp/layertestcomposite.pk","w")
        clayer = api.CompositeLayer("sub",layers=[api.Layer(store,"test"), api.Layer(store,"foo/bar")])
        self.assertEquals(clayer.list_layers(),['test', 'foo/bar'])

    def test_create_with_layer_and_add(self):
        store = self.storage_class.open("temp/layertestcomposite.pk","w")
        clayer = api.CompositeLayer(layers=[api.Layer(store,"test"), api.Layer(store,"foo/bar")])
        self.assertEquals(clayer.list_layers(),['test', 'foo/bar'])
        clayer.add_layer(api.Layer(store,"res"))
        self.assertEquals(clayer.list_layers(),['test', 'foo/bar', 'res'])

    def test_get_layer(self):
        store = self.storage_class.open("temp/layertestcomposite.pk","w")
        clayer = api.CompositeLayer(layers=[api.Layer(store,"test"), api.Layer(store,"foo/bar")])
        self.assertEquals(clayer.list_layers(),['test', 'foo/bar'])
        layer = clayer.get_layer('foo/bar')
        self.assertEquals(layer.get_current_path(),'foo/bar')

    def test_create_layers_with_resources_and_list_with_composite(self):
        store = self.storage_class.open("temp/layertest.pk","w")
        foolayer = api.Layer(store, "foo")
        res = foolayer.open_resource("doc/bar/test.txt","w")
        res.write("foo.conf")
        res.close()
        res = foolayer.open_resource("implml/foo2.crml","w")
        res.write("foo.conf")
        res.close()
        res = foolayer.open_resource("confml/bar.confml","w")
        res.write("foo.conf")
        res.close()
        res = foolayer.open_resource("content/data/abc.txt","w")
        res.write("foo.conf")
        res.close()
        res = foolayer.open_resource("foo.txt","w")
        res.write("foo.conf")
        res.close()
        barlayer = api.Layer(store, "bar")
        res = barlayer.open_resource("doc/bar/test.txt","w")
        res.write("foo.conf")
        res.close()
        res = barlayer.open_resource("implml/foo.crml","w")
        res.write("foo.conf")
        res.close()
        res = barlayer.open_resource("confml/bar.confml","w")
        res.write("foo.conf")
        res.close()
        res = barlayer.open_resource("content/data/abc.txt","w")
        res.write("foo.conf")
        res.close()
        res = barlayer.open_resource("foo.txt","w")
        res.write("foo.conf")
        res.close()
        clayer = api.CompositeLayer('test',layers=[foolayer,barlayer])
        
        self.assertEquals(clayer.list_all_resources(),['foo/confml/bar.confml', 
                                                       'foo/content/data/abc.txt', 
                                                       'foo/doc/bar/test.txt', 
                                                       'foo/implml/foo2.crml', 
                                                       'bar/confml/bar.confml', 
                                                       'bar/content/data/abc.txt', 
                                                       'bar/doc/bar/test.txt',
                                                       'bar/implml/foo.crml',])
        self.assertEquals(clayer.list_implml(),['foo/implml/foo2.crml','bar/implml/foo.crml'])
        self.assertEquals(clayer.list_confml(),['foo/confml/bar.confml', 'bar/confml/bar.confml'])
        self.assertEquals(clayer.list_content(),['foo/content/data/abc.txt', 'bar/content/data/abc.txt'])
        self.assertEquals(clayer.list_doc(),['foo/doc/bar/test.txt', 'bar/doc/bar/test.txt'])

if __name__ == '__main__':
      unittest.main()
      
