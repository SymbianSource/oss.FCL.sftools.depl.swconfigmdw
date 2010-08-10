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
import os
import logging

from cone.public import api, plugin, rules
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))



class TestPluginImplContainer(unittest.TestCase):
    class ImplTest(plugin.ImplBase):
        def __init__(self,ref,configuration):
            plugin.ImplBase.__init__(self,ref,configuration)
            self.generate_invoked = False
            self.output_created = False
            self.refs = ["dummy1.too"]
            self.output_files = ['foo/test.txt']
            self.context = None
        def generate(self, context=None):
            self.generate_invoked = True
            if context:
                for outfile in self.list_output_files():
                    context.add_file(outfile, implementation=self)
            
        def get_refs(self):
            return self.refs

        def list_output_files(self):
            return self.output_files

        def get_outputs(self):
            """
            Return a list of GenerationOutput objets as a list. 
            """
            outputs = []
            phase = None 
            if self.context: phase = self.context.phase
            for outfile in self.list_output_files():
                outputs.append( plugin.GenerationOutput(outfile,self,type='file', phase=phase) )
            return outputs
    
    def test_impl_container_add(self):
        container = plugin.ImplContainer("norm", None)
        imp1  = plugin.ImplBase("implml/test.content",None)
        imp2a = plugin.ImplBase("implml/copy:21.content",None)
        imp2b = plugin.ImplBase("implml/copy:24.content",None)
        container.append(imp1)
        container.append(imp2a)
        container.append(imp2b)
        self.assertEquals(container.impls, [imp1,imp2a, imp2b])

    def test_impl_container_sub_container(self):
        container = plugin.ImplContainer("norm", None)
        imp1  = plugin.ImplBase("implml/test.content",None)
        container.append(imp1)
        subcontainer = plugin.ImplContainer("implml/sub.implml", None)
        imp2a = plugin.ImplBase("implml/sub.implml:21.content",None)
        imp2b = plugin.ImplBase("implml/sub.implml:24.content",None)
        subcontainer.append(imp2a)
        subcontainer.append(imp2b)
        container.append(subcontainer)
        self.assertEquals(container.get_all_implementations(),[imp1,imp2a,imp2b])
        self.assertEquals(container.impls, [imp1,subcontainer])
        container[0] = subcontainer
        self.assertEquals(container.impls, [subcontainer,subcontainer])
        del container[0]
        self.assertEquals(container.impls, [subcontainer])

    def test_impl_container_with_condition(self):
        logger = logging.getLogger('cone')
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        logger.addHandler(ch)
        context = plugin.GenerationContext()
        context.configuration = api.Configuration()
        context.configuration.add_feature(api.Feature("test"))
        context.configuration.add_feature(api.Feature("stringsub"),"test")
        context.configuration.add_feature(api.Feature("intsub"),"test")
        context.configuration.get_default_view().test.value = True
        context.configuration.get_default_view().test.stringsub.value = "stringval"
        context.configuration.get_default_view().test.intsub.value = 2

        condition = rules.SimpleCondition("${test}", "true")
        container = plugin.ImplContainer("norm", None)
        container.condition = condition
        imp1  = TestPluginImplContainer.ImplTest("implml/test.content",None)
        container.append(imp1)
        container.generate(context)
        self.assertTrue(imp1.generate_invoked)
        imp1.generate_invoked = False
        context.configuration.get_default_view().test.value = False
        container.generate(context)
        self.assertFalse(imp1.generate_invoked)

        imp1.generate_invoked = False
        condition = rules.SimpleCondition("${test}", "false")
        container.condition = condition
        container.generate(context)
        self.assertTrue(imp1.generate_invoked)
        imp1.generate_invoked = False
        context.configuration.get_default_view().test.value = True
        container.generate(context)
        self.assertFalse(imp1.generate_invoked)

        imp1.generate_invoked = False
        condition = rules.SimpleCondition("${test.intsub}", "1")
        container.condition = condition
        container.append(imp1)
        container.generate(context)
        self.assertFalse(imp1.generate_invoked)
        context.configuration.get_default_view().test.intsub.value = 1
        container.generate(context)
        self.assertTrue(imp1.generate_invoked)
        
        
    def test_impl_container_generate(self):
        container = plugin.ImplContainer("norm", None)
        imp1  = TestPluginImplContainer.ImplTest("implml/test.content",None)
        imp2a = TestPluginImplContainer.ImplTest("implml/copy:21.content",None)
        imp2b = TestPluginImplContainer.ImplTest("implml/copy:24.content",None)
        container.append(imp1)
        container.append(imp2a)
        container.append(imp2b)
        container.generate()
        self.assertTrue(imp1.generate_invoked)
        self.assertTrue(imp2a.generate_invoked)
        self.assertTrue(imp2a.generate_invoked)

    def test_impl_container_get_tags(self):
        container = plugin.ImplContainer("norm", None)
        imp1  = TestPluginImplContainer.ImplTest("implml/test.content",None)
        imp2a = TestPluginImplContainer.ImplTest("implml/copy:21.content",None)
        imp2b = TestPluginImplContainer.ImplTest("implml/copy:24.content",None)
        subcontainer = plugin.ImplContainer("sub", None)
        container.append(imp1)
        container.append(imp2a)
        container.append(imp2b)
        container.append(subcontainer)
        self.assertEquals(container.get_tags(), None)
        self.assertEquals(container.get_child_tags(), {})
        container.set_tags({'test':['foobar']})
        self.assertEquals(container.get_tags(), None)
        self.assertEquals(container.get_child_tags(), {})
        imp1.set_tags({'foo':['bar']})
        self.assertEquals(container.get_child_tags(), {'foo':['bar']})
        self.assertEquals(container.get_tags(), None)
        imp2a.set_tags({'test':['bar'], 'foo' :['more']})
        self.assertEquals(container.get_child_tags(), {'foo':['bar', 'more'], 'test': ['bar']})
        
        self.assertEquals(container.get_tags(), None)
        subcontainer.set_tags({'test':['bar1']})
        self.assertEquals(container.get_tags(), None)

    def test_impl_container_get_phase(self):
        container = plugin.ImplContainer("norm", None)
        imp1  = TestPluginImplContainer.ImplTest("implml/test.content",None)
        imp2a = TestPluginImplContainer.ImplTest("implml/copy:21.content",None)
        imp2b = TestPluginImplContainer.ImplTest("implml/copy:24.content",None)
        subcontainer1 = plugin.ImplContainer("norm", None)
        container.append(subcontainer1)
        subcontainer1.append(imp1)
        subcontainer1.append(imp2a)
        subcontainer1.append(imp2b)
        subcontainer1.set_invocation_phase("normal")
        self.assertEquals(container.invocation_phase(), "normal")
        imp1.set_invocation_phase('pre')
        self.assertEquals(container.invocation_phase(), "normal")
        subcontainer2 = plugin.ImplContainer("norm", None)
        subimp = TestPluginImplContainer.ImplTest("implml/copy:24.content",None)
        subimp.set_invocation_phase('post')
        subcontainer2.append(subimp)
        subcontainer2.set_invocation_phase('post')
        container.append(subcontainer2)
        self.assertEquals(container.invocation_phase(), 'normal')
        
    def test_impl_container_get_refs(self):
        container = plugin.ImplContainer("norm", None)
        imp1  = TestPluginImplContainer.ImplTest("implml/test.content",None)
        imp2a = TestPluginImplContainer.ImplTest("implml/copy:21.content",None)
        imp2b = TestPluginImplContainer.ImplTest("implml/copy:24.content",None)
        container.append(imp1)
        container.append(imp2a)
        container.append(imp2b)
        self.assertEquals(container.get_refs(), None)
        self.assertEquals(container.get_child_refs(), ['dummy1.too'])
        imp2b.refs = ['dummy2.foo']
        self.assertEquals(container.get_refs(), None)
        self.assertEquals(container.get_child_refs(), ['dummy1.too', 'dummy2.foo'])
        imp2b.refs = None
        self.assertEquals(container.get_refs(), None)
        self.assertEquals(container.get_child_refs(), ['dummy1.too'])
        
    def test_impl_container_list_output_files(self):
        container = plugin.ImplContainer("norm", None)
        subcontainer = plugin.ImplContainer("norm", None)
        imp1  = TestPluginImplContainer.ImplTest("implml/test.content",None)
        imp2a = TestPluginImplContainer.ImplTest("implml/copy:21.content",None)
        imp2b = TestPluginImplContainer.ImplTest("implml/copy:24.content",None)
        container.append(subcontainer)
        subcontainer.append(imp1)
        subcontainer.append(imp2a)
        subcontainer.append(imp2b)
        self.assertEquals(container.list_output_files(), ['foo/test.txt'])
        imp2b.output_files= ['output/dummy2.txt']
        self.assertEquals(container.list_output_files(), ['foo/test.txt', 'output/dummy2.txt'])
        imp1.output_files= ['output/foobar/hee.txt']
        self.assertEquals(container.list_output_files(), ['output/foobar/hee.txt',
                                                          'foo/test.txt', 
                                                          'output/dummy2.txt'])

    def test_impl_container_get_outputs(self):
        container = plugin.ImplContainer("norm", None)
        subcontainer = plugin.ImplContainer("norm", None)
        imp1  = TestPluginImplContainer.ImplTest("implml/test.content",None)
        imp2a = TestPluginImplContainer.ImplTest("implml/copy:21.content",None)
        imp2b = TestPluginImplContainer.ImplTest("implml/copy:24.content",None)
        container.append(subcontainer)
        subcontainer.append(imp1)
        subcontainer.append(imp2a)
        subcontainer.append(imp2b)
        self.assertEquals(len(container.get_outputs()), 3)
        self.assertEquals(container.get_outputs()[0].name, 'foo/test.txt')
        self.assertEquals(container.get_outputs()[1].name, 'foo/test.txt')
        self.assertEquals(container.get_outputs()[2].name, 'foo/test.txt')
        imp2b.output_files= ['foobar.txt','output/dummy2.txt']
        self.assertEquals(len(container.get_outputs()),4)
        self.assertEquals(container.get_outputs()[0].name, 'foo/test.txt')
        self.assertEquals(container.get_outputs()[1].name, 'foo/test.txt')
        self.assertEquals(container.get_outputs()[2].name, 'foobar.txt')


    def test_impl_container_set_output_root(self):
        container = plugin.ImplContainer("norm", None)
        subcontainer = plugin.ImplContainer("norm", None)
        imp1  = TestPluginImplContainer.ImplTest("implml/test.content",None)
        imp2a = TestPluginImplContainer.ImplTest("implml/copy:21.content",None)
        imp2b = TestPluginImplContainer.ImplTest("implml/copy:24.content",None)
        container.append(subcontainer)
        subcontainer.append(imp1)
        subcontainer.append(imp2a)
        subcontainer.append(imp2b)
        self.assertEquals(imp1.get_output_root(), '')
        container.set_output_root('foobar/test')
        self.assertEquals(imp1.get_output_root(), 'foobar/test')

    def test_impl_container_sub_container_generate(self):
        container = plugin.ImplContainer("norm", None)
        imp1  = TestPluginImplContainer.ImplTest("implml/test.content",None)
        container.append(imp1)
        subcontainer = plugin.ImplContainer("implml/sub.implml", None)
        imp2a = TestPluginImplContainer.ImplTest("implml/copy:21.content",None)
        imp2b = TestPluginImplContainer.ImplTest("implml/copy:24.content",None)
        subcontainer.append(imp2a)
        subcontainer.append(imp2b)
        container.append(subcontainer)
        self.assertEquals(container.impls, [imp1,subcontainer])
        container.append(subcontainer)
        container.generate()
        self.assertTrue(imp1.generate_invoked)
        self.assertTrue(imp2a.generate_invoked)
        self.assertTrue(imp2a.generate_invoked)

    def test_impl_container_sub_container_generate_with_generation_contexts(self):
        container = plugin.ImplContainer("norm", None)
        imp1  = TestPluginImplContainer.ImplTest("implml/test.content",None)
        container.append(imp1)
        subcontainer = plugin.ImplContainer("implml/sub.implml", None)
        imp2a = TestPluginImplContainer.ImplTest("implml/copy:21.content",None)
        imp2b = TestPluginImplContainer.ImplTest("implml/copy:24.content",None)
        subcontainer.append(imp2a)
        subcontainer.append(imp2b)
        container.append(subcontainer)
        self.assertEquals(container.impls, [imp1,subcontainer])
        context = plugin.GenerationContext()
        container.generate(context)
        self.assertTrue(imp1.generate_invoked)
        self.assertTrue(imp2a.generate_invoked)
        self.assertTrue(imp2a.generate_invoked)
        self.assertEquals(sorted(context.executed_impls), sorted([imp1,imp2a,imp2b]))

    def test_impl_container_generate_with_generation_contexts_tags(self):
        container = plugin.ImplContainer("norm", None)
        imp1  = TestPluginImplContainer.ImplTest("implml/test.content",None)
        subcontainer1 = plugin.ImplContainer("implml/sub1.implml", None)
        subcontainer1.append(imp1)
        
        subcontainer2 = plugin.ImplContainer("implml/sub2.implml", None)
        imp2a = TestPluginImplContainer.ImplTest("implml/copy:21.content",None)
        imp2a.set_tags({'target': ['rofs3','uda']})
        imp2b = TestPluginImplContainer.ImplTest("implml/copy:24.content",None)
        imp2b.set_tags({'target': ['rofs3','uda']})
        subcontainer2.append(imp2a)
        subcontainer2.append(imp2b)
        container.append(subcontainer1)
        container.append(subcontainer2)
        
        context = plugin.GenerationContext()
        context.tags = {'target': ['rofs3'], 'foobar' :['test']}
        container.generate(context)
        self.assertFalse(imp1.generate_invoked)
        self.assertTrue(imp2a.generate_invoked)
        self.assertTrue(imp2a.generate_invoked)
        self.assertEquals(sorted(context.executed_impls), sorted([imp2a,imp2b]))

    def test_impl_container_generate_with_generation_phase(self):
        container = plugin.ImplContainer("norm", None)
        imp1  = TestPluginImplContainer.ImplTest("implml/test.content",None)
        subcontainer1 = plugin.ImplContainer("implml/sub1.implml", None)
        subcontainer1.append(imp1)
        
        subcontainer2 = plugin.ImplContainer("implml/sub2.implml", None)
        imp2a = TestPluginImplContainer.ImplTest("implml/copy:21.content",None)
        imp2a.set_invocation_phase("post")
        imp2b = TestPluginImplContainer.ImplTest("implml/copy:24.content",None)
        imp2b.set_invocation_phase("post")
        subcontainer2.append(imp2a)
        subcontainer2.append(imp2b)
        container.append(subcontainer1)
        container.append(subcontainer2)
        
        context = plugin.GenerationContext(output='')
        context.phase = "post"
        container.generate(context)
        self.assertFalse(imp1.generate_invoked)
        self.assertTrue(imp2a.generate_invoked)
        self.assertTrue(imp2a.generate_invoked)
        self.assertEquals(sorted(context.executed_impls), sorted([imp2a,imp2b]))
        self.assertEquals(context.executed_impls[0].list_output_files(), ['foo/test.txt'])
        self.assertEquals(len(context.generation_output), 2)
        self.assertEquals(context.generation_output[0].name, 'foo/test.txt')
        self.assertEquals(str(context.generation_output[0]), "GenerationOutput(foo/test.txt, ImplTest(ref='implml/copy:21.content', type=None, lineno=None))")
        self.assertEquals(str(context.generation_output[1]), "GenerationOutput(foo/test.txt, ImplTest(ref='implml/copy:24.content', type=None, lineno=None))")
        self.assertEquals(context.generation_output[0].implementation, imp2a)
        
    def test_impl_container_generate_dry_run(self):
        container = plugin.ImplContainer("norm", None)
        imp1  = TestPluginImplContainer.ImplTest("implml/test.content",None)
        container.append(imp1)
        subcontainer = plugin.ImplContainer("implml/sub.implml", None)
        imp2a = TestPluginImplContainer.ImplTest("implml/copy:21.content",None)
        imp2b = TestPluginImplContainer.ImplTest("implml/copy:24.content",None)
        subcontainer.append(imp2a)
        subcontainer.append(imp2b)
        container.append(subcontainer)
        self.assertEquals(container.impls, [imp1,subcontainer])
        context = plugin.GenerationContext()
        context.dry_run= True
        container.generate(context)
        self.assertFalse(imp1.generate_invoked)
        self.assertFalse(imp2a.generate_invoked)
        self.assertFalse(imp2a.generate_invoked)
        self.assertEquals(sorted(context.executed_impls), sorted([imp1, imp2a,imp2b]))
        self.assertEquals(context.executed_impls[0].list_output_files(), ['foo/test.txt'])
        self.assertEquals(len(context.generation_output), 0)
        