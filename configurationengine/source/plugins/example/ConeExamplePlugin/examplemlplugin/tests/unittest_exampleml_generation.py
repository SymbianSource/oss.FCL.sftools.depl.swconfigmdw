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

import os

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

from testautomation.base_testcase import BaseTestCase
from cone.public import plugin, api


def abspath(path):
    return os.path.normpath(os.path.join(ROOT_PATH, path))

class TestExamplemlGeneration(BaseTestCase):

    def test_generate_from_project(self):
        project_dir     = abspath('testdata/generation/project')
        config          = 'root.confml'
        output_dir      = abspath('temp/generation/output')
        expected_dir    = abspath('testdata/generation/expected')
        
        self.remove_if_exists(output_dir)
        
        prj = api.Project(api.Storage.open(project_dir))
        config = prj.get_configuration(config)
        context = plugin.GenerationContext(configuration=config, 
                                           output=output_dir)
        impls = plugin.get_impl_set(config)
        impls.generate(context)
        
        self.assert_dir_contents_equal(output_dir, expected_dir, ['.svn'])
        