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
import sys,os
import __init__

from cone.public import api,exceptions,utils


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
        fea.add_feature(api.Feature('child1',type='int'))
        fea.add_feature(api.Feature('child2'))
        fea.add_feature(api.Feature('child3'))
        self.assertEquals(fea.get_type(), 'sequence')
        self.assertEquals(fea.list_features(), ['child1','child2','child3'])

    def test_feature_get_dict(self):
        fea= api.Feature("foo", type='int')
        self.assertEquals(fea._dict(), {'ref': 'foo','type': 'int', 'name': 'foo'})

    def test_clone_single_feature(self):
        fea= api.Feature("foo", type='int')
        fea2 = fea._clone()
        self.comparefeatures(fea,fea2)

    def test_clone_feature_with_subfeatures(self):
        fea= api.Feature("foo")
        fea.add_feature(api.Feature("child1",type='string'))
        fea.add_feature(api.Feature("child2",type='int'))
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
        config = api.Configuration('foo.confml')
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

        self.assertEquals(seqfea.get_map_key().name,"KeySubSetting")
        self.assertEquals(seqfea.get_map_value().name,"ValueSubSetting")
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
        
        self.assertEquals(seqfea.get_map_key_value('Default'),'Default value')
        self.assertEquals(seqfea.get_map_key_value('Key 1'),'Value 1')
if __name__ == '__main__':
      unittest.main()
      
