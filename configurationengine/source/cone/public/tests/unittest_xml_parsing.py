# *-* coding: utf-8 *-*
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

import sys, os
import unittest
import StringIO

from cone.public import utils, exceptions

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class ElementTreeBackendTester(object):
    """
    Base tester class that contains all test cases.
    
    The actual test case classes derive from this and set the
    class attributes BACKEND_ID and LINE_NUMBERS.
    """
    
    DATA = u"""<?xml version="1.0" encoding="UTF-8"?>
            <root xmlns="http://www.test.com/xml/1">
                <!-- Comment -->
                <elem1 attr1="test" attr2="test 2"/>
                <elem2>カタカナ</elem2>
                <elem3>
                    <!-- Comment 2 -->
                    some text
                </elem3>
            </root>""".encode('utf-8')
    
    # ID of the ElementTree back-end to use in the tests
    BACKEND_ID = None
    
    # Whether to check if line numbers in elements are correct or None
    LINE_NUMBERS = False
    
    def setUp(self):
        self.orig_backend_id = utils.etree.get_backend_id()
        utils.etree.set_backend_id(self.BACKEND_ID)
    
    def tearDown(self):
        utils.etree.set_backend_id(self.orig_backend_id)
    
    def assert_lineno_equals(self, actual, expected):
        if self.LINE_NUMBERS:
            self.assertEquals(actual, expected)
        else:
            self.assertEquals(actual, None)
    
    def assert_elem_tag(self, actual, expected):
        if self.LINE_NUMBERS:
            self.assertEquals(actual.tag, expected)
        else:
            self.assertEquals(actual, None)
    
    def test_correct_parser_set(self):
        self.assertEquals(utils.etree.get_backend_id(), self.BACKEND_ID)
    
    def test_fromstring_successful(self):
        root = utils.etree.fromstring(self.DATA)
        self.assertEquals(root.tag, '{http://www.test.com/xml/1}root')
        children = [e for e in root]
        self.assertEquals(len(children), 3)
        self.assertEquals(children[0].tag, '{http://www.test.com/xml/1}elem1')
        self.assertEquals(children[1].tag, '{http://www.test.com/xml/1}elem2')
        self.assertEquals(children[2].tag, '{http://www.test.com/xml/1}elem3')
        self.assertEquals(children[1].text, u'カタカナ')
        
        self.assert_lineno_equals(utils.etree.get_lineno(root), 2)
        self.assert_lineno_equals(utils.etree.get_lineno(children[0]), 4)
        self.assert_lineno_equals(utils.etree.get_lineno(children[1]), 5)
        self.assert_lineno_equals(utils.etree.get_lineno(children[2]), 6)
        self.assert_elem_tag(utils.etree.get_elem_from_lineno(root, 5), '{http://www.test.com/xml/1}elem2')

    def test_tostring_ascii(self):
        root = utils.etree.fromstring(self.DATA)
        output = utils.etree.tostring(root)
    
    def test_tostring_utf_8(self):
        root = utils.etree.fromstring(self.DATA)
        output = utils.etree.tostring(root, 'UTF-8')
    
    def test_tostring_utf_16(self):
        root = utils.etree.fromstring(self.DATA)
        output = utils.etree.tostring(root, 'UTF-16')
    
    def test_fromstring_failed(self):
        data = """<?xml version="1.0" encoding="UTF-8"?>
            <root xmlns="http://www.test.com/xml/1">
                <elem1 attr1="test" attr2="test 2"/>
                <elem2>testing</elem3>
            </root>"""
        try:
            etree = utils.etree.fromstring(data)
            self.fail("XmlParseError not raised!")
        except exceptions.XmlParseError, e:
            self.assertEquals(e.problem_lineno, 4)

# ============================================================================
# Actual test cases
# ============================================================================

# NOTE:
# The test classes MUST inherit the two super-classes in the order
# (ElementTreeBackendTester, unittest.TestCase), or otherwise setUp() and
# tearDown() will not be overridden correctly

class TestElementTreeBackend(ElementTreeBackendTester, unittest.TestCase):
    BACKEND_ID = utils.etree.BACKEND_ELEMENT_TREE
    LINE_NUMBERS = True

class TestCElementTreeBackend(ElementTreeBackendTester, unittest.TestCase):
    BACKEND_ID = utils.etree.BACKEND_C_ELEMENT_TREE
    LINE_NUMBERS = False

class TestLxmlBackend(ElementTreeBackendTester, unittest.TestCase):
    BACKEND_ID = utils.etree.BACKEND_LXML
    LINE_NUMBERS = True


if __name__ == '__main__':
    unittest.main()
