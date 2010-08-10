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

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

from cone.public import api,exceptions,utils

class TestViews(unittest.TestCase):    
    def setUp(self):
        pass

    def test_create_view(self):
        view = api.View("view1")
        self.assertTrue(view)
        self.assertTrue(view.ref, "view1")

    def test_create_view_with_configuration(self):
        config = api.Configuration("")
        view = config.create_view("view1")
        self.assertTrue(view)
        self.assertTrue(view.ref, "view1")

    def test_view_add(self):
        view = api.View("view1")
        view._add(api.Group("Test"))
        self.assertEquals(view._list(),['Test'])

#    def test_view_add_child_incorrect_class(self):
#        view = api.View("view1")
#        try:
#            view._add(api.Feature("Test"))
#            self.fail("Adding incorrect class succeeds!")
#        except exceptions.IncorrectClassError,e:
#            pass

#    def test_group_add_child_incorrect_class(self):
#        group = api.Group("Group")
#        try:
#            group._add(api.Feature("Test"))
#            self.fail("Adding incorrect class succeeds!")
#        except exceptions.IncorrectClassError,e:
#            pass

#    def test_feature_add_child_incorrect_class(self):
#        feature = api.Feature("Feature")
#        try:
#            feature._add(api.Group("Test"))
#            self.fail("Adding incorrect class succeeds! This succeeds because of Base class support in model.")
#        except exceptions.IncorrectClassError,e:
#            pass

    def test_feature_add(self):
        feature = api.Feature("Feature")
        feature._add(api.Feature("Test"))
        self.assertEquals(feature._list(),['Test'])

    def test_view_create_groups_and_features_and_list_all(self):
        view = api.View("view1")
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

    def test_view_create_groups_and_features_and_list_features(self):
        view = api.View("view1")
        view._add(api.Group("group1"))
        view._add(api.Group("group2"))
        view._add(api._FeatureProxy("feature1"))
        view.group1._add(api.Group("group21"))
        view.group1.group21._add(api._FeatureProxy("feature211"))
        view.group1.group21._add(api._FeatureProxy("feature212"))
        view.feature1._add(api._FeatureProxy("feature11"))
        self.assertEquals(sorted(view.list_all_features()),
                          sorted(['feature1', 
                                          'group1.group21.feature211', 
                                          'group1.group21.feature212', 
                                          'feature1.feature11']))


    def test_view_add_features_with_view_add_feature(self):
        view = api.View("view1")
        view.add_feature(api.Feature("feature1"))
        view.add_feature(api.Feature("feature2"), "com.nokia.s60")
        view.com.nokia.s60.feature2.add_feature(api.Feature("feature21"))
        self.assertEquals(sorted(view.list_all_features()),
                          sorted(['feature1', 
                                          'com.nokia.s60.feature2', 
                                          'com.nokia.s60.feature2.feature21', 
                                          ]))


    def test_view_add_features_and_get_matching_features(self):
        view = api.View("view1")
        view.add_feature(api.Feature("feature1"))
        view.add_feature(api.Feature("feature2"), "com.nokia.s60")
        view.com.nokia.s60.feature2.add_feature(api.Feature("feature21"))
        self.assertEquals(view.get_feature("com.nokia.s60.feature2"), view.com.nokia.s60.feature2)

    def test_view_get_matching_features(self):
        view = api.View("view1")
        view.add_feature(api.Feature("feature1",type='boolean'))
        view.add_feature(api.Feature("feature2"))
        view.add_feature(api.Feature("feature11", type='boolean'),"feature1")
        view.add_feature(api.Feature("feature12"),"feature1")
        self.assertEquals(view.get_matching_features("feature2"), [view.feature2])
        self.assertEquals(view.get_matching_features("feature2.*"), [])
        self.assertEquals(view.get_matching_features("feature1.*"), [view.feature1.feature11, view.feature1.feature12])
        self.assertEquals(view.get_matching_features("feature1.*", name='feature11'), [view.feature1.feature11])
        self.assertEquals(view.get_matching_features("**", filters=[lambda x: x.get_type()=='boolean']), 
                          [view.feature1,
                           view.feature1.feature11])


    def test_view_get_matching_features_with_list(self):
        view = api.View("view1")
        view.add_feature(api.Feature("feature1",type='boolean'))
        view.add_feature(api.Feature("feature2"))
        view.add_feature(api.Feature("feature11", type='boolean'),"feature1")
        view.add_feature(api.Feature("feature12"),"feature1")
        self.assertEquals(view.get_features(["feature2", "feature1"]), [view.feature2, view.feature1])
        self.assertEquals(view.get_features(["feature2", "feature1.*"]), [view.feature2, 
                                                                          view.feature1.feature11,
                                                                          view.feature1.feature12])
        self.assertEquals(view.get_features([""]), [])

    def test_view_add_features_and_remove_features(self):
        view = api.View("view1")
        view.add_feature(api.Feature("feature1"))
        view.add_feature(api.Feature("feature2"), "com.nokia.s60")
        view.com.nokia.s60.feature2.add_feature(api.Feature("feature21"))
        
        self.assertEquals(view.list_all_features(),['feature1', 'com.nokia.s60.feature2', 'com.nokia.s60.feature2.feature21'])
        self.assertEquals(view.get_group("com.nokia.s60").list_features(),['feature2'])
        for fearef in view.list_features():
            view.remove_feature(fearef)
        self.assertEquals(view.list_all_features(),['com.nokia.s60.feature2', 'com.nokia.s60.feature2.feature21'])

    def test_view_create_groups_remove_groups(self):
        view = api.View("view1")
        view.create_group("Group one")
        view.create_group("Group two")
        view.add_feature(api.Feature("feature2"),"Group one")
        self.assertEquals(view.list_groups(),['Group one',  'Group two'])
        view.remove_group("Group two")
        self.assertEquals(view.list_groups(),['Group one'])
        view.get_group('Group one').add_feature(api.Feature("testing"))
        self.assertEquals(view.get_group('Group one').list_features(),['feature2','testing'])
        self.assertEquals(view.list_all_features(),['Group one.feature2', 'Group one.testing'])
        view.remove_group("Group one")
        self.assertEquals(view.list_groups(),[])
        self.assertEquals(view.list_features(),[])

    def test_create_featurelink(self):
        self.assertEquals(api.FeatureLink.get_featurelink_ref("fealink"), "link_fealink")
        fealink = api.FeatureLink("fealink")
        self.assertEquals(fealink.ref, "link_fealink")
        self.assertEquals(fealink.link, "fealink")
        
    def test_view_create_featurelink(self):
        view = api.View("view1")
        fl = view.create_featurelink("Testing.foobar")
        self.assertTrue(isinstance(fl, api.FeatureLink))
        self.assertEquals(view.get_featurelink("Testing.foobar"), fl)
        

    def test_view_create_group_with_name(self):
        view = api.View("view1")
        view.create_group("Group one", name="Testing group")
        self.assertEquals(view.get_group("Group one").name, "Testing group")

    def test_view_add_featurelink(self):
        view = api.View("view1")
        view.create_group("Group one")
        view.create_group("Group two")
        view.add_feature(api.Feature("feature2"),"Group one")
        self.assertEquals(view.list_groups(),['Group one',  'Group two'])
        view.remove_group("Group two")
        #view.add(api.FeatureGroup('foo.*'))
        self.assertEquals(view.list_groups(),['Group one'])
        view.get_group('Group one').create_featurelink("testing", name='testing 1')
        self.assertEquals(view.get_group('Group one').get_featurelink('testing').get_name(), 'testing 1')
        g1 = view.get_group('Group one')
        self.assertEquals(g1.list_features(),['feature2'])
        self.assertEquals(view.list_all_features(),['Group one.feature2'])
        view.remove_group("Group one")

        self.assertEquals(view.list_groups(),[])
        self.assertEquals(view.list_features(),[])

    def test_feature_link_get_overrides(self):
        fl = api.FeatureLink("testing")
        self.assertEquals(fl.get_attributes(), {})
        self.assertEquals(fl.get_attributes(), {})
        fl.override_attributes.append('desc')
        fl.override_attributes.append('name')
        fl.name = None
        fl.desc = "test"
        self.assertEquals(fl.get_attributes(), {'desc': 'test'})
        fl.desc = "bar"
        self.assertEquals(fl.get_attributes(), {'desc': 'bar'})
        fl.desc = ""
        fl.minLength = 2
        fl.override_attributes.append('minLength')
        self.assertEquals(fl.get_attributes(), { 'minLength' : 2, 'desc': ''})

    def test_add_view_to_configuration_and_populate(self):
        config = api.Configuration("foo")
        config.add_feature(api.Feature("testing"))
        view = api.View("view1")
        view.create_group("Group one")
        fl = api.FeatureLink("testing")
        view.get_group('Group one').add(fl)
        config.add_view(view)
        view.populate()
        self.assertEquals(view.get_group('Group one').list_features(),['proxy_testing'])
    
    def test_view_add_featurelink_with_description_override(self):
        api.FeatureLink.override_attributes.append('dict')
        config = api.Configuration("foo")
        fea = api.Feature("testing")
        fea.desc = "feature desc"
        config.add_feature(fea)
        view = api.View("view1")
        view.create_group("Group one")
        fl = api.FeatureLink("testing")
        fl.desc = "view desc"
        view.get_group('Group one').add(fl)
        config.add_view(view)
        view.populate()
        self.assertEquals(view.get_group('Group one').list_features(),['proxy_testing'])
        self.assertEquals(view.get_group('Group one').get_feature('proxy_testing').desc, "view desc")
    
    def compareview(self,view1,view2):
        self.assertEquals(view1.ref, view2.ref)
        self.assertEquals(view1.container, view2.container)
        self.assertEquals(view1.name, view2.name)
        self.assertEquals(view1.support_data, view2.support_data)


    def test_clone_view_with_featurelink(self):
        view1 = api.View("view1")
        view1.create_group("Group one")
        view1.create_group("Group two")
        view1.get_group('Group one').create_featurelink("testing/foo")
        fea2 = api.Feature("feature2")
        view1.add_feature(fea2,"Group one")
        view1.add_feature(api.Feature("feature3"),"Group one")
        self.assertEquals(view1.list_groups(),['Group one',  'Group two'])
        
        view2 = view1._clone(recursion=True)
        self.compareview(view1,view2)
        self.assertEquals(view2.list_groups(),['Group one',  'Group two'])
        self.assertEquals(view2.get_group('Group one')._list(),['link_testing_foo', 'feature2', 'feature3'])
        #self.assertEquals(view2.get_group('Group one').feature2._obj, fea2)
    
    
    def test_populate_group_with_same_name_features(self):
        config = api.Configuration("foo")
        
        feature = api.Feature("Feature1", name="Some feature")
        feature.add_feature(api.Feature("Setting1", name="Setting 1"))
        feature.add_feature(api.Feature("Setting2", name="Setting 2"))
        config.add_feature(feature)
        
        feature = api.Feature("Feature2", name="Some feature")
        feature.add_feature(api.Feature("Setting1", name="Setting 1"))
        feature.add_feature(api.Feature("Setting2", name="Setting 2"))
        config.add_feature(feature)
        
        
        view = api.View('testview')
        config.add_view(view)
        
        # Test using explicit links for all settings
        view.create_group('testgroup')
        group = view.get_group('testgroup')
        group.create_featurelink('Feature1.Setting1')
        group.create_featurelink('Feature1.Setting2')
        group.create_featurelink('Feature2.Setting1')
        group.create_featurelink('Feature2.Setting2')
        
        group.populate()
        self.assertEquals(sorted(group.list_features()),
                          ['proxy_Feature1_Setting1',
                           'proxy_Feature1_Setting2',
                           'proxy_Feature2_Setting1',
                           'proxy_Feature2_Setting2'])
        
        
        # Test using wildcards
        view.create_group('testgroup2')
        group = view.get_group('testgroup2')
        group.create_featurelink('Feature1.*')
        group.create_featurelink('Feature2.*')
        
        group.populate()
        self.assertEquals(sorted(group.list_features()),
                          ['proxy_Feature1_Setting1',
                           'proxy_Feature1_Setting2',
                           'proxy_Feature2_Setting1',
                           'proxy_Feature2_Setting2'])
    
    def test_readonly_attribute(self):
        p = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'testdata', 'view_tests')))
        root = p.get_configuration('view_tests-cpf.confml')
        views = root.get_view(root.list_views()[0])
        seqs = views.get_group('Sequences')
        japan_car_name = seqs.get_feature('proxy_japan-car-fea_CarSequence_CarName')
        self.assertTrue(japan_car_name.readOnly)
    
if __name__ == '__main__':
      unittest.main()

