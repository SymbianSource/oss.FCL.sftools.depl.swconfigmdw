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
import os, shutil
import sys
import pkg_resources 
try:
    from cElementTree import ElementTree
except ImportError:
    try:    
        from elementtree import ElementTree
    except ImportError:
        try:
            from xml.etree import cElementTree as ElementTree
        except ImportError:
            from xml.etree import ElementTree

try:
	pkg_resources.require('ConeContentPlugin')
except pkg_resources.DistributionNotFound:
	import __init__
		
from contentplugin import contentmlparser

class TestConfmlRefs(unittest.TestCase):    
    
    def test_is_confml_ref_of_plain_string(self):
        self.assertFalse(contentmlparser.ConfmlRefs.is_confml_ref('foo.bar'))

    def test_is_confml_ref_of_variable_string(self):
        self.assertTrue(contentmlparser.ConfmlRefs.is_confml_ref('${foo.bar}'))

    def test_is_confml_ref_of_variable_string_with_dollar(self):
        self.assertTrue(contentmlparser.ConfmlRefs.is_confml_ref('${features.foo$bar}'))

    def test_get_confml_ref_with_normal_ref(self):
        self.assertEquals(contentmlparser.ConfmlRefs.get_confml_ref('${features.foo.bar}'), 'features.foo.bar')

    def test_get_confml_ref_with_invalid_ref(self):
        self.assertEquals(contentmlparser.ConfmlRefs.get_confml_ref('${features.foo.bar'), None)
    
    def test_get_two_confml_refs(self):
        self.assertTrue(contentmlparser.ConfmlRefs.is_ref_like('ab.cd'))
        self.assertTrue(contentmlparser.ConfmlRefs.is_confml_ref('${features.foo.bar}/${features.foo.bar2}'))
        self.assertEquals(contentmlparser.ConfmlRefs.get_confml_refs('${features.foo.bar}/${features.foo.bar2}'), ['features.foo.bar', 'features.foo.bar2'])
        self.assertEquals(contentmlparser.ConfmlRefs.get_confml_refs('${features.foo.bar}/${features.foo.bar}'), ['features.foo.bar'])


if __name__ == '__main__':
    unittest.main()
