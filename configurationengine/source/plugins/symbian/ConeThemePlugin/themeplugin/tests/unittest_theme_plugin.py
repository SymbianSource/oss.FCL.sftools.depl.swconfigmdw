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

def impl_from_resource(resource_ref, configuration):
    doc_root = plugin.ReaderBase._read_xml_doc_from_resource(resource_ref, configuration)
    return maketheme.ThemeImplReader.read_impl(resource_ref, configuration, doc_root)

class TestThemePlugin(unittest.TestCase):    
    def setUp(self):
        self.curdir = os.getcwd()
        self.output = 'output'
        pass

    def tearDown(self):
        pass
        
    def test_list_tpf_files(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,"e75")))
        config = project.get_configuration("root_variant.confml")
        impl = impl_from_resource("variant/implml/theme.thememl", config);
        t1 = impl.list_theme_dir
        t2 = impl.list_active_theme
        list_tpf_files = impl.list_tpf_files(impl.list_active_theme,impl.list_theme_dir)
        self.assertEquals(sorted(list_tpf_files),
                          sorted(['variant/content/UI/Themes/Armi.tpf', 's60/content/UI/Armi2.tpf']))
        
    def test_find_tpf_files(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,"e75")))
        config = project.get_configuration("root_variant.confml")
        impl = impl_from_resource("variant/implml/theme.thememl", config) 
        tpf_paths = []
        tpf_paths.append("UI/Themes")
        list_tpf_files = impl.find_tpf_files(tpf_paths)
        # The found TPF should be the one under variant/ not s60/
        self.assertEquals(list_tpf_files, ['variant/content/UI/Themes/Armi.tpf'])
        
        tpf_paths = []
        tpf_paths.append("UI")
        list_tpf_files = impl.find_tpf_files(tpf_paths)
        self.assertEquals(list_tpf_files, ['s60/content/UI/Armi2.tpf'])
        
        tpf_paths = []
        tpf_paths.append("UI")
        tpf_paths.append("UI/Themes")
        list_tpf_files = impl.find_tpf_files(tpf_paths)
        self.assertEquals(sorted(list_tpf_files), sorted(['variant/content/UI/Themes/Armi.tpf', 's60/content/UI/Armi2.tpf']))

         
        
if __name__ == '__main__':
  unittest.main()
