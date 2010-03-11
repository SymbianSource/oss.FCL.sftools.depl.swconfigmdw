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

import os, unittest
import __init__
from cone.public import plugin
from hcrplugin.hcrml_parser import HcrmlReader

def impl_from_resource(resource_ref, configuration):
    """
    Read a HCRML implementation from the given resource in a configuration.
    """
    doc_root = plugin.ReaderBase._read_xml_doc_from_resource(resource_ref, configuration)
    return HcrmlReader.read_impl(resource_ref, configuration, doc_root)

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

NAMESPACE = 'http://www.symbianfoundation.org/xml/hcrml/1'

TEST_HCRML_DATA = """<?xml version="1.0" encoding="UTF-8"?>
<hcr xmlns="%s">
  <output file="test.h" type="header">
    <category name="KTestCategory" uid="0x11223344">
      <setting ref="Feature1.Setting1" name="F1S1" type="int32" id="0"/>
      <setting ref="Feature1.Setting2" name="F1S2" type="int32" id="1"/>
      <setting ref="Feature2.Setting1" name="F2S1" type="int32" id="2"/>
      <setting ref="Feature2.Setting2" name="F2S2" type="int32" id="3"/>
    </category>
  </output>
</hcr>
""" % NAMESPACE

HCR_DAT_HCRML_DATA = """<?xml version="1.0" encoding="UTF-8"?>
<hcr xmlns="%s">
  <output file="sys/data/hcr.dat" type="hcr">
    <include ref="*.hcrml"/>
  </output>
</hcr>
""" % NAMESPACE

NO_OUTPUT_HCRML_DATA = """<?xml version="1.0" encoding="UTF-8"?>
<hcr xmlns="%s">
  <category name="KTestCategory2" uid="0x44332211">
    <setting ref="Feature3.Setting1" name="F3S1" type="int32" id="0x10"/>
    <setting ref="Feature3.Setting2" name="F3S2" type="int32" id="0x20"/>
  </category>
</hcr>
""" % NAMESPACE

class Dummy(object):
    pass

class DummyConfiguration(object):
    RESOURCES = {
        'layer1/test.hcrml'         : TEST_HCRML_DATA,
        'layer2/no_output.hcrml'    : NO_OUTPUT_HCRML_DATA,
        'layer4/hcr_dat.hcrml'      : HCR_DAT_HCRML_DATA,
    }
    
    def list_resources(self):
        return sorted(self.RESOURCES.keys())
    
    def get_resource(self, res_ref):
        res = Dummy()
        res.read = lambda: self.RESOURCES[res_ref]
        res.close = lambda: None
        return res
    
    def get_default_view(self):
        view = Dummy()
        feature = Dummy()
        feature.get_value = lambda: 0
        view.get_feature = lambda ref: feature
        return view

class TestHcrmlImpl(unittest.TestCase):
    
    def test_has_ref(self):
        impl = impl_from_resource('layer1/test.hcrml', DummyConfiguration())
        self.assertTrue(impl.has_ref(['Feature1.Setting1']))
        self.assertTrue(impl.has_ref(['Feature1.Setting2']))
        self.assertTrue(impl.has_ref(['Feature2.Setting1']))
        self.assertTrue(impl.has_ref(['Feature2.Setting2']))
        self.assertTrue(impl.has_ref(['Feature1.Setting1', 'foo.bar']))
        self.assertTrue(impl.has_ref(['Feature1.Setting1', 'Feature1.Setting2']))
        
        self.assertFalse(impl.has_ref([]))
        self.assertFalse(impl.has_ref(['foo.bar']))
        self.assertFalse(impl.has_ref(['Feature1.Setting3']))
        self.assertFalse(impl.has_ref(['x.y.z', 'foo.bar']))
        self.assertFalse(impl.has_ref(['Feature3.Setting1']))
        self.assertFalse(impl.has_ref(['Feature3.Setting2']))
        
        impl = impl_from_resource('layer2/no_output.hcrml', DummyConfiguration())
        self.assertFalse(impl.has_ref([]))
        self.assertFalse(impl.has_ref(['foo.bar']))
        self.assertFalse(impl.has_ref(['Feature1.Setting1']))
        self.assertFalse(impl.has_ref(['Feature1.Setting2']))
        self.assertFalse(impl.has_ref(['Feature2.Setting1']))
        self.assertFalse(impl.has_ref(['Feature2.Setting2']))
        self.assertTrue(impl.has_ref(['Feature3.Setting1']))
        self.assertTrue(impl.has_ref(['Feature3.Setting2']))
        
        
        # hcr_dat.hcrml includes test.hcrml and no_output.hcrml, but it should
        # not say that it has the setting references specified in those files
        impl = impl_from_resource('layer4/hcr_dat.hcrml', DummyConfiguration())
        repo = impl.output_obj.get_hcr_repository()
        # Check that the hcr_dat.hcrml implementation does contain the
        # records
        self.assertEquals(len(repo.records), 6)
        # Check that it doesn't report that it has the references
        self.assertFalse(impl.has_ref([]))
        self.assertFalse(impl.has_ref(['foo.bar']))
        self.assertFalse(impl.has_ref(['Feature1.Setting1']))
        self.assertFalse(impl.has_ref(['Feature1.Setting2']))
        self.assertFalse(impl.has_ref(['Feature2.Setting1']))
        self.assertFalse(impl.has_ref(['Feature2.Setting2']))
        self.assertFalse(impl.has_ref(['Feature3.Setting1']))
        self.assertFalse(impl.has_ref(['Feature3.Setting2']))
        
        
    def test_list_output_files(self):
        output_dir = 'some/test/output'
        
        impl = impl_from_resource('layer1/test.hcrml', DummyConfiguration())
        impl.set_output_root(output_dir)
        self.assertEquals(
            impl.list_output_files(),
            [os.path.normpath(os.path.join(output_dir, 'test.h'))])
        
        impl = impl_from_resource('layer4/hcr_dat.hcrml', DummyConfiguration())
        impl.set_output_root(output_dir)
        self.assertEquals(
            impl.list_output_files(),
            [os.path.normpath(os.path.join(output_dir, 'sys/data/hcr.dat'))])
        
        impl = impl_from_resource('layer2/no_output.hcrml', DummyConfiguration())
        impl.set_output_root(output_dir)
        self.assertEquals(impl.list_output_files(), [])
