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
Test the CPF metadata file parsing routines
"""
import os, unittest
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

from cone.public import exceptions
from cone.storage import metadata, stringstorage
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
emptytestdata  = '<?xml version="1.0" encoding="ASCII"?>'\
'<metadata xmlns="http://www.nokia.com/xml/ns/confml-core/metadata-2.0"/>'


testdata  = \
'<metadata xmlns="http://www.nokia.com/xml/ns/confml-core/metadata-2.0">'\
'  <property name="cpf.name" value="test"/>'\
'  <property name="cpf.description" value="just testing"/>'\
'  <property name="cpf.viewId" value="Sample View"/>'\
'  <property name="cpf.rootFile" value="root.confml"/>'\
'  <property name="cpf.dataFile"/>'\
'  <property name="cpf.author"/>'\
'  <property name="cpf.version"/>'\
'  <property name="cpf.product"/>'\
'  <property name="cpf.customer"/>'\
'  <property name="cpf.platform"/>'\
'  <property name="cpf.release"/>'\
'  <property name="cpf.date"/>'\
'  <property name="cpf.owner"/>'\
'</metadata>'\

class TestMetadataReader(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_create_meta_fromstring(self):
        m = metadata.MetadataReader().fromstring(testdata)
        self.assertTrue(m)
        
    def test_create_meta_fromstring_test_has_key(self):
        m = metadata.MetadataReader().fromstring(testdata)
        self.assertTrue(m.data.has_key('cpf.name'))
        self.assertTrue(m.data.has_key('cpf.description'))
        self.assertTrue(m.data.has_key('cpf.viewId'))
        self.assertTrue(m.data.has_key('cpf.rootFile'))
        self.assertEquals(m.data['cpf.name'], 'test')
        self.assertEquals(m.data['cpf.description'], 'just testing')
        self.assertEquals(m.data['cpf.viewId'], 'Sample View')
        self.assertEquals(m.data['cpf.rootFile'], 'root.confml')

    def test_str_to_meta_and_back(self):
        meta = metadata.MetadataReader().fromstring(testdata)
        str = metadata.MetadataWriter().tostring(meta,False)
        self.assertTrue(str.find('cpf.name'))
        
    def test_get_property(self):
        etree = ElementTree.fromstring('<property name="test" value="test"/>')
        (key,value) = metadata.MetadataReader().get_property(etree)
        self.assertEquals(key,'test')
        self.assertEquals(value,'test')
        
    def test_get_property_with_only_key(self):
        etree = ElementTree.fromstring('<property name="test"/>')
        (key,value) = metadata.MetadataReader().get_property(etree)
        self.assertEquals(key,'test')
        self.assertEquals(value,'')

class TestMetadataWriter(unittest.TestCase):
    def setUp(self):
        pass

    def test_metadata_tostring(self):
        meta = metadata.Metadata()
        str = metadata.MetadataWriter().tostring(meta)
        self.assertTrue(str,emptytestdata)

    def test_metadata_with_values_tostring(self):
        meta = metadata.Metadata()
        meta.data['cpf.name'] = 'testing ss'
        meta.data['cpf.description'] = 'foo faa'
        str = metadata.MetadataWriter().tostring(meta)
        self.assertTrue(str,'<metadata xmlns="http://www.nokia.com/xml/ns/confml-core/metadata-2.0"><property name="cpf.name" value="testing ss" /><property name="cpf.description" value="foo faa" /></metadata>')

    def test_metadata_with_values_to_resource(self):
        meta = metadata.Metadata()
        meta.data['cpf.name'] = 'testing ss'
        meta.data['cpf.description'] = 'foo faa'
        storage = stringstorage.StringStorage("")
        res = storage.open_resource(".metadata","w")
        metadata.MetadataWriter().toresource(meta,res)
        self.assertTrue(res.getvalue(),'<metadata xmlns="http://www.nokia.com/xml/ns/confml-core/metadata-2.0"><property name="cpf.name" value="testing ss" /><property name="cpf.description" value="foo faa" /></metadata>')

    def test_metadata_from_meta_to_str_and_back(self):
        meta = metadata.Metadata()
        meta.data['cpf.name'] = 'testing ss'
        meta.data['cpf.description'] = 'foo faa'
        str = metadata.MetadataWriter().tostring(meta)
        meta2 = metadata.MetadataReader().fromstring(str)
        self.assertEqual(meta.data,meta2.data)

    def test_metadata_write_with_empty_data(self):
        meta = metadata.Metadata()
        str = metadata.MetadataWriter().tostring(meta)
        meta2 = metadata.MetadataReader().fromstring(str)
        self.assertEqual(meta.data,meta2.data)

    def test_incorrect_class_fails(self):
        try:
            class dummy:
                pass 
            str = metadata.MetadataWriter().tostring(dummy())
            self.fail("Writing dummy class succeeds!")
        except exceptions.IncorrectClassError,e:
            pass
        
        
    def test_set_property(self):
        elem = ElementTree.Element('property')
        mwriter = metadata.MetadataWriter()
        prop_elem = mwriter.set_property(elem,'test','foof')
        self.assertTrue(prop_elem.get('name'),'test')
        self.assertTrue(prop_elem.get('value'),'foof')

    def test_set_property_with_only_key(self):
        elem = ElementTree.Element('property')
        prop = metadata.MetadataWriter().set_property(elem,'test','')
        self.assertEquals(prop.get('name'),'test')
        self.assertEquals(prop.get('value'),None)


if __name__ == '__main__':
    unittest.main()
      
