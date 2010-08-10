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

from legacyruleplugin import rules
from cone.public import api, utils, exceptions, plugin

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
    def get_relations(cls, configuration, relation):
        try:
            relations = []
            (left_expression,relation_name,right_expression) = parse_rule(relation)
            relation = cls.get_relation_by_name(relation_name)(configuration, left_expression, right_expression)
            relations.append(relation)
            propagated_relations = cls.get_relations(configuration, right_expression)
            if propagated_relations:
                for relation in propagated_relations:
                    relations.append(relation)
            return relations
        except exceptions.ParseError:
            return None
    

class ConfigurationContext(rules.DefaultContext):
    
    def __init__(self, data):
        rules.DefaultContext.__init__(self, data)
        
        # Callback called with the setting reference when a setting is dereferenced
        # as a terminal expression
        self.ref_terminal_callback = None
        
        # Callback called with the setting reference when a setting is dereferenced
        # inside an EvalExpression
        self.ref_eval_callback = None
        
        # Callback called with the setting reference when the value of a setting
        # is set inside a SetExpression
        self.ref_set_callback = None
        
    def handle_terminal(self, expression):
        try:
            value = self.data.get_default_view().get_feature(expression).get_value()
            
            # Got a valid ref, call the callback
            if self.ref_terminal_callback:
                self.ref_terminal_callback(expression)
            
            return value
        except exceptions.NotFound,e:
            """ return the expression itself if it is not a fearef """
            #print "handle_terminal constant %s" % (expression)
            try:
                return eval(expression)
            except (NameError,SyntaxError), e:
                return expression

    def eval(self, ast, expression, value):
        #print "expression %s = %s" % (expression,value)
        pass
        
class ConfigurationBaseRelation(rules.BaseRelation):
    def __init__(self, data, left, right):
        self.context = ConfigurationContext(data)
        super(ConfigurationBaseRelation, self).__init__(data, left, right)

class RequireRelation(ConfigurationBaseRelation):
    KEY = 'requires'
    def __init__(self, data, left, right):
        super(RequireRelation, self).__init__(data, left, right)
        self.context = ConfigurationContext(data)

class ConfigureRelation(ConfigurationBaseRelation):
    KEY = 'configures'
    def __init__(self, data, left, right):
        self.context = ConfigurationContext(data)
        super(ConfigureRelation, self).__init__(data, left, right)
        
        # A plugin.RelationExecutionResult object is stored here
        self._execution_result = None
        
    
    def execute(self, context=None):
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

def handle_set(self, left, right):
    left.set_value(right)

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

def handle_plus(self, left, right):
    return left + right

def handle_minus(self, left, right):
    return left - right

def handle_multiply(self, left, right):
    return left * right

def handle_divide(self, left, right):
    return left / right

class ConfigureExpression(rules.TwoOperatorExpression):
    PRECEDENCE = rules.PRECEDENCES['RELATION_OPERATORS']
    KEY = 'configures'
    OP = handle_configure

    def eval(self, context, **kwargs):
        input_refs = []
        affected_refs = []
        
        # Evaluate the left-hand side expression, catching refs for the result
        try:
            context.ref_terminal_callback = lambda ref: input_refs.append(ref)
            context.ref_eval_callback = lambda ref: input_refs.append(ref)
            evaluated_left = self.left.eval(context, **kwargs)
        finally:
            context.ref_terminal_callback = None
            context.ref_eval_callback = None
        
        if evaluated_left:
            # If left evaluated to True, evaluate the right-hand side and
            # catch refs from SetExpression evaluations
            try:
                context.ref_set_callback = lambda ref: affected_refs.append(ref)
                self.value = self.right.eval(context, **kwargs)
            finally:
                context.ref_set_callback = None
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

class MultiplyExpression(rules.TwoOperatorExpression):
    expression = "multiply_operation"
    PRECEDENCE = rules.PRECEDENCES['MULDIV_OPERATORS']
    KEY= '*'
    OP = handle_multiply

class DivideExpression(rules.TwoOperatorExpression):
    expression = "divide_operation"
    PRECEDENCE = rules.PRECEDENCES['MULDIV_OPERATORS']
    KEY= '/'
    OP = handle_divide

class PlusExpression(rules.TwoOperatorExpression):
    expression = "plus_operation"
    PRECEDENCE = rules.PRECEDENCES['ADDSUB_OPERATORS']
    KEY= '+'
    OP = handle_plus

class MinusExpression(rules.TwoOperatorExpression):
    expression = "minus_operation"
    PRECEDENCE = rules.PRECEDENCES['ADDSUB_OPERATORS']
    KEY= '-'
    OP = handle_minus

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
            if context.ref_eval_callback:
                context.ref_eval_callback(ref)
            return var_name
        def expand_value_ref(ref, index):
            var_name = "__feaval_%05d" % index
            globals_and_locals[var_name] = context.configuration.get_default_view().get_feature(ref).get_value()
            if context.ref_eval_callback:
                context.ref_eval_callback(ref)
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

rules.OPERATORS[EvalExpression.KEY] = EvalExpression

class FilenamejoinExpression(rules.TwoOperatorExpression):
    expression = "filenamejoin"
    PRECEDENCE = rules.PRECEDENCES['ADDSUB_OPERATORS']
    KEY = 'filenamejoin'
    OP = handle_filenamejoin
    
rules.OPERATORS[FilenamejoinExpression.KEY] = FilenamejoinExpression
    
class SetExpression(rules.TwoOperatorExpression):
    PRECEDENCE = rules.PRECEDENCES['SET_OPERATORS']
    KEY= '='
    OP = handle_set

#    def eval(self, context):
#        try:
#            variable = context.configuration.get_default_view().get_feature(self.left.expression)
#            value = self.right.eval(context)
#            variable.set_value(value)
#            logging.getLogger('cone.ruleml').info("Set %r = %r from %r" % (self.left.expression, value, self.right.expression) )
#            if context.ref_set_callback:
#                context.ref_set_callback(self.left.expression)
#            return True
#        except exceptions.NotFound,e:
#            self.ast.add_error(self.left.expression, { 'error_string' : 'Setting value failed, because of %s' % e,
#                               'left_key' : self.left.expression,
#                               'rule' : self.ast.expression})
#            return False

    def eval(self, context, **kwargs):
        
        value = self.right.eval(context, **kwargs)
        ref = self.left.get_ref()
        context.set(ref, value, **kwargs)
        return True

_relations_and_operators_backup = None

def register():
    """
    Register the relations and operators to ConE rules.
    """
    global _relations_and_operators_backup
    if _relations_and_operators_backup is None:
        # Create the backup copies of the dictionaries
        rels_backup = rules.RELATIONS.copy()
        ops_backup = rules.OPERATORS.copy()
        assert rels_backup is not rules.RELATIONS
        assert ops_backup is not rules.OPERATORS
        _relations_and_operators_backup = (rels_backup, ops_backup)
        
        # Register relations and operators to rules
        rules.RELATIONS[RequireRelation.KEY] = RequireRelation
        rules.RELATIONS[ConfigureRelation.KEY] = ConfigureRelation
        rules.OPERATORS[ConfigureExpression.KEY] = ConfigureExpression
        rules.OPERATORS[PlusExpression.KEY] = PlusExpression
        rules.OPERATORS[SetExpression.KEY] = SetExpression
        rules.OPERATORS[MinusExpression.KEY] = MinusExpression
        rules.OPERATORS[MultiplyExpression.KEY] = MultiplyExpression
        rules.OPERATORS[DivideExpression.KEY] = DivideExpression

def unregister():
    """
    Undo the changes made by a call to register().
    """
    global _relations_and_operators_backup
    if _relations_and_operators_backup is not None:
        rules.RELATIONS = _relations_and_operators_backup[0]
        rules.OPERATORS = _relations_and_operators_backup[1]
        _relations_and_operators_backup = None

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

