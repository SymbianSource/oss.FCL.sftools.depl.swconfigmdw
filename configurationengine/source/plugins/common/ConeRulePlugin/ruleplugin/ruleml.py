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
A plugin implementation for rule generation.
'''


import os
import sys
import logging
import shutil

import __init__
import re

from ruleplugin import relations
from cone.public import exceptions,plugin,utils,api,rules

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
        self.logger = logging.getLogger('cone.ruleml(%s)' % self.ref)
        self.relation_container = relation_container

    def list_output_files(self):
        """
        Return a list of output files as an array. 
        """
        return []
    
    def generate(self, context=None):
        self.logger.info("Generating rules from %s" % self.ref)
        relation_container = self.get_relation_container()
        relation_container.context = context
        return relation_container.execute()
    
    def has_tag(self, tags, policy=None):
        # RuleML should always be executed, regardless of the tags
        return True
    
    def get_relation_container(self):
        return self.relation_container

class RulemlRelationContainer(plugin.RelationContainer):
    """
    Relation container for RuleML rules.
    
    Basically this is a wrapper for rules.RelationContainer that adapts
    it to the interface of plugin.RelationContainer.
    """
    def __init__(self, configuration, source, rule_list, eval_globals):
        plugin.RelationContainer.__init__(self, configuration, source=source)
        self.logger = logging.getLogger('cone.ruleml_relation_container(%s)' % self.source)
        self.configuration = configuration
        self.relation_container = rules.RelationContainerImpl()
        self.eval_globals = eval_globals
        self.context = None
        for rule in rule_list:
            self.relation_container.add_relation(rule)
    
    def execute(self):
        results = []
        
        # Create the autoconfig if not done already
        plugin.get_autoconfig(self.configuration)
        
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
            self.configuration._eval_expression_globals_dict = self.eval_globals
            for i, rel in enumerate(self.relation_container):
                index = i + 1
                
                # Execute
                self._execute_relation_and_log_error(rel, self.source, index)
                
                # Collect execution result if supported
                if hasattr(rel, 'get_execution_result'):
                    result = rel.get_execution_result()
                    if isinstance(result, plugin.RelationExecutionResult):
                        result.source = self.source
                        result.index = index
                        results.append(result)
            
            del self.configuration._eval_expression_globals_dict
            
            if self.relation_container.has_errors():
                for error in self.relation_container.get_errors():
                    self.logger.error(error)
            
            if self.context:
                self.context.results += results
            return results
        finally:
            relations.unregister()
    
    def get_relation_count(self):
        return len(self.relation_container)
    
    def _set_builtin_eval_globals(self):
        """
        Add built-in attributes into the eval globals dictionary.
        """
        class RuleBuiltinsModule(object):
            pass
                
        builtins = RuleBuiltinsModule()
        builtins.configuration = self.configuration
        
        self.eval_globals['ruleml'] = builtins

class RuleImplReaderBase(plugin.ReaderBase):
    NAMESPACE = None # Used as a base class, so should have no namespace
    FILE_EXTENSIONS = ['ruleml']
    
    def __init__(self, resource_ref, configuration):
        self.resource_ref = resource_ref
        self.configuration = configuration
        self.logger = logging.getLogger('cone.ruleml(%s)' % self.resource_ref)
    
    @classmethod
    def read_impl(cls, resource_ref, configuration, etree):
        reader = cls(resource_ref, configuration)
        
        # Register relations etc. to the rule engine.
        # Due to unit test issues the relations are not registered
        # in the relations module, but only for the duration of
        # rule parsing and execution
        relations.register()
        try:
            rules = reader.parse_rules(etree)
            eval_globals = reader.parse_eval_globals(etree)
            
            relation_container = RulemlRelationContainer(
                configuration   = configuration,
                source          = resource_ref,
                rule_list       = rules,
                eval_globals    = eval_globals)
            
            impl = RuleImpl(resource_ref, configuration, relation_container)
        finally:
            relations.unregister()
        
        return impl
        
class RuleImplReader1(RuleImplReaderBase):
    NAMESPACE = 'http://www.s60.com/xml/ruleml/1'
    
    def __init__(self, resource_ref, configuration):
        RuleImplReaderBase.__init__(self, resource_ref, configuration)
    
    def parse_rules(self, etree):
        rules = []
        for elem in etree.getiterator("{%s}rule" % self.NAMESPACE):
            rules.extend(relations.RelationFactory.get_relations(self.configuration, elem.text))
        return rules
    
    def parse_eval_globals(self, etree):
        return {}

class RuleImplReader2(RuleImplReaderBase):
    NAMESPACE = 'http://www.s60.com/xml/ruleml/2'
    
    def __init__(self, resource_ref, configuration):
        RuleImplReaderBase.__init__(self, resource_ref, configuration)
    
    def parse_rules(self, etree):
        rules = []
        for elem in etree.getiterator("{%s}rule" % self.NAMESPACE):
            rules.extend(relations.RelationFactory.get_relations(self.configuration, self._replace_eval_blocks(elem.text)))
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
                    self.logger.warning('Failed to evaluate eval_globals block, exception: %s' % (e))
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
            self.logger.warning('Cannot import eval file: %s. Exception: %s' % (pyfile_path, e))
        finally:
            if resource is not None: resource.close()
        
    
    @classmethod
    def _replace_eval_blocks(cls, code):
        return utils.expand_delimited_tokens(
            string          = code,
            expander_func   = lambda ref, index: '__eval__ %r' % ref,
            delimiters      =('{%', '%}'))
