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
import cone.validation.implmlvalidation

class TestCrmlValidation(BaseTestCase):
    
    def _run_test(self, filename):
        filepath = 'Layer1/implml/' + filename
        project_dir = os.path.join(ROOT_PATH, 'validation_project')
        config      = 'root.confml'
        
        prj = api.Project(api.Storage.open(project_dir))
        config = prj.get_configuration(config)
        problems = cone.validation.implmlvalidation.validate_impls(config, filter=filepath + '$')
        
        self.assert_problem_list_equals_expected(
            actual = problems,
            expected_file = os.path.join(ROOT_PATH, 'validation_expected', filename + '.txt'),
            outdir = os.path.join(ROOT_PATH, 'temp/validation', filename))
    
    def test_validate_invalid_refs(self):
        self._run_test('00000002_invalid_refs.crml')
    
    def test_validate_duplicate_uids(self):
        self._run_test('00000003_duplicate_uids.crml')
