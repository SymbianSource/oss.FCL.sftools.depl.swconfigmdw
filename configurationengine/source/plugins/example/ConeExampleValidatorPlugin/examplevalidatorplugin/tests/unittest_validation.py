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
from cone.public import api
from cone.validation import confmlvalidation

class TestExampleValidatorValidation(BaseTestCase):
    
    def test_validate(self):
        project_dir = os.path.join(ROOT_PATH, 'testdata')
        config      = 'test.confml'
        
        prj = api.Project(api.Storage.open(project_dir))
        config = prj.get_configuration(config)
        problems = confmlvalidation.validate_configuration(config).problems
        
        self.assert_problem_list_equals_expected(
            actual = problems,
            expected_file = os.path.join(ROOT_PATH, 'testdata/expected.txt'),
            outdir = os.path.join(ROOT_PATH, 'temp'))
