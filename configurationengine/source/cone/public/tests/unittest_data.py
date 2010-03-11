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

class TestData(unittest.TestCase):    
    # @test 
    def test_create_data(self):
        data = api.Data(fqr="foo", value=123)
        self.assertTrue(data)
        data = api.Data(fqr="foo.bar", value=123, attr='rfs')
        self.assertEquals(data.attr,'rfs')
        data = api.Data(fqr="foo.bar", value=123, attr=None)
        self.assertEquals(data.attr,'data')
        data = api.Data(fqr="foo.bar", value=123, attr='data')
        self.assertEquals(data.attr,'data')

    def test_create_data_with_map(self):
        data = api.Data(ref="StringToString", map="StringToStringSequenceFeature/SequenceSetting[@key='Key 1']")
        self.assertEqual(data.get_map(),"StringToStringSequenceFeature/SequenceSetting[@key='Key 1']")
        self.assertEqual(data.get_map_ref(),"StringToStringSequenceFeature/SequenceSetting")
        self.assertEqual(data.get_map_key_value(),"Key 1")
        self.assertTrue(data)

    def test_create_data_getters(self):
        data = api.Data(ref="foo", value=123)
        self.assertEquals(data.fqr, "foo")
        data = api.Data(fqr="foo.bar.test", value=123)
        self.assertEquals(data.get_ref(), "test")
        self.assertEquals(data.get_value(), 123)
        self.assertEquals(data.get_policy(), "")

    def test_create_data_for_sequences(self):
        data = api.Data(ref="seq")
        data._add(api.Data(ref="foo", value='sss'),container.APPEND)
        data._add(api.Data(ref="foo", value='aaa'),container.APPEND)
        data._add(api.Data(ref="foo", value=123),container.PREPEND)
        
        self.assertEquals(data.fqr, "seq")
        self.assertEquals(data._get('foo[0]').get_ref(), "foo")
        self.assertEquals(data._get('foo[0]').fqr, "seq.foo")
        self.assertEquals(data.foo[0].get_value(), 123)
        self.assertEquals(data.foo[0].get_index(), 0)
        self.assertEquals(data.foo[1].get_value(), 'sss')
        self.assertEquals(data.foo[1].get_index(), 1)
        self.assertEquals(data.foo[2].get_value(), 'aaa')
        self.assertEquals(data.foo[2].get_index(), 2)
        data._add(api.Data(ref="foo", value='NEW'))
        self.assertEquals(data.foo.get_value(), 'NEW')
        
    def test_create_configuration_with_data(self):
        config  = api.Configuration("dataconf")
        config.add_data(api.Data(fqr='foo.setting1',value=123))
        config.add_data(api.Data(fqr='foo.setting2',value=456))
        config.add_data(api.Data(fqr='foo.seq.data1',value='juhuu'))
        config.add_data(api.Data(fqr='foo.seq.data2',value='x:\\ss'))
        self.assertEquals(config.data.foo.setting1.get_value(), 123)
        self.assertEquals(config.data.foo.setting1.fqr, 'foo.setting1')
        self.assertEquals(config.data.foo.seq.data2.fqr, 'foo.seq.data2')
        self.assertEquals(config.data.foo.seq.data2.get_ref(), 'data2')
        self.assertEquals(config.get_data('foo.seq.data2').get_value(), 'x:\\ss')

    def comparedata(self,data1,data2):
        self.assertEquals(data1.ref, data1.ref)
        self.assertEquals(data1.fqr, data1.fqr)
        self.assertEquals(data1.value, data1.value)

    def test_clone_data(self):
        data1 = api.Data(ref="dat")
        data2 = data1._clone()
        self.comparedata(data1, data2)

    def test_clone_hierarchical_data(self):
        data1 = api.Data(ref="seq")
        data1._add(api.Data(ref="foo1", value='sss'))
        data1._add(api.Data(ref="foo2", value='aaa'))
        data1._add(api.Data(ref="foo3", value=123))
        
        data2 = data1._clone(recursion=True)
        self.comparedata(data1, data2)
        self.comparedata(data1.foo1, data2.foo1)
        self.comparedata(data1.foo2, data2.foo2)
        self.comparedata(data1.foo3, data2.foo3)

    def test_clone_sequential_data(self):
        data1 = api.Data(ref="seq")
        data1._add(api.Data(ref="foo", value='sss'),container.APPEND)
        data1._add(api.Data(ref="foo", value='aaa'),container.APPEND)
        data1._add(api.Data(ref="foo", value=123),container.APPEND)
        
        data2 = data1._clone(recursion=True)
        self.comparedata(data1, data2)
        self.comparedata(data1.foo[0], data2.foo[0])
        self.comparedata(data1.foo[1], data2.foo[1])
        self.comparedata(data1.foo[2], data2.foo[2])
if __name__ == '__main__':
      unittest.main()
      
