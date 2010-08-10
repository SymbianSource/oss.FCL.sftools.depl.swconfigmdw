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

import os, shutil
import unittest

from cone.public import plugin, api
from testautomation.base_testcase import BaseTestCase
from testautomation.unzip_file import unzip_file

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
TESTDATA_DIR  = os.path.join(ROOT_PATH, 'testdata')
TEMP_DIR = os.path.join(ROOT_PATH, 'temp/emptydircopy')

class TestContentCopyEmptyDirs(BaseTestCase):
    
    def _get_project_and_config(self, workdir, storage_type):
        # Create the working directory for the test
        self.remove_if_exists(workdir)
        os.makedirs(workdir)
        
        # Unpack or copy the project into the working directory
        project_source_zip = os.path.join(TESTDATA_DIR, 'emptydircopy/project.zip')
        if storage_type == 'fs':
            project_location = os.path.join(workdir, 'project')
            unzip_file(project_source_zip, project_location)
        elif storage_type == 'zs':
            project_location = os.path.join(workdir, 'project.zip')
            shutil.copy(project_source_zip, project_location)
        else:
            raise ValueError('Invalid storage type %r' % storage_type)
        
        # Copy the external content directory
        unzip_file(os.path.join(TESTDATA_DIR, 'emptydircopy/external_content.zip'),
                   os.path.join(workdir, 'external_content'))
        
        project = api.Project(api.Storage.open(project_location, 'r'))
        config = project.get_configuration('root.confml')
        return project, config
    
    def test_get_copy_list(self):
        workdir = os.path.join(TEMP_DIR, 'get_copy_list')
        proj, conf = self._get_project_and_config(workdir, 'fs')
        proj.close()
        impls = plugin.get_impl_set(conf)
        
        orig_dir = os.getcwd()
        os.chdir(workdir)
        try:
            self.assertEquals(1, len(impls))
            impl = iter(impls).next()
            self.assertEquals(8, len(impl.impls))
            
            # Normal inputs
            # -------------
            def check(impl_index, expected):
                self.assertEquals(sorted(impl.impls[impl_index].get_full_copy_list()),
                                  sorted(expected))
            check(0, [
                ('layer2/content/foobar/layer2_emptydir',       'foobar_out/layer2_emptydir', False),
                ('layer1/content/foobar/layer1_emptydir',       'foobar_out/layer1_emptydir', False),
                ('layer1/content/foobar/layer1_emptydir2/foo',  'foobar_out/layer1_emptydir2/foo', False),
                ('layer2/content/foobar/layer2.txt',            'foobar_out/layer2.txt', False),
                ('layer1/content/foobar/layer1.txt',            'foobar_out/layer1.txt', False)
            ])
            check(1, [
                #('layer2/content/foobar_filtered/layer2_filtered_emptydir', 'foobar_out/layer2_filtered_emptydir', False),
                #('layer1/content/foobar_filtered/layer1_filtered_emptydir', 'foobar_out/layer1_filtered_emptydir', False),
                ('layer1/content/foobar_filtered/bar.txt', 'foobar_out_filtered/bar.txt', False),
            ])
            check(2, [('layer1/content/empty', 'empty_out', False)])
            check(3, [])
            
            
            # External inputs
            # ---------------
            def check(impl_index, expected):
                expected = [(os.path.abspath(src).replace('\\', '/'), tgt, ext) for src, tgt, ext in expected]
                self.assertEquals(sorted(impl.impls[impl_index].get_full_copy_list()),
                                  sorted(expected))
            check(4, [
                ('external_content/foobar/emptydir',       'ext_out/foobar_out/emptydir', True),
                ('external_content/foobar/emptydir2/foo',  'ext_out/foobar_out/emptydir2/foo', True),
                ('external_content/foobar/x.txt',          'ext_out/foobar_out/x.txt', True)
            ])
            check(5, [
                #('external_content/foobar_filtered/layer1_filtered_emptydir', 'ext_out/foobar_out/layer1_filtered_emptydir', False),
                ('external_content/foobar_filtered/bar.txt', 'ext_out/foobar_out_filtered/bar.txt', True),
            ])
            check(6, [('external_content/empty', 'ext_out/empty_out', True)])
            check(7, [])
        finally:
            os.chdir(orig_dir)
            self.remove_if_exists(workdir)
    
    def test_copy_empty_dirs_filestorage(self):
        workdir = os.path.join(TEMP_DIR, 'filestorage')
        proj, conf = self._get_project_and_config(workdir, 'fs')
        
        orig_dir = os.getcwd()
        os.chdir(workdir)
        try:
            self._run_test_copy_empty_dirs(workdir, conf)
        finally:
            os.chdir(orig_dir)
            proj.close()
            self.remove_if_exists(workdir)
    
    def test_copy_empty_dirs_zipstorage(self):
        workdir = os.path.join(TEMP_DIR, 'zipstorage')
        proj, conf = self._get_project_and_config(workdir, 'zs')
        
        orig_dir = os.getcwd()
        os.chdir(workdir)
        try:
            self._run_test_copy_empty_dirs(workdir, conf)
        finally:
            os.chdir(orig_dir)
            proj.close()
            self.remove_if_exists(workdir)
    
    def _run_test_copy_empty_dirs(self, workdir, config):
        output_dir = os.path.join(workdir, 'output')
        context = plugin.GenerationContext(configuration=config, output=output_dir)
        impl_set = plugin.get_impl_set(config)
        impl_set.generate(context)
        
        created_dirs = []
        created_files = []
        def strip(path):
            return path[len(output_dir):].replace('\\', '/').strip('/')
        for root, dirs, files in os.walk(output_dir):
            for d in dirs:  created_dirs.append(strip(os.path.join(root, d)))
            for f in files: created_files.append(strip(os.path.join(root, f)))
        
        self.assertEquals(sorted(created_dirs), sorted(
            ['empty_out',
             'ext_out',
             'ext_out/empty_out',
             'ext_out/foobar_out',
             'ext_out/foobar_out/emptydir',
             'ext_out/foobar_out/emptydir2',
             'ext_out/foobar_out/emptydir2/foo',
             'ext_out/foobar_out_filtered',
             'foobar_out',
             'foobar_out/layer1_emptydir',
             'foobar_out/layer1_emptydir2',
             'foobar_out/layer1_emptydir2/foo',
             'foobar_out/layer2_emptydir',
             'foobar_out_filtered'
             #'foobar_out_filtered/layer1_emptydir',
             #'foobar_out_filtered/layer2_emptydir',
             ]))
        self.assertEquals(sorted(created_files), sorted(
            ['ext_out/foobar_out/x.txt',
             'ext_out/foobar_out_filtered/bar.txt',
             'foobar_out/layer1.txt',
             'foobar_out/layer2.txt',
             'foobar_out_filtered/bar.txt']))

if __name__ == '__main__':
    unittest.main()
