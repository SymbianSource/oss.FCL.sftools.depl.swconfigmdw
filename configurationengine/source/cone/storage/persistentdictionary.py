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

from cone.public import persistence, exceptions, api, utils

def dumps(obj):
    return DictWriter().dumps(obj)

def loads(dictstr):
    # convert the dict string with eval to actual dict
    return DictReader().loads(eval(dictstr))

class DictWriter(persistence.ConeWriter):
    """
    """ 

    def dumps(self, obj):
        """
        @param obj: The object 
        """
        writer = get_writer_for_class(obj.__class__.__name__)
        return {obj.__class__.__name__: writer.dumps(obj)}


class DictReader(persistence.ConeReader):
    """
    """ 
    class_type = "Dict"

    def loads(self, dict):
        """
        @param dict: The dictianary which to read. reads only the first object. 
        """
        classname = dict.keys()[0]
        reader = get_reader_for_elem(classname)
        return reader.loads(dict)


class GenericWriter(DictWriter):
    """
    """ 

    def dumps(self, obj):
        """
        @param obj: The Configuration object 
        """
        dict = {'dict': todict(obj)}
        for child in obj._objects():
            writer = get_writer_for_class(child.__class__.__name__)
            chd = writer.dumps(child)
            if not dict.has_key('children'):
                 dict['children'] = []
            dict['children'].append({child.__class__.__name__: chd})
        return dict

    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this DictWriter supports writing
        of the given class name
        """
        try:
            cls = get_class(classname)
            return True
        except exceptions.IncorrectClassError:
            return False


class GenericReader(DictReader):
    """
    """ 
    
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this DictWriter supports reading
        of the given elem name
        """
        try:
            cls = get_class(elemname)
            return True
        except exceptions.IncorrectClassError:
            return False

    def __init__(self):
        pass

    def loads(self, dict):
        """
        @param obj: The Configuration object 
        """
        
        (classname,objdata) = dict.popitem()
        obj = get_class(classname)()
        objdict = objdata.get('dict',{})
        for membername in objdict.keys():
            try:
                setattr(obj, membername, objdict[membername])
            except AttributeError:
                # read only attributes cannot be set
                pass
        obj._name = utils.resourceref.to_objref(obj.ref)

        #container.ObjectContainer.__init__(obj,utils.resourceref.to_dottedref(obj.ref))
        for child in objdata.get('children',[]):
            classname = child.keys()[0]
            reader = get_reader_for_elem(classname)
            childobj = reader.loads(child)
            obj.add(childobj)
        return obj


class ConfigurationProxyWriter(DictWriter):
    """
    """ 
    def dumps(self, obj):
        """
        @param obj: The Configuration object 
        """
        dict = {'dict': todict(obj)}
        return dict

    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this DictWriter supports writing
        of the given class name
        """
        if classname=="ConfigurationProxy":
            return True
        else:
            return False


class ConfigurationProxyReader(DictReader):
    """
    """ 
    def loads(self, dict):
        """
        @param obj: The Configuration object 
        """
        (classname,objdata) = dict.popitem()
        obj = api.ConfigurationProxy("")
        obj.__dict__.update(objdata.get('dict',{}))
        obj.set('_name',utils.resourceref.to_objref(obj.path))
        return obj
        
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this DictWriter supports reading
        of the given elem name
        """
        if elemname=="ConfigurationProxy":
            return True
        else:
            return False


def get_class(elemname):
    """
    Get a correct class from a element name.
    """
    if elemname=="Configuration":
        return api.Configuration
    elif elemname=="CompositeConfiguration":
        return api.CompositeConfiguration
    elif elemname=="Feature":
        return api.Feature
    elif elemname=="Data":
        return api.Data
    elif elemname=="DataContainer":
        return api.DataContainer
    elif elemname=="Base":
        return api.Base
    else:
        raise exceptions.IncorrectClassError("Could not find a class for name %s!" % elemname)

def get_reader_for_elem(classname):
    for reader in DictReader.__subclasses__():
        if reader.supported_elem(classname):
            return reader()
    raise exceptions.ConePersistenceError("No reader for given class found!")

def get_writer_for_class(classname):
    for writer in DictWriter.__subclasses__():
        if writer.supported_class(classname):
            return writer ()
    raise exceptions.ConePersistenceError("No writer for given class found! %s" % classname)

def todict(obj):
    """
    Helper function to push all non internal data to a dictionary
    """
    dict = {}
    fromdict = obj._dict()
    for member in fromdict:
        if member.startswith("_"):
            # skip internals
            continue
        value = getattr(obj,member)
        if isinstance(value,str):
            dict[member] = value
            continue
        if isinstance(value,int):
            dict[member] = value
            continue
    return dict

