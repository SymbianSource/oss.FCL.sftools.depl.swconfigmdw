from __future__ import with_statement
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

from cone.public import api
from cone.storage.filestorage import FileStorage
from testautomation import unzip_file
from testautomation.base_testcase import BaseTestCase

ROOT_PATH       = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR        = os.path.join(ROOT_PATH, "temp/edit_data")
TEST_CPF        = os.path.join(ROOT_PATH, "testdata/test_project.cpf")

class open_config_and_get_dview(object):
    def __init__(self, project, mode, config):
        self.project_path = project
        self.mode = mode
        self.config = config
        self.project = None

    def __enter__(self):
        self.project = api.Project(FileStorage(self.project_path, self.mode))
        conf = self.project.get_configuration(self.config)
        dview = conf.get_default_view()
        return dview
        setting = dview.get_feature(self.setting_ref)
        return setting

    def __exit__(self, type, value, tb):
        if self.project:
            if self.mode == 'a':
                self.project.save()
            self.project.close()

class open_config_and_get_setting(open_config_and_get_dview):
    def __init__(self, project, mode, config, setting):
        open_config_and_get_dview.__init__(self, project, mode, config)
        self.setting_ref = setting

    def __enter__(self):
        dview = open_config_and_get_dview.__enter__(self)
        setting = dview.get_feature(self.setting_ref)
        return setting

class TestEditConfigurationProjectData(BaseTestCase):
    
    def test_edit_sequence_data_on_last_layer_with_dview(self):
        PROJ = os.path.join(TEMP_DIR, "test_project_1")
        CONF = 'root3.confml'
        SETTING = 'Feature2.SequenceSetting'
        unzip_file.unzip_file(TEST_CPF, PROJ, delete_if_exists=True)
        
        # Open the temp project in append mode
        with open_config_and_get_setting(PROJ, 'a', CONF, SETTING) as setting:
            self.assertEquals(setting.value,
                [[333, 'layer3 (1)'],
                 [1, 'default 1'],
                 [2, 'default 2'],
                 [222, 'layer2 (1)'],
                 [222, 'layer2 (2)'],
                 [222, 'layer2 (3)']])
        
            # Change the value
            setting.value = [[123, 'foo1'],
                             [456, 'foo2']]
        
        # Reopen the project in read mode and check that the sequence data
        # was modified correctly
        with open_config_and_get_setting(PROJ, 'r', CONF, SETTING) as setting:
            self.assertEquals(setting.value,
                              [[123, 'foo1'],
                               [456, 'foo2']])
            self.assertEquals(setting.get_original_value(),
                              [['123', 'foo1'],
                               ['456', 'foo2']])
        
        # Modify the sequence data again by setting it empty
        with open_config_and_get_setting(PROJ, 'a', CONF, SETTING) as setting:
            setting.value = []
            self.assertEquals(setting.value, [])
            self.assertEquals(setting.get_original_value(), [])
        
        # Reopen and check again
        with open_config_and_get_setting(PROJ, 'r', CONF, SETTING) as setting:
            self.assertEquals(setting.value, [])
            self.assertEquals(setting.get_original_value(), [])
        
        # Do the same 'set empty' check with a more complex sequence setting
        SETTING = 'SequenceSettingTest.SequenceSetting'
        with open_config_and_get_setting(PROJ, 'a', CONF, SETTING) as setting:
            setting.value = []
            self.assertEquals(setting.value, [])
            self.assertEquals(setting.get_original_value(), [])
        with open_config_and_get_setting(PROJ, 'r', CONF, SETTING) as setting:
            self.assertEquals(setting.value, [])
            self.assertEquals(setting.get_original_value(), [])
    
    def test_edit_complex_sequence_data_on_last_layer_with_dview(self):
        PROJ = os.path.join(TEMP_DIR, "test_project_4")
        CONF = 'root3.confml'
        SETTING = 'SequenceSettingTest.SequenceSetting'
        unzip_file.unzip_file(TEST_CPF, PROJ, delete_if_exists=True)
        
        # Open the temp project in append mode
        with open_config_and_get_setting(PROJ, 'a', CONF, SETTING) as setting:
            self.assertEquals(setting.value,
                [[['seq/layer2_folder2', None], 2.1000000000000001, ['seq/layer2_file2.txt', None], 222, 'L22', True, '1', ('opt 1', 'opt 3'), '\x22\x22'],
                 [['seq/layer2_folder', None], 2.0, ['seq/layer2_file.txt', None], 22, 'L21', True, '2', ('opt 2',), '\x22\x11'],
                 [['seq/def1_folder', None], 1.25, ['seq/def1_file.txt', None], 128, 'def1', False, '1', ('opt 1',), '\x00\x11'],
                 [['seq/def2_folder', None], 1.5, ['seq/def2_file.txt', None], 256, 'def2', False, '1', ('opt 2',), '\x00\x22'],
                 [['seq/layer3_folder', None], 3.0, ['seq/layer3_file.txt', None], 33, 'L31', False, '0', ('opt 3', 'opt 2'), '\x33\x11'],
                 [['seq/layer3_folder', None], 3.3500000000000001, [None, None], 1, 'L32', True, '2', ('opt 1', 'opt 2'), '\x33\x22']])
            
            # Change the value
            setting.value = [[['seq/foofolder1', None], 5.6, ['seq/foofile1.txt', None], 1010, 'Lfoo', False, '3', ('opt 4', 'opt 0'), '\xaa\xbb'],
                             [['seq/foofolder2', None], 6.5, ['seq/foofile2.txt', None], 2020, 'Lfoo', True, '3', (), ''],
                             [['seq/foofolder1', None], 5.6, ['seq/foofile1.txt', None], 1010, 'Lfoo', False, '3', ('opt 4', 'opt 0'), '\xaa\xbb']]
        
        with open_config_and_get_setting(PROJ, 'r', CONF, SETTING) as setting:
            self.assertEquals(setting.value,
                [[['seq/foofolder1', None], 5.6, ['seq/foofile1.txt', None], 1010, 'Lfoo', False, '3', ('opt 4', 'opt 0'), '\xaa\xbb'],
                 [['seq/foofolder2', None], 6.5, ['seq/foofile2.txt', None], 2020, 'Lfoo', True, '3', (), ''],
                 [['seq/foofolder1', None], 5.6, ['seq/foofile1.txt', None], 1010, 'Lfoo', False, '3', ('opt 4', 'opt 0'), '\xaa\xbb']])
        # Modify the sequence data again by setting it empty
        with open_config_and_get_setting(PROJ, 'a', CONF, SETTING) as setting:
            setting.value = []
        
        # Reopen and check again
        with open_config_and_get_setting(PROJ, 'r', CONF, SETTING) as setting:
            self.assertEquals(setting.value, [])

    def test_edit_data_on_last_layer_with_dview(self):
        PROJ = os.path.join(TEMP_DIR, "test_project_2")
        CONF = 'root3.confml'
        unzip_file.unzip_file(TEST_CPF, PROJ, delete_if_exists=True)
        
        # Open the temp project in append mode
        with open_config_and_get_dview(PROJ, 'a', CONF) as dview:
            self.assertEquals(dview.get_feature('BasicSettingTypesTest.IntSetting').value,          333)
            self.assertEquals(dview.get_feature('BasicSettingTypesTest.BooleanSetting').value,      False)
            self.assertEquals(dview.get_feature('BasicSettingTypesTest.RealSetting').value,         3.1456)
            self.assertEquals(dview.get_feature('BasicSettingTypesTest.SelectionSetting').value,    '3')
            self.assertEquals(dview.get_feature('BasicSettingTypesTest.StringSetting').value,       'layer 3 string')
            self.assertEquals(dview.get_feature('BasicSettingTypesTest.MultiSelectionSetting').value, ('opt 1', 'opt 3'))
            self.assertEquals(dview.get_feature('BasicSettingTypesTest.HexBinarySetting').value, '\x00\x11\x22\x33\x44\x55\x66\x77\x88\x99\xaa\xbb\xcc\xdd\xee\xff')
        
            dview.get_feature('BasicSettingTypesTest.IntSetting').value         = 1500
            dview.get_feature('BasicSettingTypesTest.BooleanSetting').value     = True
            dview.get_feature('BasicSettingTypesTest.RealSetting').value        = 15.15
            dview.get_feature('BasicSettingTypesTest.SelectionSetting').value   = '1'
            dview.get_feature('BasicSettingTypesTest.StringSetting').value      = 'edit data test'
            dview.get_feature('BasicSettingTypesTest.MultiSelectionSetting').value = ('opt 4', 'opt 0')
            dview.get_feature('BasicSettingTypesTest.HexBinarySetting').value = '\x12\x34'
        
        # Reopen the project in read mode and check that the sequence data
        # was modified correctly
        with open_config_and_get_dview(PROJ, 'r', CONF) as dview:
            self.assertEquals(dview.get_feature('BasicSettingTypesTest.IntSetting').value,          1500)
            self.assertEquals(dview.get_feature('BasicSettingTypesTest.BooleanSetting').value,      True)
            self.assertEquals(dview.get_feature('BasicSettingTypesTest.RealSetting').value,         15.15)
            self.assertEquals(dview.get_feature('BasicSettingTypesTest.SelectionSetting').value,    '1')
            self.assertEquals(dview.get_feature('BasicSettingTypesTest.StringSetting').value,       'edit data test')
            self.assertEquals(dview.get_feature('BasicSettingTypesTest.MultiSelectionSetting').value, ('opt 4', 'opt 0'))
            self.assertEquals(dview.get_feature('BasicSettingTypesTest.HexBinarySetting').value, '\x12\x34')
        
        # Test that setting the multi-selection setting to empty works
        SETTING = 'BasicSettingTypesTest.MultiSelectionSetting'
        with open_config_and_get_setting(PROJ, 'a', 'root4.confml', SETTING) as setting:
            self.assertEquals(setting.value, ('opt 0', 'opt 4'))
            setting.value = ()
            self.assertEquals(setting.value, ())
        with open_config_and_get_setting(PROJ, 'r', 'root4.confml', SETTING) as setting:
            self.assertEquals(setting.value, ())
    
    def test_read_name_id_mapped_values(self):
        PROJ = os.path.join(TEMP_DIR, "test_project_5")
        CONF = 'root3.confml'
        unzip_file.unzip_file(TEST_CPF, PROJ, delete_if_exists=True)
        
        with open_config_and_get_dview(PROJ, 'r', CONF) as dview:
            def check(setting, expected_value):
                fea = dview.get_feature('NameIdMappingTestTargetSettings.' + setting)
                self.assertEquals(fea.get_value(), expected_value)
            
            check('Selection',       'seq1_item2')
            check('Selection2',      12)
            check('MultiSelection',  ('seq1_item1', 'seq1_item2', 'seq2_item2', 'seq2_item3'))
            check('MultiSelection2', (11, 12, True, False))
            check('String',          'seq1_item2')
            check('Int',             12)
            check('Real',            1.2)
            check('Boolean',         False)
            
            check('Sequence.Selection',       ['seq1_item2'])
            check('Sequence.Selection2',      [12])
            check('Sequence.MultiSelection',  [('seq1_item1', 'seq1_item2', 'seq2_item2', 'seq2_item3')])
            check('Sequence.MultiSelection2', [(11, 12, True, False)])
            check('Sequence.String',          ['seq1_item2'])
            check('Sequence.Int',             [12])
            check('Sequence.Real',            [1.2])
            check('Sequence.Boolean',         [False])

if __name__ == '__main__':
    unittest.main()
