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
import sys,os,re
import __init__

from cone.public import utils, container, exceptions

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
importpk   = os.path.join(ROOT_PATH,"Import.pk")


class TestC(object):
    def __init__(self, path=""):
        self.path = path
    def test(self):
        return "test string"
class TestB(object):
    def __init__(self, path=""):
        self.path = path
    def test(self):
        return "test string"
    
    
class TestDataContainer(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_add_values_and_get_values(self):
        cont = container.DataContainer()
        cont.add_value('test/ff',123)
        cont.add_value('test/ff','test')
        self.assertEquals(cont.get_value('test/ff'),'test')
        self.assertEquals(cont.get_values('test/ff')[0],123)
        self.assertEquals(cont.get_values('test/ff')[1],'test')
        
    def test_add_values_and_list_values(self):
        cont = container.DataContainer()
        cont.add_value('test/ff',123)
        cont.add_value('test/ff','test')
        cont.add_value('test/foo','test')
        keys = cont.list_keys()
        self.assertEquals(len(keys),2)

    def test_add_values_and_remove_one_value(self):
        cont = container.DataContainer()
        cont.add_value('test/ff',123)
        cont.add_value('test/ff','test')
        cont.add_value('test/foo','test')
        cont.add_value('test/foo','123')
        cont.add_value('sss',123)
        cont.remove_value('test/foo','test')        
        self.assertEquals(cont.get_values('test/foo'),['123'])

    def test_add_values_and_remove_all_values_of_a_key(self):
        cont = container.DataContainer()
        cont.add_value('test/ff',123)
        cont.add_value('test/ff','test')
        cont.add_value('test/foo','test')
        cont.add_value('test/foo','123')
        cont.add_value('test/foo','foobar')
        cont.add_value('sss',123)
        for val in cont.get_values('test/foo'):
            cont.remove_value('test/foo',val)
        self.assertEquals(cont.get_values('test/foo'),[])

    def test_add_values_and_remove_key(self):
        cont = container.DataContainer()
        cont.add_value('test/ff',123)
        cont.add_value('test/ff','test')
        cont.add_value('test/foo','test')
        cont.add_value('test/foo','123')
        cont.add_value('test/foo','foobar')
        cont.add_value('sss',123)
        cont.remove_key('test/foo')
        self.assertEquals(cont.list_keys(),['test/ff','sss'])

    def test_add_values_clear_all_data(self):
        cont = container.DataContainer()
        cont.add_value('test/ff',123)
        cont.add_value('test/ff','test')
        cont.add_value('test/foo','test')
        cont.add_value('test/foo','123')
        cont.clear()
        self.assertEquals(len(cont.list_keys()),0)
        
    def test_conatainer_flatten(self):
        data = container.DataContainer()
        data.add_value('test', 1)
        data.add_value('test', 2)
        data.add_value('test', 3)
        data.add_value('foo', 1)
        data.add_value('foo', 2)
        data.add_value('bar', 3)
        self.assertEquals(data.flatten(),{'test': 3, 'foo' : 2,'bar': 3})



class TestObjectProxy(unittest.TestCase):    
    def test_create_object_proxy_for_test(self):
        cont = container.ObjectProxy(TestC("foo"))
        self.assertTrue(cont)
        self.assertEquals(cont.test(),"test string")

    def test_create_none_proxy(self):
        cont = container.ObjectProxy("")
        self.assertTrue(cont)
        try: 
            cont.test()
            self.fail("calling None succeeds?")
        except AttributeError:
            pass

    def test_create_object_proxy_for_string(self):
        cont = container.ObjectProxy("test string")
        self.assertTrue(cont)
        self.assertEquals(cont.startswith("test"),True)
        

def graph(obj):
    if obj._parent:
        return ["%s -> %s" % (obj._parent._name, obj._name)]
    return []

class TestObjectContainer(unittest.TestCase):    
    def test_create_object_container(self):
        cont = container.ObjectContainer("test")
        self.assertTrue(cont)

    def test_add_incorrect_type(self):
        cont = container.ObjectContainer()
        try: 
            cont._add(container.ObjectProxy())
            self.fail("Adding incorrect class type to container succeeds?")
        except exceptions.IncorrectClassError,e:
            pass
            

    def test_add_child(self):
        cont = container.ObjectContainer("root")
        obj = container.ObjectContainer("test")
        cont._add(obj)
        cont._add(container.ObjectContainer("foo"))
        self.assertEquals(cont._list(),['test','foo'])
        self.assertEquals(cont.test,obj)

    def test_add_internal_child(self):
        cont = container.ObjectContainer("root")
        obj = container.ObjectContainer("?test")
        cont._add(obj)
        cont._add(container.ObjectContainer("foo"))
        self.assertEquals(cont._list(),['foo'])
        self.assertEquals(cont._get('?test'),obj)
        

    def test_add_child_to_path(self):
        cont = container.ObjectContainer("test")
        obj = container.ObjectContainer("test")
        cont._add_to_path("com.nokia", obj)
        self.assertEquals(cont._list(),['com'])
        self.assertEquals(cont.com.nokia._list(),['test'])
        self.assertEquals(cont.com.nokia.test,obj)

    def test_add_child_to_path_and_replace_parent(self):
        cont = container.ObjectContainer("test")
        obj = container.ObjectContainer("test")
        cont._add_to_path("com.nokia", obj)
        cont._add_to_path("com", container.ObjectContainer("bar"))
        com = container.ObjectContainer("com")
        cont._add(com)
        self.assertEquals(cont._list(),['com'])
        self.assertEquals(cont.com._list(),['nokia','bar'])
        self.assertEquals(cont.com.bar._parent,com)
        self.assertEquals(cont.com.nokia._list(),['test'])
        self.assertEquals(cont.com.nokia.test,obj)

    def test_append(self):
        cont = container.ObjectContainer("test")
        cont._append(container.ObjectContainer('test'))
        self.assertEquals(len(utils.get_list(cont.test)), 1)
        cont._append(container.ObjectContainer('test'))
        self.assertEquals(len(cont.test), 2)

    def test_prepend(self):
        cont = container.ObjectContainer("test")
        cont._prepend(container.ObjectContainer('test'))
        self.assertEquals(len(utils.get_list(cont.test)), 1)
        cont._prepend(container.ObjectContainer('test'))
        self.assertEquals(len(cont.test), 2)

    def test_replace(self):
        cont = container.ObjectContainer("test")
        t1 = container.ObjectContainer('test')
        cont._replace(t1)
        self.assertEquals(cont.test, t1)
        t2 = container.ObjectContainer('test')
        cont._replace(t2)
        self.assertEquals(cont.test, t2)

    def test_error(self):
        cont = container.ObjectContainer("test")
        t1 = container.ObjectContainer('test')
        cont._error(t1)
        self.assertEquals(cont.test, t1)
        t2 = container.ObjectContainer('test')
        try:
            cont._error(t2)
            self.fail("adding same with error succeeds")
        except exceptions.AlreadyExists, e:
            pass

    def test_add_child_to_existing_path_with_error(self):
        cont = container.ObjectContainer("test")
        obj = container.ObjectContainer("test")
        cont._add_to_path("com.nokia", obj)
        com = container.ObjectContainer("com")
        try:
            cont._add(com, policy=container.ERROR)
            self.fail("Adding an existing object succeeds with ERROR policy")
        except exceptions.AlreadyExists, e:
            pass

    def test_add_child_to_existing_path_append(self):
        cont = container.ObjectContainer("test")
        obj = container.ObjectContainer("test")
        cont._add_to_path("com.nokia", obj)
        cont._add_to_path("com.nokia", container.ObjectContainer("test"), container.APPEND)
        com = container.ObjectContainer("com")
        cont._add(com, policy=container.APPEND)
        self.assertEquals(len(cont._get('com')),2)
        self.assertEquals(cont._get('com')[1],com)
        self.assertEquals(len(cont._objects()),2)
        self.assertEquals(len(cont.com[0].nokia.test),2)
        self.assertEquals(len(cont._get('com[0].nokia.test')),2)
        self.assertEquals([e._name for e in cont._traverse()],['com', 'nokia', 'test', 'test', 'com'])
        
    def test_add_child_to_existing_path_append_and_objects(self):
        cont = container.ObjectContainer("test")
        cont._add(container.ObjectContainer("dummy"),container.APPEND)
        cont._add(container.ObjectContainer("child"),container.APPEND)
        cont._add(container.ObjectContainer("child"),container.APPEND)
        cont._add(container.ObjectContainer("child"),container.APPEND)
        self.assertEquals(len(cont._objects()),4)
        cont._remove('child[1]')
        self.assertEquals(len(cont._objects()),3)
        cont._remove('child[0]')
        cont._remove('child[0]')
        self.assertEquals(len(cont._objects()),1)

    def test_add_child_and_access_via_index(self):
        cont = container.ObjectContainer("test")
        cont._add(container.ObjectContainer("dummy"),container.APPEND)
        d1 = cont._get('dummy')
        d2 = cont._get('dummy[0]')
        self.assertEquals(d1,d2)
        try:
            cont._get('dummy[1]')
            self.fail("getting dummy")
        except exceptions.NotFound:
            pass

    def test_add_child_to_existing_path_append_and_remove(self):
        cont = container.ObjectContainer("test")
        obj = container.ObjectContainer("test")
        cont._add_to_path("com.nokia", obj)
        com = container.ObjectContainer("com")
        cont._add(com, policy=container.APPEND)
        self.assertEquals(len(cont._get('com')),2)
        self.assertEquals(cont._get('com')[1],com)
        self.assertEquals(cont._list(),['com'])
        cont._remove('com')
        self.assertEquals(cont._list(), [])
        
    def test_add_child_to_existing_path_prepend(self):
        cont = container.ObjectContainer("test")
        obj = container.ObjectContainer("test")
        cont._add_to_path("com.nokia", obj)
        com = container.ObjectContainer("com")
        cont._add(com, policy=container.PREPEND)
        self.assertEquals(len(cont._get('com')),2)
        self.assertEquals(cont._get('com')[0],com)

    def test_add_child_and_get(self):
        cont = container.ObjectContainer("test")
        obj = container.ObjectContainer("test")
        cont._add_to_path("com.nokia", obj)
        self.assertEquals(cont._get('com.nokia.test'),obj)
        self.assertEquals(cont.com._get('nokia.test'),obj)
        self.assertEquals(cont.com.nokia._get('test'),obj)

    def test_add_child_and_remove_one(self):
        cont = container.ObjectContainer("test")
        obj = container.ObjectContainer("test")
        cont._add_to_path("com.nokia", obj)
        cont._add_to_path("com.nokia", container.ObjectContainer("foo"))
        cont._add_to_path("com", container.ObjectContainer("bar"))
        self.assertEquals(len(cont._traverse()),5)
        cont._remove("com.nokia.foo")
        self.assertEquals(len(cont._traverse()),4)
        
    def test_add_child_and_remove_all(self):
        cont = container.ObjectContainer("test")
        obj = container.ObjectContainer("test")
        cont._add_to_path("com.nokia", obj)
        cont._add_to_path("com.nokia", container.ObjectContainer("foo"))
        cont._add_to_path("com", container.ObjectContainer("bar"))
        self.assertEquals(len(cont._traverse()),5)
        for item in cont._list():
            cont._remove(item)
        self.assertEquals(len(cont._list()),0)

    def test_add_children_and_list_all(self):
        cont = container.ObjectContainer("test")
        obj = TestC()
        cont._add_to_path("com.nokia", container.ObjectContainer("test"))
        cont._add_to_path("com.nokia", container.ObjectContainer("foo"))
        cont._add_to_path("com", container.ObjectContainer("bar"))
        self.assertEquals(len(cont._traverse()),5)

    def test_create_hieararchy_and_remove_child(self):
        root = container.ObjectContainer("test")
        root._add(container.ObjectContainer("child1"))
        root._add(container.ObjectContainer("child2"))
        root.child1._add(container.ObjectContainer("child11"))
        root.child1._add(container.ObjectContainer("child12"))
        root.child2._add(container.ObjectContainer("child21"))
        self.assertEquals(root._list_traverse(),
                          ['child1', 
                          'child1.child11', 
                          'child1.child12',
                          'child2',
                          'child2.child21'])
        root.child2._remove('child21')
        self.assertEquals(root._list_traverse()
                          ,['child1',  
                                           'child1.child11', 
                                           'child1.child12',
                                           'child2'])

    def test_add_children_and_traverse_and_get_path(self):
        cont = container.ObjectContainer("default")
        cont._add_to_path("com.nokia", container.ObjectContainer("test"))
        cont._add_to_path("com.nokia", container.ObjectContainer("foo"))
        cont._add_to_path("com", container.ObjectContainer("bar"))
        cont.com._list()
        self.assertEquals(cont._traverse()[0]._path(),"default.com")
        self.assertEquals(cont._traverse()[0]._path(cont),"com")
        self.assertEquals(cont._traverse()[0]._path(cont.com),"")

    def test_add_children_and_traverse_filter_name_and_get_path(self):
        cont = container.ObjectContainer("default")
        cont._add_to_path("com.nokia", container.ObjectContainer("test"))
        cont._add_to_path("com.nokia", container.ObjectContainer("foo"))
        cont._add_to_path("com", container.ObjectContainer("bar"))
        cont.com._list()
        ret = cont._traverse(name="^t.*$")
        self.assertEquals(len(ret),1)
        self.assertEquals(ret[0]._path(),"default.com.nokia.test")

    def test_add_children_and_traverse_filter_name_many(self):
        cont = container.ObjectContainer("default")
        cont._add_to_path("com.nokia", container.ObjectContainer("test"))
        cont._add_to_path("com.nokia", container.ObjectContainer("foo"))
        cont._add_to_path("com", container.ObjectContainer("bar"))
        cont.com._list()
        ret = cont._traverse(path=".*nokia.*")
        self.assertEquals(len(ret),3)
        self.assertEquals(ret[0]._path(),"default.com.nokia")

    def test_add_children_tail_recurse_with_function(self):
        cont = container.ObjectContainer("default")
        cont._add_to_path("com.nokia", container.ObjectContainer("test"))
        cont._add_to_path("com.nokia", container.ObjectContainer("foo"))
        cont._add_to_path("com", container.ObjectContainer("bar"))
        ret = cont._tail_recurse(graph)
        self.assertEquals(ret,['default -> com', 'com -> nokia', 'nokia -> test', 'nokia -> foo', 'com -> bar'])

    def test_add_children_head_recurse_with_function(self):
        cont = container.ObjectContainer("default")
        cont._add_to_path("com.nokia", container.ObjectContainer("test"))
        cont._add_to_path("com.nokia", container.ObjectContainer("foo"))
        cont._add_to_path("com", container.ObjectContainer("bar"))
        ret = cont._head_recurse(graph)
        self.assertEquals(ret,['nokia -> test', 'nokia -> foo', 'com -> nokia', 'com -> bar', 'default -> com'])

    def test_add_children_and_find_parent(self):
        cont = container.ObjectContainer("default", container=True)
        cont._add(container.ObjectContainer("com",housut="test"))
        cont._add_to_path("com.nokia", container.ObjectContainer("test"))
        cont._add_to_path("com.nokia", container.ObjectContainer("foo"))
        cont._add_to_path("com", container.ObjectContainer("bar"))
        child = cont._get('com.nokia.test')
        self.assertEquals(child._find_parent()._name, 'nokia')
        self.assertEquals(child._find_parent(container=True)._name, 'default')
        self.assertEquals(child._find_parent(housut="test")._name, 'com')
        self.assertEquals(child._find_parent(__class__=container.ObjectContainer)._name, 'nokia')
        self.assertEquals(child._find_parent(type=container.ObjectContainer)._name, 'nokia')

class TestObjectProxyContainer(unittest.TestCase):    
    def test_create_object_container_for_test(self):
        cont = container.ObjectProxyContainer(TestC("foo"))
        self.assertTrue(cont)
        self.assertEquals(cont.test(),"test string")

    def test_create_none_container(self):
        cont = container.ObjectProxyContainer(None)
        self.assertTrue(cont)
        try: 
            cont.test()
            self.fail("calling None succeeds?")
        except AttributeError:
            pass

    def test_create_object_container_for_string(self):
        cont = container.ObjectProxyContainer("Test")
        self.assertTrue(cont)
        self.assertEquals(cont.startswith("Test"),True)
        
    def test_create_object_container(self):
        cont = container.ObjectProxyContainer(TestC())
        self.assertTrue(cont)

    def test_add_child(self):
        cont = container.ObjectProxyContainer(None)
        obj = TestC()
        cont._add(container.ObjectProxyContainer(obj,"test"))
        self.assertEquals(cont._list(),['test'])
        self.assertEquals(cont.test._obj,obj)
    
    def test_add_child_to_path(self):
        cont = container.ObjectProxyContainer(None)
        obj = TestC()
        cont._add_to_path("com.nokia", container.ObjectProxyContainer(obj,"test"))
        self.assertEquals(cont._list(),['com'])
        self.assertEquals(cont.com.nokia._list(),['test'])
        self.assertEquals(cont.com.nokia.test._obj,obj)
        self.assertEquals(cont.com.nokia.test.test(),"test string")

    def test_add_child_and_get(self):
        cont = container.ObjectProxyContainer(None)
        obj = TestC()
        cont._add_to_path("com.nokia", container.ObjectProxyContainer(obj,"test"))
        self.assertEquals(cont._get('com.nokia.test')._obj,obj)
        self.assertEquals(cont.com._get('nokia.test')._obj,obj)
        self.assertEquals(cont.com.nokia._get('test')._obj,obj)

    def test_add_child_and_remove_one(self):
        cont = container.ObjectProxyContainer(None)
        obj = TestC()
        cont._add_to_path("com.nokia", container.ObjectProxyContainer(obj,"test"))
        cont._add_to_path("com.nokia", container.ObjectProxyContainer(TestC(),"foo"))
        cont._add_to_path("com", container.ObjectProxyContainer(TestC(),"bar"))
        
        self.assertEquals(len(cont._traverse()),5)
        cont._remove("com.nokia.foo")
        self.assertEquals(len(cont._traverse()),4)
        
    def test_add_child_and_remove_all(self):
        cont = container.ObjectProxyContainer(None)
        obj = TestC()
        cont._add_to_path("com.nokia", container.ObjectProxyContainer(obj,"test"))
        cont._add_to_path("com.nokia", container.ObjectProxyContainer(TestC(),"foo"))
        cont._add_to_path("com", container.ObjectProxyContainer(TestC(),"bar"))
        self.assertEquals(len(cont._traverse()),5)
        for item in cont._list():
            cont._remove(item)
        self.assertEquals(len(cont._list()),0)

    def test_add_children_and_list_all(self):
        cont = container.ObjectProxyContainer(None)
        obj = TestC()
        cont._add_to_path("com.nokia", container.ObjectProxyContainer(obj,"test"))
        cont._add_to_path("com.nokia", container.ObjectProxyContainer(TestC(),"foo"))
        cont._add_to_path("com", container.ObjectProxyContainer(TestC(),"bar"))
        self.assertEquals(len(cont._traverse()),5)

    def test_add_children_and_traverse_and_get_path(self):
        cont = container.ObjectProxyContainer(None,"default")
        cont._add_to_path("com.nokia", container.ObjectProxyContainer(TestC(),"test"))
        cont._add_to_path("com.nokia", container.ObjectProxyContainer(TestC(),"foo"))
        cont._add_to_path("com", container.ObjectProxyContainer(TestC(),"bar"))
        cont.com._list()
        self.assertEquals(cont._traverse()[0]._path(),"default.com")

    def test_add_children_and_traverse_filter_name_and_get_path(self):
        cont = container.ObjectProxyContainer(None,"default")
        cont._add_to_path("com.nokia", container.ObjectProxyContainer(TestC(),"test"))
        cont._add_to_path("com.nokia", container.ObjectProxyContainer(TestC(),"foo"))
        cont._add_to_path("com", container.ObjectProxyContainer(TestC(),"bar"))
        cont.com._list()
        ret = cont._traverse(name="^t.*$")
        self.assertEquals(len(ret),1)
        self.assertEquals(ret[0]._path(),"default.com.nokia.test")

    def test_add_children_and_traverse_filter_name_many(self):
        cont = container.ObjectProxyContainer(None,"default")
        cont._add_to_path("com.nokia", container.ObjectProxyContainer(TestC(),"test"))
        cont._add_to_path("com.nokia", container.ObjectProxyContainer(TestC(),"foo"))
        cont._add_to_path("com", container.ObjectProxyContainer(TestC(),"bar"))
        cont.com._list()
        ret = cont._traverse(path=".*nokia.*")
        self.assertEquals(len(ret),3)
        self.assertEquals(ret[0]._path(),"default.com.nokia")

    def test_add_children_and_traverse_filter_class(self):
        cont = container.ObjectProxyContainer(None,"default")
        cont._add_to_path("com.nokia", container.ObjectProxyContainer(TestC(),"test"))
        cont._add_to_path("com.nokia", container.ObjectProxyContainer(TestC(),"foo"))
        cont._add_to_path("com", container.ObjectProxyContainer(TestC(),"bar"))
        cont._add_to_path("com.nokia", container.ObjectProxyContainer(TestB(),"bee"))
        cont.com.nokia._add(container.ObjectProxyContainer(TestB(),"vee"))
        ret = cont._traverse(filters=[lambda x: hasattr(x,'_obj') and isinstance(x._obj, TestB)])
        self.assertEquals(len(ret),2)
        self.assertEquals(ret[0]._path(cont),"com.nokia.bee")
        self.assertEquals(ret[1]._path(cont),"com.nokia.vee")

    def test_add_children_and_traverse_filter_class_proxies(self):
        cont = container.ObjectProxyContainer(None,"default")
        cont._add_to_path("com.nokia", container.ObjectProxyContainer(TestC(),"test"))
        cont._add_to_path("com.nokia", container.ObjectProxyContainer(TestC(),"foo"))
        cont._add_to_path("com", container.ObjectProxyContainer(TestC(),"bar"))
        cont._add_to_path("com.nokia", container.ObjectProxyContainer(TestB(),"bee"))
        cont.com.nokia._add(container.ObjectProxyContainer(TestB(),"vee"))
        ret = cont._traverse(filters=[lambda x: isinstance(x, container.ObjectProxyContainer)])
        self.assertEquals(len(ret),5)
        self.assertEquals(ret[0]._path(cont),"com.nokia.test")
        self.assertEquals(ret[1]._path(cont),"com.nokia.foo")

class TestLoadProxy(unittest.TestCase):
    def test_create_load_proxy(self):
        proxy = container.LoadProxy(importpk, container.LoadInterface())
        proxy._load()
        self.assertTrue(proxy._obj != None)

    def test_create_load_proxy_and_get(self):
        proxy = container.LoadProxy(importpk, container.LoadInterface())
        self.assertEquals(proxy.list_resources(''),['test1.txt', 'test2.txt', 'test3.txt'])
        self.assertTrue(proxy._obj != None)

    def test_create_load_proxy_and_unload(self):
        proxy = container.LoadProxy(importpk, container.LoadInterface())
        self.assertEquals(proxy.list_resources(''),['test1.txt', 'test2.txt', 'test3.txt'])
        proxy.set('path',"unload.pk")
        proxy._unload()
        self.assertTrue(proxy._obj == None)
        proxy =None
        proxy2 = container.LoadProxy("unload.pk", container.LoadInterface())
        self.assertEquals(proxy2.list_resources(''),['test1.txt', 'test2.txt', 'test3.txt'])
        os.unlink("unload.pk")

if __name__ == '__main__':
    unittest.main()
      
