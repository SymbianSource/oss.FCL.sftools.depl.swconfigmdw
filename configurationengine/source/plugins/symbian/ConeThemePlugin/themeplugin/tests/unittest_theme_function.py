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

import unittest, os, shutil

import __init__    
from cone.public import exceptions,plugin,api
from cone.storage import filestorage
from cone.confml import implml
from themeplugin import maketheme
from themeplugin import theme_function
from cone.storage.filestorage import FileStorage

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class TestThemePlugin(unittest.TestCase):    
    def setUp(self):
        self.curdir = os.getcwd()
        self.output = 'output'
        pass

    def tearDown(self):
        pass
        
    def test_convert_hexa_to_decimal(self):
       decimal = theme_function.convert_hexa_to_decimal("a5d5f19d6e6097b8")
       self.assertEquals(decimal,"-1512705635 1851824056")
       
    def test_find_text_in_string(self):
        row_in_pkg_file = "\"themepackage.mbm\" - \"!:\\resource\\skins\\99d49b086e6097b8\\themepackage.mbm\""
        start_text = "!:\\resource\\skins\\"
        end_text = "\\"

        PID_number = theme_function.find_text_in_string(row_in_pkg_file,start_text, end_text)
        self.assertEquals(PID_number,"99d49b086e6097b8")
        
    def test_find_text_in_file(self):
        start_text = "!:\\resource\\skins\\"
        end_text = "\\"
        PID = theme_function.find_text_in_file(os.path.join(ROOT_PATH,"e75\\test_pkg\\themepackage.pkg"),start_text, end_text)
        self.assertEquals(PID,"99d49b086e6097b8")

        
if __name__ == '__main__':
  unittest.main()
