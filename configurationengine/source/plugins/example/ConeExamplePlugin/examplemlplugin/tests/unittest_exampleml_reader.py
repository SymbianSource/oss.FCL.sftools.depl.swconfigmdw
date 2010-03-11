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

import sys, os, unittest
import __init__

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

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

from cone.public import exceptions, plugin, api

from examplemlplugin.exampleml_reader import ExamplemlReader
from examplemlplugin.exampleml_model import Output

class TestExamplemlReader(unittest.TestCase):
    
    NAMESPACE = ExamplemlReader.NAMESPACE
    
    def setUp(self):
        self.reader = ExamplemlReader()
    
    def assert_read_output_equals(self, data, expected):
        etree = ElementTree.fromstring(data)
        output = self.reader._read_output_elem(etree)
        self.assertEquals(expected, output)
    
    def test_read_output(self):
        data = """<output file="test1.txt" encoding="UTF-16">Test</output>"""
        self.assert_read_output_equals(data, Output('test1.txt', 'UTF-16', 'Test'))
        
        data = """<output file="test2.txt">Test</output>"""
        self.assert_read_output_equals(data, Output('test2.txt', 'UTF-8', 'Test'))
        
        data = """<output file="test3.txt"/>"""
        self.assert_read_output_equals(data, Output('test3.txt', 'UTF-8', ''))
        
        data = """<output/>"""
        self.assertRaises(exceptions.ParseError, self.reader._read_output_elem, ElementTree.fromstring(data))
    
    def test_read_outputs(self):
        data = """<?xml version="1.0" encoding="UTF-8"?>
                <printml xmlns="%s">
                    <output file="test1.txt" encoding="UTF-16-LE">Test 1</output>
                    <output file="test2.txt">Test 2</output>
                    <output file="test3.txt"/>
                </printml>""" % self.NAMESPACE
        outputs = self.reader._read_outputs(ElementTree.fromstring(data))
        self.assertEquals(outputs,
                          [Output('test1.txt', 'UTF-16-LE', 'Test 1'),
                           Output('test2.txt', 'UTF-8', 'Test 2'),
                           Output('test3.txt', 'UTF-8', '')])
