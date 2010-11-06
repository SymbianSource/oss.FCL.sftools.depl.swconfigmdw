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
import re
import logging

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

# cone specific imports
from cone.public import persistence, exceptions, api, utils, container, parsecontext
from cone.confml import model

CONFIGURATION_NAMESPACES = ["http://www.s60.com/xml/confml/2","http://www.s60.com/xml/confml/1"]
INCLUDE_NAMESPACES       = ["http://www.w3.org/2001/XInclude","http://www.w3.org/2001/xinclude"]
XLINK_NAMESPACES         = ["http://www.w3.org/1999/xlink"]
SCHEMA_NAMESPACES        = ["http://www.w3.org/2001/XMLSchema"]
RULEML_NAMESPACES        = ["http://www.s60.com/xml/ruleml/3"]
RULEML_NAMESPACE         = {"http://www.s60.com/xml/ruleml/3" : "ruleml"}
CV_NAMESPACE             = {"http://www.nokia.com/xml/cpf-id/1": "cv"}
KNOWN_NAMESPACES         = []
KNOWN_NAMESPACES.extend(CONFIGURATION_NAMESPACES)
KNOWN_NAMESPACES.extend(INCLUDE_NAMESPACES)
KNOWN_NAMESPACES.extend(XLINK_NAMESPACES)
KNOWN_NAMESPACES.extend(SCHEMA_NAMESPACES)
KNOWN_NAMESPACES.extend(CV_NAMESPACE)
MODEL                    = model

def dumps(obj, indent=True):
    etree = ConfmlWriter().dumps(obj)
    if indent:
        persistence.indent(etree)
    result = ElementTree.tostring(etree)
    
    # To make the output the same in linux and windows
    # (needed to make testing easier)
    if os.linesep != '\r\n':
        result = result.replace(os.linesep, '\r\n')
    
    return result

def loads(xml):
    return ConfmlReader().loads(xml)

def add_parse_warning(msg, line, type='model.confml'):
    parsecontext.get_confml_context().handle_problem(
        api.Problem(msg,
                    severity = api.Problem.SEVERITY_WARNING,
                    type     = type,
                    line     = line))

def add_unknown_element_warning(elem):
    add_parse_warning("Unknown element '%s'" % elem.tag,
                      utils.etree.get_lineno(elem),
                      type='model.confml.unknown_element')

class ConfmlWriter(persistence.ConeWriter):
    """
    """ 
    def dumps(self, obj):
        """
        @param obj: The object 
        """
        """ Make sure that the object is mapped to an object in this model """
        mobj = obj._get_mapper('confml').map_object(obj)
        writer = get_writer_for_class(mobj.__class__.__name__)
        return writer.dumps(obj)

class ConfmlReader(persistence.ConeReader):
    """
    """ 
    def loads(self, xmlstr):
        """
        @param xml: The xml which to read. reads only the first object. 
        """
        reader = get_reader_for_elem("configuration")
        try:
            etree = utils.etree.fromstring(xmlstr)
        except exceptions.XmlParseError, e:
            e.problem_type = 'xml.confml'
            raise e
        return reader.loads(etree)


class ConfigurationWriter(ConfmlWriter):
    """
    Writes a single Configuration project confml file.
    """ 
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given class name
        """
        if classname=="Configuration" or \
           classname=="ConfmlConfiguration" :
            return True
        else:
            return False

    def __init__(self):
        self.configuration_namespace = CONFIGURATION_NAMESPACES[0]
        self.include_namespace       = INCLUDE_NAMESPACES[0]
        self.xlink_namespace         = XLINK_NAMESPACES[0]
        self.schema_namespace        = SCHEMA_NAMESPACES[0]
    
    def dumps(self,obj,indent=True):
        elem = ElementTree.Element("configuration")
        if self.configuration_namespace:
            elem.set("xmlns",self.configuration_namespace)
        if self.include_namespace:
            elem.set("xmlns:xi",self.include_namespace)
        if self.include_namespace:
            elem.set("xmlns:xlink",self.xlink_namespace)
        if self.schema_namespace:
            elem.set("xmlns:xs",self.schema_namespace)
        if obj.get_name():
            elem.set("name", obj.get_name()) 
        if obj.version != None:
            elem.set("version", obj.version) 
        if obj.get_id():
            elem.set('id', obj.get_id())

        for child in obj._objects():
            """ Make sure that the object is mapped to an object in this model """
            mobj = child._get_mapper('confml').map_object(child)
            writer = get_writer_for_class(mobj.__class__.__name__)
            childelem = writer.dumps(child)
            elem.append(childelem)
        return elem
 

class ConfigurationReader(ConfmlReader):
    """
    Parses a single CPF configuration project root confml file. Parses the XInclude statements to 
    find out the layers inside the project
    """ 
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given elem name
        """
        if elemname=="configuration":
            return True
        else:
            return False

    def __init__(self):
        self.configuration_namespaces  = CONFIGURATION_NAMESPACES
        self.include_namespaces        = INCLUDE_NAMESPACES
        self.schema_namespaces         = SCHEMA_NAMESPACES

    def loads(self, etree):
        configuration = model.ConfmlConfiguration(name=etree.get("name"),
                                                  id=etree.get("id"),
                                                  version=etree.get("version"))
        configuration.lineno = utils.etree.get_lineno(etree)
        # configuration.set_name(etree.get("name") or 'unknown') 
        configuration.set_ref(etree.get("name") or 'unknown')
        for elem in etree.getchildren():
            # At the moment we ignore the namespace of elements
            (namespace,elemname) = get_elemname(elem.tag)
            try:
                reader = get_reader_for_elem(elemname)
                obj = reader.loads(elem)
                if obj:
                    configuration.add(obj)
            except exceptions.ConePersistenceError,e:
                add_unknown_element_warning(elem)
                continue
        return configuration


class MetaWriter(ConfmlWriter):
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given class name
        """
        if classname=="ConfmlMeta":
            return True
        else:
            return False

    def dumps(self, obj):
        """
        @param obj: The Configuration object 
        """
        
        elem = ElementTree.Element("meta")
        for metaproperty in obj:
            prefix = CV_NAMESPACE.get(metaproperty.ns, "")
            if prefix != "":
                #Including namespace to metadata element as well            
                elem.set(("xmlns:%s" % prefix), metaproperty.ns)
                childelem = ElementTree.Element(prefix + ":" + metaproperty.tag)
            else:
                childelem = ElementTree.Element(metaproperty.tag)
            if metaproperty.value != None:
                childelem.text = metaproperty.value
            for attr in metaproperty.attrs:
                childelem.set(attr, metaproperty.attrs[attr])
            elem.append(childelem)
        return elem


class MetaReader(ConfmlReader):
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports reading
        of the given elem name
        """
        if elemname=="meta":
            return True
        else:
            return False

    def loads(self,etree):
        metaelem = model.ConfmlMeta()
        metaelem.lineno = utils.etree.get_lineno(etree)
        for elem in etree.getchildren():            
            (namespace,elemname) = get_elemname(elem.tag)
            attributes = {}
            for key in elem.keys():
                attributes[key] = elem.get(key)
            
            metaprop = model.ConfmlMetaProperty(elemname, elem.text, namespace, attrs=attributes)
            metaelem.append(metaprop)
        return metaelem


class DescWriter(ConfmlWriter):
    """
    """ 
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given class name
        """
        if classname=="ConfmlDescription":
            return True
        else:
            return False

    def dumps(self, obj):
        """
        @param obj: The Configuration object 
        """
        elem = ElementTree.Element('desc')
        elem.text = obj.text
        return elem


class DescReader(ConfmlReader):
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlReader supports reading
        of the given elem name
        """
        if elemname=="desc":
            return True
        else:
            return False

    def loads(self,elem):
        desc = model.ConfmlDescription(elem.text)
        desc.lineno = utils.etree.get_lineno(elem)
        return desc

class ConfigurationProxyWriter(ConfmlWriter):
    """
    """ 
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given class name
        """
        if classname=="ConfigurationProxy":
            return True
        else:
            return False

    def dumps(self, obj):
        """
        @param obj: The Configuration object 
        """
        elem = self.to_include(obj.path)
        return elem

    def to_include(self,include):
        elem = ElementTree.Element("xi:include",{"href":include})
        return elem 

class ConfigurationProxyReader(ConfmlReader):
    """
    """ 
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports reading
        of the given elem name
        """
        if elemname=="include":
            return True
        else:
            return False

    def loads(self, elem):
        """
        @param elem: The xml include elem
        """
        proxy = api.ConfigurationProxy(self.parse_include(elem))
        # proxy.lineno = utils.etree.get_lineno(elem)
        return proxy

    def parse_include(self,include):
        #print "Found include %s" % include.get('href').replace('#/','')
        return include.get('href').replace('#/','')


class FeatureWriter(ConfmlWriter):
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given class name
        """
        if classname=="ConfmlFeature" or \
           classname=="Feature":
            return True
        else:
            return False

    def dumps(self, obj):
        """
        @param obj: The Configuration object 
        """
        elem = ElementTree.Element('feature', 
                                   {'ref' : obj.get_ref()})
        if obj.get_name():
            elem.set('name', obj.get_name())
        if obj.get_type():
            elem.set('type', obj.get_type())
        if obj.get_id() != None:
            elem.set('id', obj.get_id())
        if obj.get_relevant() != None:
            elem.set('relevant', obj.get_relevant())
        if obj.get_constraint() != None:
            elem.set('constraint', obj.get_constraint())
        
        dump_extension_attributes(obj, elem)
        
        for child in obj._objects():
            """ Make sure that the object is mapped to an object in this model """
            mobj = child._get_mapper('confml').map_object(child)
            writer = get_writer_for_class(mobj.__class__.__name__)
            childelem = writer.dumps(child)
            if childelem != None:
                elem.append(childelem)
        return elem


class FeatureReader(ConfmlReader):
    """
    """ 
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports reading
        of the given elem name
        """
        if elemname=="feature":
            return True
        else:
            return False

    def loads(self, elem):
        """
        @param elem: The xml include elem
        """
        type = elem.get('type')
        if type == 'sequence':
            feature = api.FeatureSequence(elem.get('ref'))
        else:
            feature = model.ConfmlFeature(elem.get('ref'))
        if elem.get('name'):
            feature.set_name(elem.get('name'))
        if elem.get('id') != None:
            feature.set_id(elem.get('id'))
        if elem.get('relevant') != None:
            feature.set_relevant(elem.get('relevant'))
        if elem.get('constraint') != None:
            feature.set_constraint(elem.get('constraint'))
        feature.set_type(type)
        feature.lineno = utils.etree.get_lineno(elem)
        
        load_extension_attributes(elem, feature)
        
        for elem in elem.getchildren():
            # At the moment we ignore the namespace of elements
            (_,elemname) = get_elemname(elem.tag)
            try:
                reader = get_reader_for_elem(elemname)
                obj = reader.loads(elem)
                feature.add(obj)
            except exceptions.ConePersistenceError:
                add_unknown_element_warning(elem)
                continue
        return feature


class OptionWriter(ConfmlWriter):
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given class name
        """
        if classname=="Option":
            return True
        else:
            return False

    def dumps(self, obj):
        """
        @param obj: The Option object 
        """
        
        objdict = {}
        if obj.get_name() is not None: objdict['name'] = obj.get_name()
        if obj.get_value() is not None: objdict['value'] = obj.get_value()
        if obj.map is not None: objdict['map'] = obj.map
        if obj.relevant is not None: objdict['relevant'] = obj.relevant
        if obj.display_name is not None: objdict['displayName'] = obj.display_name
        if obj.map_value is not None: objdict['mapValue'] = obj.map_value

        if hasattr(obj,'extensionAttributes') and obj.extensionAttributes is not None and obj.extensionAttributes != []:
            for ext_attribute in obj.extensionAttributes:
                if ext_attribute.ns != None and ext_attribute.ns != "":
                    objdict["{%s}%s" % (ext_attribute.ns, ext_attribute.name)] = str(ext_attribute.value)
                else:
                    objdict[ext_attribute.name] = str(ext_attribute.value)    

        elem = ElementTree.Element('option', objdict)
        
        return elem


class OptionReader(ConfmlReader):
    """
    """ 
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports reading
        of the given elem name
        """
        if elemname=="option":
            return True
        else:
            return False

    def loads(self, elem):
        """
        @param elem: The xml include elem
        """
        name = elem.get('name')
        value = elem.get('value')
        optmap = elem.get('map')

        if value == None and optmap == None:
            logging.getLogger('cone').warning("Encountered option with no value")
            option = None
        else:
            option = api.Option(name, value, map=optmap, 
                                relevant=elem.get('relevant'),
                                map_value=elem.get('mapValue'), 
                                display_name=elem.get('displayName'))
            option.lineno = utils.etree.get_lineno(elem) 
            
        #Add extension attributes
        for attribute in elem.attrib:
            (ns,attname) = get_elemname(attribute)
            if ns != None and ns != "":
                if not ns in KNOWN_NAMESPACES:
                    option.add_extension_attribute(model.ConfmlExtensionAttribute(attname, elem.attrib[attribute], ns))
        
        return option


class IconWriter(ConfmlWriter):
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given class name
        """
        if classname=="ConfmlIcon":
            return True
        else:
            return False

    def dumps(self, obj):
        """
        @param obj: The Option object 
        """
        elem = ElementTree.Element('icon', 
                                   {'xlink:href' : obj.href})
        return elem


class IconReader(ConfmlReader):
    """
    """ 
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports reading
        of the given elem name
        """
        if elemname=="icon":
            return True
        else:
            return False

    def loads(self, elem):
        """
        @param elem: The xml include elem
        """
        href = elem.get('{%s}href' % XLINK_NAMESPACES[0])
        obj = model.ConfmlIcon(href)
        obj.lineno = utils.etree.get_lineno(elem)
        return obj


class PropertyWriter(ConfmlWriter):
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given class name
        """
        if classname=="Property":
            return True
        else:
            return False

    def dumps(self, obj):
        """
        @param obj: The Option object 
        """
        elem = ElementTree.Element('property')
        if obj.name != None:
            elem.set('name', obj.name)
        if obj.value != None:
            elem.set('value', obj.value)
        if obj.unit != None:
            elem.set('unit', obj.unit)
        return elem


class PropertyReader(ConfmlReader):
    """
    """ 
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports reading
        of the given elem name
        """
        if elemname=="property":
            return True
        else:
            return False

    def loads(self, elem):
        """
        @param elem: The xml include elem
        """
        option = api.Property(name=elem.get('name'),value=elem.get('value'), unit=elem.get('unit'))
        option.lineno = utils.etree.get_lineno(elem)
        return option


class XmlSchemaFacetWriter(ConfmlWriter):
    MAPPING = {'ConfmlLength'       : 'xs:length',
               'ConfmlMinLength'    : 'xs:minLength',
               'ConfmlMaxLength'    : 'xs:maxLength',
               'ConfmlMinInclusive' : 'xs:minInclusive',
               'ConfmlMaxInclusive' : 'xs:maxInclusive',
               'ConfmlMinExclusive' : 'xs:minExclusive',
               'ConfmlMaxExclusive' : 'xs:maxExclusive',
               'ConfmlPattern'      : 'xs:pattern',
               'ConfmlTotalDigits'  : 'xs:totalDigits'}
    
    @classmethod
    def supported_class(cls, classname):
        return classname in cls.MAPPING
    
    def dumps(self, obj):
        """
        @param obj: The facet object 
        """
        
        classname = obj.__class__.__name__
        elem = ElementTree.Element(self.MAPPING[classname])
        if obj.value != None:
            elem.set('value', str(obj.value))
        return elem

class XmlSchemaFacetReader(ConfmlReader):
    MAPPING = {'length'       : model.ConfmlLength,
               'minLength'    : model.ConfmlMinLength,
               'maxLength'    : model.ConfmlMaxLength,
               'minInclusive' : model.ConfmlMinInclusive,
               'maxInclusive' : model.ConfmlMaxInclusive,
               'minExclusive' : model.ConfmlMinExclusive,
               'maxExclusive' : model.ConfmlMaxExclusive,
               'pattern'      : model.ConfmlPattern,
               'totalDigits'  : model.ConfmlTotalDigits}
    
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports reading
        of the given elem name
        """
        return elemname in cls.MAPPING
    
    def loads(self, elem):
        """
        @param elem: The XML schema facet element
        """
        elem_name = utils.xml.split_tag_namespace(elem.tag)[1]
        facet_class = self.MAPPING[elem_name]
        obj = facet_class(elem.get('value'))
        obj.lineno = utils.etree.get_lineno(elem)
        return obj


class DataWriter(ConfmlWriter):
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given class name
        """
        if classname=="Data" or \
           classname=="DataContainer":
            return True
        else:
            return False

    def dumps(self, obj):
        """
        @param obj: The Data object 
        """
        # Create a data hierarchy of the 
        elem = ElementTree.Element(obj.get_ref())
        if hasattr(obj,'get_map') and obj.get_map() is not None:
            elem.set('map', obj.get_map())
        elif hasattr(obj,'get_value') and obj.get_value() is not None:
            elem.text = obj.get_value()
        if hasattr(obj,'template') and obj.template == True:
            elem.set('template','true')
        if hasattr(obj,'policy') and obj.policy != '':
            elem.set('extensionPolicy',obj.policy)
        if hasattr(obj,'empty') and obj.empty == True:
            elem.set('empty','true')
        for child in obj._objects():
            writer = DataWriter()
            childelem = writer.dumps(child)
            if childelem != None:
                elem.append(childelem)
        return elem


class DataReader(ConfmlReader):
    """
    """ 
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports reading
        of the given elem name
        """
        if elemname=="data":
            return True
        else:
            return False

    def loads(self, elem):
        """
        @param elem: The xml include elem
        """
        
        (namespace,elemname) = get_elemname(elem.tag)
        obj = api.DataContainer(elemname, container=True)
        obj.lineno = utils.etree.get_lineno(elem)
        for elem in elem.getchildren():
            try:
                reader = ElemReader(attr='data')
                childobj = reader.loads(elem)
                obj.add(childobj)
            except exceptions.ConePersistenceError,e:
                add_unknown_element_warning(elem)
                continue
        return obj


class ViewWriter(ConfmlWriter):
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given class name
        """
        if classname=="View" or \
           classname=="ConfmlView":
            return True
        else:
            return False

    def dumps(self, obj):
        """
        @param obj: The Configuration object 
        """
        elem = ElementTree.Element('view', 
                                   {'name' : obj.get_name()})
        if obj.id != None:  
            elem.set('id', obj.id)
        for child in obj._objects():
            """ Make sure that the object is mapped to an object in this model """
            mobj = child._get_mapper('confml').map_object(child)
            writer = get_writer_for_class(mobj.__class__.__name__)
            childelem = writer.dumps(child)
            if childelem != None:
                elem.append(childelem)
        return elem


class ViewReader(ConfmlReader):
    """
    """ 
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports reading
        of the given elem name
        """
        if elemname=="view":
            return True
        else:
            return False

    def loads(self, elem):
        """
        @param elem: The xml include elem
        """
        vid = elem.get('id')
        name = elem.get('name')
        view = model.ConfmlView(name, id=vid)
        view.lineno = utils.etree.get_lineno(elem)
        for elem in elem.getchildren():
            # At the moment we ignore the namespace of elements
            (namespace,elemname) = get_elemname(elem.tag)
            try:
                reader = get_reader_for_elem(elemname)
                obj = reader.loads(elem)
                view.add(obj)
            except exceptions.ConePersistenceError,e:
                add_unknown_element_warning(elem)
                continue
        return view


class GroupWriter(ConfmlWriter):
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given class name
        """
        if classname=="Group" or classname=="ConfmlGroup":
            return True
        else:
            return False

    def dumps(self, obj):
        """
        @param obj: The Configuration object 
        """
        elem = ElementTree.Element('group', 
                                   {'name' : obj.get_name()})
        if obj.get_id():
            elem.set('id', obj.get_id())

        for child in obj._objects():
            """ Make sure that the object is mapped to an object in this model """
            mobj = child._get_mapper('confml').map_object(child)
            writer = get_writer_for_class(mobj.__class__.__name__)
            childelem = writer.dumps(child)
            if childelem != None:
                elem.append(childelem)
        return elem


class GroupReader(ConfmlReader):
    """
    """ 
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports reading
        of the given elem name
        """
        if elemname=='group':
            return True
        else:
            return False

    def loads(self, elem):
        """
        @param elem: The xml include elem
        """
        gname = elem.get('name')
        gref = utils.resourceref.to_dref(gname).replace('.','_')
        group = model.ConfmlGroup(gref, name=gname)
        group.lineno = utils.etree.get_lineno(elem)
        if elem.get('id'):
            group.set_id(elem.get('id'))
        for elem in elem.getchildren():
            # At the moment we ignore the namespace of elements
            (namespace,elemname) = get_elemname(elem.tag)
            try:
                reader = get_reader_for_elem(elemname, 'group')
                obj = reader.loads(elem)
                if obj != None:
                    group.add(obj)
            except exceptions.ConePersistenceError,e:
                add_unknown_element_warning(elem)
                continue
        return group


class ConfmlSettingWriter(ConfmlWriter):
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given class name
        """
        if classname=="ConfmlSetting" or \
           classname=="ConfmlStringSetting" or \
           classname=="ConfmlIntSetting" or \
           classname=="ConfmlRealSetting" or \
           classname=="ConfmlBooleanSetting" or \
           classname=="ConfmlSelectionSetting" or \
           classname=="ConfmlMultiSelectionSetting" or \
           classname=="ConfmlDateSetting" or \
           classname=="ConfmlTimeSetting" or \
           classname=="ConfmlDateTimeSetting" or \
           classname=="ConfmlDurationSetting" or \
           classname=="ConfmlHexBinarySetting" or \
           classname=="ConfmlFileSetting" or \
           classname=="ConfmlFolderSetting" or \
           classname=="FeatureSequence" or \
           classname=="ConfmlSequenceSetting":
            return True
        else:
            return False

    def dumps(self, obj):
        """
        @param obj: The Configuration object 
        """
        elem = ElementTree.Element('setting', 
                                   {'ref' : obj.get_ref()})
        self._set_setting_properties(elem, obj)
        return elem

    def _set_setting_properties(self, elem, obj):
        """
        Set the setting properties for the given elm from the given feature object
        """
        if obj.get_name():
            elem.set('name', obj.get_name())
        if obj.type:
            elem.set('type', obj.get_type())
        if obj.get_id():
            elem.set('id', obj.get_id())
        if hasattr(obj,'minOccurs'):
            elem.set('minOccurs', str(obj.minOccurs))
        if hasattr(obj,'maxOccurs'):
            elem.set('maxOccurs', str(obj.maxOccurs))
        if hasattr(obj,'readOnly') and obj.readOnly != None:
            elem.set('readOnly', str(obj.readOnly).lower())
        if hasattr(obj,'required') and obj.required != None:
            elem.set('required', str(obj.required).lower())
        if hasattr(obj,'constraint') and obj.constraint != None:
            elem.set('constraint', obj.constraint)
        if hasattr(obj,'relevant') and obj.relevant != None:
            elem.set('relevant', obj.relevant)
        if hasattr(obj,'mapKey') and obj.mapKey is not None:
            elem.set('mapKey', str(obj.mapKey))
        if hasattr(obj,'mapValue') and obj.mapValue is not None:
            elem.set('mapValue', str(obj.mapValue))
        if hasattr(obj,'displayName') and obj.displayName is not None:
            elem.set('displayName', str(obj.displayName))
            
        if getattr(obj, 'extensionAttributes', None):
            for ext_attribute in obj.extensionAttributes:
                if ext_attribute.ns:
                    elem.set(("{%s}%s" % (ext_attribute.ns, ext_attribute.name)), str(ext_attribute.value))
                else:
                    elem.set(ext_attribute.name, str(ext_attribute.value))
            
        for child in obj._objects():
            """ Make sure that the object is mapped to an object in this model """
            mobj = child._get_mapper('confml').map_object(child)
            writer = get_writer_for_class(mobj.__class__.__name__)
            childelem = writer.dumps(child)
            if childelem != None:
                elem.append(childelem)


class ConfmlSettingReader(ConfmlReader):
    """
    """ 
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports reading
        of the given elem name
        """
        if parent and not (parent=='feature' or parent=='setting'):
            return False
        if elemname=='setting':
            return True
        else:
            return False

    def loads(self, elem):
        """
        @param elem: The xml include elem
        """
        typedef = elem.get('type')
        if typedef == 'sequence':
            map_key = elem.get('mapKey')
            map_value = elem.get('mapValue')
            display_name = elem.get('displayName')
            feature = model.ConfmlSequenceSetting(elem.get('ref'), mapKey=map_key, mapValue=map_value, displayName=display_name)
        elif typedef == 'int':
            feature = model.ConfmlIntSetting(elem.get('ref'))
        elif typedef == 'boolean':
            feature = model.ConfmlBooleanSetting(elem.get('ref'))
        elif typedef == 'selection':
            feature = model.ConfmlSelectionSetting(elem.get('ref'))
        elif typedef == 'multiSelection':
            feature = model.ConfmlMultiSelectionSetting(elem.get('ref'))
        elif typedef == 'string':
            feature = model.ConfmlStringSetting(elem.get('ref'))
        elif typedef == 'real':
            feature = model.ConfmlRealSetting(elem.get('ref'))
        elif typedef == 'file':
            feature = model.ConfmlFileSetting(elem.get('ref'))
        elif typedef == 'folder':
            feature = model.ConfmlFolderSetting(elem.get('ref'))
        elif typedef == 'date':
            feature = model.ConfmlDateSetting(elem.get('ref'))
        elif typedef == 'time':
            feature = model.ConfmlTimeSetting(elem.get('ref'))
        elif typedef == 'dateTime':
            feature = model.ConfmlDateTimeSetting(elem.get('ref'))
        elif typedef == 'duration':
            feature = model.ConfmlDurationSetting(elem.get('ref'))
        elif typedef == 'hexBinary':
            feature = model.ConfmlHexBinarySetting(elem.get('ref'))
        else:
            # Handle the default setting as int type
            feature = model.ConfmlSetting(elem.get('ref'), type=typedef)
        feature.lineno = utils.etree.get_lineno(elem)
        self._get_setting_properties(elem, feature)
        
        return feature
        
    def _get_setting_properties(self, elem, feature):
        """
        Get the setting properties for the given feature from the given xml elem
        """
        if elem.get('name'):
            feature.set_name(elem.get('name'))
        if elem.get('id'):
            feature.set_id(elem.get('id'))
        if elem.get('minOccurs'):
            feature.minOccurs = int(elem.get('minOccurs'))
        if elem.get('maxOccurs'):
            feature.maxOccurs = int(elem.get('maxOccurs'))
        if elem.get('readOnly'):
            feature.readOnly = elem.get('readOnly') == 'true' or False
        if elem.get('required'):
            feature.required = elem.get('required') == 'true' or False
        if elem.get('constraint'):
            feature.constraint = elem.get('constraint')
        if elem.get('relevant'):
            feature.relevant = elem.get('relevant')
        
        #Add extension attributes
        for attribute in elem.attrib:
            (ns,attname) = get_elemname(attribute)
            if ns != None and ns != "":
                if not ns in KNOWN_NAMESPACES:
                    feature.add_extension_attribute(model.ConfmlExtensionAttribute(attname, elem.attrib[attribute], ns))
        
        for elem in elem.getchildren():
            # At the moment we ignore the namespace of elements
            (namespace,elemname) = get_elemname(elem.tag)
            try:
                reader = get_reader_for_elem(elemname)
                obj = reader.loads(elem)
                    
                if obj != None:
                    feature.add(obj,container.APPEND)
                else:
                    add_parse_warning("Invalid child %s in %s" % (elem, feature.name),
                                      utils.etree.get_lineno(elem))
            except exceptions.ConePersistenceError,e:
                add_unknown_element_warning(elem)
                continue


class GroupSettingWriter(ConfmlSettingWriter):
    """
    """ 
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given class name
        """
        if classname=="FeatureLink" or \
           classname=="ConfmlFeatureLink":
            return True
        else:
            return False

    def dumps(self, obj):
        """
        @param obj: The Configuration object 
        """
        ref = obj.fqr.replace('.','/')
        elem = ElementTree.Element('setting', 
                                   {'ref' : ref})
        self._set_setting_properties(elem, obj)
        return elem


class GroupSettingReader(ConfmlSettingReader):
    """
    """ 
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports reading
        of the given elem name
        """
        if elemname=='setting' and parent=='group':
            return True
        else:
            return False

    def loads(self, elem):
        """
        @param elem: The xml include elem
        """
        ref = elem.get('ref') or ''
        ref = ref.replace('/','.')
        feature_link = model.ConfmlFeatureLink(ref)
        feature_link.lineno = utils.etree.get_lineno(elem)
        self._get_setting_properties(elem, feature_link)
        return feature_link

class ConfmlLocalPathWriter(ConfmlWriter):
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given class name
        """
        if classname=="ConfmlLocalPath":
            return True
        else:
            return False

    def dumps(self, obj):
        """
        @param obj: The ConfmlLocalPath object 
        """
        elem = ElementTree.Element('localPath')
        if obj.readOnly:
            elem.set('readOnly', unicode(obj.readOnly))
        return elem


class ConfmlLocalPathReader(ConfmlReader):
    """
    """ 
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports reading
        of the given elem name
        """
        if elemname=="localPath":
            return True
        else:
            return False

    def loads(self, elem):
        """
        @param elem: The xml include elem
        """
        obj = model.ConfmlLocalPath(readOnly=elem.get('readOnly'))
        obj.lineno = utils.etree.get_lineno(elem)
        return obj


class ConfmlTargetPathWriter(ConfmlWriter):
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given class name
        """
        if classname=="ConfmlTargetPath":
            return True
        else:
            return False

    def dumps(self, obj):
        """
        @param obj: The ConfmlLocalPath object 
        """
        elem = ElementTree.Element('targetPath')
        if obj.readOnly:
            elem.set('readOnly', unicode(obj.readOnly))
        return elem


class ConfmlTargetPathReader(ConfmlReader):
    """
    """ 
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports reading
        of the given elem name
        """
        if elemname=="targetPath":
            return True
        else:
            return False

    def loads(self, elem):
        """
        @param elem: The xml include elem
        """
        obj = model.ConfmlTargetPath(readOnly=elem.get('readOnly'))
        obj.lineno = utils.etree.get_lineno(elem)
        return obj


class DummyWriter(ConfmlWriter):
    """
    Dummy writer is executed on ConE model elements that are not supposed to go to the confml file
    """ 
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given class name
        """
        if classname=="_FeatureProxy":
            return True
        else:
            return False

    def dumps(self, obj):
        return None

class ExtensionsWriter(ConfmlWriter):
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given class name
        """
        if classname=="ConfmlExtensions":
            return True
        else:
            return False

    def dumps(self, obj):
        """
        @param obj: The Configuration object 
        """
        
        elem = ElementTree.Element("extensions")
        for extension in obj._objects():
            if isinstance(extension, api.RulemlEvalGlobals):
                writer = EvalGlobalsWriter()
                childelem = writer.dumps(extension)
                if childelem != None:
                    elem.append(childelem)
            else:
                if extension.ns != None and extension.ns != "":
                    childelem = ElementTree.Element("{%s}%s" % (extension.ns, extension.tag))
                else:
                    childelem = ElementTree.Element(extension.tag)
                if extension.value != None:
                    childelem.text = extension.value
                for attr in extension.attrs:
                    childelem.set(attr, extension.attrs[attr])
                
                childs = self._dump_childen(extension._objects())
                for ch in childs:
                    childelem.append(ch)
                
                elem.append(childelem)
        return elem

    def _dump_childen(self, obj):
        childs = []
        
        for child in obj:
            if child.ns != None and child.ns != "":
                childelem = ElementTree.Element("{%s}%s" % (child.ns, child.tag))
            else:
                childelem = ElementTree.Element(child.tag)
            if child.value != None:
                childelem.text = child.value
            for attr in child.attrs:
                childelem.set(attr, child.attrs[attr])
                
                
            chds = self._dump_childen(child._objects())
            for ch in chds:
                childelem.append(ch)
                
            childs.append(childelem)
            
        return childs
#import xml.sax.expatreader 

class ExtensionsReader(ConfmlReader):
    
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports reading
        of the given elem name
        """
        if elemname=="extensions":
            return True
        else:
            return False

    def loads(self,etree):
        extensionselem = model.ConfmlExtensions()
        extensionselem.lineno = utils.etree.get_lineno(etree)
        for elem in etree.getchildren():
            try:
                (_,elemname) = utils.xml.split_tag_namespace(elem.tag)
                reader = get_reader_for_elem(elemname, 'extensions')
            except exceptions.ConePersistenceError:
                extensionselem._add(self._load_children(elem, etree), policy=container.APPEND)
            else:
                obj = reader.loads(elem)
                if obj != None:
                    extensionselem._add(obj, policy=container.APPEND)
        return extensionselem

    def _load_children(self, elem, etree):
        (namespace,elemname) = get_elemname(elem.tag)
        attributes = {}
        for key in elem.keys():
            attributes[key] = elem.get(key)

        extension = model.ConfmlExtension(elemname, elem.text, namespace, attrs=attributes)
        
        for childelem in elem.getchildren():
            extension._add(self._load_children(childelem, etree), policy=container.APPEND)
        
        return extension
        

class EvalGlobalsWriter(ConfmlWriter):
    @classmethod
    def supported_class(cls, classname):
        """
        Class method to determine if this ConfmlWriter supports writing
        of the given class name
        """
        if classname=="RulemlEvalGlobals":
            return True
        else:
            return False

    def dumps(self, obj):
        """
        @param obj: The Configuration object 
        """
        
        elem = ElementTree.Element("{%s}eval_globals" % (RULEML_NAMESPACES[0]))

        if obj.value != None:
            elem.text = obj.value
        if obj.file != None:
            elem.set('file', obj.file)
        
        return elem

class EvalGlobalsReader(ConfmlReader):
    
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports reading
        of the given elem name
        """
        if elemname=="eval_globals":
            return True
        else:
            return False

    def loads(self,etree):
        eval_globals = api.RulemlEvalGlobals(etree.text, etree.get("file", None))
        
        return eval_globals

class RfsReader(ConfmlReader):
    """
    """ 
    @classmethod
    def supported_elem(cls, elemname, parent=None):
        """
        Class method to determine if this ConfmlWriter supports reading
        of the given elem name
        """
        if elemname=="rfs":
            return True
        else:
            return False

    def loads(self, elem):
        """
        @param elem: The xml include elem
        """
        
        (namespace,elemname) = get_elemname(elem.tag)
        obj = api.DataContainer(elemname, container=True)
        obj.lineno = utils.etree.get_lineno(elem)
        for elem in elem.getchildren():
            try:
                reader = ElemReader(attr='rfs')
                childobj = reader.loads(elem)
                obj.add(childobj)
            except exceptions.ConePersistenceError,e:
                add_unknown_element_warning(elem)
                continue
        return obj

class ElemReader(ConfmlReader):
    def __init__(self, **kwargs):
        self.template = kwargs.get('template',False)
        self.attr = kwargs.get('attr',None)
        self.args = kwargs

    def loads(self, elem):
        """
        @param elem: The xml include elem
        """
        (namespace,elemname) = get_elemname(elem.tag)
        datavalue = None
        if len(list(elem)) == 0:
            datavalue = elem.text
        obj = model.ConfmlData(
            ref      = elemname,
            value    = datavalue,
            template = elem.get('template') == 'true' or self.template,
            attr     = self.attr,
            policy   = elem.get('extensionPolicy') or '',
            map      = elem.get('map'),
            empty    = elem.get('empty') == 'true')
        obj.lineno = utils.etree.get_lineno(elem)
        for elem in elem.getchildren():
            try:
                reader = ElemReader(**self.args)
                childobj = reader.loads(elem)
                obj.add(childobj)
            except exceptions.ConePersistenceError,e:
                logging.getLogger('cone').warning("Could not parse element %s. Exception: %s" % (elem,e))
                continue
        return obj

namespace_pattern = re.compile("{(.*)}(.*)")
nonamespace_pattern = re.compile("(.*)")

def get_elemname(tag):
    
    ns = namespace_pattern.match(tag)
    nn = nonamespace_pattern.match(tag)
    if ns:
        namespace = ns.group(1)
        elemname = ns.group(2)
        return (namespace,elemname)
    elif nn:
        namespace = ""
        elemname = nn.group(1)
        return (namespace,elemname)
    else:
        raise exceptions.ParseError("Could not parse tag %s" % tag)

def get_reader_for_elem(elemname, parent=None):
    for reader in utils.all_subclasses(ConfmlReader):
        if reader.supported_elem(elemname,parent):
            return reader()
    raise exceptions.ConePersistenceError("No reader for given elem %s under %s found!" % (elemname, parent))

def get_writer_for_class(classname):
    for writer in utils.all_subclasses(ConfmlWriter):
        if writer.supported_class(classname):
            return writer ()
    raise exceptions.ConePersistenceError("No writer for given class found! %s" % classname)

def dump_extension_attributes(obj, elem):
    if hasattr(obj,'extensionAttributes') and obj.extensionAttributes is not None and obj.extensionAttributes != []:
        for ext_attribute in obj.extensionAttributes:
            if ext_attribute.ns != None and ext_attribute.ns != "":
                elem.set(("{%s}%s" % (ext_attribute.ns, ext_attribute.name)), unicode(ext_attribute.value))
            else:
                elem.set(ext_attribute.name, unicode(ext_attribute.value))    

def load_extension_attributes(elem, obj):
    for attribute in elem.attrib:
        (ns,attname) = get_elemname(attribute)
        if ns != None and ns != "":
            if not ns in KNOWN_NAMESPACES:
                obj.add_extension_attribute(model.ConfmlExtensionAttribute(attname, elem.attrib[attribute], ns))
