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
'''
Legacy RuleML plug-in to support RuleML 1 and 2 after rule engine changes
in cone.public.rules. The new RuleML version is 3, and it uses the setting
reference format ${MyFeature.MySetting} in the rules.

The rule engine (rules.py) before the change is contained in this plug-in.

NOTE THAT THIS PLUG-IN WILL NOT BE MAINTAINED, ALL NEW DEVELOPMENT SHOULD
HAPPEN IN THE NEW RULE PLUG-IN. IF NEW FUNCTIONALITY IS REQUIRED IN AN
EXISTING RULEML FILE, THE CHANGES SHOULD BE MADE TO THE NEW RULE PLUG-IN
AND THE EXISTING RULEML FILE CONVERTED TO RULEML 3.
'''


import os
import sys
import logging
import shutil
import pkg_resources

import __init__
import re

from legacyruleplugin import relations, rules
from cone.public import exceptions,plugin,utils,api

class RuleImpl(plugin.ImplBase):
    """
    MakeImpl plugin finds feature references that are configured in a .ruleml file
    and generate a rule from them
    """
    IMPL_TYPE_ID = 'ruleml'
    DEFAULT_INVOCATION_PHASE = 'pre'
    
    def __init__(self, ref, configuration, relation_container):
        """
        Overloading the default constructor
        """
        plugin.ImplBase.__init__(self,ref,configuration)
        self.relation_container = relation_container

    def list_output_files(self):
        """
        Return a list of output files as an array. 
        """
        return []
    
    def generate(self, context=None):
        relation_container = self.get_relation_container()
        relation_container.context = context
        return relation_container.execute(context)
    
    def has_tag(self, tags, policy=None):
        # RuleML should always be executed, regardless of the tags
        return True
    
    def get_relation_container(self):
        return self.relation_container
    
    def get_refs(self):
        """
        Return a list of all ConfML setting references that affect this
        implementation. May also return None if references are not relevant
        for the implementation.
        """
        refs = []
        relations = self.get_relations()
        for relation in relations:
            # get refs from relation return a tuple (left side refs, right side refs)
            # only the left side refs are the "input" refs  
            refs += relation.get_refs()
        # If the rules do not have any references return None to disable filter by refs 
        if refs == []: 
            refs = None
        return refs
    
    def get_relations(self):
        return self.relation_container.get_relations()

class RuleBuiltinsModule(object):
    pass

class RulemlRelationContainer(plugin.RelationContainer):
    """
    Relation container for RuleML rules.
    
    Basically this is a wrapper for rules.RelationContainer that adapts
    it to the interface of plugin.RelationContainer.
    """
    def __init__(self, configuration, source, rule_list, eval_globals):
        plugin.RelationContainer.__init__(self, configuration, source=source)
        self.configuration = configuration
        self.relation_container = rules.RelationContainerImpl()
        self.eval_globals = eval_globals
        self.context = None
        for rule in rule_list:
            self.relation_container.add_relation(rule)
    
    def execute(self, context=None):
        results = []
        
        # Create the autoconfig if not done already
        autoconfig = plugin.get_autoconfig(self.configuration)
        
        # Register relations etc. to the rule engine.
        # Due to unit test issues the relations are not registered
        # in the relations module, but only for the duration of
        # rule parsing and execution
        relations.register()
        try:
            # Using the configuration to pass the eval globals dict to the
            # eval expression. The configuration only contains the globals
            # dict for the duration of the rule execution, so hopefully this
            # shouldn't mess anything up
            self._set_builtin_eval_globals()
            context._eval_expression_globals_dict = self.eval_globals
            for i, rel in enumerate(self.relation_container):
                index = i + 1
                
                # Execute
                self._execute_relation_and_log_error(rel, self.source, index, context)
                
                # Collect execution result if supported
                if hasattr(rel, 'get_execution_result'):
                    result = rel.get_execution_result()
                    if isinstance(result, plugin.RelationExecutionResult):
                        result.source = self.source
                        result.index = index
                        results.append(result)
            
            del context._eval_expression_globals_dict
            
            if self.relation_container.has_errors():
                for error in self.relation_container.get_errors():
                    logging.getLogger('cone.ruleml_relation_container(%s)' % self.source).error(error)
            
            if self.context:
                self.context.results += results
                self.context.add_changed_refs(autoconfig.list_leaf_datas())
            return results
        finally:
            relations.unregister()
    
    def get_relation_count(self):
        return len(self.relation_container)
    
    def get_relations(self):
        return list(self.relation_container)
    
    def _set_builtin_eval_globals(self):
        """
        Add built-in attributes into the eval globals dictionary.
        """
                
        builtins = RuleBuiltinsModule()
        builtins.configuration = self.configuration
        
        self.eval_globals['ruleml'] = builtins

class RuleImplReaderBase(plugin.ReaderBase):
    NAMESPACE = None # Used as a base class, so should have no namespace
    FILE_EXTENSIONS = ['ruleml']
    
    def __init__(self, resource_ref, configuration):
        self.resource_ref = resource_ref
        self.configuration = configuration
        
    @classmethod
    def read_impl(cls, resource_ref, configuration, etree):
        reader = cls(resource_ref, configuration)
        
        # Register relations etc. to the rule engine.
        # Due to unit test issues the relations are not registered
        # in the relations module, but only for the duration of
        # rule parsing and execution
        relations.register()
        try:
            rules = reader.parse_rules(resource_ref, etree)
            eval_globals = reader.parse_eval_globals(etree)
            lineno = utils.etree.get_lineno(etree)
            
            # Create an ImplContainer to hold each rule as its own
            # RuleML implementation
            main_impl = plugin.ImplContainer(resource_ref, configuration)
            main_impl.lineno = lineno
            
            for rule in rules:
                relation_container = RulemlRelationContainer(
                    configuration   = configuration,
                    source          = "%s:%d" % (resource_ref, rule.lineno),
                    rule_list       = [rule],
                    eval_globals    = eval_globals)
            
                impl = RuleImpl(resource_ref, configuration, relation_container)
                impl.lineno = rule.lineno
                rule.implml = impl
                
                main_impl.append(impl)
        finally:
            relations.unregister()
        
        return main_impl
        
class RuleImplReader1(RuleImplReaderBase):
    NAMESPACE = 'http://www.s60.com/xml/ruleml/1'
    NAMESPACE_ID = 'ruleml1'
    ROOT_ELEMENT_NAME = 'ruleml'
    
    def __init__(self, resource_ref, configuration):
        RuleImplReaderBase.__init__(self, resource_ref, configuration)
    
    @classmethod
    def get_schema_data(cls):
        return pkg_resources.resource_string('legacyruleplugin', 'xsd/ruleml.xsd')
    
    def parse_rules(self, ref, etree):
        rules = []
        for elem in etree.getiterator("{%s}rule" % self.NAMESPACE):
            lineno = utils.etree.get_lineno(elem)
            for rule in relations.RelationFactory.get_relations(self.configuration, elem.text):
                rule.ref = ref
                rule.lineno = lineno
                rules.append(rule)
        return rules
    
    def parse_eval_globals(self, etree):
        return {}

class RuleImplReader2(RuleImplReaderBase):
    NAMESPACE = 'http://www.s60.com/xml/ruleml/2'
    NAMESPACE_ID = 'ruleml2'
    ROOT_ELEMENT_NAME = 'ruleml'
    
    def __init__(self, resource_ref, configuration):
        RuleImplReaderBase.__init__(self, resource_ref, configuration)
    
    @classmethod
    def get_schema_data(cls):
        return pkg_resources.resource_string('legacyruleplugin', 'xsd/ruleml2.xsd')
    
    def parse_rules(self, ref, etree):
        rules = []
        for elem in etree.getiterator("{%s}rule" % self.NAMESPACE):
            lineno = utils.etree.get_lineno(elem)
            for rule in relations.RelationFactory.get_relations(self.configuration, self._replace_eval_blocks(elem.text)):
                rule.ref = ref
                rule.lineno = lineno
                rules.append(rule)
        return rules
    
    def parse_eval_globals(self, etree):
        eval_globals = {}
        for elem in etree.getiterator("{%s}eval_globals" % self.NAMESPACE):
            text = ""
            if elem.get('file') != None:
                self._read_eval_globals_from_file(elem.get('file'), eval_globals)
            else:
                try: 
                    # Strip surrounding whitespace, otherwise there might be Python
                    # indentation errors
                    text = elem.text.strip()
                    exec(text, eval_globals)
                except Exception, e:
                    logging.getLogger('cone.ruleml(%s)' % self.resource_ref).warning('Failed to evaluate eval_globals block, exception: %s' % (e))
        return eval_globals
    
    def _read_eval_globals_from_file(self, relative_path, eval_globals):
        # Get the actual path (relative to the current implementation file)
        base_path = os.path.dirname(self.resource_ref)
        pyfile_path = os.path.normpath(os.path.join(base_path, relative_path)).replace('\\', '/')
        # Read the data and execute
        try:
            resource = None
            resource = self.configuration.get_resource(pyfile_path)
            text = resource.read()
            exec(text.replace('\r', ''), eval_globals)
        except Exception, e:
            logging.getLogger('cone.ruleml(%s)' % self.resource_ref).warning('Cannot import eval file: %s. Exception: %s' % (pyfile_path, e))
        finally:
            if resource is not None: resource.close()
        
    
    @classmethod
    def _replace_eval_blocks(cls, code):
        return utils.expand_delimited_tokens(
            string          = code,
            expander_func   = lambda ref, index: '__eval__ %r' % ref,
            delimiters      =('{%', '%}'))
