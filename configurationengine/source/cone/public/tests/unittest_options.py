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


class TestOption(unittest.TestCase):
    def test_create_option(self):
        elem = api.Option('test','123')
        self.assertTrue(elem)
        self.assertTrue(elem.get_name(),'test')
        self.assertTrue(elem.get_value(),'123')
    
    def test_add_option(self):
        fea = api.Feature('test')
        fea.add_option(api.Option('foo','1'))
        fea.add_option(api.Option('test','2'))
        self.assertEquals(fea.list_options(), ['value_1','value_2'])
    
    def test_add_option_invalid_param(self):
        fea = api.Feature('test')
        self.assertRaises(TypeError, fea.add_option, object())

    def test_option_compare(self):
        elem1 = api.Option('test','1')
        elem2 = api.Option('foo','2')
        elem3 = api.Option('test','3')
        self.assertFalse(elem1==elem2)
        self.assertFalse(elem1==elem3)
        self.assertTrue(elem1=='opt_value_1')
        self.assertTrue(elem2=='opt_value_2')
        self.assertTrue('opt_value_2' == elem2)

    def test_create_feature_with_options(self):
        fea = api.Feature('test')
        fea.create_option('foo','3')
        fea.create_option('test','4')
        self.assertEquals(fea.list_options(), ['value_3','value_4'])
        self.assertEquals(fea.opt_value_3.get_name(),'foo')
        self.assertEquals(fea.opt_value_3.get_value(),'3')
        self.assertEquals(fea.opt_value_4.get_name(),'test')
        self.assertEquals(fea.opt_value_4.get_value(),'4')
    
    def test_list_and_get_options(self):
        fea = api.Feature('test')
        fea.create_option('foo','1')
        fea.create_option('test','2')
        fea.create_option('bar','3')
        
        self.assertEquals(fea.list_options(), ['value_1', 'value_2', 'value_3'])
        
        self.assertEquals(fea.get_option('value_1').get_name(), 'foo')
        self.assertEquals(fea.get_option('value_2').get_name(), 'test')
        self.assertEquals(fea.get_option('value_3').get_name(), 'bar')
    
    def test_get_option_nonexistent(self):
        fea = api.Feature('test')
        self.assertRaises(exceptions.NotFound, fea.get_option, 'foo')
    
    def test_get_option_invalid_type(self):
        fea = api.Feature('test')
        fea.add(api.Feature('opt_foo'))
        self.assertRaises(TypeError, fea.get_option, 'foo')
    
    def test_remove_option(self):
        fea = api.Feature('test')
        fea.create_option('foo','1')
        fea.create_option('test','2')
        fea.create_option('bar','3')
        self.assertEquals(fea.list_options(), ['value_1', 'value_2', 'value_3'])
        
        fea.remove_option('value_2')
        self.assertEquals(fea.list_options(), ['value_1', 'value_3'])
    
    def test_remove_option_nonexistent(self):
        fea = api.Feature('test')
        self.assertRaises(exceptions.NotFound, fea.remove_option, 'xyz')
    
    def test_remove_option_invalid_param(self):
        fea = api.Feature('test')
        fea.add(api.Feature('opt_xyz'))
        self.assertRaises(TypeError, fea.remove_option, 'xyz')
