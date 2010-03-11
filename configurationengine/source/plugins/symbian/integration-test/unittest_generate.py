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
import __init__
from testautomation.base_testcase import BaseTestCase
from testautomation import zip_dir

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

if sys.platform == "win32":
    CONE_SCRIPT = "cone.cmd"
else:
    CONE_SCRIPT = "cone.sh"

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
        self._run_test_generate_all_impls_on_last_layer('temp/gen_ll1', project_dir)
    
    def test_generate_all_impls_on_last_layer_on_zip_storage(self):
        project_dir = os.path.join(ROOT_PATH, "testdata/generate/project")
        self.assert_exists_and_contains_something(project_dir)
        
        project_zip = os.path.join(ROOT_PATH, "temp/generation_test_project.zip")
        self.remove_if_exists(project_zip)
        zip_dir.zip_dir(project_dir, project_zip, [zip_dir.SVN_IGNORE_PATTERN])
        self.assert_exists_and_contains_something(project_zip)
        
        self._run_test_generate_all_impls_on_last_layer('temp/gen_ll2', project_zip)
    
    def _run_test_generate_all_impls_on_last_layer(self, workdir, project):
        # Create a temp workdir and go there to run the test
        orig_workdir = os.getcwd()
        workdir = self._prepare_workdir(workdir)
        os.chdir(workdir)
        
        try:
            # Run the generation command
            cmd = '%s -p "%s" --output output --layer -1 --add-setting-file imaker_variantdir.cfg' % (get_cmd(), project)
            self.run_command(cmd)
            
            # Check that all expected output files are generated
            def check(path):
                self.assert_exists_and_contains_something("output/" + path)
            
            try:
                check("content/animations/anim1.mbm")
                check("content/animations/anim2.mif")
            except AssertionError:
                if ' ' in ROOT_PATH:
                    self.fail("Known bug (#177)")
                else:
                    raise
            
            check("content/data/sounds/test.mp3")
            check("content/data/sequence_setting_test.txt")
            check("content/private/10202BE9/10000000.txt")
            check("content/private/10202BE9/12341001.txt")
            check("content/private/10202BE9/12341002.txt")
            check("content/private/10202BE9/20000000.txt")
            check("content/sound_folder/test2.mp3")
            check("hcr_test.h")
            check("content/private/10207114/import/12340001/themepackage.mbm")
            check("content/private/10207114/import/12340001/themepackage.mif")
            check("content/private/10207114/import/12340001/themepackage.skn")
            
            # Check that files that should not have been generated are not
            def check_not_gen(path):
                self.assertFalse(os.path.exists("output/" + path),
                                 "'%s' was generated when it should not have been!" % path)
            check_not_gen("content/private/10202BE9/ABCD0000.txt")
            check_not_gen("content/private/10202BE9/12341000.txt")
            
            # Check that the data has been generated correctly
            self.assert_file_contains(
                "output/content/private/10202BE9/12341002.txt",
                "0x1 int 42 0 cap_rd=alwayspass cap_wr=WriteDeviceData",
                encoding='utf-16')
            self.assert_file_contains(
                "output/content/private/10202BE9/10000000.txt",
                r'0x1 string "Z:\\data\\sounds\\test.mp3" 0 cap_rd=alwayspass cap_wr=WriteDeviceData',
                encoding='utf-16')
            self.assert_file_contains(
                "output/content/private/10202BE9/12341001.txt",
                u'0x1 string "default string カタカナ <&> カタカナ" 0 cap_rd=alwayspass cap_wr=WriteDeviceData',
                encoding='utf-16')
            self.assert_file_contains(
                "output/content/private/10202BE9/20000000.txt",
                ['0x11 string "305397761" 0',
                 '0x12 string "305397761" 0',
                 '0x13 string "305397761" 0',
                 '0x21 string "305397762" 0',
                 '0x22 string "305397762" 0'],
                encoding='utf-16')
        finally:
            os.chdir(orig_workdir)

if __name__ == '__main__':
      unittest.main()
