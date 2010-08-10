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
import sys, os, re

from cone.public import plugin,api
from testautomation.base_testcase import BaseTestCase

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
testdata  = os.path.join(ROOT_PATH,'imageproject')

class TestGeneratorFromProject(BaseTestCase):
    def test_create_generator_from_project_and_generate_all(self):
        orig_workdir = os.getcwd()
        os.chdir(ROOT_PATH)
        try:
            output = os.path.join(ROOT_PATH, "temp/output_all")
            self.recreate_dir(output)
            
            prj = api.Project(api.Storage.open(os.path.join(ROOT_PATH,"imageproject")))
            config = prj.get_configuration('product.confml')
            context = plugin.GenerationContext(configuration=config, output=output)
            context.filtering_disabled = True
            
            impl_set = plugin.get_impl_set(config, 'imageml$')
            self.assertEquals(len(impl_set), 5)
            impl_set.generate(context)
            
            def check_gen(p):
                self.assert_exists_and_contains_something(os.path.join(output, p))
            def check_not_gen(p):
                self.assertFalse(os.path.exists(os.path.join(output, p)), "'%s' exists when it should not!" % p)
            
            try:
                check_gen('startup.mbm')
                check_gen('startup_mif.mif')
                
                check_not_gen('optional1_mbm.mbm')
                check_gen('optional2_mbm.mbm')
                check_not_gen('optional3_mbm.mbm')
                check_not_gen('optional4_mbm.mbm')
                
                check_not_gen('optional1_mif.mif')
                check_gen('optional2_mif.mif')
                check_not_gen('optional3_mif.mif')
                check_not_gen('optional4_mif.mif')
                
                check_gen('resource/apps/startup.mif')
                
                check_gen('depth_from_ref_test_mbm.mbm')
                check_gen('depth_from_ref_test_mif.mif')
            except AssertionError, e:
                if ' ' in ROOT_PATH:
                    self.fail("Known bug (#177): %s" % e)
                else:
                    raise
        finally:
            os.chdir(orig_workdir)
    
    def _get_impl(self, filename):
        prj = api.Project(api.Storage.open(os.path.join(ROOT_PATH, "imageproject")))
        config = prj.get_configuration('product.confml')
        implcontainer = plugin.get_impl_set(config, re.escape(filename) + '$')
        self.assertEquals(len(implcontainer), 1)
        return iter(implcontainer).next()
        
    
    def test_get_refs(self):
        impl = self._get_impl('startupmif_animation.imageml')
        self.assertEquals(impl.get_refs(), None)
        self.assertEquals(impl.has_ref('Foo.Bar'), None)
        
        impl = self._get_impl('optional_test.imageml')
        self.assertEquals(impl.get_refs(), ['OptionalTest.EmptyString',
                                            'OptionalTest.EmptyString2'])
        self.assertEquals(impl.has_ref('OptionalTest.EmptyString'), True)
        self.assertEquals(impl.has_ref('Foo.Foo'), False)
        
        impl = self._get_impl('startup_animation.imageml')
        self.assertEquals(impl.get_refs(), ['CVC_StartupAnimationSequence.CVC_StartupFrameLocation.localPath'])
        self.assertEquals(impl.has_ref('CVC_StartupAnimationSequence.CVC_StartupFrameLocation.localPath'), True)
        self.assertEquals(impl.has_ref('Foo.Foo'), False)

# Only run these tests on Windows
if sys.platform != 'win32':
    del TestGeneratorFromProject

if __name__ == '__main__':
    unittest.main()
