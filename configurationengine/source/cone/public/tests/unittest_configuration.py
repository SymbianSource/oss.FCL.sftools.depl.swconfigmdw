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
import os
import pickle 

from cone.public import api,exceptions
from cone.storage import persistentdictionary
from testautomation.utils import remove_if_exists

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class TestConfiguration(unittest.TestCase):    
    def setUp(self):
        pass

    # @test 
    def test_create_configuration(self):
        conf = api.Configuration("testmee.confml")
        self.assertTrue(conf)

    def test_configuration_reduce_ex(self):
        prj = api.Project(api.Storage('.'))
        conf = api.Configuration("testmee.confml")
        prj.add_configuration(conf)
        tpl = conf.__reduce_ex__(2)
        self.assertEquals(tpl[2]['_storeint'],prj)
        self.assertEquals(tpl[2]['path'],'testmee.confml')
        
    def test_configuration_pickle(self):
        remove_if_exists(os.path.join(ROOT_PATH,'temp'))
        prj = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'temp'), 'w'))
        conf = api.Configuration("testmee.confml")
        prj.add_configuration(conf, True)
        prj.save()
        dfile  = open(os.path.join(ROOT_PATH,'temp/out.dat'), 'w')
        pickle.dump(conf, dfile)
        dfile.close()
        dfile  = open(os.path.join(ROOT_PATH,'temp/out.dat'))
        conf2 = pickle.load(dfile)
        self.assertEquals(conf2.path,'testmee.confml')
        self.assertEquals(conf2.name,'testmee_confml')


    def test_get_root_configuration(self):
        conf = api.Configuration("testmee.confml")
        self.assertEquals(conf.get_root_configuration(),conf)
        conf.add_configuration(api.Configuration("foo/foo.confml")) 
        conf.add_configuration(api.Configuration("fii/fii.confml")) 
        conf.fii__fii_confml.add_configuration(api.Configuration("fii/foo.confml"))
        self.assertEquals(conf.fii__fii_confml.get_root_configuration(),conf)
        self.assertEquals(conf.foo__foo_confml.get_root_configuration(),conf)
        self.assertEquals(conf.fii__fii_confml.fii__foo_confml.get_root_configuration(),conf)

    def test_get_last_configuration(self):
        conf = api.Configuration("testmee.confml")
        conf.add_configuration(api.Configuration("foo/foo.confml")) 
        conf.add_configuration(api.Configuration("fii/fii.confml")) 
        conf.add_configuration(api.Configuration("hii/hii.confml")) 
        conf.fii__fii_confml.add_configuration(api.Configuration("fii/foo.confml"))
        self.assertEquals(conf.list_configurations(), ["foo/foo.confml","fii/fii.confml","hii/hii.confml"])

        self.assertEquals(conf.get_configuration_by_index(-1).get_path(), "hii/hii.confml")
        self.assertEquals(conf.get_configuration_by_index(0).get_path(), "foo/foo.confml")
        self.assertEquals(conf.get_configuration_by_index(1).get_path(), "fii/fii.confml")
        self.assertEquals(conf.get_configuration_by_index(2).get_path(), "hii/hii.confml")

    def compareconfiguration(self, conf1,conf2):
        self.assertEquals(conf1.path,conf2.path)
        self.assertEquals(conf1.name,conf2.name)
        self.assertEquals(conf1.ref,conf2.ref)
        self.assertEquals(conf1.namespace,conf2.namespace)
 
    def test_get_configuration_and_path(self):
        conf1 = api.Configuration("testmee.confml")
        fea = conf1.create_feature('test1')
        conf1.create_feature('test2')
        subfea = fea.create_feature('child1')
        self.assertEquals(fea.get_configuration(), conf1)
        self.assertEquals(fea.get_configuration_path(), 'testmee.confml')
        self.assertEquals(subfea.get_configuration(), conf1)
        self.assertEquals(subfea.get_configuration_path(), 'testmee.confml')
        
    def test_clone_single_configuration(self):
        conf1 = api.Configuration("testmee.confml")
        conf1.add_feature(api.Feature('test1'))
        conf1.add_feature(api.Feature('test2'))
        conf1.add_feature(api.Feature('child1'),'test1')
        dview = conf1.get_default_view()
        dview.get_feature('test1').set_value('one')
        dview.get_feature('test1.child1').set_value('subone')
        conf2 = conf1._clone(recursion=True)
        self.compareconfiguration(conf1, conf2)
        self.assertEquals(conf2.list_all_features(),['test1', 'test1.child1', 'test2'])
        dview2 = conf2.get_default_view()
        self.assertEquals(dview2.get_feature('test1').get_value(),'one')
        self.assertEquals(dview2.get_feature('test1.child1').get_value(),'subone')

    def test_clone_configuration_with_includes(self):
        conf1 = api.Configuration("testmee.confml")
        conf1.add_feature(api.Feature('test1'))
        conf1.add_feature(api.Feature('test2'))
        conf1.add_feature(api.Feature('child1'),'test1')
        conf1.create_configuration("confml/data.confml")
        dview = conf1.get_default_view()
        dview.get_feature('test1').set_value('one')
        dview.get_feature('test1.child1').set_value('subone')
        conf2 = conf1._clone(recursion=True)
        self.compareconfiguration(conf1, conf2)
        self.assertEquals(conf2.list_all_features(),['test1', 'test1.child1', 'test2'])
        self.assertEquals(conf2.list_configurations(),['confml/data.confml'])
        dview2 = conf2.get_default_view()
        self.assertEquals(dview2.get_feature('test1').get_value(),'one')
        self.assertEquals(dview2.get_feature('test1.child1').get_value(),'subone')

#    def test_create_and_get_root(self):
#        conf = api.Configuration("foobar/testmee.confml")
#        self.assertEquals(conf.get_root(),"foobar/testmee.confml")

class TestCompositeConfiguration(unittest.TestCase):    
    def test_add(self):
        conf = api.Configuration("data/simple.confml")
        layer = api.Configuration("laa")
        conf.add_configuration(layer)
        self.assertEquals(conf.list_configurations()[0],"laa")    

    def test_add_and_access_via_member(self):
        conf = api.Configuration("data/simple.confml")
        layer = api.Configuration("laa")
        conf.add_configuration(layer)
        self.assertEquals(conf.laa.name,"laa")    

    def test_add_and_add_another_config_under(self):
        conf = api.Configuration("data/simple.confml")
        layer = api.Configuration("laa")
        conf.add_configuration(layer)
        conf.laa.add_configuration(api.Configuration("foo"))
        self.assertEquals(conf.laa.foo.name,"foo")    

    def test_add_several_configurations(self):
        conf = api.Configuration("data/simple.confml")
        layer = api.Configuration("laa")
        conf.add_configuration(layer)
        conf.add_configuration(api.Configuration("foo"))
        conf.add_configuration(api.Configuration("faa"))
        self.assertEquals(conf.list_configurations()[0],"laa")    
        self.assertEquals(conf.list_configurations()[1],"foo")    
        self.assertEquals(conf.list_configurations()[2],"faa")    

    def test_add_several_and_remove_one_layer(self):
        conf = api.Configuration("data/simple.confml")
        layer = api.Configuration("laa")
        conf.add_configuration(layer)
        conf.add_configuration(api.Configuration("foo"))
        conf.add_configuration(api.Configuration("faa"))
        conf.remove_configuration("foo")
        
        self.assertEquals(conf.list_configurations()[0],"laa")    
        self.assertEquals(conf.list_configurations()[1],"faa")    

    def test_add_several_and_remove_last_layer(self):
        conf = api.Configuration("data/simple.confml")
        layer = api.Configuration("laa")
        conf.add_configuration(layer)
        conf.add_configuration(api.Configuration("foo"))
        conf.add_configuration(api.Configuration("faa"))
        conf.remove_configuration("faa")
        self.assertEquals(conf.list_configurations()[0],"laa")    
        self.assertEquals(conf.list_configurations()[1],"foo")    

    def test_add_several_and_remove_all_configurations(self):
        conf = api.Configuration("data/simple.confml")
        layer = api.Configuration("laa")
        conf.add_configuration(layer)
        conf.add_configuration(api.Configuration("foo"))
        conf.add_configuration(api.Configuration("faa"))
        for layername in conf.list_configurations():
            conf.remove_configuration(layername)
            
        self.assertTrue(len(conf.list_configurations())==0)        

    def test_add_several_and_try_to_remove_not_existing(self):
        conf = api.Configuration("data/simple.confml")
        layer = api.Configuration("laa")
        conf.add_configuration(layer)
        conf.add_configuration(api.Configuration("foo"))
        conf.add_configuration(api.Configuration("faa"))
        try:
            conf.remove_configuration("notthere")
            self.fail("removing of nonexisting layer succeeds!")
        except exceptions.NotFound:
            pass

    def test_create_view_simple(self):
        conf = api.Configuration("data/simple.confml")
        conf.create_view("view1")
        view = conf.get_view("view1")
        self.assertEquals(view.list_groups(),[])
        
    def test_create_views_and_list_views(self):
        conf = api.Configuration("data/simple.confml")
        conf.create_view("view1")
        conf.create_view("view2")
        self.assertEquals(conf.list_views(),['view1','view2'])

    def test_create_views_and_remove_one(self):
        conf = api.Configuration("data/simple.confml")
        conf.create_view("view1")
        conf.create_view("view2")
        conf.create_view("view3")
        conf.remove_view('view2')
        self.assertEquals(conf.list_views(),['view1','view3'])

    def test_create_views_and_remove_invalid(self):
        conf = api.Configuration("data/simple.confml")
        conf.create_view("view1")
        conf.create_view("view2")
        conf.create_view("view3")
        try:
            conf.remove_view('invalid')
            self.fail('Removing invalid view succeeds!')
        except exceptions.NotFound:
            pass
        
    def test_create_views_and_remove_all(self):
        conf = api.Configuration("data/simple.confml")
        conf.create_view("view1")
        conf.create_view("view2")
        conf.create_view("view3")
        for view in conf.list_views():
            conf.remove_view(view)
        self.assertEquals(conf.list_views(),[])

    def test_create_view_with_data(self):
        conf = api.Configuration("data/simple.confml")
        conf.create_view("view1")
        view = conf.get_view("view1")
        view.add_group(api.Group("group1"))
        view.add_group(api.Group("group2"))
        view.create_featurelink("feature1")
        view.group1.add_group(api.Group("group21"))
        view.group1.group21.create_featurelink("feature211")
        view.group1.group21.create_featurelink("feature212")
        
        self.assertEquals(sorted(view._list_traverse()),
                          sorted(['group1', 
                                  'group1.group21', 
                                  'group1.group21.link_feature211', 
                                  'group1.group21.link_feature212', 
                                  'group2', 
                                  'link_feature1']))

    def test_get_default_view(self):
        conf = api.Configuration("data/simple.confml")
        dview = conf.get_default_view()
        self.assertEquals(dview.ref,'?default_view')

    def test_create_configuration_and_features(self):
        conf = api.Configuration("data/simple.confml")
        fea = conf.create_feature("test")
        self.assertEquals(conf.get_feature('test'), fea)
        fea = conf.create_feature("test1", name="test name")
        self.assertEquals(conf.get_feature('test1').name, 'test name')
        fea.create_feature("subfea", name="subfea name")
        self.assertEquals(conf.list_all_features(), ['test','test1','test1.subfea'])

    def test_get_default_view_and_data_to_it(self):
        conf = api.Configuration("data/simple.confml")
        view = conf.get_default_view()
        view._add(api.Group("group1"))
        view._add(api.Group("group2"))
        view._add(api._FeatureProxy("feature1"))
        view.group1._add(api.Group("group21"))
        view.group1.group21._add(api._FeatureProxy("feature211"))
        view.group1.group21._add(api._FeatureProxy("feature212"))
        view.feature1._add(api._FeatureProxy("feature11"))
        
        self.assertEquals(sorted(view._list_traverse()),
                          sorted(['group1', 
                                           'group2', 
                                           'feature1', 
                                           'group1.group21', 
                                           'group1.group21.feature211', 
                                           'group1.group21.feature212', 
                                           'feature1.feature11']))


    def test_add_feature_normal_configuration(self):
        conf = api.Configuration("simple.confml")
        conf.add_feature(api.Feature("feature1"))
        self.assertEquals(conf.list_all_features(),['feature1'])

    def test_add_feature_normal_and_get_default_view(self):
        conf = api.Configuration("simple.confml")
        conf.add_feature(api.Feature("feature1"))
        conf.add_feature(api.Feature("feature2"))
        conf.add_feature(api.Feature("feature11"),'feature1')
        view = conf.get_default_view()
        
        self.assertEquals(view.list_all_features(),['feature1',
                                                'feature1.feature11',
                                                'feature2',])
        self.assertEquals(view.get_feature('feature1.feature11')._obj._parent,conf.feature1)

    def test_add_feature_hierarchy_and_get_default_view(self):
        root = api.Configuration("data/simple.confml")
        conf = api.Configuration("test/root.confml")
        root.add_configuration(conf)
        conf2 = api.Configuration("test2/root.confml",namespace="com.nokia")
        root.add_configuration(conf2)
        conf.add_feature(api.Feature("group1"))
        conf.add_feature(api.Feature("group2"))
        conf.add_feature(api.Feature("feature1"))
        conf.group1.add_feature(api.Feature("group21"))
        conf.group1.group21.add_feature(api.Feature("feature211"))
        conf.group1.group21.add_feature(api.Feature("feature212"))
        conf.feature1.add_feature(api.Feature("feature11"))
        conf2.add_feature(api.Feature("wlan"))
        conf2.add_feature(api.Feature("bluetooth"))
        self.assertEquals(conf.list_all_features(),
                          ['group1', 
                           'group1.group21', 
                           'group1.group21.feature211', 
                           'group1.group21.feature212', 
                           'group2', 
                           'feature1', 
                           'feature1.feature11'])
        dview = conf.get_default_view()
        self.assertEquals(dview.list_features(),
                          ['group1', 
                           'group2', 
                           'feature1'])
        
        self.assertEquals(dview.list_groups(),['com'])
        self.assertEquals(dview.list_all_features(),
                          ['group1', 
                           'group1.group21', 
                           'group1.group21.feature211', 
                           'group1.group21.feature212', 
                           'group2', 
                           'feature1', 
                           'feature1.feature11',
                           'com.nokia.wlan',
                           'com.nokia.bluetooth'])

    def test_add_feature(self):
        conf = api.Configuration("simple.confml")
        conf.add_feature(api.Feature("feature1"))
        self.assertEquals(conf.list_features(),['feature1'])

#    def test_add_feature_namespace(self):
#        conf = api.Configuration("test","com.nokia")
#        conf.add_feature(api.Feature("feature1"))
#        self.assertEquals(conf.list_all_features(),['com.nokia.feature1'])
#        self.assertEquals(conf.feature1, conf.get_default_view().com.nokia.feature1._obj)
    def test_get_path_for_parent(self):
        conf = api.Configuration("test.confml")
        conf.create_configuration("foo/root.confml")
        conf.get_configuration("foo/root.confml").create_configuration("confml/jee.confml")
        self.assertEquals(conf.get_path_for_parent(None), "test.confml")
        self.assertEquals(conf.get_configuration("foo/root.confml").get_path_for_parent(None), "foo/root.confml")
        foo = conf.get_configuration("foo/root.confml")
        jee = foo.get_configuration("confml/jee.confml")
        self.assertEquals(foo.get_path_for_parent(conf), "foo/root.confml")
        self.assertEquals(jee.get_path_for_parent(conf), "foo/confml/jee.confml")
        self.assertEquals(jee.get_path_for_parent(foo._obj), "confml/jee.confml")


    def test_add_subconfiguration(self):
        conf = api.Configuration("test",namespace="com.nokia")
        conf.create_configuration("foo/root.confml")
        conf.create_configuration("platforms/s60.confml")
        dconf = api.Configuration('confml/data.confml')
        sconf = conf.get_configuration('foo/root.confml')
        sconf.add_configuration(dconf)
        self.assertEquals(conf.list_configurations(),['foo/root.confml',
                                                      'platforms/s60.confml',])
        self.assertEquals(conf.list_all_configurations(),['foo/root.confml',
                                                          'foo/confml/data.confml',
                                                          'platforms/s60.confml'])
        self.assertEquals(conf.get_configuration('foo/root.confml').list_all_configurations(),['confml/data.confml'])
        
        
    def test_remove_configuration(self):
        conf = api.Configuration("test.confml",namespace="com.nokia")
        conf.create_configuration("foo/root.confml")
        self.assertEquals(conf.list_configurations(),['foo/root.confml'])
        conf.remove_configuration("foo/root.confml")
        self.assertEquals(conf.list_configurations(),[])

    def test_get_configuration(self):
        conf = api.Configuration("test.confml",namespace="com.nokia")
        conf.create_configuration("foo/root.confml")
        self.assertEquals(conf.list_configurations(),['foo/root.confml'])
        foo = conf.get_configuration("foo/root.confml")
        self.assertEquals(foo.get_path(),"foo/root.confml")


    def test_remove_all(self):
        conf = api.Configuration("test",namespace="com.nokia")
        conf.create_configuration("foo/root.confml")
        conf.create_configuration("platforms/s60.confml")
        conf.create_configuration("platforms/customsw.confml")
        self.assertEquals(conf.list_configurations(),['foo/root.confml',
                                                      'platforms/s60.confml',
                                                      'platforms/customsw.confml'])
        for configref in conf.list_configurations():
            conf.remove_configuration(configref)
        self.assertEquals(conf.list_configurations(),[])


    def test_add_subconfiguration_and_access(self):
        conf = api.Configuration("data/simple.confml")
        conf.create_configuration("foo/layer1.confml")
        self.assertTrue(conf.foo__layer1_confml)

#    def test_add_subconfiguration_and_features(self):
#        conf = api.Configuration("test","com.nokia")
#        conf.create_configuration("foo/root.confml")
#        conf.create_configuration("fii/root.confml")
#        conf.foo_root.add_feature(api.Feature("feature1"))
#        conf.foo_root.add_feature(api.Feature("feature12"),"feature1")
#        conf.fii_root.add_feature(api.Feature("feature2"))
#        conf.fii_root.add_feature(api.Feature("feature21"),"feature2")
#        self.assertEquals(conf.list_all_features(),['com.nokia.feature1',
#                                                'com.nokia.feature1.feature12',
#                                                'com.nokia.feature2',
#                                                'com.nokia.feature2.feature21',
#                                                ])
#        self.assertEquals(conf.foo_root.feature1.get_ref(), 
#                          conf.get_default_view()._get('com.nokia.feature1').get_ref())

    def test_add_configuration_with_features_to_root(self):
        root= api.Configuration("test",namespace="com.nokia")
        conf1 = api.Configuration("foo/foo.confml")
        conf1.add_feature(api.Feature("feature1"))
        conf1.add_feature(api.Feature("feature12"),"feature1")
        conf2 = api.Configuration("bar/bar.confml")
        conf2.add_feature(api.Feature("feature2"))
        conf2.add_feature(api.Feature("feature22"),"feature2")
        root.add_configuration(conf1)
        self.assertEquals(root.list_all_features(),
                          ['feature1',
                           'feature1.feature12'])
        root.add_configuration(conf2)
        self.assertEquals(root.list_all_features(),
                          ['feature1',
                           'feature1.feature12',
                           'feature2',
                           'feature2.feature22'])

    def test_add_configuration_to_other_conf_and_then_to_root(self):
        root= api.Configuration("test",namespace="com.nokia")
        conf1 = api.Configuration("foo/foo.confml")
        conf1.add_feature(api.Feature("feature1"))
        conf1.add_feature(api.Feature("feature12"),"feature1")
        conf2 = api.Configuration("bar/foo.confml")
        conf2.add_feature(api.Feature("feature2"))
        conf2.add_feature(api.Feature("feature22"),"feature2")
        conf2.add_configuration(conf1)
        self.assertEquals(conf2.list_all_features(),
                          ['feature2',
                           'feature2.feature22',
                           'feature1',
                           'feature1.feature12'])
        root.add_configuration(conf2)
        self.assertEquals(root.list_all_features(),
                          ['feature2',
                           'feature2.feature22',
                           'feature1',
                           'feature1.feature12'])

    def test_add_features_feature_hiararchy_and_then_to_configurations(self):
        conf1 = api.Configuration("foo/foo.confml")
        fea = api.Feature('feature1')
        fea2 = api.Feature('feature12')
        fea2.add_feature(api.Feature('feature121'))
        fea.add_feature(api.Feature('feature11'))
        fea.add_feature(fea2)
        self.assertEquals(fea.list_all_features(),
                                ['feature11',
                                 'feature12',
                                 'feature12.feature121'])
        conf1.add_feature(fea)
        self.assertEquals(conf1.list_all_features(),
                                ['feature1',
                                 'feature1.feature11',
                                 'feature1.feature12',
                                 'feature1.feature12.feature121'])
        

    def test_add_features_and_remove_one(self):
        conf1 = api.Configuration("foo/foo.confml")
        fea = api.Feature('feature1')
        fea2 = api.Feature('feature12')
        fea2.add_feature(api.Feature('feature121'))
        fea.add_feature(api.Feature('feature11'))
        fea.add_feature(fea2)
        conf1.add_feature(fea)
        conf1.remove_feature('feature1.feature12')
        self.assertEquals(conf1.list_all_features(), 
                          ['feature1',
                           'feature1.feature11'])
        fea.remove_feature('feature11')
        self.assertEquals(conf1.list_all_features(), 
                          ['feature1'])

    def test_add_features_and_remove_all(self):
        conf = api.Configuration("foo/foo.confml")
        fea = api.Feature('feature1')
        conf.add_feature(fea)
        conf.add_feature(api.Feature('feature2'))
        conf.add_feature(api.Feature('feature3'))
        conf.add_feature(api.Feature('feature4'))
        for fearef in conf.list_features():
            conf.remove_feature(fearef)
        self.assertEquals(conf.list_all_features(), [])

    def test_add_features_and_create_view(self):
        
        conf = api.Configuration("foo/foo.confml")
        conf.add_feature(api.Feature('feature1'))
        conf.add_feature(api.Feature('feature2'))
        conf.add_feature(api.Feature('feature3'))
        conf.add_feature(api.Feature('feature4'))
        conf.add_feature(api.Feature('feature11'),'feature1')
        conf.add_feature(api.Feature('feature12'),'feature1')
        
        conf.create_view("rootfeas")
        view = conf.get_view('rootfeas')
        for fearef in conf.list_features():
            fea = conf.get_feature(fearef)
            view.add_feature(fea)
        self.assertEquals(view.list_all_features(), ['feature1',
                                                     'feature2',
                                                     'feature3',
                                                     'feature4'])
        view.remove_feature('feature2')
        self.assertEquals(view.list_all_features(), ['feature1',
                                                     'feature3',
                                                     'feature4'])

    def test_add_features_and_create_view_with_links(self):
        conf = api.Configuration("foo/foo.confml")
        conf.add_feature(api.Feature('feature1'))
        conf.add_feature(api.Feature('feature2'))
        conf.add_feature(api.Feature('feature3'))
        conf.add_feature(api.Feature('feature4'))
        conf.add_feature(api.Feature('feature11'),'feature1')
        conf.add_feature(api.Feature('feature12'),'feature1')
        conf.create_view('fea1')
        view1 = conf.get_view('fea1')
        view1.create_group('thegruppe1')
        view1.get_group('thegruppe1').add(api.FeatureLink('feature1.feature11'))
        view1.add(api.FeatureLink('feature1.*'))
        view1.populate()
        self.assertEquals(view1.list_all_features(),
                          ['thegruppe1.proxy_feature1_feature11',
                           'proxy_feature1_feature11',
                           'proxy_feature1_feature12'])
        fpr = view1.get_feature('thegruppe1.proxy_feature1_feature11')
        self.assertEquals(fpr._obj.fqr,conf.get_default_view().get_feature('feature1.feature11').fqr) 
        self.assertEquals(view1.list_all_features(),
                          ['thegruppe1.proxy_feature1_feature11',
                           'proxy_feature1_feature11',
                           'proxy_feature1_feature12'])

    def test_add_features_and_create_all_view_with_links(self):
        conf = api.Configuration("foo/foo.confml")
        conf.add_feature(api.Feature('feature1'))
        conf.add_feature(api.Feature('feature2'))
        conf.add_feature(api.Feature('feature3'))
        conf.add_feature(api.Feature('feature4'))
        conf.add_feature(api.Feature('feature11'),'feature1')
        conf.add_feature(api.Feature('feature12'),'feature1')
        conf.create_view("all")
        view1 = conf.get_view('all')
        view1.add(api.FeatureLink('**'))
        view1.populate()
        self.assertEquals(view1.list_all_features(),
                          ['proxy_feature1',
                           'proxy_feature1_feature11',
                           'proxy_feature1_feature12',
                           'proxy_feature2',
                           'proxy_feature3',
                           'proxy_feature4'])
        fpr = view1.get_feature('proxy_feature1_feature11')
        self.assertEquals(fpr._obj.fqr,conf.get_default_view().get_feature('feature1.feature11').fqr) 

    def test_add_a_configuration_and_remove_it(self):
        conf = api.Configuration("simple.confml")
        conf.add_configuration(api.Configuration("confml/data.confml"))
        self.assertEquals(conf.list_configurations(),['confml/data.confml'])
        conf.remove_configuration("confml/data.confml")
        self.assertEquals(len(conf.list_configurations()),0)    

    def test_add_a_include_and_remove_it(self):
        conf = api.Configuration("simple.confml")
        conf.include_configuration("confml/data.confml")
        self.assertEquals(conf.list_configurations(),['confml/data.confml'])
        conf.remove_configuration("confml/data.confml")
        self.assertEquals(len(conf.list_configurations()),0)    

    def test_add_a_include_with_dots_in_path_and_remove_it(self):
        conf = api.Configuration("simple.confml")
        conf.include_configuration("test/foo.bar/data.confml")
        self.assertEquals(conf.list_configurations(),['test/foo.bar/data.confml'])
        conf.remove_configuration("test/foo.bar/data.confml")
        self.assertEquals(len(conf.list_configurations()),0)    

    def test_add_a_include_with_dots_and_remove_it(self):
        conf = api.Configuration("simple.confml")
        conf.include_configuration("../foo/data.confml")
        self.assertEquals(conf.list_configurations(),['../foo/data.confml'])
        conf.remove_configuration("../foo/data.confml")
        self.assertEquals(len(conf.list_configurations()),0)    

class TestConfigurationData(unittest.TestCase):
    def test_add_features_and_add_data_via_default_view(self):
        conf = api.Configuration("foo/foo.confml")
        conf.add_feature(api.Feature('feature1'))
        conf.add_feature(api.Feature('feature2'))
        conf.add_feature(api.Feature('feature3'))
        conf.add_feature(api.Feature('feature4'))
        conf.add_feature(api.Feature('feature12'),'feature1')
        dview = conf.get_default_view()
        dview.feature1._add_data(api.Data(ref="feature1", value=123))
        dview.feature2._add_data(api.Data(ref="feature2", value=123))
        dview.feature3._add_data(api.Data(ref="feature3", value=123))
        dview.feature1.feature12._add_data(api.Data(ref="feature12", value=123))
        dview.feature1._add_data(api.Data(ref="feature1", value=123))
        self.assertEquals(dview.feature1.get_value(), 123)
        dview.feature1._add_data(api.Data(ref="feature1", value=111))
        self.assertEquals(dview.feature1.get_value(), 111)

    def test_add_data_to_configuration(self):
        conf = api.Configuration("foo/foo.confml")
        conf.add_data(api.Data(ref='feature1', value=123))
        self.assertEquals(conf.get_data('feature1').get_value(),123)
        conf.add_data(api.Data(fqr='feature1.feature12', value="test"))
        self.assertEquals(conf.get_data('feature1.feature12').get_value(),"test")
        self.assertEquals(conf.data.feature1.feature12.get_value(),"test")
        conf.remove_data('feature1.feature12')
        self.assertEquals(conf.list_datas(), ['feature1'])
    
    def test_add_data_to_configuration_from_list(self):
        def check(data_objs, policy, expected):
            conf = api.Configuration("foo/foo.confml")
            conf.add_data(api.Data(ref='base1', value="foo"))
            conf.add_data(api.Data(ref='foo', value="foobar"))
            conf.add_data(api.Data(ref='base2', value="bar"))
            
            if policy is None:
                conf.add_data(data_objs)
            else:
                conf.add_data(data_objs, policy=policy)
            
            actual = []
            for d in conf._traverse(type=api.Data):
                actual.append((d.fqr, d.value))
            self.assertEquals(actual, expected)
        
        # Adding an empty list should do nothing
        check(data_objs = [],
              policy    = None,
              expected  = [('base1', 'foo'),
                           ('foo', 'foobar'),
                           ('base2', 'bar')])
        
        # Default policy (replace)
        check(data_objs = [api.Data(ref="foo", value="1"),
                           api.Data(ref="foo", value="2"),
                           api.Data(ref="foo", value="3"),],
              policy    = None,
              expected  = [('base1', 'foo'),
                           ('foo', '1'),
                           ('foo', '2'),
                           ('foo', '3'),
                           ('base2', 'bar')])
        
        # Replace explicitly
        check(data_objs = [api.Data(ref="foo", value="1"),
                           api.Data(ref="foo", value="2"),
                           api.Data(ref="foo", value="3"),],
              policy    = api.container.REPLACE,
              expected  = [('base1', 'foo'),
                           ('foo', '1'),
                           ('foo', '2'),
                           ('foo', '3'),
                           ('base2', 'bar')])
        
        # Append
        check(data_objs = [api.Data(ref="foo", value="1"),
                           api.Data(ref="foo", value="2"),
                           api.Data(ref="foo", value="3"),],
              policy    = api.container.APPEND,
              expected  = [('base1', 'foo'),
                           ('foo', 'foobar'),
                           ('foo', '1'),
                           ('foo', '2'),
                           ('foo', '3'),
                           ('base2', 'bar')])
        
        # Prepend
        check(data_objs = [api.Data(ref="foo", value="1"),
                           api.Data(ref="foo", value="2"),
                           api.Data(ref="foo", value="3"),],
              policy    = api.container.PREPEND,
              expected  = [('base1', 'foo'),
                           ('foo', '1'),
                           ('foo', '2'),
                           ('foo', '3'),
                           ('foo', 'foobar'),
                           ('base2', 'bar')])

    def test_set_data_to_configuration(self):
        conf = api.Configuration("foo/foo.confml")
        conf.add_data(api.Data(fqr='feature1', value=123))
        self.assertEquals(conf.get_data('feature1').get_value(),123)
        conf.add_data(api.Data(fqr='feature1.feature12', value="test"))
        self.assertEquals(conf.get_data('feature1.feature12').get_value(),"test")
        self.assertEquals(conf.data.feature1.feature12.get_value(),"test")

    def test_add_features_and_add_data_via_features(self):
        conf = api.Configuration("foo/foo.confml")
        conf.add_feature(api.Feature('feature1'))
        conf.add_feature(api.Feature('feature2'))
        conf.add_feature(api.Feature('feature3'))
        conf.add_feature(api.Feature('feature4'))
        conf.add_feature(api.Feature('feature12'),'feature1')
        conf.feature1.set_value(123)
        conf.feature1.feature12.set_value("test")
        self.assertEquals(conf.feature1.get_value(),123)
        self.assertEquals(conf.feature1.feature12.get_value(),"test")

    def test_create_layers_add_features_and_add_data_via_features(self):
        conf = api.Configuration("foo/foo.confml")
        conf.add_feature(api.Feature('feature1'))
        conf.add_feature(api.Feature('feature2'))
        conf.add_feature(api.Feature('feature3'))
        conf.add_feature(api.Feature('feature4'))
        conf.add_feature(api.Feature('feature12'),'feature1')
        conf.feature1.set_value(123)
        self.assertEquals(conf.feature1.get_value(),123)
        conf.create_configuration("layer1.confml")
        conf.feature1.feature12.set_value("test")
        self.assertEquals(conf.feature1.get_data().find_parent(type=api.Configuration),conf)
        self.assertEquals(conf.feature1.feature12.get_value(),"test")

        conf.feature1.set_value(321)
        conf.create_configuration("layer2.confml")
        self.assertEquals(conf.layer2_confml.list_datas(), [])
        
        self.assertEquals(conf.feature1.get_value(),321)
        self.assertEquals(conf.feature1.get_data().find_parent(type=api.Configuration).get_path(),conf.get_configuration("layer1.confml").get_path())
        self.assertEquals(conf.layer1_confml.list_all_datas(), ['feature1','feature1.feature12'])
        self.assertEquals([data.get_value() for data in conf.layer1_confml.get_all_datas()], [321,'test'])
        self.assertEquals(conf.list_datas(), ['feature1'])
        self.assertEquals([data.find_parent(type=api.Configuration).get_path() for data in conf.get_all_datas()], 
                          ['foo/foo.confml',
                           'layer1.confml',
                           'layer1.confml',])

    def test_create_layers_add_featuresequence_and_add_data_via_features(self):
        conf = api.Configuration("foo/foo.confml")
        conf.add_feature(api.FeatureSequence('feature1'))
        conf.add_feature(api.Feature('child1'),'feature1')
        conf.add_feature(api.Feature('child2'),'feature1')
        conf.add_feature(api.Feature('child3'),'feature1')
        conf.feature1.add_sequence()
        conf.feature1.get_data()[0][0].set_value('test1')
        conf.feature1.get_data()[0][1].set_value('test2')
        conf.feature1.get_data()[0][2].set_value('test3')
        conf.feature1.add_sequence(['foo1','foo2','foo3'])
        self.assertEquals(conf.feature1.get_data()[1][0].get_value(),'foo1')
        self.assertEquals(conf.feature1.get_data()[1][1].get_value(),'foo2')
        self.assertEquals(conf.feature1.get_data()[1][2].get_value(),'foo3')
        self.assertEquals(conf.feature1.get_value(),
                          [['test1','test2','test3'],
                           ['foo1','foo2','foo3']])
        self.assertEquals(conf.list_all_datas(),['feature1', 'feature1.child1', 'feature1.child2', 'feature1.child3', 'feature1', 'feature1.child1', 'feature1.child2', 'feature1.child3'])

    def test_create_featuresequence_and_get_empty_data(self):
        conf = api.Configuration("foo/foo.confml")
        conf.add_feature(api.FeatureSequence('feature1'))
        conf.add_feature(api.Feature('child1'),'feature1')
        conf.add_feature(api.Feature('child2'),'feature1')
        conf.add_feature(api.Feature('child3'),'feature1')
        self.assertEquals(conf.get_feature('feature1').get_data(),[])
        self.assertEquals(conf.get_feature('feature1').get_value(),[])

    def test_create_featuresequence_and_set_template(self):
        conf = api.Configuration("foo/foo.confml")
        conf.add_feature(api.FeatureSequence('feature1'))
        conf.add_feature(api.Feature('child1'),'feature1')
        conf.add_feature(api.Feature('child2'),'feature1')
        conf.add_feature(api.Feature('child3'),'feature1')
        fea = conf.get_feature('feature1')
        fea.set_template(['test1','test2','test3'])
        self.assertEquals(fea.get_template(),['test1', 'test2', 'test3'])
        fea.set_template(['Test1','Test2','Test3'])
        self.assertEquals(fea.get_template(),['Test1','Test2','Test3'])
        
        self.assertRaises(ValueError, fea.set_template, [])
        self.assertRaises(ValueError, fea.set_template, ['foo', 'bar'])
        self.assertRaises(ValueError, fea.set_template, ['foo', 'bar', 'foo', 'bar'])

    def test_create_features_with_rfs_data(self):
        conf = api.Configuration("foo/foo.confml")
        conf.add_feature(api.Feature('feature1'))
        conf.add_feature(api.Feature('child1'),'feature1')
        conf.add_feature(api.Feature('child2'),'feature1')
        conf.add_feature(api.Feature('child3'),'feature1')
        
        conf.add_data(api.Data(fqr='feature1.child1',attr='rfs',value='true'))
        conf.add_data(api.Data(fqr='feature1.child2',attr='rfs',value='false'))
        dview = conf.get_default_view()
        self.assertEquals(dview.get_feature('feature1.child1').get_value(), None)
        self.assertEquals(dview.get_feature('feature1.child1').get_value('rfs'), 'true')
        self.assertEquals(dview.get_feature('feature1.child2').get_value('rfs'), 'false')

class TestConfigurationDictStoring(unittest.TestCase):    
    
    def test_dumps_simple(self):
        root = api.Configuration("root",namespace="com.nokia")
        conf = root.create_configuration("test.confml")
        dumped = persistentdictionary.DictWriter().dumps(conf)
        dict =dumped['Configuration']['dict']
        self.assertEquals(dict['path'],'test.confml')
        self.assertEquals(dict['namespace'],'com.nokia')

    def test_dumps_add_features(self):
        root = api.Configuration("root",namespace="com.nokia")
        conf = root.create_configuration("test.confml")
        conf.add_feature(api.Feature("feature1", name="feature1"))
        conf.add_feature(api.Feature("feature2", name="feature2"))
        dumped = persistentdictionary.DictWriter().dumps(conf)
        dict =dumped['Configuration']['dict']
        self.assertEquals(dict['path'],'test.confml')
        self.assertEquals(dict['namespace'],'com.nokia')
        self.assertEquals(dumped['Configuration']['children'],
                          [{'Feature': {'dict': {'name': 'feature1', 'ref': 'feature1'}}}, 
                           {'Feature': {'dict': {'name': 'feature2', 'ref': 'feature2'}}}]
                                            )

    def test_dumps_root_configuration(self):
        root = api.Configuration("root",namespace="com.nokia")
        conf = root.create_configuration("foo/root.confml")
        conf.add_feature(api.Feature("feature1"))
        conf.add_feature(api.Feature("feature2"))
        conf.feature1.add_feature(api.Feature("feature11"))
        conf.feature1.add_feature(api.Feature("feature12"))
        dumped = persistentdictionary.DictWriter().dumps(root)
        dict =dumped['Configuration']['dict']
        self.assertEquals(dict['ref'],'root')
        self.assertEquals(dict['namespace'],'com.nokia')

    def test_dumps_feature_hierarchy(self):
        root = api.Configuration("root",namespace="com.nokia")
        conf = root.create_configuration("test.confml")
        conf.add_feature(api.Feature("feature1", name="feature1"))
        conf.add_feature(api.Feature("feature2", name="feature2"))
        conf.feature1.add_feature(api.Feature("feature11", name="feature11"))
        conf.feature1.add_feature(api.Feature("feature12", name="feature12"))
        dumped = persistentdictionary.DictWriter().dumps(conf)
        dict =dumped['Configuration']['dict']
        self.assertEquals(dict['path'],'test.confml')
        self.assertEquals(dict['ref'],'test_confml')
        self.assertEquals(dict['namespace'],'com.nokia')
        self.assertEquals(dumped['Configuration']['children'],
                        [{'Feature': {'dict': {'name': 'feature1', 'ref': 'feature1'}, 
                                'children': [
                                    {'Feature': {'dict': {'name': 'feature11', 'ref': 'feature11'}}},
                                    {'Feature': {'dict': {'name': 'feature12', 'ref': 'feature12'}}}]}}, 
                        {'Feature': {'dict': {'name': 'feature2', 'ref': 'feature2'}}}
                        ])

    def test_loads(self):
        conf = persistentdictionary.DictReader().loads({'Configuration': {'dict' : {'namespace':'test','ref':'test.confml'}}} )
        self.assertTrue(isinstance(conf,api.Configuration))
        self.assertEquals(conf.namespace,'test')
        self.assertEquals(conf.get_ref(),'test.confml')

    def test_loads_with_features(self):
        root = api.Configuration("root",namespace="com.nokia")
        conf = persistentdictionary.DictReader().loads({
        'Configuration': {'dict' : {'namespace':'test','ref':'test.confml'},
        'children': [{'Feature': {'dict': {'ref': 'feature1'}, 
                                  'children': [
                                               {'Feature': {'dict': {'ref': 'feature11'}}}, 
                                               {'Feature': {'dict': {'ref': 'feature12'}}}]
                                  }
                    }, 
                    {'Feature': {'dict': {'ref': 'feature2'}}}]}} )

        self.assertEquals(conf.namespace,'test')
        self.assertEquals(conf.ref,'test.confml')
        root.add_configuration(conf)
        self.assertEquals(root.list_all_features(),['test.feature1',
                                                'test.feature1.feature11',
                                                'test.feature1.feature12',
                                                'test.feature2'])


    def test_dumps_and_loads(self):
        conf = api.Configuration("test.confml")
        conf.add_feature(api.Feature("feature1"))
        conf.add_feature(api.Feature("feature2"))
        conf.feature1.add_feature(api.Feature("feature11"))
        conf.feature1.add_feature(api.Feature("feature12"))
        dumped = persistentdictionary.DictWriter().dumps(conf)
        
        conf2 = persistentdictionary.DictReader().loads(dumped)
        self.assertEquals(conf.list_all_features(),
                          conf2.list_all_features())

    def test_dumps_and_loads_configuration_hierarchy(self):
        root = api.Configuration("root.confml")
        root.add_configuration(api.Configuration("layer1"))
        layer = api.Configuration("layer2")
        conf = api.Configuration("test")
        conf.add_feature(api.Feature("feature1"))
        conf.add_feature(api.Feature("feature2"))
        conf.feature1.add_feature(api.Feature("feature11"))
        conf.feature1.add_feature(api.Feature("feature12"))
        layer.add_configuration(conf)
        root.add_configuration(layer)
        dumped = persistentdictionary.DictWriter().dumps(root)
        
        root2= persistentdictionary.DictReader().loads(dumped)
        self.assertEquals(root.list_all_features(),
                          root2.list_all_features())

    def test_dumps_and_loads_configuration_hierarchy_with_data(self):
        root = api.Configuration("root.confml")
        layer = api.Configuration("layer1")
        conf = api.Configuration("test")
        conf.add_feature(api.Feature("feature1"))
        conf.add_feature(api.Feature("feature2"))
        conf.feature1.add_feature(api.Feature("feature11"))
        conf.feature1.add_feature(api.Feature("feature12"))
        conf.feature1.set_value(1)
        conf.feature2.set_value(2)
        layer.add_configuration(conf)
        root.add_configuration(layer)
        root.add_configuration(api.Configuration("layer2"))
        root.get_default_view().feature1.feature11.set_value("testing11")
        root.get_default_view().feature1.set_value("test1")
        dumped = persistentdictionary.DictWriter().dumps(root)
        root2= persistentdictionary.DictReader().loads(dumped)
        self.assertEquals(root.list_all_features(),
                          root2.list_all_features())
        self.assertEquals(root2.get_default_view().feature1.get_value(), "test1")
        self.assertEquals(root2.get_default_view().feature2.get_value(), 2)
        self.assertEquals(root2.get_default_view().feature1.feature11.get_value(), "testing11")

        self.assertEquals([data.find_parent(type=api.Configuration).get_path() for data in root2.get_all_datas()],
                          ['test', 'test', 'layer2','layer2'])

    def test_access_via_configuration_proxy(self):
        conf = api.Configuration("root.confml")
        conf.add_feature(api.Feature("feature1"))
        proxy = api.ConfigurationProxy("root.confml")
        proxy._set_obj(conf)
        self.assertEquals(proxy.get_ref(), 'root_confml')
        self.assertEquals(proxy.get_path(), 'root.confml')
        self.assertEquals(conf.feature1.get_ref(), 'feature1')
        self.assertEquals(proxy.feature1.get_ref(), 'feature1')
        

class TestConfigurationInclude(unittest.TestCase):    
    class StoreTestInt(object):
        def load(self, ref):
            return api.Configuration(ref)

        def dump(self, obj, ref):
            pass
    
    def get_store_interface(self):
        return TestConfigurationInclude.StoreTestInt()
    
    def _test_include(self):
        inc = api.Include("foo/bar.txt", self.get_store_interface())
        objs =inc._objects()
        self.assertEquals(len(objs),1)
        self.assertEquals(objs[0].path,"foo/bar.txt")  
        
    def test_include_clone(self):
        inc = api.Include("foo/bar.txt", store_interface=self.get_store_interface())
        ci = inc._clone()
        self.assertEquals(inc.ref, ci.ref)
        self.assertEquals(inc.get_path(), ci.get_path())
        
#    def test_configuration_with_include(self):
#        conf = api.Configuration("foo.confml")
#        # Set the get_store_interface function to test stub method 
#        conf.get_store_interface = self.get_store_interface
#        conf.include_configuration("foo/test.confml")
#        subconfs = conf.list_configurations()
#        self.assertEquals(len(subconfs),1)
#        self.assertTrue(isinstance(subconfs[0], api.Configuration))  
#        self.assertEquals(subconfs[0].path,"foo/test.confml")  
        
if __name__ == '__main__':
    unittest.main()
      
"""
{'Configuration': {'dict': {'path': 'root.confml', 'ref': 'root', 'namespace': '', 'desc': ''}, 'children': [{'Configuration': {'dict': {'path': 'foo/layer1.confml', 'ref': 'foo_layer1', 'namespace': '', 'desc': ''}, 'children': [{'Configuration': {'dict': {'path': 'foo/test.confml', 'ref': 'foo_test', 'namespace': '', 'desc': ''}, 'children': [{'Feature': {'dict': {'ref': 'feature1'}, 'children': [{'Feature': {'dict': {'ref': 'feature11'}}}, {'Feature': {'dict': {'ref': 'feature12'}}}]}}, {'Feature': {'dict': {'ref': 'feature2'}}}, {'DataContainer': {'dict': {'ref': 'data'}, 'children': [{'Data': {'dict': {'ref': 'feature1', 'value': 1}}}, {'Data': {'dict': {'ref': 'feature2', 'value': 2}}}]}}]}}]}}, {'Configuration': {'dict': {'path': 'layer2.confml', 'ref': 'layer2', 'namespace': '', 'desc': ''}}}]}}
"""
