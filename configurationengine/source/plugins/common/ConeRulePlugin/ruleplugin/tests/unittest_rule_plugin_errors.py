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

import unittest
import os, shutil
import sys
import logging

from cone.public import exceptions,plugin,api,container
from cone.storage import filestorage
from ruleplugin import ruleml
from testautomation.base_testcase import BaseTestCase

# Hardcoded value of testdata folder that must be under the current working dir
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
testdata  = os.path.join(ROOT_PATH,'errorruleproject')

class TestErrorReporting(BaseTestCase):
    def setUp(self):
        pass
      
    def tearDown(self):
        pass
    
    def _prepare_workdir(self, workdir):
        workdir = os.path.join(ROOT_PATH, workdir)
        self.recreate_dir(workdir)
        return workdir

    def _prepare_log(self, log_file, level=logging.DEBUG, formatter="%(levelname)s - %(name)s - %(message)s", logger='cone'):
        FULL_PATH = os.path.join(ROOT_PATH, "temp", log_file)
        self.remove_if_exists(FULL_PATH)
        self.create_dir_for_file_path(FULL_PATH)
        
        handler = logging.FileHandler(FULL_PATH)
        handler.setLevel(level)
        frm = logging.Formatter(formatter)
        handler.setFormatter(frm)
        logger = logging.getLogger(logger)
        logger.addHandler(handler)
        
        return [FULL_PATH, handler, logger]
    
    def _execute_rules(self, project_location):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH, project_location)))
        config = project.get_configuration('root.confml')
        context = plugin.GenerationContext(configuration=config)
        implcontainer = plugin.get_impl_set(config, r'\.ruleml$')
        implcontainer.get_relation_container().execute(context)
        lastconfig = config.get_last_configuration()
        project.close()
    
    def test_terminal_expression_repr(self):
        log_file, handler, logger = self._prepare_log('test1.log')
        self._execute_rules('errorruleproject/test1')
        logger.removeHandler(handler)
        
        self.assert_file_does_not_contain(log_file, "<cone.public.rules.TerminalExpression object at")

    def test_invalid_python_code_eval(self):
        log_file, handler, logger = self._prepare_log('test2.log')
        self._execute_rules('errorruleproject/test2')
        logger.removeHandler(handler)
        self.assert_file_contains(log_file, "WARNING - cone.ruleml - Invalid syntax in eval: -> this is invalid python code")

    def test_invalid_python_code_eval_globals(self):
        log_file, handler, logger = self._prepare_log('test3.log')
        self._execute_rules('errorruleproject/test3')
        logger.removeHandler(handler)
        self.assert_file_contains(log_file, "WARNING - cone.ruleml(implml/invalid_python_eval.ruleml) - Cannot import eval file: implml/scripts/test_eval.py. Exception: invalid syntax (<string>, line 17)")
        
    def test_invalid_file_reference_in_eval_globals_file_attribute(self):
        log_file, handler, logger = self._prepare_log('test4.log')
        self._execute_rules('errorruleproject/test4')
        logger.removeHandler(handler)
        self.assert_file_contains(log_file, "WARNING - cone.ruleml(implml/invalid_python_eval.ruleml) - Cannot import eval file: implml/scripts/not_valid_filename.py. Exception: implml/scripts/not_valid_filename.py, [Errno 2] No such file or directory:")
        self.assert_file_contains(log_file, '/implml/scripts/not_valid_filename.py')
    
    def test_runtime_error_when_running_an_eval_block_inside_rule(self):
        log_file, handler, logger = self._prepare_log('test5.log')
        self._execute_rules('errorruleproject/test5')
        logger.removeHandler(handler)
        
        self.assert_file_contains(log_file, "Execution failed for eval: 7/0 <type 'exceptions.ZeroDivisionError'>: integer division or modulo by zero")

    def test_references_non_existent_settings(self):
        log_file, handler, logger = self._prepare_log('test6.log')
        self._execute_rules('errorruleproject/test6')
        logger.removeHandler(handler)
        #self.assert_file_contains(log_file, "Execution failed for eval: 7/0 <type 'exceptions.ZeroDivisionError'>: integer division or modulo by zero")

    
if __name__ == '__main__':
    unittest.main()
