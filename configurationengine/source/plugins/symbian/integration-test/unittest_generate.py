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

import sys, os, shutil, unittest

from testautomation.base_testcase import BaseTestCase
from testautomation import zip_dir

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

if sys.platform == "win32":
    CONE_SCRIPT = "cone.cmd"
else:
    CONE_SCRIPT = "cone"

def get_cmd(action='generate'):
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

class TestSymbianGenerateAllImplsOnLastLayer(BaseTestCase):
    
    def _prepare_workdir(self, workdir):
        workdir = os.path.join(ROOT_PATH, workdir)
        self.recreate_dir(workdir)
        
        # Get the binaries needed for ImageML to work
        bin_target_dir = os.path.join(workdir, "bin")
        self.recreate_dir(bin_target_dir)
        bin_source_dir = os.path.join(ROOT_PATH, "testdata/generate/imageplugin_bin")
        for name in os.listdir(bin_source_dir):
            source_path = os.path.join(bin_source_dir, name)
            target_path = os.path.join(bin_target_dir, name)
            if os.path.isfile(source_path):
                shutil.copy2(source_path, target_path)
        
        # Create the mock carbide.ui directory
        target_dir = os.path.join(workdir, "mock_carbide_ui")
        self.recreate_dir(target_dir)
        def copy_file(file_name):
            source_file = os.path.join(ROOT_PATH, "testdata/generate/mock_carbide_ui", file_name)
            target_file = os.path.join(target_dir, file_name)
            shutil.copy2(source_file, target_file)
        copy_file('makepackage.bat')
        copy_file('makepackage.py')
        
        return workdir
    
    def test_generate_all_impls_on_last_layer_on_file_storage(self):
        project_dir = os.path.join(ROOT_PATH, "testdata/generate/project")
        self.assert_exists_and_contains_something(project_dir)
        self._run_test_generate_all_impls_on_last_layer(
            workdir = 'temp/gen_ll1',
            project = project_dir,
            expected = os.path.join(ROOT_PATH, 'testdata/generate/expected_last_layer'),
            args = '--layer -1',
            linux_ignores = ['anim1.mbm', 'anim2.mif', '20000000.txt', '10207114',  'themepackage.mbm', 'themepackage.mif', '12340001', '12340002', 'resource'])
    
    def test_generate_all_impls_target_rofs2_file_storage(self):
        project_dir = os.path.join(ROOT_PATH, "testdata/generate/project")
        self.assert_exists_and_contains_something(project_dir)
        self._run_test_generate_all_impls_on_last_layer(
            workdir = 'temp/gen_ll_rofs2',
            project = project_dir,
            expected = os.path.join(ROOT_PATH, 'testdata/generate/expected_rofs2'),
            args = '--all-layers --impl-tag target:rofs2')
    
    def test_generate_all_impls_on_last_layer_on_zip_storage(self):
        project_dir = os.path.join(ROOT_PATH, "testdata/generate/project")
        self.assert_exists_and_contains_something(project_dir)
        
        project_zip = os.path.join(ROOT_PATH, "temp/generation_test_project.zip")
        self.remove_if_exists(project_zip)
        zip_dir.zip_dir(project_dir, project_zip, [zip_dir.SVN_IGNORE_PATTERN])
        self.assert_exists_and_contains_something(project_zip)
        
        self._run_test_generate_all_impls_on_last_layer(
            workdir = 'temp/gen_ll2',
            project = project_zip,
            expected = os.path.join(ROOT_PATH, 'testdata/generate/expected_last_layer'),
            args = '--layer -1',
            linux_ignores = ['anim1.mbm', 'anim2.mif', '20000000.txt', '10207114', 'themepackage.mbm', 'themepackage.mif', '12340001', '12340002', 'resource' ])
    
    def _run_test_generate_all_impls_on_last_layer(self, workdir, project, expected, args='', linux_ignores=[]):
        # Create a temp workdir and go there to run the test
        orig_workdir = os.getcwd()
        workdir = self._prepare_workdir(workdir)
        os.chdir(workdir)
        
        try:
            # Run the generation command
            cmd = '%s -p "%s" --output output --add-setting-file imaker_variantdir.cfg %s' % (get_cmd(), project, args)
            self.run_command(cmd)
            
            self.assert_dir_contents_equal('output', expected, ['.svn'] + linux_ignores)
        finally:
            os.chdir(orig_workdir)

class TestDeltaCenrepGeneration(BaseTestCase):
    
    def test_generate_deltacenreps(self):
        self._run_test_generation(
            workdir      = 'temp/deltacenrep/deltacenrep',
            expected_dir = 'testdata/deltacenrep/deltacenrep_expected',
            tag_args     = '--impl-tag target:rofs3 --impl-tag crml:deltacenrep')
    
    def test_generate_normal_cenreps_from_deltacenrep_project(self):
        self._run_test_generation(
            workdir      = 'temp/deltacenrep/normalcenrep',
            expected_dir = 'testdata/deltacenrep/normalcenrep_expected',
            tag_args     = '--impl-tag target:rofs3')
    
    def _run_test_generation(self, workdir, expected_dir, tag_args):
        PROJECT_DIR = os.path.join(ROOT_PATH, 'testdata/deltacenrep/project')
        EXPECTED_DIR = os.path.join(ROOT_PATH, expected_dir)
        
        # Create a temp workdir and go there to run the test
        orig_workdir = os.getcwd()
        workdir = os.path.join(ROOT_PATH, workdir)
        self.recreate_dir(workdir)
        os.chdir(workdir)
        
        try:
            # Run the generation command
            cmd = '%(cmd)s -p "%(project)s" --output output --layer -1 '\
                  '--add-setting-file imaker_variantdir.cfg %(args)s'\
                  % {'cmd'      : get_cmd(),
                     'project'  : PROJECT_DIR,
                     'args'     : tag_args}
            self.run_command(cmd)
            OUTPUT_DIR = os.path.abspath('output')
            
            # Assert that the CenRep files are equal
            self.assert_dir_contents_equal(OUTPUT_DIR, EXPECTED_DIR, ignore=['.svn', 'include'])
            
            # If generating delta CenReps, check also the iby file
            OUTPUT_IBY = os.path.join(OUTPUT_DIR, 'include/deltacenreps.iby')
            EXPECTED_IBY = os.path.join(EXPECTED_DIR, 'include/deltacenreps.iby')
            if os.path.exists(EXPECTED_IBY):
                self.assert_file_contents_equal(OUTPUT_IBY, EXPECTED_IBY,
                    ignore_patterns = [r'(\w:)?[\\/].*output[\\/]deltacenreps[\\/]'],
                    ignore_endline_style = True)
        finally:
            os.chdir(orig_workdir)

if __name__ == '__main__':
      unittest.main()
