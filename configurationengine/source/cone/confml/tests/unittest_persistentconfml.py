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
Test the CPF root file parsing routines
"""

import unittest
import string
import sys
import os
import shutil
import __init__
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

from cone.public import api, exceptions, persistence
from cone.storage import filestorage
from cone.confml import persistentconfml, model
from testautomation.base_testcase import BaseTestCase
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

testdata  = os.path.join(ROOT_PATH,'data')

simplerootxml = \
'''<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns="http://www.s60.com/xml/confml/1" xmlns:xi="http://www.w3.org/2001/xinclude" name="simple" version="1">
  <xi:include href="platform/s60/confml/test.confml#/"/>
</configuration>
'''

newincludexml = '''<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns="http://www.s60.com/xml/confml/1" xmlns:xi="http://www.w3.org/2001/XInclude" name="simple" version="1">
  <xi:include href="platform/s60/confml/test.confml"/>
</configuration>'''

complexrootxml = '''<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns="http://www.s60.com/xml/confml/1" xmlns:xi="http://www.w3.org/2001/xinclude" name="simple" version="1">
  <xi:include href="platform/s60/confml/test.confml#/"/>
  <xi:include href="platform/jallaa/confml/root.confml#/"/>
  <xi:include href="configB/confml/configB.confml#/"/>
  <xi:include href="ncp33/prod/confml/root.confml#/"/>
</configuration>'''


morestuff='''<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns="http://www.s60.com/xml/confml/1" xmlns:xi="http://www.w3.org/2001/xinclude" name="foobar" version="1">
  <meta xmlns:cv="http://www.nokia.com/xml/cpf-id/1">
    <cv:configuration-property name="coreplat_name" value="abc_123" />
    <cv:configuration-property name="product_name" value="qwerty" />
    <owner>Variant1 creator</owner>
    <origin>somestorage:somelocation_123/and/path</origin>
    <target>proto_b2</target>
  </meta>
  <desc>This is a configuration for Product1 Region1 Variant1 </desc>
  <xi:include href="platform/s60/confml/root.confml"/>
  <xi:include href="ncp11/confml/jallaa.confml"/>
  <xi:include href="ncp11/prodX/confml/root.confml"/>
  <xi:include href="regional/japan/confml/root.confml"/>
</configuration>'''

actualconfml='''<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns="http://www.s60.com/xml/confml/1" name="accesspoints">
  <feature ref="KCRUidApEngineLV" name="KCRUidApEngineLV">
    <desc></desc>
    <setting ref="KApEngineLVFlags" name="KApEngineLVFlags"/>
  </feature>
  <feature ref="KCRUidApSettingsHandlerUiLV" name="KCRUidApSettingsHandlerUiLV">
    <desc></desc>
    <setting ref="KApSettingsHandlerUiLVFlags" name="KApSettingsHandlerUiLVFlags"/>
    <setting ref="KAIStatusPaneLayout" name="Status Pane Layout" type="selection">
      <desc>Status pane layout setting. 0 = normal, 1 = flat, 2 = hidden</desc>
      <option name="normal" value="0"/>
      <option name="flat" value="1"/>
      <option name="hidden" value="2"/>
    </setting>
  </feature>
  <feature name="Customer Menu" ref="CVC_OperatorMenu">
    <desc>Often referred to as the Operator Menu, the Customer Menu is an application that launches the browser as an embedded application with a predefined URL as parameter. The URL defines the xHTML Startup page that is shown when the Customer Menu application is launched, for example www.customername.com/index.html. The URL also defines the customer domain URL path, for example www.customername.com/. All user-browsed xHTML pages belonging to that path are automatically stored in the Customer Menu cache.The Customer Menu application can be configured as a shortcut just like any other application. In Main menu, the Customer Menu is placed by default to 11th position. When the Customer Menu is enabled, Help moves from position 11 to 12 and Apps moves from 12 to 13, which is not visible until the user scrolls the menu cursor.</desc>
       <setting name="Customer Menu icon" ref="CVC_OperatorMenuIconFile" type="file">
            <desc>Customer menu icon that will be present in Application Grid. Size: 65 x 65 pixels. Format: SVGT (preferred) or BMP. Color depth: 24 bit</desc>
        <localPath/>
        <targetPath readOnly="true"/>
      </setting>
  </feature>
  <data>
    <KCRUidApEngineLV>
      <KApEngineLVFlags>0</KApEngineLVFlags>
    </KCRUidApEngineLV>
    <KCRUidApSettingsHandlerUiLV>
      <KApSettingsHandlerUiLVFlags>0</KApSettingsHandlerUiLVFlags>
      <KAIStatusPaneLayout>0</KAIStatusPaneLayout>
    </KCRUidApSettingsHandlerUiLV>
    <CVC_OperatorMenu>
      <CVC_OperatorMenuIconFile>
        <localPath>UI/Customer Menu/Cache</localPath>
      </CVC_OperatorMenuIconFile>
    </CVC_OperatorMenu>
  </data>
  <rfs>
    <KCRUidApEngineLV>
      <KApEngineLVFlags>true</KApEngineLVFlags>
    </KCRUidApEngineLV>
    <KCRUidApSettingsHandlerUiLV>
      <KApSettingsHandlerUiLVFlags>false</KApSettingsHandlerUiLVFlags>
    </KCRUidApSettingsHandlerUiLV>
  </rfs>
</configuration>
'''

sequencesettings = \
'''<?xml version="1.0" encoding="utf-8"?><configuration xmlns="http://www.s60.com/xml/confml/1" name="BrowserBookmarks">
<feature name="BookmarkItems" ref="BookmarkItems">
  <setting name="BookmarkItem" ref="BookmarkItem" type="sequence">
    <setting name="Type Of Bookmark" ref="Type" type="selection">
      <desc>This defines the Type of the element created. To create a Folder item - select "Folder". To create a bookmark item - select "Item".</desc>
      <option name="Folder" value="Folder"/>
      <option name="Item" value="Item"/>
    </setting>
    <setting name="Name Of The New Entry" ref="Name" type="string">
      <desc>Text field containing name for the Folder or Bookmark.  Must be unique.</desc>
    </setting>
  </setting>
</feature>
<data>
  <BookmarkItems>
    <BookmarkItem template="true">
      <Type>Template</Type>
      <Name>Download Applications</Name>
    </BookmarkItem>
    <BookmarkItem>
      <Type>Folder1</Type>
      <Name>Download Applications</Name>
    </BookmarkItem>
    <BookmarkItem>
      <Type>Folder2</Type>
      <Name>Download Images</Name>
    </BookmarkItem>
    <BookmarkItem>
      <Type>Folder3</Type>
    </BookmarkItem>
  </BookmarkItems>
</data>
</configuration>
'''

simpleview = \
'''<?xml version="1.0" encoding="UTF-8"?>
<confml:configuration  xmlns:confml="http://www.s60.com/xml/confml/1" schemaLocation="http://www.s60.com/xml/confml/1 http://www.s60.com/xml/confml/1#//confml2">
  <feature ref="imaker" name="iMaker Image creation">
    <setting ref="imagetarget" name="IMAGE_TARGET" type="selection">
      <option name="core" value="0"/>
      <option name="rofs2" value="1"/>
      <option name="rofs3" value="2"/>
      <option name="rofs4" value="3"/>
      <option name="uda" value="4"/>
      <option name="rofs3_uda" value="4"/>
    </setting>
  </feature>
  <feature ref="imakerapi" name="iMaker API">
    <setting ref="imagetype" name="IMAGE_TYPE" type="selection">
      <option name="rnd" value="0"/>
      <option name="subcon" value="1"/>
      <option name="prd" value="2"/>
    </setting>
    <setting ref="rofs3version" name="ROFS3_VERSION" type="string"/>
    <setting ref="productname" name="PRODUCT_NAME" type="string"/>
    <setting ref="outputLocation" name="OUTPUT_LOCATION" type="string"/>
  </feature>
  <data>
    <imaker>
      <imagetarget>2</imagetarget>
    </imaker>
    <imakerapi>
      <imagetype>0</imagetype>
      <rofs3version>V .50.2009.04.0113 RND</rofs3version>
      <productname>myProduct</productname>
      <outputLocation>myProduct</outputLocation>
    </imakerapi>
  </data>
  <confml:view id="imakerimage" name="Image creation">
    <confml:desc>Image creation related settings</confml:desc>
    <confml:group name="Imageproperties">
      <confml:desc>Sample Description</confml:desc>
      <confml:setting ref="imakerapi/*"/>
      <confml:setting ref="imaker/*"/>
    </confml:group>
  </confml:view>
</confml:configuration>
'''

class TestModuleGetters(unittest.TestCase):
    def test_get_reader_for_configuration(self):
        confread = persistentconfml.get_reader_for_elem("configuration")
        self.assertTrue(isinstance(confread, persistentconfml.ConfigurationReader))

    def test_get_writer_for_configuration(self):
        confread = persistentconfml.get_writer_for_class("Configuration")
        self.assertTrue(isinstance(confread, persistentconfml.ConfigurationWriter))

    def test_get_elemname_from_string(self):
        self.assertEquals(persistentconfml.get_elemname("{http://www.s60.com/xml/confml/1}configuration")[0],"http://www.s60.com/xml/confml/1")
        self.assertEquals(persistentconfml.get_elemname("{http://www.s60.com/xml/confml/1}configuration")[1],"configuration")

    def test_get_elemname_from_element_tree(self):
        root = ElementTree.fromstring(simplerootxml)
        for elem in root.getiterator():
            (namespace,elemname) = persistentconfml.get_elemname(elem.tag)
        self.assertEquals(elemname,"include")

    def test_loads(self):
        config = persistentconfml.loads(simplerootxml)
        self.assertEquals(config.get_name(),"simple")

    def test_dumps(self):
        config = api.Configuration("test.confml")
        config.include_configuration('path/to/config.confml')
        dump = persistentconfml.dumps(config)
        elem = ElementTree.fromstring(dump)
        self.assertEquals(elem.get('name'),"test_confml")

class TestConfigurationParser(unittest.TestCase):    
    def test_load_simple(self):
        reader = persistentconfml.get_reader_for_elem("configuration")
        obj = reader.loads(ElementTree.fromstring(simplerootxml))
        self.assertEquals(obj.get_ref(),'simple')
        self.assertEquals(obj._list(),['platform__s60__confml__test_confml'])

    def test_load_new_include_confml(self):
        reader = persistentconfml.get_reader_for_elem("configuration")
        obj = reader.loads(ElementTree.fromstring(newincludexml))
        self.assertEquals(obj._list(),['platform__s60__confml__test_confml'])

    def test_load_complexrootxml(self):
        reader = persistentconfml.get_reader_for_elem("configuration")
        obj = reader.loads(ElementTree.fromstring(complexrootxml))
        self.assertEquals(obj._list(),['platform__s60__confml__test_confml',
                                        'platform__jallaa__confml__root_confml', 
                                        'configB__confml__configB_confml', 
                                        'ncp33__prod__confml__root_confml'])

    def test_load_morestuff(self):
        reader = persistentconfml.get_reader_for_elem("configuration")
        obj = reader.loads(ElementTree.fromstring(morestuff))
        self.assertEquals(obj._list(),['_meta','_desc','platform__s60__confml__root_confml', 'ncp11__confml__jallaa_confml', 'ncp11__prodX__confml__root_confml', 'regional__japan__confml__root_confml'])
        met = obj.meta
        self.assertEquals(obj.meta[2].value,'Variant1 creator')
        self.assertEquals(obj.meta[3].value,'somestorage:somelocation_123/and/path')
        self.assertEquals(obj.meta[4].value,'proto_b2')        
        self.assertEquals(obj.meta[0].tag,'configuration-property')
        self.assertEquals(obj.meta[0].value, None)
        self.assertEquals(obj.meta[0].ns,'http://www.nokia.com/xml/cpf-id/1')
        self.assertEquals(obj.meta[0].attrs,{"name": "coreplat_name", "value": "abc_123"})        
        self.assertEquals(obj.desc,'This is a configuration for Product1 Region1 Variant1 ')

    def test_load_morestuff_and_remove_included_configuration(self):
        reader = persistentconfml.get_reader_for_elem("configuration")
        obj = reader.loads(ElementTree.fromstring(morestuff))
        self.assertEquals(obj.list_configurations(),['platform/s60/confml/root.confml', 'ncp11/confml/jallaa.confml', 'ncp11/prodX/confml/root.confml', 'regional/japan/confml/root.confml'])
        obj.remove_configuration('platform/s60/confml/root.confml')
        self.assertEquals(obj.list_configurations(),['ncp11/confml/jallaa.confml', 'ncp11/prodX/confml/root.confml', 'regional/japan/confml/root.confml'])
        for configname in obj.list_configurations():
            obj.remove_configuration(configname)
        self.assertEquals(obj.list_configurations(),[])

    def test_load_actualconfml(self):
        reader = persistentconfml.get_reader_for_elem("configuration")
        obj = reader.loads(ElementTree.fromstring(actualconfml))
        self.assertEquals(obj.list_features(),['KCRUidApEngineLV', 'KCRUidApSettingsHandlerUiLV','CVC_OperatorMenu'])
        self.assertEquals(obj.list_all_features(),['KCRUidApEngineLV', 
                                                   'KCRUidApEngineLV.KApEngineLVFlags', 
                                                   'KCRUidApSettingsHandlerUiLV', 
                                                   'KCRUidApSettingsHandlerUiLV.KApSettingsHandlerUiLVFlags', 
                                                   'KCRUidApSettingsHandlerUiLV.KAIStatusPaneLayout', 
                                                   'CVC_OperatorMenu', 
                                                   'CVC_OperatorMenu.CVC_OperatorMenuIconFile',
                                                   'CVC_OperatorMenu.CVC_OperatorMenuIconFile.localPath', 
                                                   'CVC_OperatorMenu.CVC_OperatorMenuIconFile.targetPath'])
        fea = obj.KCRUidApSettingsHandlerUiLV.KApSettingsHandlerUiLVFlags
        vset = fea.get_valueset()
        self.assertTrue(fea.get_value() in vset)
        self.assertTrue('0' in obj.KCRUidApSettingsHandlerUiLV.KAIStatusPaneLayout.get_valueset())
        self.assertTrue('1' in obj.KCRUidApSettingsHandlerUiLV.KAIStatusPaneLayout.get_valueset())
        for fearef in obj.list_all_features():
            fea = obj.get_feature(fearef)
            if fea.get_type() == 'int':
                #print "Feature %s, %s: %s" % (fea.get_type(),fea.get_name(),fea.get_value()) 
                self.assertEquals(fea.get_value(),0)
        self.assertEquals(obj.get_feature('CVC_OperatorMenu.CVC_OperatorMenuIconFile.targetPath').get_value(),None)
        self.assertEquals(obj.get_feature('CVC_OperatorMenu.CVC_OperatorMenuIconFile.localPath').get_value(),'UI/Customer Menu/Cache')

    def test_create_features_with_rfs_data_and_dump_and_load(self):
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
        
        dumped = persistentconfml.dumps(conf)
        conf2 = persistentconfml.loads(dumped)
        dview = conf2.get_default_view()
        self.assertEquals(dview.get_feature('feature1.child1').get_value(), None)
        self.assertEquals(dview.get_feature('feature1.child1').get_value('rfs'), 'true')
        self.assertEquals(dview.get_feature('feature1.child2').get_value('rfs'), 'false')

    def test_load_actualconfml_test_rfs_settings(self):
        reader = persistentconfml.get_reader_for_elem("configuration")
        obj = reader.loads(ElementTree.fromstring(actualconfml))
        self.assertEquals(obj.get_feature('KCRUidApEngineLV.KApEngineLVFlags').rfs,True)
        self.assertEquals(obj.get_feature('KCRUidApSettingsHandlerUiLV.KApSettingsHandlerUiLVFlags').rfs,False)

    def test_load_sequence_confml(self):
        reader = persistentconfml.get_reader_for_elem("configuration")
        etree = ElementTree.fromstring(sequencesettings)
        obj = reader.loads(etree)
        dcont = obj.get_data('BookmarkItems')
        dview = obj.get_default_view()
        self.assertEquals(dview.get_feature('BookmarkItems.BookmarkItem').list_features(),['Type', 'Name'])
        self.assertEquals(dview.get_feature('BookmarkItems.BookmarkItem').list_all_features(),['Type', 'Name'])
        datatable = dview.get_feature('BookmarkItems.BookmarkItem').get_data()
        self.assertEquals(len(datatable), 3)
        self.assertEquals(datatable[0].list_features(), ['Type', 'Name'])
        self.assertEquals(datatable[0].get_feature('Name').get_value(), 'Download Applications')
        self.assertEquals(datatable[0][0].get_value(), 'Folder1')
        self.assertEquals(datatable[0][1].get_value(), 'Download Applications')
        self.assertEquals(dview.get_feature('BookmarkItems.BookmarkItem').get_value(), 
                          [
                          ['Folder1','Download Applications'],
                          ['Folder2','Download Images'],
                          ['Folder3',None]])

    def test_load_commsdat_sequence_confml_from_file(self):
        conffile = open(os.path.join(ROOT_PATH,"data/commsdatcreator.confml"))
        reader = persistentconfml.get_reader_for_elem("configuration")
        etree = ElementTree.fromstring(conffile.read())
        obj = reader.loads(etree)
        dview = obj.get_default_view()
        dnsfea = dview.get_feature('DNs.DN')
        self.assertEquals(dnsfea.list_features(),['Name', 'DNId', 'Metadata', 'Protection', 'Hidden', 'HiddenAgent', 'Highlighted', 'Icon', 'EmbeddedDN', 'IAP', 'IAP2', 'IAP3', 'IAP4', 'IAP5', 'IAP6', 'IAP7', 'IAP8', 'IAP9', 'IAP10'])
        self.assertEquals(dnsfea.get_template(),['User Defined', '0', 'No', 'No', 'No', '11', None, None, None, None, None, None, None, None, None, None, None, None, None])
        self.assertEquals(dnsfea.get_value(),
        [['Internet', '1', 'Internet', '2', 'No', 'No', 'Yes', '0', None, None, None, None, None, None, None, None, None, None, None],
         ['MMS', '2', 'MMS', '2', 'No', 'Yes', 'No', '2', None, None, None, None, None, None, None, None, None, None, None], 
         ['Operator', '3', 'Operator', '2', 'No', 'No', 'No', '4', None, None, None, None, None, None, None, None, None, None, None]
        ])

    def test_load_content_sequence_confml_from_file(self):
        conffile = open(os.path.join(ROOT_PATH,"data/CVC_Content.confml"))
        reader = persistentconfml.get_reader_for_elem("configuration")
        etree = ElementTree.fromstring(conffile.read())
        obj = reader.loads(etree)
        dview = obj.get_default_view()
        content = dview.get_feature('ContentFiles.contentfile')
        self.assertEquals(content.list_all_features(),['fileelem', 'fileelem.localPath', 'fileelem.targetPath'])
        self.assertEquals(content.value,[[['test/BookmarkImportSample.txt', None]]])
        self.assertEquals(content.fileelem.localPath.value,['test/BookmarkImportSample.txt'])

    def test_load_content_multiselection_confml_from_file(self):
        fs = filestorage.FileStorage(testdata)
        p = api.Project(fs)
        config = p.get_configuration('multiselection.confml')
        dview = config.get_default_view()
        multisel1 = dview.get_feature('MultiSelections.MultiSel1')
        self.assertEquals(multisel1.value,["first selection","second selection"])
        self.assertEquals(multisel1.get_data_cast(multisel1.get_value()),["first selection","second selection"])
        self.assertEquals(multisel1.get_value(),["first selection","second selection"])
        self.assertEquals(multisel1.get_data().get_value(),'"first selection" "second selection"')
        
        
    def test_load_content_multiselection_empty_confml_from_file(self):
        fs = filestorage.FileStorage(testdata)
        p = api.Project(fs)
        config = p.get_configuration('multiselection.confml')
        dview = config.get_default_view()
        multisel1 = dview.get_feature('uda_selection.selectedfiles')
        self.assertEquals(multisel1.get_value(),None)
        self.assertEquals(multisel1.get_data().get_value(),None)
        
        
        
    def test_add_sequence_data_to_separate_confml(self):
        prj = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'data'),"w"))
        config = prj.create_configuration('test2.confml')
        seqconfig = config.create_configuration('sequence.confml')
        config.create_configuration('testdata.confml')
        seqconfig.add_feature(api.FeatureSequence('feature1'))
        seqconfig.add_feature(api.Feature('child1'),'feature1')
        seqconfig.add_feature(api.Feature('child2'),'feature1')
        seqconfig.add_feature(api.Feature('child3'),'feature1')
        dview = config.get_default_view()
        self.assertEquals(dview.get_feature('feature1').get_type(),'sequence')
        dview.get_feature('feature1').set_template(['c1','c2','c3'])
        dview.get_feature('feature1').add_sequence(['row 1','43','56'])
        dview.get_feature('feature1').add_sequence(['row 2','43','56'])
        config.create_configuration('testdata2.confml')
        dview.get_feature('feature1').add_sequence(['row 3','43','56'])
        dview.get_feature('feature1').add_sequence(['row 4','43','56'])
        dview.get_feature('feature1').get_data()[1].set_value(['row 2 updated', 'foo', '56'])
        config.save()
        prj.close()
        prj = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'data')))
        config = prj.get_configuration('test2.confml')
        dview = config.get_default_view()
        self.assertEquals(dview.get_feature('feature1').get_template(),['c1','c2','c3'])
        self.assertEquals(dview.get_feature('feature1').get_value(),[['row 3', '43', '56'], 
                                                                     ['row 4', '43', '56']])
        self.assertEquals(dview.get_feature('feature1').get_data()[0]._index,0)
        self.assertEquals(dview.get_feature('feature1').get_data()[0].get_value(),['row 3', '43', '56'])
        self.assertEquals(dview.get_feature('feature1').get_data()[1].get_value(),['row 4', '43', '56'])
        self.assertEquals(dview.get_feature('feature1').get_data()[0].get_data().find_parent(type=api.Configuration), config.get_configuration('testdata2.confml')._obj)
        prj.remove_configuration('test2.confml')
        
        
    def test_add_sequence_data_to_separate_confml_with_append_policy(self):
        prj = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'data'),"w"))
        config = prj.create_configuration('test1.confml')
        seqconfig = config.create_configuration('sequence.confml')
        config.create_configuration('testdata.confml')
        seqconfig.add_feature(api.FeatureSequence('feature1'))
        seqconfig.add_feature(api.Feature('child1'),'feature1')
        seqconfig.add_feature(api.Feature('child2'),'feature1')
        seqconfig.add_feature(api.Feature('child3'),'feature1')
        dview = config.get_default_view()
        self.assertEquals(dview.get_feature('feature1').get_type(),'sequence')
        dview.get_feature('feature1').set_template(['c1','c2','c3'])
        dview.get_feature('feature1').add_sequence(['row 1','43','56'])
        dview.get_feature('feature1').add_sequence(['row 2','43','56'])
        config.create_configuration('testdata2.confml')
        dview.get_feature('feature1').add_sequence(['row 3','43','56'])
        dview.get_feature('feature1').add_sequence(['row 4','43','56'])
        dview.get_feature('feature1').get_data()[1].set_value(['row 2 updated', 'foo', '56'])
        config.save()
        prj.close()
        prj = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'data')))
        config = prj.get_configuration('test1.confml')
        dview = config.get_default_view()
        self.assertEquals(dview.get_feature('feature1').get_template(),['c1','c2','c3'])
        self.assertEquals(dview.get_feature('feature1').get_value(),[['row 3', '43', '56'], 
                                                                     ['row 4', '43', '56']])
        self.assertEquals(dview.get_feature('feature1').get_data()[0]._index,0)
        self.assertEquals(dview.get_feature('feature1').get_data()[0].get_value(),['row 3', '43', '56'])
        self.assertEquals(dview.get_feature('feature1').get_data()[1].get_value(),['row 4', '43', '56'])
        self.assertEquals(dview.get_feature('feature1').get_data()[0].get_data().find_parent(type=api.Configuration), config.get_configuration('testdata2.confml')._obj)
        prj.remove_configuration('test1.confml')
        
    def test_load_view(self):
        reader = persistentconfml.get_reader_for_elem("configuration")
        etree = ElementTree.fromstring(simpleview)
        obj = reader.loads(etree)
        self.assertEquals(obj.get_name(), 'unknown')
        self.assertEquals(obj.list_views(), ['Image creation'])
        self.assertEquals(obj.get_view('Image creation').get_name(),'Image creation')
        self.assertEquals(obj.get_view('Image creation').desc,'Image creation related settings')
        self.assertEquals(obj.get_view('Image creation').list_features(),[])
        self.assertEquals(obj.get_view('Image creation').list_groups(),['Imageproperties'])
        self.assertEquals(obj.get_view('Image creation').list_all_features(),['Imageproperties.imagetype', 
                                                                           'Imageproperties.rofs3version', 
                                                                           'Imageproperties.productname', 
                                                                           'Imageproperties.outputLocation', 
                                                                           'Imageproperties.imagetarget'])
        self.assertEquals(obj.get_view('Image creation').get_feature('Imageproperties.imagetype').get_value(), '0') 
        self.assertEquals(obj.get_view('Image creation').get_feature('Imageproperties.rofs3version').get_value(), 'V .50.2009.04.0113 RND') 
        self.assertEquals(obj.get_view('Image creation').get_feature('Imageproperties.productname').get_value(), 'myProduct') 
        self.assertEquals(obj.get_view('Image creation').get_feature('Imageproperties.outputLocation').get_value(), 'myProduct') 
        self.assertEquals(obj.get_view('Image creation').get_feature('Imageproperties.imagetarget').get_value(), '2') 
        
    def test_load_cvc_view(self):
        prj = api.Project(api.Storage.open(os.path.join(ROOT_PATH,'data')))
        config = prj.get_configuration('cvc_root.confml')
        dview = config.get_default_view()
        self.assertEquals(config.list_views(),['cvc_view_confml.Custom modeled ConfMLs for customization  foo'])
        view = config.get_view('cvc_view_confml.Custom modeled ConfMLs for customization  foo')
        self.assertEquals(view.id, 'CVC')
        self.assertEquals(view.list_groups(),['Applications', 'Connectivity', 'System', 'UI', 'Pre-Installed Content'])
        self.assertEquals(view.list_features(),[])
        group = view.get_group('Connectivity')
        self.assertEquals(group.icon, 'connectivity_48_nav.png')
        self.assertEquals(len(view.list_all_features()),130)


    def test_load_booleans_confml_from_file(self):
        conffile = open(os.path.join(ROOT_PATH,"data/booleans.confml"))
        reader = persistentconfml.get_reader_for_elem("configuration")
        etree = ElementTree.fromstring(conffile.read())
        obj = reader.loads(etree)
        dview = obj.get_default_view()
        boolfea = dview.get_feature('Booleans')
        self.assertEquals(len(boolfea.list_features()),20)

    def test_load_confml_with_properties(self):
        conffile = open(os.path.join(ROOT_PATH,"data/CVC_StartupShutdownAnimations.confml"))
        reader = persistentconfml.get_reader_for_elem("configuration")
        etree = ElementTree.fromstring(conffile.read())
        obj = reader.loads(etree)
        fea = obj.get_feature('CVC_StartupAnimationSequence.CVC_StartupAnimationTone')
        self.assertEquals(fea.list_properties(),['maxSize'])
        self.assertEquals(fea.properties['maxSize'].value,'100')

        conffile = open(os.path.join(ROOT_PATH,"data/CVC_Preinstalled.confml"))
        reader = persistentconfml.get_reader_for_elem("configuration")
        etree = ElementTree.fromstring(conffile.read())
        obj = reader.loads(etree)
        fea = obj.get_feature('CVC_PreinstalledContent.CVC_PreInstalledMMSs.CVC_PreInstalledMMS')
        self.assertEquals(fea.list_properties(),['maxFileSize'])
        self.assertEquals(fea.properties['maxFileSize'].value,'35')

    def test_load_voicemailbox_confml_from_file(self):
        conffile = open(os.path.join(ROOT_PATH,"data/voicemailbox.confml"))
        reader = persistentconfml.get_reader_for_elem("configuration")
        etree = ElementTree.fromstring(conffile.read())
        obj = reader.loads(etree)
        dview = obj.get_default_view()
        stringfea = dview.get_feature('KCRUidVoiceMailbox.KVmbxNumberLinePrimary')
        self.assertEquals(stringfea.type,'string')
        self.assertEquals(stringfea.value,None)
        
    def test_load_facets(self):
        conffile = open(os.path.join(ROOT_PATH,"data/facets.confml"))
        reader = persistentconfml.get_reader_for_elem("configuration")
        etree = ElementTree.fromstring(conffile.read())
        obj = reader.loads(etree)
        setting = obj.get_feature('Facets.MessageSize')
        self.assertEquals(setting.minInclusive,'0')
        self.assertEquals(setting.maxInclusive,'10')
        setting = obj.get_feature('Facets.MessageSize2')
        self.assertEquals(setting.minExclusive,'-1')
        self.assertEquals(setting.maxExclusive,'11')
        setting = obj.get_feature('Facets.StringPattern')
        self.assertEquals(setting.pattern,"[a-zA-Z]{5,10}")        
        setting = obj.get_feature('Facets.TotalDigits')
        self.assertEquals(setting.totalDigits,'3')
        dview = obj.get_default_view()
        intfea = dview.get_feature('Facets.MessageSize')
        self.assertEquals(intfea.type,'int')
        self.assertEquals(intfea.value,9)
             
class TestConfigurationWriter(unittest.TestCase):    
    def test_dump_simple_configuration(self):
        config = api.Configuration("test.confml")
        writer = persistentconfml.get_writer_for_class("Configuration")
        etree = writer.dumps(config)
        self.assertEquals(etree.get('name'), 'test_confml')

    def test_dump_configuration_with_include(self):
        config = api.Configuration("test.confml")
        config.include_configuration('path/to/config.confml')
        writer = persistentconfml.get_writer_for_class("Configuration")
        elem = writer.dumps(config)
        etree = ElementTree.fromstring(ElementTree.tostring(elem))
        self.assertEquals(etree.find('{http://www.w3.org/2001/XInclude}include').get('href'), 'path/to/config.confml')

    def test_dump_configuration_with_feature_sequence(self):
        config = api.Configuration("test.confml")
        config.add_feature(api.Feature('test'))
        config.add_feature(api.FeatureSequence('sequentialfeature'),'test')
        config.test.sequentialfeature.add_feature(model.ConfmlSetting('setting1'))
        config.test.sequentialfeature.add_feature(model.ConfmlSetting('setting2'))
        config.test.sequentialfeature.add_feature(model.ConfmlSetting('setting3'))
        writer = persistentconfml.get_writer_for_class("Configuration")
        elem = writer.dumps(config)
        etree = ElementTree.fromstring(ElementTree.tostring(elem))
        self.assertEquals([elem for elem in etree.getiterator('{http://www.s60.com/xml/confml/2}setting')][0].get('ref'), 'sequentialfeature')

    def test_dump_complex_configuration(self):
        config = api.Configuration("test.confml")
        config.include_configuration('path/to/config1.confml')
        config.include_configuration('path/to/config2.confml')
        config.include_configuration('path/to/config3.confml')
        config.add( model.ConfmlMeta([model.ConfmlMetaProperty('test', '123'),\
                                      model.ConfmlMetaProperty('model', 'foo')]))
        config.add( model.ConfmlDescription( 'Description text' ) )
        writer = persistentconfml.get_writer_for_class("Configuration")
        elem = writer.dumps(config)
        etree = ElementTree.fromstring(ElementTree.tostring(elem))
        self.assertEquals([elem.get('href') for elem in etree.getiterator('{http://www.w3.org/2001/XInclude}include')], 
                          ['path/to/config1.confml',
                           'path/to/config2.confml',
                           'path/to/config3.confml'
                           ])
        meta = etree.find('{http://www.s60.com/xml/confml/2}meta')
        self.assertEquals(meta.find('{http://www.s60.com/xml/confml/2}test').text,'123')
        self.assertEquals(meta.find('{http://www.s60.com/xml/confml/2}model').text,'foo')
        self.assertEquals(etree.find('{http://www.s60.com/xml/confml/2}desc').text,'Description text')

    def test_dump_load_configuration(self):
        writer = persistentconfml.get_writer_for_class("Configuration")
        config = model.ConfmlConfiguration("test.confml")
        config.include_configuration('path/to/config1.confml')
        config.include_configuration('path/to/config2.confml')
        config.include_configuration('path/to/config3.confml')
        config.meta = model.ConfmlMeta([model.ConfmlMetaProperty('test', '123'),\
                                      model.ConfmlMetaProperty('model', 'foo'),\
                                      model.ConfmlMetaProperty('configuration-property', None, \
                                                               'http://www.nokia.com/xml/cpf-id/1', \
                                                               attrs ={"name":"123", "value": "234"})])
        config.desc = 'Description text'
        etree= writer.dumps(config)
        xmlstr = ElementTree.tostring(etree)
        config2 = persistentconfml.get_reader_for_elem("configuration").loads(ElementTree.fromstring(xmlstr))
        self.assertEquals(config2.get_ref(),config.ref)
        self.assertEquals(config2._list(),config._list())
        self.assertEquals(config2.desc,'Description text')
        elem = config2.meta.get_property_by_tag('test')
        self.assertEquals(elem.tag, 'test')
        self.assertEquals(elem.value, '123')

        self.assertEquals(config2.meta[0].tag, 'test')
        self.assertEquals(config2.meta[0].value, '123')
        self.assertEquals(config2.meta[1].tag, 'model')
        self.assertEquals(config2.meta[1].value, 'foo')
        self.assertEquals(config2.meta[2].tag, 'configuration-property')
        self.assertEquals(config2.meta[2].value, None)
        self.assertEquals(config2.meta[2].ns, 'http://www.nokia.com/xml/cpf-id/1')
        self.assertEquals(config2.meta[2].attrs, {"name":"123", "value": "234"})


    def test_configuration_with_features_and_properties(self):
        config = model.ConfmlConfiguration("test.confml")
        config.add_feature(model.ConfmlSetting('testfea11'))
        config.testfea11.add_property(name='smaller',value='10')
        config.testfea11.add_property(name='bigger',value='1', unit='B')
        elem = persistentconfml.dumps(config)
        config2 =  persistentconfml.loads(elem)
        self.assertEquals(config2.testfea11.properties['smaller'].value,'10')
        self.assertEquals(config2.testfea11.properties['bigger'].value,'1')

    def test_configuration_with_features_and_minoccurs(self):
        config = model.ConfmlConfiguration("test.confml")
        config.add_feature(model.ConfmlSequenceSetting('testfea11'))
        config.testfea11.minOccurs = 1
        config.testfea11.maxOccurs = 10
        elem = persistentconfml.dumps(config)
        config2 =  persistentconfml.loads(elem)
        self.assertEquals(config2.testfea11.minOccurs,1)
        self.assertEquals(config2.testfea11.maxOccurs,10)

    def test_configuration_with_features_and_readonly(self):
        config = model.ConfmlConfiguration("test.confml")
        config.add_feature(model.ConfmlSequenceSetting('testfea11'))
        config.add_feature(model.ConfmlSetting('readme',readOnly=True))
        config.add_feature(model.ConfmlSetting('writeme',readOnly=False))
        elem = persistentconfml.dumps(config)
        config2 =  persistentconfml.loads(elem)
        self.assertEquals(config2.testfea11.readOnly,None)
        self.assertEquals(config2.readme.readOnly,True)
        self.assertEquals(config2.writeme.readOnly,False)

    def test_configuration_with_features_and_constraint(self):
        config = model.ConfmlConfiguration("test.confml")
        config.add_feature(model.ConfmlSequenceSetting('testfea11'))
        config.add_feature(model.ConfmlSetting('const',constraint=". &gt; '1'"))
        config.add_feature(model.ConfmlSetting('writeme',readOnly=False, constraint='foo bar'))
        elem = persistentconfml.dumps(config)
        config2 =  persistentconfml.loads(elem)
        self.assertEquals(config2.testfea11.constraint,None)
        self.assertEquals(config2.const.constraint,". &gt; '1'")
        self.assertEquals(config2.writeme.readOnly,False)
        self.assertEquals(config2.writeme.constraint,"foo bar")

    def test_configuration_with_features_and_required_attr(self):
        config = model.ConfmlConfiguration("test.confml")
        config.add_feature(model.ConfmlSequenceSetting('testfea11'))
        config.add_feature(model.ConfmlSetting('requ',required=True))
        config.add_feature(model.ConfmlSetting('writeme',required=False, readOnly=False))
        elem = persistentconfml.dumps(config)
        config2 =  persistentconfml.loads(elem)
        self.assertEquals(config2.testfea11.required,None)
        self.assertEquals(config2.requ.required,True)
        self.assertEquals(config2.writeme.readOnly,False)
        self.assertEquals(config2.writeme.required,False)

    def test_configuration_with_features_and_relevant_attr(self):
        config = model.ConfmlConfiguration("test.confml")
        config.add_feature(model.ConfmlSequenceSetting('testfea11'))
        config.add_feature(model.ConfmlSetting('requ',relevant='testfea11'))
        elem = persistentconfml.dumps(config)
        config2 =  persistentconfml.loads(elem)
        self.assertEquals(config2.testfea11.relevant,None)
        self.assertEquals(config2.requ.relevant,'testfea11')

    def test_configuration_with_features_and_maxlength(self):
        config = model.ConfmlConfiguration("test.confml")
        config.add_feature(model.ConfmlSetting('testfea1', type='int'))
        config.add_feature(model.ConfmlSetting('testfea2', type='int'))
        config.add_feature(model.ConfmlSetting('testfea3', type='int',maxLength=100))
        config.testfea1.maxLength = 10

        elem = persistentconfml.dumps(config)
        config2 =  persistentconfml.loads(elem)
        self.assertEquals(config2.testfea1.maxLength,10)
        self.assertEquals(config2.testfea2.maxLength,None)
        self.assertEquals(config2.testfea3.maxLength,100)

    def test_configuration_with_features_and_maxlength(self):
        config = model.ConfmlConfiguration("test.confml")
        config.add_feature(model.ConfmlSetting('testfea1', type='int'))
        config.add_feature(model.ConfmlSetting('testfea2', type='int'))
        config.add_feature(model.ConfmlSetting('testfea3', type='int',minLength=100))
        config.testfea1.minLength = 10

        elem = persistentconfml.dumps(config)
        config2 =  persistentconfml.loads(elem)
        self.assertEquals(config2.testfea1.minLength,'10')
        self.assertEquals(config2.testfea3.minLength,'100')
        self.assertEquals(config2.testfea2.minLength,None)

    def test_configuration_with_features(self):
        config = model.ConfmlConfiguration("test.confml")
        config.add_feature(api.Feature('testfea1'))
        config.testfea1.add_feature(model.ConfmlSetting('testfea11'))
        config.add_feature(api.Feature('testfea2'))
        set1 = model.ConfmlSetting('testfea21', type='selection')
        set1.create_option('pre', '1')
        set1.create_option('normal', '2')
        set1.create_option('post', '3')
        config.add_feature(set1, 'testfea2')
        config.add_feature(api.Feature('testfea4'))
        config.add_feature(api.Feature('testfea5'))
        config.add_feature(api.Feature('testfea6'))
        set1.set_value('pre')
        config.testfea1.set_value('foo:bar')
        config.testfea4.set_value('4')
        writer = persistentconfml.get_writer_for_class("Configuration")
        elem = writer.dumps(config)
        #print ElementTree.tostring(elem)
        etree = ElementTree.fromstring(ElementTree.tostring(elem))
        fea1 = etree.find('{http://www.s60.com/xml/confml/2}feature')
        self.assertEquals(fea1.get('ref'),'testfea1')
        self.assertEquals(fea1.find('{http://www.s60.com/xml/confml/2}setting').get('ref'),'testfea11')
        config2 =  persistentconfml.get_reader_for_elem('configuration').loads(etree)
        self.assertEquals(config2.testfea1.list_features(),['testfea11'])
        self.assertEquals(config2.testfea2.list_features(),['testfea21'])
        self.assertEquals(config2.testfea2.testfea21.get_type(),'selection')
        self.assertTrue('1' in config2.testfea2.testfea21.get_valueset())
        self.assertTrue('2' in config2.testfea2.testfea21.get_valueset())
        self.assertEquals(config2.testfea2.testfea21.options['3'].get_name(), 'post')
        self.assertEquals(config2.testfea2.testfea21.get_value(), 'pre')

    def test_write_configuration_with_multiselections(self):
        config = model.ConfmlConfiguration("test.confml")
        config.add_feature(api.Feature('testfea1'))
        config.testfea1.add_feature(model.ConfmlSetting('testfea11'))
        config.add_feature(api.Feature('testfea2'))
        set1 = model.ConfmlMultiSelectionSetting('testfea21')
        set1.create_option('pre', '1')
        set1.create_option('normal', '2')
        set1.create_option('post', '3')
        config.add_feature(set1, 'testfea2')
        config.add_feature(api.Feature('testfea4'))
        config.add_feature(api.Feature('testfea5'))
        config.add_feature(api.Feature('testfea6'))
        set1.value = ["pre","post"]       
        self.assertEquals(set1.get_data().get_value(), '"pre" "post"')
        writer = persistentconfml.get_writer_for_class("Configuration")
        elem = writer.dumps(config)
        self.assertEquals(ElementTree.tostring(elem), '<configuration name="test_confml" xmlns="http://www.s60.com/xml/confml/2" xmlns:xi="http://www.w3.org/2001/XInclude" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xs="http://www.w3.org/2001/XMLSchema"><feature name="testfea1" ref="testfea1"><setting name="testfea11" ref="testfea11" /></feature><feature name="testfea2" ref="testfea2"><setting name="testfea21" ref="testfea21" type="multiSelection"><option name="pre" value="1" /><option name="normal" value="2" /><option name="post" value="3" /></setting></feature><feature name="testfea4" ref="testfea4" /><feature name="testfea5" ref="testfea5" /><feature name="testfea6" ref="testfea6" /><data><testfea2><testfea21>"pre" "post"</testfea21></testfea2></data></configuration>')
        etree = ElementTree.fromstring(ElementTree.tostring(elem))
        fea1 = etree.find('{http://www.s60.com/xml/confml/2}feature')
        self.assertEquals(fea1.get('ref'),'testfea1')
        self.assertEquals(fea1.find('{http://www.s60.com/xml/confml/2}setting').get('ref'),'testfea11')
        config2 =  persistentconfml.get_reader_for_elem('configuration').loads(etree)
        self.assertEquals(config2.testfea2.list_features(),['testfea21'])
        self.assertEquals(config2.testfea2.testfea21.get_type(),'multiSelection')
        self.assertEquals(config2.testfea2.testfea21.get_value(), ['pre', 'post'])

    def test_configuration_with_view(self):
        config = api.Configuration("view.confml")
        config.add_view('testing')
        view = config.get_view('testing')
        view.add_group('group1')
        view.add_group('group2')
        view.add_group('group3')
        view.group1.add(api.FeatureLink('test.foo'))
        view.group2.add(api.FeatureLink('foo.*'))
        writer = persistentconfml.get_writer_for_class("Configuration")
        elem = writer.dumps(config)
        etree = ElementTree.fromstring(ElementTree.tostring(elem))
        view = etree.find('{http://www.s60.com/xml/confml/2}view')
        groups = etree.getiterator('{http://www.s60.com/xml/confml/2}group')
        listgroups = [elem for elem in groups]
        
        self.assertEquals(listgroups[0].get('name'), 'group1')
        self.assertEquals(listgroups[1].get('name'), 'group2')
        self.assertEquals(listgroups[2].get('name'), 'group3')
        settings = [elem for elem in etree.getiterator('{http://www.s60.com/xml/confml/2}setting')]
        self.assertEquals(settings[0].get('ref'), 'test/foo')
        self.assertEquals(settings[1].get('ref'), 'foo/*')

    def test_load_dump_reload_configuration_with_view(self):
        reader = persistentconfml.get_reader_for_elem("configuration")
        etree = ElementTree.fromstring(simpleview)
        obj = reader.loads(etree)
        # Getting the view populates it and check that the writing still works
        self.assertEquals(obj.get_view('Image creation').get_name(),'Image creation')
        self.assertEquals(obj.get_view('Image creation').id,'imakerimage')
        self.assertEquals(obj.get_view('Image creation').list_groups(), ['Imageproperties'])
        writer = persistentconfml.get_writer_for_class("Configuration")
        elem = writer.dumps(obj)
        # Reload the configuration with view after dumping it to ensure data stays the same
        elemstr = ElementTree.tostring(elem)      
        etree = ElementTree.fromstring(elemstr)
        obj = reader.loads(etree)
        self.assertEquals(obj.get_view('Image creation').get_name(),'Image creation')
        self.failUnlessEqual(obj.get_view('Image creation').id,'imakerimage', 'Known bug (#564)')
        self.assertEquals(obj.get_view('Image creation').id,'imakerimage')
        
    def test_load_configuration_and_create_copy_and_dump(self):
        conffile = open(os.path.join(ROOT_PATH,"data/commsdatcreator.confml"))
        #reader = persistentconfml.get_reader_for_elem("configuration")
        #etree = ElementTree.fromstring(conffile.read())
        obj = persistentconfml.loads(conffile.read())
        copyconfig = api.Configuration('data/copy_commsdatcreator.confml')
        
        for child in obj._objects():
            copyconfig._add(child)
        output = persistentconfml.dumps(copyconfig)
        ofile = open(os.path.join(ROOT_PATH,'data/copy_commsdatcreator.confml'),"wb")
        ofile.write(output)
        ofile.close()
        newconfig = persistentconfml.loads(output)
        orgview = obj.get_default_view()
        newview = newconfig.get_default_view()
        for fea in orgview.list_all_features():
            orgval = orgview.get_feature(fea).get_value() 
            newval = newview.get_feature(fea).get_value()
            if not orgval == newval:
                self.fail("Value of %s does not match. org = %s != new = %s" % (fea,orgval,newval))
        
    def test_create_configuration_with_meta_and_dump(self):
        prj = api.Project(api.Storage.open('dump','w'))
        testconf = prj.create_configuration('test.confml')
        testconf.include_configuration('test/foo.confml')
        testconf.save()
        prj.close()
        prj2 = api.Project(api.Storage.open('dump','a'))
        testconf = prj2.get_configuration('test.confml')
        testconf.meta = model.ConfmlMeta()
        testconf.meta.append(model.ConfmlMetaProperty('test', 'foo one two'))
        testconf.meta.append(model.ConfmlMetaProperty('owner', 'test erik'))
        testconf.save()
        prj2.close()
        prj = api.Project(api.Storage.open('dump','a'))
        testconf = prj.get_configuration('test.confml')
        self.assertEquals(testconf.meta[0].tag, 'test')
        self.assertEquals(testconf.meta[0].value,'foo one two')
        self.assertEquals(testconf.meta[1].tag, 'owner')
        self.assertEquals(testconf.meta[1].value,'test erik')
        del testconf.meta[1]
        del testconf.meta
        testconf.save()
        prj.close()
        prj = api.Project(api.Storage.open('dump','a'))
        testconf = prj.get_configuration('test.confml')
        self.assertEquals(testconf.meta, None)
        prj.close()
        shutil.rmtree('dump')

class TestMeta(unittest.TestCase):
    def test_get_reader_for_meta(self):
        reader = persistentconfml.get_reader_for_elem("meta")
        self.assertTrue(isinstance(reader, persistentconfml.MetaReader))

    def test_parse_meta_elem(self):
        reader = persistentconfml.get_reader_for_elem("meta")
        elem = ElementTree.Element('meta')
        owner = ElementTree.Element('owner')
        owner.text = 'Testing owner'
        origin = ElementTree.Element('origin')
        origin.text = 'just origin'
        target = ElementTree.Element('target')
        target.text = 'target hw'
        elem.append(owner)
        elem.append(origin)
        elem.append(target)
        data = reader.loads(elem)
        self.assertEquals(data[0].tag, 'owner')
        self.assertEquals(data[0].value, 'Testing owner')
        self.assertEquals(data[1].tag, 'origin')
        self.assertEquals(data[1].value, 'just origin')
        self.assertEquals(data[2].tag, 'target')
        self.assertEquals(data[2].value, 'target hw')

    def test_write_meta_elem(self):
        writer = persistentconfml.get_writer_for_class("ConfmlMeta")
        celem = model.ConfmlMeta([model.ConfmlMetaProperty('test', 123),\
                                 model.ConfmlMetaProperty('owner', "some ownername"),\
                                 model.ConfmlMetaProperty('target', "hw")])
        etree = writer.dumps(celem)
        self.assertEquals(etree.find('test').text,123)
        self.assertEquals(etree.find('owner').text,'some ownername')
        self.assertEquals(etree.find('target').text,'hw')
        
#    
class TestDesc(unittest.TestCase):
    def test_get_reader_for_desc(self):
        reader = persistentconfml.get_reader_for_elem("desc")
        self.assertTrue(isinstance(reader, persistentconfml.DescReader))

    def test_parse_desc_elem(self):
        reader = persistentconfml.get_reader_for_elem("meta")
        elem = ElementTree.Element('desc')
        elem.text = 'Testing desc'
        data = reader.loads(elem)

    def test_write_desc_elem(self):
        writer = persistentconfml.get_writer_for_class("ConfmlDescription")
        celem = model.ConfmlDescription('testing')
        etree = writer.dumps(celem)
        self.assertEquals(etree.text,'testing')

class TestFeature(unittest.TestCase):
    def test_get_reader_for_feature(self):
        reader = persistentconfml.get_reader_for_elem("feature")
        self.assertTrue(isinstance(reader, persistentconfml.FeatureReader))

    def test_parse_feature_elem(self):
        reader = persistentconfml.get_reader_for_elem("feature")
        elem = ElementTree.Element('feature', 
                                   {'ref' : 'hiifoo',
                                    'name': 'Some other name'})
        fea = reader.loads(elem)
        self.assertEquals(fea.get_ref(),'hiifoo')
        self.assertEquals(fea.get_name(),'Some other name')

    def test_write_feature_elem(self):
        writer = persistentconfml.get_writer_for_class("Feature")
        celem = api.Feature('testing')
        etree = writer.dumps(celem)
        self.assertEquals(etree.get('ref'),'testing')
        self.assertEquals(etree.get('name'),'testing')


class TestSetting(unittest.TestCase):
    def test_get_reader_for_feature(self):
        reader = persistentconfml.get_reader_for_elem("setting")
        self.assertTrue(isinstance(reader, persistentconfml.ConfmlSettingReader))

    def test_parse_elem(self):
        reader = persistentconfml.get_reader_for_elem("setting")
        elem = ElementTree.Element('setting', 
                                   {'ref' : 'hiifoo',
                                    'name': 'Some other name',
                                    'type' :'int',
                                    'readOnly': 'true'})
        fea = reader.loads(elem)
        self.assertEquals(fea.get_ref(),'hiifoo')
        self.assertEquals(fea.get_name(),'Some other name')
        self.assertEquals(fea.get_type(),'int')

    def test_write_setting_elem(self):
        writer = persistentconfml.get_writer_for_class("ConfmlSetting")
        celem = model.ConfmlSetting('testing')
        etree = writer.dumps(celem)
        self.assertEquals(etree.get('ref'),'testing')
        self.assertEquals(etree.get('name'),'testing')
        self.assertEquals(etree.get('type'),None)

    def test_write_setting_with_options(self):
        writer = persistentconfml.get_writer_for_class("ConfmlSetting")
        elem = model.ConfmlSetting('testing', type='selection')
        elem.create_option('one','1')
        elem.create_option('two','2')
        elem.create_option('three','3')
        elem.create_option('four','bar')
        etree = writer.dumps(elem)

        self.assertEquals(etree.get('ref'),'testing')
        self.assertEquals(etree.get('name'),'testing')
        self.assertEquals(etree.get('type'),'selection')
        self.assertEquals(etree.find('option').get('name'),'one')
        self.assertEquals(etree.find('option').get('value'),'1')

    def test_write_setting_with_facets(self):
        writer = persistentconfml.get_writer_for_class("ConfmlSetting")
        setting = model.ConfmlIntSetting(name="Int Setting", ref='intSetting')
        setting.minInclusive = 0
        setting.maxInclusive = 10
        setting.minExclusive = 0
        setting.maxExclusive = 10
        setting.totalDigits = 3
        setting.pattern = "\d*{3}"
        etree = writer.dumps(setting)
        
        self.assertEquals(etree.find('xs:minInclusive').get('value'),'0')
        self.assertEquals(etree.find('xs:maxInclusive').get('value'),'10')
        self.assertEquals(etree.find('xs:minExclusive').get('value'),'0')
        self.assertEquals(etree.find('xs:maxExclusive').get('value'),'10')
        self.assertEquals(etree.find('xs:totalDigits').get('value'),'3')
        self.assertEquals(etree.find('xs:pattern').get('value'),'\d*{3}')
        
        conffile = open(os.path.join(ROOT_PATH,"data/facets.confml"))
        obj = persistentconfml.loads(conffile.read())
        
        new_path = os.path.join(ROOT_PATH,"temp/facets_dumped.confml")
        dir = os.path.dirname(new_path)
        if dir and not os.path.exists(dir):
            os.makedirs(dir)
        f = open(new_path,"wb")
        try:        f.write(persistentconfml.dumps(obj))
        finally:    f.close()
        
    def test_read_setting_with_options(self):
        reader = persistentconfml.get_reader_for_elem("setting")
        elem = ElementTree.Element('setting', {'ref' : 'hii',
                                               'name': 'hoo hii',
                                               'type': 'selection'})
        elem.append(ElementTree.Element('option', {'name': 'test1', 'value': '123'}))
        elem.append(ElementTree.Element('option', {'name': 'test2', 'value': '456'}))
        elem.append(ElementTree.Element('option', {'name': 'test3', 'value': '789'}))
        setobj = reader.loads(elem)
        vset = setobj.get_valueset()
        self.assertTrue('123' in vset)
        self.assertTrue('456' in vset)
        self.assertTrue('789' in vset)
        self.assertEquals(setobj.options['123'].get_value(),'123')
        self.assertEquals(setobj.options['456'].get_value(),'456')
        self.assertEquals(setobj.options['789'].get_value(),'789')

    def test_read_sequence_setting(self):
        reader = persistentconfml.get_reader_for_elem("setting")
        elem = ElementTree.Element('setting', {'ref' : 'hii',
                                               'name': 'hoo hii',
                                               'type': 'sequence'})
        elem.append(ElementTree.Element('setting', {'ref' : 'intsetting',
                                               'name': 'intme',
                                               'type': 'int'}))
        elem.append(ElementTree.Element('setting', {'ref' : 'strsetting',
                                               'name': 'strme',
                                               'type': 'string'}))
        setobj = reader.loads(elem)
        self.assertEquals(setobj.list_features(), ['intsetting', 'strsetting'])
        self.assertEquals(setobj.intsetting.fqr, 'hii.intsetting')

    def test_read_sequence_setting_with_mapping(self):
        reader = persistentconfml.get_reader_for_elem("setting")
        elem = ElementTree.Element('setting', {'ref' : 'hii',
                                               'name': 'hoo hii',
                                               'type': 'sequence',
                                               'mapKey': 'intsetting',
                                               'mapValue': 'strsetting'})
        elem.append(ElementTree.Element('setting', {'ref' : 'intsetting',
                                               'name': 'intme',
                                               'type': 'int'}))
        elem.append(ElementTree.Element('setting', {'ref' : 'strsetting',
                                               'name': 'strme',
                                               'type': 'string'}))
        setobj = reader.loads(elem)
        self.assertEqual(setobj.get_map_key().name,"intme")
        self.assertEqual(setobj.get_map_value().name,"strme")

class TestSettingData(unittest.TestCase):
    def test_get_reader_for_data(self):
        reader = persistentconfml.get_reader_for_elem("data")
        self.assertTrue(isinstance(reader, persistentconfml.DataReader))

    def test_get_writer_for_data(self):
        writer = persistentconfml.get_writer_for_class("Data")
        self.assertTrue(isinstance(writer, persistentconfml.DataWriter))

    def test_dump_data(self):
        writer = persistentconfml.get_writer_for_class("Data")
        dobj = api.Data(ref='foo', value=1)
        elem = writer.dumps(dobj)
        self.assertEquals(elem.text, 1)

    def test_dump_data_with_subref(self):
        writer = persistentconfml.get_writer_for_class("DataContainer")
        base = api.DataContainer('foo')
        base._add(api.Data(fqr='foo.bar', value='test'))
        elem = writer.dumps(base)
        self.assertEquals(elem.find('bar').text, 'test')

    def test_dump_data_with_long_ref(self):
        writer = persistentconfml.get_writer_for_class("Data")
        base = api.Data(ref='foo')
        base._add(api.Data(ref='bar'))
        base._add_to_path('bar',api.Data(ref='test',  value='test'))
        elem = writer.dumps(base)
        self.assertEquals(elem.find('bar').find('test').text, 'test')

    def test_dump_data_with_hierarchy(self):
        writer = persistentconfml.get_writer_for_class("Data")
        base = api.DataContainer('foo')
        base._add(api.Data(fqr='foo.bar', value='test'))
        elem = writer.dumps(base)
        self.assertEquals(elem.find('bar').text, 'test')

    def test_read_data_with_map(self):
        reader = persistentconfml.get_reader_for_elem("data")
        data = ElementTree.Element('data')
        feature = ElementTree.Element('foo')
        data.append(feature)
        feature.append(ElementTree.Element('bar', {'map' : "foo/bar[@key='key 1']"}))
        
        obj = reader.loads(data)
        bar = obj._get('foo.bar')
        self.assertEqual(bar.get_map(),"foo/bar[@key='key 1']")

    def test_load_confml_with_meta(self):
        conffile = open(os.path.join(ROOT_PATH,"data/accessoryserver.confml"))
        reader = persistentconfml.get_reader_for_elem("configuration")
        etree = ElementTree.fromstring(conffile.read())
        obj = reader.loads(etree)
        self.assertEquals(obj.meta.get('type'), 'featurelist')

class TestReadWriteConfml(BaseTestCase):
    """
    Test case for ensuring that reading in a ConfML file and then writing
    it out again results in logically the same data (XML-wise) as the
    original data was.
    """
    
    def _normalize_xml_data(self, data):
        """
        Normalize XML data so that it can be compared using a binary
        comparison.
        """
        etree = ElementTree.fromstring(data)
        persistence.indent(etree)
        normalized_data = ElementTree.tostring(etree)
        return normalized_data
    
    def _run_read_and_write_test(self, file_name, input_dir, output_dir):
        file_path = os.path.join(input_dir, file_name)
        
        f = open(file_path, "rb")
        try:        original_data = f.read()
        finally:    f.close()
        
        original_data_normalized = self._normalize_xml_data(original_data)
        
        model = persistentconfml.loads(original_data)
        model_data = persistentconfml.dumps(model)
        
        model_data_normalized = self._normalize_xml_data(model_data)
        
        PATH_ORIGINAL = os.path.join(output_dir, 'original', file_name)
        PATH_DUMPED   = os.path.join(output_dir, 'dumped', file_name)
        
        if original_data_normalized != model_data_normalized:
            def write(file_path, data):
                file_dir = os.path.dirname(file_path)
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)
                f = open(file_path, "wb")
                try:        f.write(data)
                finally:    f.close()
            
            write(PATH_ORIGINAL, original_data_normalized)
            write(PATH_DUMPED, model_data_normalized)
            self.fail("Known bug (#506)")
            self.fail("Read-write output for file '%s' is different, see the files in '%s'" % (file_name, output_dir))
        else:
            # Test was successful, remove any old files that might have been there,
            # so that the output directories only contain files for the tests that
            # failed
            self.remove_if_exists(PATH_ORIGINAL)
            self.remove_if_exists(PATH_DUMPED)
    
    def _run_test_for_file(self, file_path):
        self._run_read_and_write_test(
            file_name  = os.path.basename(file_path),
            input_dir  = os.path.dirname(file_path),
            output_dir = os.path.normpath(os.path.join(ROOT_PATH, 'temp/read_write_results')))

# Create a separate test method for each ConfML file in the read-write test data
_READ_WRITE_TESTDATA_DIR = os.path.join(ROOT_PATH, 'testdata/read_write')
for filename in filter(lambda fn: fn.endswith('.confml'), os.listdir(_READ_WRITE_TESTDATA_DIR)):
    path = os.path.join(_READ_WRITE_TESTDATA_DIR, filename)
    test_method_name = 'test_read_write_file__%s' % filename.replace('.', '_')
    
    # Use a separate function to create and set the lambda function on the
    # test class, because otherwise 'path' would be the last one value set to
    # it in the for loop
    def _register_test_method(path):
        method = lambda self: self._run_test_for_file(path)
        method.__name__ = test_method_name
        setattr(TestReadWriteConfml, test_method_name, method)
    _register_test_method(path)


if __name__ == '__main__':
    unittest.main()
