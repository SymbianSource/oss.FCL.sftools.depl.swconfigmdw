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

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

from testautomation.base_testcase import BaseTestCase
from cone.public import exceptions, plugin, api, container, utils

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
        gc = plugin.GenerationContext(configuration=config,
                      output=output_dir)

        impls = plugin.get_impl_set(config, 'crml$')
        gc.tags['target'] = ['rofs2']
        gc.filtering_disabled = True
        impls.generate(gc)
        impls.post_generate(gc)
        
        self.assert_dir_contents_equal(output_dir, expected_dir, ['.svn'])
    
    def test_generate_from_project_without_rfs(self):
        project_dir     = abspath('gen_project')
        config          = 'root.confml'
        output_dir      = abspath('temp/gen_output2')
        expected_dir    = abspath('gen_expected')
        
        self.remove_if_exists(output_dir)
        
        prj = api.Project(api.Storage.open(project_dir))
        config = prj.get_configuration(config)
        gc = plugin.GenerationContext(configuration=config,
                                      output=output_dir)

        impls = plugin.get_impl_set(config, 'crml$')
        gc.tags['target'] = []
        gc.filtering_disabled = True
        impls.generate(gc)
        impls.post_generate(gc)
        
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
        gc = plugin.GenerationContext(configuration=config,
                                      output=output_dir)
        impls = plugin.get_impl_set(config, 'crml$')
        gc.tags['target'] = ['rofs2']
        gc.filtering_disabled = True
        impls.generate(gc)
        impls.post_generate(gc)
        
        self.assert_dir_contents_equal(output_dir, expected_dir, ['.svn'])
    
    def test_generate_delta_cenreps(self):
        project_dir     = abspath('gen_project')
        config          = 'root2.confml'
        output_dir      = abspath('temp/gen_output_deltacenrep')
        expected_dir    = abspath('gen_expected_deltacenrep')
        
        self.remove_if_exists(output_dir)
        
        prj = api.Project(api.Storage.open(project_dir))
        config = prj.get_configuration(config)
        gc = plugin.GenerationContext(configuration=config,
                                      output=output_dir)
        # Get refs from the last layer
        layer = config.get_configuration_by_index(-1)
        refs = utils.distinct_array(layer.list_leaf_datas())
        
        impls = plugin.get_impl_set(config, 'crml$')
        impls = impls | plugin.get_impl_set(config, 'implml$')
        impls = impls.filter_implementations(refs=refs)
        
        gc.tags['crml'] = ['deltacenrep']
        gc.changed_refs = refs
        gc.filtering_disabled = True
        impls.generate(gc)
        impls.post_generate(gc)
        
        output_dir = os.path.join(output_dir, 'deltacenreps')
        self.assert_dir_contents_equal(output_dir, expected_dir, ['.svn'])
