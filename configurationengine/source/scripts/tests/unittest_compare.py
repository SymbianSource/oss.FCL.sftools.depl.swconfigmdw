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
import shutil
import subprocess
import difflib
import __init__
from testautomation.base_testcase import BaseTestCase
from scripttest_common import get_cmd


ROOT_PATH       = os.path.dirname(os.path.abspath(__file__))
TESTDATA_DIR    = os.path.normpath(os.path.join(ROOT_PATH, 'testdata/compare'))
TEMP_DIR        = os.path.normpath(os.path.join(ROOT_PATH, 'temp/compare'))

from cone.public import api

#import conesub_compare
class TestCompareAction(BaseTestCase):
    
    def setUp(self):
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
    
    #def test_parse_target_configuration(self):
    #    act = conesub_compare.CompareAction('','','')
    #    self.assertEquals(act.parse_target_configuration("root.confml"), ('','root.confml'))
    #    self.assertEquals(act.parse_target_configuration("x:\foo.cpf;root.confml"), ('x:\foo.cpf','root.confml'))
    #    self.assertEquals(act.parse_target_configuration("root\project;root.confml"), ('root\project','root.confml'))
    #    self.assertEquals(act.parse_target_configuration("http://testserver:8000/external;foo/bar/root.confml"), ('http://testserver:8000/external','foo/bar/root.confml'))

    def test_default_compare(self):
        # Test comparison using default parameters
        orig_workdir = os.getcwd()
        os.chdir(os.path.join(TEMP_DIR))
        try:
            project = os.path.join(TESTDATA_DIR, "project1.zip")
            source_conf = "root1.confml"
            target_conf = "root2.confml"
            
            report_file = os.path.join(TEMP_DIR, "data_comparison.html")
            self.remove_if_exists(report_file)
            
            command = '%s -p "%s" -s "%s" -t "%s"' \
                % (get_cmd('compare'), project, source_conf, target_conf)
            self.run_command(command)
            self.assert_exists_and_contains_something(report_file)
        finally:
            os.chdir(orig_workdir)

    def test_compare_api_same_root(self):
        self._run_comparison_test(
            source_project  = 'project1.zip',
            source_conf     = 'root1.confml',
            target_project  = None,
            target_conf     = 'root1.confml',
            template        = 'api_template.txt',
            report_file     = 'api_p1r1_vs_p1r1.txt',
            check_against_expected_output = True)
    
    def test_compare_data_same_root(self):
        self._run_comparison_test(
            source_project  = 'project1.zip',
            source_conf     = 'root1.confml',
            target_project  = None,
            target_conf     = 'root1.confml',
            template        = 'data_template.txt',
            report_file     = 'data_p1r1_vs_p1r1.txt',
            check_against_expected_output = True)
    
    def test_compare_api_same_project_different_root(self):
        self._run_comparison_test(
            source_project  = 'project1.zip',
            source_conf     = 'root1.confml',
            target_project  = None,
            target_conf     = 'root4.confml',
            template        = 'api_template.txt',
            report_file     = 'api_p1r1_vs_p1r4.txt',
            check_against_expected_output = True)
    
    def test_compare_data_same_project_different_root(self):
        self._run_comparison_test(
            source_project  = 'project1.zip',
            source_conf     = 'root1.confml',
            target_project  = None,
            target_conf     = 'root4.confml',
            template        = 'data_template.txt',
            report_file     = 'data_p1r1_vs_p1r4.txt',
            check_against_expected_output = True)
    
    def test_compare_api_proj1_vs_proj2(self):
        self._run_comparison_test(
            source_project  = 'project1.zip',
            source_conf     = 'root1.confml',
            target_project  = 'project2.zip',
            target_conf     = 'root1.confml',
            template        = 'api_template.txt',
            report_file     = 'api_p1r1_vs_p2r1.txt',
            check_against_expected_output = True)
    
    def test_compare_data_proj1_vs_proj2(self):
        self._run_comparison_test(
            source_project  = 'project1.zip',
            source_conf     = 'root1.confml',
            target_project  = 'project2.zip',
            target_conf     = 'root1.confml',
            template        = 'data_template.txt',
            report_file     = 'data_p1r1_vs_p2r1.txt',
            check_against_expected_output = True)
    
    def test_comparison_using_type_api(self):
        self._run_comparison_test(
            source_project  = 'project1.zip',
            source_conf     = 'root1.confml',
            target_project  = None,
            target_conf     = 'root4.confml',
            report_type     = 'api',
            report_file     = 'api_p1r1_vs_p1r4.html',
            check_against_expected_output = False)
    
    def test_comparison_using_type_data(self):
        self._run_comparison_test(
            source_project  = 'project1.zip',
            source_conf     = 'root1.confml',
            target_project  = None,
            target_conf     = 'root4.confml',
            report_type     = 'data',
            report_file     = 'data_p1r1_vs_p1r4.html',
            check_against_expected_output = False)

    def _run_comparison_test(self, **kwargs):
        """
        Run comparison test.
        
        @param source_project: The source project, relative to the test data directory or an
            absolute path.
        @param source_conf: The source configuration.
        @param target_project: The target project, relative to the test data directory
            If not given or None, the source project will be used also for this.
        @param target_conf: The target configuration.
        @param template: The template file used for the report, relative to the test data directory.
        @param report_type: The report type. Should not be used with the 'template' parameter.
        @param report_file: The location where the report is written. This will also be used as
            the name of the expected report file against which the actual report is checked.
        @param impl_filter: Implementation filter to use.
        @param check_against_expected_output: If True, the actual report is checked against an
            expected file with the same name. Otherwise it is just checked that the output
            file has been created and it contains something.
        """
        # Get parameters
        # ---------------
        def get_project_absdir(project_dir):
            if os.path.isabs(project_dir):
                return project_dir
            else:
                return os.path.normpath(os.path.join(TESTDATA_DIR, project_dir))
        
        source_conf = kwargs['source_conf']
        target_conf = kwargs['target_conf']
        source_project = get_project_absdir(kwargs['source_project'])
        target_project = kwargs.get('target_project', None)
        
        if target_project != None:
            target_project = get_project_absdir(target_project)
            target_conf = target_project + ';' + target_conf
        
        template = kwargs.get('template', None)
        report_type = kwargs.get('report_type', None)
        if template and report_type:
            raise ValueError("Both 'template' and 'report_type' parameters given")
        elif not template and not report_type:
            raise ValueError("Neither 'template' not 'report_type' parameter given")
        elif template:
            template = os.path.normpath(os.path.join(TESTDATA_DIR, template))
        
        report_file = kwargs['report_file']
        check_against_expected_output = kwargs['check_against_expected_output']
        actual_report = os.path.normpath(os.path.join(TEMP_DIR, report_file))
        
        impl_filter = kwargs.get('impl_filter', None)
        
        
        # Generate output
        # ----------------
        if report_type:
            command = '%s -p "%s" -s "%s" -t "%s" --report-type "%s" --report "%s"' \
                % (get_cmd('compare'), source_project, source_conf, target_conf, report_type, actual_report)
        else:
            command = '%s -p "%s" -s "%s" -t "%s" --template "%s" --report "%s"' \
                % (get_cmd('compare'), source_project, source_conf, target_conf, template, actual_report)
        
        if impl_filter:
            command += ' --impl-filter "%s"' % impl_filter
        
        self.remove_if_exists(actual_report)
        self.run_command(command)
        
        
        # Check output
        # -------------
        if check_against_expected_output:
            expected_report = os.path.normpath(os.path.join(TESTDATA_DIR, 'expected', report_file))
            self.assert_file_contents_equal(expected_report, actual_report)
        else:
            self.assert_exists_and_contains_something(actual_report)
        
        
if __name__ == '__main__':
      unittest.main()
