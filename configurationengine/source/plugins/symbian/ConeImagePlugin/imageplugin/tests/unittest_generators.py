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
import sys, os

from imageplugin import generators
from cone.public import api, exceptions, plugin, utils
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

def impl_from_resource(resource_ref, configuration):
    impls = plugin.ImplFactory.get_impls_from_file(resource_ref, configuration)
    assert len(impls) == 1
    return impls[0]

class TestGenerator(unittest.TestCase):
    def test_create_generator_with_output(self):
        gen = generators.OutputGenerator('foo/bar')
        self.assertEquals(gen.outputpath,'foo/bar')
        gen.outputpath = 'foo/bar/test.confml'
        self.assertEquals(gen.outputpath,'foo/bar/test.confml')
        del gen.outputpath
        self.assertEquals(gen.outputpath,None)


    def test_generator_subpath_and_path(self):
        gen = generators.OutputGenerator('foo/bar.mbm')
        self.assertEquals(gen.subpath, '')
        gen.subpath = 'test/foo'
        self.assertEquals(gen.subpath, 'test/foo')
        self.assertEquals(gen.path, 'test/foo/foo/bar.mbm')
        self.assertTrue(isinstance(gen.get_command(), generators.BmconvCommand))
        gen.outputpath = 'bar/test.mif'
        self.assertTrue(isinstance(gen.get_command(), generators.MifconvCommand))
        gen.outputpath = 'bar/test.gif'
        self.assertTrue(isinstance(gen.get_command(), generators.CopyCommand))


class TestInputFile(unittest.TestCase):
    def test_create_inputfile(self):
        input = generators.InputFile('foo/bar.bmb')
        self.assertEquals(input.path,'foo/bar.bmb')
        self.assertEquals(input.files[0].filename, 'foo/bar.bmb')
        input.path = 'foo/bar/test.confml'
        self.assertEquals(input.path,'foo/bar/test.confml')
        del input.path
        self.assertEquals(input.path,None)
        

    def test_create_inputfile_with_args(self):
        input = generators.InputFile('foo/bar.bmb',depth="c8",test="juu")
        self.assertEquals(input.path,'foo/bar.bmb')
        self.assertEquals(input.depth,'c8')
        self.assertEquals(input.test,'juu')

class TestInputDir(unittest.TestCase):
    def test_create_inputdir(self):
        dir = generators.InputDir('foo/bar', dir='foo/bar',depth="c8")
        self.assertEquals(dir.path,'foo/bar')
        self.assertEquals(dir.depth,'c8')
        self.assertEquals(dir.files, [])

    def test_create_inputdir_and_get_files(self):
        dir = generators.InputDir('imageproject/variant/content/UI/Start-up Animation')
        dir.include = {'pattern' : 'bmp$'}
        self.assertEquals(dir.files, [])

class TestGeneratorFromProject(unittest.TestCase):
    def test_create_generator_from_project(self):
        prj = api.Project(api.Storage.open(os.path.join(ROOT_PATH,"imageproject")))
        config = prj.get_configuration('product.confml')
        impl = impl_from_resource('variant/implml/startup_animation.imageml', config)
        self.assertEquals(impl.generators[0].outputpath, 'startup.mbm')
        self.assertEquals(impl.generators[0].configuration, config)
        self.assertEquals(impl.generators[0].palette, '../bin/ThirdPartyBitmap.pal')
        self.assertEquals(impl.generators[0].inputs[0].configuration, config)
        self.assertEquals(impl.generators[0].inputs[0].path, 'UI/Start-up Animation')
        self.assertEquals(impl.generators[0].inputs[0].type, 'dir')
        self.assertEquals(impl.generators[1].outputpath, 'nocompress.mbm')
        self.assertEquals(impl.generators[1].get_command().compress, False)
        self.assertEquals(impl.generators[1].inputs[0].configuration, config)
        self.assertEquals(impl.generators[1].inputs[0].path, 'UI/Start-up Animation')
        self.assertEquals(impl.generators[1].inputs[0].type, 'dir')
        self.assertEquals(len(impl.generators[1].inputs[0].files),20)
        self.assertEquals(impl.generators[1].inputs[0].files[0].filename,'variant/content/UI/Start-up Animation/frame01.bmp')
        self.assertEquals(impl.generators[1].inputs[0].files[0].path,'UI/Start-up Animation/frame01.bmp')
        self.assertEquals(impl.generators[1].inputs[0].files[0].depth,'c8')
        self.assertEquals(impl.generators[1].inputs[0].files[19].filename,'variant/content/UI/Start-up Animation/frame20.bmp')
        self.assertEquals(impl.generators[1].inputs[0].files[19].depth,'c8')
    
    def test_create_generator_with_configurable_depth_from_project(self):
        prj = api.Project(api.Storage.open(os.path.join(ROOT_PATH,"imageproject")))
        config = prj.get_configuration('product.confml')
        impl = impl_from_resource('variant/implml/depth_from_ref_test.imageml', config)
        self.assertEquals(impl.generators[0].inputs[0].depth, 'c16')
        self.assertEquals(impl.generators[1].inputs[0].depth, 'c16')
        
        # Assert the the depth is actually used in the command
        command_obj = impl.generators[0].get_command()
        cmd = command_obj.get_command(command_obj._get_filtered_input_files())
        self.assertEquals(len(cmd), 4)
        self.assertEquals(cmd[3], r'/c16conversion_workdir\frame01.bmp')
        
        command_obj = impl.generators[1].get_command()
        cmd = command_obj.get_command(command_obj._get_filtered_input_files())
        self.assertEquals(len(cmd), 5)
        self.assertEquals(cmd[3], '/c16')
        self.assertEquals(cmd[4], r'conversion_workdir\icon.svg')

    def test_create_generator_with_extraparams(self):
        prj = api.Project(api.Storage.open(os.path.join(ROOT_PATH,"imageproject")))
        config = prj.get_configuration('product.confml')
        dview = config.get_default_view()
        impl = impl_from_resource('variant/implml/startupmif_animation_with_version.imageml', config)
        
        # 1st impl
        self.assertEquals(impl.generators[0].extraparams, '/V3')
        
        # Assert the the extraparams is actually used in the command
        command_obj = impl.generators[0].get_command()
        cmd = command_obj.get_command(command_obj._get_filtered_input_files())
        self.assertEquals(len(cmd), 6)
        self.assertEquals(cmd[2], r'/V3')
        
        # 2nd impl
        self.assertEquals(impl.generators[1].extraparams, '${StartupSettings.PluginTimeout}')
        self.assertEquals(utils.expand_refs_by_default_view(impl.generators[1].extraparams, dview), '30000')
        
        # Assert the the extraparams is actually used in the command
        command_obj = impl.generators[1].get_command()
        cmd = command_obj.get_command(command_obj._get_filtered_input_files())
        self.assertEquals(len(cmd), 6)
        self.assertEquals(cmd[2], r'30000')
        
        # 3rd impl
        self.assertEquals(impl.generators[2].extraparams, '${StartupSettings.PluginTimeout}')
        self.assertEquals(utils.expand_refs_by_default_view(impl.generators[1].extraparams, dview), '30000')
        
        # Assert the the extraparams is actually used in the command
        command_obj = impl.generators[2].get_command()
        cmd = command_obj.get_command(command_obj._get_filtered_input_files())
        self.assertEquals(len(cmd), 4)
        self.assertEquals(cmd[1], r'30000')
        
    
    def test_create_generator_with_invalid_output(self):
        prj = api.Project(api.Storage.open(os.path.join(ROOT_PATH,"imageproject")))
        config = prj.get_configuration('product.confml')
        impl = impl_from_resource('variant/implml/startup_animation.imageml', config)
        impl.generators[0].outputpath = '${KCRUidStartup.StartupOperatorAnimationPath}'
        try:
            self.assertEquals(impl.generators[0].outputpath, '${KCRUidStartup.StartupOperatorAnimationPath}')
            self.fail("Output path value should be none")
        except exceptions.NotFound:
            pass

        try:
            self.assertEquals(impl.generators[0].outputpath, '${KCRUidStartup.foobar}')
            self.fail("Output path ref is invalid!")
        except exceptions.NotFound:
            pass

# Only run these tests on Windows
if sys.platform != 'win32':
    del TestGenerator
    del TestInputFile
    del TestInputDir
    del TestGeneratorFromProject

if __name__ == '__main__':
    unittest.main()
