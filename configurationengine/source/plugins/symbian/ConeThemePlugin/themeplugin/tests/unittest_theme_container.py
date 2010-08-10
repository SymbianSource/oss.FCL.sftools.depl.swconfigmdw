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

import unittest, sys, os

from cone.public import api
from themeplugin.theme_container import ThemeContainer

from unittest_theme_plugin import impl_from_resource

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class TestThemePlugin(unittest.TestCase):    
    def setUp(self):
        self.curdir = os.getcwd()
        self.output = 'output'
        pass

    def tearDown(self):
        pass
  
  
    def test_create_themes(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,"e75")))
        config = project.get_configuration("root_variant.confml")
        impl = impl_from_resource("variant/implml/theme.thememl", config);
        list_tpf = impl.list_tpf_files(impl.list_active_theme, impl.list_theme_dir)
        
        container = ThemeContainer(list_tpf,impl.configuration)
        container.create_themes()
        self.assertEquals(len(container.list_theme),2)
        container.removeTempDirs() 

    def test_prepare_active_themes(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,"e75")))
        config = project.get_configuration("root_variant.confml")
        impl = impl_from_resource("variant/implml/theme.thememl", config);
        list_tpf = impl.list_tpf_files(impl.list_active_theme, impl.list_theme_dir)
        container = ThemeContainer(list_tpf,impl.configuration)
        container.create_themes()
        
        def get_theme(lst, tpf_path):
            for theme in lst:
                if theme.tpf_path == tpf_path:
                    return theme
            self.fail("Theme with tpf_path = %r not found!" % tpf_path)
        
        self.assertEquals(len(container.list_theme), 2)
        theme = get_theme(container.list_theme, 'variant/content/UI/Themes/Armi.tpf')
        self.assertEquals(theme.get_setting_uids(),[])
        self.assertEquals(theme.get_uid(), None)
        
        container.prepare_active_themes(impl.list_active_theme)
        theme = get_theme(container.list_theme, 's60/content/UI/Armi2.tpf')
        self.assertEquals(theme.get_setting_uids(), ["KCRUidPersonalisation.KPslnActiveSkinUid"])
        self.assertEquals(theme.get_uid(), "0x101FD60A")

# Only run these tests on Windows
if sys.platform != 'win32':
    del TestThemePlugin
        
if __name__ == '__main__':
    unittest.main()
