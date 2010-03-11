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

import sys, os, shutil, unittest
import __init__
from testautomation.base_testcase import BaseTestCase

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
TEMP_DIR        = os.path.normpath(os.path.join(ROOT_PATH, 'temp/crml_dc'))

if sys.platform == "win32":
    CONE_SCRIPT = "cone.cmd"
else:
    CONE_SCRIPT = "cone.sh"

def get_cmd(action='compare'):
    """Return the command used to run the ConE sub-action"""
    if 'CONE_PATH' in os.environ:
        CONE_CMD = os.path.join(os.environ['CONE_PATH'], CONE_SCRIPT)
        if not os.path.exists(CONE_CMD):
            raise RuntimeError("'%s' does not exist!" % CONE_CMD)
        return '"%s" %s' % (CONE_CMD, action)
    else:
        SOURCE_ROOT = os.path.normpath(os.path.join(ROOT_PATH, '../../..'))
        assert os.path.split(SOURCE_ROOT)[1] == 'source'
        cmd = 'python "%s" %s' % (os.path.normpath(os.path.join(SOURCE_ROOT, 'scripts/cone_tool.py')), action)
        return cmd

def get_crml_dc_testdata_dir():
    # If running from the working copy
    dir1 = os.path.normpath(os.path.join(ROOT_PATH, '../ConeCRMLPlugin/CRMLPlugin/tests'))
    if os.path.isdir(dir1): return dir1
    
    # If running from standalone
    dir2 = os.path.normpath(os.path.join(ROOT_PATH, 'testdata/compare/crml_dc'))
    if os.path.isdir(dir2): return dir2
    
    raise RuntimeError("CRML DC test data found neither in '%s' nor '%s'!" % (dir1, dir2))


class TestCompareAction(BaseTestCase):
    
    def setUp(self):
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
    
    def _run_crml_dc_test(self, crml_file_name_without_extension, do_filtering=True):
        testdata_dir = get_crml_dc_testdata_dir()
        report_file = 'crml_dc_%s.csv' % crml_file_name_without_extension
        if do_filtering:
            impl_filter = '%s' % crml_file_name_without_extension
        else:
            impl_filter = '.*'
        self._run_comparison_test(
            source_project  = os.path.join(testdata_dir, 'comp_project_1'),
            source_conf     = 'root.confml',
            target_project  = os.path.join(testdata_dir, 'comp_project_2'),
            target_conf     = 'root.confml',
            report_type     = 'crml_dc_csv',
            report_file     = report_file,
            impl_filter     = impl_filter,
            check_against_expected_output = True)
    
    def test_crml_dc_00000001_simple_keys(self):        self._run_crml_dc_test('00000001_simple_keys')
    def test_crml_dc_00000002_bitmask_keys(self):       self._run_crml_dc_test('00000002_bitmask_keys')
    def test_crml_dc_00000003_key_ranges(self):         self._run_crml_dc_test('00000003_key_ranges')
    def test_crml_dc_00000004_key_type_changed(self):   self._run_crml_dc_test('00000004_key_type_changed')
    def test_crml_dc_00000005_repo_attrs_changed(self): self._run_crml_dc_test('00000005_repo_attrs_changed')
    def test_crml_dc_10000001_removed_repo(self):       self._run_crml_dc_test('10000001_removed_repo')
    def test_crml_dc_20000001_added_repo(self):         self._run_crml_dc_test('20000001_added_repo')
    def test_crml_dc_00000006_renamed_repo(self):       self._run_crml_dc_test('00000006_renamed_repo')
    def test_crml_dc_30000000_duplicate_repo(self):     self._run_crml_dc_test('30000000_duplicate_repo')
    def test_crml_dc_all(self):                         self._run_crml_dc_test('all', do_filtering=False)
    
    def test_crml_dc_html_report(self):
        testdata_dir = get_crml_dc_testdata_dir()
        
        # Ignore the portion of the data where the path to the target is shown
        ignore_patterns = [r'<tr>\s*<td>Target:</td>\s*<td>.*[\\,/]comp_project_2;root.confml</td>']
        
        self._run_comparison_test(
            source_project  = os.path.join(testdata_dir, 'comp_project_1'),
            source_conf     = 'root.confml',
            target_project  = os.path.join(testdata_dir, 'comp_project_2'),
            target_conf     = 'root.confml',
            report_type     = 'crml_dc',
            report_file     = 'crml_dc.html',
            check_against_expected_output = True,
            data_ignore_patterns = ignore_patterns)
    
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
        @param data_ignore_patterns: List of regular expression patterns for ignoring some portions
            of the data when checking against expected output. The patterns are used to remove
            data portions before doing the actual comparison.
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
                % (get_cmd(), source_project, source_conf, target_conf, report_type, actual_report)
        else:
            command = '%s -p "%s" -s "%s" -t "%s" --template "%s" --report "%s"' \
                % (get_cmd(), source_project, source_conf, target_conf, template, actual_report)
        
        if impl_filter:
            command += ' --impl-filter "%s"' % impl_filter
        
        self.remove_if_exists(actual_report)
        self.run_command(command)
        
        
        # Check output
        # -------------
        if check_against_expected_output:
            expected_report = os.path.normpath(os.path.join(ROOT_PATH, 'testdata/crml_dc_expected', report_file))
            ignore_patterns = kwargs.get('data_ignore_patterns', [])
            self.assert_file_contents_equal(expected_report, actual_report, ignore_patterns)
        else:
            self.assert_exists_and_contains_something(actual_report)
        
        
if __name__ == '__main__':
      unittest.main()
