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
import sets
import sys
import os
import __init__

from cone.public import api,exceptions,utils


class TestOption(unittest.TestCase):
    def test_create_option(self):
        elem = api.Option('test','123')
        self.assertTrue(elem)
        self.assertTrue(elem.get_name(),'test')
        self.assertTrue(elem.get_value(),'123')

    def test_option_compare(self):
        elem1 = api.Option('test','1')
        elem2 = api.Option('foo','2')
        elem3 = api.Option('test','3')
        self.assertFalse(elem1==elem2)
        self.assertFalse(elem1==elem3)
        self.assertTrue(elem1=='opt_value_1')
        self.assertTrue(elem2=='opt_value_2')
        self.assertTrue('opt_value_2' == elem2)

class TestSets(unittest.TestCase):    

    def test_create_set(self):
        ss = api.ValueSet([1,3,4])
        self.assertTrue(1 in ss)
        self.assertFalse(2 in ss)
        self.assertTrue(3 in ss)
        self.assertTrue(4 in ss)
        self.assertFalse(5 in ss)

    def test_create_set_with_range(self):
        r = range(0,100000)
        ss = api.ValueSet(r)
        for i in r:
            self.assertTrue(i in ss)
        self.assertFalse(12345678 in ss)
        self.assertFalse(-1 in ss)
        self.assertFalse('test' in ss)

    def test_set_union(self):
        ss1 = api.ValueSet([1,3,4])
        ss2 = api.ValueSet([2,5,6])
        ss3 = ss1.union(ss2)
        self.assertFalse(0 in ss3)
        self.assertTrue(1 in ss3)
        self.assertTrue(2 in ss3)
        self.assertTrue(3 in ss3)
        self.assertTrue(4 in ss3)
        self.assertTrue(5 in ss3)
        self.assertTrue(6 in ss3)
    
    def test_set_intersection(self):
        ss1 = api.ValueSet([1,2,3,4])
        ss2 = api.ValueSet([2,5,6])
        ss3 = ss1.intersection(ss2)
        self.assertFalse(0 in ss3)
        self.assertFalse(1 in ss3)
        self.assertTrue(2 in ss3)
        self.assertFalse(3 in ss3)
        self.assertFalse(4 in ss3)
        self.assertFalse(5 in ss3)
        self.assertFalse(6 in ss3)


class TestRange(unittest.TestCase):    
    def test_create_integer_range(self):
        r= api.ValueRange(1,100)
        self.assertTrue(1 in r)
        self.assertTrue(2 in r)
        self.assertTrue(3 in r)
        self.assertTrue(4 in r)
        self.assertFalse(0 in r)
        self.assertFalse(101 in r)

class TestRegexp(unittest.TestCase):    
    def test_create_regexp(self):
        r= api.ValueRe('.*')
        self.assertTrue('test' in r)
        self.assertTrue('foo.foo' in r)
        self.assertTrue('haahiis' in r)
        self.assertTrue('1235' in r)

    def test_create_regexp_allows_only_letters(self):
        r= api.ValueRe('^[A-Za-z]*$')
        self.assertTrue('test' in r)
        self.assertFalse('foo.foo' in r)
        self.assertTrue('haahiis' in r)
        self.assertFalse('1235' in r)
        self.assertTrue('Haaa' in r)

    def test_create_regexp_allows_windows_drive(self):
        r= api.ValueRe('^[A-Za-z]:$')
        self.assertTrue('C:' in r)
        self.assertFalse('foo.foo' in r)
        self.assertTrue('h:' in r)
        self.assertFalse('1235' in r)
        self.assertFalse('Haaa' in r)

    def test_create_regexp_allows_windows_path(self):
        r= api.ValueRe('^[:\\\\A-Za-z1-9_\.]*$')
        #self.assertTrue('C:' in r)
        self.assertTrue('foo.foo' in r)
        self.assertTrue('X:\\aaa\\bbb\ccc' in r)
        