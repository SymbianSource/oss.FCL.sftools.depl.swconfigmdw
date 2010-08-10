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
Test sets
"""
import unittest

from cone.public import api,exceptions


class TestProperty(unittest.TestCase):
    def test_create_property(self):
        property = api.Property(name='test',value='foo', unit='kB')
        self.assertEquals(property.name, 'test')
        self.assertEquals(property.value, 'foo')
        self.assertEquals(property.unit, 'kB')
        property.name = 'testnew'
        property.value = 'foo faa'
        property.unit = "MB"
        self.assertEquals(property.name, 'testnew')
        self.assertEquals(property.value, 'foo faa')
        self.assertEquals(property.unit, 'MB')

    def test_add_property_to_feature(self):
        fea = api.Feature("testfea")
        prop1 = api.Property(name='test',value='foo', unit='kB')
        fea.add_property(prop1)
        self.assertEquals(fea.list_properties(),['test'])
        self.assertEquals(fea.get_property('test'),prop1)

    def test_add_and_remove_property_to_feature(self):
        fea = api.Feature("testfea")
        prop1 = api.Property(name='test',value='foo', unit='kB')
        fea.add_property(prop1)
        self.assertEquals(fea.list_properties(),['test'])
        fea.remove_property('test')
        self.assertEquals(fea.list_properties(),[])

    def test_add_property_invalid_param(self):
        fea = api.Feature('test')
        self.assertRaises(TypeError, fea.add_property, object())
        
    def test_property_compare(self):
        elem1 = api.Property(name='test1',value='foo', unit='kB')
        elem2 = api.Property(name='test2',value='bar', unit='MB')
        elem3 = api.Property(name='test3',value='foobar', unit='B')
        self.assertFalse(elem1==elem2)
        self.assertFalse(elem1==elem3)

    def test_get_property_nonexistent(self):
        fea = api.Feature('test')
        self.assertRaises(exceptions.NotFound, fea.get_property, 'foo')

    def test_get_property_invalid_type(self):
        fea = api.Feature('test')
        fea.add(api.Feature('property_foo'))
        self.assertRaises(TypeError, fea.get_property, 'foo')

    def test_create_feature_with_properties(self):
        fea = api.Feature('test')
        prop1 = api.Property(name='test1',value='foo', unit='kB')
        prop2 = api.Property(name='test2',value='bar', unit='MB')
        fea.add_property(prop1)
        fea.add(prop2)
        self.assertEquals(fea.list_properties(), ['test1','test2'])
        self.assertEquals(fea.property_test1.get_name(),'test1')
        self.assertEquals(fea.property_test1.get_value(),'foo')
        self.assertEquals(fea.property_test1.get_unit(),'kB')
        self.assertEquals(fea.get_property('test1').get_name(),'test1')
        self.assertEquals(fea.get_property('test1').get_value(),'foo')
        self.assertEquals(fea.get_property('test1').get_unit(),'kB')
        self.assertEquals(fea.property_test2.get_name(),'test2')
        self.assertEquals(fea.property_test2.get_value(),'bar')
        self.assertEquals(fea.property_test2.get_unit(),'MB')
        fea.add_property(prop2)
        self.assertEquals(fea.list_properties(), ['test1','test2'])

    def test_resetting_properties(self):
        fea = api.Feature('test')
        prop1 = api.Property(name='test1',value='foo', unit='kB')
        prop2 = api.Property(name='test1',value='bar', unit='MB')
        fea.add_property(prop1)
        self.assertEquals(fea.list_properties(), ['test1'])
        self.assertEquals(fea.get_property('test1').get_name(),'test1')
        self.assertEquals(fea.get_property('test1').get_value(),'foo')
        self.assertEquals(fea.get_property('test1').get_unit(),'kB')
        fea.add_property(prop2)
        self.assertEquals(fea.get_property('test1').get_name(),'test1')
        self.assertEquals(fea.get_property('test1').get_value(),'bar')
        self.assertEquals(fea.get_property('test1').get_unit(),'MB')
        self.assertEquals(fea.list_properties(), ['test1'])

    def test_adding_and_removing_multiple_properties(self):
        fea = api.Feature('test')
        prop1 = api.Property(name='test1',value='foo', unit='kB')
        prop2 = api.Property(name='test2',value='bar1', unit='MB1')
        prop3 = api.Property(name='test3',value='bar2', unit='MB2')
        
        self.assertEquals(fea.list_properties(), [])
        
        fea.add_property(prop1)
        self.assertEquals(fea.list_properties(), ['test1'])
        
        fea.add_property(prop2)
        self.assertEquals(fea.list_properties(), ['test1', 'test2'])

        fea.add_property(prop3)
        self.assertEquals(fea.list_properties(), ['test1', 'test2', 'test3'])
        self.assertEquals(fea.get_property('test1').get_name(),'test1')
        self.assertEquals(fea.get_property('test1').get_value(),'foo')
        self.assertEquals(fea.get_property('test1').get_unit(),'kB')
        self.assertEquals(fea.get_property('test2').get_name(),'test2')
        self.assertEquals(fea.get_property('test2').get_value(),'bar1')
        self.assertEquals(fea.get_property('test2').get_unit(),'MB1')
        self.assertEquals(fea.get_property('test3').get_name(),'test3')
        self.assertEquals(fea.get_property('test3').get_value(),'bar2')
        self.assertEquals(fea.get_property('test3').get_unit(),'MB2')

        fea.remove_property('test2')
        self.assertEquals(fea.list_properties(), ['test1', 'test3'])

        fea.remove_property('test3')
        self.assertEquals(fea.list_properties(), ['test1'])

        fea.remove_property('test1')
        self.assertEquals(fea.list_properties(), [])

    def test_remove_property_nonexistent(self):
        fea = api.Feature('test')
        self.assertRaises(exceptions.NotFound, fea.remove_property, 'nonexisting')
    
    def test_remove_property_invalid_param(self):
        fea = api.Feature('test')
        fea.add(api.Feature('property_xyz'))
        self.assertRaises(TypeError, fea.remove_property, 'xyz')
        
    def test_create_property_without_name(self):
        try:
            api.Property(name=None, value='foo', unit='kB')
        except ValueError:
            return #ValueError expected
        self.fail("ValueError expected.")
