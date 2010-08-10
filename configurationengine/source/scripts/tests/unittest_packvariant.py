# *-* coding: utf-8 *-*
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
## 
# @author Teemu Rytkonen

import os, unittest

from testautomation import unzip_file
from testautomation.base_testcase import BaseTestCase
from scripttest_common import get_cmd


ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
rootconf = 'testprod_custvariant_root.confml'

TESTDATA_DIR = os.path.join(ROOT_PATH, 'testdata/packvariant')
TEMP_DIR = os.path.join(ROOT_PATH, 'temp/packvariant')

class TestPackvariant(BaseTestCase):
    def test_get_help(self):
        cmd = '%s -h' % get_cmd('packvariant')
        out = self.run_command(cmd)
        lines = out.split(os.linesep)
        self.assertTrue('Options:' in lines)
        self.assertTrue('  Packvariant options:' in lines)

    def test_packvariant(self):
        PROJECT_DIR = os.path.join(ROOT_PATH, TESTDATA_DIR, 'project')
        REMOTE_ZIP = os.path.join(ROOT_PATH, TEMP_DIR, 'output/packvariant.zip')
        EXPECTED_ZIP = os.path.join(ROOT_PATH, TESTDATA_DIR, 'expected/packvariant.zip')

        self.remove_if_exists(REMOTE_ZIP)
        cmd = '%s -p "%s" -c "%s" -r "%s"' % (get_cmd('packvariant'),PROJECT_DIR,rootconf,REMOTE_ZIP)
        out = self.run_command(cmd)
        self.assert_exists_and_contains_something(REMOTE_ZIP)
        
        REMOTE_TEMP_DIR = os.path.join(TEMP_DIR, 'output/remote')
        EXPECTED_TEMP_DIR = os.path.join(TEMP_DIR, 'output/expected')

        self.remove_if_exists(REMOTE_TEMP_DIR)    
        self.remove_if_exists(EXPECTED_TEMP_DIR)    

        unzip_file.unzip_file(
            REMOTE_ZIP,
            REMOTE_TEMP_DIR)
        unzip_file.unzip_file(
            EXPECTED_ZIP,
            EXPECTED_TEMP_DIR)
        
        self.assert_dir_contents_equal(REMOTE_TEMP_DIR, EXPECTED_TEMP_DIR, ignore=['.svn'])

    def test_packvariant_project_does_not_exist(self):
        PROJECT_DIR = os.path.join(ROOT_PATH, TESTDATA_DIR, 'project_does_not_exist')
        REMOTE_ZIP = os.path.join(ROOT_PATH, TEMP_DIR, 'output/packvariant.zip')

        self.remove_if_exists(REMOTE_ZIP)
        cmd = '%s -p "%s" -c "%s" -r "%s"' % (get_cmd('packvariant'),PROJECT_DIR,rootconf,REMOTE_ZIP)
        
        self._run_test(
           cmd, 2,
           "Could not create Zip archive: The given data folder for storage does not exist!")


    def test_packvariant_configuration_does_not_exist(self):
        PROJECT_DIR = os.path.join(ROOT_PATH, TESTDATA_DIR, 'project')
        REMOTE_ZIP = os.path.join(ROOT_PATH, TEMP_DIR, 'output', 'packvariant.zip')
        rootconf = 'root_does_not_exist.confml'
        expected_msg = "Could not create Zip archive: Child root_does_not_exist_confml not found from Project"
        
        self.remove_if_exists(REMOTE_ZIP)
        cmd = '%s -p "%s" -c "%s" -r "%s"' % (get_cmd('packvariant'),PROJECT_DIR,rootconf,REMOTE_ZIP)
        out = self.run_command(cmd, None)
        
        self.assertTrue(expected_msg in out,
                "Expected message '%s' not in output ('%s')" % (expected_msg, out))
        

    def test_packvariant_project_is_not_a_folder(self):
        PROJECT_DIR = os.path.join(ROOT_PATH, TESTDATA_DIR, 'packvariant/project/testprod_custvariant_root.confml')
        REMOTE_ZIP = os.path.join(ROOT_PATH, TEMP_DIR, 'output/packvariant.zip')

        self.remove_if_exists(REMOTE_ZIP)
        cmd = '%s -p "%s" -c "%s" -r "%s"' % (get_cmd('packvariant'),PROJECT_DIR,rootconf,REMOTE_ZIP)
        
        self._run_test(
           cmd, 1,
           "ERROR: --Project must be a directory. Terminating the program.")


    def _run_test(self, args, expected_return_code, expected_msg):
        if not isinstance(args, basestring):
            args = ' '.join(args)
        
        cmd = get_cmd('packvariant') + ' ' + args
        out = self.run_command(cmd, expected_return_code = None)
        
        self.assertTrue(expected_msg in out,
                        "Expected message '%s' not in output ('%s')" % (expected_msg, out))

if __name__ == '__main__':
    unittest.main()
