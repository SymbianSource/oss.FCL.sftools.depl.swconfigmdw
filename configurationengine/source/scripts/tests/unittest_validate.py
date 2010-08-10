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
import string
import unittest
import os

from scripttest_common import get_cmd
from testautomation.base_testcase import BaseTestCase

ROOT_PATH    = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR     = os.path.join(ROOT_PATH, 'temp/validate')
TESTDATA_DIR = os.path.join(ROOT_PATH, 'testdata/validate')
TEST_TEMPLATE = os.path.join(TESTDATA_DIR, 'template.txt')

class TestValidate(BaseTestCase):
    
    def test_get_help(self):
        cmd = '%s -h' % get_cmd('validate')
        out = self.run_command(cmd)
        lines = out.split(os.linesep)
        self.assertTrue('Options:' in lines)
        self.assertTrue('  Validate options:' in lines)
    
    def _run_test_validate(self, args, report_file, template=None, report_type=None, assert_file=True):
        REPORT_FILE = os.path.join(TEMP_DIR, report_file)
        self.remove_if_exists(REPORT_FILE)
        
        cmd = '%(cmd)s %(args)s --report "%(report)s"' \
            % {'cmd'        : get_cmd('validate'),
               'args'       : args,
               'report'     : REPORT_FILE}
        if template:
            cmd = cmd + ' --template "%s"' % template
        if report_type:
            cmd = cmd + ' --report-type %s' % report_type
        out = self.run_command(cmd)
        
        EXPECTED_FILE = os.path.join(TESTDATA_DIR, 'expected', report_file)
        if assert_file:
            self.assert_file_contents_equal(EXPECTED_FILE, REPORT_FILE)
        return out

    def test_validate_templates(self):
        PROJECT = os.path.join(TESTDATA_DIR, 'project')
        CONFIG = 'errors_root.confml'
        self._run_test_validate(
            args        = '-p "%s" -c %s' % (PROJECT, CONFIG),
            report_type = 'xml',
            report_file = 'report.xml')
    
    def test_validate_invalid_configuration(self):
        PROJECT = os.path.join(TESTDATA_DIR, 'project')
        CONFIG = 'errors_root.confml'
        self._run_test_validate(
            args        = '-p "%s" -c %s' % (PROJECT, CONFIG),
            report_file = 'invalid_config_report.txt',
            template = TEST_TEMPLATE)
    
    def test_validate_valid_configuration(self):
        PROJECT = os.path.join(TESTDATA_DIR, 'project')
        CONFIG = 'no_errors_root.confml'
        self._run_test_validate(
            args        = '-p "%s" -c %s' % (PROJECT, CONFIG),
            report_file = 'valid_config_report.txt',
            template = TEST_TEMPLATE)
    
    def test_validate_invalid_file(self):
        orig_workdir = os.getcwd()
        os.chdir(ROOT_PATH)
        try:
            FILE = 'testdata/validate/project/assets/invalid/confml/invalid_type.confml'
            self._run_test_validate(
                args        = '--confml-file %s' % FILE,
                report_file = 'invalid_file_report.txt',
                template = TEST_TEMPLATE)
        finally:
            os.chdir(orig_workdir)
    
    def test_dump_schema_files(self):
        OUTPUT_DIR = os.path.join(TEMP_DIR, 'schema_file_dump')
        self.remove_if_exists(OUTPUT_DIR)
        
        cmd = '%(cmd)s --dump-schema-files "%(output)s"' \
            % {'cmd'    : get_cmd('validate'),
               'output' : OUTPUT_DIR}
        self.run_command(cmd)
        
        def check(path):
            path = os.path.normpath(os.path.join(OUTPUT_DIR, path))
            self.assert_exists_and_contains_something(path)
        check('confml/confml.xsd')
        check('confml/confml2.xsd')
        check('implml/implml.xsd')
    
    def _run_filtering_test(self, args, report_file):
        PROJECT = os.path.join(TESTDATA_DIR, 'project')
        CONFIG = 'errors_root.confml'
        return self._run_test_validate(
            args        = '-p "%s" -c %s %s' % (PROJECT, CONFIG, args),
            report_file = report_file,
            template = TEST_TEMPLATE)
    
    def test_validate_only_confml(self):
        out = self._run_filtering_test(
            args        = '--include-filter *.confml',
            report_file = 'report_only_confml.txt')
        self.assertTrue('Performing XML schema validation on ConfML files...' in out)
        self.assertTrue('Validating ConfML model...' in out)
        self.assertFalse('Performing XML schema validation on ImplML files...' in out)
        self.assertFalse('Validating implementations...' in out)
    
    def test_validate_multiple_confml(self):
        out = self._run_test_validate(
            args        = '--confml-file "%s" --confml-file "%s"' % (os.path.join(TESTDATA_DIR, 'project/assets/invalid/confml/broken.confml'),
                                                                 os.path.join(TESTDATA_DIR, 'project/assets/invalid/confml/invalid_element.confml')),
            report_type = 'xml',
            report_file = 'report.xml',
            assert_file = False)
        out = "".join(out)
        self.assertTrue(string.find(out,"broken.confml")!=-1)
        self.assertTrue(string.find(out,"invalid_element.confml")!=-1)
    
    def test_validate_only_implml(self):
        out = self._run_filtering_test(
            args        = '--include-filter *.implml',
            report_file = 'report_only_implml.txt')
        self.assertFalse('Performing XML schema validation on ConfML files...' in out)
        self.assertFalse('Validating ConfML model...' in out)
        self.assertTrue('Performing XML schema validation on ImplML files...' in out)
        self.assertTrue('Validating implementations...' in out)
    
    def test_validate_multiple_implml(self):
        out = self._run_test_validate(
            args        = '--implml-file "%s" --implml-file "%s"' % (os.path.join(TESTDATA_DIR, 'project/assets/invalid/implml/broken.implml'),
                                                                 os.path.join(TESTDATA_DIR, 'project/assets/invalid/implml/invalid_attribute.implml')),
            report_type = 'xml',
            report_file = 'report.xml',
            assert_file = False)
        out = "".join(out)
        self.assertTrue(string.find(out,"broken.implml")!=-1)
        self.assertTrue(string.find(out,"invalid_attribute.implml")!=-1)
    
    def test_validate_only_model(self):
        out = self._run_filtering_test(
            args        = '--include-filter model',
            report_file = 'report_only_model.txt')
        self.assertFalse('Performing XML schema validation on ConfML files...' in out)
        self.assertTrue('Validating ConfML model...' in out)
        self.assertFalse('Performing XML schema validation on ImplML files...' in out)
        self.assertTrue('Validating implementations...' in out)
    
    def test_validate_only_schema(self):
        out = self._run_filtering_test(
            args        = '--include-filter schema',
            report_file = 'report_only_schema.txt')
        self.assertTrue('Performing XML schema validation on ConfML files...' in out)
        self.assertFalse('Validating ConfML model...' in out)
        self.assertTrue('Performing XML schema validation on ImplML files...' in out)
        self.assertFalse('Parsing implementations...' in out)
        self.assertFalse('Validating implementations...' in out)
    
    def test_validate_multiple_filters(self):
        self._run_filtering_test(
            args        = '--include-filter schema --include-filter model.confml '
                          '--exclude-filter schema.confml '
                          '--exclude-filter model.confml.missing_feature_for_data',
            report_file = 'report_multiple_filters.txt')
    
if __name__ == '__main__':
    unittest.main()
