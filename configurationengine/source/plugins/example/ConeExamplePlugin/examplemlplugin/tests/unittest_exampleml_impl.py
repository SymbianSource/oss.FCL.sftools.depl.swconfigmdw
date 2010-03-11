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

import sys, os, unittest
import __init__

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

from cone.public import plugin, api
from examplemlplugin.exampleml_reader import ExamplemlReader
from examplemlplugin.exampleml_model import Output

class TestExamplemlImpl(unittest.TestCase):

    def setUp(self):
        project_dir = os.path.join(ROOT_PATH, 'project')
        self.project = api.Project(api.Storage.open(project_dir))
        self.config = self.project.get_configuration('root.confml')
    
    def get_impl(self, ref, index):
        impl_list = plugin.ImplFactory.get_impls_from_file(ref, self.config)
        return impl_list[index]
    
    def test_has_ref(self):
        impl = self.get_impl('Layer/implml/test.exampleml', 0)
        self.assertTrue(impl.has_ref(['TestFeature.Value1']))
        self.assertFalse(impl.has_ref(['TestFeature.Foo']))
        self.assertFalse(impl.has_ref(['Foo.Bar']))
    
    def test_list_output_files(self):
        def oj( p2): # oj = output_join
            return os.path.normpath(os.path.join('output', p2))
        
        impl = self.get_impl('Layer/implml/test.exampleml', 0)
        self.assertEquals(impl.list_output_files(), [oj('test.txt'),
                                                     oj('some/dir/out1.txt'),
                                                     oj('some/dir2/out2.txt')])
        
        impl = self.get_impl('Layer/implml/multitest.implml', 0)
        self.assertEquals(impl[0].list_output_files(), [oj('multitest1_1.txt'),
                                                     oj('multitest1_2.txt')])
        
        impl = self.get_impl('Layer/implml/multitest.implml', 0)
        self.assertEquals(impl[1].list_output_files(), [oj('multitest2_1.txt'),
                                                     oj('multitest2_2.txt')])
