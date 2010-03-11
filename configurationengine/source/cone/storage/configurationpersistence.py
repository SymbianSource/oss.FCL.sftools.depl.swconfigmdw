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

from cone.public import persistence
 
# list of namespaces supported. the first one in the list is always used in writing
CONFIGURATION_NAMESPACES = ["http://www.s60.com/xml/confml/1"]
INCLUDE_NAMESPACES       = ["http://www.w3.org/2001/xinclude","http://www.w3.org/2001/XInclude"]

class ConfigurationReader(persistence.ConeReader):
    """
    Parses a single CPF configuration project root confml file. Parses the XInclude statements to 
    find out the layers inside the project
    """ 

    class_type = "Configuration"

    def __init__(self):
        self.configuration_namespaces = CONFIGURATION_NAMESPACES
        self.include_namespaces       = INCLUDE_NAMESPACES
            
    def fromstring(self, xml_as_string):
        configuration = api.CompositeConfiguration(None)
        etree = ElementTree.fromstring(xml_as_string)
        configuration.desc = self.parse_desc(etree)
        configuration.meta = self.parse_meta(etree)
        configuration.set_name(self.parse_name(etree))
        for inc in self.parse_includes(etree):
            configuration.add_layer(inc)
    
        return configuration

    def parse_includes(self,etree):
        include_elems = []
        include_elems.extend(etree.getiterator("{%s}include" % self.include_namespaces[0]))
        include_elems.extend(etree.getiterator("{%s}include" % self.include_namespaces[1]))
        includes = []
        for inc in include_elems:
            includes.append(inc.get('href').replace('#/',''))
        return includes
    
    def parse_meta(self,etree):
        meta_elem = etree.find("{%s}meta" % self.configuration_namespaces[0])
        meta = {}
        if meta_elem:      
            # There must be a nicer way to do this!! :(
            for elem in meta_elem.getiterator():
                m = re.match("{.*}(?P<tagname>.*)",elem.tag)
                if m and m.group('tagname') != 'meta':
                    meta[m.group('tagname')] = elem.text 
        return meta
     
    def parse_desc(self,etree):
        desc = ""
        desc_elem = etree.find("{%s}desc" % self.configuration_namespaces[0])
        if desc_elem != None:
            desc = desc_elem.text
        return desc
    
    def parse_name(self,etree):
        return etree.get("name")


class ConfigurationWriter(persistence.ConeWriter):
    """
    Parses a single CPF configuration project root confml file. Parses the XInclude statements to 
    find out the layers inside the project
    """ 

    class_type = "Configuration"

    def __init__(self):
        self.configuration_namespace = CONFIGURATION_NAMESPACES[0]
        self.include_namespace       = INCLUDE_NAMESPACES[0]
    
    def tostring(self,configuration,indent=True):
        root = ElementTree.Element("configuration")
        root.set("xmlns",self.configuration_namespace)
        root.set("xmlns:xi",self.include_namespace)
        root.set("name",configuration.ref) 
        root.append(self.to_desc(configuration.desc))
        root.append(self.to_meta(configuration.meta))
        for inc in configuration.list_layers():
            root.append(self.to_include(inc))
        if indent:
            self.indent(root)
        return ElementTree.tostring(root)
 
    def to_desc(self,desc):
        elem = ElementTree.Element("desc")
        elem.text = desc
        return elem 
      
    def to_meta(self,meta):
        elem = ElementTree.Element("meta")
        for key in meta.keys():
            selem = ElementTree.SubElement(elem,key)
            selem.text = meta[key]
        return elem 
    
    def to_include(self,include):
        elem = ElementTree.Element("xi:include")
        elem.set("href",include)
        return elem 
    
