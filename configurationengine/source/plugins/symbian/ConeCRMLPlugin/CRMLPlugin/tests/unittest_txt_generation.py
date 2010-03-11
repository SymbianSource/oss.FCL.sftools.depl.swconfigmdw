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

import sys, os, unittest
import __init__

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

from testautomation.base_testcase import BaseTestCase
from cone.public import exceptions, plugin, api, container

from CRMLPlugin import crml_impl

def abspath(path):
    return os.path.normpath(os.path.join(ROOT_PATH, path))

class TestCrmlImpl(BaseTestCase):

    def test_generate_from_project_with_rfs(self):
        project_dir     = abspath('gen_project')
        config          = 'root.confml'
        output_dir      = abspath('temp/gen_output1')
        expected_dir    = abspath('gen_expected')
        
        self.remove_if_exists(output_dir)
        
        prj = api.Project(api.Storage.open(project_dir))
        config = prj.get_configuration(config)
        impls = plugin.get_impl_set(config, 'crml$')
        impls.output = output_dir
        impls.generation_context.tags['target'] = ['rofs2']
        impls.generate()
        impls.post_generate()
        
        self.assert_dir_contents_equal(output_dir, expected_dir, ['.svn'])
    
    def test_generate_from_project_without_rfs(self):
        project_dir     = abspath('gen_project')
        config          = 'root.confml'
        output_dir      = abspath('temp/gen_output2')
        expected_dir    = abspath('gen_expected')
        
        self.remove_if_exists(output_dir)
        
        prj = api.Project(api.Storage.open(project_dir))
        config = prj.get_configuration(config)
        impls = plugin.get_impl_set(config, 'crml$')
        impls.output = output_dir
        impls.generation_context.tags['target'] = []
        impls.generate()
        impls.post_generate()
        
        self.assert_dir_contents_equal(output_dir, expected_dir, ['.svn', 'private'])
        self.assertFalse(os.path.exists(os.path.join(output_dir, 'private/100059C9/cenrep_rfs.txt')))
    
    
    def test_generate_from_project_duplicate_rfs(self):
        project_dir     = abspath('duplicate_rfs_project')
        config          = 'root.confml'
        output_dir      = abspath('temp/duplicate_rfs_output')
        expected_dir    = abspath('duplicate_rfs_expected')
        
        self.remove_if_exists(output_dir)
        
        prj = api.Project(api.Storage.open(project_dir))
        config = prj.get_configuration(config)
        impls = plugin.get_impl_set(config, 'crml$')
        impls.output = output_dir
        impls.generation_context.tags['target'] = ['rofs2']
        impls.generate()
        impls.post_generate()
        
        self.assert_dir_contents_equal(output_dir, expected_dir, ['.svn'])
    
