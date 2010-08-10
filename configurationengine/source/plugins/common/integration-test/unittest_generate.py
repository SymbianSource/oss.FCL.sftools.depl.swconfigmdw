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
# @author Lasse Salo

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

def get_uses_layer_test_project():
    # If running from the working copy
    dir1 = os.path.normpath(os.path.join(ROOT_PATH, '../ConeRulePlugin/ruleplugin/evals/tests/layer_filtering_project'))
    if os.path.isdir(dir1): return dir1
    
    # If running from standalone
    dir2 = os.path.normpath(os.path.join(ROOT_PATH, 'testdata/uses_layer_test_project'))
    if os.path.isdir(dir2): return dir2
    
    raise RuntimeError("layers_used() test project found neither in '%s' nor '%s'!" % (dir1, dir2))

class TestCommonGenerateAllImplsOnLastLayer(BaseTestCase):
    
    def _prepare_workdir(self, workdir):
        workdir = os.path.join(ROOT_PATH, workdir)
        self.recreate_dir(workdir)
        
        # Any needed extra preparation can be done here
        
        return workdir
    
    def test_generate_all_impls_on_last_layer_on_file_storage(self):
        project_dir = os.path.join(ROOT_PATH, "testdata/generate/project")
        self.assert_exists_and_contains_something(project_dir)
        self._run_test_generate_all_impls_on_last_layer('temp/gen_ll1', project_dir)
    
    def test_generate_all_impls_on_last_layer_on_zip_storage(self):
        project_dir = os.path.join(ROOT_PATH, "testdata/generate/project")
        self.assert_exists_and_contains_something(project_dir)
        
        project_zip = os.path.join(ROOT_PATH, "temp/generation_test_project.zip")
        self.remove_if_exists(project_zip)
        zip_dir.zip_dir(project_dir, project_zip, [zip_dir.SVN_IGNORE_PATTERN])
        self.assert_exists_and_contains_something(project_zip)
        
        self._run_test_generate_all_impls_on_last_layer('temp/gen_ll2', project_zip)

    def test_uses_layers_rule(self):
        project_dir = get_uses_layer_test_project()
        self.assert_exists_and_contains_something(project_dir)
        
        orig_workdir = os.getcwd()
        workdir = self._prepare_workdir("temp/uses_layers_test")
        os.chdir(workdir)
        
        try:
            cmd = '%s -p "%s" --output output --add-setting-file imaker_variantdir.cfg' % (get_cmd(), project_dir)
            self.run_command(cmd)
            
            self.assert_file_contents_equal(
                os.path.join(ROOT_PATH, "testdata/uses_layers_test_expected.txt"),
                "output/uses_layers_test.txt",
                ignore_endline_style=True)
        finally:
            os.chdir(orig_workdir)
            
    def test_override_templateml_outputattribs_from_cmd_line(self):
        project_dir = os.path.join(ROOT_PATH, 'testdata', 'templateml_test_project')
        
        #Added because of known bug #1018 (test data missing)
        # Remove after fix ->
        if os.path.isdir(project_dir):
            if len(os.listdir(project_dir)) == 0:
                self.fail("Path '%s' exists (is a directory) but does not contain anything)" % project_dir)
        elif os.path.isfile(project_dir):
            if os.stat(project_dir).st_size == 0:
                self.fail("Path '%s' exists (is a file) but does not contain anything)" % project_dir)
        else:
            self.fail("Known bug #1018: Test data missing. Path '%s' does not exist" % project_dir)
        # Remove after fix <-
        
        self.assert_exists_and_contains_something(project_dir)
        
        workdir = os.getcwd()
        workdir = self._prepare_workdir(os.path.join('temp','gen_tmplml_out_from_cmd_line'))
        
        logfile = os.path.join(workdir, 'cone.log')
        
        file1 = os.path.join(workdir,'setdir','setfile1.txt')
        file2 = os.path.join(workdir,'setdir','setfile2.txt')        
        
        cmd = ['%(cone_cmd)s',
               '-p "%(project)s"',
               '-c root.confml',
               '--output "%(output)s"',
               '--log-file="%(log_file)s"',
               '--all-layers',
               '--set=Tempfeature.Outputfile1=setfile1.txt',
               '--set=Tempfeature.Outputfile2=setfile2.txt',
               '--set=Tempfeature.Outputdir=setdir',
               '--set=Tempfeature.Encoding=UTF-16',
               '--set=Tempfeature.BOM=false',
               '--set=Tempfeature.Newline=unix',]
        cmd = ' '.join(cmd) % {'cone_cmd':      get_cmd(),
                               'project':       project_dir,
                               'output':        workdir,
                               'log_file':      logfile}

        self.run_command(cmd)
        
        self.assert_exists_and_contains_something(os.path.join(workdir,'setdir'))
        self.assert_file_contains(file1, ['TempFeature.Outputfile1:  setfile1.txt',
                                          'TempFeature.Outputdir:    setdir',
                                          'TempFeature.Encoding:     UTF-16',
                                          'TempFeature.BOM:          false',
                                          'TempFeature.Newline:      unix'],
                                          encoding='UTF-16')
        self.assert_file_contains(file2, ['TempFeature.Outputfile2:  setfile2.txt',
                                          'TempFeature.Outputdir:    setdir',
                                          'TempFeature.Encoding:     UTF-8',
                                          'TempFeature.BOM:          true',
                                          'TempFeature.Newline:      win'])
        

    def test_set_tempvariables_as_templateml_outputattribs(self):
        project_dir = os.path.join(ROOT_PATH, 'testdata', 'templateml_test_project')
        
        #Added because of known bug #1018 (test data missing)
        # Remove after fix ->
        if os.path.isdir(project_dir):
            if len(os.listdir(project_dir)) == 0:
                self.fail("Path '%s' exists (is a directory) but does not contain anything)" % project_dir)
        elif os.path.isfile(project_dir):
            if os.stat(project_dir).st_size == 0:
                self.fail("Path '%s' exists (is a file) but does not contain anything)" % project_dir)
        else:
            self.fail("Known bug #1018: Test data missing. Path '%s' does not exist" % project_dir)
        # Remove after fix <-
        
        self.assert_exists_and_contains_something(project_dir)
        
        workdir = os.getcwd()
        workdir = self._prepare_workdir(os.path.join('temp','gen_tmplml_out_from_ref'))
        
        logfile = os.path.join(workdir, 'cone.log')
        
        file1 = os.path.join(workdir,'origdir','orig1.txt')
        file2 = os.path.join(workdir,'origdir','orig2.txt')
        
        cmd = ['%(cone_cmd)s',
               '-p "%(project)s"',
               '-c root.confml',
               '--output "%(output)s"',
               '--log-file="%(log_file)s"',
               '--all-layers',]
        cmd = ' '.join(cmd) % {'cone_cmd':      get_cmd(),
                               'project':       project_dir,
                               'output':        workdir,
                               'log_file':      logfile}

        self.run_command(cmd)
        
        self.assert_exists_and_contains_something(os.path.join(workdir,'origdir'))
        self.assert_file_contains(file1, ['TempFeature.Outputfile1:  orig1.txt',
                                          'TempFeature.Outputdir:    origdir',
                                          'TempFeature.Encoding:     ASCII',
                                          'TempFeature.BOM:          true',
                                          'TempFeature.Newline:      win'])
        self.assert_file_contains(file2, ['TempFeature.Outputfile2:  orig2.txt',
                                          'TempFeature.Outputdir:    origdir',
                                          'TempFeature.Encoding:     UTF-8',
                                          'TempFeature.BOM:          true',
                                          'TempFeature.Newline:      win'])
    
    def _run_test_generate_all_impls_on_last_layer(self, workdir, project):
        # Create a temp workdir and go there to run the test
        orig_workdir = os.getcwd()
        workdir = self._prepare_workdir(workdir)
        os.chdir(workdir)
        
        try:
            cmd = '%s -p "%s" --output output --layer -1 --add-setting-file imaker_variantdir.cfg' % (get_cmd(), project)
            self.run_command(cmd)
            
            EXPECTED_DIR = os.path.join(ROOT_PATH, "testdata/generate/expected")
            self.assert_dir_contents_equal('output', EXPECTED_DIR, ['.svn'])
        finally:
            os.chdir(orig_workdir)




if __name__ == '__main__':
      unittest.main()
