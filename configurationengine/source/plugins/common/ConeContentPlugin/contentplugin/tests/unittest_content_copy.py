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

import unittest, os
import pkg_resources 

from cone.public.exceptions import NotSupportedException
from contentplugin import contentml

class TestCreateContentPlugin(unittest.TestCase):    
    def test_create_content_impl(self):
        imp = contentml.ContentImpl('test.content',None)
        pass

class TestContentImplementation(unittest.TestCase):    
    def setUp(self):
        self.imp = contentml.ContentImpl('test.content',None)
        pass

    def test_content_filter(self):
        files = ['aaa.txt', 'bbb.txt']
        filesfunc = lambda x: x.lower() in [file.lower() for file in files]
        self.assertEquals(filesfunc('aaa'), False)
        self.assertEquals(filesfunc('AAA'), False)
        self.assertEquals(filesfunc('AAA.txt'), True)
        self.assertEquals(filesfunc('aaa.txt'), True)

if __name__ == '__main__':
    unittest.main()
