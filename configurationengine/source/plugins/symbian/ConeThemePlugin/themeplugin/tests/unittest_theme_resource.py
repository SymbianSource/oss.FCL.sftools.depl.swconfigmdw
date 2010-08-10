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

from themeplugin import theme_resource

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class TestThemePlugin(unittest.TestCase):    
    def setUp(self):
        self.curdir = os.getcwd()
        self.output = 'output'
        pass

    def tearDown(self):
        pass
    
    def test_modify_resource_path(self):
        resource = theme_resource.ThemeResource()
        path = resource.modify_resource_path("!:\\private\\10207114\\import\\f99553e36ea1a92f\\themepackage.mbm")
        self.assertEquals(path,"private\\10207114\\import\\f99553e36ea1a92f")

    def test_parse_pkg_file(self):
        resource = theme_resource.ThemeResource()
        resource.parse_pkg_file(os.path.join(ROOT_PATH,"e75\\test_pkg\\themepackage2.pkg"))
        if len(resource.list_resource) > 0:
            filename = resource.list_resource[0].get_filename()
            self.assertEquals(filename,"themepackage.mbm")
            path = resource.list_resource[0].get_path()
            self.assertEquals(path,"private\\10207114\\import\\f99553e36ea1a92f")
        else:
            self.assertFalse()

# Only run these tests on Windows
if sys.platform != 'win32':
    del TestThemePlugin
        
if __name__ == '__main__':
    unittest.main()
