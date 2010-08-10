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

"""
Test the configuration
"""
import unittest
import os

from testautomation.base_testcase import BaseTestCase
from testautomation import unzip_file
from scripttest_common import get_cmd
from cone.public import api


ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
TESTDATA_DIR = os.path.join(ROOT_PATH, 'testdata/initvariant')
TEMP_DIR = os.path.join(ROOT_PATH, 'temp/initvariant')
TEST_VARIANT_CPF = os.path.join(TESTDATA_DIR, 'variant.cpf')


class TestInitVariant(BaseTestCase):
    
    def _prepare_workdir(self, subdir, expected_zip):
        WORKDIR = os.path.join(TEMP_DIR, subdir)
        PROJECT_DIR = os.path.join(WORKDIR, 'project')
        EXPECTED_DIR = os.path.join(WORKDIR, 'expected')
        
        self.remove_if_exists(WORKDIR)
        
        unzip_file.unzip_file(
            os.path.join(TESTDATA_DIR, 'test_project.zip'),
            PROJECT_DIR)
        unzip_file.unzip_file(
           os.path.join(TESTDATA_DIR, expected_zip),
           EXPECTED_DIR)
        
        return PROJECT_DIR, EXPECTED_DIR
        
    
    def _get_active_configuration(self, project):
        p = api.Project(api.Storage.open(project, 'r'))
        active_root = p.get_storage().get_active_configuration()
        p.close()
        return active_root
    
    def test_initvariant(self):
        PROJECT_DIR, EXPECTED_DIR = self._prepare_workdir('var1', 'expected.zip')
        
        self.assertEquals(self._get_active_configuration(PROJECT_DIR), None)
        
        cmd = '%s -p "%s" -r "%s" --variant-id 123 --variant-name foo --set-active-root' % (get_cmd('initvariant'), PROJECT_DIR, TEST_VARIANT_CPF)
        self.run_command(cmd)
        
        self.assert_dir_contents_equal(PROJECT_DIR, EXPECTED_DIR, ['.svn', '.metadata'])
        self.assertEquals(self._get_active_configuration(PROJECT_DIR),
                          'testprod_custvariant_123_foo_root.confml')
    
    
    def test_initvariant_2(self):
        PROJECT_DIR, EXPECTED_DIR = self._prepare_workdir('var2', 'expected2.zip')
        
        self.assertEquals(self._get_active_configuration(PROJECT_DIR), None)
        
        cmd = '%s -p "%s" -r "%s" -c foovariant.confml --variant-id 321' % (get_cmd('initvariant'), PROJECT_DIR, TEST_VARIANT_CPF)
        self.run_command(cmd)
        
        self.assert_dir_contents_equal(PROJECT_DIR, EXPECTED_DIR, ['.svn', '.metadata'])
        self.assertEquals(self._get_active_configuration(PROJECT_DIR), None)


    def test_initvariant_based_on_configuration(self):
        PROJECT_DIR, EXPECTED_DIR = self._prepare_workdir('var3', 'expected3.zip')
        
        self.assertEquals(self._get_active_configuration(PROJECT_DIR), None)
        
        cmd = '%s -p "%s" -c foovariant.confml --variant-id=123 -b testprod_custvariant_root.confml' % (get_cmd('initvariant'), PROJECT_DIR)

        self.run_command(cmd)
        
        self.assert_dir_contents_equal(PROJECT_DIR, EXPECTED_DIR, ['.svn', '.metadata'])
        self.assertEquals(self._get_active_configuration(PROJECT_DIR), None)


if __name__ == '__main__':
    unittest.main()
