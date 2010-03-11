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




import re
import os
import sys
import logging
import xml.parsers.expat
import codecs
from hcrplugin.hcr_exceptions import *
from hcrplugin.hcrrepository import HcrRecord, HcrRepository
from hcrplugin.hcr_writer import HcrWriter
from hcrplugin.header_writer import *
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

import __init__

from cone.public import exceptions,plugin,utils,api

class HcrmlImpl(plugin.ImplBase):
    """
    <class description>
    """
    
    IMPL_TYPE_ID = "hcrml"

    def __init__(self, resource_ref, configuration):
        plugin.ImplBase.__init__(self, resource_ref, configuration)
        self.logger = logging.getLogger('cone.hcrml(%s)' % resource_ref)
        self.configuration = configuration
        self.hcrml_file = resource_ref


    def generate(self, context=None):
        """
        Generate the given implementation. 
        @return: 
        """
        outputfile = self.__get_output_filename()
        if outputfile != None:
            # Create the path to the output file
            output_path = os.path.dirname(outputfile)
            if output_path != '' and not os.path.exists(output_path):
                os.makedirs(output_path)
        
        # For output type 'hcr', write the binary repository file
        if self.output_obj.type == 'hcr':
            self.logger.info("Generating binary repository to '%s'" % outputfile)
            writer = HcrWriter()
            repo = self.output_obj.get_hcr_repository()
            data = writer.get_repository_bindata(repo)
            f = open(outputfile,'wb')
            try:        f.write(data)
            finally:    f.close()
        elif self.output_obj.type == 'header':
            self.logger.info("Generating header file to '%s'" % outputfile)
            writer = HeaderWriter(outputfile, self.output_obj)
            writer.write()
        elif self.output_obj.type == None:
            # The HCRML file contains no <output> element, so no output should
            # be generated
            pass

    def get_refs(self):
        return self.refs
    
    def list_output_files(self):
        """
        Return a list of output files as an array. 
        """
        fname = self.__get_output_filename()
        return [fname] if fname else []
    
    def __get_output_filename(self):
        if self.output_obj.file != None:
            return os.path.normpath(os.path.join(self.output, self.output_obj.file))
        else:
            return None


class HcrmlReader(plugin.ReaderBase):
    NAMESPACE = 'http://www.symbianfoundation.org/xml/hcrml/1'
    FILE_EXTENSIONS = ['hcrml']
    
    def __init__(self, resource_ref, configuration):
        self.configuration = configuration
        self.hcrml_file = resource_ref
        self.refs = []
        self.namespaces = [self.NAMESPACE]
        self.doc = None
    
    @classmethod
    def read_impl(cls, resource_ref, configuration, etree):
        reader = HcrmlReader(resource_ref, configuration)
        reader.doc = etree
        
        impl = HcrmlImpl(resource_ref, configuration)
        impl.output_obj = reader.read_hcrml_output()
        impl.refs = reader.refs
        return impl

    def read_hcrml_output(self, ignore_includes=False):
        output = Output()
        
        # There should only be one <output> element, so use find()
        out_elem = self.doc.find("{%s}output" % self.namespaces[0])
        if out_elem != None:
            version = out_elem.get('version')
            read_only = out_elem.get('readOnly')
            file = out_elem.get('file')
            type = out_elem.get('type')
            
            if type == None or type == '':
                raise NoTypeDefinedInOutPutTagError("Type attribute missing in hcrml file")
            
            if type not in ('hcr', 'header'): 
               raise InvalidTypeDefinedInOutPutTagError("Type attribute invalid in hcrml file: %s" % type)
           
            output.version = version
            output.read_only = read_only
            output.file = file
            output.type = type
         
            # An <output> element may contain <include> elements for including other
            # HCRML files, so read and include categories from those
            if not ignore_includes:
                included_files = self.read_hcrml_includes(out_elem)
                read_categories = self.read_categories_from_hcrml_files(included_files)
                output.categories.extend(read_categories)
            
         
        """ output tag is not mandatory, but there should be some categories included """
        for cat_elem in self.doc.getiterator("{%s}category" % self.namespaces[0]):
            category = self.read_hrcml_category(cat_elem)
            output.categories.append(category)
        return output 
    
    def read_hcrml_includes(self, output_elem):
        """
        Read all <include> elements under an <output> element.
        @return: List of other HCRML files to include.
        """
        result = []
        
        include_refs = []
        for include_elem in output_elem.findall("{%s}include" % self.namespaces[0]):
            ref = include_elem.get('ref')
            if ref != None: include_refs.append(ref)
        
        if include_refs:
            # There are include refs, construct the list of files that should
            # be included
            all_files = self.configuration.list_resources()
            included_files = []
            for ref in include_refs:
                files_by_ref = self.filter_file_list_by_include_ref(all_files, ref)
                result.extend(files_by_ref)
        
        # Make sure that no file is in the list more than once
        result = list(set(result))
        return result
        
    def read_categories_from_hcrml_files(self, files):
        """
        Read all categories from the list of the given HCRML files.
        """
        categories = []
        
        for file in files:
            # Skip the current file
            if os.path.normpath(file) == os.path.normpath(self.hcrml_file):
                continue
            
            # Read the <output> element and append its categories to the result list
            reader = HcrmlReader(file, self.configuration)
            reader.doc = self._read_xml_doc_from_resource(file, self.configuration)
            # Read the output element, but ignore includes, since we are
            # currently reading from inside an include
            output_obj = reader.read_hcrml_output(ignore_includes=True)
            categories.extend(output_obj.categories)
            
        return categories
            
    def read_hrcml_category(self,cat_elem):
        category_uid = cat_elem.get('uid')
        if category_uid == None or category_uid == '':
           raise NoCategoryUIDInHcrmlFileError("No category uid attribute implemented in hcrml file!")
        name = cat_elem.get('name')
        if name == None or name == '':
           raise NoCategoryNameInHcrmlFileError("No category name attribute implemented in hcrml file!")
        category = Category()
        category.name = name
        try:
            category.category_uid = long(category_uid)
        except ValueError:
            category.category_uid = long(category_uid, 16)
        category.xml_elem = cat_elem  
        for setting_elem in cat_elem.getiterator("{%s}setting" % self.namespaces[0]):
             setting = self.read_hcrml_setting(setting_elem)
             category.settings.append(setting)
        return category
            

    def read_hcrml_setting(self,setting_elem):
        
        ref = setting_elem.get('ref')
        if ref == None or ref == '':
            raise NoRefInHcrmlFileError("No ref in setting tag attribute implemented in hcrml file!")
        else:
            self.refs.append(ref)
        type = setting_elem.get('type')
        if type == None or type == '':
            raise NoTypeAttributeInSettingHcrmlFileError("No type in setting tag attribute implemented in hcrml file ref: %s" % ref )
        name = setting_elem.get('name')
        if name == None or name == '':
            raise NoNameAttributeInSettingHcrmlFileError("No type in setting tag attribute implemented in hcrml file ref: %s" % ref )
        id = setting_elem.get('id')
        if id == None or id == '':
            raise NoIdAttributeInSettingHcrmlFileError("No id in setting tag attribute implemented in hcrml file ref: %s" % ref )

        comment = setting_elem.get('comment')
        if comment == None:
            comment = ''
            
        
        setting = Setting(self.configuration)
        setting.comment = comment
        setting.name = name
        setting.ref = ref
        try:
            setting.id = long(id)
        except ValueError:
            setting.id = long(id, 16)
        setting.type = type
        setting.xml_elem = setting_elem
        for flag_elem in setting_elem.getiterator("{%s}flags" % self.namespaces[0]):
             flag = self.read_hrcml_flags(setting_elem)
             setting.flag = flag
        return setting

    def read_hrcml_flags(self,flag_elem):
         Uninitialised = flag_elem.get('Uninitialised') 
         Modifiable = flag_elem.get('Modifiable')
         Persistent = flag_elem.get('Persistent')
         flag = Flag()
         flag.Uninitialised = Uninitialised
         flag.Modifiable = Modifiable
         flag.Persistent = Persistent
         return flag
     
    def filter_file_list_by_include_ref(self, files, ref):
        pattern = ref + '$'
        pattern = pattern.replace('.', r'\.')
        pattern = pattern.replace('*', '.*')
        pattern = '(^|.*/)' + pattern
        result = []
        for file in files:
            if re.match(pattern, file.replace('\\', '/')) != None:
                result.append(file)
        return result


class Flag(object):
    def __init__(self):
        self.Uninitialised = 0
        self.Modifiable    = 0
        self.Persistent    = 0

class Setting(object):
    def __init__(self,configuration):
        self.name   = None
        self.ref    = None
        self.type   = None
        self.id = None
        self.flag = None
        self.comment = ''
        self.configuration = configuration
        
    @property
    def value(self):
        dview = self.configuration.get_default_view()
        feature = dview.get_feature(self.ref)
        value = feature.get_value()
        
        if self.type in (HcrRecord.VALTYPE_ARRAY_INT32, HcrRecord.VALTYPE_ARRAY_UINT32):
            # Convert string values to numbers
            value = map(lambda x: self.__str_to_long(x), value)
        elif self.type == HcrRecord.VALTYPE_BIN_DATA and feature.get_type() == 'string':
            value = self.__hex_to_bindata(value)
        return value
    
    def __str_to_long(self, str_value):
        try:
            return long(str_value)
        except ValueError:
            return long(str_value, 16)
    
    def __hex_to_bindata(self, hexdata):
        orig_hexdata = hexdata
        hexdata = hexdata.replace(' ', '').replace('\r', '').replace('\n', '').replace('\t', '')
        if len(hexdata) % 2 != 0:
            raise ValueError("Failed to convert %r into binary data: String length %d (whitespace stripped) is not divisible by 2", orig_hexdata, len(hexdata))
        for c in hexdata:
            if c not in "0123456789abcdefABCDEF":
                raise ValueError("Failed to convert %r into binary data: Not a valid hex string", hexdata)
        
        temp = []
        for i in xrange(len(hexdata) / 2):
            start = i * 2
            end   = start + 2 
            temp.append(chr(int(hexdata[start:end], 16)))
        return ''.join(temp)

class Category(object):
    def __init__(self):
        self.name   = None
        self.category_uid    = None
        self.settings = []
    
    def get_hcr_records(self):
        """
        Return a list of HcrRecord objects created based on this category's settings.
        """
        result = []
        for setting in self.settings:
            record = HcrRecord(setting.type, setting.value, self.category_uid, setting.id)
            flag = setting.flag
            if flag:
                record.flags = 0
                if flag.Uninitialised == '1':   record.flags |= HcrRecord.FLAG_UNINITIALIZED
                if flag.Modifiable == '1':      record.flags |= HcrRecord.FLAG_MODIFIABLE
                if flag.Persistent == '1':      record.flags |= HcrRecord.FLAG_PERSISTENT
            result.append(record)
        return result 
        

class Output(object):
    def __init__(self):
        self.file = None
        self.type = None
        self.version = None
        self.read_only = None
        self.categories = []
    
    def get_hcr_records(self):
        """
        Return a list of HcrRecord objects created based on this output object's categories.
        """
        result = []
        for category in self.categories:
            result.extend(category.get_hcr_records())
        return result
    
    def get_hcr_repository(self):
        """
        Return a HcrRepository object created based on this output.
        
        The type of this Output object should be 'hcr', otherwise and an exception is raised.
        """
        if self.type != 'hcr':
            raise RuntimeError("get_hcr_repository() called on an Output object with type '%s' (should be 'hcr')" % self.type)
        
        return HcrRepository(self.get_hcr_records())
        