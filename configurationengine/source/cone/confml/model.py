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
Base class for Confml elements.
Attributes:
 All Confml element attributes become attributes of this instance.
"""
import types
from cone.public import api, exceptions, container, utils

class ConfmlElement(api.Base):
    def _get_mapper(self,modelname):
        """
        Return a instance of appropriate mapper for given model.
        """
        mapmodule = __import__('cone.confml.mapping')
        return mapmodule.confml.mapping.MAPPERS[modelname]()

    def get_desc(self): 
        try:
            desc = getattr(self,ConfmlDescription.refname)
            return desc.text
        except AttributeError:
            return None

    def set_desc(self,value): 
        self._add(ConfmlDescription(value))

    def del_desc(self): 
        try:
            self._remove(ConfmlDescription.refname)
        except exceptions.NotFound:
            pass
    """ The description as a property """
    desc = property(get_desc,set_desc,del_desc)
class ConfmlConfiguration(ConfmlElement, api.Configuration):
    """
    Confml configuration class. 
    """
    def __init__(self,ref="", **kwargs):
        super(ConfmlConfiguration,self).__init__(ref, **kwargs)
        if kwargs.get('meta'):
            self.meta = kwargs.get('meta')
        if kwargs.get('desc'):
            self.desc = kwargs.get('desc')


    def get_desc(self): 
        """
        @return: The description of the Configuration.
        """
        try:
            desc = getattr(self,ConfmlDescription.refname)
            return desc.text
        except AttributeError:
            return None

    def set_desc(self,value): 
        self._add(ConfmlDescription(value))

    def del_desc(self): 
        try:
            self._remove(ConfmlDescription.refname)
        except exceptions.NotFound:
            pass

    """ The description as a property """
    desc = property(get_desc,set_desc,del_desc)

    def get_meta(self): 
        """
        @return: The description of the Configuration.
        """
        try:
            meta = getattr(self,ConfmlMeta.refname)
            return meta
        except AttributeError:
            return None

    def set_meta(self,value): 
        self._add(ConfmlMeta(value))

    def del_meta(self): 
        try:
            self._remove(ConfmlMeta.refname)
        except exceptions.NotFound:
            pass

    """ The meta element as a property """
    meta = property(get_meta,set_meta,del_meta)


class ConfmlGroup(ConfmlElement, api.Group):
    """
    Confml view.
    """
    def __init__(self, ref="", **kwargs):
        super(ConfmlGroup,self).__init__(ref,**kwargs)
        if kwargs.get('icon'):
            self.icon = kwargs.get('icon')
        if kwargs.get('desc'):
            self.desc = kwargs.get('desc')

    def get_icon(self): 
        try:
            icon = getattr(self,ConfmlIcon.refname)
            return icon.href
        except AttributeError:
            return None
    def set_icon(self,value): self._add(ConfmlIcon(value))
    def del_icon(self): 
        try:
            self._remove(ConfmlIcon.refname)
        except exceptions.NotFound:
            pass
    """ The icon as a property """
    icon = property(get_icon,set_icon,del_icon)

    def get_desc(self): 
        try:
            desc = getattr(self,ConfmlDescription.refname)
            return desc.text
        except AttributeError:
            return None
    def set_desc(self,value): self._add(ConfmlDescription(value))
    def del_desc(self): 
        try:
            self._remove(ConfmlDescription.refname)
        except exceptions.NotFound:
            pass
    """ The description as a property """
    desc = property(get_desc,set_desc,del_desc)


class ConfmlView(api.View):
    """
    Confml view.
    """
    def __init__(self, ref="", **kwargs):
        super(ConfmlView,self).__init__(ref,**kwargs)
        if kwargs.get('desc'):
            self.desc = kwargs.get('desc')


    def get_desc(self): 
        try:
            desc = getattr(self,ConfmlDescription.refname)
            return desc.text
        except AttributeError:
            return None
    def set_desc(self,value): self._add(ConfmlDescription(value))
    def del_desc(self): 
        try:
            self._remove(ConfmlDescription.refname)
        except exceptions.NotFound:
            pass
    """ The description as a property """
    desc = property(get_desc,set_desc,del_desc)

class ConfmlFeature(ConfmlElement, api.Feature):
    pass

class ConfmlSetting(ConfmlElement, api.Feature):
    """
    Confml setting class. Attribute 'options' contains options of this setting.
    """
    supported_types = ['int',
                       'string',
                       'boolean',
                       'selection']
    def __init__(self, ref,**kwargs):
        super(ConfmlSetting,self).__init__(ref,**kwargs)
        self.type = kwargs.get('type',None)
        if kwargs.get('desc'):
            self.desc = kwargs.get('desc')
        if kwargs.get('minOccurs'):
            self.minOccurs = kwargs.get('minOccurs')
        if kwargs.get('maxOccurs'):
            self.maxOccurs = kwargs.get('maxOccurs')
        if kwargs.get('maxLength'):
            self.maxLength = kwargs.get('maxLength')
        if kwargs.get('minLength'):
            self.minLength = kwargs.get('minLength')
        if kwargs.get('mapKey'):
            self.mapKey = kwargs.get('mapKey')
        if kwargs.get('mapValue'):
            self.mapValue = kwargs.get('mapValue')
        
        self.readOnly = kwargs.get('readOnly',None)
        self.constraint = kwargs.get('constraint',None)
        self.required = kwargs.get('required',None)
        self.relevant = kwargs.get('relevant',None)

    def get_valueset(self):
        """
        Get the ValueSet object for this feature, that has the list of available values.
        """
        return api.ValueRe('.*')

    def add_property(self, **kwargs):
        """
        @param name=str: property name 
        @param value=str: property value
        @param unit=str: property unit, e.g. kB
        """
        self._add(ConfmlProperty(**kwargs), container.APPEND)

    def get_property(self, name):
        """
        @param name: The name of the property
        """
        for property in utils.get_list(self._get(ConfmlProperty.refname)):
            if property.name == name:
                return property
        raise exceptions.NotFound("ConfmlProperty with name %s not found!" % name)

    def remove_property(self, name):
        """
        remove a given option from this feature by name. 
        @param name: 
        """
        for property in self._get(ConfmlProperty.refname):
            if property.name == name:
                return self._remove(property.get_fullref())
        raise exceptions.NotFound("ConfmlProperty with name %s not found!" % name)

    def list_properties(self):
        """
        Return a array of all Feature children references under this object.
        """
        return [obj.name for obj in utils.get_list(self._get(ConfmlProperty.refname))]

    def get_maxlength(self): 
        try:
            return getattr(self,ConfmlMaxLength.refname).value
        except AttributeError:
            return None

    def set_maxlength(self,value): 
        self._add(ConfmlMaxLength(value))

    def del_maxlength(self): 
        try:
            self._remove(ConfmlMaxLength.refname)
        except exceptions.NotFound:
            pass
    """ The description as a property """
    maxLength = property(get_maxlength,set_maxlength,del_maxlength)

    def get_minlength(self): 
        try:
            return getattr(self,ConfmlMinLength.refname).value
        except AttributeError:
            return None

    def set_minlength(self,value): 
        self._add(ConfmlMinLength(value))

    def del_minlength(self): 
        try:
            self._remove(ConfmlMinLength.refname)
        except exceptions.NotFound:
            pass
    """ The description as a property """
    minLength = property(get_minlength,set_minlength,del_minlength)

    def get_minInclusive(self): 
        try:
            return getattr(self,ConfmlMinInclusive.refname).value
        except AttributeError:
            return None

    def set_minInclusive(self,value): 
        self._add(ConfmlMinInclusive(value))

    def del_minInclusive(self): 
        try:
            self._remove(ConfmlMinInclusive.refname)
        except exceptions.NotFound:
            pass     
    """ The minInclusive as a property """
    minInclusive = property(get_minInclusive,set_minInclusive,del_minInclusive)

    def get_maxInclusive(self): 
        try:
            return getattr(self,ConfmlMaxInclusive.refname).value
        except AttributeError:
            return None

    def set_maxInclusive(self,value): 
        self._add(ConfmlMaxInclusive(value))

    def del_maxInclusive(self): 
        try:
            self._remove(ConfmlMaxInclusive.refname)
        except exceptions.NotFound:
            pass     
    """ The minInclusive as a property """
    maxInclusive = property(get_maxInclusive,set_maxInclusive,del_maxInclusive)

    def get_minExclusive(self): 
        try:
            return getattr(self,ConfmlMinExclusive.refname).value
        except AttributeError:
            return None

    def set_minExclusive(self,value): 
        self._add(ConfmlMinExclusive(value))

    def del_minExclusive(self): 
        try:
            self._remove(ConfmlMinExclusive.refname)
        except exceptions.NotFound:
            pass     
    """ The minExclusive as a property """
    minExclusive = property(get_minExclusive,set_minExclusive,del_minExclusive)

    def get_maxExclusive(self): 
        try:
            return getattr(self,ConfmlMaxExclusive.refname).value
        except AttributeError:
            return None

    def set_maxExclusive(self,value): 
        self._add(ConfmlMaxExclusive(value))

    def del_maxExclusive(self): 
        try:
            self._remove(ConfmlMaxExclusive.refname)
        except exceptions.NotFound:
            pass     
    """ The maxExclusive as a property """
    maxExclusive = property(get_maxExclusive,set_maxExclusive,del_maxExclusive)

    def get_pattern(self): 
        try:
            return getattr(self,ConfmlPattern.refname).value
        except AttributeError:
            return None

    def set_pattern(self,value): 
        self._add(ConfmlPattern(value))

    def del_pattern(self): 
        try:
            self._remove(ConfmlPattern.refname)
        except exceptions.NotFound:
            pass     
    """ The pattern as a property """
    pattern = property(get_pattern,set_pattern,del_pattern)

    def get_totalDigits(self): 
        try:
            return getattr(self,ConfmlTotalDigits.refname).value
        except AttributeError:
            return None

    def set_totalDigits(self,value): 
        self._add(ConfmlTotalDigits(value))

    def del_totalDigits(self): 
        try:
            self._remove(ConfmlTotalDigits.refname)
        except exceptions.NotFound:
            pass     
    """ The totalDigits as a property """
    totalDigits = property(get_totalDigits,set_totalDigits,del_totalDigits)

    @property
    def options(self):
        optdict = {}
        for opt in self._objects(type=api.Option):
            optdict[opt.value] = opt
        return  optdict

    @property
    def properties(self):
        dict = {}
        for property in utils.get_list(self._get(ConfmlProperty.refname)):
            dict[property.name] = property
        return  dict

    def get_rfs(self,):
        return super(ConfmlSetting,self).get_value('rfs')

    def set_rfs(self, value):
        super(ConfmlSetting,self).set_value('rfs',value)

    def del_rfs(self):
        super(ConfmlSetting,self).del_value('rfs')

    rfs = property(get_rfs,set_rfs,del_rfs)

    def get_value_cast(self, value, attr=None):
        """
        A function to perform the value type casting in get operation  
        @param value: the value to cast 
        @param attr: the attribute which is fetched from model (normally in confml either None='data' or 'rfs')
        """
        if not attr or attr == 'data':
            return self.get_data_cast(value)
        elif attr == 'rfs':
            return self.get_rfs_cast(value)
        else:
            return value
    
    def set_value_cast(self, value, attr=None):
        """
        A function to perform the value type casting in the set operation  
        @param value: the value to cast 
        @param attr: the attribute which is fetched from model (normally in confml either None='data' or 'rfs')
        """
        if not attr or attr == 'data':
            return self.set_data_cast(value)
        elif attr == 'rfs':
            return self.set_rfs_cast(value)
        else:
            return value

    def get_data_cast(self, value):
        """
        A function to perform the data type casting in get operation  
        @param value: the value to cast 
        """
        return value
    
    def set_data_cast(self, value):
        """
        A function to perform the data type casting in the set operation  
        @param value: the value to cast 
        """
        return value

    def get_rfs_cast(self, value):
        """
        A function to perform the rfs type casting in get operation  
        @param value: the value to cast 
        """
        if value == 'true':
            return True
        elif value == 'false':
            return False
        else: # otherwise this is an invalid rfs value. Should it report an error?
            return value
    
    def set_rfs_cast(self, value):
        """
        A function to perform the rfs type casting in the set operation  
        @param value: the value to cast 
        """
        if value:
            return 'true'
        else: 
            return 'false'


class ConfmlStringSetting(ConfmlSetting):
    """
    Confml setting class for integer type.
    """
    def __init__(self, ref,**kwargs):
        kwargs['type'] = 'string'
        ConfmlSetting.__init__(self,ref,**kwargs)


class ConfmlIntSetting(ConfmlSetting):
    """
    Confml setting class for integer type.
    """
    def __init__(self, ref,**kwargs):
        kwargs['type'] = 'int'
        ConfmlSetting.__init__(self,ref,**kwargs)

    def get_valueset(self):
        """
        Get the ValueSet object for this feature, that has the list of available values.
        """
        return api.ValueRange(0,sys.maxint)

    def get_data_cast(self, value):
        """
        A function to perform the value type casting in get operation  
        """
        if value:
            try:
                return int(value)
            except ValueError:
                return int(value, 16)
        else:
            return value
    
    def set_data_cast(self, value):
        """
        A function to perform the value type casting in the set operation  
        """
        return str(int(value))


class ConfmlRealSetting(ConfmlSetting):
    """
    Confml setting class for real type.
    """
    def __init__(self, ref,**kwargs):
        kwargs['type'] = 'real'
        ConfmlSetting.__init__(self,ref,**kwargs)

    def get_valueset(self):
        """
        Get the ValueSet object for this feature, that has the list of available values.
        """
        return api.ValueRange(0,float(sys.maxint))

    def get_data_cast(self, value):
        """
        A function to perform the value type casting in get operation  
        """
        if value:
            return float(value)
        else:
            return value
    
    def set_data_cast(self, value):
        """
        A function to perform the value type casting in the set operation  
        """
        return str(float(value))




class ConfmlBooleanSetting(ConfmlSetting):
    """
    Confml setting class for boolean type.
    """
    def __init__(self, ref,**kwargs):
        kwargs['type'] = 'boolean'
        ConfmlSetting.__init__(self,ref,**kwargs)

    def get_valueset(self):
        """
        Get the ValueSet object for this feature, that has the list of available values.
        """
        return api.ValueSet([True,False])

    def get_data_cast(self, value):
        """
        A function to perform the value type casting in get operation  
        """
        if value:
            if value in ('true', '1'):
                return True
            else:
                return False
        else:
            return value
    
    def set_data_cast(self, value):
        """
        A function to perform the value type casting in the set operation  
        """
        if isinstance(value, basestring):
            if value in ('false', '0'):
                return 'false'
            elif value in ('true', '1'):
                return 'true'
        
        return str(bool(value)).lower()


class ConfmlSelectionSetting(ConfmlSetting):
    """
    Confml setting class for boolean type.
    """
    def __init__(self, ref,**kwargs):
        kwargs['type'] = 'selection'
        ConfmlSetting.__init__(self,ref,**kwargs)
    
    def get_valueset(self):
        """
        Get the ValueSet object for this feature, that has the list of available values.
        """
        return api.Feature.get_valueset(self)

class ConfmlMultiSelectionSetting(ConfmlSetting):
    """
    Confml setting class for multiSelection type.
    """

    def __init__(self, ref,**kwargs):
        kwargs['type'] = 'multiSelection'
        ConfmlSetting.__init__(self,ref,**kwargs)
        

    def get_valueset(self):
        """
        Get the ValueSet object for this feature, that has the list of available values.
        """
        return api.Feature.get_valueset(self)

    def get_data_cast(self, value):
        """
        A function to perform the value type casting in get operation  
        """
        try:
            if not isinstance(value, types.ListType):
                values = value.split('" "')
                for i in range(len(values)):
                    if values[i].startswith('"'):
                        values[i] = values[i][1:] 
                    if values[i].endswith('"'):
                        values[i] = values[i][:-1]
                return values
            return value
        except AttributeError:
            return None
    
    def set_data_cast(self, value):
        """
        A function to perform the value type casting in the set operation  
        """
        
        if isinstance(value, list):
            value = " ".join(['"%s"' % elem for elem in value])
        return value
    
    def set_value(self, value):
        if not isinstance(value, types.ListType):
            raise ValueError("Only list types are allowed.")
        self.value = value

class ConfmlDateSetting(ConfmlSetting):
    """
    Confml setting class for date type.
    """
    def __init__(self, ref,**kwargs):
        kwargs['type'] = 'date'
        ConfmlSetting.__init__(self,ref,**kwargs)

class ConfmlTimeSetting(ConfmlSetting):
    """
    Confml setting class for time type.
    """
    def __init__(self, ref,**kwargs):
        kwargs['type'] = 'time'
        ConfmlSetting.__init__(self,ref,**kwargs)

class ConfmlDateTimeSetting(ConfmlSetting):
    """
    Confml setting class for date-time type.
    """
    def __init__(self, ref,**kwargs):
        kwargs['type'] = 'dateTime'
        ConfmlSetting.__init__(self,ref,**kwargs)

class ConfmlDurationSetting(ConfmlSetting):
    """
    Confml setting class for date type.
    """
    def __init__(self, ref,**kwargs):
        kwargs['type'] = 'duration'
        ConfmlSetting.__init__(self,ref,**kwargs)

class ConfmlSequenceSetting(api.FeatureSequence,ConfmlSetting):
    """
    Confml setting class. Attribute 'options' contains options of this setting.
    """
    def __init__(self, ref,**kwargs):
        ConfmlSetting.__init__(self,ref,**kwargs)
        api.FeatureSequence.__init__(self,ref,**kwargs)

class ConfmlFileSetting(ConfmlSetting):
    """
    Confml file setting class.
    """
    def __init__(self, ref,**kwargs):
        kwargs['type'] = 'file'
        ConfmlSetting.__init__(self, ref, **kwargs)
        """
        The file element always includes localPath and targetPath child elements.
        """
        self.add_feature(ConfmlLocalPath())
        self.add_feature(ConfmlTargetPath())

class ConfmlFolderSetting(ConfmlSetting):
    """
    Confml folder setting class.
    """
    def __init__(self, ref,**kwargs):
        kwargs['type'] = 'folder'
        ConfmlSetting.__init__(self, ref, **kwargs)
        """
        The folder element always includes localPath and targetPath child elements.
        """
        self.add_feature(ConfmlLocalPath())
        self.add_feature(ConfmlTargetPath())

class ConfmlLocalPath(ConfmlElement, api.Feature):
    """
    Confml file class. Attribute setting.
    """
    def __init__(self, ref='localPath', **kwargs):
        kwargs['type'] = 'string'
        ConfmlElement.__init__(self, **kwargs)
        api.Feature.__init__(self, ref, **kwargs)
        self.readOnly = kwargs.get('readOnly', None)


class ConfmlTargetPath(ConfmlElement, api.Feature):
    """
    Confml file class. Attribute setting.
    """
    def __init__(self, ref='targetPath', **kwargs):
        kwargs['type'] = 'string'
        ConfmlElement.__init__(self, **kwargs)
        api.Feature.__init__(self, ref, **kwargs)
        self.readOnly = kwargs.get('readOnly', None)


class ConfmlMeta(api.Base):
    """
    Confml meta element
    """
    refname = "_meta"
    def __init__(self, array=None, **kwargs):
        super(ConfmlMeta,self).__init__(self.refname)
        self.array  = []
        if array:            
            self.array += array

    def __getitem__(self, key):
        return self.array[key]
 
    def __delitem__(self, key):
        del self.array[key]

    def __setitem__(self, key, value):
        self.array[key] = value

    def __str__(self):
        tempstr = "ConfmlMeta object\n"
        counter = 0
        for item in self.array:
            tempstr += "\t%d: %s\n" % (counter, item.__str__())
            counter += 1
        return tempstr 

    def __cmp__(self, other):
        try:
            for item in self.array:
                if item != other.array[self.array.index(item)]:
                    return 1
        except:
            return 1
        return 0

    def append(self, value):
        self.array.append(value)

    def add(self, tag, value, ns=None, attributes=None):
        self.array.append(ConfmlMetaProperty(tag, value, ns, attrs=attributes))

    def get(self, tag, default=None):
        """
        Try to find the element by its tag in the meta elem array.
        @param tag: the tag that is searched,
        @param default: return the default value if the element is not found. 
        @return: the value of the ConfmlMetaProperty object if it is found. Default value 
        if element with tag is not found.
        """
        for item in self.array:
            if item.tag == tag:
                return item.value
        return default

    def replace(self, index, tag, value, ns=None, dict=None):
        self.array[index] = ConfmlMetaProperty(tag, value, ns, attrs=dict)

    def clear(self, value):
        self.array = []

    def clone(self):
        newMeta = ConfmlMeta()
        for item in self.array:
            newProp = ConfmlMetaProperty(item.tag, item.value, item.ns, attrs = item.attrs)
            newMeta.append(newProp)
        return newMeta

    def find_by_tag(self, value):
        for item in self.array:
            if item.tag == value:
                return self.array.index(item)
        return -1

    def find_by_attribute(self, name, value):
        for item in self.array:
            if item.attrs.has_key(name) and item.attrs[name] == value: 
                return self.array.index(item)
        return -1

    def get_property_by_tag(self, tag):
        """
        Try to find the element by its tag in the meta elem array.
        @param tag: the tag that is searched
        @return: the ConfmlMetaProperty object if it is found. None if element with tag is not found.
        """
        for item in self.array:
            if item.tag == tag:
                return item
        return None


class ConfmlDescription(api.Base):
    """
    Confml description element
    """
    refname = "_desc"
    def __init__(self, text=None, **kwargs):
        super(ConfmlDescription,self).__init__(self.refname)
        self.text = text or ''


class ConfmlIcon(api.Base):
    """
    Confml icon element
    """
    refname = "_icon"
    def __init__(self, href='', **kwargs):
        super(ConfmlIcon,self).__init__(self.refname)
        self.href = href


class ConfmlProperty(api.Base):
    """
    Confml meta element
    """
    refname = "_property"
    def __init__(self, **kwargs):
        """
        @param name=str: name string 
        @param value=str: value for the property, string 
        @param unit=str: unit of the property
        """
        super(ConfmlProperty,self).__init__(self.refname)
        self.name = kwargs.get('name',None)
        self.value = kwargs.get('value',None)
        self.unit = kwargs.get('unit',None)


class ConfmlMetaProperty(api.Base):
    """
    Confml meta property element
    """
    refname = "_metaproperty"
    def __init__(self, tag, value = None, ns = None, **kwargs):
        """
        """
        super(ConfmlMetaProperty,self).__init__(self.refname)
        self.tag = tag
        self.value = value
        self.ns = ns
        if kwargs.has_key("attrs") and kwargs["attrs"] != None:
            self.attrs = dict(kwargs["attrs"])
        else:
            self.attrs = {}

    def __cmp__(self, other):
        try:
            if self.tag != other.tag or self.value != other.value\
                or self.ns != other.ns or self.attrs != other.attrs:
                return 1
        except:
            return 1
        return 0

    def __str__(self):
        return "Tag: %s Value: %s Namespace: %s Attributes: % s" % (self.tag, self.value, self.ns, repr(self.attrs))         
        
            

class ConfmlLength(api.Base):
    """
    Confml length element
    """
    refname = "_length"
    def __init__(self, value, **kwargs):
        super(ConfmlLength,self).__init__(self.refname)
        self.value = value

class ConfmlMaxLength(api.Base):
    """
    Confml max element
    """
    refname = "_maxLength"
    def __init__(self, value, **kwargs):
        super(ConfmlMaxLength,self).__init__(self.refname)
        self.value = value

class ConfmlMinLength(api.Base):
    """
    Confml min element
    """
    refname = "_minLength"
    def __init__(self, value, **kwargs):
        super(ConfmlMinLength,self).__init__(self.refname)
        self.value = value

class ConfmlMinInclusive(api.Base):
    """
    Confml minInclusive element
    """
    refname = "_minInclusive"
    def __init__(self, value, **kwargs):
        super(ConfmlMinInclusive,self).__init__(self.refname)
        self.value = value

class ConfmlMaxInclusive(api.Base):
    """
    Confml minInclusive element
    """
    refname = "_maxInclusive"
    def __init__(self, value, **kwargs):
        super(ConfmlMaxInclusive,self).__init__(self.refname)
        self.value = value

class ConfmlMinExclusive(api.Base):
    """
    Confml minExclusive element
    """
    refname = "_minExclusive"
    def __init__(self, value, **kwargs):
        super(ConfmlMinExclusive,self).__init__(self.refname)
        self.value = value

class ConfmlMaxExclusive(api.Base):
    """
    Confml maxExclusive element
    """
    refname = "_maxExclusive"
    def __init__(self, value, **kwargs):
        super(ConfmlMaxExclusive,self).__init__(self.refname)
        self.value = value

class ConfmlPattern(api.Base):
    """
    Confml pattern element
    """
    refname = "_pattern"
    def __init__(self, value, **kwargs):
        super(ConfmlPattern,self).__init__(self.refname)
        self.value = value   

class ConfmlTotalDigits(api.Base):
    """
    Confml totalDigits element
    """
    refname = "_totalDigits"
    def __init__(self, value, **kwargs):
        super(ConfmlTotalDigits,self).__init__(self.refname)
        self.value = value

def get_mapper(modelname):
    """
    Return a instance of appropriate mapper for given model.
    """
    mapmodule = __import__('cone.confml.mapping')
    return mapmodule.confml.mapping.MAPPERS[modelname]()

