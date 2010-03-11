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

import unittest, os, shutil, sys

import __init__	
from genconfmlplugin import xslttransformer
from cone.public import exceptions,plugin,api
from cone.storage import filestorage
from cone.confml import implml

# Hardcoded value of testdata folder that must be under the current working dir
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
testdata  = os.path.join(ROOT_PATH,'project')

class TestGenconfmlPlugin(unittest.TestCase):    
    def setUp(self):
        self.curdir = os.getcwd()
        self.output = 'output'
        pass

    def tearDown(self):
        pass
        
    def test_transform(self):
        '''
        Test that the xslt transformation works
        '''
        transformer = xslttransformer.XsltTransformer()
        transformer.transform_lxml(os.path.join(ROOT_PATH,"xslt\cdcatalog.xml"), 
                                 os.path.join(ROOT_PATH,"xslt\cdcatalog_ex1.xsl"), 
                                 "testioutput.xml",
                                 sys.getdefaultencoding())
        os.unlink("testioutput.xml")

        
if __name__ == '__main__':
  unittest.main()
