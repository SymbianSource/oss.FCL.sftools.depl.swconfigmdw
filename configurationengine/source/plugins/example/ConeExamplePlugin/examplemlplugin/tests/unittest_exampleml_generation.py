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

from examplemlplugin import exampleml_reader

def abspath(path):
    return os.path.normpath(os.path.join(ROOT_PATH, path))

class TestExamplemlGeneration(BaseTestCase):

    def test_generate_from_project(self):
        project_dir     = abspath('project')
        config          = 'root.confml'
        output_dir      = abspath('temp/output')
        expected_dir    = abspath('gen_expected')
        
        self.remove_if_exists(output_dir)
        
        prj = api.Project(api.Storage.open(project_dir))
        config = prj.get_configuration(config)
        impls = plugin.get_impl_set(config)
        impls.output = output_dir
        impls.generate()
        
        self.assert_dir_contents_equal(output_dir, expected_dir, ['.svn'])
        