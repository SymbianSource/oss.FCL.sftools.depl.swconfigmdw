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
## 
# @author Teemu Rytkonen

import sys
import os
import logging
import inspect
import re
import codecs

from cone.public import exceptions, utils, api, settings, rules, parsecontext
import _plugin_reader
from cone.public.exceptions import NotFound


debug = 0
"""
Implementation specific settings can be overriden in the global impl_settings variable
"""

AUTOCONFIG_CONFML = "autodata.confml"

def get_autoconfig(configuration):
    """
    Return the "automatic" configuration for storing temporary run-time ConfML
    features and values.
    """
    lastconfig = configuration.get_last_configuration()
    if lastconfig.get_path() != AUTOCONFIG_CONFML:
        logging.getLogger('cone').debug('Adding autodata configuration %s' % AUTOCONFIG_CONFML)
        configuration.create_configuration(AUTOCONFIG_CONFML)
    
    lastconfig = configuration.get_last_configuration()
    assert lastconfig.get_path() == AUTOCONFIG_CONFML
    return lastconfig

def get_supported_file_extensions():
    """
    Return a list of all supported ImplML file extension.
    
    Implementations are only attempted to be read from files with these
    extensions.
    """
    return ImplFactory.get_supported_file_extensions()

def get_supported_namespaces():
    """
    Returns a list of all supported ImplML namespaces.
    """
    return ImplFactory.get_reader_dict().keys()

def is_temp_feature(feature):
    """
    Return whether the given feature is a temporary feature.
    """
    return hasattr(feature, _plugin_reader.TEMP_FEATURE_MARKER_VARNAME)

def uses_ref(refs, impl_refs):
    """
    Compare two lists of setting references and return whether any of the
    references in ``refs`` is used in ``impl_refs``.
    """
    for ref in refs:
        for impl_ref in impl_refs:
            if ref.startswith(impl_ref):
                if len(ref) == len(impl_ref):
                    return True
                elif ref[len(impl_ref)] == '.':
                    return True
    return False

class GenerationContext(rules.DefaultContext):
    """
    Context object that can be used for passing generation-scope
    data to implementation instances.
    """
    
    def __init__(self, **kwargs):
        #: The tags used in this generation context
        #: (i.e. the tags passed from command line)
        self.tags = kwargs.get('tags', {})
        
        #: The tags policy used in this generation context
        self.tags_policy = kwargs.get('tags_policy', "OR")
        
        #: A dictionary that implementation instances can use to
        #: pass any data between each other
        self.impl_data_dict = {}
        
        #: A string for the phase of the generation.
        #: If None, no filtering based on phase is done when
        #: running the implementations
        self.phase = kwargs.get('phase', None)
        
        #: a list of rule results
        self.results = []
        
        #: a pointer to the configuration 
        self.configuration = kwargs.get('configuration', None)
        
        #: If True, then all implementation filtering done by
        #: should_run() is disabled, and it always returns True.
        self.filtering_disabled = False
        
        #: if True, then the execution flow should normal except 
        #: no output files are actually generated
        self.dry_run= kwargs.get('dry_run', None)
        
        #: the output folder for generation
        #: ensure already here that the output exists
        self.output= kwargs.get('output', 'output')
        
        #: List of references of the settings that have been modified in 
        #: listed layers and should trigger an implementation to be executed.
        #: None if ref filtering is not used
        self.changed_refs = kwargs.get('changed_refs', None)
        
        
        #: A boolean flag to determine whether to use ref filtering or not
        self.filter_by_refs = kwargs.get('filter_by_refs', False)
        
        #: Temp features
        self.temp_features = kwargs.get('temp_features', [])
        
        #: Executed implementation objects. This is a set so that a 
        #: implementation would exist only once in it. Even if it executed 
        #: more than once. The generation_output will show the actual 
        #: output several times if a implementation is executed several times.
        self.executed = set()
        
        #: Set of all implementation objects in the configuration context 
        self.impl_set = kwargs.get('impl_set', ImplSet())
        
        #: Generation output elements as a list 
        self.generation_output = []

        #: possible log element 
        self.log = []
        self.log_file = ""
    
    def __getstate__(self):
        state = self.__dict__.copy()
        state['impl_data_dict'] = {}
        return state
    
    def eval(self, ast, expression, value, **kwargs):
        """
        eval for rule evaluation against the context
        """
        pass

    def handle_terminal(self, expression):
        """
        Handle a terminal object 
        """
        try:
            if isinstance(expression, basestring): 
                try:
                    dview = self.configuration.get_default_view()
                    return dview.get_feature(expression).value
                except Exception, e:
                    logging.getLogger('cone').error("Could not dereference feature %s. Exception %s" % (expression, e))
                    raise e
        except Exception,e:
            logging.getLogger('cone').error("Exception with expression %s: %s" % (expression, e))
            raise e
    
    def convert_value(self, value):
        try:
            # Handle some special literals
            if value == 'true':     return True
            if value == 'false':    return False
            if value == 'none':     return None
            
            # Values can be any Python literals, so eval() the string to
            # get the value
            return eval(value)
        except Exception:
            ref_regex = re.compile('^[\w\.\*]*$', re.UNICODE) 
            if ref_regex.match(value) is None:
                raise RuntimeError("Could not evaluate '%s'" % value)
            else:
                raise RuntimeError("Could not evaluate '%s'. Did you mean a setting reference and forgot to use ${}?" % value)
    
    def set(self, expression, value, **kwargs):
        log = logging.getLogger('cone.ruleml')
        try:
            feature = self.configuration.get_default_view().get_feature(expression)
            feature.set_value(value)
            
            relation = kwargs.get('relation')
            if relation:
                log.info("Set %s = %r from %r" % (expression, value, relation))
            else:
                log.info("Set %s = %r" % (expression, value))
            
            refs = [feature.fqr]
            if feature.is_sequence():
                refs = ["%s.%s" % (feature.fqr,subref) for subref in feature.list_features()]
                
            self.add_changed_refs(refs, relation)

            if relation:
                self.generation_output.append(GenerationOutput(expression, 
                                                               relation,
                                                               type='ref'))
            return True
        except exceptions.NotFound,e:
            log.error('Set operation for %s failed, because feature with that reference was not found! Exception %s', expression, e) 
            raise e
    
    def should_run(self, impl, log_debug_message=True):
        """
        Return True if the given implementation should be run (generated).
        
        Also optionally log a message that the implementation is
        filtered out based on phase, tags or setting references.
        
        Calling this method also affects the output of executed_impls. Every
        implementation for which a call to this method has returned True
        will also be in that list.
        
        @param impl: The implementation to check.
        @param log_debug_message: If True, a debug message will be logged
            if the implementation is filtered out based on phase, tags
            or setting references.
        """
        if self.filtering_disabled:
            return True
        
        if isinstance(impl, ImplContainer):
            # Don't perform any filtering on containers
            return True
        
        impl_phases = impl.invocation_phase()
        if isinstance(impl_phases, basestring):
            impl_phases = [impl_phases]
        
        if self.phase is not None and self.phase not in impl_phases:
            # Don't log a debug message for phase-based filtering to
            # avoid unnecessary spamming (uncomment if necessary
            # during development)
            #logging.getLogger('cone').debug('Filtered out based on phase: %r (%r not in %r)' % (impl, self.phase, impl_phases))
            return False
        if self.tags and not impl.has_tag(self.tags, self.tags_policy):
            if log_debug_message:
                logging.getLogger('cone').debug('Filtered out based on tags: %r' % impl)
            return False
        if self.filter_by_refs and self.changed_refs and impl.has_ref(self.changed_refs) == False:
            if log_debug_message:
                logging.getLogger('cone').debug('Filtered out based on refs: %r' % impl)
            return False
        
        # Assumption is that when a implementation should be run it is added to the executed pile
        self.executed.add(impl)
        return True
    
    def have_run(self, impl):
        """
        This function will add the given implementation 
        outputs to the list of generation_outputs.
        """
        # Add outputs only from actual leaf implementations
        # not from ImplContainers
        if not isinstance(impl, ImplContainer):
            self.generation_output += impl.get_outputs()
    
    def create_file(self, filename, **kwargs):
        """
        Create a file handle under the output folder. Also adds the output file to the generation outputs list.
        @param filename: the filename with path, that is created under the output folder of the generation context.
        @param **kwargs: the keyword arguments that can provide essential information for the GenerationOutput 
        object creation. They should at least contain the implementation argument for the GenerationObject.
          @param **kwargs implementation: the implementation object that created this output
          @param **kwargs mode: the mode of the output file created 
          @param **kwargs encoding: the possible encoding of the output file. When this parameter is given the create_file will 
          use codecs.open method to create the file. 
        @return: the filehandle of the new file. 
        """
        
        implml   = kwargs.get('implementation', None)
        mode     = kwargs.get('mode', 'wb')
        encoding = kwargs.get('encoding', None)
        targetfile = os.path.normpath(os.path.join(self.output, filename))
        
        if not os.path.exists(os.path.dirname(targetfile)):
            os.makedirs(os.path.dirname(targetfile))
        
        if not encoding:
            outfile = open(targetfile, mode)
        else: 
            outfile = codecs.open(targetfile, mode, encoding)
        # Add the generation output
        self.generation_output.append(GenerationOutput(utils.resourceref.norm(targetfile), 
                                                       implml, 
                                                       phase=self.phase,
                                                       type='file',
                                                       output=self.output))
        return outfile
    
    def add_file(self, filename, **kwargs):
        """
        Add a file to the generation outputs list.
        @param filename: the filename with path, that is added. If the path is a relative path
        the path is added under the output folder of the generation context. Absolute path is added as such and not manipulated.
        @param **kwargs: the keyword arguments that can provide essential information for the GenerationOutput 
        object creation. They should at least contain the implementation argument for the GenerationObject.
        @return: None 
        """
        if not os.path.isabs(filename):
            targetfile = os.path.join(self.output, filename)
        else:
            targetfile = filename
        # Add the generation output
        self.generation_output.append(GenerationOutput(utils.resourceref.norm(targetfile), 
                                                       kwargs.get('implementation'), 
                                                       phase=self.phase,
                                                       type='file',
                                                       output=self.output))

    def get_output(self, **kwargs):
        """
        Get a output object from the generation_output list.
        @param **kwargs: the keyword arguments. 
            @param implml_type: a filter for generation outputs to filter generation outputs only with given implementation type. 
        @return: list of generation output objects
        """
        filters = []
        if kwargs.get('implml_type'):
            filters.append(lambda x: x.implementation and x.implementation.IMPL_TYPE_ID == kwargs.get('implml_type'))
             
        outputs = []
        # go through all the generation_output items with all provided filters
        # if the item passes all filters add it to the outputs list 
        for item in self.generation_output:
            passed = True
            for filter in filters:
                if not filter(item):
                    passed = False
                    continue
            if passed:
                outputs.append(item)
        return outputs

    def add_changed_refs(self, refs, implml=None):
        """
        Add changed refs to the current set of changed refs if necessary.
        
        If there are new refs and they are added, log also a debug message.
        """
        if self.changed_refs is None:
            return
        for ref in refs:
            self.add_changed_ref(ref, implml)
    
    def add_changed_ref(self, ref, implml=None):
        """
        Add changed ref to the current set of changed refs if necessary.
        
        If there are new refs and they are added, log also a debug message.
        """
        if self.changed_refs is None:
            return
        
        if ref not in self.changed_refs:
            self.changed_refs.append(ref)
            logging.getLogger('cone').debug('Added ref %s from implml %s' % (ref, implml))

    def get_refs_with_no_output(self, refs=None):
        if not refs:
            refs = self.changed_refs
        if refs:
            # create a set from the changed refs 
            # then remove the refs that have a generation output
            # and return the remaining refs as a list
            refsset = set(refs)
            implrefs = set()
            for output in self.generation_output:
                if output.implementation:
                    implrefs |= set(output.implementation.get_refs() or [])
                    if output.type == 'ref':
                        implrefs.add(output.name)
            # Add all sequence subfeatures to the list of implementation references
            dview = self.configuration.get_default_view()
            for fea in dview.get_features(list(implrefs)):
                if fea.is_sequence():
                    seqfeas = ["%s.%s" % (fea.fqr,fearef) for fearef in fea.get_sequence_parent().list_features()] 
                    implrefs |= set(seqfeas)
            
            refsset = refsset - implrefs
            return sorted(list(refsset))
        else:
            return []

    def get_refs_with_no_implementation(self, refs=None):
        if not refs:
            refs = self.changed_refs
        if refs:
            # create a set from the changed refs 
            # then remove the refs that have a generation output
            # and return the remaining refs as a list
            refsset = set(refs)
            implrefs = set(self.impl_set.get_implemented_refs())
            logging.getLogger('cone').debug("changed_refs: %s" % refsset)
            logging.getLogger('cone').debug("implrefs: %s" % implrefs)
            # Add all sequence subfeatures to the list of implementation references
            dview = self.configuration.get_default_view()
            for fea in dview.get_features(list(implrefs)):
                if fea.is_sequence():
                    seqfeas = ["%s.%s" % (fea.fqr,fearef) for fearef in fea.get_sequence_parent().list_features()] 
                    implrefs |= set(seqfeas)
            
            refsset = refsset - implrefs
            return sorted(list(refsset))
        else:
            return []

    @property
    def executed_impls(self):
        """
        List of all executed implementations (implementations for which
        a call to should_run() has returned True).
        """
        return list(self.executed)

    @property
    def features(self):
        """
        return the default view of the context configuration to access all features of the configuration.
        """
        return self.configuration.get_default_view()

    def grep_log(self, entry):
        """
        Grep the self.log entries for given entry and return a list of tuples with line (index, entry) 
        """
        return utils.grep_tuple(entry, self.log)

class MergedContext(GenerationContext):
    def __init__(self, contexts):
        self.contexts = contexts
        self.configuration = None
        self.changed_refs = []
        self.temp_features = []
        self.executed = set()
        self.impl_set = ImplSet()
        self.impl_dict = {}
        self.generation_output = []
        self.log = []
        self.log_files = []
        self.outputs = {}
        for context in contexts:
            self.changed_refs += context.changed_refs
            self.temp_features += context.temp_features
            self.configuration = context.configuration
            self.executed |= context.executed
            self.generation_output += context.generation_output
            self.log += context.log
            self.log_files.append(context.log_file)
            for output in context.generation_output:
                self.outputs[output.name] = output
            for impl in context.impl_set:
                self.impl_dict[impl.ref] = impl
        self.impl_set = ImplSet(self.impl_dict.values())

    def get_changed_refs(self, **kwargs):
        changed_refs = set()
        operation = kwargs.get('operation', 'union')
        for context in self.contexts:
            if not changed_refs:
                # set the base set from the first context
                changed_refs = set(context.changed_refs)
            else:
                if operation == 'union':
                    changed_refs |= set(context.changed_refs)
                elif operation == 'intersection':
                    changed_refs &= set(context.changed_refs)
                elif operation == 'difference':
                    changed_refs -= set(context.changed_refs)
                elif operation == 'symmetric_difference':
                    changed_refs ^= set(context.changed_refs)
                else:
                    raise exceptions.NotSupportedException('Illegal opration %s for get_changed_refs!' % operation)
        #remove temp features
        if kwargs.get('ignore_temps'):
            changed_refs = changed_refs - set(self.temp_features)
        return list(changed_refs)

class GenerationOutput(object):
    """
    A GenerationOutput object that is intended to be part of GenerationContext.generation_outputs.
    The data should hold information about
    """
    TYPES = ['file', 'ref']
    
    def __init__(self, name, implementation, **kwargs):
        """
        @param name: the name of the output as string
        @param implementation: the implementation object that generated this output
        @param type: the type of the output that could be file|ref
        """
        
        """ The name of the output """
        self.name = name
        
        """ The implementation object that generated the output """
        self.implementation = implementation
        
        """ The type of the output """
        self.type = kwargs.get('type', None)

        """ phase of the generation """
        self.phase = kwargs.get('phase', None)

        """ the context output path of the generation """
        self.output = kwargs.get('output', None)
        
        """ the possible exception """
        self.exception = kwargs.get('exception', None)
         
    def __str__(self):
        return "%s(%s, %s)" % (self.__class__.__name__, self.name, self.implementation)

    @property
    def filename(self):
        """
        return the filename part of the the output name. Valid only if the output name is a path.
        """
        return os.path.basename(self.name)

    @property
    def relpath(self):
        """
        return the relative name part of the the output name, with relation to the context output path. 
        """
        return utils.relpath(self.name, self.output)
        
    @property
    def abspath(self):
        """
        return the relative name part of the the output name, with relation to the context output path. 
        """
        if os.path.isabs(self.name):
            return os.path.normpath(self.name)
        else:
            return os.path.abspath(os.path.normpath(self.name))

class FlatComparisonResultEntry(object):
    """
    Class representing a result entry for a flat implementation
    comparison.
    
    Contains the following members:
    Member        Description
    file          Implementation file
    impl_type     Implementation type (e.g. 'crml', 'gcfml')
    id            Entry ID (e.g. CRML repository UID)
    sub_id        Entry sub-ID if applicable (e.g. CRML key UID)
    value_id      Implementation-specific value identifier
    source_value  Value in the source implementation
    target_value  Value in the target implementation
    
    data          Any extra data (implementation-specific)
    """
    
    VARNAMES = ['file', 'impl_type', 'id', 'sub_id', 'value_id', 'source_value', 'target_value']
    
    def __init__(self, **kwargs):
        for varname in self.VARNAMES:
            setattr(self, varname, kwargs.get(varname))
        self.data = kwargs.get('data')
    
    def __repr__(self):
        var_entries = [] 
        for varname in self.VARNAMES:
            var_entries.append('%s=%r' % (varname, getattr(self, varname)))
        return "FlatComparisonResultEntry(%s)" % ', '.join(var_entries)
    
    def __eq__(self, other):
        if type(self) is not type(other):
            return False
        for varname in self.VARNAMES:
            if getattr(self, varname) != getattr(other, varname):
                return False
        return True
    
    def __ne__(self, other):
        return not (self == other)
    
    def __lt__(self, other):
        for varname in self.VARNAMES:
            self_val = getattr(self, varname)
            other_val = getattr(other, varname)
            if self_val < other_val:    return True
            elif self_val == other_val: pass
            else:                       return False
        return False

class DuplicateImplementationEntry(object):
    """
    Class representing an entry of duplicate implementation instances
    found in a comparison.
    """
    VARNAMES = ['impl_type', 'id', 'files_in_source', 'files_in_target']
    
    def __init__(self, **kwargs):
        self.impl_type       = kwargs.get('impl_type')
        self.id              = kwargs.get('id')
        self.files_in_source = kwargs.get('files_in_source', [])
        self.files_in_target = kwargs.get('files_in_target', [])
    
    def __repr__(self):
        var_entries = [] 
        for varname in self.VARNAMES:
            val = getattr(self, varname)
            if isinstance(val, list): val = sorted(val)
            var_entries.append('%s=%r' % (varname, val))
        return "DuplicateImplementationEntry(%s)" % ', '.join(var_entries)
    
    def __eq__(self, other):
        if type(self) is not type(other):
            return False
        return self.impl_type == other.impl_type \
            and self.impl_type == other.impl_type \
            and sorted(self.files_in_source) == sorted(other.files_in_source) \
            and sorted(self.files_in_target) == sorted(other.files_in_target)
    
    def __ne__(self, other):
        return not (self == other)
    
    def __lt__(self, other):
        for varname in self.VARNAMES:
            self_val = getattr(self, varname)
            other_val = getattr(other, varname)
            if isinstance(self_val, list):      self_val = sorted(self_val)
            if isinstance(other_val, list):     other_val = sorted(other_val)
            if self_val < other_val:    return True
            elif self_val == other_val: pass
            else:                       return False
        return False

class FlatComparisonResult(object):
    """
    Class representing a flat comparison result.
    
    Each member is a list of FlatComparisonResultEntry
    objects, except for 'duplicate', which contains
    DuplicateImplementationEntry objects.
    
    Note that the entry members 'value_id', 'source_value' and
    'target_value' are irrelevant in the 'only_in_source' and
    'only_in_target' lists, and will always be None.
    """
    def __init__(self, **kwargs):
        self.only_in_source = kwargs.get('only_in_source', [])
        self.only_in_target = kwargs.get('only_in_target', [])
        self.modified       = kwargs.get('modified', [])
        self.duplicate      = kwargs.get('duplicate', [])
        
    
    def extend(self, other):
        """
        Extend this comparison result with another one.
        """
        if not isinstance(other, FlatComparisonResult):
            raise ValueError("Expected instance of %s" % FlatComparisonResult.__name__)
        
        self.only_in_source.extend(other.only_in_source)
        self.only_in_target.extend(other.only_in_target)
        self.modified.extend(other.modified)
    
    def __repr__(self):
        data = ["FlatComparisonResult(\n"]
        
        def get_list_data(lst):
            if len(lst) == 0: return '[]'
            
            temp = ['[\n']
            for item in sorted(lst):
                temp.append("    %r\n" % item)
            temp.append('  ]')
            return ''.join(temp)
        
        entries = []
        for varname in ('only_in_source', 'only_in_target', 'modified', 'duplicate'):
            entry_text = '  %s = %s' % (varname, get_list_data(getattr(self, varname)))
            entries.append(entry_text)
        data.append(',\n'.join(entries))
        
        data.append('\n)')
        return ''.join(data)
    
    def __len__(self):
        return len(self.only_in_source) + len(self.only_in_target) + len(self.modified)
    
    def __eq__(self, other):
        if type(self) is not type(other):
            return False
        return sorted(self.only_in_source) == sorted(other.only_in_source) \
            and sorted(self.only_in_target) == sorted(other.only_in_target) \
            and sorted(self.modified) == sorted(other.modified) \
            and sorted(self.duplicate) == sorted(other.duplicate)
    
    def __ne__(self, other):
        return not (self == other)

class ImplBase(object):
    """
    Base class for any implementation class. 
    """
    
    #: Identifier for the implementation type, used e.g. in .cfg files.
    #: Should be a string like e.g. 'someml'.
    IMPL_TYPE_ID = None
    
    #: Defines the default invocation phase for the implementation.
    #: The default is used if the phase is not explicitly set in the
    #: ImplML file or manually overridden by calling set_invocation_phase()
    DEFAULT_INVOCATION_PHASE = None
    
    def __init__(self, ref, configuration):
        """
        Create a ImplBase object
        @param ref : the ref to the Implml file resource.
        @param configuration : the Configuration instance for the
        configuration data.
        """
        self._settings = None
        self.ref = ref
        self.index = None
        self.lineno = None
        self.configuration = configuration
        self._output_root = self.settings.get('output_root','')
        self.output_subdir = self.settings.get('output_subdir','')
        self.plugin_output = self.settings.get('plugin_output','')
        
        self.generation_context = None
        self._tags = None
        self._invocation_phase = None
        self._tempvar_defs = []
        self.condition = None
        self._output_root_override = None

    def __reduce_ex__(self, protocol_version):
        config = self.configuration
        if protocol_version == 2:
            tpl =  (read_impl_from_location,
                    (self.ref, config, self.lineno),
                    None,
                    None,
                    None)
            return tpl
        else:
            return (read_impl_from_location,
                    (self.ref, config, self.lineno))
            

    #def __getstate__(self):
        #state = self.__dict__
        #state['configuration'] = self.configuration.path
        #return state
    
    #def __setstate__(self, dict):
    #    path = dict['configuration']
    #    configuration = api.ConfigurationProxy(path)
    #    self.__dict__.update(dict)
    #    self.configuration = configuration

    def _dereference(self, ref):
        """
        Function for dereferencing a configuration ref to a value in the Implementation configuration context. 
        """
        return self.configuration.get_default_view().get_feature(ref).value

    def _compare(self, other, dict_keys=None):
        """ 
        The plugin instance against another plugin instance
        """
        raise exceptions.NotSupportedException()
    
    def generate(self, context=None):
        """
        Generate the given implementation.
        @param context: The generation context can be given as a parameter. 
        The context can contain generation specific parameters for the 
        implementation object itself or the implementation can store data to it 
        which is visible to other implementations. 
        @return: 
        """
        raise exceptions.NotSupportedException()
    
    def post_generate(self, context=None):
        """
        Called when all normal generation has been done.
        
        @param context: The generation context can be given as a parameter. 
        The context can contain generation specific parameters for the 
        implementation object itself or the implementation can store data to it 
        which is visible to other implementations. 
        @attention: This is a temporary method used for implementing cenrep_rfs.txt generation.
        """
        pass
    
    def list_output_files(self):
        """
        Return a list of output files as an array. 
        """
        return []
    
    def get_outputs(self):
        """
        Return a list of GenerationOutput objets as a list. 
        """
        outputs = []
        phase = None 
        if self.generation_context: phase = self.generation_context.phase
        for outfile in self.list_output_files():
            outputs.append(GenerationOutput(outfile,self,type='file', phase=phase) )
        return outputs
    
    
    def get_refs(self):
        """
        Return a list of all ConfML setting references that affect this
        implementation. May also return None if references are not relevant
        for the implementation.
        """
        return None
    
    def has_ref(self, refs):
        """
        @param refs: a list of references to check against.
        @returns True if the implementation uses the given refs as input value, return False if the ref is not found.
        If refs are not relevant for the given plugin returns None. 
        """
        impl_refs = self.get_refs()
        if impl_refs is None:
            return None
        
        if isinstance(refs, basestring):
            refs = [refs]
        
        return uses_ref(refs, impl_refs)

    def flat_compare(self, other):
        """
        Return a flat comparison result for two implementations.
        @param other: The target implementation to compare against.
        @return: A FlatComparisonResult object.
        
        @raise exceptions.NotSupportedException(): The implementation class does not support
            flat comparison.
        """
        raise exceptions.NotSupportedException()
    
    def get_flat_comparison_id(self):
        """
        Return the ID used to uniquely identify this implementation instance for flat comparison.
        
        @raise exceptions.NotSupportedException() if the implementation class does not support
            flat comparison.
        """
        raise exceptions.NotSupportedException()
    
    def get_flat_comparison_extra_data(self):
        """
        Return the extra data object for a flat comparison entry.
        
        This method is called when an implementation container comparison finds an
        implementation instance that is not in the other container.
        
        @raise exceptions.NotSupportedException() if the implementation class does not support
            flat comparison.
        """
        raise exceptions.NotSupportedException()
    
    @classmethod
    def get_flat_comparison_impl_type_id(cls):
        """
        Return the type ID used to uniquely identify the current implementation class in flat comparison.
        
        @raise exceptions.NotSupportedException() if the implementation class does not support
            flat comparison.
        """
        raise exceptions.NotSupportedException()

    @property
    def settings(self):
        """
        return the plugin specific settings object.
        """
        if not self._settings:
            parser = settings.SettingsFactory.cone_parser()
            if self.IMPL_TYPE_ID is not None:
                section = self.IMPL_TYPE_ID.upper()
            else:
                section = settings.DEFAULT_SECTION
            self._settings = settings.ConeSettings(parser, section)
        return self._settings

    @property
    def output(self):
        """
        return the output folder for this plugin instance.
        """
        vars = {'output_root': self.output_root,'output_subdir': self.output_subdir,'plugin_output': self.plugin_output}
        default_format = '%(output_root)s/%(output_subdir)s/%(plugin_output)s'
        output = utils.resourceref.remove_begin_slash(utils.resourceref.norm(self.settings.get('output',default_format,vars)))
        if os.path.isabs(self.output_root):
            output = utils.resourceref.insert_begin_slash(output) 
        return output
    
    def _get_output_root(self):
        if self._output_root_override is not None:
            return self._output_root_override
        else:
            return self._output_root
    
    def _set_output_root(self, value):
        self._output_root = value
    
    output_root = property(_get_output_root, _set_output_root, None,
       """
       The output root directory.
       
       Note that if set_output_root_override() has been called with a value
       other than None, reading this property will always return that value.
       Otherwise it works just like any other property.
       """)
        
    def get_tags(self):
        if self._tags is not None:
            tags = self._tags
        else:
            tags = eval(self.settings.get('plugin_tags','{}'))
        
        # If we have a configuration, expand setting references in the tags
        if self.configuration is not None:
            dview = self.configuration.get_default_view()
            expanded_tags = {}
            for name, values in tags.iteritems():
                exp_name = utils.expand_refs_by_default_view(name, dview)
                exp_values = []
                expanded_tags[exp_name] = exp_values
                for value in values:
                    exp_value = utils.expand_refs_by_default_view(value, dview)
                    exp_values.append(exp_value)
            return expanded_tags
        else:
            return tags.copy()
        
    
    def set_tags(self, tags):
        """
        Override the default implementation tags.
        @param phase: The tag dictionary to set. If None, the implementation's
            default tags will be used.
        """
        self._tags = tags

    def has_tag(self, tags, policy=None):
        """
        @param tags: a dictionary of context : tags to check agains
        @returns True if the implementation has a matching tag.
        Otherwise return False.
        """
        if (tags==None or len(tags)==0) and len(self.get_tags()) == 0:
            return True
        if (tags!=None and len(tags)!=0) and len(self.get_tags()) == 0:
            return False
        
        items = tags.iteritems()
        self_tags = self.get_tags()
        if policy == 'AND':
            for (key,values) in items:
                tagvals = self_tags.get(key, [])
                for val in values:
                    if val not in tagvals:
                        return False
            return True
        else:
            for (key,values) in items:
                tagvals = self_tags.get(key, [])
                for val in values:
                    if val in tagvals:
                        return True
            return False
            
        return False

    def set_output_root(self,output):
        """
        Set the root directory for the output files. The output
        @param output : path to output dir.
        """
        self.output_root = output

    def get_output_root(self):
        """
        Return the current output dir.
        """
        return self.output_root
    
    def set_output_root_override(self, output):
        """
        Set the output root override.
        @param output: The override value. If None, the normal output root
            value is used.
        """
        self._output_root_override = output

    def invocation_phase(self):
        """
        @return: the phase name in which the plugin wants to be executed. 
        """
        # 1. Check if overridden on implementation instance level
        if self._invocation_phase is not None:
            return self._invocation_phase
        # 2. Check if overridden on implementation class level
        elif self.DEFAULT_INVOCATION_PHASE is not None:
            return self.DEFAULT_INVOCATION_PHASE
        # 3. Get from settings (if all else fails fall back to 'normal'
        else:
            return self.settings.get('plugin_phase', 'normal')
    
    def set_invocation_phase(self, phase):
        """
        Override the default invocation phase.
        @param phase: The invocation phase to set. If None, the implementation's
            default phase will be used.
        """
        self._invocation_phase = phase

    def compare(self):
        """
        @return: the phase name in which the plugin wants to be executed. 
        """
        return self.settings.get('plugin_phase','normal')
    
    def get_temp_variable_definitions(self):
        return self._tempvar_defs
    
    def get_relation_container(self):
        """
        Return a relation container containing all relations from this
        implementation instance, or None.
        """
        return None
    
    def get_all_implementations(self):
        """
        return a list of all actual implementation which is for ImplBase object self. 
        """
        return [self]
    
    def __repr__(self):
        return "%s(ref=%r, type=%r, lineno=%r)" % (self.__class__.__name__, self.ref, self.IMPL_TYPE_ID, self.lineno)

    @property
    def path(self):
        """
        return path relative to the Configuration projec root
        """
        return self.ref

    @property
    def abspath(self):
        """
        return absolute system path to the implementation
        """
        return os.path.abspath(os.path.join(self.configuration.storage.path,self.ref))
    
    def uses_layers(self, layers, context):
        """
        Return whether this implementation uses any of the given layers
        in the given context, i.e., whether the layers contain anything that would
        affect generation output.
        """
        # The default implementation checks against refs changed in the layers
        refs = []
        for l in layers: refs.extend(l.list_leaf_datas())
        return self.has_ref(refs)

class ImplContainer(ImplBase):
    """
    Acts as a container object with list functionality.  
    """
    def __init__(self, ref, configuration):
        ImplBase.__init__(self, ref, configuration)
        self.impls = []

    # The list functions
    def __getattr__(self, name):
        if hasattr(self.impls, name):
            return self.impls.__getattribute__(name)

    def __getitem__(self, key):
        return self.impls[key]

    def __setitem__(self, key, value):
        self.impls[key] = value
    
    def __delitem__(self, key):
        del self.impls[key]

    def __len__(self):
        return len(self.impls)
    
    def __iter__(self):
        return iter(self.impls)

    def generate(self, context=None):
        """
        Generate function for container executes generate for all sub implementations.
        @param context: The generation context can be given as a parameter. The container
        passes the context to its sub implementations.
         
        @return: 
        """
        log = logging.getLogger('cone')
        
        if self.condition and not self.condition.eval(context):
            log.debug('Filtered out based on condition %s: %r' % (self.condition, self))
            return
        
        # run generate on sub impls
        for impl in self.impls:
            if context:
                # 1. Check should the implementation be run from context
                # 2. Run ImplContainer if should
                # 3. run other ImplBase objects if this is not a dry_run                      
                if context.should_run(impl):
                    if isinstance(impl, ImplContainer) or \
                        not context.dry_run:
                        impl.generate(context)
                        # context.have_run(impl)
            else:
                impl.generate(context)

    def get_refs(self):
        # Containers always return None, because the ref-based filtering
        # happens only on the actual implementations
        return None
    
    def get_child_refs(self):
        """
        ImplContainer always None with get_refs so it one wants to get the references from all 
        leaf child objects, one can use this get_child_refs function
        @return: a list of references.
        """
        refs = []
        for impl in self.impls:
            if isinstance(impl, ImplContainer):
                refs += impl.get_child_refs()
            else:
                refs += impl.get_refs() or []
        return utils.distinct_array(refs)

    def has_tag(self, tags, policy=None):
        # Container always returns True
        return True
    
    def get_tags(self):
        # Containers always return None, because the tag-based filtering
        # happens only on the actual implementations
        return None

    def get_child_tags(self):
        """
        ImplContainer always None with get_tags so it one wants to get the teags from all 
        leaf child objects, one can use this get_child_tags function
        @return: a list of references.
        """
        tags = {}
        for impl in self.impls:
            if isinstance(impl, ImplContainer):
                utils.update_dict(tags, impl.get_child_tags())
            else:
                utils.update_dict(tags, impl.get_tags())
        return tags

    def list_output_files(self):
        """
        Return a list of output files as an array. 
        """
        files = []
        for impl in self.impls:
            files += impl.list_output_files()
        return utils.distinct_array(files)

    def get_outputs(self):
        """
        Return a list of GenerationOutput objets as a list. 
        """
        outputs = []
        for impl in self.impls:
            outputs += impl.get_outputs()
        return outputs
    
    def set_output_root(self,output):
        """
        Set the root directory for the output files. The output
        @param output : path to output dir.
        """
        self.output_root = output
        for impl in self.impls:
            impl.set_output_root(output) 

    def get_temp_variable_definitions(self):
        tempvars = self._tempvar_defs[:]
        for impl in self.impls:
            tempvars += impl.get_temp_variable_definitions()
        return tempvars

    def get_relation_container(self):
        """
        Return a relation container containing all relations from this
        container object instance, or empty relation container.
        """
        container = RelationContainer([], '<root>')
        for impl in self.impls:
            c = impl.get_relation_container()
            if isinstance(c, RelationContainer):
                container.entries.append(c)
        return container
    
    def get_all_implementations(self):
        """
        return a list of all actual implementation under this container 
        """
        actual_impls = []
        for subimpl in self.impls:
            actual_impls += subimpl.get_all_implementations()
        return actual_impls
    
    def uses_layers(self, layers, context):
        #log = logging.getLogger('uses_layers(%r)' % self)
        
        # If no sub-implementation has matching tags, the implementations would
        # never be run in this context, so there's no need to go further in that case
        if not self._have_impls_matching_tags(context.tags, context.tags_policy):
            #log.debug("No impls have matching tags, returning False")
            return False
        
        # If the container has a condition depending on any of the changed refs,
        # it means that the refs can affect generation output
        if self.condition:
            refs = []
            for l in layers: refs.extend(l.list_leaf_datas())
            if uses_ref(refs, self.condition.get_refs()):
                #log.debug("Refs affect condition, returning True")
                return True
        
        # If the condition evaluates to False (and doesn't depend on the
        # changed refs), the implementations won't be run, and thus they
        # don't use the layers in this context
        if self.condition and not self.condition.eval(context):
            #log.debug("Condition evaluates to False, returning False")
            return False
        
        for impl in self.impls:
            # Filter out based on tags if the implementation is not
            # a container (using ImplBase.has_tag() here since RuleML v2
            # overrides has_tag() to always return True)
            if not isinstance(impl, ImplContainer):
                if not ImplBase.has_tag(impl, context.tags, context.tags_policy):
                    continue
            
            if impl.uses_layers(layers, context):
                #log.debug("%r uses layer, returning True" % impl)
                return True
        
        #log.debug("Returning False")
        return False
    
    def _have_impls_matching_tags(self, tags, tags_policy):
        """
        Return if any of the container's leaf implementations use the given tags.
        """
        for impl in self.impls:
            if isinstance(impl, ImplContainer):
                if impl._have_impls_matching_tags(tags, tags_policy):
                    return True
            elif ImplBase.has_tag(impl, tags, tags_policy):
                return True
        return False
        
class ReaderBase(object):
    """
    Base class for implementation readers.
    
    Each reader class supports one XML namespace, from which it reads an implementation
    instance.
    
    The method for parsing an implementation (read_impl()) is given an ElementTree
    XML element as the root from which to parse the implementation. The plug-in
    machinery handles each XML file so that the correct reader class is used to read
    the implementations from XML elements based on the namespaces.
    """
    
    #: The XML namespace supported by the implementation reader.
    #: Should be something like "http://www.xyz.org/xml/1".
    #: Can also be None, in which case the reader will not be used
    #: (this can be useful for defining base classes for e.g. readers
    #: for different versions of an implementation).
    NAMESPACE = None
    
    #: ID for the namespace used in the generated XML schema files.
    #: Must be unique, and something simple like 'someml'. 
    NAMESPACE_ID = None
    
    #: Sub-ID for schema problems for this ImplML namespace.
    #: This is used as part of the problem type for schema validation
    #: problems. E.g. if the sub-ID is 'someml', then a schema validation
    #: problem would have the problem type 'schema.implml.someml'.
    #: If this is not given, then the problem type will simply be
    #: 'schema.implml'.
    SCHEMA_PROBLEM_SUB_ID = None
    
    #: The root element name of the implementation langauge supported by
    #: the reader. This is also used in the generate XML schema files, and
    #: must correspond to the root element name specified in the schema data.
    #: If get_schema_data() returns None, then this determines the name of
    #: the root element in the automatically generated default schema.
    ROOT_ELEMENT_NAME = None
    
    #: Any extra XML namespaces that should be ignored by the
    #: implementation parsing machinery. This is useful for specifying
    #: namespaces that are not actual ImplML namespaces, but are used
    #: inside an implementation (e.g. XInclude)
    IGNORED_NAMESPACES = []
    
    #: Supported implementation file extensions.
    #: Sub-classes can override this to add new supported file extensions
    #: if necessary. The file extensions simply control whether implementations
    #: are attempted to be read from a file or not.
    #: Note that the extensions are case-insensitive.
    FILE_EXTENSIONS = ['implml']
    
    @classmethod
    def read_impl(cls, resource_ref, configuration, doc_root):
        """
        Read an implementation instance from the given element tree.
        
        @param resource_ref: Reference to the resource in the configuration in
            which the given document root resides.
        @param configuration: The configuration used.
        @param doc_root: The document root from which to parse the implementation.
        @return: The read implementation instance, or None.
        """
        raise exceptions.NotSupportedException()
    
    @classmethod
    def read_impl_from_location(cls, resource_ref, configuration, lineno):
        """
        Read an implementation instance from the given resource at the given line number.
        
        @param resource_ref: Reference to the resource in the configuration in
            which the given document root resides.
        @param configuration: The configuration used.
        @param lineno: the line number where the root node for this particular element is searched from.
        @return: The read implementation instance, or None.
        """
        root =  cls._read_xml_doc_from_resource(resource_ref, configuration)
        elemroot = utils.etree.get_elem_from_lineno(root, lineno)
        ns, tag = utils.xml.split_tag_namespace(elemroot.tag)
        reader = cls.get_reader_for_namespace(ns)
        implml = reader.read_impl(resource_ref, configuration, elemroot)
        implml.lineno = lineno
        return implml

    @classmethod
    def get_reader_for_namespace(cls, namespace):
        return ImplFactory.get_reader_dict().get(namespace, None)
    
    @classmethod
    def get_schema_data(cls):
        """
        Return the XML schema data used for validating the ImplML supported by this reader.
        @return: The schema data as a string, or None if not available.
        """
        return None
    
    @classmethod
    def _read_xml_doc_from_resource(cls, resource_ref, configuration):
        """
        Parse an ElementTree instance from the given resource.
        """
        resource = configuration.get_resource(resource_ref)
        try:
            try:
                data = resource.read()
                return utils.etree.fromstring(data)
            except exceptions.XmlParseError, e:
                msg = "Invalid XML in implementation file '%s'. Exception: %s" % (resource_ref, e)
                raise e
        finally:
            resource.close()

class ImplContainerReader(ReaderBase):
    """
    Reader class for reading containers inside implementation files. A container 
    is a implementation in it self that can contain a list of actual implementations.
    """
    NAMESPACE = "http://www.symbianfoundation.org/xml/implml/1"
    
    
    # The reader class list loaded using ImplFactory
    __reader_classes = None
    __supported_file_extensions = None
    __ignored_namespaces = None
    
    @classmethod
    def get_reader_classes(cls):
        """
        Return a dictionary of all possible implementation reader classes.
        
        Dictionary key is the XML namespace and the value is the corresponding
        reader class.
        """
        cls.__reader_classes = ImplFactory.get_reader_dict()
        return cls.__reader_classes
    
    @classmethod
    def read_impl(cls, resource_ref, configuration, doc_root, read_impl_count=None):
        on_top_level = read_impl_count == None
        # The variable read_impl_count is used to keep track of the number of
        # currently read actual implementations. It is a list so that it can be used
        # like a pointer, i.e. functions called from here can modify the number
        # inside it. A more elegant solution is not done here, since this is temporary
        # and the index variable in implementation instances will be changed to line_number,
        # which specifies the actual line on which the implementation is specified in the file
        if read_impl_count is None: read_impl_count = [0]
        
        ns, tag = utils.xml.split_tag_namespace(doc_root.tag)
        if tag != "container":
            logging.getLogger('cone').error("Error: The root element must be a container in %s, %s" % (ns, resource_ref))
            
        reader_classes = cls.get_reader_classes()
        namespaces = reader_classes.keys()
        # Read first the root container object with attributes 
        # and then traverse through possible child containers 
        containerobj = ImplContainer(resource_ref, configuration)
        containerobj.condition = cls.get_condition(doc_root)
        
        containerobj._common_data = _plugin_reader.CommonImplmlDataReader.read_data(doc_root)
        
        # traverse through the subelements
        for elem in doc_root:
            ns, tag = utils.xml.split_tag_namespace(elem.tag)
            if ns == cls.NAMESPACE:
                # Read a sub-container from the common namespace (all other
                # common namespace elements were handled earlier)
                if tag == "container":
                    subcontainer = cls.read_impl(resource_ref, configuration, elem, read_impl_count=read_impl_count)
                    subcontainer.lineno = utils.etree.get_lineno(elem)
                    containerobj.append(subcontainer)
                    subcontainer.index = None # For now all sub-containers have index = None
            else:
                # Try to read the sub implementation object from some other namespace 
                if ns not in namespaces:
                    logging.getLogger('cone').error("Error: no reader for namespace '%s' in %s" % (ns, resource_ref))
                else:
                    reader = reader_classes[ns]
                    subelem = reader.read_impl(resource_ref, configuration, elem)
                    subelem.lineno = utils.etree.get_lineno(elem)
                    containerobj.append(subelem)
                    subelem.index = read_impl_count[0]
                    read_impl_count[0] = read_impl_count[0] +  1
        
        containerobj._tempvar_defs = containerobj._common_data.tempvar_defs
        
        if on_top_level:
            def inherit_common_data(container):
                for impl in container.impls:
                    if isinstance(impl, ImplContainer):
                        new_common_data = container._common_data.copy()
                        new_common_data.extend(impl._common_data)
                        impl._common_data = new_common_data
                        inherit_common_data(impl)
            def apply_common_data(container):
                for impl in container.impls:
                    if isinstance(impl, ImplContainer):
                        apply_common_data(impl)
                    else:
                        container._common_data.apply(impl)
            inherit_common_data(containerobj)
            apply_common_data(containerobj)
        
        return containerobj

    @classmethod
    def read_implementation(cls, xml_data):
        """
        Read a container implementation from the given xmlroot element.
        """
        root = utils.etree.fromstring(xml_data)
        return cls.read_impl("", None,root)

    @classmethod 
    def get_condition(cls, root):
        if root.get('condition'):
            left = root.get('condition')
            right = root.get('value', 'true')
            return rules.SimpleCondition(left, right)
        else:
            return None

class ImplSet(set):
    """
    Implementation set class that can hold a set of ImplBase instances. 
    """

    """ 
    The plugin phases is a list of possible phases in which the plugins are executed. 
    Each plugin instance can tell in which phase it needs to be executed. 
    """ 
    INVOCATION_PHASES = ['pre','normal','post']

    def __init__(self,implementations=None, generation_context=None):
        super(ImplSet,self).__init__(implementations or [])
        self.output = 'output'
        self.generation_context = generation_context
        self.ref_to_impl = {}
    
    def _create_ref_dict(self):
        for impl in self:
            for ref in impl.get_refs() or []:
                self.ref_to_impl.setdefault(ref, []).append(impl)
 
    def invocation_phases(self):
        """
        @return: A list of possible invocation phases
        """
        return self.INVOCATION_PHASES

    def list_output_files(self):
        """
        List the output file names from this container.
        """
        filelist = []
        for impl in self:
            files = impl.list_output_files()
            filelist.extend(files)
        return utils.distinct_array(filelist)

    def generate(self, context=None):
        """
        Generate all implementations. 
        @return: 
        """
        #for impl in self.impls:
        #    impl.generation_context = self.generation_context
        if not context:
            context =  self.generation_context
        else:
            self.generation_context = context
        # Sort by file name so that execution order is always the same
        # (easier to compare logs)
        sorted_impls = sorted(self, key=lambda impl: impl.ref)

        for impl in sorted_impls:
            # 1. Check should the implementation be run from context
            # 2. Run ImplContainer if should  
            # 3. run other ImplBase objects if this is not a dry_run                      
            if context.should_run(impl):
                if isinstance(impl, ImplContainer) or \
                    not context.dry_run:
                    self.execute([impl], 'generate', context)
                    # context.have_run(impl)
    
    def post_generate(self, context=None):
        """
        @attention: This is a temporary method used for implementing cenrep_rfs.txt generation.
        """
        if not context:
            context =  self.generation_context
        
        impls = []
        # Sort by file name so that execution order is always the same
        # (easier to compare logs)
        sorted_impls = sorted(self, key=lambda impl: impl.ref)
        for impl in sorted_impls:
            if context.should_run(impl, log_debug_message=False):
                impls.append(impl)
        
        self.execute(impls, 'post_generate', context)

    def execute(self, implementations, methodname, *args):
        """
        Internal function for executing a function to a list of implementations.
        
        Mutual execution order (for separate implementation instances defined in
        the same implementation file) is the order the implementations are
        specified in the file.
        
        @param implementations:
        @param methodname: the name of the function to execute  
        """
        for impl in implementations:
            try:
                if hasattr(impl, methodname): 
                    _member = getattr(impl, methodname)
                    _member(*args)
                else:
                    logging.getLogger('cone').error('Impl %r has no method %s' % (impl, methodname))
            except Exception, e:
                if self.generation_context:
                    self.generation_context.generation_output.append(GenerationOutput('exception from %s' % impl.ref, 
                                                                                      impl, 
                                                                                      phase=self.generation_context.phase,              
                                                                                      type='exception',
                                                                                      output=self.generation_context.output,
                                                                                      exception=e))
                utils.log_exception(logging.getLogger('cone'), 'Impl %r raised an exception: %s' % (impl, repr(e)))
        
    
    def add_implementation(self,impl):
        """
        Add a ImplBase object to this ImplBaseContainer.
        """
        self.add(impl)
        
    def remove_implementation(self,ref):
        """
        Remove implementation object by its ref (name of the implml resource). 
        """
        impls_to_remove = []
        for impl in self:
            if impl.ref == ref:
                impls_to_remove.append(impl)
        
        for impl in impls_to_remove:
            self.remove(impl)
        
    def list_implementation(self):
        """
        List all implementation in this container.
        @return: an array of resource references.
        """
        implrefs = []
        for impl in self:
            if impl.ref not in implrefs:
                implrefs.append(impl.ref)
        return implrefs
    
    def get_implementations_by_file(self, ref):
        """
        Return a list of implementations read from the given file.
        """
        return filter(lambda impl: impl.ref == ref, self)
    
    def filter_implementations(self,**kwargs):
        """
        Find any implementation with certain parameters.
        All arguments are given as dict, so they must be given with name. E.g. copy(phase='normal')
        @param phase: name of the phase
        @param refs: A list of refs that are filtered with function has_refs
        @param tags: A dictionary of tags that are filtered with function has_tags
        @return: a new ImplSet object with the filtered items.
        """
        impls = []
        """ Create a list of filter functions for each argument """ 
        filters=[]
        filters.append(lambda x: x != None)
        if kwargs.get('phase', None) != None:
            filters.append(lambda x: kwargs.get('phase') in x.invocation_phase())
        if kwargs.get('refs',None) != None:
            # Changed has_ref usage to allow not supporting refs (meaning that non supported wont be filtered with refs)
            filters.append(lambda x: x.has_ref(kwargs.get('refs')) == True or x.has_ref(kwargs.get('refs')) == None)
        if kwargs.get('tags', None) != None:
            filters.append(lambda x: x.has_tag(kwargs.get('tags'),kwargs.get('policy')))
            
        """ Go through the implementations and add all to resultset that pass all filters """ 
        for impl in self:
            pass_filters = True
            for filter in filters:
                if not filter(impl):
                    pass_filters = False
                    break
            if pass_filters:
                impls.append(impl)
        return ImplSet(impls)
    
    def find_implementations(self,**kwargs):
        """
        Find any implementation with certain parameters.
        All arguments are given as dict, so they must be given with name. E.g. copy(phase='normal')
        @param phase: name of the phase
        @param refs: A list of refs that are filtered with function has_refs
        @param tags: A dictionary of tags that are filtered with function has_tags
        @return: a new ImplSet object with the filtered items.
        """
        impls = []
        """ Create a list of filter functions for each argument """ 
        filters=[]
        filters.append(lambda x: x != None)
        if kwargs.get('phase', None) != None:
            filters.append(lambda x: kwargs.get('phase') in x.invocation_phase())
        if kwargs.get('refs',None) != None:
            # Changed has_ref usage to allow not supporting refs (meaning that non supported wont be filtered with refs)
            filters.append(lambda x: x.has_ref(kwargs.get('refs')) == True)
        if kwargs.get('tags', None) != None:
            filters.append(lambda x: x.has_tag(kwargs.get('tags'),kwargs.get('policy')))
            
        """ Go through the implementations and add all to resultset that pass all filters """ 
        for impl in self:
            pass_filters = True
            for filter in filters:
                if not filter(impl):
                    pass_filters = False
                    break
            if pass_filters:
                impls.append(impl)
        return ImplSet(impls)

    def flat_compare(self, other):
        """
        Perform a flat comparison between this implementation container and another one.
        @return: @return: A FlatComparisonResult object.
        """
        # Collect dictionaries of all comparable implementation instances
        # ---------------------------------------------------------------
        source_impls_by_class, duplicates_in_source = self._get_flat_comparison_impl_by_class_dicts('source')
        target_impls_by_class, duplicates_in_target = other._get_flat_comparison_impl_by_class_dicts('target')
        
        # Collect a list containing all implementation classes
        # ----------------------------------------------------
        all_impl_classes = []
        for impl_class in source_impls_by_class.iterkeys():
            if impl_class not in all_impl_classes:
                all_impl_classes.append(impl_class)
        for impl_class in target_impls_by_class.iterkeys():
            if impl_class not in all_impl_classes:
                all_impl_classes.append(impl_class)
        
        # Perform comparison for all classes
        # ----------------------------------
        result = FlatComparisonResult()
        for impl_class in all_impl_classes:
            src = source_impls_by_class.get(impl_class, {})
            tgt = target_impls_by_class.get(impl_class, {})
            temp_result = self._get_flat_comparison_result(impl_class, src, tgt)
            result.extend(temp_result)
        
        # Add duplicates into the comparison result
        # -----------------------------------------
        def get_or_add_dup_entry(impl_type_id, impl_id):
            for e in result.duplicate:
                if e.impl_type == impl_type_id and e.id == impl_id:
                    return e
            e = DuplicateImplementationEntry(impl_type=impl_type_id, id=impl_id)
            result.duplicate.append(e)
            return e
                    
        for impl_class, impl_type_id, impl_id, file in duplicates_in_source:
            entry = get_or_add_dup_entry(impl_type_id, impl_id)
            entry.files_in_source.append(file)
        for impl_class, impl_type_id, impl_id, file in duplicates_in_target:
            entry = get_or_add_dup_entry(impl_type_id, impl_id)
            entry.files_in_target.append(file)
        
        # Sort the files so that the output is easier to compare in unit tests
        for e in result.duplicate:
            e.files_in_source.sort()
            e.files_in_target.sort()
        
        return result
    
    def _get_flat_comparison_impl_by_class_dicts(self, name):
        result = {}
        duplicates = [] # List of (impl_class, impl_type_id, impl_id, file) tuples
        for impl in self:
            # See if the implementation is flat comparable
            try:
                impl_id = impl.get_flat_comparison_id()
            except exceptions.NotSupportedException:
                continue
            
            # Get the dictionary where implementations of this type are collected
            impl_class = type(impl)
            if impl_class not in result:
                result[impl_class] = {}
            impls_dict = result[impl_class]
            
            # Add to the dictionary
            if impl_id not in impls_dict:
                impls_dict[impl_id] = impl
            else:
                logging.getLogger('cone').warning("Multiple '%s' implementations with ID %r in %s" % (impl.IMPL_TYPE_ID, impl_id, name))
                duplicates.append((impl_class, impl.IMPL_TYPE_ID, impl_id, impl.ref))
        
        # Handle duplicates (add new duplicate entries and
        # remove from the dictionaries)
        new_duplicates = []
        for impl_class, impl_type_id, impl_id, _ in duplicates:
            # Get the corresponding dictionary 
            if impl_class not in result: continue
            impls_dict = result[impl_class]
            if impl_id not in impls_dict: continue
            impl = impls_dict[impl_id]
            
            # Add a new entry
            new_duplicates.append((impl_class, impl.IMPL_TYPE_ID, impl_id, impl.ref))
            
            # Remove from the dictionary
            del impls_dict[impl_id]
        duplicates.extend(new_duplicates)
        
        return result, duplicates
    
    def _get_flat_comparison_result(self, impl_class, source_impls_dict, target_impls_dict):
        result = FlatComparisonResult()
        impl_type_id = impl_class.get_flat_comparison_impl_type_id()
        
        for impl_id, impl in target_impls_dict.iteritems():
            if impl_id not in source_impls_dict:
                result.only_in_target.append(FlatComparisonResultEntry(
                    file        = impl.ref,
                    impl_type   = impl_type_id,
                    id          = impl_id,
                    data        = impl.get_flat_comparison_extra_data()))
        
        
        def fill_in_fields(entries, field_values):
            for entry in entries:
                for varname, value in field_values.iteritems():
                    setattr(entry, varname, value)
        
        for impl_id, src_impl in source_impls_dict.iteritems():
            if impl_id not in target_impls_dict:
                result.only_in_source.append(FlatComparisonResultEntry(
                    file        = src_impl.ref,
                    impl_type   = impl_type_id,
                    id          = impl_id,
                    data        = src_impl.get_flat_comparison_extra_data()))
            else:
                tgt_impl = target_impls_dict[impl_id]
                
                temp_result = src_impl.flat_compare(tgt_impl)
                field_values = {'file'      : tgt_impl.ref,
                                'impl_type' : impl_type_id,
                                'id'        : impl_id}
                fill_in_fields(temp_result.only_in_source,  field_values)
                fill_in_fields(temp_result.only_in_target,  field_values)
                fill_in_fields(temp_result.modified,        field_values)
                result.extend(temp_result)
        
        return result
    
    def create_temp_features(self, configuration):
        """
        Create all temporary features for the implementations in this container.
        
        @param configuration: The configuration where the temporary features are
            to be created.
        @return: A list containing the references of all created temporary features.
        
        @raise exceptions.AlreadyExists: There are duplicate temporary features defined
            in the configuration. Redefinitions of the temporaty features are only ignored.
        """
        # ----------------------------------------------------
        # Collect a list of all temporary variable definitions
        # and check for duplicates and already existing
        # features at the same time
        # ----------------------------------------------------
        tempvar_defs = []
        files_by_refs = {}
        dview = configuration.get_default_view()
        
        for impl in self:
            for fea_def in impl.get_temp_variable_definitions():
                # Check if already exists
                try:
                    dview.get_feature(fea_def.ref)
                    #raise exceptions.AlreadyExists(
                    #    "Temporary variable '%s' defined in file '%s' already exists in the configuration!" \
                    #    % (fea_def.ref, impl.ref))
                    logging.getLogger('cone').warning("Temporary variable '%s' re-definition ignored." % fea_def.ref)
                    continue
                except exceptions.NotFound:
                    pass
                
                # Add to temporary dictionary for duplicate checking
                if fea_def.ref not in files_by_refs:
                    files_by_refs[fea_def.ref] = []
                files_by_refs[fea_def.ref].append(impl.ref)
                
                # Add to the list of all temp feature definitions
                tempvar_defs.append(fea_def)
        
        # Check for duplicates
        for ref, file_list in files_by_refs.iteritems():
            if len(file_list) > 1:
                raise exceptions.AlreadyExists(
                    "Duplicate temporary variable! '%s' defined in the following files: %r" \
                    % (ref, file_list))
        del files_by_refs
        
        
        # ------------------------------
        # Create the temporary variables
        # ------------------------------
        refs = []
        if tempvar_defs:
            logging.getLogger('cone').debug('Creating %d temporary variable(s) %r' % (len(tempvar_defs), tempvar_defs))
            autoconfig = get_autoconfig(configuration)
            for fea_def in tempvar_defs:
                fea_def.create_feature(autoconfig)
                refs.append(fea_def.ref)
            
            # The default view needs to be recreated, or the created
            # features will not be visible there
            configuration.recreate_default_view()
        return refs
    
    def get_relation_container(self):
        """
        Return a relation container containing all rules from this set
        of implementation instances.
        """
        container = RelationContainer([], '<root>')
        for impl in self:
            c = impl.get_relation_container()
            if isinstance(c, RelationContainer):
                container.entries.append(c)
        return container
    
    def get_all_implementations(self):
        """
        Return a flattened list of all implementation instances in this set.
        
        The returned list contains only actual implementation instances, not
        ImplContainer objects.
        """
        # Get a list of implementation objects sorted by file name
        impl_list = list(self)
        impl_list.sort(key=lambda impl: impl.ref)
        
        result = []
        for impl in impl_list:
            result += impl.get_all_implementations()
        return result

    def get_implemented_refs(self):
        if not self.ref_to_impl:
            self._create_ref_dict()
        return sorted(self.ref_to_impl.keys())
    
    def get_implementations_with_ref(self, ref):
        if not self.ref_to_impl:
            self._create_ref_dict()
        return sorted(self.ref_to_impl.get(ref, []), lambda a,b: cmp(a.ref, b.ref))
    
class RelationExecutionResult(object):
    """
    Class representing a result from relation execution.
    """
    def __init__(self, input_refs, affected_refs, source=None, index=None):
        """
        @param input_refs: Input references, i.e. the references on the left side of
            the relation.
        @param affected_refs: Affected references, i.e. the references of the setting
            that have been assigned something as a result of the relation execution.
        @param source: The source of the relation. Can be e.g. the path to a RuleML file.
        @param index: The index (number) of the relation in the source. This could be
            e.g. 1 to denote the first rule in a RuleML file.
        """
        self.input_refs = input_refs
        self.affected_refs = affected_refs
        self.source = source
        self.index = index
    
    def __repr__(self):
        return "RelationExecutionResult(input_refs=%r, affected_refs=%r, source=%r, index=%r)" \
            % (sorted(self.input_refs), sorted(self.affected_refs), self.source, self.index)
    
    def __eq__(self, other):
        if type(self) is not type(other):
            return False
        return sorted(self.input_refs) == sorted(other.input_refs) \
            and sorted(self.affected_refs) == sorted(other.affected_refs) \
            and self.source == other.source \
            and self.index == other.index
    
    def __ne__(self, other):
        return not (self == other)

class RelationContainer(object):
    """
    A relation container that may contain relations or other
    RelationContainer objects.
    """
    def __init__(self, entries=[], source=None):
        """
        @param entries: The relations or relation containers to be added.
        @param source: The source of the relations in this container. Can be
            e.g. the path to a RuleML file.
        """
        self.entries = entries
        self.source = source
        
    def execute(self, context=None):
        """
        Execute all relations inside the container, logging any exceptions thrown
        during the execution.
        @return: A list of RelationExecutionResult objects.
        """
        results = []
        for i, entry in enumerate(self.entries):
            
            if isinstance(entry, rules.RelationBase):
                result = self._execute_relation_and_log_error(entry, self.source, i + 1, context)
                if isinstance(RelationExecutionResult):
                    results.append(result)
            elif isinstance(entry, RelationContainer):
                results.extend(self._execute_container_and_log_error(entry, context))
            else:
                logging.getLogger('cone').warning("Invalid RelationContainer entry: type=%s, obj=%r" % (type(entry), entry))
        return results
    
    def _execute_relation_and_log_error(self, relation, source, index, context=None):
        """
        Execute a relation, logging any exceptions that may be thrown.
        @param relation: The relation to execute.
        @param source: The source of the rule.
        @param index: The index of the rule, can be None if the index is not known.
        @return: The return value from the relation execution, or None if an error occurred.
        """
        try: 
            return relation.execute(context)
        except Exception, e:
            msg = "Error executing rule %r: %s: %s" % (relation, e.__class__.__name__, e)
            if context:
                gout = GenerationOutput('exception from %s' % source, 
                                        relation, 
                                        phase=context.phase,
                                        type='exception',
                                        output=context.output,
                                        exception=msg)
                context.generation_output.append(gout)
            utils.log_exception(logging.getLogger('cone'), msg)
            return None
    
    def _execute_container_and_log_error(self, container, context):
        """
        Execute a relation container, logging any exceptions that may be thrown.
        @param relation: The relation container to execute.
        @return: The results from the relation execution, or an empty list if an error occurred.
        """
        try:
            return container.execute(context)
        except Exception, e:
            log = logging.getLogger('cone')
            utils.log_exception(log, "Exception executing rules in '%s': %s" % container.source, e)
            return []
    
    def get_relation_count(self):
        """
        Return the number of relations in this container.
        """
        count = 0
        for entry in self.entries:
            if isinstance(entry, RelationContainer):
                count += entry.get_relation_count()
            else:
                count += 1
        return count
    
    def get_relations(self):
        """
        Return a list of all relations in this container.
        """
        result = []
        for entry in self.entries:
            if isinstance(entry, RelationContainer):
                result.extend(entry.get_relations())
            else:
                result.append(entry)
        return result
    

class ImplFactory(api.FactoryBase):

    __registered_reader_classes = None
    __registered_reader_classes_override = None
    __common_reader_classes = [ImplContainerReader]
    
    @classmethod
    def get_reader_classes(cls):
        """
        return a list of reader classes
        """
        reader_classes = cls.__common_reader_classes[:]
        # If the reader class list is overridden, return that
        if cls.__registered_reader_classes_override is not None:
            reader_classes += cls.__registered_reader_classes_override
        else:
            # Load the classes if not loaded already
            if cls.__registered_reader_classes is None:
                cls.__registered_reader_classes = cls.__load_reader_classes()
            reader_classes += cls.__registered_reader_classes
            
        return reader_classes
    
    @classmethod
    def get_reader_dict(cls):
        """
        return a dictionary of reader classes, where key is the reader namespace
        """
        reader_dict = {}
        for reader in cls.get_reader_classes():
            reader_dict[reader.NAMESPACE] = reader
        return reader_dict

    @classmethod
    def get_supported_file_extensions(cls):
        """
        return a dictionary of reader classes, where key is the reader namespace
        """
        file_extensions = []
        for reader in cls.get_reader_classes():
            for fe in reader.FILE_EXTENSIONS:
                fe = fe.lower()
                if fe not in file_extensions:
                    file_extensions.append(fe)
        return file_extensions

    @classmethod
    def set_reader_classes_override(cls, reader_classes):
        """
        Override the list of registered reader classes.
        
        This method is provided for unit tests.
        @param reader_classes: Reader class list to use as override. Pass None to
            disable overriding.
        """
        cls.__registered_reader_classes_override = reader_classes
    
    @classmethod
    def force_reload_reader_classes(cls):
        """
        Force-reload all reader classes.
        """
        cls.__registered_reader_classes = cls.__load_reader_classes()
    
    @classmethod
    def __load_reader_classes(cls):
        """
        Load all registered ImplML reader classes from plug-ins.
        """
        log = logging.getLogger('cone')
        log.setLevel(logging.DEBUG)
        reader_classes = []
        ENTRY_POINT = 'cone.plugins.implmlreaders'
        
        import pkg_resources
        working_set = pkg_resources.WorkingSet(sys.path)
        for entry_point in working_set.iter_entry_points(ENTRY_POINT):
            reader_class = entry_point.load()
            if not inspect.isclass(reader_class):
                log.warn("'%s' entry point '%s' is not a class (%r)" % (ENTRY_POINT, entry_point.name, reader_class))
            elif not issubclass(reader_class, ReaderBase):
                log.warn("'%s' entry point '%s' is not a sub-class of cone.plugin.ReaderBase (%r)" % (ENTRY_POINT, entry_point.name, reader_class))
            else:
                msg = "Reader class for XML namespace '%s' loaded from egg '%s' entry point '%s'" % (reader_class.NAMESPACE, ENTRY_POINT, entry_point.name)
                #log.debug(msg)
                #print msg
                reader_classes.append(reader_class)
                
        return reader_classes

    @classmethod
    def is_supported_impl_file(cls, file_name):
        """
        Return whether the given file is a supported implementation file.
        """
        ext = os.path.splitext(file_name)[1]
        if ext is not None:
            return ext[1:].lower() in cls.get_supported_file_extensions()
        else:
            return False
    
    @classmethod
    def get_impls_from_file(cls, resource_ref, configuration):
        """
        Get a list of implementation instances from the given file (resource in a configuration).
        
        @param resource_ref: Reference of the resource to read the impls from.
        @param configuration: The configuration to use.
        @return: List of implementation instances parsed and created from the file.
        
        @raise NotSupportedException: The file contains an XML namespace that is
            not registered as an ImplML namespace.
        """
        context = parsecontext.get_implml_context()
        context.current_file = resource_ref
        try:
            resource = configuration.get_resource(resource_ref)
            try:        data = resource.read()
            finally:    resource.close()
            
            # Schema-validation while parsing disabled for now
            #cone.validation.schemavalidation.validate_implml_data(data)
            
            impls = []
            reader_dict = cls.get_reader_dict()
            
            root =  utils.etree.fromstring(data)
            ns = utils.xml.split_tag_namespace(root.tag)[0]
            if ns not in reader_dict.keys():
                context.handle_problem(api.Problem("No reader for namespace '%s'" % ns,
                                                   type="xml.implml",
                                                   file=resource_ref,
                                                   line=utils.etree.get_lineno(root)))
                #logging.getLogger('cone').error("Error: no reader for namespace '%s' in %s" % (ns, resource_ref))
                return []
            rc = reader_dict[ns]
            # return the single implementation as a list to maintain 
            # backwards compability
            impl = rc.read_impl(resource_ref, configuration, root)
            impl.index = 0
            impl.lineno = utils.etree.get_lineno(root)
            return [impl]
        except Exception, e:
            if isinstance(e, exceptions.XmlParseError):
                e.problem_type = 'xml.implml'
            context.handle_exception(e)
            return []

def get_impl_set(configuration,filter='.*'):
    """
    return a ImplSet object that contains all implementation objects related to the 
    given configuration
    """
    impls = configuration.layered_implml().flatten().values()
    impls = pre_filter_impls(impls)
    # filter the resources with a given filter
    impls = utils.resourceref.filter_resources(impls,filter)
    impl_set = create_impl_set(impls,configuration)
    return impl_set

def filtered_impl_set(configuration,pathfilters=None, reffilters=None):
    """
    return a ImplSet object that contains all implementation objects related to the 
    given configuration
    """
    if pathfilters: logging.getLogger('cone').info('Filtering impls with %s' % pathfilters)
    impls = configuration.layered_implml().flatten().values()
    impls = pre_filter_impls(impls)
    # filter the resources with a given filter
    if pathfilters:
        newimpls = []
        for filter in pathfilters:
            newimpls += utils.resourceref.filter_resources(impls,filter)
        impls = utils.distinct_array(newimpls)
    impl_set = create_impl_set(impls,configuration,reffilters)
    return impl_set

def create_impl_set(impl_filename_list, configuration,reffilters=None):
    impl_filename_list = pre_filter_impls(impl_filename_list)
    if reffilters: logging.getLogger('cone').info('Filtering with refs %s' % reffilters)
    impl_container = ImplSet()
    impl_container.generation_context = GenerationContext()
    impl_container.generation_context.configuration = configuration
    for impl in impl_filename_list:
        try:
            if configuration != None and ImplFactory.is_supported_impl_file(impl):
                plugin_impls = ImplFactory.get_impls_from_file(impl, configuration)
                for plugin_impl in plugin_impls:
                    if not reffilters or plugin_impl.has_ref(reffilters):
                        impl_container.add_implementation(plugin_impl)
        except Exception, e:
            utils.log_exception(logging.getLogger('cone'), "Creating impl '%s' failed. Exception: %s" % (impl,e))
            continue
    return impl_container

def pre_filter_impls(impls):
    """
    Pre-filter implementation file refs so that files and directories
    beginning with a dot (e.g. '.svn', '.scripts') are ignored.
    """
    filter = r'(/|^|\\)\..*(/|$|\\)'
    return utils.resourceref.neg_filter_resources(impls, filter)

def read_impl_from_location(resource_ref, configuration, lineno):
    return ReaderBase.read_impl_from_location(resource_ref, configuration, lineno)
