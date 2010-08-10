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
import zipfile
import shutil

from testautomation.base_testcase import BaseTestCase
from testautomation.unzip_file import unzip_file
from cone.storage.filestorage import FileStorage
from cone.storage.zipstorage import ZipStorage
from scripttest_common import get_cmd

ROOT_PATH   = os.path.dirname(os.path.abspath(__file__))

def abspath(p):
    return os.path.normpath(os.path.join(ROOT_PATH, p))
    
TEST_PROJECT_CPF    = abspath("test_project.cpf")
TEMP_DIR            = abspath("temp/export")
EXPORT_TEST_PROJECT = abspath("export_test_project.zip")

class TestExport(BaseTestCase):

    def setUp(self):
        self.orig_workdir = os.getcwd()
        os.chdir(ROOT_PATH)
        
    def tearDown(self):
        os.chdir(self.orig_workdir)

    def test_get_help(self):
        cmd = '%s -h' % get_cmd('export')
        out = self.run_command(cmd)
        lines = out.split(os.linesep)
        self.assertTrue('Options:' in lines)
        self.assertTrue('  Export options:' in lines)

    def test_export_project(self):
        remote = os.path.join(TEMP_DIR, 'test1')
        self.remove_if_exists(remote)
        
        self.set_modification_reference_time(TEST_PROJECT_CPF)
        cmd = '%s -p "%s" -c "root4.confml" -r "%s"' % (get_cmd('export'), TEST_PROJECT_CPF, remote)
        out = self.run_command(cmd)
        #print out
        lines = out.split(os.linesep)
        self.assertTrue('Export root4.confml to %s done!' % remote in lines)
        
        self.assertEquals(set(os.listdir(remote)),
            set(["Layer1", "Layer2", "Layer3", "Layer4", ".metadata", "root4.confml"]))
        def fp(p): # fp = full_path
            return os.path.join(remote, p)
        self.assert_exists_and_contains_something(fp("Layer1"))
        self.assert_exists_and_contains_something(fp("Layer2"))
        self.assert_exists_and_contains_something(fp("Layer3"))
        self.assert_exists_and_contains_something(fp("Layer4"))
        self.assert_exists_and_contains_something(fp("root4.confml"))
        
        self.assert_not_modified(TEST_PROJECT_CPF)
        
    def test_export_multiple_configurations(self):
        remote = os.path.join(TEMP_DIR, 'test2')
        self.remove_if_exists(remote)
        
        self.set_modification_reference_time(TEST_PROJECT_CPF)
        cmd = '%s -p "%s" -c "root2.confml" -c "root3.confml" -c "root5.confml" -r "%s"' % (get_cmd('export'), TEST_PROJECT_CPF, remote)
        out = self.run_command(cmd)
        #print out
        lines = out.split(os.linesep)
        self.assertTrue('Export root2.confml to %s done!' % remote in lines)
        self.assertTrue('Export root3.confml to %s done!' % remote in lines)
        self.assertTrue('Export root5.confml to %s done!' % remote in lines)
        
        self.assertEquals(set(os.listdir(remote)),
            set(["Layer1", "Layer2", "Layer3", "Layer4", "Layer5",
                 ".metadata", "root2.confml", "root3.confml", "root5.confml"]))
        def fp(p): # fp = full_path
            return os.path.join(remote, p)
        self.assert_exists_and_contains_something(fp("Layer1"))
        self.assert_exists_and_contains_something(fp("Layer2"))
        self.assert_exists_and_contains_something(fp("Layer3"))
        self.assert_exists_and_contains_something(fp("Layer4"))
        self.assert_exists_and_contains_something(fp("Layer5"))
        self.assert_exists_and_contains_something(fp("root2.confml"))
        self.assert_exists_and_contains_something(fp("root3.confml"))
        self.assert_exists_and_contains_something(fp("root5.confml"))
        
        self.assert_not_modified(TEST_PROJECT_CPF)
    
    def test_export_multiple_configurations_into_cpf(self):
        remote = os.path.join(TEMP_DIR, 'test3.cpf')
        self.remove_if_exists(remote)
        
        self.set_modification_reference_time(TEST_PROJECT_CPF)
        cmd = '%s -p "%s" -c "root2.confml" -c "root3.confml" -c "root5.confml" -r "%s"' % (get_cmd('export'), TEST_PROJECT_CPF, remote)
        out = self.run_command(cmd)
        #print out
        lines = out.split(os.linesep)
        self.assertTrue('Export root2.confml to %s done!' % remote in lines)
        self.assertTrue('Export root3.confml to %s done!' % remote in lines)
        self.assertTrue('Export root5.confml to %s done!' % remote in lines)
        
        self.assert_zip_entry_exists(remote, "root2.confml")
        self.assert_zip_entry_exists(remote, "root3.confml")
        self.assert_zip_entry_exists(remote, "root5.confml")
        
        self.assert_not_modified(TEST_PROJECT_CPF)
    
    def assert_zip_entry_exists(self, zip_file, path):
        zf = zipfile.ZipFile(zip_file, "r")
        try:
            if path not in zf.namelist():
                self.fail("Entry '%s' not in zip file '%s'." % (path, zipfile))
        finally:
            zf.close()
    
    
    def _run_test_export_project_to_project(self,
        source_project, source_storage_type,
        target_project, target_storage_type,
        empty_folders):
        # Set up the source project
        # -------------------------
        source_path = os.path.join(TEMP_DIR, source_project)
        self.remove_if_exists(source_path)
        if source_storage_type == 'file':
            unzip_file(EXPORT_TEST_PROJECT, source_path, delete_if_exists=True)
        elif source_storage_type == 'zip':
            self.create_dir_for_file_path(source_path)
            shutil.copy2(EXPORT_TEST_PROJECT, source_path)
        else:
            raise RuntimeError('Invalid storage type %r' % source_storage_type)
        
        # Set up the target project
        # -------------------------
        target_path = os.path.join(TEMP_DIR, target_project)
        self.remove_if_exists(target_path)
        if target_storage_type not in ('file', 'zip'):
            raise RuntimeError('Invalid storage type %r' % target_storage_type)
        
        # Run the command
        # ---------------
        if empty_folders:   empty_folder_switch = ''
        else:               empty_folder_switch = '--exclude-folders'
        cmd = '%s -p "%s" -c "root5.confml" -r "%s" %s' % \
            (get_cmd('export'), source_path, target_path, empty_folder_switch)
        out = self.run_command(cmd)
        
        # Check the output
        # ----------------
        if target_storage_type == 'file':   storage_class = FileStorage
        elif target_storage_type == 'zip':  storage_class = ZipStorage
        
        storage = storage_class(target_path, 'r')
        res_list = storage.list_resources("/", recurse=True, empty_folders=True)
        
        expected = ['.metadata',
                    'root5.confml',
                    'Layer1/root.confml',
                    'Layer2/root.confml',
                    'Layer3/root.confml',
                    'Layer4/root.confml',
                    'Layer5/root.confml',]
        for res in expected:
            self.assertTrue(res in res_list, "%r not in %r" % (res, res_list))
            self.assertFalse(storage.is_folder(res), "%r is a folder")
        
        not_expected = ['Layer1/foo/foo.txt',
                        'Layer2/foo/layer2_foo.txt',
                        'Layer3/foo/layer3_foo.txt',
                        'Layer4/foo/layer4_foo.txt',
                        'Layer5/foo/layer5_foo.txt',]
        for res in not_expected:
            self.assertFalse(res in res_list, "%r in %r" % (res, res_list))
        
        # Check empty folders
        expected = ['Layer1/doc/empty',
                    'Layer1/content/empty',
                    'Layer1/implml/empty',
                    'Layer3/doc/empty',
                    'Layer3/content/empty',
                    'Layer3/implml/empty',]
        not_expected = ['Layer1/foo/empty',
                        'Layer3/foo/empty']
        if empty_folders:
            for res in expected:
                self.assertTrue(res in res_list, "%r not in %r" % (res, res_list))
                self.assertTrue(storage.is_folder(res), "%r is not a folder")
            
            for res in not_expected:
                self.assertFalse(res in res_list, "%r in %r" % (res, res_list))
        else:
            for res in expected + not_expected:
                self.assertFalse(res in res_list, "%r in %r" % (res, res_list))

    
    def test_export_file_to_file(self):
        self._run_test_export_project_to_project(
            source_project      = 'f2f/source',
            source_storage_type = 'file',
            target_project      = 'f2f/target',
            target_storage_type = 'file',
            empty_folders       = False)
    
        self._run_test_export_project_to_project(
            source_project      = 'f2f/source_ef',
            source_storage_type = 'file',
            target_project      = 'f2f/target_ef',
            target_storage_type = 'file',
            empty_folders       = True)
    
    def test_export_zip_to_zip(self):
        self._run_test_export_project_to_project(
            source_project      = 'z2z/source.zip',
            source_storage_type = 'zip',
            target_project      = 'z2z/target.zip',
            target_storage_type = 'zip',
            empty_folders       = False)
    
        self._run_test_export_project_to_project(
            source_project      = 'z2z/source_ef.zip',
            source_storage_type = 'zip',
            target_project      = 'z2z/target_ef.zip',
            target_storage_type = 'zip',
            empty_folders       = True)
    
    def test_export_file_to_zip(self):
        self._run_test_export_project_to_project(
            source_project      = 'f2z/source',
            source_storage_type = 'file',
            target_project      = 'f2z/target.zip',
            target_storage_type = 'zip',
            empty_folders       = False)
    
        self._run_test_export_project_to_project(
            source_project      = 'f2z/source_ef',
            source_storage_type = 'file',
            target_project      = 'f2z/target_ef.zip',
            target_storage_type = 'zip',
            empty_folders       = True)
    
    def test_export_zip_to_file(self):
        self._run_test_export_project_to_project(
            source_project      = 'z2f/source.zip',
            source_storage_type = 'zip',
            target_project      = 'z2f/target',
            target_storage_type = 'file',
            empty_folders       = False)
    
        self._run_test_export_project_to_project(
            source_project      = 'z2f/source_ef.zip',
            source_storage_type = 'zip',
            target_project      = 'z2f/target_ef',
            target_storage_type = 'file',
            empty_folders       = True)
    
    def test_export_to_target_with_nonexistent_path(self):
        # Remove the target root directory to make sure that it
        # does not exist before the export
        self.remove_if_exists(os.path.join(TEMP_DIR, 'nep'))
        
        self._run_test_export_project_to_project(
            source_project      = 'f2z/source',
            source_storage_type = 'file',
            target_project      = 'nep/f2z/x/y/z/target.zip',
            target_storage_type = 'zip',
            empty_folders       = False)
    
        self._run_test_export_project_to_project(
            source_project      = 'f2z/source',
            source_storage_type = 'file',
            target_project      = 'nep/f2f/x/y/z/target',
            target_storage_type = 'file',
            empty_folders       = False)
    
    def _run_test_multi_export(self, export_dir, export_format, config_args,
                               expected_cpfs=None, expected_dirs=None):
        self.assertFalse(expected_cpfs is not None and expected_dirs is not None,
                         "Only one of expected_cpfs or expected_dirs can be specified!")
        self.assertFalse(expected_cpfs is None and expected_dirs is None,
                         "Either expected_cpfs or expected_dirs must be specified!")
        
        EXPORT_DIR = os.path.join(TEMP_DIR, export_dir)
        self.remove_if_exists(EXPORT_DIR)
        
        self.set_modification_reference_time(TEST_PROJECT_CPF)
        cmd = '%(cmd)s -p "%(project)s" %(args)s --export-dir "%(export_dir)s" --export-format %(export_format)s' \
            % {'cmd'            : get_cmd('export'),
               'project'        : TEST_PROJECT_CPF,
               'args'           : config_args,
               'export_dir'     : EXPORT_DIR,
               'export_format'  : export_format}
        out = self.run_command(cmd)
        self.assert_not_modified(TEST_PROJECT_CPF)
        
        if expected_cpfs:
            for cpf_name, config_root in expected_cpfs:
                path = os.path.join(EXPORT_DIR, cpf_name)
                self.assert_exists_and_contains_something(path)
                self.assert_zip_entry_exists(path, config_root)
        else:
            for dir_name, config_root in expected_dirs:
                path = os.path.join(EXPORT_DIR, dir_name)
                self.assert_exists_and_contains_something(path)
                self.assert_exists_and_contains_something(os.path.join(path, config_root))
    
    def test_export_multiple_cpfs(self):
        self._run_test_multi_export(
            export_dir    = 'multiexport/cpfs',
            export_format = 'cpf',
            config_args   = '--configuration root1.confml '\
                            '--configuration root3.confml',
            expected_cpfs = [('root1.cpf', 'root1.confml'),
                             ('root3.cpf', 'root3.confml')])
    
    def test_export_multiple_dirs(self):
        self._run_test_multi_export(
            export_dir    = 'multiexport/dirs',
            export_format = 'dir',
            config_args   = '--configuration root1.confml '\
                            '--configuration root3.confml',
            expected_dirs = [('root1/', 'root1.confml'),
                             ('root3/', 'root3.confml')])
    
    def test_export_multiple_dirs_with_added_layers(self):
        self._run_test_multi_export(
            export_dir    = 'multiexport/dirs_with_added_layers',
            export_format = 'dir',
            config_args   = '--configuration root1.confml '\
                            '--configuration root3.confml '\
                            '--add new/layer1/root.confml '\
                            '--add new/layer2/root.confml ',
            expected_dirs = [('root1/', 'root1.confml'),
                             ('root3/', 'root3.confml')])
        # Check that the added layers have really been added to the exported
        # projects
        def check(path):
            path = os.path.join(TEMP_DIR, 'multiexport/dirs_with_added_layers', path)
            self.assert_exists_and_contains_something(path)
        check('root1/new/layer1/root.confml')
        check('root1/new/layer2/root.confml')
        check('root3/new/layer1/root.confml')
        check('root3/new/layer2/root.confml')
        
        # Check that the configuration root contains the added layers
        file_path = os.path.join(TEMP_DIR, 'multiexport/dirs_with_added_layers/root1/root1.confml')
        data = self.read_data_from_file(file_path)
        self.assertTrue('href="Layer1/root.confml"' in data)
        self.assertTrue('href="new/layer1/root.confml"' in data)
        self.assertTrue('href="new/layer2/root.confml"' in data)
        
        file_path = os.path.join(TEMP_DIR, 'multiexport/dirs_with_added_layers/root3/root3.confml')
        data = self.read_data_from_file(file_path)
        self.assertTrue('href="Layer1/root.confml"' in data)
        self.assertTrue('href="Layer2/root.confml"' in data)
        self.assertTrue('href="Layer3/root.confml"' in data)
        self.assertTrue('href="new/layer1/root.confml"' in data)
        self.assertTrue('href="new/layer2/root.confml"' in data)
    
    def test_export_multiple_cpfs_with_wildcard(self):
        self._run_test_multi_export(
            export_dir    = 'multiexport/cpfs_wildcard',
            export_format = 'cpf',
            config_args   = '--config-wildcard root*.confml',
            expected_cpfs = [('root1.cpf', 'root1.confml'),
                             ('root2.cpf', 'root2.confml'),
                             ('root3.cpf', 'root3.confml'),
                             ('root4.cpf', 'root4.confml'),
                             ('root5.cpf', 'root5.confml')])
    
    def test_export_multiple_cpfs_with_regex(self):
        self._run_test_multi_export(
            export_dir    = 'multiexport/cpfs_regex',
            export_format = 'cpf',
            config_args   = '--config-regex root[14].confml',
            expected_cpfs = [('root1.cpf', 'root1.confml'),
                             ('root4.cpf', 'root4.confml')])
    

class TestExportInvalidArgs(BaseTestCase):
    
    def _run_test_invalid_args(self, args, expected_msg):
        cmd = '%s -p "%s" %s' \
            % (get_cmd('export'), TEST_PROJECT_CPF, args)
        # Note: The following run_command() should really expect the
        #       return code 2, but for some reason when running from the
        #       standalone test set, the return value is 0
        out = self.run_command(cmd, expected_return_code = None)
        self.assertTrue(expected_msg in out,
                        "Expected message '%s' not in output.\nOutput:\n%s" % (expected_msg, out))
    
    def test_export_format_without_export_dir(self):
        self._run_test_invalid_args(
            '-c root1.confml --export-format cpf',
            "error: --export-format can only be used in conjunction with --export-dir")
    
    def test_remote_storage_and_export_dir(self):
        self._run_test_invalid_args(
            '-c root1.confml --remote jojo.cpf --export-dir test/',
            "error: --export-dir and --remote cannot be used at the same time")
    
    def test_unknown_export_format(self):
        self._run_test_invalid_args(
            '-c root1.confml --export-dir test/ --export-format foo',
            "error: Invalid export format 'foo'")
    
    def test_export_dir_but_no_configurations(self):
        self._run_test_invalid_args(
            '--export-dir test/',
            "error: Use of --export-dir requires at least one configuration to be specified")
    

if __name__ == '__main__':
    unittest.main()
