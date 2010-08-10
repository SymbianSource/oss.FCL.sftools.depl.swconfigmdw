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

from genconfmlplugin import genconfmlplugin
from cone.public import plugin,api
from cone.storage import filestorage


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


# Hardcoded value of testdata folder that must be under the current working dir
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
testdata  = os.path.join(ROOT_PATH,'project')

invalidxml_string = '<file xmlns="http://www.s60.com/xml/genconfml/1">'
genconfgml_string = \
'<file xmlns="http://www.s60.com/xml/genconfml/1" name="Setting/Data.xml" target="output">'\
'  <setting ref="Setting/Settings"/>'\
'  <setting ref="Setting/ContentSettings"/>'\
'  <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xi="http://www.w3.org/2001/xinclude">'\
'    <xsl:output method="xml" indent="yes" encoding="UTF-8"/>'\
'    <xsl:template match="configuration/data">'\
'      <Variant>'\
'        <xsl:copy-of select="Setting/Settings"/>'\
'        <xsl:copy-of select="Setting/ContentSettings"/>'\
'      </Variant>'\
'    </xsl:template>'\
'  </xsl:stylesheet>'\
'</file>'



class TestGenconfmlPlugin(unittest.TestCase):
    def setUp(self):
        self.curdir = os.getcwd()
        self.output = os.path.join(ROOT_PATH, 'temp/output')

    def test_example_parse_and_generate_prj2(self):
        fs = filestorage.FileStorage(testdata)
        p = api.Project(fs)
        config = p.get_configuration('root1.confml')
        impls = plugin.get_impl_set(config,'\.gcfml$')
        impls.output = self.output
        impl = impls.get_implementations_by_file('Layer1/implml/feature1.gcfml')[0]
        impls.generate()

    def test_predefined_contacts_parse_and_generate(self):
        fs = filestorage.FileStorage(testdata)
        p = api.Project(fs)
        config = p.get_configuration('product.confml')
        impls = plugin.get_impl_set(config,'\.gcfml$')
        impls.output = self.output
        impl = impls.get_implementations_by_file('assets/s60/implml/predefinedcontacts.gcfml')[0]
        impls.generate()

    def test_write_element_fo_file(self):
        '''
        Fix this
        '''
        OUTFILE = os.path.join(ROOT_PATH, 'temp/elementfile.xml')
        if not os.path.exists(os.path.join(ROOT_PATH, 'temp')):
            os.makedirs(os.path.join(ROOT_PATH, 'temp'))
        #fs = filestorage.FileStorage(testdata)
        #p = api.Project(fs)
        #config = p.get_configuration('product.confml')
        #genconfml_plugin = genconfmlplugin.GenconfmlImpl(None, config)
        element = ElementTree.fromstring('<test>kfkadl</test>')
        
        genconfmlplugin.write_element(element, OUTFILE)
        self.assertTrue(os.path.exists(OUTFILE))
        #out_file = open(output, 'r')
        #out_file.write(xml.etree.ElementTree.tostring(element))
        #out_file.close()
        
        
        #resource = self.configuration.get_resource("elementfile.xml")
        
        
    def test_parse_target(self):
        etree = ElementTree.fromstring(genconfgml_string)
        reader = genconfmlplugin.GenconfmlImplReader()
        target = reader.parse_target(etree)
        self.assertEquals(target,'output')

    def test_parse_stylesheet(self):
        etree = ElementTree.fromstring(genconfgml_string)
        reader = genconfmlplugin.GenconfmlImplReader()
        stylesheet = reader.parse_stylesheet(etree)
        #print stylesheet
        #FIX THIS
        #self.assertEquals(stylesheet, etree.find("{%s}stylesheet" % 'http://www.w3.org/1999/XSL/Transform'))

    def test_parse_name(self):
        etree = ElementTree.fromstring(genconfgml_string)
        reader = genconfmlplugin.GenconfmlImplReader()
        name = reader.parse_name(etree)
        self.assertEquals(name,'Setting/Data.xml')

    def test_parse_subdir_without_definition(self):
        etree = ElementTree.fromstring(genconfgml_string)
        reader = genconfmlplugin.GenconfmlImplReader()
        subdir = reader.parse_subdir(etree)
        self.assertEquals(subdir, "")

    def test_parse_subdir_with_definition(self):
        etree = ElementTree.fromstring(genconfgml_string.replace("target=\"output\"", "subdir=\"include\""))
        reader = genconfmlplugin.GenconfmlImplReader()
        subdir = reader.parse_subdir(etree)
        self.assertEquals(subdir, "include")

    def test_parse_settings(self):
        etree = ElementTree.fromstring(genconfgml_string)
        reader = genconfmlplugin.GenconfmlImplReader()
        settings = reader.parse_settings(etree)
        self.assertEquals(settings[0],'Setting/Settings')
        self.assertEquals(settings[1],'Setting/ContentSettings')
        
    def test_has_ref(self):
        fs = filestorage.FileStorage(testdata)
        p = api.Project(fs)
        config = p.get_configuration('product.confml')
        impls = plugin.get_impl_set(config,'\.gcfml$')
        impls.output = self.output
        impl = impls.get_implementations_by_file('assets/s60/implml/predefinedcontacts.gcfml')[0]
        self.assertEquals(impl.get_refs(), ['Contacts.Contact'])
        self.assertFalse(impl.has_ref(['ref1', 'ref2']))
        self.assertTrue(impl.has_ref(['Contacts.Contact']))
        self.assertTrue(impl.has_ref(['Contacts.Contact.FirstName']))
        self.assertFalse(impl.has_ref(['Contacts.OtherSetting']))
        
    def test_get_refs(self):
        fs = filestorage.FileStorage(testdata)
        p = api.Project(fs)
        config = p.get_configuration('product.confml')
        impls = plugin.get_impl_set(config,'\.gcfml$')
        impls.output = self.output
        impl = impls.get_implementations_by_file('assets/s60/implml/commsdatcreator_01.gcfml')[0]
        self.assertEquals(impl.get_refs(), ['APs.AP', 'WLAN_APs.WLAN_AP'])
        self.assertTrue(impl.has_ref(['APs.AP']))
        
    def test_list_output_files(self):
        fs = filestorage.FileStorage(testdata)
        p = api.Project(fs)
        config = p.get_configuration('product.confml')
        impls = plugin.get_impl_set(config,'\.gcfml$')
        impls.output = self.output
        impl = impls.get_implementations_by_file('assets/s60/implml/predefinedcontacts.gcfml')[0]
        
        normalize_slash = lambda l: map(lambda p: p.replace('\\', '/'), l)
        self.assertEquals(normalize_slash(impl.list_output_files()),
                          ['private/2000BEE5/predefinedcontacts.xml'])

    
if __name__ == '__main__':
    unittest.main()
