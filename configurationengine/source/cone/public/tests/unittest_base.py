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

from cone.public import api,exceptions,utils, container

class TestBase(unittest.TestCase):    
    # @test 
    def test_create_base(self):
        base = api.Base("foo")
        self.assertTrue(base)

    def test_get_namespace(self):
        base= api.Base("foo")
        self.assertTrue(base)
        self.assertEquals(base.namespace,"")

    def test_properties(self):
        base= api.Base("foo")
        self.assertTrue(base)
        self.assertEquals(base.ref,"foo")
        self.assertEquals(base.fqr,"foo")
        self.assertEquals(base.get_fullref(),"foo")
        self.assertEquals(base.get_fullfqr(),"foo")

    def test_create_hiearchy(self):
        base= api.Base("foo")
        base._add(api.Base("bar"))
        self.assertTrue(base)
        self.assertEquals(base.bar.find_parent(type=api.Base),base)
        self.assertEquals(base.bar.namespace, 'foo')
        self.assertEquals(base.bar.fqr, 'foo.bar')
        self.assertEquals(base.bar.get_fullfqr(), 'foo.bar')

    def test_create_hiearchy_with_container(self):
        cont= api.Base("", container=True)
        base= api.Base("foo")
        base._add(api.Base("bar1"))
        base._add(api.Base("bar2"))
        base.bar2._add(api.Base("bar21"))
        cont._add(base)
        self.assertTrue(base)
        self.assertEquals(cont.foo.bar2.bar21.find_parent(container=True), cont)
        self.assertEquals(cont.foo.bar1.find_parent(type=api.Base),base)
        self.assertEquals(cont.foo.bar1.namespace, 'foo')
        self.assertEquals(cont.foo.bar2.bar21.namespace, 'foo.bar2')
        self.assertEquals(cont.foo.bar2.bar21.fqr, 'foo.bar2.bar21')

    def test_create_hiearchy_with_container_and_hidden_elem(self):
        cont= api.Base("", container=True)
        base= api.Base("foo")
        base._add(api.Base("bar1"))
        base._add(api.Base("_bar2"))
        base._bar2._add(api.Base("bar21"))
        cont._add(base)
        self.assertTrue(base)
        self.assertEquals(cont.foo._bar2.bar21.find_parent(container=True), cont)
        self.assertEquals(cont.foo.bar1.find_parent(type=api.Base),base)
        self.assertEquals(cont.foo._bar2.bar21.get_fullnamespace(), 'foo._bar2')
        self.assertEquals(cont.foo._bar2.bar21.get_fullfqr(), 'foo._bar2.bar21')
        self.assertEquals(cont.foo.bar1.namespace, 'foo')
        self.assertEquals(cont.foo._bar2.bar21.namespace, 'foo')
        self.assertEquals(cont.foo._bar2.bar21.fqr, 'foo.bar21')

    def test_create_hiearchy_with_append(self):
        cont= api.Base("", container=True)
        base= api.Base("foo")
        base._add(api.Base("bar1"),container.APPEND)
        base._add(api.Base("bar1"),container.APPEND)
        base.bar1[0]._add(api.Base("bar21"))
        cont._add(base)
        self.assertTrue(base)
        self.assertEquals(cont.foo.bar1[1].get_fullnamespace(),'foo')
        self.assertEquals(cont.foo.bar1[0].get_fullref(),'bar1[0]')
        self.assertEquals(cont.foo.bar1[1].get_fullref(),'bar1[1]')
        self.assertEquals(cont.foo.bar1[0].get_fullfqr(), 'foo.bar1[0]')
        self.assertEquals(cont.foo.bar1[1].get_fullfqr(), 'foo.bar1[1]')
        self.assertEquals(cont.foo.bar1[0].bar21.get_fullnamespace(), 'foo.bar1[0]')
        self.assertEquals(cont.foo.bar1[0].bar21.get_fullfqr(), 'foo.bar1[0].bar21')

if __name__ == '__main__':
      unittest.main()
      
