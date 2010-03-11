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

import unittest, os, re, subprocess

import __init__
from cone.public import api, plugin
from cone.storage import filestorage
from testautomation.base_testcase import BaseTestCase
from commandplugin.commandml import Command, Condition

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
testdata  = os.path.join(ROOT_PATH,'project')

class TestParseCommandMl(BaseTestCase):
    def _get_impl(self, ref):
        fs = filestorage.FileStorage(testdata)
        p = api.Project(fs)
        config = p.get_configuration('product.confml')
        impl_set = plugin.get_impl_set(config, re.escape(ref) + '$')
        self.assertEquals(len(impl_set), 1)
        return iter(impl_set).next()
    
    def test_parse_file1(self):
        impl = self._get_impl('file1.commandml')
        self.assertEquals(len(impl.reader.elements), 2)
        
        cmd = impl.reader.elements[0]
        self.assertTrue(isinstance(cmd, Command))
        self.assertEquals(cmd.executable, r'c:\program1\run.exe')
        self.assertEquals(cmd.shell, False)
        self.assertEquals(cmd.bufsize, 0)
        self.assertEquals(cmd.cwd, r'c:\program1')
        self.assertEquals(cmd.envs, {'MYVAR': '123'})
        self.assertEquals(cmd.arguments, ['-c some_config.txt',
                                          '-d some_dir',
                                          '-x'])
        self.assertEquals(cmd.pipes, {'stdin':  subprocess.PIPE,
                                      'stdout': 'program1.log'})
        
        cond = impl.reader.elements[1]
        self.assertTrue(isinstance(cond, Condition))
        self.assertEquals(cond.condition, 'False')
        self.assertEquals(len(cond.commands), 1)
        cmd = cond.commands[0]
        self.assertTrue(isinstance(cmd, Command))
        self.assertEquals(cmd.executable, r'c:\program2\abc.exe')
        self.assertEquals(cmd.shell, True)
        self.assertEquals(cmd.bufsize, 0)
        self.assertEquals(cmd.arguments, ['-c some_config.txt'])
        self.assertEquals(cmd.pipes, {})
        
        self.assertEquals(impl.get_tags(), {})
    
    def test_parse_file2(self):
        impl = self._get_impl('file2.commandml')
        self.assertEquals(len(impl.reader.elements), 4)
        
        self.assertTrue(isinstance(impl.reader.elements[0], Condition))
        self.assertTrue(isinstance(impl.reader.elements[1], Condition))
        self.assertTrue(isinstance(impl.reader.elements[2], Command))
        self.assertTrue(isinstance(impl.reader.elements[3], Command))
        
        self.assertEquals(impl.get_tags(), {'target': ['footarget']})
        
if __name__ == '__main__':
    unittest.main()
