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

from testautomation.base_testcase import BaseTestCase
from cone.public import api
from cone.validation import schemavalidation, implmlvalidation

class TestExamplemlValidation(BaseTestCase):
    
    def _run_test(self, filename):
        filepath = 'Layer1/implml/' + filename
        project_dir = os.path.join(ROOT_PATH, 'testdata/validation/project')
        config      = 'root.confml'
        
        prj = api.Project(api.Storage.open(project_dir))
        config = prj.get_configuration(config)
        problems = implmlvalidation.validate_impls(config, filter=filepath + '$')
        
        self.assert_problem_list_equals_expected(
            actual = problems,
            expected_file = os.path.join(ROOT_PATH, 'testdata/validation/expected', filename + '.txt'),
            outdir = os.path.join(ROOT_PATH, 'temp/validation', filename))
    
    def test_validate_invalid_refs(self):
        self._run_test('invalid_refs.exampleml')
    
    def test_validate_invalid_encoding(self):
        self._run_test('invalid_encoding.exampleml')

class TestExamplemlSchemaValidation(BaseTestCase, schemavalidation.SchemaValidationTestMixin):
    NAMESPACE = 'http://www.example.org/xml/exampleml/1'
    PROBLEM_TYPE = 'schema.implml.exampleml'
    
    def test_schemavalidate_exampleml_valid_files(self):
        self.assert_schemavalidation_succeeds(
            type = 'implml',
            dir = os.path.join(ROOT_PATH, 'testdata/validation/schema/valid'),
            namespace = self.NAMESPACE)
    
    def test_schemavalidate_exampleml_invalid_files(self):
        self.assert_schemavalidation_fails(
            type = 'implml',
            dir = os.path.join(ROOT_PATH, 'testdata/validation/schema/invalid'),
            namespace = self.NAMESPACE,
            problem_type = self.PROBLEM_TYPE)
