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

import os
import unittest
import logging

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
TESTDATA_DIR = os.path.join(ROOT_PATH, 'testdata')
TEMP_DIR = os.path.join(ROOT_PATH, 'temp')

from testautomation.base_testcase import BaseTestCase
from cone.public import api
import cone.validation.confmlvalidation

class TestConfmlFixing(unittest.TestCase):
    def test_confml_fixer_filter_problems(self):
        fixer = cone.validation.confmlvalidation.FixerBase()
        prbs = [api.Problem("msg1", type="test.foo.bar"),
                api.Problem("msg2", type="test.foo.bar"),
                api.Problem("msg3", type="test.foo.faa"),
                api.Problem("msg4", type="test.foo.bar")]
        self.assertEquals(len(fixer.filter_problems(prbs,'test.foo.bar')),3)

    def test_get_fixer_classes(self):
        fixers = cone.validation.confmlvalidation.get_fixer_classes()
        self.assertEquals(len(fixers),1)

class TestConfmlFixModel(BaseTestCase):
    def test_fix_duplicates(self):
        prj_dir = os.path.join(TESTDATA_DIR, 'model/confml/single_files')
        prj = api.Project(api.Storage.open(prj_dir))
        conf = prj.get_configuration("duplicate_root.confml")
        vc = cone.validation.confmlvalidation.fix_configuration(conf)
        self.assertEqual(len(vc.fixes), 1)
        self.assertEquals(conf.list_configurations(),['duplicate_settings1.confml', 
                                                      'duplicate_settings2.confml'])
        subconf1 = conf.get_configuration('duplicate_settings1.confml')
        subconf2 = conf.get_configuration('duplicate_settings2.confml')
        self.assertEquals(subconf2.list_all_features(),[])
        self.assertEquals(subconf1.list_all_features(),['Feature', 
                                                        'Feature.One', 
                                                        'Feature.Two', 
                                                        'Feature.Three', 
                                                        'Feature.NoData',
                                                        'Feature.TestSequence', 
                                                        'Feature.TestSequence.SeqTwo', 
                                                        'Feature.TestSequence.SeqThree'])

class TestConfmlFixingFiles(BaseTestCase):
        
    def test_export_fixed_configuration_test(self):
        # Open the file as a configuration
        prj_dir = os.path.join(TESTDATA_DIR, 'model/confml/single_files')
        prj = api.Project(api.Storage.open(prj_dir))
        conf = prj.get_configuration('duplicate_root.confml')
        vc = cone.validation.confmlvalidation.fix_configuration(conf)
        self.recreate_dir(os.path.join(TEMP_DIR,'fixed'))
        rstorage = api.Storage.open(os.path.join(TEMP_DIR,'fixed'), "w")
        prj.export_configuration(conf, rstorage)
        rstorage.save()
        rstorage.close()
        self.assert_dir_contents_equal(os.path.join(TEMP_DIR,'fixed'),
                                       os.path.join(TESTDATA_DIR, 'model/confml/fixed_expected'),
                                       ignore=[".metadata", '.svn'])
        
