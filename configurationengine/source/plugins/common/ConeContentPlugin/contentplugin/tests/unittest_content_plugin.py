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
from contentplugin import contentml

# Hardcoded value of testdata folder that must be under the current working dir
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
testdata  = os.path.join(ROOT_PATH,'contentproject')


class TestContentPlugin(unittest.TestCase):
	    
    def test_create_copy_list_from_datacontainer_with_test(self):
        '''
        Test that the loading of the plugins works
        '''
        data = container.DataContainer()
        data.add_value('test/test.txt','/foo/content/test/test.txt')
        data.add_value('test/test.txt','/bar/content/test/test.txt')
        data.add_value('product/aaa.txt','/foo/content/product/aaa.txt')
        data.add_value('images/kuva.jpg','/foo/content/images/kuva.jpg')
        data.add_value('include/hide.iby','/bar/content/include/hide.iby')
        impl = contentml.ContentImpl("foo",None)
        copylist = impl.create_copy_list(content=data, input='test',output='content')
        self.assertEquals(copylist[0][1],'content/test.txt')

    def test_create_copy_list_from_datacontainer_with_defauls(self):
        '''
        Test that the loading of the plugins works
        '''
        data = container.DataContainer()
        data.add_value('test/test.txt','/foo/content/test/test.txt')
        data.add_value('test/test.txt','/bar/content/test/test.txt')
        data.add_value('product/aaa.txt','/foo/content/product/aaa.txt')
        data.add_value('images/kuva.jpg','/foo/content/images/kuva.jpg')
        data.add_value('include/hide.iby','/bar/content/include/hide.iby')
        impl = contentml.ContentImpl("foo",None)
        copylist = impl.create_copy_list(content=data)
        self.assertEquals(copylist[0][0],'/bar/content/test/test.txt')
        self.assertEquals(copylist[0][1],'test/test.txt')
        self.assertEquals(copylist[1][0],'/bar/content/include/hide.iby')
        self.assertEquals(copylist[1][1],'include/hide.iby')

    def test_create_copy_list_from_datacontainer_with_filters(self):
        '''
        Test that the loading of the plugins works
        '''
        data = container.DataContainer()
        data.add_value('test/test.txt','/foo/content/test/test.txt')
        data.add_value('test/test.txt','/bar/content/test/test.txt')
        data.add_value('product/aaa.txt','/foo/content/product/aaa.txt')
        data.add_value('images/kuva.jpg','/foo/content/images/kuva.jpg')
        data.add_value('include/hide.iby','/bar/content/include/hide.iby')
        impl = contentml.ContentImpl("foo",None)
        copylist = impl.create_copy_list(content=data,input='include',include_filter='*.iby')
        self.assertEquals(copylist[0][0],'/bar/content/include/hide.iby')
        self.assertEquals(copylist[0][1],'hide.iby')

class TestContentPluginOnFileStorage(unittest.TestCase):    
    def setUp(self):
        self.curdir = os.getcwd()
        self.output = 'output'
        self.workdir = 'workdir'
        if not os.path.exists(self.workdir):
            os.mkdir(self.workdir)
        os.chdir(self.workdir)
        pass

    def tearDown(self):
    	os.chdir(self.curdir)
        if os.path.exists(self.workdir):
            shutil.rmtree(self.workdir)
            pass

    def load_config(self, config='product.confml'):
        fs = filestorage.FileStorage(testdata)
        p = api.Project(fs)
        return p.get_configuration(config)
    
    def load_impl(self, resource_ref, config='product.confml'):
        configuration = self.load_config(config)
        impls = plugin.ImplFactory.get_impls_from_file(resource_ref, configuration)
        self.assertEquals(len(impls), 1)
        impl = impls[0]
        return impl

    def test_configuration_parse_resource(self):
        impl = self.load_impl('assets/s60/implml/test_filter_both.content')
        self.assertEquals(impl.outputs[0].dir,'content')
        self.assertEquals(impl.outputs[0].inputs[0].include,{'pattern': ['prod']})
        self.assertEquals(impl.outputs[0].inputs[0].exclude,{'pattern': ['.svn']})
        self.assertEquals(impl.get_tags(), {'target': ['rofs3', 'uda']})
        self.assertEquals(impl.has_tag({'target':['rofs3']}), True)


    def test_configuration_parse_content2(self):
        impl = self.load_impl('assets/s60/implml/content2_with_tags.content')
        self.assertEquals(impl.outputs[0].dir,'content')
        self.assertEquals(impl.outputs[0].inputs[0].include,{'files': ['test/override.txt, test/s60.txt']})
        self.assertEquals(impl.get_tags(), {'target': ['rofs3', 'uda']})
        self.assertEquals(impl.has_tag({'target':['rofs3']}), True)

    def test_configuration_parse_content2_with_tag_refs(self):
        impl = self.load_impl('assets/s60/implml/content2_with_tags_refs.content')
        self.assertEquals(impl.get_tags(), {'target': ['rofs3']})
        self.assertEquals(impl.has_tag({'target':['rofs3']}), True)

    def test_configuration_parse_and_filter_implementation_with_tags(self):
        fs = filestorage.FileStorage(testdata)
        p = api.Project(fs)
        config = p.get_configuration('product.confml')
        impls = plugin.get_impl_set(config,'\.content$')
        impls_rofs3 = impls.filter_implementations(tags={'target':['rofs3']})
        self.assertEquals(len(list(impls_rofs3)),3)
        
    def test_configuration_parse_content_with_include_files(self):
        impl = self.load_impl('assets/s60/implml/copy_files.content')
        self.assertEquals(impl.outputs[0].inputs[0].include['files'],['test/override.txt, test/s60.txt'])

    def test_configuration_content_get_full_copy_list(self):
        impl = self.load_impl('assets/s60/implml/copy_files.content')
        files = impl.get_full_copy_list()
        self.assertEquals(files,
            [('assets/s60/content/test/s60.txt', 'content/test/s60.txt', False),
             ('family/content/test/override.txt', 'content/test/override.txt', False)])

    def test_configuration_content_list_output_files(self):
        config = self.load_config()
        impls = plugin.get_impl_set(config,'\.content$')
        files = impls.list_output_files()
        self.assertTrue('content/test/override.txt' in files)

    def test_configuration_content_list_output_files_with_refs_filter(self):
        impl = self.load_impl('assets/s60/implml/test_content_with_sequence_refs.content')
        files = impl.list_output_files()
        self.assertEquals(files[0],'content/override.txt')

    def test_configuration_content_list_output_files_with_exclude_filter(self):
        impl = self.load_impl('assets/s60/implml/test_filter_both.content')
        files = impl.list_output_files()
        self.assertEquals(files[0],'content/prodX/jee/ProdX_specific.txt')
#
    def test_configuration_get_input_with_ref(self):
        impl = self.load_impl('assets/s60/implml/test_content_with_refs.content')
        self.assertEquals(impl.outputs[0].dir, 'content')
        self.assertEquals(impl.outputs[0].inputs[0].dir, 'content')

    def test_configuration_get_include_with_refs(self):
        impl = self.load_impl('assets/s60/implml/test_content_with_sequence_refs.content')
        self.assertEquals(impl.outputs[0].inputs[0].include['files'], ['test/override.txt'])
        self.assertEquals(impl.list_output_files(), ['content/override.txt'])

    def test_configuration_get_include_with_refs2(self):
        impl = self.load_impl('assets/s60/implml/copy.content')
        expected = ['content/prodX/jee/ProdX_specific.txt', 
                    'content/test/shout.txt', 
                    'content/test/override.txt', 
                    'content/test/s60.txt',
                    'content/test/test_CAP_letters.txt',
                    'content/wallpapers/wallpaper1.png',
                    'content/wallpapers/wallpaper2.png',
                    'content/wallpapers/wallpaper3.png']
        actual = impl.list_output_files()
        self.assertEquals(sorted(actual), sorted(expected))

    def test_configuration_content_create_output(self):
        impl = self.load_impl('assets/s60/implml/copy.content')
        impl.logger.setLevel(logging.DEBUG)
        impl.create_output()
        self.assertTrue(os.path.exists(os.path.join(self.output,'content/prodX/jee/ProdX_specific.txt')))

    def test_configuration_content_generate(self):
        config = self.load_config()
        impls = plugin.get_impl_set(config,'\.content$')
        context = plugin.GenerationContext(output=self.output)
        results = impls.generate(context)
        self.assertTrue(os.path.exists(impls.output))
        self.assertTrue(os.path.exists(os.path.join(context.output,'content/prodX/jee/ProdX_specific.txt')))

    def test_configuration_content_generate_with_include_refs(self):
        impl = self.load_impl('assets/s60/implml/test_content_with_sequence_refs.content')
        context = plugin.GenerationContext(output=self.output)
        results = impl.generate(context)
        self.assertTrue(os.path.exists(os.path.join(context.output,'content/override.txt')))

    def test_configuration_content_generate_with_external_input(self):
        impl = self.load_impl('assets/s60/implml/test_external_input.content')
        context = plugin.GenerationContext(output=self.output)
        results = impl.generate(context)
        self.assertTrue(os.path.exists(os.path.join(context.output,'content_external/abc.txt')))
        self.assertTrue(os.path.exists(os.path.join(context.output,'content_external/folder1/data.txt')))
        self.assertTrue(os.path.exists(os.path.join(context.output,'content_external2/folder2/setting.txt')))

    def test_configuration_content_generate_with_multi_output(self):
        impl = self.load_impl('assets/s60/implml/content2_with_multi_outputs.content')
        context = plugin.GenerationContext(output=self.output)
        results = impl.generate(context)
        self.assertTrue(os.path.exists(os.path.join(context.output,'content/test/override.txt')))
        self.assertTrue(os.path.exists(os.path.join(context.output,'include/s60.txt')))

    def test_configuration_content_generate_with_refs(self):
        impl = self.load_impl('assets/s60/implml/test_content_with_refs2.content')
        context = plugin.GenerationContext(output=self.output)
        results = impl.generate(context)
        self.assertTrue(os.path.exists(os.path.join(context.output,'content2p1/content2p2/override.txt')))
        
    def test_configuration_content_generate_with_refs2(self):
        impl = self.load_impl('assets/s60/implml/test_content_with_refs3.content')
        context = plugin.GenerationContext(output=self.output)
        results = impl.generate(context)
        self.assertTrue(os.path.exists(os.path.join(self.output,'example/content2p2/override.txt')))
       
    def test_configuration_content_generate_capital_letters(self):
        impl = self.load_impl('assets/s60/implml/test_content_capital_file_input.content')
        context = plugin.GenerationContext(output=self.output)
        results = impl.generate(context)
        self.assertTrue(os.path.exists(context.output))
        self.assertTrue(os.path.exists(os.path.join(context.output,'content/test_CAP_letters.txt')))

    def test_get_refs(self):
        def check(filename, expected_refs):
            impl = self.load_impl('assets/s60/implml/' + filename)
            actual_refs = impl.get_refs()
            
            if expected_refs is None:
                self.assertEquals(actual_refs, None)
            else:
                self.assertTrue(actual_refs is not None)
                self.assertEquals(sorted(actual_refs), sorted(expected_refs))
       
        check('content2_with_multi_outputs.content', None)
        check('content2_with_tags_refs.content', None)
        check('content2_with_tags.content', None)
        check('copy_files.content', None)
        check('copy.content', None)
        check('test_content_with_refs.content', ['content.inputdir'])
        check('test_content_with_refs2.content', ['content.inputdir2'])
        check('test_content_with_refs3.content', ['content.inputdir2'])
        check('test_content_with_sequence_refs.content', ['ContentFiles.contentfile.fileelem.localPath'])
        check('test_external_input.content', None)
        check('test_external_with_ref.content', ['CTD_Special.InputPath'])
        check('test_filter_both.content', None)

    def test_uses_layer(self):
        project = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'contentproject')))
        root_config = project.get_configuration('product.confml')
        
        impl = self.load_impl('assets/s60/implml/test_content_capital_file_input.content')
        self.assertFalse(impl.uses_layer(root_config.get_configuration_by_index(0)))
        self.assertFalse(impl.uses_layer(root_config.get_configuration_by_index(1)))
        self.assertTrue(impl.uses_layer(root_config.get_configuration_by_index(2)))
    
    def test_get_copy_list_with_empty_file_input_from_sequence(self):
        impl = self.load_impl('assets/s60/implml/empty_input_file_from_sequence.content')
        copylist = impl.get_full_copy_list()
        # There should be nothing in the copy list
        self.assertEquals(copylist, [])
        
    def test_get_copy_list_with_multiple_includes_from_sequence(self):
        impl = self.load_impl('assets/s60/implml/multiple_input_includes_from_sequence.content')
        copylist = impl.get_full_copy_list()
        self.assertEquals(sorted(copylist),
            sorted(
                [('assets/s60/content/test/foo.txt', 'widget/temp/foo.txt', False),
                 ('assets/s60/content/test/bar.txt', 'widget/temp/bar.txt', False),
                 ('assets/s60/content/test/baz.txt', 'widget/temp/baz.txt', False),
                 ('assets/s60/content/test/s60.txt', 'widget/temp/s60.txt', False)]))

    def test_get_copy_list_with_multiple_input_from_sequence_with_flatten(self):
        impl = self.load_impl('assets/s60/implml/multiple_input_from_sequence_with_flatten.content')
        copylist = impl.get_full_copy_list()
        self.assertEquals(sorted(copylist),
            sorted(
                [('family/product/content/wallpapers/wallpaper1.png', 'content/wallpapers/1_wallpaper1.png', False),
                 ('family/product/content/wallpapers/wallpaper2.png', 'content/wallpapers/2_wallpaper2.png', False),
                 ('family/product/content/wallpapers/wallpaper3.png', 'content/wallpapers/3_wallpaper3.png', False)]))
        
if __name__ == '__main__':
    unittest.main()
