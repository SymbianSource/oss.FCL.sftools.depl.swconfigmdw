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

import copy
import logging
from cone.public import exceptions, api, utils
import plugin
import cone.confml.model

log = logging.getLogger('cone')

# The XML namespace for common ImplML definitions
COMMON_IMPLML_NAMESPACE = "http://www.symbianfoundation.org/xml/implml/1"

# Name of the marker variable used to mark a feature as a temporary
# feature
TEMP_FEATURE_MARKER_VARNAME = '__plugin_temp_feature_marker'

class TempVariableDefinition(object):
    """
    Class representing a temporary variable definition in an implementation file.
    """
    
    def __init__(self, ref, type, value, lineno=None):
        self.ref = ref
        self.type = type
        self.value = value
        self.lineno = lineno
    
    def create_feature(self, config):
        """
        Add a feature based on this temp feature definition to the given configuration.
        """
        if '.' in self.ref:
            pos = self.ref.rfind('.')
            ref = self.ref[pos + 1:]
            namespace = self.ref[:pos]
        else:
            ref = self.ref
            namespace = ''
        
        mapping = {'string' : cone.confml.model.ConfmlStringSetting,
                   'int'    : cone.confml.model.ConfmlIntSetting,
                   'real'   : cone.confml.model.ConfmlRealSetting,
                   'boolean': cone.confml.model.ConfmlBooleanSetting}
        # Create temp variables always name being also the ref
        feature = mapping[self.type](ref, name=ref)
        setattr(feature, TEMP_FEATURE_MARKER_VARNAME, True)
        config.add_feature(feature, namespace)
        
        value = utils.expand_refs_by_default_view(self.value, config.get_default_view())
        config.add_data(api.Data(fqr=self.ref, value=value))
    
    def __eq__(self, other):
        if type(self) is type(other):
            for varname in ('ref', 'type', 'value'):
                if getattr(self, varname) != getattr(other, varname):
                    return False
            return True
        else:
            return False
        
    def __ne__(self, other):
        return not (self == other)
    
    def __repr__(self):
        return "TempFeatureDefinition(ref=%r, type=%r, value=%r)" % (self.ref, self.type, self.value)

class TempVariableSequenceDefinition(object):
    """
    Class representing a temporary variable sequence definition in an implementation file.
    """
    
    def __init__(self, ref, sub_items, lineno=None):
        self.ref = ref
        self.sub_items = sub_items
        self.lineno = lineno
    
    def create_feature(self, config):
        if '.' in self.ref:
            pos = self.ref.rfind('.')
            ref = self.ref[pos + 1:]
            namespace = self.ref[:pos]
        else:
            ref = self.ref
            namespace = ''
        
        # Creature the sequence feature
        # Create temp variables always name being also the ref
        seq_fea = api.FeatureSequence(ref, name=ref)
        setattr(seq_fea, TEMP_FEATURE_MARKER_VARNAME, True)
        config.add_feature(seq_fea, namespace)
        
        # Create the sub-features
        mapping = {'string' : cone.confml.model.ConfmlStringSetting,
                   'int'    : cone.confml.model.ConfmlIntSetting,
                   'real'   : cone.confml.model.ConfmlRealSetting,
                   'boolean': cone.confml.model.ConfmlBooleanSetting}
        sub_features = []
        for sub_item in self.sub_items:
            sub_feature = mapping[sub_item[1]](sub_item[0], name=sub_item[0])
            seq_fea.add_feature(sub_feature)
    
    def __eq__(self, other):
        if type(self) is type(other):
            return self.ref == other.ref and self.sub_items == other.sub_items
        else:
            return False
        
    def __ne__(self, other):
        return not (self == other)
    
    def __repr__(self):
        return "TempSeqFeatureDefinition(ref=%r, sub_items=%r)" % (self.ref, self.sub_items)

class SettingRefsOverride(object):
    """
    Class representing a setting reference override for an implementation.
    """
    def __init__(self, refs=None):
        """
        @param refs: The reference overrides, can be a list of references or None.
        """
        self.refs = refs
    
    def get_refs(self):
        return self.refs

    def __eq__(self, other):
        if type(self) is type(other):
            return self.refs == other.refs
        else:
            return False
        
    def __ne__(self, other):
        return not (self == other)
    
    def __repr__(self):
        return "SettingRefsOverride(refs=%r)" % self.refs

class CommonImplmlData(object):
    """
    Class representing the common ImplML namespace data read from
    an XML element.
    """
    
    def __init__(self):
        self.phase = None
        self.tags = None
        self.tempvar_defs = []
        self.setting_refs_override = None
        self.output_root_dir = None
        self.output_sub_dir = None
    
    def apply(self, impl):
        """
        Apply the data on the given implementation instance.
        """
        if self.phase:
            impl.set_invocation_phase(self.phase)
        if self.tags:
            impl.set_tags(self.tags)
        if self.setting_refs_override:
            # Override the get_refs() method of the implementation
            impl.get_refs = self.setting_refs_override.get_refs
            # Override also the has_ref() method in case it is overridden
            # in the implementation sub-class
            impl.has_ref = lambda refs: plugin.ImplBase.has_ref(impl, refs)
        if self.output_root_dir:
            impl.set_output_root_override(self.output_root_dir)
        if self.output_sub_dir:
            impl.output_subdir = self.output_sub_dir
    
    def extend(self, other):
        """
        Extend this object with the contents of another CommonImplmlData object.
        """
        if other is None:
            return
        
        if other.phase:
            self.phase = other.phase
        if other.tags:
            self.tags = other.tags
        if other.setting_refs_override:
            self.setting_refs_override = other.setting_refs_override
        if other.output_root_dir:
            self.output_root_dir = other.output_root_dir
        if other.output_sub_dir:
            self.output_sub_dir = other.output_sub_dir
    
    def copy(self):
        result = CommonImplmlData()
        result.phase = self.phase
        if self.tags is not None:
            result.tags = self.tags.copy()
        result.tempvar_defs = list(self.tempvar_defs)
        result.setting_refs_override = copy.deepcopy(self.setting_refs_override)
        result.output_root_dir = self.output_root_dir
        result.output_sub_dir = self.output_sub_dir
        return result
    
    def __eq__(self, other):
        if type(self) is type(other):
            for varname in ('phase', 'tags', 'tempvar_defs', 'setting_refs_override', 'output_root_dir', 'output_sub_dir'):
                if getattr(self, varname) != getattr(other, varname):
                    return False
            return True
        else:
            return False
    
    def __ne__(self, other):
        return not (self == other)
    
    def __repr__(self):
        return "CommonImplmlData(phase=%r, tags=%r, tempvar_defs=%r, setting_refs_override=%r, output_root_dir=%r, output_sub_dir=%r)" \
            % (self.phase,
               self.tags,
               self.tempvar_defs,
               self.setting_refs_override,
               self.output_root_dir,
               self.output_sub_dir)

class ImplReader(object):
    """
    Internal reader class for reading implementations from a file in a configuration.
    """
    
    # The reader class list loaded using ImplFactory
    __loaded_reader_classes = None
    __reader_classes = None
    __supported_file_extensions = None
    __ignored_namespaces = None
    
    def __init__(self, resource_ref, configuration):
        self.resource_ref = resource_ref
        self.configuration = configuration
    
    @classmethod
    def _load_data_from_plugins(cls):
        """
        Load all data needed for implementation parsing from the plug-ins.
        
        The actual loading is only done the first time this method is called.
        """
        # Load the data only if the reader class list has not been loaded
        # yet or it has changed
        loaded_reader_classes = plugin.ImplFactory.get_reader_classes()
        if cls.__loaded_reader_classes is loaded_reader_classes:
            return
        
        reader_classes = [plugin.ReaderBase]
        reader_classes.extend(loaded_reader_classes)
        
        cls.__reader_classes = {}
        cls.__ignored_namespaces = []
        cls.__supported_file_extensions = []
        
        for rc in reader_classes:
            # Reader class
            ns = rc.NAMESPACE
            if ns is not None:
                if ns in cls.__reader_classes:
                    raise RuntimeError("Multiple reader classes registered for ImplML namespace '%s': at least %s and %s"\
                                       % (ns, rc, cls.__reader_classes[ns]))
                cls.__reader_classes[ns] = rc
            
            # Ignored namespaces
            for ns in rc.IGNORED_NAMESPACES:
                if ns not in cls.__ignored_namespaces:
                    cls.__ignored_namespaces.append(ns)
            
            # Supported file extensions
            for fe in rc.FILE_EXTENSIONS:
                fe = fe.lower()
                if fe not in cls.__supported_file_extensions:
                    cls.__supported_file_extensions.append(fe)
            
        cls.__loaded_reader_classes = loaded_reader_classes
    
    @classmethod
    def _get_namespaces(cls, etree):
        """
        Return a list of XML namespaces in the given element tree.
        """
        namespaces = []
        namespaces.append(utils.xml.split_tag_namespace(etree.tag)[0])
        for elem in etree:
            ns = utils.xml.split_tag_namespace(elem.tag)[0]
            if ns not in namespaces:
                namespaces.append(ns)
        return filter(lambda ns: ns is not None, namespaces)
    
    def _read_impls_from_file_root_element(self, root, namespaces):
        impls = []
        reader_classes = self.get_reader_classes()
        
        # Go through the list of XML namespaces encountered in the
        # file and read an implementation using the corresponding
        # reader for each namespace
        impl_count = 0
        common_data = CommonImplmlDataReader.read_data(root)
        for ns in namespaces:
            if ns not in reader_classes: continue
            
            rc = reader_classes[ns]
            impl = self._read_impl(rc, root)
            if impl:
                impl.index = impl_count
                impl_count += 1
                if common_data: common_data.apply(impl)
                impls.append(impl)
        
        # Add temp feature definitions to the first implementation
        if common_data and impls:
            impls[0]._tempvar_defs.extend(common_data.tempvar_defs)
        return impls
    
    def _read_impls_from_file_sub_elements(self, root):
        impls = []
        
        # Collect common ImplML namespace data
        common_data = CommonImplmlData()
        for elem in root:
            ns = utils.xml.split_tag_namespace(elem.tag)[0]
            if ns == COMMON_IMPLML_NAMESPACE:
                cd = CommonImplmlDataReader.read_data(elem)
                if cd: common_data.extend(cd)
        
        # Go through all sub-elements and read an implementation instance
        # from each if possible
        impl_count = 0
        reader_classes = self.get_reader_classes()
        for elem in root:
            ns = utils.xml.split_tag_namespace(elem.tag)[0]
            if ns != COMMON_IMPLML_NAMESPACE and ns in reader_classes:
                reader_class = reader_classes[ns]
                impl = self._read_impl(reader_class, elem)
                if impl:
                    cd = CommonImplmlDataReader.read_data(elem)
                    if cd is not None:
                        impl._tempvar_defs.extend(cd.tempvar_defs)
                        data = common_data.copy()
                        data.extend(cd)
                        data.apply(impl)
                    else:
                        common_data.apply(impl)
                    
                    impl.index = impl_count
                    impl_count += 1
                    impls.append(impl)
        
        # Add temporary feature definitions to the first implementation instance
        if impls:
            impls[0]._tempvar_defs = common_data.tempvar_defs + impls[0]._tempvar_defs
        
        return impls
    
    def _read_impl(self, reader_class, elem):
        """
        Read an implementation with the given reader class from the given element.
        
        If an exception is raised during reading, the exception is logged
        and None returned. 
        
        @return: The read implementation or None.
        """
        try:
            return reader_class.read_impl(self.resource_ref, self.configuration, elem)
        except exceptions.ParseError, e:
            log.error("Error reading implementation '%s': %s", (self.resource_ref, e))
        except Exception, e:
            utils.log_exception(log, e)
            
        return None

    @classmethod
    def get_reader_classes(cls):
        """
        Return a dictionary of all possible implementation reader classes.
        
        Dictionary key is the XML namespace and the value is the corresponding
        reader class.
        """
        cls._load_data_from_plugins()
        return cls.__reader_classes
    
    @classmethod
    def get_supported_file_extensions(cls):
        """
        Return a list of all supported implementation file extensions.
        """
        cls._load_data_from_plugins()
        return cls.__supported_file_extensions
    
    @classmethod
    def get_ignored_namespaces(cls):
        """
        Return a list of all ignored XML namespaces.
        """
        cls._load_data_from_plugins()
        return cls.__ignored_namespaces

    def read_implementations(self):
        try:
            root = plugin.ReaderBase._read_xml_doc_from_resource(self.resource_ref, self.configuration)
            return self.read_implementation(root)
        except exceptions.ParseError, e:
            # Invalid XML data in the file
            log.error(e)
            return []

    def read_implementation(self, xmlroot):
        root = xmlroot
        
        # Check if the implementations should all be read from the
        # document root, or each from its own sub-element under the root
        read_from_root = False
        ns = utils.xml.split_tag_namespace(root.tag)[0]
        if ns: read_from_root = True
        
        # Collect namespaces from the file and check that all are supported or ignored
        namespaces = self._get_namespaces(root)
        for ns in namespaces:
            if ns != COMMON_IMPLML_NAMESPACE \
                and ns not in self.get_reader_classes() \
                and ns not in self.get_ignored_namespaces():
                log.error("Unsupported XML namespace '%s' in file '%s'" % (ns, self.resource_ref))
                return []
        
        if read_from_root:
            impls = self._read_impls_from_file_root_element(root, namespaces)
        else:
            impls = self._read_impls_from_file_sub_elements(root)
        return impls


class CommonImplmlDataReader(object):
    """
    Internal reader class for reading common ImplML namespace data from and element.
    """
    
    VALID_PHASES = ('pre', 'normal', 'post')
    VALID_TYPES = ('string', 'int', 'real', 'boolean')
    
    @classmethod
    def read_data(cls, etree):
        """
        Read common ImplML data from the given XML element.
        @return: A CommonImplmlData instance.
        """
        result = CommonImplmlData()
        
        reader_methods = {'phase'                   : cls._read_phase,
                          'tag'                     : cls._read_tag,
                          'tempVariable'            : cls._read_tempvar,
                          'tempVariableSequence'    : cls._read_tempvarseq,
                          'settingRefsOverride'     : cls._read_setting_refs_override,
                          'outputRootDir'           : cls._read_output_root_dir,
                          'outputSubDir'            : cls._read_output_sub_dir}
        
        for elem in etree:
            ns, tag = utils.xml.split_tag_namespace(elem.tag)
            if ns != COMMON_IMPLML_NAMESPACE:   continue
            if tag not in reader_methods:       continue
            
            reader_methods[tag](elem, result)
        
        return result
    
    @classmethod
    def _read_phase(cls, elem, result):
        phase = elem.get('name')
        if phase is None:
            cls._raise_missing_attr(elem, 'name')
        if phase not in cls.VALID_PHASES:
            raise exceptions.ParseError("Invalid invocation phase '%s' defined." % phase)
        
        result.phase = phase
    
    @classmethod
    def _read_tag(cls, elem, result):
        name = elem.get('name')
        value = elem.get('value')
        if name is not None:
            if result.tags is None:     result.tags = {}
            if name not in result.tags: result.tags[name] = []
            result.tags[name].append(value)
    
    @classmethod
    def _read_tempvar(cls, elem, result):
        ref = elem.get('ref')
        type = elem.get('type', 'string')
        value = elem.get('value', '')
        lineno = utils.etree.get_lineno(elem)
        
        if ref is None:
            cls._raise_missing_attr(elem, 'ref')
        if type not in cls.VALID_TYPES:
            cls._raise_invalid_type(ref, type)
        
        result.tempvar_defs.append(TempVariableDefinition(ref, type, value, lineno))
    
    @classmethod
    def _read_tempvarseq(cls, elem, result):
        ref = elem.get('ref')
        if ref is None:
            cls._raise_missing_attr(elem, 'ref')
        
        sub_items = []
        for sub_elem in elem.findall('{%s}tempVariable' % COMMON_IMPLML_NAMESPACE):
            sub_ref = sub_elem.get('ref')
            sub_type = sub_elem.get('type', 'string')
            
            if sub_ref is None:
                cls._raise_missing_attr(sub_elem, 'ref')
            if sub_type not in cls.VALID_TYPES:
                cls._raise_invalid_type(sub_ref, sub_type)
            
            sub_items.append((sub_ref, sub_type))
        
        if not sub_items:
            raise exceptions.ParseError("Temporary variable sequence '%s' does not have any sub-items" % ref)
        
        lineno = utils.etree.get_lineno(elem)
        
        result.tempvar_defs.append(TempVariableSequenceDefinition(ref, sub_items, lineno))
    
    @classmethod
    def _read_setting_refs_override(cls, elem, result):
        if elem.get('refsIrrelevant', 'false').lower() in ('1', 'true'):
            refs = None
        else:
            refs = []
            for sub_elem in elem.findall('{%s}settingRef' % COMMON_IMPLML_NAMESPACE):
                ref = sub_elem.get('value')
                
                if ref is None:
                    cls._raise_missing_attr(sub_elem, 'value')
                
                refs.append(ref)
                
        result.setting_refs_override = SettingRefsOverride(refs)
    
    @classmethod
    def _read_output_root_dir(cls, elem, result):
        value = elem.get('value')
        if value: result.output_root_dir = value
    
    @classmethod
    def _read_output_sub_dir(cls, elem, result):
        value = elem.get('value')
        if value: result.output_sub_dir = value

    @classmethod
    def _raise_missing_attr(cls, elem, attrname):
        raise exceptions.ParseError("XML element %s does not contain the mandatory '%s' attribute." % (elem.tag, attrname))
    
    @classmethod
    def _raise_invalid_type(cls, ref, type):
        raise exceptions.ParseError("Invalid feature type '%s' specified for temporary ConfML feature '%s'." % (type, ref))