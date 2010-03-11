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
from projectconvertplugin  import convertproject
from cone.public import exceptions,plugin,api
from cone.storage import filestorage
from cone.confml import implml
from testautomation.base_testcase import BaseTestCase

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
temp_dir  = os.path.join(ROOT_PATH, "temp")
testdata  = os.path.join(ROOT_PATH,'project')

class TestConvertProjectPlugin(BaseTestCase):    
        
    def test_example_parse_prj(self):
        output_dir = os.path.join(temp_dir, "new_project2")
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
            
        fs = filestorage.FileStorage(testdata)
        p = api.Project(fs)
        config = p.get_configuration('product.confml')
        impls = plugin.get_impl_set(config, r'file1\.convertprojectml$')
        self.assertEquals(1, len(impls))
        impl = iter(impls).next()
        self.assertTrue(isinstance(impl, convertproject.ConvertProjectImpl))
        
    def test_generate(self):
        output_dir = os.path.join(temp_dir, "new_project")
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        expected_dir = os.path.join(ROOT_PATH, "expected/new_project")
        oldPath = os.path.join(ROOT_PATH,'old_structure/epoc32/rom/config')
         
        fs = filestorage.FileStorage(oldPath)
        p = api.Project(fs)
        config = p.get_configuration('convert.confml')
        impls = plugin.get_impl_set(config,'\.convertprojectml$')
        impls.output = output_dir
        impls.generate()
        
        self.assert_dir_contents_equal(expected_dir, output_dir, ['.svn'])

        
if __name__ == '__main__':
  unittest.main()
