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
Test Respource
"""
import unittest
import string
import sys,os
import __init__

from cone.public.api import Resource
from cone.storage.stringstorage import StringResource

class TestResource(unittest.TestCase):    
    def setUp(self):
        pass

    def test_create_resource(self):
        res = Resource("","",None)
        self.assertTrue(res)

class TestStringResource(unittest.TestCase):    
    def setUp(self):
        pass

    def test_create_stringresource_with_data(self):
        res = StringResource("","","Test data")
        self.assertTrue(res)
        self.assertEqual(res.read(),"Test data")

    
if __name__ == '__main__':
    unittest.main()
      
