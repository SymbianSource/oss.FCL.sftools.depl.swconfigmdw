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
import StringIO
import os

from cone.public import exceptions, persistence

class Metadata(object):
    """
    metadata container objectl, which is only a dictionary container
    """
    META_ROOT_FILE = 'cpf.rootFile'

    def __init__(self, copyobj=None):
        """
        Constructor initializes the default values
        """
        self.data = {}
        if copyobj != None:
            self.data = copyobj.data.copy()
        pass

    def get_root_file(self):
        return self.data.get(self.META_ROOT_FILE,"")

    def set_root_file(self,filename):
        self.data[self.META_ROOT_FILE] = filename

class MetadataReader(persistence.ConeReader):
    """
    Parses a single metadata file
    """ 
    class_type = "Metadata"
    NAMESPACES = ['http://www.nokia.com/xml/ns/confml-core/metadata-2.0']
    def __init__(self):
        return
    
    def fromstring(self, xml_as_string):
        meta = Metadata()
        etree = ElementTree.fromstring(xml_as_string)
        iter = etree.getiterator("{%s}property" % self.NAMESPACES[0])
        for elem in iter:
            (key,value) = self.get_property(elem)
            meta.data[key] = value
        return meta

    def get_property(self, elem):
        key = elem.get('name')
        value = ''
        if elem.get('value'): value = elem.get('value')
        return (key,value)

class MetadataWriter(persistence.ConeWriter):
    """
    Writes a single metadata file
    """ 
    class_type = "Metadata"
    NAMESPACES = ['http://www.nokia.com/xml/ns/confml-core/metadata-2.0']
    DEFAULT_ENCODING = "ASCII"
    def __init__(self):
        self.encoding = self.DEFAULT_ENCODING
        return
    
    def tostring(self,obj,indent=True):
        stringdata =  StringIO.StringIO()
        self.toresource(obj, stringdata, indent)
        return stringdata.getvalue()
    
    def toresource(self,obj,res,indent=True):
        root = ElementTree.Element("metadata")
        root.set('xmlns',self.NAMESPACES[0])
        if not obj.__class__ == Metadata:
            raise exceptions.IncorrectClassError('The given object is not a instance of %s' % Metadata)
        for key in obj.data.keys():
            prop = ElementTree.SubElement(root,'property')
            self.set_property(prop, key, obj.data[key])
        if indent:
            persistence.indent(root)
        # some smarter way to implement adding of the encoding to the beginning of file
        res.write('<?xml version="1.0" encoding="%s"?>%s' % (self.encoding,os.linesep))
        ElementTree.ElementTree(root).write(res)
        
    def set_property(self, elem, key, value):
        elem.attrib['name'] = key
        if value != '':
            elem.attrib['value'] = value
        return elem