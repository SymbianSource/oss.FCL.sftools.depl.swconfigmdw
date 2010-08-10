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

# import __init__
from cone.public import api, plugin
from cone.storage import filestorage
from testautomation.base_testcase import BaseTestCase
from commandplugin.commandml import Command, Condition
from cone.public.api import Configuration

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
testdata  = os.path.join(ROOT_PATH,'project')

class TestParseCommandMl(BaseTestCase):
    def _get_impl_and_set(self, ref):
        fs = filestorage.FileStorage(testdata)
        p = api.Project(fs)
        config = p.get_configuration('product.confml')
        impl_set = plugin.get_impl_set(config, re.escape(ref) + '$')
        self.assertEquals(len(impl_set), 1)
        return iter(impl_set).next(), impl_set
        
    def test_parse_file3(self):
        impl, impl_set = self._get_impl_and_set('file3.commandml')
        self.assertEquals(len(impl[0].reader.elements), 2)
 
        cond1 = impl.impls[0].reader.elements[0]
        cond2 = impl.impls[0].reader.elements[1]
        
        # Create temporary variables
        impl_set.create_temp_features(impl_set.generation_context.configuration)

        self.assertTrue(isinstance(cond1, Condition))
        self.assertTrue(isinstance(cond2, Condition))


        self.assertEquals(True, cond1._solve_condition(cond1.condition, impl_set.generation_context))
        self.assertEquals(False, cond2._solve_condition(cond2.condition, impl_set.generation_context))
        
        
if __name__ == '__main__':
    unittest.main()
