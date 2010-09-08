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

from cone.public import *
from cone.public import _plugin_reader
from testautomation.utils import remove_if_exists
import pickle
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

Tfd = _plugin_reader.TempVariableDefinition
Tsfd = _plugin_reader.TempVariableSequenceDefinition
Sro = _plugin_reader.SettingRefsOverride



MULTI_IMPL_1 = """<?xml version="1.0" encoding="UTF-8"?>
<common:container xmlns:common="http://www.symbianfoundation.org/xml/implml/1">
    <impl xmlns="http://www.test.com/xml/1">
        <elem x="1" y="2"/>
    </impl>
    
    <impl xmlns="http://www.test.com/xml/2">
        <dummy z="500"/>
        <elem x="10" y="20"/>
    </impl>
    
    <impl xmlns="http://www.test.com/xml/3">
        <elem x="100" y="200"/>
        <elem z="300"/>
    </impl>
</common:container>
""".encode('utf-8')

MULTI_IMPL_2 = """<?xml version="1.0" encoding="UTF-8"?>
<container xmlns="http://www.symbianfoundation.org/xml/implml/1"
    xmlns:ns0="http://www.test.com/xml/1" 
    xmlns:ns2="http://www.test.com/xml/2"
    xmlns:ns3="http://www.test.com/xml/3">
    
    <ns0:impl>
      <ns0:elem x="1" y="2"/>
    </ns0:impl>

    <ns2:impl>
      <ns2:dummy z="500"/>
      <ns2:elem x="10" y="20"/>
    </ns2:impl>

    <ns3:impl>
      <ns3:elem x="100" y="200"/>
      <ns3:elem z="300"/>
    </ns3:impl>
</container>
""".encode('utf-8')

MULTI_IMPL_3 = """<?xml version="1.0" encoding="UTF-8"?>
<container xmlns="http://www.symbianfoundation.org/xml/implml/1">
    <impl1:impl xmlns:impl1="http://www.test.com/xml/1">
        <impl1:elem x="1" y="2"/>
    </impl1:impl>
    
    <impl2:impl xmlns:impl2="http://www.test.com/xml/2">
        <impl2:elem x="1" y="2"/>
    </impl2:impl>
    
    <impl1:impl xmlns:impl1="http://www.test.com/xml/1">
        <impl1:elem a="1" b="2"/>
    </impl1:impl>
    
    <impl2:impl xmlns:impl2="http://www.test.com/xml/2">
        <impl2:elem a="1" b="2"/>
    </impl2:impl>
</container>
""".encode('utf-8')

UNSUPPORTED_IMPL_1 = """<?xml version="1.0" encoding="UTF-8"?>
<test_impl>
    <impl xmlns="http://www.test.com/xml/1">
        <elem x="1" y="2"/>
    </impl>
    
    <impl xmlns="http://www.test.com/xml/2">
        <dummy z="500"/>
        <elem x="10" y="20"/>
    </impl>
    
    <impl xmlns="http://www.test.com/xml/4">
        <elem x="1" y="2"/>
    </impl>
</test_impl>
""".encode('utf-8')

UNSUPPORTED_IMPL_2 = """<?xml version="1.0" encoding="UTF-8"?>
<test_impl xmlns="http://www.test.com/xml/6"
    xmlns:ns2="http://www.test.com/xml/2"
    xmlns:ns4="http://www.test.com/xml/4">
    
    <elem x="1" y="2"/>

    <ns2:dummy z="500"/>
    <ns2:elem x="10" y="20"/>

    <ns4:elem x="1" y="2"/>
</test_impl>
""".encode('utf-8')

SINGLE_IMPL_1 = """<?xml version="1.0" encoding="UTF-8"?>
<impl xmlns="http://www.test.com/xml/1">
    <elem x="1"/>
    <elem y="2"/>
    <elem z="3"/>
</impl>
""".encode('utf-8')

SINGLE_IMPL_2 = """<?xml version="1.0" encoding="UTF-8"?>
<impl xmlns="http://www.test.com/xml/2"/>
""".encode('utf-8')

SINGLE_IMPL_3 = """<?xml version="1.0" encoding="UTF-8"?>
<impl xmlns="http://www.test.com/xml/3">
    <elem x="1"/>
</impl>
""".encode('utf-8')

NO_IMPL = """<?xml version="1.0" encoding="UTF-8"?>
<impl>
</impl>
""".encode('utf-8')

class Mock(object):
    pass

class MockView(object):
    def __init__(self, feature_dict):
        self.feature_dict = feature_dict
    
    def get_feature(self, ref):
        feature = Mock()
        feature.get_value = lambda: self.feature_dict[ref]
        feature.get_original_value = lambda: self.feature_dict[ref]
        return feature

class MockConfiguration(object):
    def __init__(self, resources, features={}):
        self.resources = resources
        self.features = features
    
    def get_resource(self, ref):
        res = Mock()
        res.read = lambda: self.resources[ref]
        res.close = lambda: None
        return res
    
    def get_layer(self):
        layer = Mock()
        layer.list_implml = lambda: self.resources.keys()
        return layer
    
    def get_doc(self, ref):
        return utils.etree.fromstring(self.get_resource(ref).read())
    
    def get_default_view(self):
        return MockView(self.features)
    
    def layered_implml(self):
        result = container.DataContainer()
        for res in self.resources.iterkeys():
            result.add_value(res, res)
        return result

class SimpleImpl(plugin.ImplBase):
    def __init__(self, ref, configuration):
        super(SimpleImpl, self).__init__(ref, configuration)
        self.generate_invoked = False
        self.outputfile = ''
    
    def generate(self, context=None):
        if context:
            if self.outputfile:
                f = context.create_file(self.outputfile, implementation=self)
                f.close()
                
        self.generate_invoked = True

class MockImpl(plugin.ImplBase):
    IMPL_TYPE_ID = 'mock'
    
    def __init__(self, data):
        self.data = data
        self.generate_invoked = False
        self.outputfile = ''
        self.refs = None
        self.ref = ''
        
    @classmethod
    def create(cls, resource_ref, configuration, data):
        impl = cls(data)
        plugin.ImplBase.__init__(impl, resource_ref, configuration)
        return impl
    
    def generate(self, context=None):
        if context and hasattr(context,'objects'):
            context.objects.append(self) 
        self.generate_invoked = True
    
    def __repr__(self):
        return "MockImpl(%r)" % self.data
    
    def __eq__(self, other):
        if type(self) == type(other):
            return self.data == other.data
        else:
            return False
    
    def __ne__(self, other):
        return not (self == other)
        
    def __lt__(self, other):
        if type(self) == type(other):
            return self.data < other.data
        else:
            return False

    def get_refs(self):
        """
        Return a list of all ConfML setting references that affect this
        implementation. May also return None if references are not relevant
        for the implementation.
        """
        return self.refs

class MockReaderBase(plugin.ReaderBase):
    @classmethod
    def read_impl(cls, resource_ref, configuration, root_elem):
        data = [cls.__name__, resource_ref]
        for elem in root_elem.findall('{%s}elem' % cls.NAMESPACE):
            data.append(elem.attrib)
        return MockImpl.create(resource_ref, configuration, data)

class MockReader1(MockReaderBase):
    NAMESPACE = "http://www.test.com/xml/1"
    NAMESPACE_ID = "mock1"
    ROOT_ELEMENT_NAME = "impl"
    FILE_EXTENSIONS = ['mock1ml']
class MockReader2(MockReaderBase):
    NAMESPACE = "http://www.test.com/xml/2"
    NAMESPACE_ID = "mock2"
    ROOT_ELEMENT_NAME = "impl"
    FILE_EXTENSIONS = ['mock2ml']
class MockReader3(MockReaderBase):
    NAMESPACE = "http://www.test.com/xml/3"
    NAMESPACE_ID = "mock3"
    ROOT_ELEMENT_NAME = "impl"
    IGNORED_NAMESPACES = ["http://www.test.com/xml/ignored/3"]
    FILE_EXTENSIONS = ['mock3ml', 'test3ml']

MOCK_READER_CLASSES = [MockReader1, MockReader2, MockReader3]

mock_config = MockConfiguration({
    'layer1/implml/multi1.implml'           : MULTI_IMPL_1,
    'layer1/implml/multi2.implml'           : MULTI_IMPL_2,
    'layer1/implml/multi3.implml'           : MULTI_IMPL_3,
    'layer1/implml/unsupported1.implml'     : UNSUPPORTED_IMPL_1,
    'layer1/implml/unsupported2.implml'     : UNSUPPORTED_IMPL_2,
    'layer1/implml/single1.implml'          : SINGLE_IMPL_1,
    'layer1/implml/single2.implml'          : SINGLE_IMPL_2,
    'layer1/implml/single3.implml'          : SINGLE_IMPL_3,
    'layer1/implml/none.implml'             : NO_IMPL,
    'layer1/implml/broken.implml'           : 'Some invalid XML data...',
    'layer1/implml/single1.mock1ml'         : SINGLE_IMPL_1,
    'layer1/implml/single2.mock2ml'         : SINGLE_IMPL_2,
    'layer1/implml/single3.mock3ml'         : SINGLE_IMPL_3,
    'layer1/implml/single3.test3ml'         : SINGLE_IMPL_3,
    'layer1/implml/multi1.dummyml'          : MULTI_IMPL_1,
    'layer1/implml/dummy'                   : MULTI_IMPL_1,
})


class TestPluginGenerationContext(unittest.TestCase):
    def test_generation_context_handle_terminal(self):
        config = api.Configuration()
        context = plugin.GenerationContext(configuration=config)
        self.assertRaises(exceptions.NotFound, context.handle_terminal, 'feature')
        config.create_feature('feature')
        # rebuild default view
        config._remove('?default_view')
        self.assertEquals(context.handle_terminal('feature'), None)
            

    def test_generation_create_file(self):
        config = api.Configuration()
        context = plugin.GenerationContext(configuration=config, 
                                           output=os.path.join(ROOT_PATH, 'temp'),
                                           phase="normal")
        mi = MockImpl({})
        outfile = context.create_file('foobar/test.txt', implementation=mi)
        outfile.write("Test output file creation")
        outfile.close()
        expected = utils.resourceref.norm(os.path.join(context.output, 'foobar/test.txt'))
        self.assertEquals(len(context.generation_output), 1)
        self.assertEquals(context.generation_output[0].name, expected)
        self.assertEquals(context.generation_output[0].implementation, mi)
        self.assertEquals(context.generation_output[0].phase, "normal")
        self.assertTrue(os.path.exists(expected))
        os.unlink(expected)

        absfile = utils.resourceref.norm(os.path.join(ROOT_PATH, 'temp/foobar/abspath.txt'))
        outfile = context.create_file(absfile, implementation=mi)
        outfile.write("Test output file creation")
        outfile.close()
        self.assertEquals(len(context.generation_output), 2)
        self.assertEquals(context.generation_output[1].name, absfile)
        self.assertEquals(context.generation_output[1].implementation, mi)
        self.assertEquals(context.generation_output[1].phase, "normal")
        self.assertTrue(os.path.exists(absfile))
        os.unlink(absfile)
        
    def test_generation_add_output(self):
        config = api.Configuration()
        context = plugin.GenerationContext(configuration=config, 
                                           output=os.path.join(ROOT_PATH, 'temp'),
                                           phase="normal")
        mi = MockImpl({})
        context.add_file('add.txt', implementation=mi)

        self.assertEquals(len(context.generation_output), 1)
        self.assertEquals(context.generation_output[0].name, utils.resourceref.norm(os.path.join(context.output, 'add.txt')))
        self.assertEquals(context.generation_output[0].implementation, mi)
        self.assertEquals(context.generation_output[0].phase, "normal")
        
        external_output = utils.resourceref.norm(os.path.join(ROOT_PATH, 'temp', 'external/foobar.txt'))
        context.add_file(external_output, implementation=mi)
        self.assertEquals(len(context.generation_output), 2)
        self.assertEquals(context.generation_output[1].name, external_output)
        self.assertEquals(context.generation_output[1].implementation, mi)
        self.assertEquals(context.generation_output[1].phase, "normal")

    def test_generation_get_output(self):
        config = api.Configuration()
        context = plugin.GenerationContext(configuration=config, 
                                           output=os.path.join(ROOT_PATH, 'temp'),
                                           phase="normal")
        mi = MockImpl({})
        context.add_file('add1.txt', implementation=mi)
        context.add_file('foo/add2.txt', implementation=None)

        self.assertEquals(len(context.get_output()), 2)
        self.assertEquals(context.get_output()[1].filename, 'add2.txt')
        self.assertEquals(context.get_output()[1].abspath, os.path.normpath(os.path.join(context.output,'foo/add2.txt')))
        self.assertEquals(context.get_output()[1].relpath, os.path.normpath('foo/add2.txt'))
        self.assertEquals(len(context.get_output(implml_type='mock')), 1)
        self.assertEquals(context.get_output(implml_type='mock')[0].filename, 'add1.txt')

    def test_generation_get_refs_no_output(self):
        config = api.Configuration()
        context = plugin.GenerationContext(configuration=config, 
                                           output=os.path.join(ROOT_PATH, 'temp'),
                                           phase="normal")
        self.assertEquals(context.get_refs_with_no_output(),[]) 
        self.assertEquals(context.get_refs_with_no_output(['']),['']) 

        context.changed_refs = ['foo.bar', 
                                'foo.two',
                                'foo.three']
        
        self.assertEquals(context.get_refs_with_no_output(),['foo.bar', 
                                                             'foo.three',
                                                             'foo.two']) 
        mi = MockImpl({})
        mi.refs = ['foo.bar','nonno.noo','foo.three']
        context.add_file('add1.txt', implementation=mi)
        context.add_file('foo/add2.txt', implementation=None)
        
        self.assertEquals(context.get_refs_with_no_output(),['foo.two']) 
        context.changed_refs = ['foo.bar', 
                                'foo.three']
        self.assertEquals(context.get_refs_with_no_output(),[]) 
        mi.refs = []
        self.assertEquals(context.get_refs_with_no_output(),['foo.bar', 
                                                             'foo.three']) 
        mi.refs = None
        self.assertEquals(context.get_refs_with_no_output(),['foo.bar', 
                                                             'foo.three']) 

    def test_merged_context_get_changed_refs_intersect(self):
        config = api.Configuration()
        context1 = plugin.GenerationContext(configuration=config, 
                                           output=os.path.join(ROOT_PATH, 'temp'),
                                           phase="normal")
        context2 = plugin.GenerationContext(configuration=config, 
                                           output=os.path.join(ROOT_PATH, 'temp'),
                                           phase="normal")

        context1.changed_refs = ['foo.bar', 
                                'foo.two',
                                'foo.three']
        context2.changed_refs = ['foo.bar', 
                                'foo.two1']
        outs = plugin.MergedContext([context1,context2])
        self.assertEquals(sorted(outs.get_changed_refs(operation='union')), 
                          sorted(['foo.two1',
                                  'foo.bar',
                                  'foo.two',
                                  'foo.three']))
        self.assertEquals(outs.get_changed_refs(operation='intersection'), ['foo.bar'])
        self.assertEquals(sorted(outs.get_changed_refs(operation='difference')), sorted(['foo.three',
                                                                                         'foo.two']))
        self.assertEquals(sorted(outs.get_changed_refs(operation='symmetric_difference')), sorted(['foo.two1', 
                                                                                          'foo.three', 
                                                                                          'foo.two']))

    def test_generation_get_refs_no_output_with_two_contexts(self):
        config = api.Configuration()
        context1 = plugin.GenerationContext(configuration=config, 
                                           output=os.path.join(ROOT_PATH, 'temp'),
                                           phase="normal")
        context2 = plugin.GenerationContext(configuration=config, 
                                           output=os.path.join(ROOT_PATH, 'temp'),
                                           phase="normal")

        context1.changed_refs = ['foo.bar', 
                                'foo.two',
                                'foo.three']
        context2.changed_refs = ['foo.bar1', 
                                'foo.two1']
        
        
        mi1 = MockImpl({})
        mi1.refs = ['foo.bar','nonno.noo','foo.three']
        mi2 = MockImpl({})
        mi2.refs = ['foo.bar1']
        context1.add_file('add1.txt', implementation=mi1)
        context1.add_file('foo/add2.txt', implementation=None)
        context2.add_file('add2.txt', implementation=mi2)
        outs = plugin.MergedContext([context1,context2])
        self.assertEquals(outs.get_refs_with_no_output(), ['foo.two', 'foo.two1'])
        self.assertEquals(outs.get_refs_with_no_output(['foo.two']), ['foo.two'])
        self.assertEquals(outs.get_refs_with_no_output(['foo.bar']), [])

    def test_generation_get_refs_with_no_implementation(self):
        config = api.Configuration()
        context1 = plugin.GenerationContext(configuration=config, 
                                           output=os.path.join(ROOT_PATH, 'temp'),
                                           phase="normal")
        context2 = plugin.GenerationContext(configuration=config, 
                                           output=os.path.join(ROOT_PATH, 'temp'),
                                           phase="normal")

        context1.changed_refs = ['foo.bar', 
                                'foo.two',
                                'foo.three']
        context2.changed_refs = ['foo.bar1', 
                                'foo.two1']
        
        
        mi1 = MockImpl({})
        mi1.ref = 'mi1'
        mi1.refs = ['foo.bar','nonno.noo','foo.three']
        mi2 = MockImpl({})
        mi2.ref = 'mi2'
        mi2.refs = ['foo.bar1']
        context1.impl_set.add(mi1)
        context2.impl_set.add(mi2)
        outs = plugin.MergedContext([context1,context2])
        self.assertEquals(outs.get_refs_with_no_implementation(), ['foo.two', 'foo.two1'])
        self.assertEquals(outs.get_refs_with_no_implementation(['foo.bar']), [])
        self.assertEquals(outs.get_refs_with_no_implementation(['foo.two', 'foo.bar1']), ['foo.two'])


    def test_context_data_grep_log(self):
        context = plugin.GenerationContext()
        context.log = ['foo bar',
                     'foo faa',
                     'jee jee jehu']
        self.assertEquals(context.grep_log('jee'), [(2,'jee jee jehu')])

    def test_context_pickle(self):
        remove_if_exists(os.path.join(ROOT_PATH,'temp'))
        os.mkdir(os.path.join(ROOT_PATH, 'temp'))
        
        config = api.Configuration()
        config.create_feature('feature')
        context = plugin.GenerationContext(configuration=config, 
                                           output=os.path.join(ROOT_PATH, 'temp'),
                                           phase="normal")
        
        dfile  = open(os.path.join(ROOT_PATH,'temp/out_gencontext.dat'), 'w')
        pickle.dump(context, dfile)
        dfile.close()
        dfile  = open(os.path.join(ROOT_PATH,'temp/out_gencontext.dat'))
        context2 = pickle.load(dfile)
        self.assertEquals(context2.configuration.path, context.configuration.path)

    def test_context_with_project_pickle(self):
        remove_if_exists(os.path.join(ROOT_PATH,'temp'))
        os.mkdir(os.path.join(ROOT_PATH, 'temp'))
        prj = api.Project(api.Storage(""))
        config = api.Configuration()
        config.create_feature('feature')
        prj.add_configuration(config, True)
        context = plugin.GenerationContext(configuration=config, 
                                           output=os.path.join(ROOT_PATH, 'temp'),
                                           phase="normal")
        
        dfile  = open(os.path.join(ROOT_PATH,'temp/out_gencontext2.dat'), 'w')
        pickle.dump(context, dfile)
        dfile.close()
        dfile  = open(os.path.join(ROOT_PATH,'temp/out_gencontext2.dat'))
        context2 = pickle.load(dfile)
        self.assertEquals(context2.configuration.path, context.configuration.path)


class TestPluginImplBase(unittest.TestCase):
    def setUp(self):
        pass

    def test_implbase_add_tags(self):
        impl = plugin.ImplBase('test',None)
        impl.set_tags({'target': ['test', 'foo']})
        self.assertEquals(impl.get_tags()['target'],['test','foo'])
        #self.assertEquals(impl.has_tag({}, policy='OR'), True)
        self.assertEquals(impl.has_tag({'target': ['test']}, policy='OR'), True)
        self.assertEquals(impl.has_tag({'target': ['test']}, policy='AND'), True)
        self.assertEquals(impl.has_tag({'target': ['foo']}, policy='OR'), True)
        self.assertEquals(impl.has_tag({'target': ['foo']}, policy='AND'), True)
        self.assertEquals(impl.has_tag({'target': ['test','foo']}, policy='OR'), True)
        self.assertEquals(impl.has_tag({'target': ['test','foo']}, policy='AND'), True)
        self.assertEquals(impl.has_tag({'target': ['test2','foo']}, policy='OR'), True)
        self.assertEquals(impl.has_tag({'target': ['test2','foo']}, policy='AND'), False)
        self.assertEquals(impl.has_tag({'foo': ['foo']}, policy='OR'), False)
        self.assertEquals(impl.has_tag({'foo': ['foo']}, policy='AND'), False)
        self.assertEquals(impl.has_tag({'target': ['foo'], 'foo':['bar']}, policy='AND'), False)
        self.assertEquals(impl.has_tag({'target': ['foo'], 'foo':['bar']}, policy='OR'), True)

    def test_implbase_output(self):
        str = api.Storage(utils.relpath(ROOT_PATH))
        config = api.Configuration('foo')
        config.storage = str
        impl = plugin.ImplBase('foo.implml', config)
        self.assertEquals(impl.output, '')
        impl.plugin_output = 'test'
        self.assertEquals(impl.output, 'test')
        impl.set_output_root('foobar')
        self.assertEquals(impl.output, 'foobar/test')
        impl.set_output_root('/foobar')
        self.assertEquals(impl.output, '/foobar/test')

        self.assertEquals(impl.path, 'foo.implml')
        self.assertEquals(impl.abspath, os.path.abspath(os.path.join(ROOT_PATH,'foo.implml')))


    def test_implbase_tags_with_refs(self):
        config = MockConfiguration({}, features = {
            'Foo.Bar'           : 'foobar',
            'Foo.Baz'           : 'foobaz',
            'Feature.TagName'   : 'tagname',
            'Feature.TagValue'  : 'tagvalue',
        })
        
        impl = plugin.ImplBase('test', config)
        impl.set_tags({
            'test'              : ['${Foo.Bar}', 'foo', 'bar', '${Foo.Bar} and ${Foo.Baz}'],
            '${Feature.TagName}': ['${Feature.TagValue}']})
        
        expected = {
            'test': ['foobar', 'foo', 'bar', 'foobar and foobaz'],
            'tagname': ['tagvalue'],
        }
        self.assertEquals(impl.get_tags(), expected)
    
    def test_has_ref(self):
        impl = plugin.ImplBase('test', None)
        self.assertEquals(impl.has_ref('Foo.Bar'), None)
        
        impl.get_refs = lambda: ['Foo.Bar', 'Xyz']
        
        # Test using different supported parameter types
        self.assertTrue(impl.has_ref('Foo.Bar'))
        self.assertTrue(impl.has_ref(['Foo.Bar']))
        self.assertTrue(impl.has_ref(('Foo.Bar',)))
        
        # Impl uses the exact given ref
        self.assertTrue(impl.has_ref('Foo.Bar'))
        self.assertTrue(impl.has_ref('Xyz'))
        
        # Impl uses the given ref's parent ref
        self.assertTrue(impl.has_ref('Foo.Bar.Baz'))
        self.assertTrue(impl.has_ref('Xyz.Zyx'))
        
        # Impl does not use the entire parent ref of 'Foo.Bar', only the
        # 'Bar' sub-ref
        self.assertFalse(impl.has_ref('Foo'))
        
        # Various refs almost matching a specified ref
        self.assertFalse(impl.has_ref('Fo'))
        self.assertFalse(impl.has_ref('Fog'))
        self.assertFalse(impl.has_ref('Food'))
        self.assertFalse(impl.has_ref('Foo.Ba'))
        self.assertFalse(impl.has_ref('Foo.Bag'))
        self.assertFalse(impl.has_ref('Foo.Bard'))
        
        # Various refs not at all in the impl's ref list
        self.assertFalse(impl.has_ref('Yay'))
        self.assertFalse(impl.has_ref(['Yay', 'Fhtagn']))
        
        # One of the refs in the given list matches
        self.assertTrue(impl.has_ref(['Yay', 'Fhtagn', 'Foo.Bar']))
        self.assertTrue(impl.has_ref(['Yay', 'Foo.Bar.Baz', 'Fhtagn']))
        self.assertTrue(impl.has_ref(['Yay', 'Xyz', 'Fhtagn']))
        

class TestPlugin(plugin.ImplBase):
    def __init__(self, ref):
        super(TestPlugin, self).__init__(ref, None)
        self.refs = None
    
    def get_refs(self):
        return self.refs

class TestPluginImplSet(unittest.TestCase):    
    def test_add_implementation_and_list(self):
        iset= plugin.ImplSet()
        imp1  = plugin.ImplBase("implml/test.content",None)
        imp2a = plugin.ImplBase("implml/copy.content",None)
        imp2b = plugin.ImplBase("implml/copy.content",None)
        iset.add_implementation(imp1)
        iset.add_implementation(imp2a)
        iset.add_implementation(imp2b)
        self.assertEquals(sorted(iset.list_implementation()),
                          sorted(['implml/test.content',
                                  'implml/copy.content']))

    def test_add_implementation_and_generate(self):
        iset = plugin.ImplSet()
        imp1  = SimpleImpl("implml/test1.content", None)
        imp1.outputfile = 'test/foo.txt'
        imp2a = SimpleImpl("implml/test2.content", None)
        imp2b = SimpleImpl("implml/test3.content", None)
        iset.add_implementation(imp1)
        iset.add_implementation(imp2a)
        iset.add_implementation(imp2b)
        context = plugin.GenerationContext(output="temp")
        iset.generate(context)
        self.assertEquals(sorted(context.executed_impls), sorted([imp1, imp2a, imp2b])) 
        self.assertEquals(context.generation_output[0].name, 'temp/test/foo.txt')
        self.assertTrue(os.path.exists(context.generation_output[0].name))
        self.assertEquals(context.generation_output[0].implementation,imp1)


    def test__generate_with_exception(self):
        def generate_exception(*args):
            raise Exception("test exception %s" % args)
            
        iset = plugin.ImplSet()
        imp1  = SimpleImpl("implml/test1.content", None)
        imp1.outputfile = 'test/foo.txt'
        imp2a = SimpleImpl("implml/test2.content", None)
        imp2a.generate = generate_exception
        iset.add_implementation(imp1)
        iset.add_implementation(imp2a)
        context = plugin.GenerationContext(output="temp")
        iset.generate(context)
        self.assertEquals(sorted(context.executed_impls), sorted([imp1, imp2a])) 
        self.assertEquals(context.generation_output[1].type, 'exception')
        self.assertEquals(context.generation_output[1].name, 'exception from implml/test2.content')
        self.assertEquals(context.generation_output[1].implementation, imp2a)

    def test_add_implementation_and_get_implementations_by_file(self):
        iset = plugin.ImplSet()
        imp1  = plugin.ImplBase("implml/test.content",None)
        imp2a = plugin.ImplBase("implml/copy.content",None)
        imp2b = plugin.ImplBase("implml/copy.content",None)
        iset.add_implementation(imp1)
        iset.add_implementation(imp2a)
        iset.add_implementation(imp2b)
        self.assertEquals(iset.get_implementations_by_file("implml/test.content"), [imp1])
        self.assertEquals(sorted(iset.get_implementations_by_file("implml/copy.content")),
                          sorted([imp2a, imp2b]))

    def test_add_implementation_and_remove_implementation(self):
        iset = plugin.ImplSet()
        imp1  = plugin.ImplBase("implml/test.content",None)
        imp2a = plugin.ImplBase("implml/copy.content",None)
        imp2b = plugin.ImplBase("implml/copy.content",None)
        iset.add_implementation(imp1)
        iset.add_implementation(imp2a)
        iset.add_implementation(imp2b)
        iset.remove_implementation("implml/test.content")
        self.assertEquals(len(iset.list_implementation()),1)
        self.assertEquals(iset.list_implementation()[0],"implml/copy.content")

    def test_add_implementation_and_remove_all(self):
        iset = plugin.ImplSet()
        imp1  = plugin.ImplBase("implml/test.content",None)
        imp2a = plugin.ImplBase("implml/copy.content",None)
        imp2b = plugin.ImplBase("implml/copy.content",None)
        imp3  = plugin.ImplBase("implml/foo.content",None)
        iset.add_implementation(imp1)
        iset.add_implementation(imp2a)
        iset.add_implementation(imp2b)
        iset.add_implementation(imp3)
        for implref in iset.list_implementation():
            iset.remove_implementation(implref)
        self.assertEquals(len(iset.list_implementation()),0)

    def test_create_impl_set(self):
        plugin.create_impl_set('',None);
        pass

    def test_add_implementation_find_with_tags(self):
        def impl_list(impl_iterable):
            return sorted(list(impl_iterable), key=lambda impl: impl.ref)
        
        iset = plugin.ImplSet()
        imp1 = TestPlugin("implml/test.content")
        imp2 = TestPlugin("implml/copy.content")
        imp3 = TestPlugin("implml/foo.content")
        imp1.set_tags({'target': ['core','rofs2','rofs3']})
        imp2.set_tags({'target': ['rofs3','uda']})
        imp3.set_tags({'target': ['mmc','uda']})
        iset.add_implementation(imp1)
        iset.add_implementation(imp2)
        iset.add_implementation(imp3)
        self.assertEquals(impl_list(iset.filter_implementations(tags={'target' : ['rofs3']})),
                          impl_list([imp1,imp2]))
        self.assertEquals(impl_list(iset.filter_implementations(tags={'target' : ['uda']})),
                          impl_list([imp2,imp3]))
        self.assertEquals(impl_list(iset.filter_implementations(tags={'target' : ['mmc','uda']}, policy='AND')),
                          impl_list([imp3]))
        self.assertEquals(impl_list(iset.filter_implementations(tags={'target' : ['mmc','uda']}, policy='OR')),
                          impl_list([imp2, imp3]))
        cont = iset.filter_implementations(tags={'target' : ['core']}) | iset.filter_implementations(tags={'target' : ['mmc']}) 
        self.assertEquals(len(cont),2)
        self.assertEquals(impl_list(cont), impl_list([imp1,imp3]))

        cont = iset.filter_implementations(tags={'target' : ['rofs3']}) & iset.filter_implementations(tags={'target' : ['uda']}) 
        self.assertEquals(len(cont),1)
        self.assertEquals(impl_list(cont), impl_list([imp2]))
    
    def test_pre_impl_filter(self):
        resources = [
            "foo.txt",
            ".hidden_file",
            ".test/test.txt",
            "layer1/implml/.hidden",
            "layer1/implml/test.crml",
            "layer1/implml/test3.gcfml",
            "layer1/implml/.svn/text-base/test.crml.svn-base",
            "layer1/implml/subdir/test5.crml",
            "layer1/implml/subdir/test6.ruleml",
            "layer1/implml/subdir/.scripts/test6_ruleml.py",
        ]
        
        expected = [
            "foo.txt",
            "layer1/implml/test.crml",
            "layer1/implml/test3.gcfml",
            "layer1/implml/subdir/test5.crml",
            "layer1/implml/subdir/test6.ruleml",
        ]
        
        self.assertEquals(expected, plugin.pre_filter_impls(resources))
        
        # Test with backslashes
        resources = map(lambda path: path.replace('/', '\\'), resources)
        expected = map(lambda path: path.replace('/', '\\'), expected)
        self.assertEquals(expected, plugin.pre_filter_impls(resources))

    def test_get_implemented_refs(self):
            
        iset = plugin.ImplSet()
        imp1 = TestPlugin('imp1')
        imp2 = TestPlugin('imp2')
        imp3 = TestPlugin('imp3')
        iset.add_implementation(imp1)
        iset.add_implementation(imp2)
        iset.add_implementation(imp3)
        imp1.refs = ['fea.child1', 'fea.child2']
        imp2.refs = ['fea.setting1']
        imp3.refs = ['foo.bar']
        self.assertEquals(sorted(iset.get_implemented_refs()), sorted(['fea.child1', 
                                                                       'fea.child2',
                                                                       'fea.setting1',
                                                                       'foo.bar']))

    def test_get_implementations_with_ref(self):
            
        iset = plugin.ImplSet()
        imp1 = TestPlugin('implml1')
        imp2 = TestPlugin('implml2')
        imp3 = TestPlugin('implml3')
        imp4 = TestPlugin('implml3')
        iset.add_implementation(imp1)
        iset.add_implementation(imp2)
        iset.add_implementation(imp3)
        iset.add_implementation(imp4)
        imp1.refs = ['fea.child1', 'fea.child2']
        imp2.refs = ['foo.bar', 'fea.setting1']
        imp3.refs = ['foo.bar']
        self.assertEquals(iset.get_implementations_with_ref('fea.child1'), [imp1])
        self.assertEquals(iset.get_implementations_with_ref('fea.setting1'), [imp2])
        self.assertEquals(iset.get_implementations_with_ref('foo.bar'), [imp2, imp3])

class TestPluginImplSetCopy(unittest.TestCase):
    class TestImpl(plugin.ImplBase):
        pass # No default invocation phase specified, should be 'normal'
    class PreImpl(plugin.ImplBase):
        DEFAULT_INVOCATION_PHASE = 'pre'
    class NormalImpl(plugin.ImplBase):
        DEFAULT_INVOCATION_PHASE = 'normal'
    class PostImpl(plugin.ImplBase):
        DEFAULT_INVOCATION_PHASE = 'post'

    def setUp(self):
        plugin.ImplFactory.set_reader_classes_override(MOCK_READER_CLASSES)
    
    def tearDown(self):
        plugin.ImplFactory.set_reader_classes_override(None)
    
    def _get_impl_container(self):
        impl_files = ['layer1/implml/single1.implml',
                      'layer1/implml/single2.implml',
                      'layer1/implml/single3.implml',
                      'layer1/implml/multi1.implml',
                      'layer1/implml/multi2.implml']
        return plugin.create_impl_set(impl_files, mock_config)
    

    def test_get_test_impl_iset(self):
        iset = self._get_impl_container()
        # There are 5 ImplML files
        self.assertEquals(len(iset.list_implementation()), 5)
        # ...but two of them contain 3 implementations each
        self.assertEquals(len(iset), 5)
    
    def _get_phase_test_impl_container(self):
        return plugin.ImplSet([
            self.TestImpl('foo.test', None),
            self.NormalImpl('foo.norm', None),
            self.PreImpl('foo.pre', None),
            self.PostImpl('test.post', None),
            self.PostImpl('foo.post', None),
        ])
    
    def test_get_phase_test_impl_iset(self):
        iset = self._get_phase_test_impl_container()
        self.assertEquals(5, len(iset))
        self.assertEquals(len(iset.list_implementation()), 5)
        
        def check(filename, phase):
            impls = iset.get_implementations_by_file(filename)
            self.assertEquals(1, len(impls))
            impl = impls[0]
            self.assertEquals(impl.ref, filename)
            self.assertEquals(impl.invocation_phase(), phase)
        check('foo.test', 'normal')
        check('foo.norm', 'normal')
        check('foo.pre', 'pre')
        check('test.post', 'post')
        check('foo.post', 'post')
        
        return iset
    
    def test_create_impl_set(self):
        iset = self._get_impl_container()
        # There are 5 ImplML files
        self.assertEquals(len(iset.list_implementation()), 5)
        # ...but two of them contain 3 implementations each
        self.assertEquals(len(iset), 5)
    
    def test_invocation_phases(self):
        iset = self._get_phase_test_impl_container()
        phases = iset.invocation_phases()
        self.assertEquals(phases,['pre','normal','post'])
 
    def test_copy(self):
        iset = self._get_impl_container()
        newcontainer = iset.copy()
        self.assertTrue(newcontainer is not iset)
        self.assertEquals(len(newcontainer), 5)

    def test_execute_generate(self):
        iset = self._get_impl_container()
        iset.execute(iset, 'generate')
        actual_impls = []
        for impl in iset:
            if isinstance(impl, plugin.ImplContainer):
                actual_impls += impl.get_all_implementations()
            else:
                actual_impls.append(impl)
        for impl in actual_impls:
            self.assertTrue(impl.generate_invoked)

    def test_impl_container_generate(self):
        iset = self._get_impl_container()
        context = plugin.GenerationContext()
        context.history = ""
        context.objects = []
        iset.generate(context)
        self.assertEquals(len(context.objects), 9)
        actual_impls = []
        for impl in iset:
            if isinstance(impl, plugin.ImplContainer):
                actual_impls += impl.get_all_implementations()
            else:
                actual_impls.append(impl)
        for impl in actual_impls:
            self.assertTrue(impl.generate_invoked)

    def test_filter_all(self):
        iset = self._get_impl_container()
        impl_list = iset.filter_implementations()
        self.assertEquals(len(impl_list), 5)

    def test_filter_for_pre_phase(self):
        iset = self._get_phase_test_impl_container()
        impl_list = list(iset.filter_implementations(phase='pre'))
        self.assertEquals(len(impl_list), 1)
        self.assertEquals(impl_list[0].invocation_phase(), 'pre')
        self.assertEquals(impl_list[0].ref, 'foo.pre')

    def test_filter_for_normal_phase(self):
        iset = self._get_phase_test_impl_container()
        impl_list = list(iset.filter_implementations(phase='normal'))
        self.assertEquals(len(impl_list), 2)
        self.assertEquals(impl_list[0].invocation_phase(), 'normal')
        self.assertEquals(impl_list[1].invocation_phase(), 'normal')

    def test_filter_for_post_phase(self):
        iset = self._get_phase_test_impl_container()
        impl_list = list(iset.filter_implementations(phase='post'))
        self.assertEquals(len(impl_list), 2)
        self.assertEquals(impl_list[0].invocation_phase(), 'post')
        self.assertEquals(impl_list[1].invocation_phase(), 'post')


class TestPluginImplSettings(unittest.TestCase):
    class Test1Impl(plugin.ImplBase):
        IMPL_TYPE_ID = "test1"
    class Test2Impl(plugin.ImplBase):
        IMPL_TYPE_ID = "test2"
    class Test3Impl(plugin.ImplBase):
        IMPL_TYPE_ID = "test3"

    def test_plugin_settings(self):
        settings.SettingsFactory.cone_parser().read([os.path.join(ROOT_PATH,'test_defaults.cfg')])
        impl = TestPluginImplSettings.Test1Impl("",None)
        self.assertEquals(impl.output_root, '')
        self.assertEquals(impl.output_subdir, '')
        impl.output_subdir = 'foobar'
        self.assertEquals(impl.get_tags(), {})
        self.assertEquals(impl.output, 'foobar')

        impl = TestPluginImplSettings.Test2Impl("",None)
        self.assertEquals(impl.output_subdir, '')



class TestReaders(unittest.TestCase):
    
    def setUp(self):
        plugin.ImplFactory.set_reader_classes_override(MOCK_READER_CLASSES)
    
    def tearDown(self):
        plugin.ImplFactory.set_reader_classes_override(None)
    
    def assert_namespace_list_equals(self, resource_ref, expected_namespaces):
        self.assertEquals(
            expected_namespaces,
            _plugin_reader.ImplReader._get_namespaces(mock_config.get_doc(resource_ref)))
    
    def test_get_needed_reader_classes(self):
        self.assert_namespace_list_equals('layer1/implml/none.implml', [])
        
        self.assert_namespace_list_equals('layer1/implml/single1.implml',
            ['http://www.test.com/xml/1'])
        
        self.assert_namespace_list_equals('layer1/implml/single2.implml',
            ['http://www.test.com/xml/2'])
        
        self.assert_namespace_list_equals('layer1/implml/multi1.implml',
            ['http://www.symbianfoundation.org/xml/implml/1', 
             'http://www.test.com/xml/1',
             'http://www.test.com/xml/2',
             'http://www.test.com/xml/3'])
        
        self.assert_namespace_list_equals('layer1/implml/multi2.implml',
            ['http://www.symbianfoundation.org/xml/implml/1', 
             'http://www.test.com/xml/1',
             'http://www.test.com/xml/2',
             'http://www.test.com/xml/3'])
        
        self.assert_namespace_list_equals('layer1/implml/multi3.implml',
            ['http://www.symbianfoundation.org/xml/implml/1', 
             'http://www.test.com/xml/1',
             'http://www.test.com/xml/2'])
        
        self.assert_namespace_list_equals('layer1/implml/unsupported1.implml',
            ['http://www.test.com/xml/1',
             'http://www.test.com/xml/2',
             'http://www.test.com/xml/4'])
        
        self.assert_namespace_list_equals('layer1/implml/unsupported2.implml',
            ['http://www.test.com/xml/6',
             'http://www.test.com/xml/2',
             'http://www.test.com/xml/4'])
    
    def assert_read_impls_equal(self, expected, resource_ref):
        actual = plugin.ImplFactory.get_impls_from_file(resource_ref, mock_config)
        if len(actual) == 1 and isinstance(actual[0], plugin.ImplContainer):
            actual = actual[0].get_all_implementations() 
        self.assertEquals(expected, actual)
        
#        # Assert that the implementations have the correct impl indices set
#        for i, impl in enumerate(actual):
#            self.assertEquals(i, impl.index, "Impl %r does not have the expected index %r (is %r)" % (impl, i, impl.index))
        
    def test_get_impls_from_file(self):
        self.assert_read_impls_equal(
            [],
            'layer1/implml/none.implml')
        
        file = 'layer1/implml/single1.implml'
        self.assert_read_impls_equal(
            [MockImpl(['MockReader1', file, {'x': '1'}, {'y': '2'}, {'z': '3'}])],
            file)
        
        file = 'layer1/implml/single2.implml'
        self.assert_read_impls_equal(
            [MockImpl(['MockReader2', file])],
            file)
        
        file = 'layer1/implml/single3.implml'
        self.assert_read_impls_equal(
            [MockImpl(['MockReader3', file, {'x': '1'}])],
            file)
        
        file = 'layer1/implml/multi1.implml'
        self.assert_read_impls_equal(
            [MockImpl(['MockReader1', file, {'x': '1', 'y': '2'}]),
             MockImpl(['MockReader2', file, {'x': '10', 'y': '20'}]),
             MockImpl(['MockReader3', file, {'x': '100', 'y': '200'}, {'z': '300'}])],
            file)
        
        file = 'layer1/implml/multi2.implml'
        self.assert_read_impls_equal(
            [MockImpl(['MockReader1', file, {'x': '1', 'y': '2'}]),
             MockImpl(['MockReader2', file, {'x': '10', 'y': '20'}]),
             MockImpl(['MockReader3', file, {'x': '100', 'y': '200'}, {'z': '300'}])],
            file)
        
        file = 'layer1/implml/multi3.implml'
        self.assert_read_impls_equal(
            [MockImpl(['MockReader1', file, {'x': '1', 'y': '2'}]),
             MockImpl(['MockReader2', file, {'x': '1', 'y': '2'}]),
             MockImpl(['MockReader1', file, {'a': '1', 'b': '2'}]),
             MockImpl(['MockReader2', file, {'a': '1', 'b': '2'}]),],
            file)
        
        
        self.assert_read_impls_equal([], 'layer1/implml/unsupported1.implml')
        self.assert_read_impls_equal([], 'layer1/implml/unsupported2.implml')
        
        self.assert_read_impls_equal([], 'layer1/implml/broken.implml')
    
    def test_is_supported_impl_file(self):
        def check(filename, expected):
            self.assertEquals(expected, plugin.ImplFactory.is_supported_impl_file(filename))
        check('test.implml', True)
        check('layer/implml/test.implml', True)
        check('layer/implml/test.mock1ml', True)
        check('layer/implml/test.mock2ml', True)
        check('layer/implml/test.mock3ml', True)
        check('layer/implml/test.test3ml', True)
        check('layer/implml/test.dummyml', False)
        check('layer/implml/test.xml', False)
        check('layer/implml/test', False)
        check('layer/implml/test.IMPLML', True)
        check('layer/implml/test.ImplML', True)
        check('layer/implml/test.Mock1ML', True)
    
    def test_read_all_impls(self):
        actual = list(plugin.get_impl_set(mock_config))
        actual_impls = []
        for impl in actual:
            if isinstance(impl, plugin.ImplContainer):
                actual_impls += impl.get_all_implementations()
            else:
                actual_impls.append(impl)
        
        expected = [
            MockImpl(['MockReader1', 'layer1/implml/single1.implml', {'x': '1'}, {'y': '2'}, {'z': '3'}]),
            MockImpl(['MockReader2', 'layer1/implml/single2.implml']),
            MockImpl(['MockReader3', 'layer1/implml/single3.implml', {'x': '1'}]),
            
            MockImpl(['MockReader1', 'layer1/implml/single1.mock1ml', {'x': '1'}, {'y': '2'}, {'z': '3'}]),
            MockImpl(['MockReader2', 'layer1/implml/single2.mock2ml']),
            MockImpl(['MockReader3', 'layer1/implml/single3.mock3ml', {'x': '1'}]),
            
            MockImpl(['MockReader3', 'layer1/implml/single3.test3ml', {'x': '1'}]),
            
            MockImpl(['MockReader1','layer1/implml/multi1.implml', {'y': '2', 'x': '1'}]),  
            MockImpl(['MockReader2', 'layer1/implml/multi1.implml', {'y': '20', 'x': '10'}]),
            MockImpl(['MockReader3', 'layer1/implml/multi1.implml', {'y': '200', 'x': '100'}, {'z': '300'}]),
            
            MockImpl(['MockReader1', 'layer1/implml/multi2.implml', {'x': '1', 'y': '2'}]),
            MockImpl(['MockReader2', 'layer1/implml/multi2.implml', {'x': '10', 'y': '20'}]),
            MockImpl(['MockReader3', 'layer1/implml/multi2.implml', {'x': '100', 'y': '200'}, {'z': '300'}]),
            
            MockImpl(['MockReader1', 'layer1/implml/multi3.implml', {'x': '1', 'y': '2'}]),
            MockImpl(['MockReader2', 'layer1/implml/multi3.implml', {'x': '1', 'y': '2'}]),
            MockImpl(['MockReader1', 'layer1/implml/multi3.implml', {'a': '1', 'b': '2'}]),
            MockImpl(['MockReader2', 'layer1/implml/multi3.implml', {'a': '1', 'b': '2'}]),
        ]
        
        if sorted(expected) != sorted(actual_impls):
            print 50 * '-'
            for impl in sorted(expected): print impl
            print 50 * '-'
            for impl in sorted(actual_impls): print impl
            print 50 * '-'
            
        
        self.assertEquals(sorted(expected), sorted(actual_impls))


class TestTempFeatureDefinition(unittest.TestCase):
    
    def setUp(self):
        plugin.ImplFactory.set_reader_classes_override(MOCK_READER_CLASSES)
    
    def tearDown(self):
        plugin.ImplFactory.set_reader_classes_override(None)
    
    def assert_contains_feature(self, config, ref, type, value):
        dview = config.get_default_view()
        feature = dview.get_feature(ref)
        self.assertEquals(type, feature.get_type())
        self.assertEquals(value, feature.get_value())
    
    def test_create_feature(self):
        config = api.Configuration("test.confml")
        def add_feature(setting_ref, value):
            config.add_feature(api.Feature(setting_ref), "ExistingFeature")
            config.add_data(api.Data(fqr="ExistingFeature." + setting_ref, value=value))
        add_feature('String', 'existing value')
        add_feature('Boolean', '0')
        add_feature('Boolean2', 'true')
        
        Tfd = _plugin_reader.TempVariableDefinition
        feadefs = [Tfd('TempFeature.String',    'string',   'testing'),
                   Tfd('TempFeature.Int',       'int',      '500'),
                   Tfd('TempFeature.Real',      'real',     '1.5'),
                   Tfd('TempFeature.Boolean',   'boolean',  'true'),
                   Tfd('TempFeature.String2',   'string',   'xyz ${ExistingFeature.String} zyx'),
                   Tfd('TempFeature.Boolean2',  'boolean',  '${ExistingFeature.Boolean}'),
                   Tfd('TempFeature.Boolean3',  'boolean',  '${ExistingFeature.Boolean2}')]
        for feadef in feadefs:
            feadef.create_feature(config)
        
        # This needs to be done or the default view won't be up-to-date
        config.recreate_default_view()
        
        self.assert_contains_feature(config, 'TempFeature.String', 'string', 'testing')
        self.assert_contains_feature(config, 'TempFeature.Int', 'int', 500)
        self.assert_contains_feature(config, 'TempFeature.Real', 'real', 1.5)
        self.assert_contains_feature(config, 'TempFeature.Boolean', 'boolean', True)
        self.assert_contains_feature(config, 'TempFeature.String2', 'string', 'xyz existing value zyx')
        self.assert_contains_feature(config, 'TempFeature.Boolean2', 'boolean', False)
        self.assert_contains_feature(config, 'TempFeature.Boolean3', 'boolean', True)
    
    def test_create_seq_feature(self):
        Tsfd = _plugin_reader.TempVariableSequenceDefinition
        feadef = Tsfd('TempFeature.Seq', [('String', 'string'),
                                          ('Int', 'int'),
                                          ('Real', 'real'),
                                          ('Boolean', 'boolean'),
                                          ('DefaultType', 'string')])
        config = api.Configuration("test.confml")
        feadef.create_feature(config)
        self.assert_contains_feature(config, 'TempFeature.Seq', 'sequence', [])
        self.assert_contains_feature(config, 'TempFeature.Seq.String', 'string', [])
        self.assert_contains_feature(config, 'TempFeature.Seq.Int', 'int', [])
        self.assert_contains_feature(config, 'TempFeature.Seq.Real', 'real', [])
        self.assert_contains_feature(config, 'TempFeature.Seq.Boolean', 'boolean', [])
        self.assert_contains_feature(config, 'TempFeature.Seq.DefaultType', 'string', [])
        
        fea = config.get_default_view().get_feature('TempFeature.Seq')
        fea.set_value([['test', 1, 2.0, True, 'foo']])
        self.assertEquals(fea.get_value(), [['test', 1, 2.0, True, 'foo']])
    
    def _create_mock_impl(self, temp_var_defs):
        impl = Mock()
        impl.ref = "test.implml"
        impl.get_temp_variable_definitions = lambda: temp_var_defs
        return impl
    
    def test_create_from_impl_container(self):
        impls = plugin.ImplSet()
        Tfd = _plugin_reader.TempVariableDefinition
        Tsfd = _plugin_reader.TempVariableSequenceDefinition
        
        feadefs = [Tfd('TempFeature.String',    'string',   'testing'),
                   Tfd('TempFeature.Int',       'int',      '500')]
        impls.add_implementation(self._create_mock_impl(feadefs))
        
        feadefs = [Tfd('TempFeature.Real',      'real',     '1.5'),
                   Tfd('TempFeature.Boolean',   'boolean',  'true')]
        impls.add_implementation(self._create_mock_impl(feadefs))
        
        feadefs = [Tsfd('TempFeature.Seq', [('String',  'string'),
                                            ('Int',     'int'),
                                            ('Real',    'real'),
                                            ('Boolean', 'boolean')])]
        impls.add_implementation(self._create_mock_impl(feadefs))
        
        config = api.Configuration("test.confml")
        impls.create_temp_features(config)
        
        self.assert_contains_feature(config, 'TempFeature.String', 'string', 'testing')
        self.assert_contains_feature(config, 'TempFeature.Int', 'int', 500)
        self.assert_contains_feature(config, 'TempFeature.Real', 'real', 1.5)
        self.assert_contains_feature(config, 'TempFeature.Boolean', 'boolean', True)
        self.assert_contains_feature(config, 'TempFeature.Seq', 'sequence', [])
        self.assert_contains_feature(config, 'TempFeature.Seq.String', 'string', [])
        self.assert_contains_feature(config, 'TempFeature.Seq.Int', 'int', [])
        self.assert_contains_feature(config, 'TempFeature.Seq.Real', 'real', [])
        self.assert_contains_feature(config, 'TempFeature.Seq.Boolean', 'boolean', [])
        
    
    def test_create_from_impl_container_with_duplicates(self):
        impls = plugin.ImplSet()
        
        Tfd = _plugin_reader.TempVariableDefinition
        feadefs = [Tfd('TempFeature.String',    'string',   'testing'),
                   Tfd('TempFeature.Int',       'int',      '500')]
        impls.add_implementation(self._create_mock_impl(feadefs))
        
        feadefs = [Tfd('TempFeature.Real',      'real',     '1.5'),
                   Tfd('TempFeature.Boolean',   'boolean',  'true'),
                   Tfd('TempFeature.Int',       'int',      '500')]
        impls.add_implementation(self._create_mock_impl(feadefs))
        
        config = api.Configuration("test.confml")
        self.assertRaises(exceptions.AlreadyExists, impls.create_temp_features, config)
    
    def test_create_from_impl_container_with_existing(self):
        impls = plugin.ImplSet()
        
        Tfd = _plugin_reader.TempVariableDefinition
        feadefs = [Tfd('TempFeature.String',    'string',   'testing'),
                   Tfd('TempFeature.Int',       'int',      '500')]
        impls.add_implementation(self._create_mock_impl(feadefs))
        
        feadefs = [Tfd('TempFeature.Real',      'real',     '1.5'),
                   Tfd('TempFeature.Boolean',   'boolean',  'true')]
        impls.add_implementation(self._create_mock_impl(feadefs))
        
        config = api.Configuration("test.confml")
        config.add_feature(api.Feature("Int"), "TempFeature")
        #self.assertRaises(exceptions.AlreadyExists, impls.create_temp_features, config)
        temp_feature_refs = impls.create_temp_features(config)
        self.assertEquals(temp_feature_refs.sort(), ['TempFeature.String', 'TempFeature.Real', 'TempFeature.Boolean'].sort())
        

class TestCommonImplmlDataReader(unittest.TestCase):
    
    def _read_data(self, xml_data):
        etree = utils.etree.fromstring(xml_data)
        return _plugin_reader.CommonImplmlDataReader.read_data(etree)
    
    def test_simple_all_tags(self):
        XML = """<test xmlns="http://www.symbianfoundation.org/xml/implml/1">
            <phase name="pre"/>
            <tag name="target" value="rofs3"/>
            <tempVariable ref="Temp.Feature" type="string" value="test"/>
            <tempVariableSequence ref="Temp.SeqFeature">
                <tempVariable ref="Sub" type="int"/>
            </tempVariableSequence>
            <settingRefsOverride>
                <settingRef value="Foo.Bar"/>
            </settingRefsOverride>
            <outputRootDir value="output_root"/>
            <outputSubDir value="output_sub"/>
        </test>"""
        actual = self._read_data(XML)
        
        expected = _plugin_reader.CommonImplmlData()
        expected.phase = 'pre'
        expected.tags = {'target': ['rofs3']}
        expected.tempvar_defs = [Tfd('Temp.Feature', 'string', 'test'),
                                      Tsfd('Temp.SeqFeature', [('Sub', 'int')])]
        expected.setting_refs_override = Sro(['Foo.Bar'])
        expected.output_root_dir = 'output_root'
        expected.output_sub_dir = 'output_sub'
        
        self.assertEquals(actual, expected)
    
    def test_invalid_phases(self):
        XML = """<test xmlns="http://www.symbianfoundation.org/xml/implml/1">
            <phase/>
        </test>"""
        self.assertRaises(exceptions.ParseError, self._read_data, XML)
        
        XML = """<test xmlns="http://www.symbianfoundation.org/xml/implml/1">
            <phase name="foo"/>
        </test>"""
        self.assertRaises(exceptions.ParseError, self._read_data, XML)
    
    def test_valid_phases(self):
        def run_test(phase ):
            xml_data = """<test xmlns="http://www.symbianfoundation.org/xml/implml/1">
                <phase name="%s"/>
            </test>""" % phase
            actual = self._read_data(xml_data)
            expected = _plugin_reader.CommonImplmlData()
            expected.phase = phase
            self.assertEquals(actual, expected)
        
        run_test('pre')
        run_test('normal')
        run_test('post')
    
    def test_invalid_temp_features(self):
        def run_test(element_xml_data):
            xml_data = """<test xmlns="http://www.symbianfoundation.org/xml/implml/1">
                %s
            </test>""" % element_xml_data
            self.assertRaises(exceptions.ParseError, self._read_data, xml_data)
        
        run_test('<tempVariable/>')
        run_test('<tempVariable ref="Foo.Bar" type="foo"/>')
        run_test('<tempVariable ref="Foo.Bar" type="foo" value="x"/>')
        
        run_test('<tempVariableSequence/>')
        run_test('<tempVariableSequence ref="Foo.Seq"/>')
        run_test('<tempVariableSequence ref="Foo.Seq"><tempVariable/></tempVariableSequence>')
        run_test('<tempVariableSequence ref="Foo.Seq"><tempVariable ref="SubFoo" type="foo"/></tempVariableSequence>')
    
    def test_valid_temp_feature_types(self):
        def run_test(type):
            # Test for simple features
            xml_data = """<test xmlns="http://www.symbianfoundation.org/xml/implml/1">
                <tempVariable ref="Foo.Bar" type="%s"/>
            </test>""" % type
            actual = self._read_data(xml_data)
            expected = _plugin_reader.CommonImplmlData()
            expected.tempvar_defs = [Tfd('Foo.Bar', type, '')]
            self.assertEquals(actual, expected)
            
            # Test for sequence features
            xml_data = """<test xmlns="http://www.symbianfoundation.org/xml/implml/1">
                    <tempVariableSequence ref="Foo.Bar">
                        <tempVariable ref="Sub" type="%s"/>
                    </tempVariableSequence>
                </test>""" % type
            actual = self._read_data(xml_data)
            expected = _plugin_reader.CommonImplmlData()
            expected.tempvar_defs = [Tsfd('Foo.Bar', [('Sub', type)])]
            self.assertEquals(actual, expected)
        
        run_test('string')
        run_test('int')
        run_test('real')
        run_test('boolean')
    
    def test_setting_refs_override(self):
        def check(xml, expected_refs):
            xml = '<test xmlns="http://www.symbianfoundation.org/xml/implml/1">%s</test>' % xml
            actual = self._read_data(xml)
            expected = _plugin_reader.CommonImplmlData()
            expected.setting_refs_override = Sro(expected_refs)
            self.assertEquals(actual, expected)
        
        check('<settingRefsOverride/>', [])
        check('<settingRefsOverride refsIrrelevant="false"/>', [])
        check('<settingRefsOverride refsIrrelevant="true"/>', None)
        check("""
                <settingRefsOverride>
                    <settingRef value="Foo.Bar"/>
                </settingRefsOverride>
            """,
            ['Foo.Bar'])
        check("""
                <settingRefsOverride>
                    <settingRef value="Foo.Bar"/>
                    <settingRef value="Foo.Baz"/>
                    <settingRef value="Test.Setting"/>
                </settingRefsOverride>
            """,
            ['Foo.Bar', 'Foo.Baz', 'Test.Setting'])

