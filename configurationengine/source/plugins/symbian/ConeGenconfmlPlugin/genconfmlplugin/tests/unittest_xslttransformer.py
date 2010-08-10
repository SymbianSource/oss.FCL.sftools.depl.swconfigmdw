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

import unittest, os, sys

from genconfmlplugin import xslttransformer

# Hardcoded value of testdata folder that must be under the current working dir
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
testdata  = os.path.join(ROOT_PATH,'project')
expected = u'<html><body>\r\n<h2>My CD Collection</h2>\r\n<table border="1">\r\n<tr bgcolor="#9acd32">\r\n<th>Title</th>\r\n<th>Artist</th>\r\n</tr>\r\n<tr>\r\n<td>.</td>\r\n<td>.</td>\r\n</tr>\r\n</table>\r\n</body></html>\r\n\r\n'.replace('\r\n', os.linesep)


class TestXstlTransformer(unittest.TestCase):    
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
        result = transformer.transform_lxml(os.path.join(ROOT_PATH,"xslt/cdcatalog.xml"), 
                                 os.path.join(ROOT_PATH,"xslt/cdcatalog_ex1.xsl"), 
                                 sys.getdefaultencoding())
        self.assertEquals(result, expected)

        
if __name__ == '__main__':
    unittest.main()
