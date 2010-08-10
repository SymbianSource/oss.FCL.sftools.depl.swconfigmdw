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

import unittest, os
import copy

from genconfmlplugin import confflattener
from cone.public import api
from cone.storage import filestorage

# Hardcoded value of testdata folder that must be under the current working dir
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
testdata  = os.path.join(ROOT_PATH,'project')
try:
    from cElementTree import ElementTree
except ImportError:
    try:    
        from elementtree import ElementTree
    except ImportError:
        try:
            from xml.etree import cElementTree as ElementTree
        except ImportError:
            from xml.etree import ElementTree

class TestGenconfmlPlugin(unittest.TestCase):    
    def setUp(self):
        self.curdir = os.getcwd()
        self.output = 'output'
        pass

    def tearDown(self):
        pass
        
    def test_flat(self):
        '''
        Test that the configuration flattening works
        '''
        fs = filestorage.FileStorage(testdata)
        p = api.Project(fs)
        config = p.get_configuration('product.confml')
        flat = p.create_configuration('flat.confml')
        dview = config.get_default_view()
        for fea in dview.get_features('**'):
            newfea = copy.copy(fea._obj)
            flat.add_feature(newfea, fea.namespace)
        toview = flat.get_default_view()
        for fea in toview.get_features('**'):
            fromfea = dview.get_feature(fea.fqr)
            if fromfea.get_value() != None:
                fea.set_value(fromfea.get_value())
        flat.close()
        config.close()
        
        config = p.get_configuration('product.confml')
        flat = p.get_configuration('flat.confml')
        fdview = flat.get_default_view()
        for fea in config.get_default_view().get_features('**'):
            self.assertEquals(fea.get_value(),fdview.get_feature(fea.fqr).get_value())
        
        pass

    def test_flat2(self):
        '''
        Test that the configuration flattening works
        '''
        fs = filestorage.FileStorage(testdata,"a")
        p = api.Project(fs)
        config = p.get_configuration('product.confml')
        confflat = confflattener.ConfigurationFlattener()
        confflat.create_configuration(config, ['DNs/**'],"tempfile2.confml")
        config = p.get_configuration('root_cvc.confml')
        dview = config.get_default_view()
        flat = p.get_configuration('tempfile2.confml')
        fdview = flat.get_default_view()
        for fea in fdview.get_features('**'):
            self.assertEquals(fea.get_value(),dview.get_feature(fea.fqr).get_value())
        dataconf = flat.get_configuration('tempfile2_data.confml')
        fearefs = fdview.list_all_features()
        for dataref in dataconf.list_all_datas():
            self.assertTrue(dataref in fearefs,"%s not in %s" % (dataref,fearefs))

    def test_flat3(self):
        '''
        Test that the configuration flattening works
        '''
        fs = filestorage.FileStorage(testdata)
        p = api.Project(fs)
        config = p.get_configuration('product.confml')
        confflat = confflattener.ConfigurationFlattener()
        confflat.create_configuration(config, ['Contacts/Contact'],"contacts_flat.confml")

        config = p.get_configuration('product.confml')
        dview = config.get_default_view()
        flat = p.get_configuration('contacts_flat.confml')
        fdview = flat.get_default_view()
        for fea in fdview.get_features('**'):
            self.assertEquals(fea.get_value(),dview.get_feature(fea.fqr).get_value())
        dataconf = flat.get_configuration('contacts_flat_data.confml')
        fearefs = fdview.list_all_features()
        for dataref in dataconf.list_all_datas():
            self.assertTrue(dataref in fearefs,"%s not in %s" % (dataref,fearefs))

if __name__ == '__main__':
  unittest.main()
