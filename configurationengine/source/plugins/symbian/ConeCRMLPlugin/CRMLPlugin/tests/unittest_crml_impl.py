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

import sys, os, unittest

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

from cone.public import exceptions, plugin, api, container
from cone.public.plugin import FlatComparisonResultEntry, DuplicateImplementationEntry
from CRMLPlugin import crml_impl, crml_reader

def impl_from_resource(resource_ref, configuration):
    doc_root = plugin.ReaderBase._read_xml_doc_from_resource(resource_ref, configuration)
    return crml_reader.CrmlReader.read_impl(resource_ref, configuration, doc_root)

class MockGenerationContext(object):
    def __init__(self):
        self.tags = {}

class TestCrmlImpl(unittest.TestCase):

    def setUp(self):
        project_dir = os.path.join(ROOT_PATH, 'gen_project')
        self.project = api.Project(api.Storage.open(project_dir))
        self.config = self.project.get_configuration('root.confml')
    
    def test_has_ref(self):
        impl = impl_from_resource('Layer1/implml/00000001_feature1.crml', self.config)
        self.assertTrue(impl.has_ref(['Feature1.IntSetting']))
        self.assertTrue(impl.has_ref(['Feature1.RealSetting']))
        self.assertTrue(impl.has_ref(['Feature1.RealSetting', 'foo.bar']))
        
        impl = impl_from_resource('Layer1/implml/00000003_bitmask_test.crml', self.config)
        self.assertTrue(impl.has_ref(['BitmaskTest.Bit0']))
        self.assertFalse(impl.has_ref(['BitmaskTest.FooBit']))
        
        impl = impl_from_resource('Layer1/implml/0000000C_key_range.crml', self.config)
        self.assertTrue(impl.has_ref(['KeyRangeTest.EmptySequenceSetting']))
        self.assertTrue(impl.has_ref(['KeyRangeTest.EmptySequenceSetting.StringSubSetting']))
        self.assertFalse(impl.has_ref(['KeyRangeTest']))
        self.assertFalse(impl.has_ref(['KeyRangeTest.Foo']))
    
    def test_list_output_files(self):
        def on( p2): # on = output normalization
            return os.path.normpath(p2)
        
        impl = impl_from_resource('Layer1/implml/00000001_feature1.crml', self.config)
        self.assertEquals(impl.list_output_files(), [on('00000001.txt')])
        
        impl = impl_from_resource('Layer1/implml/00000003_bitmask_test.crml', self.config)
        self.assertEquals(impl.list_output_files(), [on('00000003.txt')])
        
        gc = MockGenerationContext()
        gc.tags['target'] = ['core']
        impl.generation_context = gc
        self.assertEquals(impl.list_output_files(), [on('00000003.txt'), on('private/100059C9/cenrep_rfs.txt')])
    
    def test_is_cenrep_rfs_txt_to_be_generated(self):
        impl = impl_from_resource('Layer1/implml/00000001_feature1.crml', self.config)
        self.assertFalse(impl._is_cenrep_rfs_txt_to_be_generated())
        
        gc = MockGenerationContext()
        impl.generation_context = gc
        self.assertFalse(impl._is_cenrep_rfs_txt_to_be_generated())
        gc.tags['target'] = []
        self.assertFalse(impl._is_cenrep_rfs_txt_to_be_generated())
        gc.tags['target'] = ['uda']
        self.assertFalse(impl._is_cenrep_rfs_txt_to_be_generated())
        gc.tags['target'] = ['rofs3']
        self.assertFalse(impl._is_cenrep_rfs_txt_to_be_generated())
        gc.tags['target'] = ['rofs2']
        self.assertTrue(impl._is_cenrep_rfs_txt_to_be_generated())
        gc.tags['target'] = ['core']
        self.assertTrue(impl._is_cenrep_rfs_txt_to_be_generated())
        gc.tags['target'] = ['core', 'rofs3']
        self.assertTrue(impl._is_cenrep_rfs_txt_to_be_generated())
        gc.tags['target'] = ['uda', 'rofs2']
        self.assertTrue(impl._is_cenrep_rfs_txt_to_be_generated())
    
    def _open_config(self, project, config='root.confml'):
        project_dir = os.path.join(ROOT_PATH, project)
        project = api.Project(api.Storage.open(project_dir))
        return project.get_configuration(config)
    
    def test_compare(self):
        conf1 = self._open_config('comp_project_1')
        conf2 = self._open_config('comp_project_2')
        
        crml_file = None
        repo_uid = None
        
        def entry(**kwargs):
            kwargs['file']      = crml_file
            kwargs['impl_type'] = 'crml'
            kwargs['id']        = repo_uid
            return plugin.FlatComparisonResultEntry(**kwargs)
        
        comparison_result = None
        
        crml_file = 'Layer1/implml/00000001_simple_keys.crml'
        impl_filter = '00000001_simple_keys.crml$'
        repo_uid = '0x00000001'
        impls1 = plugin.get_impl_set(conf1, impl_filter)
        impls2 = plugin.get_impl_set(conf2, impl_filter)
        actual_result = impls1.flat_compare(impls2)
        
        expected_mods = [
            entry(sub_id='0x00000001', value_id='type',     source_value='int', target_value='real'),
            entry(sub_id='0x00000002', value_id='backup',   source_value=True,  target_value=False),
            
            entry(sub_id='0x00000003', value_id='read_only', source_value=True,     target_value=False),
            entry(sub_id='0x00000004', value_id='read_only', source_value=False,    target_value=True),
            # Changing read-only changes also cap_wr
            entry(sub_id='0x00000003', value_id='cap_wr',   source_value='AlwaysFail',    target_value=None),
            entry(sub_id='0x00000004', value_id='cap_wr',   source_value=None,            target_value='AlwaysFail'),
            
            entry(sub_id='0x00000005', value_id='type',     source_value='int',                 target_value='real'),
            entry(sub_id='0x00000006', value_id='name',     source_value='Setting 6',           target_value='Setting 6 (name changed)'),
            entry(sub_id='0x00000007', value_id='ref',      source_value='SimpleKeys.Setting7', target_value='SimpleKeys.Setting7RefChanged'),
            entry(sub_id='0x00000008', value_id='cap_rd',   source_value='ReadDeviceData',      target_value='ReadUserData'),
            entry(sub_id='0x00000008', value_id='cap_wr',   source_value='WriteDeviceData',     target_value='WriteUserData'),
            entry(sub_id='0x00000008', value_id='sid_rd',   source_value='0xAABBCCDD',          target_value='0x11223344'),
            entry(sub_id='0x00000008', value_id='sid_wr',   source_value='0xDDCCBBAA',          target_value='0x44332211'),
            entry(sub_id='0x00000009', value_id='cap_rd',   source_value='ReadDeviceData',      target_value=None),
            entry(sub_id='0x00000009', value_id='cap_wr',   source_value='WriteDeviceData',     target_value=None),
            entry(sub_id='0x00000009', value_id='sid_rd',   source_value='0xAABBCCDD',          target_value=None),
            entry(sub_id='0x00000009', value_id='sid_wr',   source_value='0xDDCCBBAA',          target_value=None),
        ]
        expected_removed = [
            entry(sub_id='0x10000001'),
            entry(sub_id='0x10000002'),
        ]
        expected_added = [
            entry(sub_id='0x20000001'),
            entry(sub_id='0x20000002'),
        ]
        expected_result = plugin.FlatComparisonResult(modified=expected_mods,
                                                      only_in_source=expected_removed,
                                                      only_in_target=expected_added)
        self.assertEquals(actual_result, expected_result)
        
    
    def test_compare_all(self):
        conf1 = self._open_config('comp_project_1')
        conf2 = self._open_config('comp_project_2')
        impls1 = plugin.get_impl_set(conf1)
        impls2 = plugin.get_impl_set(conf2)
        actual_result = impls1.flat_compare(impls2)
        
        expected_result = plugin.FlatComparisonResult(
            only_in_source = [
            FlatComparisonResultEntry(file='Layer1/implml/00000001_simple_keys.crml', impl_type='crml', id='0x00000001', sub_id='0x10000001'),
            FlatComparisonResultEntry(file='Layer1/implml/00000001_simple_keys.crml', impl_type='crml', id='0x00000001', sub_id='0x10000002'),
            FlatComparisonResultEntry(file='Layer1/implml/00000002_bitmask_keys.crml', impl_type='crml', id='0x00000002', sub_id='0x00000001 (bit 4)'),
            FlatComparisonResultEntry(file='Layer1/implml/00000002_bitmask_keys.crml', impl_type='crml', id='0x00000002', sub_id='0x00000003 (bit 4)'),
            FlatComparisonResultEntry(file='Layer1/implml/00000002_bitmask_keys.crml', impl_type='crml', id='0x00000002', sub_id='0x10000001'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00001001-0x00001FFF (sub-key 0x00000004)'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00003001-0x00003FFF (sub-key 0x00000004)'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x10001001-0x10001FFF'),
            FlatComparisonResultEntry(file='Layer1/implml/10000001_removed_repo.crml', impl_type='crml', id='0x10000001'),
            ],
            only_in_target = [
            FlatComparisonResultEntry(file='Layer1/implml/00000001_simple_keys.crml', impl_type='crml', id='0x00000001', sub_id='0x20000001'),
            FlatComparisonResultEntry(file='Layer1/implml/00000001_simple_keys.crml', impl_type='crml', id='0x00000001', sub_id='0x20000002'),
            FlatComparisonResultEntry(file='Layer1/implml/00000002_bitmask_keys.crml', impl_type='crml', id='0x00000002', sub_id='0x00000001 (bit 5)'),
            FlatComparisonResultEntry(file='Layer1/implml/00000002_bitmask_keys.crml', impl_type='crml', id='0x00000002', sub_id='0x00000003 (bit 5)'),
            FlatComparisonResultEntry(file='Layer1/implml/00000002_bitmask_keys.crml', impl_type='crml', id='0x00000002', sub_id='0x20000001'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00001001-0x00001FFF (sub-key 0x00000005)'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00003001-0x00003FFF (sub-key 0x00000005)'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x20001001-0x20001FFF'),
            FlatComparisonResultEntry(file='Layer1/implml/20000001_added_repo.crml', impl_type='crml', id='0x20000001'),
            ],
            modified = [
            FlatComparisonResultEntry(file='Layer1/implml/00000001_simple_keys.crml', impl_type='crml', id='0x00000001', sub_id='0x00000001', value_id='type', source_value='int', target_value='real'),
            FlatComparisonResultEntry(file='Layer1/implml/00000001_simple_keys.crml', impl_type='crml', id='0x00000001', sub_id='0x00000002', value_id='backup', source_value=True, target_value=False),
            FlatComparisonResultEntry(file='Layer1/implml/00000001_simple_keys.crml', impl_type='crml', id='0x00000001', sub_id='0x00000003', value_id='cap_wr', source_value='AlwaysFail', target_value=None),
            FlatComparisonResultEntry(file='Layer1/implml/00000001_simple_keys.crml', impl_type='crml', id='0x00000001', sub_id='0x00000003', value_id='read_only', source_value=True, target_value=False),
            FlatComparisonResultEntry(file='Layer1/implml/00000001_simple_keys.crml', impl_type='crml', id='0x00000001', sub_id='0x00000004', value_id='cap_wr', source_value=None, target_value='AlwaysFail'),
            FlatComparisonResultEntry(file='Layer1/implml/00000001_simple_keys.crml', impl_type='crml', id='0x00000001', sub_id='0x00000004', value_id='read_only', source_value=False, target_value=True),
            FlatComparisonResultEntry(file='Layer1/implml/00000001_simple_keys.crml', impl_type='crml', id='0x00000001', sub_id='0x00000005', value_id='type', source_value='int', target_value='real'),
            FlatComparisonResultEntry(file='Layer1/implml/00000001_simple_keys.crml', impl_type='crml', id='0x00000001', sub_id='0x00000006', value_id='name', source_value='Setting 6', target_value='Setting 6 (name changed)'),
            FlatComparisonResultEntry(file='Layer1/implml/00000001_simple_keys.crml', impl_type='crml', id='0x00000001', sub_id='0x00000007', value_id='ref', source_value='SimpleKeys.Setting7', target_value='SimpleKeys.Setting7RefChanged'),
            FlatComparisonResultEntry(file='Layer1/implml/00000001_simple_keys.crml', impl_type='crml', id='0x00000001', sub_id='0x00000008', value_id='cap_rd', source_value='ReadDeviceData', target_value='ReadUserData'),
            FlatComparisonResultEntry(file='Layer1/implml/00000001_simple_keys.crml', impl_type='crml', id='0x00000001', sub_id='0x00000008', value_id='cap_wr', source_value='WriteDeviceData', target_value='WriteUserData'),
            FlatComparisonResultEntry(file='Layer1/implml/00000001_simple_keys.crml', impl_type='crml', id='0x00000001', sub_id='0x00000008', value_id='sid_rd', source_value='0xAABBCCDD', target_value='0x11223344'),
            FlatComparisonResultEntry(file='Layer1/implml/00000001_simple_keys.crml', impl_type='crml', id='0x00000001', sub_id='0x00000008', value_id='sid_wr', source_value='0xDDCCBBAA', target_value='0x44332211'),
            FlatComparisonResultEntry(file='Layer1/implml/00000001_simple_keys.crml', impl_type='crml', id='0x00000001', sub_id='0x00000009', value_id='cap_rd', source_value='ReadDeviceData', target_value=None),
            FlatComparisonResultEntry(file='Layer1/implml/00000001_simple_keys.crml', impl_type='crml', id='0x00000001', sub_id='0x00000009', value_id='cap_wr', source_value='WriteDeviceData', target_value=None),
            FlatComparisonResultEntry(file='Layer1/implml/00000001_simple_keys.crml', impl_type='crml', id='0x00000001', sub_id='0x00000009', value_id='sid_rd', source_value='0xAABBCCDD', target_value=None),
            FlatComparisonResultEntry(file='Layer1/implml/00000001_simple_keys.crml', impl_type='crml', id='0x00000001', sub_id='0x00000009', value_id='sid_wr', source_value='0xDDCCBBAA', target_value=None),
            FlatComparisonResultEntry(file='Layer1/implml/00000002_bitmask_keys.crml', impl_type='crml', id='0x00000002', sub_id='0x00000001', value_id='cap_rd', source_value='ReadDeviceData', target_value='ReadUserData'),
            FlatComparisonResultEntry(file='Layer1/implml/00000002_bitmask_keys.crml', impl_type='crml', id='0x00000002', sub_id='0x00000001', value_id='cap_wr', source_value='WriteDeviceData', target_value='WriteUserData'),
            FlatComparisonResultEntry(file='Layer1/implml/00000002_bitmask_keys.crml', impl_type='crml', id='0x00000002', sub_id='0x00000001', value_id='name', source_value='Bitmask 1', target_value='Bitmask 1 (name changed)'),
            FlatComparisonResultEntry(file='Layer1/implml/00000002_bitmask_keys.crml', impl_type='crml', id='0x00000002', sub_id='0x00000001', value_id='sid_rd', source_value='0xAABBCCDD', target_value='0x11223344'),
            FlatComparisonResultEntry(file='Layer1/implml/00000002_bitmask_keys.crml', impl_type='crml', id='0x00000002', sub_id='0x00000001', value_id='sid_wr', source_value='0xDDCCBBAA', target_value='0x44332211'),
            FlatComparisonResultEntry(file='Layer1/implml/00000002_bitmask_keys.crml', impl_type='crml', id='0x00000002', sub_id='0x00000001', value_id='type', source_value='int', target_value='binary'),
            FlatComparisonResultEntry(file='Layer1/implml/00000002_bitmask_keys.crml', impl_type='crml', id='0x00000002', sub_id='0x00000001 (bit 2)', value_id='ref', source_value='BitmaskKeys.Bit2', target_value='BitmaskKeys.Bit2RefChanged'),
            FlatComparisonResultEntry(file='Layer1/implml/00000002_bitmask_keys.crml', impl_type='crml', id='0x00000002', sub_id='0x00000001 (bit 3)', value_id='invert', source_value=False, target_value=True),
            FlatComparisonResultEntry(file='Layer1/implml/00000002_bitmask_keys.crml', impl_type='crml', id='0x00000002', sub_id='0x00000003', value_id='name', source_value='Modified read-only bitmask', target_value='Modified read-only bitmask (name changed)'),
            FlatComparisonResultEntry(file='Layer1/implml/00000002_bitmask_keys.crml', impl_type='crml', id='0x00000002', sub_id='0x00000003', value_id='type', source_value='int', target_value='binary'),
            FlatComparisonResultEntry(file='Layer1/implml/00000002_bitmask_keys.crml', impl_type='crml', id='0x00000002', sub_id='0x00000003 (bit 2)', value_id='ref', source_value='BitmaskKeys.Bit2', target_value='BitmaskKeys.Bit2RefChanged'),
            FlatComparisonResultEntry(file='Layer1/implml/00000002_bitmask_keys.crml', impl_type='crml', id='0x00000002', sub_id='0x00000003 (bit 3)', value_id='invert', source_value=False, target_value=True),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00001001-0x00001FFF', value_id='backup', source_value=True, target_value=False),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00001001-0x00001FFF', value_id='cap_rd', source_value='ReadDeviceData', target_value='ReadUserData'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00001001-0x00001FFF', value_id='cap_wr', source_value='WriteDeviceData', target_value='WriteUserData'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00001001-0x00001FFF', value_id='first_index', source_value=1L, target_value=2L),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00001001-0x00001FFF', value_id='index_bits', source_value='0x00000FF0', target_value='0x00001FE0'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00001001-0x00001FFF', value_id='name', source_value='Sequence 1', target_value='Sequence 1 (name changed)'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00001001-0x00001FFF', value_id='ref', source_value='KeyRanges.Seq1', target_value='KeyRanges.Seq1RefChanged'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00001001-0x00001FFF', value_id='sid_rd', source_value='0x11223344', target_value='0xAABBCCDD'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00001001-0x00001FFF', value_id='sid_wr', source_value='0x44332211', target_value='0xDDCCBBAA'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00001001-0x00001FFF (sub-key 0x00000002)', value_id='name', source_value='Sub-setting 2', target_value='Sub-setting 2 (name changed)'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00001001-0x00001FFF (sub-key 0x00000002)', value_id='ref', source_value='SubSetting2', target_value='SubSetting2RefChanged'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00001001-0x00001FFF (sub-key 0x00000002)', value_id='type', source_value='int', target_value='real'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00002000-0x00002FFF', value_id='backup', source_value=True, target_value=False),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00002000-0x00002FFF', value_id='read_only', source_value=True, target_value=False),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00003000-0x00003FFF', value_id='read_only', source_value=False, target_value=True),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00003001-0x00003FFF', value_id='cap_rd', source_value='ReadDeviceData', target_value='ReadUserData'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00003001-0x00003FFF', value_id='cap_wr', source_value='WriteDeviceData', target_value='WriteUserData'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00003001-0x00003FFF', value_id='first_index', source_value=1, target_value=2),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00003001-0x00003FFF', value_id='index_bits', source_value='0x00000FF0', target_value='0x00001FE0'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00003001-0x00003FFF', value_id='name', source_value='Read-only sequence', target_value='Read-only sequence (name changed)'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00003001-0x00003FFF', value_id='ref', source_value='KeyRanges.ReadOnlySeq', target_value='KeyRanges.ReadOnlySeqRefChanged'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00003001-0x00003FFF', value_id='sid_rd', source_value='0x11223344', target_value='0xAABBCCDD'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00003001-0x00003FFF', value_id='sid_wr', source_value='0x44332211', target_value='0xDDCCBBAA'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00003001-0x00003FFF (sub-key 0x00000002)', value_id='name', source_value='Sub-setting 2', target_value='Sub-setting 2 (name changed)'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00003001-0x00003FFF (sub-key 0x00000002)', value_id='ref', source_value='SubSetting2', target_value='SubSetting2RefChanged'),
            FlatComparisonResultEntry(file='Layer1/implml/00000003_key_ranges.crml', impl_type='crml', id='0x00000003', sub_id='0x00003001-0x00003FFF (sub-key 0x00000002)', value_id='type', source_value='int', target_value='real'),
            FlatComparisonResultEntry(file='Layer1/implml/00000004_key_type_changed.crml', impl_type='crml', id='0x00000004', sub_id='0x00000001', value_id='key_type', source_value='simple_key', target_value='bitmask_key'),
            FlatComparisonResultEntry(file='Layer1/implml/00000004_key_type_changed.crml', impl_type='crml', id='0x00000004', sub_id='0x00000002', value_id='key_type', source_value='bitmask_key', target_value='simple_key'),
            FlatComparisonResultEntry(file='Layer1/implml/00000004_key_type_changed.crml', impl_type='crml', id='0x00000004', sub_id='0x00000003', value_id='backup', source_value=True, target_value=False),
            FlatComparisonResultEntry(file='Layer1/implml/00000004_key_type_changed.crml', impl_type='crml', id='0x00000004', sub_id='0x00000003', value_id='cap_rd', source_value='ReadDeviceData', target_value='ReadUserData'),
            FlatComparisonResultEntry(file='Layer1/implml/00000004_key_type_changed.crml', impl_type='crml', id='0x00000004', sub_id='0x00000003', value_id='cap_wr', source_value='AlwaysFail', target_value='WriteUserData'),
            FlatComparisonResultEntry(file='Layer1/implml/00000004_key_type_changed.crml', impl_type='crml', id='0x00000004', sub_id='0x00000003', value_id='name', source_value='Bitmask key to simple key (other attrs changed also)', target_value='Bitmask key to simple key (other attrs changed also [xyz])'),
            FlatComparisonResultEntry(file='Layer1/implml/00000004_key_type_changed.crml', impl_type='crml', id='0x00000004', sub_id='0x00000003', value_id='read_only', source_value=True, target_value=False),
            FlatComparisonResultEntry(file='Layer1/implml/00000004_key_type_changed.crml', impl_type='crml', id='0x00000004', sub_id='0x00000003', value_id='sid_rd', source_value='0xAABBCCDD', target_value='0x11223344'),
            FlatComparisonResultEntry(file='Layer1/implml/00000004_key_type_changed.crml', impl_type='crml', id='0x00000004', sub_id='0x00000003', value_id='sid_wr', source_value=None, target_value='0x44332211'),
            FlatComparisonResultEntry(file='Layer1/implml/00000004_key_type_changed.crml', impl_type='crml', id='0x00000004', sub_id='0x00000003', value_id='type', source_value='int', target_value='binary'),
            FlatComparisonResultEntry(file='Layer1/implml/00000005_repo_attrs_changed.crml', impl_type='crml', id='0x00000005', sub_id=None, value_id='backup', source_value=True, target_value=False),
            FlatComparisonResultEntry(file='Layer1/implml/00000005_repo_attrs_changed.crml', impl_type='crml', id='0x00000005', sub_id=None, value_id='cap_rd', source_value='ReadDeviceData', target_value='ReadUserData'),
            FlatComparisonResultEntry(file='Layer1/implml/00000005_repo_attrs_changed.crml', impl_type='crml', id='0x00000005', sub_id=None, value_id='cap_wr', source_value='WriteDeviceData', target_value='WriteUserData'),
            FlatComparisonResultEntry(file='Layer1/implml/00000005_repo_attrs_changed.crml', impl_type='crml', id='0x00000005', sub_id=None, value_id='rfs', source_value=True, target_value=False),
            FlatComparisonResultEntry(file='Layer1/implml/00000005_repo_attrs_changed.crml', impl_type='crml', id='0x00000005', sub_id=None, value_id='sid_rd', source_value='0x11223344', target_value='0xAABBCCDD'),
            FlatComparisonResultEntry(file='Layer1/implml/00000005_repo_attrs_changed.crml', impl_type='crml', id='0x00000005', sub_id=None, value_id='sid_wr', source_value='0x44332211', target_value='0xDDCCBBAA'),
            FlatComparisonResultEntry(file='Layer1/implml/00000005_repo_attrs_changed.crml', impl_type='crml', id='0x00000005', sub_id=None, value_id='uid_name', source_value='RepoAttrsChanged', target_value='RepoAttrsChangedXyz'),
            FlatComparisonResultEntry(file='Layer1/implml/00000006_renamed_repo_xyz.crml', impl_type='crml', id='0x00000006', sub_id=None, value_id='file', source_value='Layer1/implml/00000006_renamed_repo.crml', target_value='Layer1/implml/00000006_renamed_repo_xyz.crml'),
            ],
            duplicate = [
            DuplicateImplementationEntry(impl_type='crml', id='0x30000000', files_in_source=['Layer1/implml/30000000_duplicate_repo1_proj1.crml', 'Layer1/implml/30000000_duplicate_repo2_proj1.crml'], files_in_target=['Layer1/implml/30000000_duplicate_repo2_proj2.crml', 'Layer1/implml/30000000_duplicate_repo1_proj2.crml'])
            ])
        self.assertEquals(actual_result, expected_result)
