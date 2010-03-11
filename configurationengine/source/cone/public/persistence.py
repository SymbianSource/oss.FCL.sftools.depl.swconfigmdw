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
from cone.public import api, exceptions


class PersistenceFactory(api.FactoryBase):
    @classmethod
    def get_reader_for_elem(cls,elemname):
        for reader in ConeReader.__subclasses__():
            if reader.supported_elem(elemname):
                return reader()
        raise exceptions.ConePersistenceError("No reader for given elemname %s found!" % elemname)

    @classmethod
    def get_writer_for_class(cls,classname):
        for writer in ConeWriter.__subclasses__():
            if writer.supported_class(classname):
                return writer ()
        raise exceptions.ConePersistenceError("No writer for given class found!")


class ConeHandler(object):
    ext        = ""
    class_type = ""


class ConeReader(ConeHandler):
    '''
    Read data from the string and return a ConeObject
    '''

    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConeReader supports reading 
        of the given element name
        """
        return False

    def loads(self,data):
        raise exceptions.NotSupportedException()

    def load(self,res):
        raise exceptions.NotSupportedException()
  
  
class ConeWriter(object):
    '''
    Write a ConeObject to a string
    '''
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this ConeWriter supports writing
        of the given class name
        """
        return False

    def dumps(self,ConeObject):
        raise exceptions.NotSupportedException()

    def dump(self,ConeObject,res,indent=True):
        raise exceptions.NotSupportedException()

def indent(elem, level=0):
    i = os.linesep + level*"  "
    if len(elem):
        try:
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            for e in elem:
                indent(e, level+1)
                if not e.tail or not e.tail.strip():
                    e.tail = i + "  "
                if not e.tail or not e.tail.strip():
                    e.tail = i
            else:
                if level and (not elem.tail or not elem.tail.strip()):
                    elem.tail = i
        except AttributeError,e:
            # explanation for this kind of try-except required
            pass