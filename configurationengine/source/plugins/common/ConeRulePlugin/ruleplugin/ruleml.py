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
import logging
import pkg_resources

from ruleplugin import relations
from cone.public import plugin,utils,rules

class RuleImpl(plugin.ImplBase):
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
    
    def get_target_refs(self):
        """
        Return a list of all ConfML setting references that are affected by this
        implementation. May also return None if references are not relevant
        for the implementation.
        """
        refs = []
        relations = self.get_relations()
        for relation in relations:
            refs += relation.get_set_refs()
        return refs

    def get_outputs(self):
        """
        Return a list of GenerationOutput objets as a list. 
        """
        outputs = []
        phase = None 
        if self.generation_context: phase = self.generation_context.phase
        for rel in self.get_relations():
            outrefs = rel.get_set_refs()
            for ref in outrefs:
                outputs.append(plugin.GenerationOutput(ref,rel,type='ref', phase=phase))
        return outputs
    
    def generate(self, context=None):
        logging.getLogger('cone.ruleml(%s)' % self.ref).info("Generating rules from %s" % self.ref)
        relation_container = self.get_relation_container()
        relation_container.context = context
        return relation_container.execute(context)
    
    def get_relation_container(self):
        return self.relation_container

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
        if context: self.context = context
         
        # Create the autoconfig if not done already
        autoconfig = plugin.get_autoconfig(self.configuration)
        
        # Using the configuration to pass the eval globals dict to the
        # eval expression. The configuration only contains the globals
        # dict for the duration of the rule execution, so hopefully this
        # shouldn't mess anything up
        self._set_builtin_eval_globals()
        self.context._eval_expression_globals_dict = self.eval_globals
        for i, rel in enumerate(self.relation_container):
            index = i + 1
            # Execute
            self._execute_relation_and_log_error(rel, self.source, index, context)
            
        del self.context._eval_expression_globals_dict
        
        if self.relation_container.has_errors():
            for error in self.relation_container.get_errors():
                logging.getLogger('cone.ruleml_relation_container(%s)' % self.source).error(error)
        
        if self.context:
            self.context.results += results
        return results
    
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
        builtins.context       = self.context
        
        self.eval_globals['ruleml'] = builtins

class RuleImplReader(plugin.ReaderBase):
    NAMESPACE = 'http://www.s60.com/xml/ruleml/3'
    NAMESPACE_ID = 'ruleml3'
    ROOT_ELEMENT_NAME = 'ruleml'
    FILE_EXTENSIONS = ['ruleml']
    
    def __init__(self, resource_ref, configuration):
        self.resource_ref = resource_ref
        self.configuration = configuration
    
    @classmethod
    def read_impl(cls, resource_ref, configuration, etree):
        reader = cls(resource_ref, configuration)
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
        return main_impl
    
    @classmethod
    def get_schema_data(cls):
        return pkg_resources.resource_string('ruleplugin', 'xsd/ruleml3.xsd')
    
    def parse_rules(self, ref, etree):
        rules = []
        for elem in etree.getiterator("{%s}rule" % self.NAMESPACE):
            lineno = utils.etree.get_lineno(elem)
            rule_str = self._replace_eval_blocks(elem.text or '')
            rels = relations.RelationFactory.get_relations(rule_str) or []
            for rule in rels:
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
