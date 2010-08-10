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

class TestExampleGenerate(BaseTestCase):
    
    def _prepare_workdir(self, workdir):
        workdir = os.path.join(ROOT_PATH, workdir)
        self.recreate_dir(workdir)
        
        # Any needed extra preparation can be done here
        
        return workdir
    
    def test_generate_on_file_storage(self):
        project_dir = os.path.join(ROOT_PATH, "testdata/generate/project")
        self.assert_exists_and_contains_something(project_dir)
        self._run_test_generate('temp/gen1', project_dir)
    
    def test_generate_on_zip_storage(self):
        project_dir = os.path.join(ROOT_PATH, "testdata/generate/project")
        self.assert_exists_and_contains_something(project_dir)
        
        project_zip = os.path.join(ROOT_PATH, "temp/generation_test_project.zip")
        self.remove_if_exists(project_zip)
        zip_dir.zip_dir(project_dir, project_zip, [zip_dir.SVN_IGNORE_PATTERN])
        self.assert_exists_and_contains_something(project_zip)
        
        self._run_test_generate('temp/gen2', project_zip)
    
    def _run_test_generate(self, workdir, project):
        # Create a temp workdir and go there to run the test
        orig_workdir = os.getcwd()
        workdir = self._prepare_workdir(workdir)
        os.chdir(workdir)
        
        try:
            cmd = '%s -p "%s" --output output --add-setting-file imaker_variantdir.cfg' % (get_cmd(), project)
            self.run_command(cmd)
            
            EXPECTED_DIR = os.path.join(ROOT_PATH, "testdata/generate/expected")
            self.assert_dir_contents_equal(os.path.join(workdir,'output'), EXPECTED_DIR, ['.svn'])
        finally:
            os.chdir(orig_workdir)

if __name__ == '__main__':
      unittest.main()
