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
import shutil
import zipfile

from testautomation.base_testcase import BaseTestCase
from testautomation import unzip_file
from scripttest_common import get_cmd

try:
    from cElementTree import ElementTree
except ImportError:
    try:    
        from elementtree import ElementTree
    except ImportError:
        try:
            from xml.etree import cElementTree as ElementTree
        except ImportError:
            from xml.etree import ElementTree

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
TESTDATA_DIR = os.path.join(ROOT_PATH, 'testdata/merge')
TEMP_DIR = os.path.join(ROOT_PATH, 'temp/merge')
TEST_PROJECT_CPF = os.path.join(ROOT_PATH, 'test_project.cpf')
TEST_VARIANT_CPF = os.path.join(ROOT_PATH, 'test_variant.cpf')

TEST_VARIANT_CPF_V1 = os.path.join(TESTDATA_DIR, 'test_variant_v1.cpf')
TEST_VARIANT_CPF_V2 = os.path.join(TESTDATA_DIR, 'test_variant_v2.cpf')


class TestMerge(BaseTestCase):
    
    def _prepare_workdir_with_project(self, workdir, expected_zip=None):
        """
        Prepare a working directory for running a test.
        @param workdir: Sub-directory of the workdir.
        @param expected_zip: Zip file containing expected data that should
            be extracted under the workdir, can be None. The path should be
            relative to testdata/merge.
        @return: Tuple (test_project_abs, expected_dir_abs). expected_dir_abs
            will be None if expected_zip was None.
        """
        workdir = os.path.join(TEMP_DIR, workdir)
        self.recreate_dir(workdir)
        
        # Unzip the test project
        test_project_dir = os.path.join(workdir, 'test_project')
        unzip_file.unzip_file(TEST_PROJECT_CPF, test_project_dir, delete_if_exists=True)
        
        # Check that it was unzipped correctly
        paths = [
            "Layer1/", "Layer2/","Layer3/", "Layer4/", "Layer5/",
            "root1.confml", "root2.confml", "root3.confml", "root4.confml", "root5.confml"
        ]
        for path in paths:
            self.assert_exists_and_contains_something(os.path.join(test_project_dir, path))
        
        expected_dir = None
        # Unzip the expected data
        if expected_zip:
            expected_zip = os.path.join(TESTDATA_DIR, expected_zip)
            expected_dir = os.path.join(workdir, 'expected')
            unzip_file.unzip_file(expected_zip, expected_dir)
        
        return test_project_dir, expected_dir
    
    def test_get_help(self):
        cmd = '%s -h' % get_cmd('merge')
        out = self.run_command(cmd)
        lines = out.split(os.linesep)
        self.assertTrue('Options:' in lines)
        self.assertTrue('  Merge options:' in lines)

    def test_merge_cpf_last_layer_to_project(self):
        project_dir, expected_dir = self._prepare_workdir_with_project('last_layer_from_cpf', 'last_layer_expected.zip')
        
        self.set_modification_reference_time(project_dir)
        self.set_modification_reference_time(TEST_VARIANT_CPF)
        cmd = '%s -p "%s" -r "%s" -c root5.confml -l -1 -v 5'  % (get_cmd('merge'), project_dir, TEST_VARIANT_CPF)
        self.run_command(cmd)
        
        self.assert_modified(project_dir)
        self.assert_not_modified(TEST_VARIANT_CPF)
        self.assert_dir_contents_equal(expected_dir, project_dir)
    
    def test_merge_cpf_last_layer_to_project_with_rename(self):
        project_dir, expected_dir = self._prepare_workdir_with_project('last_layer_from_cpf_rename', 'last_layer_rename_expected.zip')
        
        self.set_modification_reference_time(project_dir)
        self.set_modification_reference_time(TEST_VARIANT_CPF)
        cmd = '%s -p "%s" -r "%s" -c root5.confml -l -1 -v 5 --rename'  % (get_cmd('merge'), project_dir, TEST_VARIANT_CPF)
        self.run_command(cmd)
        
        self.assert_modified(project_dir)
        self.assert_not_modified(TEST_VARIANT_CPF)
        self.assert_dir_contents_equal(expected_dir, project_dir)
    
    def test_merge_cpf_multiple_last_layers_to_project(self):
        project_dir, expected_dir = self._prepare_workdir_with_project('multiple_last_layers_from_cpf', 'multiple_last_layers_expected.zip')
        
        self.set_modification_reference_time(project_dir)
        self.set_modification_reference_time(TEST_VARIANT_CPF)
        # Pass the merged layers in random order to check that it doesn't affect
        # the output
        cmd = '%s -p "%s" -r "%s" -c root5.confml -l -3 -l -1 -l -2 -v 5'  % (get_cmd('merge'), project_dir, TEST_VARIANT_CPF)
        self.run_command(cmd)
        
        self.assert_modified(project_dir)
        self.assert_not_modified(TEST_VARIANT_CPF)
        self.assert_dir_contents_equal(expected_dir, project_dir)
        
    def test_merge_cpf_multiple_mixed_layers_to_project(self):
        project_dir, expected_dir = self._prepare_workdir_with_project('mixed_multiple_last_layers_from_cpf', 'multiple_last_layers_expected.zip')
        
        self.set_modification_reference_time(project_dir)
        self.set_modification_reference_time(TEST_VARIANT_CPF)
        cmd = '%s -p "%s" -r "%s" -c root5.confml -l -3 -l -1 -l 4 -l 5 -v 5'  % (get_cmd('merge'), project_dir, TEST_VARIANT_CPF)
        self.run_command(cmd)
        
        self.assert_modified(project_dir)
        self.assert_not_modified(TEST_VARIANT_CPF)
        self.assert_dir_contents_equal(expected_dir, project_dir)
                
    def test_merge_layer_to_cpf(self):
        project_cpf = os.path.join(ROOT_PATH, "temp/merge/layer_to_cpf/project.cpf")
        self.create_dir_for_file_path(project_cpf)
        shutil.copy2(TEST_PROJECT_CPF, project_cpf)
        
        self.set_modification_reference_time(project_cpf)
        self.set_modification_reference_time(TEST_VARIANT_CPF)
        
        cmd = '%s -p "%s" -r "%s" -c root5.confml -l -1 -v 5'  % (get_cmd('merge'), project_cpf, TEST_VARIANT_CPF)
        self.run_command(cmd)
        
        def check(entry):
            zf = zipfile.ZipFile(project_cpf, "r")
            try:     self.assertTrue(entry in zf.namelist(), "Entry '%s' not in zip file '%s'" % (entry, project_cpf))
            finally: zf.close()
        check('variant/root.confml')
        check('variant/confml/data.confml')
        check('variant/content/empty/')
        
        self.assertEquals(
            self.get_xinclude_list(self.read_data_from_zip_file(project_cpf, "root5.confml")),
            ["Layer1/root.confml",
             "Layer2/root.confml",
             "Layer3/root.confml",
             "Layer4/root.confml",
             "Layer5/root.confml",
             "variant/root.confml"])
        
        self.assert_modified(project_cpf)
        self.assert_not_modified(TEST_VARIANT_CPF)
    
    def test_merge_cpf_last_layer_two_versions(self):
        project_dir, expected_dir = self._prepare_workdir_with_project('last_layer_two_versions', 'last_layer_variant_v1_v2_expected.zip')
        cmd = '%s -p "%s" -r "%s" -c root5.confml -l -1'  % (get_cmd('merge'), project_dir, TEST_VARIANT_CPF_V1)
        self.run_command(cmd)
        cmd = '%s -p "%s" -r "%s" -c root5.confml -l -1'  % (get_cmd('merge'), project_dir, TEST_VARIANT_CPF_V2)
        self.run_command(cmd)
        self.assert_dir_contents_equal(expected_dir, project_dir)
    
    def test_merge_cpf_last_layer_two_versions_overwrite_layer(self):
        project_dir, expected_dir = self._prepare_workdir_with_project('last_layer_two_versions_overwrite', 'last_layer_variant_v2_expected.zip')
        cmd = '%s -p "%s" -r "%s" -c root5.confml -l -1 --merge-policy overwrite-layer'  % (get_cmd('merge'), project_dir, TEST_VARIANT_CPF_V1)
        self.run_command(cmd)
        cmd = '%s -p "%s" -r "%s" -c root5.confml -l -1 --merge-policy overwrite-layer'  % (get_cmd('merge'), project_dir, TEST_VARIANT_CPF_V2)
        self.run_command(cmd)
        self.assert_dir_contents_equal(expected_dir, project_dir)
    
    def get_xinclude_list(self, confml_file_data):
        """
        Read the XInlude element list from a ConfML file and assert that.
        @param confml_file_data: The raw binary data of the ConfML file.
        """
        root_elem = ElementTree.fromstring(confml_file_data)
        
        # Make sure that we have a ConfML file
        self.assertTrue(
            root_elem.tag in ("{http://www.s60.com/xml/confml/1}configuration", "{http://www.s60.com/xml/confml/2}configuration"),
            "The root element is not a ConfML configuration element (tag is '%s')" % root_elem.tag)
        
        # Read the xi:include list
        result = []
        for elem in root_elem.findall("{http://www.w3.org/2001/XInclude}include"):
            result.append(elem.get("href"))
        
        return result

# =============================================================================

def run_in_workdir(workdir):
    """
    Decorator for running asset merge tests in a specific working directory.
    """
    workdir_abs = os.path.join(ROOT_PATH, 'temp/merge/assetmerge', workdir)
    
    def decorate(testmethod):
        def run_test(self):
            assert isinstance(self, TestAssetMerge)
            
            # Prepare the working directory
            workdir = self.prepare_workdir(workdir_abs)
            
            # Go into the working directory to run the test
            orig_workdir = os.getcwd()
            os.chdir(workdir)
            try:
                # Run the test
                testmethod(self)
            finally:
                # Revert back to the original working directory
                os.chdir(orig_workdir)
        return run_test
    
    return decorate

class TestAssetMerge(BaseTestCase):
    """
    Tests for merging an asset (basically a single configuration layer) into
    a specific layer in an existing project.
    """
    TESTDATA_ZIP = os.path.join(ROOT_PATH, 'testdata/merge/assetmerge/data.zip')
    EXPECTED_ZIP = os.path.join(ROOT_PATH, 'testdata/merge/assetmerge/expected.zip')
    
    def prepare_workdir(self, workdir):
        """
        Prepare a working directory with all needed test data into
        the given sub-dir under the temporary directory.
        @param workdir: Absolute path to the working directory.
        """
        assert os.path.isabs(workdir)
        
        # Remove the working directory
        self.remove_if_exists(workdir)
        
        # Extract asset merge test data into the working dir
        unzip_file.unzip_file(self.TESTDATA_ZIP, workdir)
        
        # Extract expected data
        unzip_file.unzip_file(self.EXPECTED_ZIP, os.path.join(workdir, 'expected'))
        
        return workdir
    
    def assert_is_expected(self, subdir):
        """
        Assert that the current main_project is equal to the expected data.
        """
        current_dir = os.path.abspath('main_project')
        expected_dir = os.path.abspath(os.path.join('expected', subdir))
        self.assert_exists_and_contains_something(expected_dir)
        self.assert_dir_contents_equal(current_dir, expected_dir, ['.svn', '.metadata'])
    
    @run_in_workdir('merge_asset1')
    def test_merge_asset1(self):
        self.run_command('%s -p main_project --targetlayer assets/test/root.confml -r asset1_v1 --sourcelayer root.confml' % get_cmd('merge'))
        self.assert_is_expected('asset1_merged')
    
    @run_in_workdir('merge_and_update_asset1')
    def test_merge_and_update_asset1(self):
        self.run_command('%s -p main_project --targetlayer assets/test/root.confml -r asset1_v1 --sourcelayer root.confml' % get_cmd('merge'))
        self.assert_is_expected('asset1_merged')
        self.run_command('%s -p main_project --targetlayer assets/test/root.confml -r asset1_v2 --sourcelayer root.confml' % get_cmd('merge'))
        self.assert_is_expected('asset1_merged_and_updated')
    
    @run_in_workdir('merge_both')
    def test_merge_both(self):
        self.run_command('%s -p main_project --targetlayer assets/test/root.confml -r asset1_v1 --sourcelayer root.confml' % get_cmd('merge'))
        self.run_command('%s -p main_project --targetlayer assets/test/root.confml -r asset2_v1 --sourcelayer root.confml' % get_cmd('merge'))
        self.assert_is_expected('both_merged')
    
    @run_in_workdir('merge_both_and_update')
    def test_merge_both_and_update(self):
        
        self.run_command('%s -p main_project --targetlayer assets/test/root.confml -r asset1_v1 --sourcelayer root.confml' % get_cmd('merge'))
        self.run_command('%s -p main_project --targetlayer assets/test/root.confml -r asset2_v1 --sourcelayer root.confml' % get_cmd('merge'))
        self.assert_is_expected('both_merged')
        
        self.run_command('%s -p main_project --targetlayer assets/test/root.confml -r asset1_v2 --sourcelayer root.confml' % get_cmd('merge'))
        self.run_command('%s -p main_project --targetlayer assets/test/root.confml -r asset2_v2 --sourcelayer root.confml' % get_cmd('merge'))
        self.assert_is_expected('both_merged_and_updated')

class TestMergeInvalidParameters(BaseTestCase):
    
    def _run_test(self, args, expected_msg):
        if not isinstance(args, basestring):
            args = ' '.join(args)
        
        cmd = get_cmd('merge') + ' ' + args
        # Note: The following run_command() should really expect the
        #       return code 2, but for some reason when running from the
        #       standalone test set, the return value is 0 for some cases
        #       (specifically, the ones that don't use parser.error() to
        #       exit the program)
        out = self.run_command(cmd, expected_return_code = None)
        
        self.assertTrue(expected_msg in out,
                        "Expected message '%s' not in output ('%s')" % (expected_msg, out))
    
    def test_no_remote(self):
        self._run_test('', "Remote project must be given")
    
    def test_source_root_and_target_layer(self):
        self._run_test(
           "-p x --targetlayer t.confml -r y --sourceconfiguration s.confml",
           "Cannot merge a configuration into a layer!")
    
    def test_source_layer_and_target_root(self):
        self._run_test(
           "-p x --configuration t.confml -r y --sourcelayer s.confml",
           "Merging a layer into a configuration is not supported at the moment!")
    
    def test_source_layer_and_layer_indices(self):
        self._run_test(
            ["-p x --configuration t.confml",
             "-r y --sourcelayer s.confml",
             "--layer -1 --layer -2"],
            "Specifying layer indices using --layer is not supported when using --sourcelayer or --targetlayer!")
    
    def test_target_layer_and_layer_indices(self):
        self._run_test(
            ["-p x --targetlayer t.confml",
             "-r y --sourceconfiguration s.confml",
             "--layer -1 --layer -2"],
            "Specifying layer indices using --layer is not supported when using --sourcelayer or --targetlayer!")
    
    def test_invalid_source_layer(self):
        source_dir = os.path.join(TEMP_DIR, 'invalid_source_layer/source_proj')
        target_dir = os.path.join(TEMP_DIR, 'invalid_source_layer/target_proj')
        self.recreate_dir(source_dir)
        self.recreate_dir(target_dir)
        self._run_test('-p "%s" --targetlayer foo/root.confml -r "%s" --sourcelayer foo/bar/root.confml' % (source_dir, target_dir),
                       "Could not merge: Layer root 'foo/bar/root.confml' not found in source project")
    
    def test_invalid_source_config(self):
        source_dir = os.path.join(TEMP_DIR, 'invalid_source_root/source_proj')
        target_dir = os.path.join(TEMP_DIR, 'invalid_source_root/target_proj')
        self.recreate_dir(source_dir)
        self.recreate_dir(target_dir)
        self._run_test('-p "%s" -c foo_root.confml -r "%s" --sourceconfiguration foobar_root.confml' % (source_dir, target_dir),
                       "Could not merge: Configuration root 'foobar_root.confml' not found in source project")
    
    def test_invalid_merge_policy(self):
        self._run_test('-p x -r y --merge-policy foopolicy',
                       "Invalid merge policy: foopolicy")
    
    def test_invalid_source_layer_root(self):
        self._run_test('-p x -r y --sourcelayer foobar --targetlayer test/foo.confml',
                       "Source layer root should be a .confml file")
    
    def test_invalid_target_layer_root(self):
        self._run_test('-p x -r y --sourcelayer test/foo.confml --targetlayer foobar',
                       "Target layer root should be a .confml file")

if __name__ == '__main__':
    unittest.main()
