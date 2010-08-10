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
import unittest
import logging

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
TESTDATA_DIR = os.path.join(ROOT_PATH, 'testdata')
TEMP_DIR = os.path.join(ROOT_PATH, 'temp')

from testautomation.base_testcase import BaseTestCase
from cone.public import api
import cone.validation.confmlvalidation


class TestConfmlValidation(BaseTestCase):
        
    def _run_single_file_test(self, filename):
        # Open the file as a configuration
        prj_dir = os.path.join(TESTDATA_DIR, 'model/confml/single_files')
        prj = api.Project(api.Storage.open(prj_dir))
        conf = prj.get_configuration(filename)
        
        self.assert_problem_list_equals_expected(
            actual = cone.validation.confmlvalidation.validate_configuration(conf).problems,
            expected_file = os.path.join(TESTDATA_DIR, 'model/confml/single_files_expected', filename + '.txt'),
            outdir = os.path.join(TEMP_DIR, 'confml_model_single_files', filename))
    
    def test_validate_min_max_length(self):
        self._run_single_file_test('min_max_length.confml')
    
    def test_validate_data_without_feature(self):
        self._run_single_file_test('data_without_feature.confml')

    def test_validate_duplicates(self):
        self._run_single_file_test('duplicate_root.confml')
    