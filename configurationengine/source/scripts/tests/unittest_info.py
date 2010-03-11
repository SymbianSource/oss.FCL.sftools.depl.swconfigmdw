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
import string
import sys
import os
import subprocess
import __init__
from testautomation.base_testcase import BaseTestCase
from scripttest_common import get_cmd

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
testproject = os.path.join(ROOT_PATH,'test_project.cpf')
temp_dir    = os.path.join(ROOT_PATH, 'temp/info')
VALUE_REPORT_PROJECT = os.path.join(ROOT_PATH, 'testdata/info/value_report_project')

class TestInfo(BaseTestCase):
    
    def test_get_help(self):
        cmd = '%s -h' % get_cmd('info')
        out = self.run_command(cmd)
        lines = out.split('\r\n')
        self.assertTrue('Options:' in lines)
        self.assertTrue('  Info options:' in lines)
    

    def test_get_project_info(self):
        self.set_modification_reference_time(testproject)
        cmd = '%s -p "%s"' % (get_cmd('info'), testproject)
        out = self.run_command(cmd)
        
        lines = out.split('\r\n')
        self.assertTrue('Configurations in the project.' in lines)
        self.assertTrue('root1.confml' in lines)
        self.assertTrue('root2.confml' in lines)
        self.assertTrue('root3.confml' in lines)
        self.assertTrue('root4.confml' in lines)
        self.assertTrue('root5.confml' in lines)
        
        self.assert_not_modified(testproject)
    
    def test_api_report(self):
        EXPECTED_FILE = os.path.join(ROOT_PATH, 'testdata/info/expected/api_report.html')
        REPORT_FILE = os.path.join(temp_dir, 'api_report.html')
        self.remove_if_exists(REPORT_FILE)
        cmd = '%s -p "%s" -c root3.confml --report-type api --report "%s"' % (get_cmd('info'), testproject, REPORT_FILE)
        out = self.run_command(cmd)
        
        # Ignore the file links, because their value depends on the current directory
        ignores= [r'<td><a href="file://.*">.*</a></td>']
        self.assert_file_contents_equal(EXPECTED_FILE, REPORT_FILE, ignores)
    
    def test_impl_report(self):
        EXPECTED_FILE = os.path.join(ROOT_PATH, 'testdata/info/expected/impl_report.html')
        REPORT_FILE = os.path.join(temp_dir, 'impl_report.html')
        self.remove_if_exists(REPORT_FILE)
        cmd = '%s -p "%s" -c root3.confml --report-type impl --report "%s"' % (get_cmd('info'), testproject, REPORT_FILE)
        out = self.run_command(cmd)
        
        self.assert_file_contents_equal(EXPECTED_FILE, REPORT_FILE)
    
    def test_impl_report_with_impl_containers(self):
        PROJECT = os.path.join(ROOT_PATH, 'generation_test_project')
        EXPECTED_FILE = os.path.join(ROOT_PATH, 'testdata/info/expected/impl_report_with_containers.html')
        REPORT_FILE = os.path.join(temp_dir, 'impl_report_with_containers.html')
        self.remove_if_exists(REPORT_FILE)
        cmd = '%s -p "%s" -c root.confml --report-type impl --report "%s"' % (get_cmd('info'), PROJECT, REPORT_FILE)
        out = self.run_command(cmd)
        
        self.assert_file_contents_equal(EXPECTED_FILE, REPORT_FILE)
    
    def test_content_report(self):
        EXPECTED_FILE = os.path.join(ROOT_PATH, 'testdata/info/expected/content_report.html')
        REPORT_FILE = os.path.join(temp_dir, 'content_report.html')
        self.remove_if_exists(REPORT_FILE)
        cmd = '%s -p "%s" -c root5.confml --report-type content --report "%s"' % (get_cmd('info'), testproject, REPORT_FILE)
        out = self.run_command(cmd)
        
        self.assert_file_contents_equal(EXPECTED_FILE, REPORT_FILE)
    
    # --------------------------------------------------
    # Tests for invalid configuration argument detection
    # --------------------------------------------------
    
    def _run_test_invalid_configuration_args(self, config_args, expected_msg):
        REPORT_FILE = os.path.join(temp_dir, "dummy_report.html")
        self.remove_if_exists(REPORT_FILE)
        cmd = '%s -p "%s" %s --report "%s"' \
            % (get_cmd('info'), VALUE_REPORT_PROJECT, config_args, REPORT_FILE)
        # Note: The following run_command() should really expect the
        #       return code 2, but for some reason when running from the
        #       standalone test set, the return value is 0
        out = self.run_command(cmd, expected_return_code = None)
        self.assertFalse(os.path.exists(REPORT_FILE))
        
        self.assertTrue(expected_msg in out,
                        "Expected message '%s' not in output ('%s')" % (expected_msg, out))
    
    def test_invalid_single_configuration(self):
        self._run_test_invalid_configuration_args(
            '--configuration nonexistent_root.confml',
            "No such configuration: nonexistent_root.confml")
        
    def test_invalid_multi_configuration(self):
        self._run_test_invalid_configuration_args(
            '--configuration product_root.confml --configuration nonexistent_root.confml',
            "No such configuration: nonexistent_root.confml")
    
    def test_invalid_wildcard_configuration(self):
        self._run_test_invalid_configuration_args(
            '--config-wildcard nonexistent*.confml',
            "No matching configurations for wildcard(s) and/or pattern(s).")
    
    def test_invalid_regex_configuration(self):
        self._run_test_invalid_configuration_args(
            '--config-regex nonexistent.*\\.confml',
            "No matching configurations for wildcard(s) and/or pattern(s).")
    
    def test_invalid_view_file(self):
        self._run_test_invalid_configuration_args(
            '-c product_root.confml --view-file nonexistent.confml',
            "No such file: nonexistent.confml")
    
    
    # ----------------------
    # Tests for value report
    # ----------------------
    
    def _run_test_value_report(self, output, expected, args, rep_type='value'):
        EXPECTED_FILE = os.path.join(ROOT_PATH, 'testdata/info/expected/%s' % expected)
        REPORT_FILE = os.path.join(temp_dir, output)
        self.remove_if_exists(REPORT_FILE)
        cmd = '%s -p "%s" %s --report-type %s --report "%s"' \
            % (get_cmd('info'), VALUE_REPORT_PROJECT, args, rep_type, REPORT_FILE)
        out = self.run_command(cmd)
        
        self.assert_file_contents_equal(EXPECTED_FILE, REPORT_FILE)
    
    def test_value_report_configs_with_wildcard(self):
        self._run_test_value_report(
            output   = 'value_report_langpacks_wildcard.html',
            expected = 'value_report_langpacks.html',
            args     = '--config-wildcard product_langpack_*_root.confml')
    
    def test_value_report_configs_with_regex(self):
        self._run_test_value_report(
            output   = 'value_report_langpacks_regex.html',
            expected = 'value_report_langpacks.html',
            args     = '--config-regex product_langpack_\\d{2}_root.confml')
    
    def test_value_report_multi_config(self):
        self._run_test_value_report(
            output   = 'value_report_langpacks_regex.html',
            expected = 'value_report_langpacks.html',
            args     = '-c product_langpack_01_root.confml '\
                       '-c product_langpack_02_root.confml '\
                       '-c product_langpack_03_root.confml')
    
    def test_value_report_single_config(self):
        self._run_test_value_report(
            output   = 'value_report_single.html',
            expected = 'value_report_single.html',
            args     = '--configuration product_root.confml')
    
    def test_value_report_multi_config_mixed_args(self):
        self._run_test_value_report(
            output   = 'value_report_multi_mixed.html',
            expected = 'value_report_multi_mixed.html',
            args     = '-c product_root.confml --config-wildcard product_langpack_*_root.confml')
    
    def test_value_report_single_config_with_view(self):
        VIEW_FILE = os.path.join(ROOT_PATH, 'testdata/info/test_view.confml')
        self._run_test_value_report(
            output   = 'value_report_single_with_view.html',
            expected = 'value_report_single_with_view.html',
            args     = '--configuration product_root.confml --view-file "%s"' % VIEW_FILE)
    
    def test_value_report_single_config_with_included_view(self):
        VIEW_FILE = os.path.join(ROOT_PATH, 'testdata/info/include_test_view.confml')
        self._run_test_value_report(
            output   = 'value_report_single_with_included_view.html',
            expected = 'value_report_single_with_view.html',
            args     = '--configuration product_root.confml --view-file "%s"' % VIEW_FILE)
    
    def test_value_report_csv(self):
        self._run_test_value_report(
            output   = 'value_report.csv',
            expected = 'value_report.csv',
            args     = '--config-wildcard product_langpack_*_root.confml',
            rep_type = 'value_csv')
    
    def test_value_report_csv_with_special_chars(self):
        self._run_test_value_report(
            output   = 'value_report_special_chars.csv',
            expected = 'value_report_special_chars.csv',
            args     = '--configuration csv_test_root.confml',
            rep_type = 'value_csv')
    
    def test_value_report_custom_template(self):
        TEMPLATE_FILE = os.path.join(ROOT_PATH, 'testdata/info/custom_value_report_template.html')
        EXPECTED_FILE = os.path.join(ROOT_PATH, 'testdata/info/expected/value_report_custom.html')
        REPORT_FILE = os.path.join(temp_dir, 'value_report_custom.html')
        self.remove_if_exists(REPORT_FILE)
        cmd = '%s -p "%s" --template "%s" --report "%s" -c product_root.confml' \
            % (get_cmd('info'), VALUE_REPORT_PROJECT, TEMPLATE_FILE, REPORT_FILE)
        out = self.run_command(cmd)
        
        self.assert_file_contents_equal(EXPECTED_FILE, REPORT_FILE)

if __name__ == '__main__':
      unittest.main()
