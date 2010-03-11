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

"""
Test the configuration
"""
import unittest
import string
import sys
import os
import subprocess
import __init__
from testautomation.base_testcase import BaseTestCase
from scripttest_common import get_cmd

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class TestConeHelp(BaseTestCase):    

    def test_get_help(self):
        cmd = '%s -h' % get_cmd('')
        out = self.run_command(cmd)
        lines = out.split(os.linesep)
        self.assertTrue('Available actions ' in lines)
    
    def test_verbose_level(self):
        cmd = '%s info --print-runtime-info --verbose=5' % get_cmd('')
        out = self.run_command(cmd)
        # Check that there are debug messages in the output
        self.assertTrue('DEBUG   : cone' in out)
        self.assertTrue('sys.path contents:' in out)
    
    def test_empty_verbose_level(self):
        cmd = '%s info --print-runtime-info --verbose=' % get_cmd('')
        out = self.run_command(cmd)
        self.assertTrue('Python version: ' in out)
    
    def test_runtime_info_logged(self):
        # This test makes sure that runtime info is always logged
        # in the log file
        
        TEST_DIR = os.path.join(ROOT_PATH, "temp", "log_test")
        self.recreate_dir(TEST_DIR)
        
        orig_workdir = os.getcwd()
        os.chdir(TEST_DIR)
        try:
            cmd = '%s' % get_cmd('info')
            self.run_command(cmd)
            
            # Check that the default log file has been created
            self.assertTrue(os.path.exists('cone.log'))
            
            # Check that it contains the runtime info that should
            # always be logged
            f = open('cone.log', 'r')
            try:        data = f.read()
            finally:    f.close()
            self.assertTrue('DEBUG   : cone' in data)
            self.assertTrue('sys.path contents:' in data)
            self.assertTrue('PATH:' in data)
            self.assertTrue('PYTHONPATH:' in data)
        finally:
            os.chdir(orig_workdir)
    
    def test_logfile_in_custom_location(self):
        TEST_DIR = os.path.join(ROOT_PATH, "temp", "log_test_custom_file")
        self.recreate_dir(TEST_DIR)
        
        orig_workdir = os.getcwd()
        os.chdir(TEST_DIR)
        try:
            cmd = '%s --log-file foo/bar.log' % get_cmd('info')
            self.run_command(cmd)
            
            self.assertFalse(os.path.exists('cone.log'))
            self.assertTrue(os.path.exists('foo/bar.log'))
        finally:
            os.chdir(orig_workdir)
    
    def test_custom_log_config(self):
        CONF_FILE = os.path.join(ROOT_PATH, 'testdata', 'log_config.ini')
        cmd = '%s --log-config "%s"' % (get_cmd('info'), CONF_FILE)
        out = self.run_command(cmd)
        self.assertTrue("Level:DEBUG, Logger:cone, Message:sys.path contents:" in out, out)

if __name__ == '__main__':
      unittest.main()
      
