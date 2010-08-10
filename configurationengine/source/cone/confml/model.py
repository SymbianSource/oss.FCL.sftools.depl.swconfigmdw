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
import sys
import re
from cone.public import api, exceptions, container, utils

class ConfmlElement(api.Base):
    def __init__(self, ref="", **kwargs):
        super(ConfmlElement,self).__init__(ref, **kwargs)
        self.lineno = None

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
    
class ConfmlData(api.Data):
    """
    The data element can contain any data setting for a feature. The data element can be 
    a value definition for any type of data. It basically just links some data to a feature. 
    The default Data attribute is 'data', but it can be any string. For example current use case 
    is 'rfs'.
    """
    def __init__(self, **kwargs):
        super(ConfmlData,self).__init__(**kwargs)
        self.lineno = None

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

    def _view_class(self):
        return ConfmlView

    def _feature_class(self):
        return ConfmlFeature

    def _configuration_class(self):
        return ConfmlConfiguration

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
        @return: The meta element of the Configuration.
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

class ConfmlSettingAttributes(ConfmlElement):
    """
    Abstract base class for setting attributes. This is used as 
    a base in actual ConfmlSetting and ConfmlFeatureLink.
    """
    def __init__(self, ref,**kwargs):
        super(ConfmlSettingAttributes,self).__init__(ref,**kwargs)
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
        self.mapKey = kwargs.get('mapKey')
        self.mapValue = kwargs.get('mapValue')
        self.displayName = kwargs.get('displayName')

        
        self.readOnly = kwargs.get('readOnly',None)
        self.constraint = kwargs.get('constraint',None)
        self.required = kwargs.get('required',None)
        self.relevant = kwargs.get('relevant',None)

    def get_valueset(self):
        """
        Get the ValueSet object for this feature, that has the list of available values.
        """
        return api.ValueRe('.*')

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
    """ The maxLength as a property """
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
    """ The minLength as a property """
    minLength = property(get_minlength,set_minlength,del_minlength)
    
    def get_length(self): 
        try:
            return getattr(self,ConfmlLength.refname).value
        except AttributeError:
            return None

    def set_length(self,value): 
        self._add(ConfmlLength(value))

    def del_length(self): 
        try:
            self._remove(ConfmlLength.refname)
        except exceptions.NotFound:
            pass
    """ The length as a property """
    length = property(get_length,set_length,del_length)

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
        propdict = {}
        for prop in self._objects(type=api.Property):
            propdict[prop.name] = prop
        return  propdict

    def get_rfs(self):
        return super(ConfmlSettingAttributes,self).get_value('rfs')

    def set_rfs(self, value):
        super(ConfmlSettingAttributes,self).set_value('rfs',value)

    def del_rfs(self):
        super(ConfmlSettingAttributes,self).del_value('rfs')

    rfs = property(get_rfs,set_rfs,del_rfs)


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

    def _group_class(self):
        return ConfmlGroup

    def _featurelink_class(self):
        return ConfmlFeatureLink

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


class ConfmlView(api.View, ConfmlGroup):
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
    def _feature_class(self):
        return ConfmlSetting

class ConfmlSetting(ConfmlSettingAttributes, api.Feature):
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
        # Add a exception case for None value, because the data casting will always fail for it
        if value == None:
            return value
        
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
    
    # Pattern for checking whether a data value should be interpreted
    # in the old style (e.g. '"opt1" "opt2" "opt3"')
    OLD_STYLE_DATA_PATTERN = re.compile(r'"[^"]*([^"]*" ")*[^"]*"')
    
    def __init__(self, ref,**kwargs):
        kwargs['type'] = 'multiSelection'
        ConfmlSetting.__init__(self,ref,**kwargs)
        
    def add_data(self, data):
        """
        Add a data value.
        @param data: A Data object  
        """
        # If there are existing data objects added to the proxy, and they
        # are not in the same DataContainer (ConfML data section), change the
        # policy to replace
        if self.dataproxy.datas.get(data.attr):
            existing_data_obj = self.dataproxy.datas[data.attr][-1]
            existing_obj_parent = existing_data_obj._find_parent_or_default(type=api.DataContainer)
            new_obj_parent = data._find_parent_or_default(type=api.DataContainer)
            
            if existing_obj_parent is not new_obj_parent:
                self.dataproxy.datas[data.attr] = []
        
        self.dataproxy._add_data(data)
    
    def get_valueset(self):
        """
        Get the ValueSet object for this feature, that has the list of available values.
        """
        return api.Feature.get_valueset(self)
    
    def convert_data_to_value(self, data_objects, cast=True, attr=None):
        if len(data_objects) == 1:
            d = data_objects[0]
            
            # Special handling for cases where the data is in the old format
            # (pre-2.88 ConfML spec)
            if d.value is not None:
                if self.OLD_STYLE_DATA_PATTERN.match(d.value):
                    return tuple([v.rstrip('"').lstrip('"') for v in d.value.split('" "')])
            
            # Single data object with empty="true" means that nothing is selected
            if d.empty: return ()
        
        # Read each data value (or name-ID mapped value) into result
        result = []
        for data_obj in data_objects:
            if data_obj.map:
                value = self._resolve_name_id_mapped_value(data_obj.map, cast_value=cast)
            else:
                value = data_obj.value
            result.append(value)
        result = utils.distinct_array(result)
        
        # Handle None in the result (data element with no text data)
        if None in result:
            # If the empty string is a valid option, change the None to that,
            # otherwise ignore
            index = result.index(None)
            if '' in self.get_valueset():   result[index] = ''
            else:                           del result[index]
        
        return tuple(result)
    
    def convert_value_to_data(self, value, attr=None):
        if not isinstance(value, (types.ListType, types.TupleType, types.NoneType)):
            raise ValueError("Only list, tuple and None types are allowed.")
        
        if value:   return [api.Data(fqr=self.fqr, value=v, attr=attr) for v in value]
        else:       return [api.Data(fqr=self.fqr, empty=True, attr=attr)]

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

class ConfmlHexBinarySetting(ConfmlSetting):
    """
    Confml setting class for hex-binary type.
    """
    def __init__(self, ref,**kwargs):
        kwargs['type'] = 'hexBinary'
        ConfmlSetting.__init__(self,ref,**kwargs)
    
    def get_valueset(self):
        return api.ValueRe(r'^([0123456789ABCDEF]{2})*$')

    def get_data_cast(self, value):
        value = value or '' # Handle None
        if value not in self.get_valueset():
            raise ValueError("Cannot convert value %r of setting '%s' into binary data: Not a valid hex string", value)
        
        temp = []
        for i in xrange(len(value) / 2):
            start = i * 2
            end   = start + 2 
            temp.append(chr(int(value[start:end], 16)))
        return ''.join(temp)
    
    def set_data_cast(self, value):
        return ''.join(['%02X' % ord(c) for c in value])

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
    The localPath "name" is always the same as its ref 'localPath'
    """
    def __init__(self, ref='localPath', **kwargs):
        kwargs['type'] = 'string'
        kwargs['name'] = ref
        ConfmlElement.__init__(self, **kwargs)
        api.Feature.__init__(self, ref, **kwargs)
        self.readOnly = kwargs.get('readOnly', None)


class ConfmlTargetPath(ConfmlElement, api.Feature):
    """
    Confml file class. Attribute setting.
    The targetPath "name" is always the same as its ref 'targetPath'
    """
    def __init__(self, ref='targetPath', **kwargs):
        kwargs['type'] = 'string'
        kwargs['name'] = ref
        ConfmlElement.__init__(self, **kwargs)
        api.Feature.__init__(self, ref, **kwargs)
        self.readOnly = kwargs.get('readOnly', None)


class ConfmlFeatureLink(ConfmlSettingAttributes, api.FeatureLink):
    """
    ConfmlFeatureLink object is the setting reference object inside confml 
    group / view. It can populate the actual FeatureProxy objects under the
    particular group / view object.
    """

    """ the override_attributes explicitly states which feature link attributes can be overridden """
    override_attributes = ['name', 
                           'desc', 
                           'minLength',
                           'maxLength',
                           'minOccurs',
                           'maxOccurs',
                           'minInclusive',
                           'maxInclusive',
                           'minExclusive',
                           'maxExclusive',
                           'pattern',
                           'totalDigits',
                           'options',
                           'properties',
                           'readOnly'
                           ]
    def __init__(self, ref,**kwargs):
        ConfmlSettingAttributes.__init__(self, ref,**kwargs)
        api.FeatureLink.__init__(self, ref, **kwargs)
        self.type = kwargs.get('type',None)

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

    def __len__(self):
        return len(self.array)
    
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

    def update(self, data):
        """
        Update this the ConfmlMeta object meta with the given data.
        @param data: The input ConfmlMeta data to update for this object
        """
        if data:
            for property in data.array:
                self.set_property_by_tag(property.tag, property.value, property.ns, property.attrs)


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

    def get_property_by_tag(self, tag, attrs={}):
        """
        Try to find the element by its tag in the meta elem array.
        @param tag: the tag that is searched
        @return: the ConfmlMetaProperty object if it is found. None if element with tag is not found.
        """ 
        for item in self.array:
            if item.tag == tag:
                if not item.attrs or (item.attrs.get("name", None) == attrs.get("name", None)):
                    return item
        return None

    def set_property_by_tag(self, tag, value, ns=None, attributes=None):
        """
        Try to find the element by its tag and set it the meta elem array. 
        This will either create a new element to the meta or replace first 
        encountered elem in array. 
        @param tag: the tag that is searched
        @return: the ConfmlMetaProperty object if it is found. None if element with tag is not found.
        """
                
        if self.get_property_by_tag(tag, attributes):
            property = self.get_property_by_tag(tag, attributes) 
            property.value = value
            property.attrs = attributes or {}
        else:
            self.add(tag, value, ns, attributes)

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
        self.attrs = dict(kwargs.get('attrs') or {})

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
        

class ConfmlNumericValue(api.Base):
    """
    Confml base class for all float type properties.
    Performs a simple value casting from string to int in value setting.
    """
    def __init__(self, ref="", **kwargs):
        super(ConfmlNumericValue,self).__init__(ref, **kwargs)
        self._value = None
        
    def get_value(self): return self._value
    def del_value(self): self._value = None
    def set_value(self, value): 
        if utils.is_float(value):
            self._value = float(value) 
        else:
            self._value = int(value)
    """ The value as a property """
    value = property(get_value,set_value,del_value)


class ConfmlLength(ConfmlNumericValue):
    """
    Confml length element
    """
    refname = "_length"
    def __init__(self, value, **kwargs):
        super(ConfmlLength,self).__init__(self.refname)
        self.value = value

class ConfmlMaxLength(ConfmlNumericValue):
    """
    Confml max element
    """
    refname = "_maxLength"
    def __init__(self, value, **kwargs):
        super(ConfmlMaxLength,self).__init__(self.refname)
        self.value = value

class ConfmlMinLength(ConfmlNumericValue):
    """
    Confml min element
    """
    refname = "_minLength"
    def __init__(self, value, **kwargs):
        super(ConfmlMinLength,self).__init__(self.refname)
        self.value = value

class ConfmlMinInclusive(ConfmlNumericValue):
    """
    Confml minInclusive element
    """
    refname = "_minInclusive"
    def __init__(self, value, **kwargs):
        super(ConfmlMinInclusive,self).__init__(self.refname)
        self.value = value

class ConfmlMaxInclusive(ConfmlNumericValue):
    """
    Confml minInclusive element
    """
    refname = "_maxInclusive"
    def __init__(self, value, **kwargs):
        super(ConfmlMaxInclusive,self).__init__(self.refname)
        self.value = value

class ConfmlMinExclusive(ConfmlNumericValue):
    """
    Confml minExclusive element
    """
    refname = "_minExclusive"
    def __init__(self, value, **kwargs):
        super(ConfmlMinExclusive,self).__init__(self.refname)
        self.value = value

class ConfmlMaxExclusive(ConfmlNumericValue):
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

class ConfmlTotalDigits(ConfmlNumericValue):
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

