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
import tempfile

from testautomation.base_testcase import BaseTestCase
from testautomation import zip_dir
from scripttest_common import get_cmd


ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
testproject = os.path.join(ROOT_PATH,'test_project.cpf')
rootconf = 'root3.confml'

class TestGenerate(BaseTestCase):
    def test_get_help(self):
        cmd = '%s -h' % get_cmd('generate')
        out = self.run_command(cmd)
        lines = out.split(os.linesep)
        self.assertTrue('Options:' in lines)
        self.assertTrue('  Generate options:' in lines)

    def test_generate(self):
        self.set_modification_reference_time(testproject)
        OUTPUT_DIR = os.path.join(ROOT_PATH, 'temp/gen1/output')
        self.remove_if_exists(OUTPUT_DIR)
        cmd = '%s -p "%s" -c "%s" -o "%s"' % (get_cmd('generate'),testproject,rootconf,OUTPUT_DIR)
        out = self.run_command(cmd)
        self.assert_exists_and_contains_something(OUTPUT_DIR)
        
        self.assert_not_modified(testproject)
            
    def test_generate_output_file_from_script(self):
        testproject = os.path.join(ROOT_PATH, 'testdata/generate/impl_container/project')
        self.set_modification_reference_time(testproject)
        OUTPUT_DIR = os.path.join(ROOT_PATH, 'temp/output')
        self.remove_if_exists(OUTPUT_DIR)
        LOGFILE = os.path.join(OUTPUT_DIR, 'cone_temp.log')
        cmd = '%s -p "%s" -c "%s" -o "%s" --log-file "%s"' % (get_cmd('generate'),
                                                                          testproject,
                                                                          'base_root.confml',
                                                                          OUTPUT_DIR,
                                                                          LOGFILE)
        out = self.run_command(cmd)

        self.assertEquals(True, os.path.isfile(os.path.join(OUTPUT_DIR, 'output_test.txt')))
        self.assert_not_modified(testproject)

    def test_generate_with_absolute_path(self):
        self.set_modification_reference_time(testproject)
        tempdir = os.path.join(tempfile.gettempdir(), 'cone_output')
        (drive,OUTPUT_DIR) = os.path.splitdrive(os.path.abspath(tempdir))
        LOGFILE = os.path.join(OUTPUT_DIR, 'cone_temp.log')
        self.remove_if_exists(OUTPUT_DIR)
        cmd = '%s -p "%s" -c "%s" -o "%s" --log-file "%s"' % (get_cmd('generate'),
                                                            testproject,
                                                            rootconf,
                                                            OUTPUT_DIR,
                                                            LOGFILE)
        out = self.run_command(cmd)
        self.assert_exists_and_contains_something(OUTPUT_DIR)
        self.assertTrue(os.path.exists(LOGFILE))
        self.assert_not_modified(testproject)

    def test_generate_with_report(self):
        self.set_modification_reference_time(testproject)
        OUTPUT_DIR  = os.path.join(ROOT_PATH, 'temp/gen2/output')
        REPORT_FILE = os.path.join(ROOT_PATH, 'temp/gen2/report.html')
        self.remove_if_exists([OUTPUT_DIR, REPORT_FILE])
        cmd = '%s -p "%s" -c "%s" -o "%s" -r "%s"' % (get_cmd('generate'),testproject,rootconf, OUTPUT_DIR, REPORT_FILE)
        out = self.run_command(cmd)
        self.assert_exists_and_contains_something(OUTPUT_DIR)
        self.assert_exists_and_contains_something(REPORT_FILE)
        
        self.assert_not_modified(testproject)
       
    def test_generate_with_report_using_custom_template(self):
        self._run_test_generate_with_report_using_custom_template(
            output_dir    = 'temp/gen3/output',
            report_file   = 'temp/gen3/report.csv',
            template_path = 'template.csv')
    
    def test_generate_with_report_using_custom_template_in_relative_dir(self):
        self._run_test_generate_with_report_using_custom_template(
            output_dir    = 'temp/gen4/output',
            report_file   = 'temp/gen4/report.csv',
            template_path = 'test_template/template2.csv')
        
    def test_generate_with_report_using_custom_template_in_relative_dir2(self):
        self._run_test_generate_with_report_using_custom_template(
            output_dir    = 'temp/gen5/output',
            report_file   = 'temp/gen5/report.csv',
            template_path = '../tests/test_template/template2.csv')
    
    def test_generate_with_report_using_custom_template_in_absolute_dir(self):
        self._run_test_generate_with_report_using_custom_template(
            output_dir    = 'temp/gen6/output',
            report_file   = 'temp/gen6/report.csv',
            template_path = os.path.join(ROOT_PATH,'test_template/template2.csv'))
    
    def _run_test_generate_with_report_using_custom_template(self,
        output_dir, report_file, template_path, project=testproject):
        
        # Since we are testing also relative paths here, we need
        # to run the test in the same directory as the script
        orig_workdir = os.getcwd()
        os.chdir(ROOT_PATH)
        try:
            self.set_modification_reference_time(project)
            self.remove_if_exists([output_dir, report_file])
            cmd = '%s -p "%s" -c "%s" -o "%s" -r "%s" -t "%s"' % (get_cmd('generate'),project,rootconf, output_dir, report_file, template_path)
            out = self.run_command(cmd)
            self.assert_exists_and_contains_something(output_dir)
            self.assert_exists_and_contains_something(report_file)
            self.assert_not_modified(project)
        finally:
            os.chdir(orig_workdir)
    
    def test_generate_with_report_and_invalid_refs_in_data(self):
        self._run_test_generate_with_report_using_custom_template(
            project       = os.path.join(ROOT_PATH, 'testdata/generate/test_project_invalid_data_refs.zip'),
            output_dir    = 'temp/gen7/output',
            report_file   = 'temp/gen7/report.csv',
            template_path = os.path.join(ROOT_PATH,'test_template/template2.csv'))

    def test_generate_with_errors_in_project(self):
        project = os.path.join(ROOT_PATH, 'testdata/generate/error_test_project')
        
        OUTPUT_DIR  = os.path.join(ROOT_PATH, 'temp/gen_err/output')
        REPORT_FILE = os.path.join(ROOT_PATH, 'temp/gen_err/report.html')
        LOG_FILE = os.path.join(ROOT_PATH, 'temp/gen_err/cone.log')
        self.remove_if_exists([OUTPUT_DIR, REPORT_FILE, LOG_FILE])
        cmd = '%s -p "%s" -c root.confml -o "%s" -r "%s" --log-file "%s"' % (get_cmd('generate'),project, OUTPUT_DIR, REPORT_FILE, LOG_FILE)
        out = self.run_command(cmd)
        
        # Check that output and report are generated even though
        # there are errors in the project
        self.assert_exists_and_contains_something(OUTPUT_DIR)
        self.assert_exists_and_contains_something(REPORT_FILE)
        self.assert_exists_and_contains_something(LOG_FILE)
        
        # Check that the errors are shown in the log correctly
        self.assert_file_contains(LOG_FILE,
            ['''ERROR   : cone.rules Exception in get_refs() of relation ConfigureRelation(ref='layer1/implml/rules_with_errors.implml', lineno=11): Expression is None''',
             '''ERROR   : cone Error executing rule ConfigureRelation(ref='layer1/implml/rules_with_errors.implml', lineno=11): ParseException: Syntax error: " configures ${TempFeature.Int} = 6000"''',
             '''ERROR   : cone Error executing rule ConfigureRelation(ref='layer1/implml/rules_with_errors.implml', lineno=12): ParseException: Syntax error: "True configures "'''])
        
        # Check that the errors are shown in the report correctly
        self.assert_file_contains(REPORT_FILE, data=[],
            regexes=[r'Exception:\s*layer1/implml/rules_with_errors.implml:11',
                     r'Exception:\s*layer1/implml/rules_with_errors.implml:12'])
        
        # Check from the output that the other rules were successfully
        # executed
        self.assert_file_contains(
            os.path.join(OUTPUT_DIR, 'content/rules_with_errors_test.txt'),
            ['TempFeature.String:  testing and more testing',
            'TempFeature.Int:     501',
            'TempFeature.Real:    1.75',
            'TempFeature.Boolean: True'])

class TestGenerateAllImplsOnLastLayer(BaseTestCase):
    def _prepare_workdir(self, workdir):
        workdir = os.path.join(ROOT_PATH, workdir)
        self.recreate_dir(workdir)
        
        # Any needed extra preparation can be done here
        
        return workdir
    
    def test_generate_all_impls_on_last_layer_on_file_storage(self):
        project_dir = os.path.join(ROOT_PATH, "generation_test_project")
        self.assert_exists_and_contains_something(project_dir)
        self._run_test_generate_all_impls_on_last_layer('temp/gen_ll1', project_dir)
    
    def test_generate_all_impls_on_last_layer_on_zip_storage(self):
        project_dir = os.path.join(ROOT_PATH, "generation_test_project")
        self.assert_exists_and_contains_something(project_dir)
        
        project_zip = os.path.join(ROOT_PATH, "temp/generation_test_project.zip")
        self.remove_if_exists(project_zip)
        zip_dir.zip_dir(project_dir, project_zip, [zip_dir.SVN_IGNORE_PATTERN])
        self.assert_exists_and_contains_something(project_zip)
        
        self._run_test_generate_all_impls_on_last_layer('temp/gen_ll2', project_zip)
    
    def test_generate_all_impls_on_last_layer_on_file_storage_with_report(self):
        project_dir = os.path.join(ROOT_PATH, "generation_test_project")
        self.assert_exists_and_contains_something(project_dir)
        
        # Create a temp workdir and go there to run the test
        orig_workdir = os.getcwd()
        workdir = self._prepare_workdir('temp/gen_ll3')
        os.chdir(workdir)
        
        try:
            cmd = '%s -p "%s" --output output --layer -1 --add-setting-file imaker_variantdir.cfg --report report.html' % (get_cmd('generate'), project_dir)
            self.run_command(cmd)
        finally:
            os.chdir(orig_workdir)
        
        ACTUAL_REPORT = os.path.join(ROOT_PATH, 'temp/gen_ll3/report.html')
        EXPECTED_REPORT = os.path.join(ROOT_PATH, "testdata/generate/expected_report.html")
        
        ignores = [
            r'<tr>\s*<td>Report generated</td>\s*<td>.*</td>\s*</tr>',
            r'<tr>\s*<td>Generation duration</td>\s*<td>.*</td>\s*</tr>',
            r'<a href=".*">',
            r'<tr>\s*<td align="left">Project</td>\s*<td align="left">.*</td>\s*</tr>',
            r'<tr>\s*<td align="left">Working directory</td>\s*<td align="left">.*</td>\s*</tr>',
        ]
        
        self.assert_file_contents_equal(ACTUAL_REPORT, EXPECTED_REPORT, ignores)
    
    def _run_test_generate_all_impls_on_last_layer(self, workdir, project):
        # Create a temp workdir and go there to run the test
        orig_workdir = os.getcwd()
        workdir = self._prepare_workdir(workdir)
        os.chdir(workdir)
        
        try:
            cmd = '%s -p "%s" --output output --layer -1 --add-setting-file imaker_variantdir.cfg' % (get_cmd('generate'), project)
            print self.run_command(cmd)
            
            EXPECTED_DIR = os.path.join(ROOT_PATH, "testdata/generate/expected")
            self.assert_dir_contents_equal('output', EXPECTED_DIR, ['.svn'])
            
            # Check that output has also been generated to the overridden output root directory
            #self.assert_exists_and_contains_something('overridden_output/output_rootdir_test.txt')
            #self.assert_exists_and_contains_something('overridden_output/test_subdir/output_rootdir_test.txt')
        finally:
            os.chdir(orig_workdir)

class TestGenerationImplFilteringByTags(BaseTestCase):
    def test_no_tag_filtering(self):
        self._run_tag_filtering_test(
            name     = 'no_filter',
            filter   = '',
            expected = ['none', 't1', 't2', 't3', 't1_t2', 't2_t3', 't1_t3', 't1_t2_t3'])
    
    def test_filter_by_t1(self):
        self._run_tag_filtering_test(
            name     = 't1',
            filter   = '--impl-tag target:t1',
            expected = ['t1', 't1_t2', 't1_t3', 't1_t2_t3'])
    
    def test_filter_by_t2(self):    
        self._run_tag_filtering_test(
            name     = 't2',
            filter   = '--impl-tag target:t2',
            expected = ['t2', 't1_t2', 't2_t3', 't1_t2_t3'])
    
    def test_filter_by_t3(self):
        self._run_tag_filtering_test(
            name     = 't3',
            filter   = '--impl-tag target:t3',
            expected = ['t3', 't1_t3', 't2_t3', 't1_t2_t3'])
    
    def test_filter_by_t1_or_t2(self):
        self._run_tag_filtering_test(
            name     = 't1_or_t2',
            filter   = '--impl-tag target:t1 --impl-tag target:t2',
            expected = ['t1', 't2', 't1_t2', 't2_t3', 't1_t3', 't1_t2_t3'])

    def test_filter_by_t2_or_t3(self):        
        self._run_tag_filtering_test(
            name     = 't2_or_t3',
            filter   = '--impl-tag target:t2 --impl-tag target:t3',
            expected = ['t2', 't3', 't1_t2', 't2_t3', 't1_t3', 't1_t2_t3'])
        
    def test_filter_by_t1_or_t3(self):
        self._run_tag_filtering_test(
            name     = 't1_or_t3',
            filter   = '--impl-tag target:t1 --impl-tag target:t3',
            expected = ['t1', 't3', 't1_t2', 't2_t3', 't1_t3', 't1_t2_t3'])
    
    def test_filter_by_t1_or_t2_or_t3(self):
        self._run_tag_filtering_test(
            name     = 't1_or_t2_or_t3',
            filter   = '--impl-tag target:t1 --impl-tag target:t2 --impl-tag target:t3',
            expected = ['t1', 't2', 't3', 't1_t2', 't2_t3', 't1_t3', 't1_t2_t3'])
    
    def test_filter_by_t1_and_t2(self):
        self._run_tag_filtering_test(
            name     = 't1_and_t2',
            filter   = '--impl-tag target:t1 --impl-tag target:t2 --impl-tag-policy=AND',
            expected = ['t1_t2', 't1_t2_t3'])
    
    def test_filter_by_t2_and_t3(self):
        self._run_tag_filtering_test(
            name     = 't2_and_t3',
            filter   = '--impl-tag target:t2 --impl-tag target:t3 --impl-tag-policy=AND',
            expected = ['t2_t3', 't1_t2_t3'])
    
    def test_filter_by_t1_and_t3(self):
        self._run_tag_filtering_test(
            name     = 't1_and_t3',
            filter   = '--impl-tag target:t1 --impl-tag target:t3 --impl-tag-policy=AND',
            expected = ['t1_t3', 't1_t2_t3'])
    
    def test_filter_by_t1_and_t2_and_t3(self):
        self._run_tag_filtering_test(
            name     = 't1_and_t2_and_t3',
            filter   = '--impl-tag target:t1 --impl-tag target:t2 --impl-tag target:t3 --impl-tag-policy=AND',
            expected = ['t1_t2_t3'])
    
    def _run_tag_filtering_test(self, name, filter, expected):
        PROJECT = os.path.join(ROOT_PATH, 'tag_filtering_test_project')
        
        OUTPUT_ROOT = os.path.join(ROOT_PATH, 'temp/gen_tf/', name)
        OUTPUT      = os.path.join(OUTPUT_ROOT, 'out')
        LOG         = os.path.join(OUTPUT_ROOT, 'cone.log')
        self.remove_if_exists(OUTPUT)
        
        cmd = '%s -p "%s" --output "%s" --log-file="%s" %s' % (get_cmd('generate'), PROJECT, OUTPUT, LOG, filter)
        #print cmd
        self.run_command(cmd)
        
        self.assert_exists_and_contains_something(OUTPUT)
        
        expected_files = sorted([x + '.txt' for x in expected])
        actual_files = sorted(os.listdir(OUTPUT))
        
        self.assertEquals(expected_files, actual_files)

class TestGenerationImplFilteringByLayers(BaseTestCase):
    def test_filter_by_last_layer(self):
        self._run_layer_filtering_test(
            name     = 'll1',
            filter   = '--layer -1',
            expected = ['layer3'])
    
    def test_filter_by_two_last_layers(self):
        self._run_layer_filtering_test(
            name     = 'll2',
            filter   = '--layer -1 --layer 2',
            expected = ['layer2', 'layer3'])
    
    def test_filter_by_regex_1(self):
        self._run_layer_filtering_test(
            name     = 'r1',
            filter   = '--layer-regex layer[13]',
            expected = ['layer1', 'layer3'])
    
    def test_filter_by_regex_2(self):
        self._run_layer_filtering_test(
            name     = 'r2',
            filter   = '--layer-regex [12]/root.confml',
            expected = ['layer1', 'layer2'])
    
    def test_filter_by_regex_3(self):
        self._run_layer_filtering_test(
            name     = 'r3',
            filter   = '--layer-regex layer1 --layer-regex layer3',
            expected = ['layer1', 'layer3'])
    
    def test_filter_by_wildcard(self):
        self._run_layer_filtering_test(
            name     = 'w',
            filter   = '--layer-wildcard *layer*',
            expected = ['layer1', 'layer2', 'layer3'])
    
    def _run_layer_filtering_test(self, name, filter, expected):
        PROJECT = os.path.join(ROOT_PATH, 'testdata/generate/layer_filtering_project')
        
        OUTPUT_ROOT = os.path.join(ROOT_PATH, 'temp/gen_lf/', name)
        OUTPUT      = os.path.join(OUTPUT_ROOT, 'out')
        LOG         = os.path.join(OUTPUT_ROOT, 'cone.log')
        self.remove_if_exists(OUTPUT)
        
        cmd = '%s -p "%s" --output "%s" --log-file="%s" %s' % (get_cmd('generate'), PROJECT, OUTPUT, LOG, filter)
        #print cmd
        self.run_command(cmd)
        
        self.assert_exists_and_contains_something(OUTPUT)
        
        expected_files = sorted([x + '.txt' for x in expected])
        actual_files = sorted(os.listdir(OUTPUT))
        
        # Ignore the rule output txt files
        for f in ('rule_test_v2.txt', 'rule_test_v3.txt'):
            if f in actual_files: del actual_files[actual_files.index(f)]
        self.assertEquals(expected_files, actual_files)
        
        # Check that the correct rules have been executed
        expected_str = ' ' + ' '.join(sorted(expected)) + ' x'
        self.assert_file_content_equals(os.path.join(OUTPUT, 'rule_test_v2.txt'), expected_str)
        self.assert_file_content_equals(os.path.join(OUTPUT, 'rule_test_v3.txt'), expected_str)

class TestGenerateInvalidParameters(BaseTestCase):
    PROJECT = os.path.join(ROOT_PATH, 'testdata/generate/layer_filtering_project')
    
    def _run_test(self, args, expected_msg):
        if not isinstance(args, basestring):
            args = ' '.join(args)
        
        cmd = get_cmd('generate') + ' ' + args
        # Note: The following run_command() should really expect the
        #       return code 2, but for some reason when running from the
        #       standalone test set, the return value is 0 for some cases
        #       (specifically, the ones that don't use parser.error() to
        #       exit the program)
        out = self.run_command(cmd, expected_return_code = None)
        
        self.assertTrue(expected_msg in out,
                        "Expected message '%s' not in output ('%s')" % (expected_msg, out))
    
    def test_invalid_layer_index_1(self):
        self._run_test(
            '-p "%s" --layer -1 --layer foobar' % self.PROJECT,
            "option --layer: invalid integer value: 'foobar'")
    
    def test_invalid_layer_index_2(self):
        self._run_test(
            '-p "%s" --layer -1 --layer 7' % self.PROJECT,
            'Invalid layer index: 7')
    
    def test_no_matching_layer_for_regex(self):
        self._run_test(
            '-p "%s" --layer-regex foo' % self.PROJECT,
            'No layers matched by layer patterns')
    
    def test_no_matching_layer_for_wildcard(self):
        self._run_test(
            '-p "%s" --layer-wildcard foo' % self.PROJECT,
            'No layers matched by layer patterns')

class TestGenerateImplContainer(BaseTestCase):
    def _run_test(self, root, args):
        PROJECT = os.path.join(ROOT_PATH, 'testdata/generate/impl_container/project')
        EXPECTED = os.path.join(ROOT_PATH, 'testdata/generate/impl_container/expected', root)
        
        OUTPUT_ROOT = os.path.join(ROOT_PATH, 'temp/gen_ic/', root)
        OUTPUT      = os.path.join(OUTPUT_ROOT, 'out')
        LOG         = os.path.join(OUTPUT_ROOT, 'cone.log')
        self.remove_if_exists(OUTPUT)
        
        cmd = '%s -p "%s" -c %s --output "%s" --log-file="%s" %s' % (get_cmd('generate'), PROJECT, root, OUTPUT, LOG, args)
        #print cmd
        self.run_command(cmd)
        
        self.assert_dir_contents_equal(EXPECTED, OUTPUT, ['.svn'])
    
    def test_implcontainer_with_triggering_rule_and_templateml(self):
        self._run_test(
            root = 'data_root.confml',
            args = '--layer -1')

class TestGenerateSetTempvarValue(BaseTestCase):
    def test_set_tempvar_value_from_cmdline(self):
        PROJECT = os.path.join(ROOT_PATH, 'generation_test_project')
        
        OUTPUT_ROOT = os.path.join(ROOT_PATH, 'temp/gen_tvs/')
        OUTPUT      = os.path.join(OUTPUT_ROOT, 'out')
        LOG         = os.path.join(OUTPUT_ROOT, 'cone.log')
        self.remove_if_exists(OUTPUT)
        
        cmd = ['%(cone_cmd)s',
               '-p "%(project)s"',
               '-c root.confml',
               '--output "%(output)s"',
               '--log-file="%(log_file)s"',
               '--impl simple_tempvar',
               '--set "TempFeature.String=testing from cmdline"',
               '--set "TempFeature.Int=8090"',
               '--set "TempFeature.Real=-5.75"',]
        cmd = ' '.join(cmd) % {'cone_cmd':  get_cmd('generate'),
                               'project':   PROJECT,
                               'output':    OUTPUT,
                               'log_file':  LOG}
        #print cmd
        self.run_command(cmd)
        
        self.assert_file_contains(
            os.path.join(OUTPUT, 'content', 'simple_tempvars_test.txt'),
            ['TempFeature.String:  testing from cmdline and more testing',
             'TempFeature.Int:     8091',
             'TempFeature.Real:    -5.5'])

class TestGenerateWhatOutput(BaseTestCase):
    PROJECT = os.path.join(ROOT_PATH, 'generation_test_project')
    OUTPUT_ROOT = os.path.join(ROOT_PATH, 'temp/gen_wop')
    OUTPUT      = os.path.join(OUTPUT_ROOT, 'out')
    LOG         = os.path.join(OUTPUT_ROOT, 'cone.log')
    WHAT_FILE   = os.path.join(OUTPUT_ROOT, 'what_output.txt')
    CMP_FILE    = os.path.join(PROJECT, 'what_output.txt')
    
    def test_write_what_out(self):        
        self.remove_if_exists(self.OUTPUT)
        
        cmd = ['%(cone_cmd)s',
               '-p "%(project)s"',
               '-c root.confml',
               '--what="%(what_file)s"',
               '--output "%(output)s"',
               '--log-file="%(log_file)s"',
               '--all-layers',]
        cmd = ' '.join(cmd) % {'cone_cmd':      get_cmd('generate'),
                               'project':       self.PROJECT,
                               'what_file':     self.WHAT_FILE,
                               'output':        self.OUTPUT,
                               'log_file':      self.LOG}
        self.run_command(cmd)
        
        cmp_what_out_fh = open(self.CMP_FILE, 'r')
        cmp_files = []
        try: cmp_files = cmp_what_out_fh.readlines()
        finally: cmp_what_out_fh.close()
            
        self.assert_exists_and_contains_something(self.WHAT_FILE)
        self.assert_file_contains(self.WHAT_FILE, [self._flip(c.strip()) for c in cmp_files])
        
    def _flip(self, path):
        newpath= path.replace('\\', os.sep)
        newpath = newpath.replace('/', os.sep)
        return newpath
        

if __name__ == '__main__':
    unittest.main()
