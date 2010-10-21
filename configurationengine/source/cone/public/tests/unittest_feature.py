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

from cone.public import api, exceptions


class TestFeature(unittest.TestCase):    
    def comparefeatures(self,fea1,fea2):
        self.assertEquals(fea1.ref, fea2.ref)
        self.assertEquals(fea1.fqr, fea2.fqr)
        self.assertEquals(fea1.name, fea2.name)
        self.assertEquals(fea1.type, fea2.type)

    def test_create_feature(self):
        fea= api.Feature("foo")
        self.assertTrue(fea)

    def test_get_namespace(self):
        fea= api.Feature("foo")
        self.assertTrue(fea)
        self.assertEquals(fea.namespace,"")

    def test_get_ref(self):
        fea= api.Feature("foo")
        self.assertTrue(fea)
        self.assertEquals(fea.get_ref(),"foo")

    def test_create_config_with_namespace_and_get_fqr(self):
        conf =  api.Configuration("test.confml", namespace="com.nokia.s60")
        conf.add_feature(api.Feature("foo"))
        fea= conf.get_feature("foo")
        self.assertEquals(fea.namespace,"com.nokia.s60")
        self.assertEquals(fea.fqr,"com.nokia.s60.foo")

    def test_set_ref_and_get_all(self):
        conf =  api.Configuration("test.confml", namespace="com.nokia.s60")
        conf.add_feature(api.Feature("foo"))
        fea = conf.get_feature("foo")
        fea.set_ref("wlan")
        self.assertEquals(fea.get_ref(),"wlan")
        self.assertEquals(fea.namespace,"com.nokia.s60")
        self.assertEquals(fea.fqr,"com.nokia.s60.wlan")

    def test_create_subfeature_and_get_namespace(self):
        fea= api.Feature("foo")
        fea.add_feature(api.Feature("bar"))
        bar = fea.get_feature("bar")        
        self.assertTrue(bar)
        self.assertEquals(bar.get_ref(),"bar")
        self.assertEquals(bar.namespace,"foo")
        self.assertEquals(bar.fqr,"foo.bar")

    def test_create_subfeature_and_get_namespace_with_config(self):
        conf =  api.Configuration("test.confml", namespace="com.nokia.s60")
        conf.add_feature(api.Feature("foo"))
        fea= conf.get_feature("foo")
        fea.add_feature(api.Feature("bar"))
        bar = fea.get_feature("bar")        
        self.assertTrue(bar)
        self.assertEquals(bar.get_ref(),"bar")
        self.assertEquals(bar.namespace,"com.nokia.s60.foo")
        self.assertEquals(bar.fqr,"com.nokia.s60.foo.bar")

    def test_create_feature_proxy(self):
        fea= api.Feature("foo", name="foo bar")
        feaproxy = api._FeatureProxy("foo",fea)
        self.assertTrue(feaproxy.get_ref(),"foo")
        self.assertEquals(feaproxy.namespace,"")
        self.assertEquals(feaproxy.fqr,"foo")
        self.assertEquals(feaproxy.name,"foo bar")
        feaproxy.add_feature(api.Feature("bar", name="bar man"))
        self.assertTrue(feaproxy.bar.get_ref(),"bar")
        self.assertEquals(feaproxy.bar.namespace,"foo")
        self.assertEquals(feaproxy.bar.fqr,"foo.bar")
        self.assertEquals(feaproxy.bar.name,"bar man")
        
    def test_create_feature_proxy_with_options(self):
        fea= api.Feature("foo", name="foo bar")
        fea.add_option(api.Option('opt1', '1'))
        
        opts = {}
        opts['opt2'] = api.Option('opt2', '2')
        
        feaproxy = api._FeatureProxy("foo",fea, options=opts)
        self.assertTrue(feaproxy.get_ref(),"foo")
        self.assertEquals(feaproxy.namespace,"")
        self.assertEquals(feaproxy.fqr,"foo")
        self.assertEquals(feaproxy.name,"foo bar")
        feaproxy.add_feature(api.Feature("bar", name="bar man"))
        self.assertTrue(feaproxy.bar.get_ref(),"bar")
        self.assertEquals(feaproxy.bar.namespace,"foo")
        self.assertEquals(feaproxy.bar.fqr,"foo.bar")
        self.assertEquals(feaproxy.bar.name,"bar man")
        opts2 = {}
        opts2['opt2'] = api.Option('opt2', '2')
        opts2['opt1'] = api.Option('opt1', '1')
        self.assertEquals(feaproxy.list_options(), ['value_1', 'value_2'])
        self.assertEquals(feaproxy.get_option('value_2').get_value(), '2')
        self.assertEquals(feaproxy.get_option('value_1').get_value(), '1')
        
    def test_create_feature_proxy_has_attribute(self):
        fea= api.Feature("foo", name="foo bar")
        feaproxy = api._FeatureProxy("foo",fea)
        self.assertEquals(feaproxy.name, "foo bar")
        self.assertEquals(feaproxy.has_attribute('name'), False)
        feaproxy.name = "test"
        self.assertEquals(feaproxy.has_attribute('name'), True)
        self.assertEquals(feaproxy.name, "test")

    def test_feature_proxy_get_proxied_obj(self):
        fea= api.Feature("foo", name="foo bar")
        feaproxy = api._FeatureProxy("foo",fea)
        proxied = feaproxy.get_proxied_obj()
        self.assertFalse(proxied == None)
        self.assertEquals(fea, proxied)
        self.assertEquals(feaproxy.get_proxied_obj(), feaproxy._obj)
        
    def test_create_feature_data(self):
        dataobj = api.Data(ref="foo", value=132)
        self.assertTrue(dataobj.fqr,"foo")
        self.assertTrue(dataobj.get_value(),123)
        self.assertTrue(dataobj.value,123)

    def test_create_feature_data_proxy(self):
        fea= api.Feature("foo")
        feaproxy = api._FeatureDataProxy("foo",fea)
        self.assertTrue(feaproxy.get_ref(),"foo")
        self.assertEquals(feaproxy._get_data(),None)
        self.assertEquals(feaproxy._get_value(),None)
        feaproxy._add_data(api.Data(ref="foo", value=123))
        self.assertEquals(feaproxy._get_data().get_value(),123)
        feaproxy._add_data(api.Data(ref="foo", value=321))
        self.assertEquals(feaproxy._get_data().get_value(),321)
        self.assertEquals(feaproxy._get_datas()[0].get_value(),123)
        self.assertEquals(feaproxy._get_datas()[1].get_value(),321)
        self.assertEquals(feaproxy._get_values(),[123,321])

    def test_access_feature_data_proxy_children_with_sequence_operations(self):
        fea= api.Feature("foo")
        feaproxy = api._FeatureDataProxy("foo",fea)
        feaproxy.add_feature(api.Feature("child1"))
        feaproxy.add_feature(api.Feature("child2"))
        feaproxy.add_feature(api.Feature("?child"))
        feaproxy.add_feature(api.Feature("child3"))
        feaproxy.add_feature(api.Feature("child4"))
        self.assertEquals(len(feaproxy),4)
        self.assertEquals(feaproxy[0].get_ref(),'child1')
        self.assertEquals(feaproxy[1].get_ref(),'child2')
        self.assertEquals(feaproxy[2].get_ref(),'child3')
        self.assertEquals(feaproxy[3].get_ref(),'child4')
        
        del feaproxy[2]
        self.assertEquals(len(feaproxy),3)
        self.assertEquals(feaproxy[0].get_ref(),'child1')
        self.assertEquals(feaproxy[1].get_ref(),'child2')
        self.assertEquals(feaproxy[2].get_ref(),'child4')
        self.assertEquals(feaproxy[2].get_ref(),'child4')
        self.assertEquals(feaproxy.get_feature('?child').get_ref(),'?child')

    def test_create_boolean_feature(self):
        fea = api.Feature('test',type='boolean')
        vset = fea.get_valueset()
        self.assertTrue(vset <= api.ValueSet([True,False]))
        self.assertTrue(len(vset) == 2)
        self.assertTrue(True in vset)
        self.assertTrue(False in vset)
        self.assertFalse(123 in vset)

    def test_create_string_feature(self):
        fea = api.Feature('test',type='string')
        vset = fea.get_valueset()
        self.assertTrue('test' in vset)
        self.assertTrue('foobar' in vset)
        self.assertFalse(False in vset)
        self.assertFalse(123 in vset)

    def test_create_integer_feature(self):
        fea = api.Feature('test',type='int')
        vset = fea.get_valueset()
        self.assertFalse('test' in vset)
        self.assertFalse('foobar' in vset)
        self.assertTrue(False in vset)
        self.assertTrue(123 in vset)
        self.assertTrue(0 in vset)
        self.assertTrue(100000000 in vset)
        self.assertFalse(-1 in vset)
        self.assertFalse(0.2 in vset)

    def test_create_selection_feature(self):
        fea = api.Feature('test',type='selection')
        fea.create_option('test', '1')
        fea.create_option('one', '2')
        fea.create_option('two', '3')
        vset = fea.get_valueset()
        self.assertTrue('1' in vset)
        self.assertFalse('foo' in vset)
        self.assertTrue('2' in vset)
        self.assertTrue('3' in vset)
        self.assertEquals(fea.get_option('value_2').get_name(), 'one')
    
    def test_create_sequence_feature(self):
        fea = api.FeatureSequence('test')
        fea.create_feature('child1',type='int')
        fea.create_feature('child2', name="test")
        fea.create_feature('child3')
        self.assertEquals(fea.get_type(), 'sequence')
        self.assertEquals(fea.list_features(), ['child1','child2','child3'])
        self.assertEquals(fea.get_feature('child1').type, 'int')
        self.assertEquals(fea.get_feature('child2').type, None)
        self.assertEquals(fea.get_feature('child2').name, 'test')

    def test_feature_get_dict(self):
        fea= api.Feature("foo", type='int')
        self.assertEquals(fea._dict(), {'ref': 'foo',
                                        'type': 'int',
                                        'name': None,
                                        'extensionAttributes': [],
                                        'relevant': None,
                                        'constraint': None })

    def test_clone_single_feature(self):
        fea= api.Feature("foo", type='int')
        fea2 = fea._clone()
        self.comparefeatures(fea,fea2)

    def test_clone_feature_with_subfeatures(self):
        fea= api.Feature("foo")
        fea.add_feature(api.Feature("child1",type='string'))
        fea.create_feature("child2",type='int')
        fea.child1.add_feature(api.Feature("child12",type='int'))
        fea2 = fea._clone()
        self.comparefeatures(fea,fea2)
        fea3 = fea._clone(recursion=True, recursion_depth=1)
        self.comparefeatures(fea,fea3)
        self.comparefeatures(fea.get_feature('child1'),fea3.get_feature('child1'))
        self.comparefeatures(fea.get_feature('child2'),fea3.get_feature('child2'))
        self.assertEquals(fea3.child1.list_features(),[])
        fea4 = fea._clone(recursion=True)
        self.comparefeatures(fea,fea4)
        self.comparefeatures(fea.get_feature('child1'),fea4.get_feature('child1'))
        self.comparefeatures(fea.get_feature('child2'),fea4.get_feature('child2'))
        self.assertEquals(fea4.child1.list_features(),['child12'])
        self.comparefeatures(fea.child1.get_feature('child12'),fea4.child1.get_feature('child12'))

    def test_clone_feature_with_options(self):
        fea= api.Feature("foo")
        fea.add_feature(api.Feature("child1",type='selection'))
        fea.add_feature(api.Feature("child2",type='int'))
        fea.child1.create_option('one','1')
        fea.child1.create_option('two','2')
        fea.child1.create_option('three','3')
        fea2 = fea._clone(recursion=True)
        self.comparefeatures(fea,fea2)
        self.comparefeatures(fea.get_feature('child1'),fea2.get_feature('child1'))
        self.assertEquals(fea.child1.list_options(),fea2.child1.list_options())

    def test_compare_features(self):
        fea1= api.Feature("foo")
        fea2= api.Feature("foo")
        fea3= api.Feature("foo", type='boolean')
        fea4= api.Feature("foo", bar='yes')
        fea5= api.Feature("foo", bar='yes')
        self.assertTrue(fea1._compare(fea2))
        self.assertFalse(fea1._compare(fea3))
        self.assertTrue(fea1._compare(fea4))
        self.assertTrue(fea5._compare(fea4, ['bar']))
        self.assertTrue(fea1._compare(fea2, ['bar']))

class TestFeatureSequence(unittest.TestCase):
    def comparefeatures(self,fea1,fea2):
        self.assertEquals(fea1.ref, fea2.ref)
        self.assertEquals(fea1.fqr, fea2.fqr)
        self.assertEquals(fea1.name, fea2.name)
        self.assertEquals(fea1.type, fea2.type)

    # @test 
    def test_create_feature(self):
        fea= api.FeatureSequence("foo")
        self.assertTrue(fea)

    def test_create_feature_with_children(self):
        fea= api.FeatureSequence("foo")
        fea.add_feature(api.Feature('child1'))
        fea.add_feature(api.Feature('child2'))
        fea.add_feature(api.Feature('child3'))
        self.assertEquals(fea.list_features(),['child1','child2','child3'])
        self.assertEquals(fea.get_column_features()[0].ref,'child1')
        self.assertEquals(fea.get_column_features()[1].ref,'child2')
        self.assertEquals(fea.get_column_features()[2].ref,'child3')

    def test_create_configuration_with_sequence_and_get_default_view(self):
        fea= api.FeatureSequence("foo")
        fea.add_feature(api.Feature('child1'))
        fea.add_feature(api.Feature('child2'))
        fea.add_feature(api.Feature('child3'))
        config = api.Configuration('foo.confml')
        config.add_feature(fea)
        dview = config.get_default_view()
        self.assertEquals(dview.list_all_features(),['foo','foo.child1','foo.child2','foo.child3'])

    def test_create_configuration_with_sequence_and_add_data_with_default_view(self):
        fea= api.FeatureSequence("foo")
        fea.add_feature(api.Feature('child1'))
        fea.add_feature(api.Feature('child2'))
        fea.add_feature(api.Feature('child3'))
        config = api.Configuration('foo.confml')
        config.add_feature(fea)
        dview = config.get_default_view()
        foofea = dview.get_feature('foo')
        
        data = api.Data(ref='foo')
        data._add(api.Data(ref='child1',value='test1'))
        data._add(api.Data(ref='child2',value='test2'))
        data._add(api.Data(ref='child3',value='test3'))
        foofea.add_data(data)
        data1 = api.Data(ref='foo', policy='append')
        data1._add(api.Data(ref='child1',value='jee'))
        data1._add(api.Data(ref='child2',value='oo'))
        data1._add(api.Data(ref='child3',value='aa'))
        
        foofea.add_data(data1)
        self.assertEquals(len(foofea.get_data()), 2)
        
        self.assertEquals(foofea.get_data()[0].list_features(), ['child1','child2','child3'])
        self.assertEquals(foofea.get_data()[0].get_feature('child1').get_value(), 'test1')
        self.assertEquals(foofea.get_data()[0].get_feature('child2').get_value(), 'test2')
        self.assertEquals(foofea.get_data()[0].get_feature('child3').get_value(), 'test3')

        self.assertEquals(foofea.get_data()[1].list_features(), ['child1','child2','child3'])
        self.assertEquals(foofea.get_data()[1].get_feature('child1').get_value(), 'jee')
        self.assertEquals(foofea.get_data()[1].get_feature('child2').get_value(), 'oo')
        self.assertEquals(foofea.get_data()[1].get_feature('child3').get_value(), 'aa')

        self.assertEquals(foofea.get_value(), [['test1','test2','test3'],
                                               ['jee','oo','aa']])
        self.assertEquals(foofea.get_data()[0][0].get_value(), 'test1')
        # Test recurse
        for row in foofea.get_data():
            for col in row:
                print col.get_value(),
            print

    def test_create_configuration_with_sequence_and_add_values_with_default_view(self):
        fea= api.FeatureSequence("foo")
        fea.add_feature(api.Feature('child1'))
        fea.add_feature(api.Feature('child2'))
        fea.add_feature(api.Feature('child3'))
        config = api.Configuration('foo.confml')
        config.add_feature(fea)
        dview = config.get_default_view()
        foofea = dview.get_feature('foo')
        # Test adding a data row with array
        foofea.add_sequence(['1','2','3'])
        foofea.add_sequence(['4','5','6'])
        foofea.add_sequence(['7','8','9'])
        print foofea.get_data()[0].get_feature('child1').get_value()
        self.assertEquals(len(foofea.get_data()), 3)
        self.assertEquals(foofea.get_value(), [['1','2','3'],
                                               ['4','5','6'],
                                               ['7','8','9']
                                               ])

    def test_create_configuration_with_sequence_and_get_column_value(self):
        fea= api.FeatureSequence("foo")
        c1 = fea.create_feature('child1')
        c11 = c1.create_feature('child11')
        c2 = fea.create_feature('child2')
        c3 = fea.create_feature('child3')
        config = api.Configuration('foo.confml')
        config.add_feature(fea)
        dview = config.get_default_view()
        foofea = dview.get_feature('foo')
        # Test adding a data row with array
        foofea.value = [[['1'],'2','3'],[['4'],'5','6'],[['7'],'8','9']]
        self.assertEquals(api.get_column_value(foofea, 'child1'), [['1'],['4'],['7']])
        self.assertEquals(foofea.child1.value, [['1'],['4'],['7']])
        self.assertEquals(foofea.child1.child11.value, ['1','4','7'])
        self.assertEquals(foofea.child2.value, ['2','5','8'])
        self.assertEquals(foofea.value, [[['1'],'2','3'],
                                         [['4'],'5','6'],
                                         [['7'],'8','9']])

    def test_create_configuration_with_sequence_and_set_value_via_column(self):
        fea= api.FeatureSequence("foo")
        fea.add_feature(api.Feature('child1'))
        fea.add_feature(api.Feature('child2'))
        fea.add_feature(api.Feature('child3'))
        config = api.Configuration('foo.confml')
        config.add_feature(fea)
        dview = config.get_default_view()
        foofea = dview.get_feature('foo')
        # Test adding a data row with array
        foofea.value = [['1','2','3'],['4','5','6'],['7','8','9']]
        self.assertEquals(foofea.get_value(), [['1','2','3'],
                                               ['4','5','6'],
                                               ['7','8','9']
                                               ])

        api.set_column_value(foofea, 'child1', ['0','0','0'])
        self.assertEquals(foofea.get_value(), [['0','2','3'],
                                               ['0','5','6'],
                                               ['0','8','9']
                                               ])
        self.assertRaises(exceptions.ConeException, api.set_column_value, foofea, 'child2', 'over')
        self.assertRaises(exceptions.ConeException, api.set_column_value, foofea, 'child2', ['0','0','0', 'over'])
        foofea.child3.value = ['0','0','0'] 
        self.assertEquals(foofea.get_value(), [['0','2','0'],
                                               ['0','5','0'],
                                               ['0','8','0']
                                               ])

    def test_create_configuration_with_sequence_and_add_sequence_value_directly(self):
        fea= api.FeatureSequence("foo")
        fea.add_feature(api.Feature('child1'))
        fea.add_feature(api.Feature('child2'))
        fea.add_feature(api.Feature('child3'))
        config = api.Configuration('foo.confml')
        config.add_feature(fea)
        dview = config.get_default_view()
        foofea = dview.get_feature('foo')
        # Test adding a data row with array
        foofea.set_value([['1','2','3'],
                         ['4','5','6'],
                         ['7','8','9']
                         ])
        self.assertEquals(len(foofea.get_data()), 3)
        self.assertEquals(foofea.get_value(), [['1','2','3'],
                                               ['4','5','6'],
                                               ['7','8','9']
                                               ])
        
        # Check the data element values
        data_elem_values = [(d.fqr, d.value) for d in config._traverse(type=api.Data)]
        self.assertEquals(data_elem_values,
            [('foo', None),
             ('foo.child1', '1'),
             ('foo.child2', '2'),
             ('foo.child3', '3'),
             ('foo', None),
             ('foo.child1', '4'),
             ('foo.child2', '5'),
             ('foo.child3', '6'),
             ('foo', None),
             ('foo.child1', '7'),
             ('foo.child2', '8'),
             ('foo.child3', '9'),])
    
    def test_set_sequence_to_empty(self):
        fea= api.FeatureSequence("foo")
        fea.add_feature(api.Feature('child1'))
        fea.add_feature(api.Feature('child2'))
        fea.add_feature(api.Feature('child3'))
        config = api.Configuration('foo.confml')
        config.add_feature(fea)
        dview = config.get_default_view()
        foofea = dview.get_feature('foo')
        # Test adding a data row with array
        foofea.set_value([['1','2','3'],
                          ['4','5','6'],
                          ['7','8','9']])
        self.assertEquals(len(foofea.get_data()), 3)
        self.assertEquals(foofea.get_value(), [['1','2','3'],
                                               ['4','5','6'],
                                               ['7','8','9']])
        self.assertEquals(foofea.child1.get_value(), ['1','4','7'])
        self.assertEquals(foofea.child2.get_value(), ['2','5','8'])
        self.assertEquals(foofea.child3.get_value(), ['3','6','9'])
        
        # Set empty and check that the single empty data item is created
        foofea.set_value([])
        data_elem_values = [(d.fqr, d.value) for d in config._traverse(type=api.Data)]
        self.assertEquals(data_elem_values, [('foo', None)])
        
        # Check that get_value() still works correctly
        self.assertEquals(foofea.get_value(), [])
        self.assertEquals(foofea.child1.get_value(), [])
        self.assertEquals(foofea.child2.get_value(), [])
        self.assertEquals(foofea.child3.get_value(), [])
        self.assertEquals(foofea.get_original_value(), [])
        self.assertEquals(foofea.child1.get_original_value(), [])
        self.assertEquals(foofea.child2.get_original_value(), [])
        self.assertEquals(foofea.child3.get_original_value(), [])
        
        # Check that column-level set_value() reports errors correctly
        self.assertRaises(exceptions.ConeException, foofea.child1.set_value, ['10', '11'])
        self.assertRaises(exceptions.ConeException, foofea.child1.set_value, ['10'])
        foofea.child1.set_value([])
        
        # Check that calling add_sequence() after set_value([]) works correctly
        foofea.add_sequence(['1', '2', '3'])
        self.assertEquals(foofea.get_value(), [['1', '2', '3']])
        self.assertEquals(foofea.child1.get_value(), ['1'])
        self.assertEquals(foofea.get_original_value(), [['1', '2', '3']])
        data_elem_values = [(d.fqr, d.value) for d in config._traverse(type=api.Data)]
        self.assertEquals(data_elem_values,
            [('foo', None),
             ('foo.child1', '1'),
             ('foo.child2', '2'),
             ('foo.child3', '3'),])
        
        # Check that explicitly setting all Nones works
        foofea.set_value([[None, None, None]])
        self.assertEquals(foofea.get_value(), [[None, None, None]])
        self.assertEquals(foofea.child1.get_value(), [None])
        self.assertEquals(foofea.get_original_value(), [[None, None, None]])
        data_elem_values = [(d.fqr, d.value) for d in config._traverse(type=api.Data)]
        self.assertEquals(data_elem_values,
            [('foo', None),
             ('foo.child1', None),
             ('foo.child2', None),
             ('foo.child3', None),])

    def test_create_configuration_and_access_feature_value_with_property(self):
        config = api.Configuration('foo.confml')
        fea= api.Feature("foo")
        config.add_feature(fea)
        fea.set_value('test')
        self.assertEquals(fea.value,'test')
        dview = config.get_default_view()
        feaproxy = dview.get_feature('foo')
        val = feaproxy.value
        self.assertEquals(val,'test')
        feaproxy.value = 'test2'
        self.assertEquals(feaproxy.value,'test2')
        del feaproxy.value
        self.assertEquals(feaproxy.value,None)
        feaproxy.value = 'test3'
        self.assertEquals(feaproxy.value,'test3')

    def test_create_configuration_and_access_feature_type_with_property(self):
        config = api.Configuration('foo.confml')
        fea= api.Feature("foo", type='int')
        config.add_feature(fea)
        self.assertEquals(fea.type, 'int') 
        dview = config.get_default_view()
        feaproxy = dview.get_feature('foo')
        self.assertEquals(feaproxy.type, 'int') 

    def test_create_feature_seq_and_access_feature_value_with_property(self):
        config = api.Configuration('foo.confml')
        fea= api.FeatureSequence("foo")
        fea.add_feature(api.Feature('child1'))
        fea.add_feature(api.Feature('child11'),'child1')
        fea.add_feature(api.Feature('child2'))
        fea.add_feature(api.Feature('child3'))
        config.add_feature(fea)
        dview = config.get_default_view()
        foofea = dview.get_feature('foo')
        # Test adding a data row with array
        foofea.set_value([[['1'],'2','3'],
                         [['4'],'5','6'],
                         [['7'],'8','9']
                         ])
        self.assertEquals(foofea.value, [[['1'],'2','3'],
                                         [['4'],'5','6'],
                                         [['7'],'8','9']
                                        ])

        foofea.value = [[['1'],'2','3'],
                         [['7'],'8','9']
                        ]
        
        self.assertEquals(foofea.data[0].value,[['1'],'2','3'])
        self.assertEquals(foofea.data[1].value,[['7'],'8','9'])
        self.assertEquals(foofea.data[1][1].value,'8')
        self.assertEquals(foofea.get_value(), [[['1'],'2','3'],
                                               [['7'],'8','9']
                                               ])
        self.assertEquals(foofea.child1.child11.value,['1','7'])
        self.assertEquals(foofea.child1.value,[['1'],['7']])

    def test_create_feature_seq_and_access_empty_data(self):
        config = api.Configuration('foo.confml')
        fea= api.FeatureSequence("foo")
        fea.add_feature(api.Feature('child1'))
        fea.add_feature(api.Feature('child11'),'child1')
        fea.add_feature(api.Feature('child2'))
        fea.add_feature(api.Feature('child3'))
        config.add_feature(fea)
        dview = config.get_default_view()
        foofea = dview.get_feature('foo')
        foofea.value = []
        self.assertEquals(foofea.value, [])

    def test_create_feature_seq_get_sequence_parent(self):
        fea= api.FeatureSequence("foo")
        fea.add_feature(api.Feature('child1'))
        fea.add_feature(api.Feature('child11'),'child1')
        fea.add_feature(api.Feature('child2'))
        fea.add_feature(api.Feature('child3'))
        self.assertEquals(fea.child1.get_sequence_parent(), fea)
        self.assertEquals(fea.child1.child11.get_sequence_parent(), fea)

    def test_clone_feature_sequence(self):
        fea= api.FeatureSequence("foo")
        fea.add_feature(api.Feature('child1'))
        fea.add_feature(api.Feature('child2'))
        fea.add_feature(api.Feature('child3'))
        fea2 = fea._clone(recursion=True)
        self.comparefeatures(fea,fea2)
        self.assertEquals(fea.list_features(),fea2.list_features())

    def test_create_configuration_with_sequence_and_mapping_properties(self):
        fea = api.FeatureSequence("SequenceSetting", mapKey='KeySubSetting', mapValue="ValueSubSetting")
        fea.add_feature(api.Feature('KeySubSetting'))
        fea.add_feature(api.Feature('ValueSubSetting'))
        
        config = api.Configuration('foo.confml')
        config.add_feature(fea)
        dview = config.get_default_view()
        seqfea = dview.get_feature("SequenceSetting")

        self.assertEquals(seqfea.mapKey, "KeySubSetting")
        self.assertEquals(seqfea.mapValue, "ValueSubSetting")
        #add item 1
        data = api.Data(ref='SequenceSetting')
        data._add(api.Data(ref='KeySubSetting',value='Default'))
        data._add(api.Data(ref='ValueSubSetting',value='Default value'))
        seqfea.add_data(data)
        
        #add item 2
        data1 = api.Data(ref='SequenceSetting', policy='append')
        data1._add(api.Data(ref='KeySubSetting',value='Key 1'))
        data1._add(api.Data(ref='ValueSubSetting',value='Value 1'))
        seqfea.add_data(data1)
        
        self.assertEquals(len(seqfea.get_data()), 2)
        
    def test_get_set_template_single_data_level(self):
        # Create a sequence feature with only a single level of sub-features
        # (i.e. no sub-sub-features)
        config = api.Configuration('foo.confml')
        seq = api.FeatureSequence("seq")
        seq.add_feature(api.Feature('child1'))
        seq.add_feature(api.Feature('child2'))
        seq.add_feature(api.Feature('child3'))
        config.add_feature(seq)
        
        # Add a template for the sequence with the data elements under it
        # in a different order than what the features were defined in
        template_data = api.Data(ref='seq', template=True)
        template_data.add(api.Data(ref='child2', value='foo2'))
        template_data.add(api.Data(ref='child3', value='foo3'))
        template_data.add(api.Data(ref='child1', value='foo1'))
        config.add_data(template_data)
        
        # Get the template data (should be in order)
        dview = config.get_default_view()
        seq = dview.get_feature('seq')
        self.assertEquals(seq.get_template(), ['foo1', 'foo2', 'foo3'])
        
        seq.set_template(['x1', 'x2', 'x3'])
        self.assertEquals(seq.get_template(), ['x1', 'x2', 'x3'])
        
        seq.set_template(None)
        self.assertEquals(seq.get_template(), None)
        
        # Test attempting to set invalid template data
        self.assertRaises(TypeError, seq.set_template, 'foo')
        self.assertRaises(ValueError, seq.set_template, [])
        self.assertRaises(ValueError, seq.set_template, ['foo', 'bar'])
        self.assertRaises(ValueError, seq.set_template, [['foo', 'x'], 'bar'])
    
    def test_get_set_template_two_data_levels(self):
        # Create a sequence feature with two levels of sub-features
        config = api.Configuration('foo.confml')
        seq = api.FeatureSequence("seq")
        seq.add_feature(api.Feature('a1'))
        seq.add_feature(api.Feature('b1'), 'a1')
        seq.add_feature(api.Feature('b2'), 'a1')
        seq.add_feature(api.Feature('a2'))
        seq.add_feature(api.Feature('a3'))
        config.add_feature(seq)
        
        # Add a template for the sequence with the data elements under it
        # in a different order than what the features were defined in
        template_data = api.Data(ref='seq', template=True)
        template_data.add(api.Data(ref='a3', value='t: a3'))
        data_a1 = api.Data(ref='a1')
        data_a1.add(api.Data(ref='b2', value='t: a1.b2'))
        data_a1.add(api.Data(ref='b1', value='t: a1.b1'))
        template_data.add(data_a1)
        template_data.add(api.Data(ref='a2', value='t: a2'))
        config.add_data(template_data)
        
        template_data = api.Data(ref='seq')
        template_data.add(api.Data(ref='a3', value='t: a3'))
        data_a1 = api.Data(ref='a1')
        data_a1.add(api.Data(ref='b2', value='t: a1.b2'))
        data_a1.add(api.Data(ref='b1', value='t: a1.b1'))
        template_data.add(data_a1)
        template_data.add(api.Data(ref='a2', value='t: a2'))
        config.add_data(template_data, api.FeatureSequence.POLICY_APPEND)
        
        # Get the template data (should be in order)
        dview = config.get_default_view()
        seq = dview.get_feature('seq')
        self.assertEquals(seq.value, [[['t: a1.b1', 't: a1.b2'], 't: a2', 't: a3']])
        self.assertEquals(seq.get_template(), [['t: a1.b1', 't: a1.b2'], 't: a2', 't: a3'])
        
        # Set the template and get it again
        seq.set_template([['t: a1.b1 (x)', 't: a1.b2 (x)'], 't: a2 (x)', 't: a3 (x)'])
        self.assertEquals(seq.get_template(), [['t: a1.b1 (x)', 't: a1.b2 (x)'], 't: a2 (x)', 't: a3 (x)'])
    
    def test_sequence_add_data_and_set_template(self):
        # Create a simple configuration with a sequence feature
        config = api.Configuration('foo.confml')
        fea = api.Feature('fea')
        config.add_feature(fea)
        seq = api.FeatureSequence("seq")
        fea.add_feature(seq)
        seq.add_feature(api.Feature('child1'))
        seq.add_feature(api.Feature('child2'))
        
        sequence = config.get_default_view().get_feature('fea.seq')
        
        # Check that initially the sequence is empty
        self.assertEquals(sequence.get_template(), None)
        self.assertEquals(sequence.value, [])
        
        # Add some data and check again
        sequence.add_sequence(['row1', 'foo'])
        sequence.add_sequence(['row2', 'foo']) 
        self.assertEquals(sequence.get_template(), None)
        self.assertEquals(sequence.value, [['row1', 'foo'],
                                           ['row2', 'foo']])

        # Setting the template should not affect the data
        sequence.set_template(['t1', 't2'])
        self.assertEquals(sequence.get_template(), ['t1', 't2'])
        self.assertEquals(sequence.value, [['row1', 'foo'],
                                           ['row2', 'foo']])
        
        sequence.set_template(['T1', 'T2'])
        sequence.add_sequence(['row3', 'foo'])
        self.assertEquals(sequence.get_template(), ['T1', 'T2'])
        self.assertEquals(sequence.value, [['row1', 'foo'],
                                           ['row2', 'foo'],
                                           ['row3', 'foo']])
    
    def test_set_value_method_for_sequence(self):
        config = api.Configuration('foo.confml')
        fea = api.Feature('Some')
        config.add_feature(fea)
        seq = api.FeatureSequence("Sequence")
        fea.add_feature(seq)
        seq.add_feature(api.Feature('Feature'))
        
        seq = config.get_default_view().get_feature('Some.Sequence')
        value = [['foo'], ['bar']]
        seq.set_value(value)
        
        self.assertEquals(seq.value, [['foo'], ['bar']])
        self.assertEquals(seq.Feature.value, ['foo', 'bar'])
    
    def test_simple_name_id_mapping(self):
        config = api.Configuration('foo.confml')
        seq = api.FeatureSequence('seq', mapKey='sub1', mapValue='sub1')
        seq.add_feature(api.Feature('sub1'))
        seq.add_feature(api.Feature('sub2'))
        config.add_feature(seq)
        config.add_feature(api.Feature('target'))
        
        config.add_data(api.Data(fqr='seq.sub1', value='foo'))
        config.add_data(api.Data(fqr='seq.sub2', value='bar'))
        config.add_data(api.Data(fqr='target', map="seq[@key='foo']"))
        
        fea = config.get_default_view().get_feature('target')
        self.assertEquals(fea.value, 'foo')
        self.assertEquals(fea.get_value(), 'foo')
        self.assertEquals(fea.get_original_value(), 'foo')
        
        seq.mapValue = 'sub2'
        self.assertEquals(fea.value, 'bar')
        self.assertEquals(fea.get_value(), 'bar')
        self.assertEquals(fea.get_original_value(), 'bar')
        
if __name__ == '__main__':
    unittest.main()
