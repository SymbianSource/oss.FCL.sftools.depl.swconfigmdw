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

import sys, os, shutil, unittest

from testautomation.base_testcase import BaseTestCase
from testautomation import zip_dir
from scripttest_common import get_cmd

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR     = os.path.normpath(os.path.join(ROOT_PATH, 'temp/report'))
TESTDATA_DIR = os.path.normpath(os.path.join(ROOT_PATH, 'testdata/report'))
TEST_PROJECT = os.path.normpath(os.path.join(TESTDATA_DIR, 'project'))


class TestReport(BaseTestCase):

    def _test_get_help(self):
        cmd = '%s -h' % get_cmd('report')
        out = self.run_command(cmd)
        lines = out.split(os.linesep)
        self.assertTrue('Options:' in lines)
        self.assertTrue('  Report options:' in lines)
    
    def test_generate_data_files_and_create_reports(self):
        TEST_DIR = 'test1/'
        
        _, datafile_rofs3 = self.generate(TEST_DIR + 'out-rofs3',   TEST_DIR + 'repdata/rofs3.dat', 'rofs3')
        _, datafile_uda   = self.generate(TEST_DIR + 'out-uda',     TEST_DIR + 'repdata/uda.dat',   'uda')
        
        REPORTS_DIR = os.path.join(TEMP_DIR, TEST_DIR + 'reports')
        self.create_report([datafile_rofs3],                os.path.join(REPORTS_DIR, 'rofs3.txt'))
        self.create_report([datafile_uda],                  os.path.join(REPORTS_DIR, 'uda.txt'))
        self.create_report([datafile_rofs3, datafile_uda],  os.path.join(REPORTS_DIR, 'both.txt'))

        EXPECTED_DIR = os.path.join(TESTDATA_DIR, 'expected')
        self.assert_dir_contents_equal(EXPECTED_DIR, REPORTS_DIR, ['.svn'])
        
        # Create by giving the directory as input and check
        REPORT_FILE = os.path.join(TEMP_DIR, TEST_DIR, 'both_from_dir.txt')
        EXPECTED_FILE = os.path.join(EXPECTED_DIR, 'both.txt')
        self.create_report_from_dir(os.path.join(TEMP_DIR, TEST_DIR, 'repdata'), REPORT_FILE)
        self.assert_file_contents_equal(EXPECTED_FILE, REPORT_FILE)
    
    def generate(self, output_dir, report_data_file, target_tag):
        """
        Generate output into the given output directory and report data file.
        @return: Tuple containing the absolute paths to the output directory
            and report data file.
        """
        OUTPUT_DIR = os.path.join(TEMP_DIR, output_dir)
        REPORT_DATA_FILE = os.path.join(TEMP_DIR, report_data_file)
        self.remove_if_exists(OUTPUT_DIR)
        
        cmd = '%s -p "%s" -o "%s" --log-file="%s" --report-data-output "%s" --impl-tag target:%s' \
            % (get_cmd('generate'), TEST_PROJECT, OUTPUT_DIR, os.path.join(OUTPUT_DIR,'cone.log'), REPORT_DATA_FILE, target_tag)
        self.run_command(cmd)
        self.assert_exists_and_contains_something(OUTPUT_DIR)
        self.assert_exists_and_contains_something(REPORT_DATA_FILE)
        
        return OUTPUT_DIR, REPORT_DATA_FILE
    
    def create_report(self, report_data_files, report_file):
        """
        Create a report based on a number of input data files.
        @return: Absolute path to the created report.
        """
        TEMPLATE_FILE = os.path.join(TESTDATA_DIR, 'template.txt')
        REPORT_FILE = os.path.join(TEMP_DIR, report_file)
        self.remove_if_exists(REPORT_FILE)
        
        cmd = '%s --report "%s" --log-file="%s" --template "%s" ' % (get_cmd('report'),
                                                                     REPORT_FILE,
                                                                     os.path.join(TEMP_DIR,'cone_report.log'),
                                                                     TEMPLATE_FILE)
        cmd += ' '.join(['--input-data "%s"' % f for f in report_data_files])
        self.run_command(cmd)
        self.assert_exists_and_contains_something(REPORT_FILE)
        return REPORT_FILE
    
    def create_report_from_dir(self, report_data_dir, report_file):
        """
        Create a report based on an input data directory.
        @return: Absolute path to the created report.
        """
        TEMPLATE_FILE = os.path.join(TESTDATA_DIR, 'template.txt')
        REPORT_FILE = os.path.join(TEMP_DIR, report_file)
        self.remove_if_exists(REPORT_FILE)
        
        cmd = '%s --report "%s" --log-file="%s" --template "%s" --input-data-dir "%s"' \
            % (get_cmd('report'), REPORT_FILE, 
                                  os.path.join(TEMP_DIR,'cone_report_from_dir.log'),
                                  TEMPLATE_FILE, 
                                  report_data_dir)
        self.run_command(cmd)
        self.assert_exists_and_contains_something(REPORT_FILE)
        return REPORT_FILE


if __name__ == '__main__':
    unittest.main()
