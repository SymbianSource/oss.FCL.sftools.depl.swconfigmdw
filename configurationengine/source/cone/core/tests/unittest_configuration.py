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

from cone.public import api, plugin
from cone.core import *

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
test_project        = os.path.join(ROOT_PATH,"testdata/test_project.cpf")
multiroot_project   = os.path.join(ROOT_PATH,"testdata/multiroot_test.zip")
LAYERED_RES_PROJECT = os.path.join(ROOT_PATH,"testdata/layered_res_test.zip")


class TestConfiguration(unittest.TestCase):    
    def setUp(self):
        pass

    def test_layered_resources_invalid_resource_type(self):
        p = api.Project(api.Storage.open(LAYERED_RES_PROJECT))
        config = p.get_configuration('root.confml')
        self.assertRaises(ValueError, config.layered_resources, resource_type='foo')
    
    def test_layered_resource_invalid_params(self):
        p = api.Project(api.Storage.open(LAYERED_RES_PROJECT))
        config = p.get_configuration('root.confml')
        
        # Both folder and resource_type specified
        self.assertRaises(ValueError, config.layered_resources, folder='foo', resource_type='implml')
        
        # Neither folder nor resource_type specified
        self.assertRaises(ValueError, config.layered_resources, folder=None, resource_type=None)
    
    def test_layered_resources(self):
        p = api.Project(api.Storage.open(LAYERED_RES_PROJECT))
        config = p.get_configuration('root.confml')
        
        data = config.layered_resources(resource_type='confml').data
        self.assertEquals(data, {'test.confml': ['layer1/confml/test.confml',
                                                 'layer2/confml/test.confml']})
        
        data = config.layered_resources(resource_type='implml').data
        self.assertEquals(data, {'test.implml': ['layer1/implml/test.implml',
                                                 'layer2/implml/test.implml']})
        
        data = config.layered_resources(resource_type='content').data
        self.assertEquals(data, {'foo.txt': ['layer1/content/foo.txt',
                                             'layer2/content/foo.txt']})
        
        data = config.layered_resources(resource_type='doc').data
        self.assertEquals(data, {'bar.txt': ['layer1/doc/bar.txt',
                                             'layer2/doc/bar.txt']})
    
    def test_layered_resources_custom_folder(self):
        p = api.Project(api.Storage.open(LAYERED_RES_PROJECT))
        config = p.get_configuration('root.confml')
        
        data = config.layered_resources(folder='foo').data
        self.assertEquals(data, {'bar.txt': ['layer1/foo/bar.txt',
                                             'layer2/foo/bar.txt']})
    
    def test_layered_resources_directly_from_layer(self):
        p = api.Project(api.Storage.open(LAYERED_RES_PROJECT))
        config = p.get_configuration('layer1/root.confml')
        
        self.assertEquals(config.layered_resources(resource_type='confml').data,
                          {'test.confml': ['layer1/confml/test.confml']})
        
        self.assertEquals(config.layered_resources(resource_type='implml').data,
                          {'test.implml': ['layer1/implml/test.implml']})
    
    def test_layered_resources_with_empty_folders(self):
        p  = api.Project(api.Storage.open(LAYERED_RES_PROJECT))
        config = p.get_configuration('root.confml')
        
        data = config.layered_resources(empty_folders=True, resource_type='confml').data
        self.assertEquals(data, {'test.confml': ['layer1/confml/test.confml',
                                                 'layer2/confml/test.confml'],
                                 'empty':       ['layer1/confml/empty',
                                                 'layer2/confml/empty']})
        
        data = config.layered_resources(empty_folders=True, resource_type='implml').data
        self.assertEquals(data, {'test.implml': ['layer1/implml/test.implml',
                                                 'layer2/implml/test.implml'],
                                 'empty':       ['layer1/implml/empty',
                                                 'layer2/implml/empty']})
        
        data = config.layered_resources(empty_folders=True, resource_type='content').data
        self.assertEquals(data, {'foo.txt': ['layer1/content/foo.txt',
                                             'layer2/content/foo.txt'],
                                 'empty':   ['layer1/content/empty',
                                             'layer2/content/empty']})
        
        data = config.layered_resources(empty_folders=True, resource_type='doc').data
        self.assertEquals(data, {'bar.txt': ['layer1/doc/bar.txt',
                                             'layer2/doc/bar.txt'],
                                 'empty':   ['layer1/doc/empty',
                                             'layer2/doc/empty']})
    
    def test_layered_resources_specific_layers(self):
        p = api.Project(api.Storage.open(LAYERED_RES_PROJECT))
        config = p.get_configuration('root.confml')
        
        self.assertEquals(config.layered_resources(layers=[-1], resource_type='confml').data,
                          {'test.confml': ['layer2/confml/test.confml']})
        self.assertEquals(config.layered_resources(layers=[0], resource_type='confml').data,
                          {'test.confml': ['layer1/confml/test.confml']})
    
    def test_layered_resources_shortcuts(self):
        p = api.Project(api.Storage.open(LAYERED_RES_PROJECT))
        config = p.get_configuration('root.confml')
        
        data = config.layered_confml().data
        self.assertEquals(data, {'test.confml': ['layer1/confml/test.confml',
                                                 'layer2/confml/test.confml']})
        
        data = config.layered_implml().data
        self.assertEquals(data, {'test.implml': ['layer1/implml/test.implml',
                                                 'layer2/implml/test.implml']})
        
        data = config.layered_content().data
        self.assertEquals(data, {'foo.txt': ['layer1/content/foo.txt',
                                             'layer2/content/foo.txt']})
        
        data = config.layered_doc().data
        self.assertEquals(data, {'bar.txt': ['layer1/doc/bar.txt',
                                             'layer2/doc/bar.txt']})
        
    
    def test_implml_override(self):
        p  = api.Project(api.Storage.open(LAYERED_RES_PROJECT))
        config = p.get_configuration('root.confml')
        
        impl_set = plugin.get_impl_set(config)
        self.assertEquals([impl.ref for impl in impl_set], ['layer2/implml/test.implml'])
        
        impl_set = plugin.filtered_impl_set(config)
        self.assertEquals([impl.ref for impl in impl_set], ['layer2/implml/test.implml'])
         
    
    def test_create_configuration(self):
        conf = api.Configuration("foobar/testmee.confml")
        self.assertTrue(conf)
    
    def test_get_root(self):
        conf = api.Configuration("foobar/testmee.confml")
        self.assertEquals(conf.get_path(),"foobar/testmee.confml")
    
    def test_add_layer(self):
        conf = api.Configuration("data/simple.confml")
        conf.add_configuration(api.Configuration("foo.confml",namespace="foo"))
        self.assertEquals(conf.list_configurations(),["foo.confml"])
    
    def test_meta_desc(self):
        conf = api.Configuration("test.confml")
        conf.meta = {'test':'data','test2':'value'}
        conf.desc = "Description osos"
        self.assertEquals(conf.meta['test'],"data")
        self.assertEquals(conf.meta['test2'],"value")
        self.assertEquals(conf.desc,"Description osos")


    def test_project_list_all_sequence_features(self):
        fs = api.Storage.open(test_project)
        p  = api.Project(fs)
        config = p.get_configuration('root5.confml')
        view = config.get_default_view()
        print "Fealist %s." % len(view.list_all_features())
        self.assertEquals(len(view.list_all_features()), 99)
        for feaname in view.list_all_features():
            fea = view.get_feature(feaname)
            if fea.get_type() == 'sequence':
                print "%s" % feaname,
                print "Value = %s" % fea.get_value()
                print "RFS = %s" % fea.get_value(attr='rfs')

    def test_get_implml_container(self):
        fs = api.Storage.open(test_project)
        p  = api.Project(fs)
        config = p.get_configuration('root5.confml')
        implcont = plugin.get_impl_set(config, 'foo$')
        self.assertEquals(implcont.list_implementation(),[])
    
    def test_multiple_open_configurations_in_one_project(self):
        prj = api.Project(api.Storage.open(multiroot_project, "r"))
        
        conf1 = prj.get_configuration('root1.confml')
        
        # Getting the same configuration again should return the same object
        self.assertTrue(conf1 is prj.get_configuration('root1.confml'))
        
        conf2 = prj.get_configuration('root2.confml')
        self.assertFalse(conf1 is conf2)
        
        # Test getting default views
        dview1 = conf1.get_default_view()
        dview2 = conf2.get_default_view()
        dview3 = prj.get_configuration('root3.confml').get_default_view()
        dview4 = prj.get_configuration('root4.confml').get_default_view()
        dview5 = prj.get_configuration('root5.confml').get_default_view()
        self.assertFalse(dview1 is dview2)
        self.assertFalse(dview2 is dview3)
        self.assertFalse(dview3 is dview4)
        self.assertFalse(dview4 is dview5)
        self.assertTrue(dview1 is conf1.get_default_view())
        
        # Test listing features from different configurations
        self.assertEquals(dview1.list_all_features(), dview2.list_all_features())
        self.assertEquals(dview2.list_all_features(), dview3.list_all_features())
        # Layer 4 introduces a new feature
        self.assertNotEquals(dview3.list_all_features(), dview4.list_all_features())        
        self.assertTrue('Layer4Feature' in dview4.list_all_features())
        self.assertTrue('Layer4Feature.RealSetting' in dview4.list_all_features())
        self.assertEquals(dview4.list_all_features(), dview5.list_all_features())
        
        # Test getting the same feature from different configurations
        FEATURE_REF = 'Feature1.StringSetting'
        ss1 = dview1.get_feature(FEATURE_REF)
        ss2 = dview2.get_feature(FEATURE_REF)
        ss3 = dview3.get_feature(FEATURE_REF)
        ss4 = dview4.get_feature(FEATURE_REF)
        ss5 = dview5.get_feature(FEATURE_REF)
        self.assertFalse(ss1 is ss2)
        self.assertFalse(ss2 is ss3)
        self.assertFalse(ss3 is ss4)
        self.assertFalse(ss4 is ss5)
        
        # Test getting values for the features
        self.assertEquals(ss1.get_value(), 'default string')
        self.assertEquals(ss2.get_value(), 'layer 2 string')
        self.assertEquals(ss3.get_value(), 'layer 3 string')
        self.assertEquals(ss4.get_value(), 'layer 4 string')
        # Layer 5 contains no data, so the value should be the same as on layer 4
        self.assertEquals(ss5.get_value(), 'layer 4 string')


#if __name__ == '__main__':
#      unittest.main()


def profile_project_list_all_features():
    fs = api.Storage.open(configproject)
    p  = api.Project(fs)
    config = p.get_configuration('s60.confml')
    view = config.get_default_view()
    print "Fealist %s." % len(view.list_all_features())
    #for fea in view.list_all_features():
    #    if view.get_feature(fea).get_type() == 'sequence':
    #        print "%s" % fea
    #        print " = %s" % view.get_feature(fea).get_value()
if __name__ == '__main__':
    
      import cProfile
      cProfile.run('profile_project_list_all_features()',None,'time')
