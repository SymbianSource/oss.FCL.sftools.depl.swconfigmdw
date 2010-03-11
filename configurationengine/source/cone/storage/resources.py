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


import zipfile,os,re,zlib
from cone.public.api import Resource

class CpfRootResource(Resource):
    """
    Parses a single CPF configuration project root confml file. Parses the XInclude statements to 
    find out the layers inside the project
    """ 
    def __init__(self):
        self.configuration_namespace = "http://www.s60.com/xml/confml/1"
        self.include_namespace       = "http://www.w3.org/2001/xinclude"
        self.desc                    = ""
        self.includes                = []
        self.meta                    = {}
        self.filename                = "defaultroot.confml"
        return
    
    def parse_file(self, xmlfile):
        self.filename = xmlfile
        self.etree    = ElementTree.parse(xmlfile)
        self.parse_includes()
        self.parse_meta()
        self.parse_desc()
        return
    
    def parse_str(self, xml_as_string):
        self.etree = ElementTree.fromstring(xml_as_string)
        self.parse_includes()
        self.parse_meta()
        self.parse_desc()
        return

    def parse_includes(self):
        includes = self.etree.getiterator("{%s}include" % self.include_namespace)
        for inc in includes:
            self.includes.append(inc.get('href'))

    def parse_meta(self):
        meta = self.etree.find("{%s}meta" % self.configuration_namespace)
        if meta:
            for elem in meta.getiterator():
                m = re.match("{.*}(?P<tagname>.*)",elem.tag)
                if m:
                    self.meta[m.group('tagname')] = elem.text

    def parse_desc(self):
        desc_elem = self.etree.find("{%s}desc" % self.configuration_namespace)
        if desc_elem != None:
            self.desc = desc_elem.text
      
    def get_layers(self):
        return self.includes
    
    def get_meta(self):
        return self.meta
    
    def get_desc(self):
        return self.desc

    def get_configuration(self):
        configuration = CpfConfiguration(self.filename)
        for inc in self.includes:
            configuration.add_layer(CpfLayer(inc))
        return configuration
    
