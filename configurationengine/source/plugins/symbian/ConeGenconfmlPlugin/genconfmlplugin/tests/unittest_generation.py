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

def abspath(path):
    return os.path.normpath(os.path.join(ROOT_PATH, path))

class TestGenconfmlGeneration(BaseTestCase):
    
    def test_generate_gcfml_layer1(self): self._run_gen_test(1)
    def test_generate_gcfml_layer2(self): self._run_gen_test(2)
    # Related to the ignored file, see ticket #160: Sequence items with extension policy prefix are reversed
    def test_generate_gcfml_layer3(self): self._run_gen_test(3, ignores=['feature2.txt'])
    def test_generate_gcfml_layer4(self): self._run_gen_test(4)
    
    def _run_gen_test(self, layer, ignores=[]):
        project_dir     = abspath('project')
        config          = 'root%s.confml' % layer
        output_dir      = abspath('temp/gen_output%s' % layer)
        expected_dir    = abspath('expected/root%s' % layer)
        
        self.remove_if_exists(output_dir)
        
        prj = api.Project(api.Storage.open(project_dir))
        config = prj.get_configuration(config)
        impls = plugin.get_impl_set(config, 'gcfml$')
        impls.output = output_dir
        impls.generate()
        
        self.assert_dir_contents_equal(output_dir, expected_dir, ['.svn'] + ignores)
