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
from testautomation.base_testcase import BaseTestCase
from commandplugin import commandml

# Hardcoded value of testdata folder that must be under the current working dir
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
temp_dir  = os.path.join(ROOT_PATH, "temp")
testdata  = os.path.join(ROOT_PATH,'project')

class TestCommandPlugin(BaseTestCase):    
    def test_example_parse_prj(self):
        fs = filestorage.FileStorage(testdata)
        p = api.Project(fs)
        config = p.get_configuration('product.confml')
        impls = plugin.get_impl_set(config,'\.commandml$')
        
    def test_generate(self):
        orig_workdir = os.getcwd()
        os.chdir(ROOT_PATH)
        try:
            OUTPUT_DIR = os.path.join(ROOT_PATH, 'output')
            self.remove_if_exists(OUTPUT_DIR)
            
            fs = filestorage.FileStorage(testdata)
            p = api.Project(fs)
            config = p.get_configuration('product.confml')
            impls = plugin.get_impl_set(config,'file2\.commandml$')
            impls.output = OUTPUT_DIR
            impls.generate()
            
            self.assert_file_content_equals('hello.log',
                "Hello\r\n" +
                "Cmd line args: ['-c', 'some_config.txt', '-d', 'some_dir', '-x']\r\n" +
                "Env: {'MYVAR': '123'}\r\n")
            
            self.assert_file_content_equals('exec_in_output_test.log',
                os.path.normpath(OUTPUT_DIR) + '\r\n')
            
            # Check that the log file of the command that should not be
            # executed does not exist
            self.assertFalse(os.path.exists("should_not_be_created.log"))
        finally:
            os.chdir(orig_workdir)
        
if __name__ == '__main__':
  unittest.main()
