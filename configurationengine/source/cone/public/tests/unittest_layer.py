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


from cone.public import api
from cone.storage import stringstorage

class TestFolder(unittest.TestCase):    
    storage_class = stringstorage.StringStorage
    def setUp(self):
        self.store = self.storage_class.open("temp/layertest.pk","w")

    def test_create_folder(self):
        folder = api.Folder(self.store, "subfolder")
        self.assertTrue(folder)

    def test_get_path(self):
        folder = api.Folder(self.store, "foo")
        self.assertEquals(folder.get_current_path(),"foo")

    def test_open_resource(self):
        folder = api.Folder(self.store, "foo")
        res = folder.open_resource("confml/test.confml","w")
        res.write("foo.conf")
        res.close()
        self.assertEquals(folder.list_resources("", recurse=True),["confml/test.confml"])
        self.assertEquals(self.store.list_resources("", recurse=True),["foo/confml/test.confml"])

    def test_open_non_existing_resource(self):
        folder = api.Folder(self.store, "foo")
        try:
            folder.open_resource("confml/test.confml","r")
        except Exception:
            pass
        self.assertEquals(folder.storage.curpath, '')

    def test_create_two_layers_and_open_resource(self):
        foo_folder = api.Folder(self.store, "foo")
        bar_folder = api.Folder(self.store, "bar")
        res = foo_folder.open_resource("confml/test.confml","w")
        res.write("foo.conf")
        res.close()
        res = foo_folder.open_resource("root.confml","w")
        res.close()
        res = bar_folder.open_resource("confml/root.confml","w")
        res.write("foo.conf")
        res.close()
        self.assertEquals(foo_folder.list_resources("", recurse=True),[ 'root.confml', 
                                                                       'confml/test.confml'])
        self.assertEquals(self.store.list_resources("", recurse=True),['bar/confml/root.confml', 
                                                                       'foo/root.confml', 
                                                                       'foo/confml/test.confml'])        
        foo_folder.delete_resource("confml/test.confml")
        self.assertEquals(foo_folder.list_resources("", recurse=True),["root.confml"])
        self.assertEquals(self.store.list_resources("", recurse=True),["bar/confml/root.confml",
                                                                       "foo/root.confml"])


class TestLayer(unittest.TestCase):    
    storage_class = stringstorage.StringStorage
    def setUp(self):
        self.store = self.storage_class.open("temp/layertest.pk","w")

    def test_create_layer(self):
        layer = api.Layer(self.store, "foo")
        self.assertTrue(layer)

#    def test_create_layer_with_kwargs(self):
#        self.store = self.storage_class.open("temp/layertest.pk","w")
#        layer = api.Layer(self.store, "foo",confml_path="foobar", implml_path="")
#        self.assertTrue(layer)
#        self.assertEquals(layer.confml_folder.get_current_path(),"foo/foobar")
#        self.assertEquals(layer.implml_folder.get_current_path(),"foo")
#        layer = api.Layer(self.store, "foo",confml_path="f", implml_path="test", content_path="data", doc_path="foo")
#        self.assertEquals(layer.confml_folder.get_current_path(),"foo/f")
#        self.assertEquals(layer.implml_folder.get_current_path(),"foo/test")
#        self.assertEquals(layer.content_folder.get_current_path(),"foo/data")
#        self.assertEquals(layer.doc_folder.get_current_path(),"foo/foo")
#        layer = api.Layer(self.store, "foo")
#        self.assertEquals(layer.confml_folder.get_current_path(),"foo/confml")
#        self.assertEquals(layer.implml_folder.get_current_path(),"foo/implml")
#        self.assertEquals(layer.content_folder.get_current_path(),"foo/content")
#        self.assertEquals(layer.doc_folder.get_current_path(),"foo/doc")

    def test_get_path(self):
        layer = api.Layer(self.store, "foo")
        self.assertTrue(layer)
        self.assertEquals(layer.get_current_path(),"foo")

    def test_open_resource(self):
        layer = api.Layer(self.store, "foo")
        self.assertTrue(layer)
        res = layer.open_resource("confml/test.confml","w")
        res.write("foo.conf")
        res.close()
        self.assertEquals(layer.list_resources("", recurse=True),["confml/test.confml"])
        self.assertEquals(self.store.list_resources("", recurse=True),["foo/confml/test.confml"])

    def test_create_two_layers_and_open_resource(self):
        foo_layer = api.Layer(self.store, "foo")
        bar_layer = api.Layer(self.store, "bar")
        res = foo_layer.open_resource("confml/test.confml","w")
        res.write("foo.conf")
        res.close()
        res = foo_layer.open_resource("root.confml","w")
        res.close()
        res = bar_layer.open_resource("confml/root.confml","w")
        res.write("foo.conf")
        res.close()
        self.assertEquals(foo_layer.list_resources("", recurse=True),['root.confml', 'confml/test.confml'])
        self.assertEquals(self.store.list_resources("", recurse=True),['bar/confml/root.confml', 'foo/root.confml', 'foo/confml/test.confml'])        
        foo_layer.delete_resource("confml/test.confml")
        self.assertEquals(foo_layer.list_resources("", recurse=True),["root.confml"])
        self.assertEquals(self.store.list_resources("", recurse=True),["bar/confml/root.confml","foo/root.confml"])

    def test_list_confml(self):
        layer = api.Layer(self.store, "foo")
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
        layer = api.Layer(self.store, "foo")
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
        layer = api.Layer(self.store, "foo")
        res = layer.open_resource("content/bar/test.txt","w")
        res.write("foo.conf")
        res.close()
        res = layer.open_resource("content/foo.confml","w")
        res.write("foo.conf")
        res.close()
        res = layer.open_resource("root.confml","w")
        res.write("foo.conf")
        res.close()
        self.assertEquals(layer.list_content(),[ 'content/foo.confml', 'content/bar/test.txt'])

    def test_list_doc(self):
        layer = api.Layer(self.store, "foo")
        res = layer.open_resource("doc/bar/test.txt","w")
        res.write("foo.conf")
        res.close()
        res = layer.open_resource("doc/foo.confml","w")
        res.write("foo.conf")
        res.close()
        res = layer.open_resource("root.confml","w")
        res.write("foo.conf")
        res.close()
        self.assertEquals(layer.list_doc(),['doc/foo.confml', 'doc/bar/test.txt' ])

    def test_list_layer_resources(self):
        layer = api.Layer(self.store, "foo")
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
        layer = api.Layer(self.store, "foo", layers=[api.Layer(self.store, "bar")])
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

    def test_list_all_related(self):
        layer = api.Layer(self.store, "foo")
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
        
        self.assertEquals(layer.list_all_related(),['content/data/abc.txt', 'doc/bar/test.txt'])

    def test_list_all_related_with_filter(self):
        store = self.storage_class.open("temp/layertest.pk","w")
        layer = api.Layer(self.store, "foo")
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
        
        self.assertEquals(layer.list_all_related(exclude_filters={'content':'.*\.txt'}), ['doc/bar/test.txt'])
        self.assertEquals(layer.list_all_related(exclude_filters={'doc':'.*\.txt'}), ['content/data/abc.txt'])




class TestCompositeLayer(unittest.TestCase):    
    storage_class = stringstorage.StringStorage
    def setUp(self):
        self.store = self.storage_class.open("temp/layertest.pk","w")

    def test_create_compositelayer(self):
        clayer = api.CompositeLayer(self.store)
        self.assertTrue(clayer)

    def test_create_with_layer(self):
        clayer = api.CompositeLayer("sub",layers=[api.Layer(self.store,"test"), api.Layer(self.store,"foo/bar")])
        self.assertEquals(clayer.list_layers(),['test', 'foo/bar'])

    def test_create_with_layer_and_add(self):
        self.store = self.storage_class.open("temp/layertestcomposite.pk","w")
        clayer = api.CompositeLayer(self.store, layers=[api.Layer(self.store,"test"), api.Layer(self.store,"foo/bar")])
        self.assertEquals(clayer.list_layers(),['test', 'foo/bar'])
        clayer.add_layer(api.Layer(self.store,"res"))
        self.assertEquals(clayer.list_layers(),['test', 'foo/bar', 'res'])

    def test_get_layer(self):
        clayer = api.CompositeLayer(self.store, layers=[api.Layer(self.store,"test"), api.Layer(self.store,"foo/bar")])
        self.assertEquals(clayer.list_layers(),['test', 'foo/bar'])
        layer = clayer.get_layer('foo/bar')
        self.assertEquals(layer.get_current_path(),'foo/bar')

    def test_create_layers_with_resources_and_list_with_composite(self):
        foolayer = api.Layer(self.store, "foo")
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
        barlayer = api.Layer(self.store, "bar")
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
      
