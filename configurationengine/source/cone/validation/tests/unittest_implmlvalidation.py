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
import __init__

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
TESTDATA_DIR = os.path.join(ROOT_PATH, 'testdata')
TEMP_DIR = os.path.join(ROOT_PATH, 'temp')

from testautomation.base_testcase import BaseTestCase
from cone.public import api
import cone.validation.implmlvalidation

class TestImplmlValidation(BaseTestCase):
    
    def _run_test(self, filename):
        filepath = 'Layer1/implml/' + filename
        project_dir = os.path.join(ROOT_PATH, 'testdata/model/implml/project')
        config      = 'root.confml'
        
        prj = api.Project(api.Storage.open(project_dir))
        config = prj.get_configuration(config)
        problems = cone.validation.implmlvalidation.validate_impls(config, filter=filepath + '$')
        
        self.assert_problem_list_equals_expected(
            actual = problems,
            expected_file = os.path.join(ROOT_PATH, 'testdata/model/implml/expected', filename + '.txt'),
            outdir = os.path.join(ROOT_PATH, 'temp/implml_model', filename))
    
    def test_validate_duplicate_tempvar_refs(self):
        self._run_test('duplicate_tempvar_ref.implml')
    