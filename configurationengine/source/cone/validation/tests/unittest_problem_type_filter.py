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

import unittest

from cone.public import api
from cone.validation.problem_type_filter import ProblemTypeFilter

class TestProblemTypeFilter(unittest.TestCase):
    def test_empty_matches_everything(self):
        filter = ProblemTypeFilter([], [])
        self.assertTrue(filter.match(''))
        self.assertTrue(filter.match('foo'))
        self.assertTrue(filter.match('foo.bar'))
        self.assertTrue(filter.match('foo.bar.baz'))
    
    def test_single_include(self):
        filter = ProblemTypeFilter(['foo.bar'], [])
        self.assertFalse(filter.match(''))
        self.assertFalse(filter.match('foo'))
        self.assertTrue(filter.match('foo.bar'))
        self.assertTrue(filter.match('foo.bar.baz'))
        self.assertFalse(filter.match('bar'))
    
    def test_single_exclude(self):
        filter = ProblemTypeFilter([], ['foo.bar'])
        self.assertTrue(filter.match(''))
        self.assertTrue(filter.match('foo'))
        self.assertTrue(filter.match('bar'))
        self.assertFalse(filter.match('foo.bar'))
        self.assertFalse(filter.match('foo.bar.baz'))
    
    def test_include_and_exclude(self):
        filter = ProblemTypeFilter(['foo'], ['foo.bar.baz'])
        self.assertFalse(filter.match(''))
        self.assertTrue(filter.match('foo'))
        self.assertFalse(filter.match('bar'))
        self.assertTrue(filter.match('foo.bar'))
        self.assertFalse(filter.match('foo.bar.baz'))
        self.assertFalse(filter.match('foo.bar.baz.x'))
    
    def test_multiple_includes_and_excludes(self):
        filter = ProblemTypeFilter(['foo', 'boo'], ['foo.bar.baz', 'boo.bar.baz'])
        
        self.assertFalse(filter.match(''))
        self.assertFalse(filter.match('bar'))
        
        self.assertTrue(filter.match('foo'))
        self.assertTrue(filter.match('foo.bar'))
        self.assertFalse(filter.match('foo.bar.baz'))
        self.assertFalse(filter.match('foo.bar.baz.x'))
        
        self.assertTrue(filter.match('boo'))
        self.assertTrue(filter.match('boo.bar'))
        self.assertFalse(filter.match('boo.bar.baz'))
        self.assertFalse(filter.match('boo.bar.baz.x'))
    
    def test_wildcard_in_include(self):
        filter = ProblemTypeFilter(['*.bar'], [])
        
        self.assertFalse(filter.match('foo'))
        self.assertFalse(filter.match('boo'))
        self.assertFalse(filter.match('foo.baz.bar'))
        
        self.assertTrue(filter.match('foo.bar'))
        self.assertTrue(filter.match('foo.bar.baz'))
        self.assertTrue(filter.match('boo.bar'))
        self.assertTrue(filter.match('boo.bar.baz'))
        
        
        filter = ProblemTypeFilter(['*.*.baz'], [])
        self.assertTrue(filter.match('foo.bar.baz'))
        self.assertTrue(filter.match('boo.bar.baz'))
        
        self.assertFalse(filter.match('baz'))
        self.assertFalse(filter.match('foo.baz'))
    
    def test_wildcard_in_exclude(self):
        filter = ProblemTypeFilter([], ['*.bar'])
        
        self.assertTrue(filter.match('foo'))
        self.assertTrue(filter.match('boo'))
        self.assertTrue(filter.match('foo.baz.bar'))
        
        self.assertFalse(filter.match('foo.bar'))
        self.assertFalse(filter.match('foo.bar.baz'))
        self.assertFalse(filter.match('boo.bar'))
        self.assertFalse(filter.match('boo.bar.baz'))
        
        
        filter = ProblemTypeFilter([], ['*.*.baz'])
        self.assertFalse(filter.match('foo.bar.baz'))
        self.assertFalse(filter.match('boo.bar.baz'))
        
        self.assertTrue(filter.match('baz'))
        self.assertTrue(filter.match('foo.baz'))
    
    def test_filter_problems(self):
        filter = ProblemTypeFilter(['foo'], ['foo.bar.baz'])
        problems = [api.Problem('', type=''),
                    api.Problem('', type='foo'),
                    api.Problem('', type='bar'),
                    api.Problem('', type='foo.bar'),
                    api.Problem('', type='foo.bar.baz'),
                    api.Problem('', type='foo.bar.baz.x')]
        
        filtered_problems = filter.filter(problems)
        self.assertEquals(filtered_problems,
                          [api.Problem('', type='foo'),
                           api.Problem('', type='foo.bar')])

    def test_filter_strings(self):
        filter = ProblemTypeFilter(['foo'], ['foo.bar.baz'])
        problems = ['',
                   'foo',
                   'bar',
                   'foo.bar',
                   'foo.bar.baz',
                   'foo.bar.baz.x']
        
        filtered_problems = filter.filter(problems, key=lambda item: item)
        self.assertEquals(filtered_problems, ['foo', 'foo.bar'])
