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
import os
import __init__
from cone.public.exceptions import NotSupportedException

from cone.confml import implml
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class TestImplementation(unittest.TestCase):    
    def setUp(self):
        pass
    
    def test_create_implml(self):
        imp = implml.Implml('test.txt',None)

    def test_generate_not_supported(self):
        try:
            imp = implml.Implml('test.txt',None)
            imp.generate()
            self.fail("Implementation base class should not support generation")
        except NotSupportedException:
            pass

#    def test_list_output_files(self):
#        imp = implml.Implml('ref/test.txt',None,ROOT_PATH)
#        files = imp.list_output_files()
#        self.assertTrue(len(files)>0)
        

if __name__ == '__main__':
    unittest.main()
