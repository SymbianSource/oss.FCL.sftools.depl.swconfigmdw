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
implementation for ruleml relations.
'''
import os
import StringIO
import logging
import operator as ops
import re
import sys, traceback

log = logging.getLogger('cone.ruleplugin.relations')

from cone.public import api, rules, utils, exceptions, plugin

class RelationFactory(api.FactoryBase):
    @ classmethod
    def get_relation_by_name(cls, relation_name):
        """
        Get the class name by file extension.
        """
        try:
            return rules.RELATIONS.get(relation_name)
        except KeyError:
            raise exceptions.NotSupportedException("No Relation class found for name %s" % relation_name)

    @ classmethod
    def get_relations(cls, relation):
        try:
            relations = []
            (left_expression,relation_name,right_expression) = parse_rule(relation)
            relation = cls.get_relation_by_name(relation_name)(left_expression, right_expression)
            relations.append(relation)
            propagated_relations = cls.get_relations(right_expression)
            if propagated_relations:
                for relation in propagated_relations:
                    relations.append(relation)
            return relations
        except exceptions.ParseError:
            return None
    

class ConfigurationBaseRelation(rules.BaseRelation):
    def __init__(self, left, right):
        super(ConfigurationBaseRelation, self).__init__(None, left, right)
        self.context = None

class RequireRelation(ConfigurationBaseRelation):
    KEY = 'requires'
    relation_name = 'requires'
    def __init__(self, left, right):
        super(RequireRelation, self).__init__(left, right)

class ConfigureRelation(ConfigurationBaseRelation):
    KEY = 'configures'
    relation_name = 'configures'
    def __init__(self, left, right):
        super(ConfigureRelation, self).__init__(left, right)
        
        # A plugin.RelationExecutionResult object is stored here
        self._execution_result = None
        
    
    def execute(self, context):
        self._execution_result = None
        exec_results = []
        
        result = rules.BaseRelation.execute(self, context)
        
        if len(exec_results) > 0:
            # There should be only one ConfigureExpression inside a ConfigureRelation
            if len(exec_results) > 1:
                log.warning("Execution of ConfigureRelation returned more than one result, ignoring all except the first")
            self._execution_result = exec_results[0]
        
        return result
    
    def get_execution_result(self):
        """
        Return the execution result from the most recent call to execute().
        """
        return self._execution_result

def handle_configure(self, left, right):
    if left and right:
        return True
    elif not left:
        return True
    return False

def handle_filenamejoin(self, left, right):
    def extract_dirname(path):
        """Extract directory name (will always contain a trailing slash or backslash)"""
        pos = max(path.rfind('/'), path.rfind('\\'))
        if pos == -1:   return path + '/'
        else:           return path[:pos + 1]
    
    def extract_filename(path):
        pos = max(path.rfind('/'), path.rfind('\\'))
        if pos == -1:   return path
        else:           return path[pos + 1:]
    
    return extract_dirname(left) + extract_filename(right)


class ConfigureExpression(rules.TwoOperatorExpression):
    PRECEDENCE = rules.PRECEDENCES['RELATION_OPERATORS']
    KEY = 'configures'
    OP = handle_configure

    def eval(self, context, **kwargs):
        input_refs = []
        affected_refs = []
        
        # Evaluate the left-hand side expression
        evaluated_left = self.left.eval(context, **kwargs)
        if evaluated_left:
            # If left evaluated to True, evaluate the right-hand side
            self.value = self.right.eval(context, **kwargs)
        else:
            self.value = True
        
        if not self.value:
            left_keys = []
            for ref in self.ast.extract_refs(str(self.left)):
                for key in context.get_keys(ref):
                    left_keys.append(key)
            for key in left_keys:
                self.ast.add_error(key, { 'error_string' : 'CONFIGURES right side value is "False"',
                                          'left_key' : key,
                                          'rule' : self.ast.expression
                                          })
        return self.value

class EvalExpression(rules.OneParamExpression):
    expression = "__eval__"
    PRECEDENCE = rules.PRECEDENCES['PREFIX_OPERATORS']
    KEY = '__eval__'
    
    def __init__(self, ast, expression): 
        super(EvalExpression, self).__init__(ast, expression)
        self.expression = expression
        self._str_to_eval = eval(expression.expression)
        #self.default_view = default_view
    
    def extract_refs(self):
        result = []
        result.extend(utils.extract_delimited_tokens(self._str_to_eval, delimiters=('${', '}')))
        result.extend(utils.extract_delimited_tokens(self._str_to_eval, delimiters=('@{', '}')))
        return result
    
    def get_refs(self):
        return self.extract_refs()
    
    def eval(self, context, **kwargs):
        # Using the configuration to pass the eval globals dictionary to here,
        # since there isn't any easy way to do this more elegantly
        globals_and_locals = {}
        if hasattr(context, '_eval_expression_globals_dict'):
            globals_and_locals = context._eval_expression_globals_dict
        
        str_to_eval = self._str_to_eval
        
        def expand_feature_ref(ref, index):
            var_name = "__fea_%05d" % index
            globals_and_locals[var_name] = context.configuration.get_default_view().get_feature(ref)
            return var_name

        def expand_value_ref(ref, index):
            var_name = "__feaval_%05d" % index
            globals_and_locals[var_name] = context.configuration.get_default_view().get_feature(ref).get_value()
            return var_name
        
        str_to_eval = utils.expand_delimited_tokens(str_to_eval, expand_feature_ref, delimiters=('@{', '}'))
        str_to_eval = utils.expand_delimited_tokens(str_to_eval, expand_value_ref, delimiters=('${', '}'))
        
        # Strip leading and trailing whitespace to avoid indentation problems
        str_to_eval = str_to_eval.strip()
        
        ret = None
        
        try:
            ret = eval(str_to_eval, globals_and_locals)
            return ret
        except SyntaxError, e:
            logging.getLogger('cone.ruleml').warning("Invalid syntax in eval: %s" % (str_to_eval) )
            self.ast.add_error(self.expression, { 'error_string' : 'Invalid syntax in eval', 'str_to_eval' : str_to_eval, 'rule' : self.ast.expression })
        except Exception, e:
            logging.getLogger('cone.ruleml').warning("Execution failed for eval: %s %s: %s" % (str_to_eval, type(e), e) )
            self.ast.add_error(self.expression, { 'error_string' : 'Execution failed for eval', 'str_to_eval' : str_to_eval, 'rule' : self.ast.expression })


class FilenamejoinExpression(rules.TwoOperatorExpression):
    expression = "filenamejoin"
    PRECEDENCE = rules.PRECEDENCES['ADDSUB_OPERATORS']
    KEY = 'filenamejoin'
    OP = handle_filenamejoin
    
# Register relations and operators to rules
rules.RELATIONS[RequireRelation.KEY] = RequireRelation
rules.RELATIONS[ConfigureRelation.KEY] = ConfigureRelation
rules.OPERATORS[FilenamejoinExpression.KEY] = FilenamejoinExpression
rules.OPERATORS[EvalExpression.KEY] = EvalExpression
rules.OPERATORS[ConfigureExpression.KEY] = ConfigureExpression

def parse_rule(rulestring):
    """
    Divide the given rule string into (left side, relation, right side) components. 
    @return: Triple (left side, relation, right side)
    """
    left_expression = ''
    relation_name = None
    right_expression = ''
    for token in rules.get_tokens(rulestring):
        if relation_name == None:
            if token in rules.RELATIONS.keys():
                relation_name = token
            else:
                left_expression += ' ' + token
        else:
            right_expression += ' ' + token
    
    if relation_name == None:
        raise exceptions.ParseError('invalid rule definition %s' % rulestring)
    
    return (left_expression,relation_name,right_expression)

