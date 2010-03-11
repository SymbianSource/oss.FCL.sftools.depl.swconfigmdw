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

import os, unittest
import __init__

from hcrplugin.hcrrepository import HcrRepository, HcrRecord
from hcrplugin.hcr_writer import HcrWriter
from hcrplugin import hcr_exceptions
from cone.public import api, plugin
from testautomation.base_testcase import BaseTestCase


ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class TestHCRMLWrite(BaseTestCase):
    def _run_generate_test(self, project_dir, output_dir, expected_dir, hcrml_file):
        project_dir = os.path.join(ROOT_PATH, project_dir)
        output_dir = os.path.join(ROOT_PATH, output_dir)
        if expected_dir != None:
            expected_dir = os.path.join(ROOT_PATH, expected_dir)
        
        self.remove_if_exists(output_dir)
        
        prj = api.Project(api.Storage.open(project_dir))
        config = prj.get_configuration('root.confml')
        impls = plugin.ImplFactory.get_impls_from_file(hcrml_file, config)
        self.assertEquals(len(impls), 1)
        impl = impls[0]
        impl.set_output_root(output_dir)
        impl.generate()
        
        if expected_dir != None:
            self.assert_dir_contents_equal(expected_dir, output_dir, ['.svn'])
        else:
            self.assertFalse(os.path.exists(output_dir))
    
    def test_create_hcr_dat_from_single_hcrml_file(self):
        self._run_generate_test(
            project_dir     = 'project',
            output_dir      = 'output/single_dat',
            expected_dir    = 'expected/single_dat',
            hcrml_file      = 'implml/example.hcrml')
    
    def test_create_hcr_dat_from_multiple_hcrml_files(self):
        self._run_generate_test(
            project_dir     = 'multifile_project',
            output_dir      = 'output/multi_dat',
            expected_dir    = 'expected/multi_dat',
            hcrml_file      = 'layer1/implml/hcr_dat.hcrml')
    
    def test_create_header_from_single_hcrml_file(self):
        self._run_generate_test(
            project_dir     = 'multifile_project',
            output_dir      = 'output/single_header',
            expected_dir    = 'expected/single_header',
            hcrml_file      = 'layer1/implml/test1.hcrml')
    
    def test_create_header_from_multiple_hcrml_files(self):
        self._run_generate_test(
            project_dir     = 'multifile_project',
            output_dir      = 'output/multi_header',
            expected_dir    = 'expected/multi_header',
            hcrml_file      = 'layer1/implml/multi_header.hcrml')
    
    def test_create_nothing_from_outputless_hcrml_file(self):
        self._run_generate_test(
            project_dir     = 'multifile_project',
            output_dir      = 'output/no_output',
            expected_dir    = None, # Check that there is no output
            hcrml_file      = 'layer1/implml/test3.hcrml')
