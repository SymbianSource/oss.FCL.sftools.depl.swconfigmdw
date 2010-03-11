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

import operator as ops
import logging
import tokenize
from token import ENDMARKER, NAME, ERRORTOKEN
import StringIO

from cone.public import container

RELATIONS = {}

def abstract():
    import inspect
    caller = inspect.getouterframes(inspect.currentframe())[1][3]
    raise NotImplementedError(caller + ' needs to be implemented')

def get_tokens(tokenstr):
    result = []
    tokens = []
    tokenstr = tokenstr.replace('\r', '')
    name_buffer = [] # Temp buffer for reading name tokens
    last_epos = None
    for toknum, tokval, spos, epos, _  in tokenize.generate_tokens(StringIO.StringIO(unicode(tokenstr)).readline):
        #print "toknum: %r, tokval: %r, spos: %r, epos: %r" % (toknum, tokval, spos, epos)
        val = tokval.strip('\r\n\t ')
        
        if toknum == ENDMARKER and name_buffer:
            tokens.append(''.join(name_buffer))
        
        # Ignore whitespace (this ignores also the end marker,
        # since its value is empty)
        if val == '': continue
        
        # Put NAME, and ERRORTOKEN tokens through the temp
        # buffer
        if toknum in (NAME, ERRORTOKEN):
            # If this and the previous token in the temp buffer are not adjacent,
            # they belong to separate tokens
            if name_buffer and spos[1] != last_epos[1]:
                tokens.append(''.join(name_buffer))
                name_buffer = []
            
            name_buffer.append(val)
            last_epos = epos
        # Other tokens can just go directly to the token list
        else:
            if name_buffer:
                tokens.append(''.join(name_buffer))
                name_buffer = []
            tokens.append(val)
    
    while len(tokens) > 0:
        val = tokens.pop(0)
        # Join the refs with dot in between them to make them dotted refs
        if val == '.':
            newval = ".".join([result.pop(),tokens.pop(0)])
            result.append( newval )
        else:
            result.append( val )

    return result

class RelationException(Exception):
    pass

#### The containers are here ####


class RelationBase(object):
    """
    RelationBase defines a base class for all named relations that can be applied between objects. 
    e.g. Relation depends, that can be applied in Rule
    """
    relation_name = "RelationBase"
    def __init__(self, data, left, right):
        self.description = ""
        self.data = data or container.DataContainer()
        self.left = left
        self.right = right

    def __str__(self):
        """
        @return: A string presentation of the relation object
        """
        return "%s %s %s" % (self.left,self.relation_name,self.right)

    def get_name(self):
        """
        @return: The relation name.
        """
        return self.relation_name

    def get_description(self):
        """
        @return: a possible description of the relation.
        """
        return self.description
        
    def execute(self):
        """
        Execute the relation object.
        """
        pass


class RelationContainer(RelationBase, list):
    """
    This class provides the RelationContainer interface for collecting
    relation sets into one place which can be executed through the container.
    """
    def __init__(self, data=None):
        super(RelationContainer, self).__init__(data, 'LContainer', 'RContainer')
        self.value_list = list()

    def append(self, value):
        self.value_list.append(value)

    def __iter__(self):
        return self.value_list.__iter__()

    def __len__(self):
        return len(self.value_list)

    def __or__(self, other):
        """
        This function adds two RelationContainers to each other and removes
        duplicates from the result.
        The modification is inplace and the returned value is called object.
        """
        self.value_list = set(self.value_list) | set(other.value_list)
        return self

    def __unicode__(self):
        if self:
            ret = ''
            for value in self:
                ret += unicode(value)
        else:
            ret = 'No relations'
        return ret

    def find_relations(self, refs): abstract()
    def add_relation(self, relation): abstract()
    def has_errors(self): abstract()

class RelationContainerImpl(RelationContainer):
    """ Base implementation for RelationContainer to use in ConE rules
    """
    def execute(self):
        ret = True
        i = 0
        for relation in self:
            i += 1
            r = relation.execute()
            ret = ret and r
        return ret

    def find_relations(self, refs):
        relations = []
        for ref in refs:
            for relation in self:
                if relation.has_ref(ref):
                    relations.append(relation)
        return relations

    def add_relation(self, relation):
        self.append(relation)

    def has_ref(self, refs):
        for ref in refs:
            for relation in self:
                if relation.has_ref(ref):
                    return True
        return False

    def has_errors(self):
        for relation in self:
            if relation.has_errors():
                return True
        return False
            
    def get_errors(self):
        errors = []
        for relation in self:
            errors += relation.get_errors()
        return errors

#### The relations are here ####

class BaseRelation(RelationBase):
    """ BaseRelation implements the basic evaluation logic for relations
    This class abstract and should be extended for concrete implementation of
    relation type.

    Subclasses need to set their own context in their constructor before this
    class's constructor is called if custom context is needed. If context not
    set then DefaultContext is used.
    """
    KEY = 'base_relation'

    def __init__(self, data, left, right):
        # Context needs to be overridden for special purposes
        try:
            self.__getattribute__('context')
        except AttributeError:
            self.context = DefaultContext(data)

        left = self.expand_rule_elements(left)
        right = self.expand_rule_elements(right)
        super(BaseRelation, self).__init__(data, left, right)
        self.interpreter = ASTInterpreter(context=self.context)

    def execute(self):
        """
        @return Returns error dictionary

        In the client code proper way to check if the rule applies:
        info = relation.execute()
        if not info.has_errors():
        else: HANDLE ERRORS
        """
        # logger.debug("Interpreter context %s" % self.interpreter.context)
        self.interpreter.create_ast('%s %s %s' % (self.left, self.KEY, self.right))
        ret = self.interpreter.eval()
        return ret

    def get_keys(self):
        """ Returns the references from this relation.
        """
        refs = ASTInterpreter.extract_refs(self.left)
        refs += ASTInterpreter.extract_refs(self.right)
        return refs

    def has_ref(self, ref):
        """ Returns if the 'ref' is included in this relation
        """
        return ref in self.get_keys()

    def has_errors(self):
        return bool(self.interpreter.errors)

    def get_refs(self):
        return (ASTInterpreter.extract_refs(self.left), ASTInterpreter.extract_refs(self.right))

    def _eval_rside_value(self, value): abstract()
    def _compare_value(self, value): abstract()

    def extract_erroneus_features_with_values(self):
        """
        Extract references who have errors.

        Returns dictionary { 'reference' : 'value' }
        """
        data_dict = {}
        for ref in ASTInterpreter.extract_refs(self.right):
            value = self.data.get_feature(ref)
            if self._compare_value(value):
                data_dict[ref] = value
            elif value == None:
                data_dict[ref] = None
        return data_dict

    def get_errors(self):
        return self.interpreter.errors

    def expand_rule_elements(self, rule):
        """ Expans rule elements base on the reference.
        Context is used for fetching the child elements for parent references
        which uses asterisk identifier for selecting all child features: 
        'parent_feature.*' -> 'child_fea_1 and child_fea_2'.
        """
        tokens = get_tokens(rule) # [token for token in rule.split()]

        expanded_rule = ""
        for token in tokens:
            if token.endswith('.*'):
                index = token.index('.*')
                parent_ref = token[:index]
                children = self.context.get_children_for_reference(parent_ref)
                expanded_element = ' and '.join([child.reference for child in children])
                if expanded_rule:
                    expanded_rule = '%s and %s' % (expanded_rule, expanded_element.rstrip())
                else:
                    expanded_rule = expanded_element.rstrip()
            elif token.lower() in OPERATORS:
                expanded_rule += ' %s ' % token
            else:
                if expanded_rule:
                    expanded_rule += '%s'% token
                else:
                    expanded_rule = token
        return expanded_rule.strip()

class RequireRelation(BaseRelation):
    KEY = 'requires'
RELATIONS[RequireRelation.KEY] = RequireRelation

class ExcludesRelation(BaseRelation):
    KEY = 'excludes'

RELATIONS['excludes'] = ExcludesRelation

################################
# Abstract syntax tree builder #
################################

def nor(expression, a, b):
    return not ops.or_(a, b)

def nand(expression, a, b):
    return not ops.and_(a, b)

def truth_and(expression, a, b):
    return ops.truth(a) and ops.truth(b)

class DefaultContext(object):
    """ DefaultContext implements ConE specific context for handling rules
    """
    def __init__(self, data):
        self.data = data

    def eval(self, ast, expression, value):
        pass

    def get_keys(self, refs):
        return ASTInterpreter.extract_refs(refs)

    def get_children_for_reference(self, reference):
        # implement ConE specific children expansion
        pass

    def handle_terminal(self, expression):
        try:
            return int(expression)
        except:
            return expression

PRECEDENCES = {
    'PREFIX_OPERATORS' : 10,
    'MULDIV_OPERATORS' : 8,
    'ADDSUB_OPERATORS' : 7,
    'SHIFT_OPERATORS' : 6,
    'BITWISE_OPERATORS' : 5,
    'COMPARISON_OPERATORS' : 4,
    'SET_OPERATORS' : 3,
    'BOOLEAN_OPERATORS' : 2, 
    'RELATION_OPERATORS' : 1,
    'NOT_DEFINED' : 0
}

class Expression(object):
    PRECEDENCE = PRECEDENCES['NOT_DEFINED']
    KEY = 'base_expression'

    def __init__(self, ast):
        self.ast = ast
        self.value = None

    def get_title(self):
        return self.KEY

    def eval(self, context): pass

class OneParamExpression(Expression):
    PARAM_COUNT = 1
    def __init__(self, ast, expression):
        super(OneParamExpression, self).__init__(ast)
        self.expression = expression

    def __unicode__(self):
        return u'%s %s' % (self.KEY, self.expression)

    def eval(self, context):
        self.value = self.OP(self.expression.eval(context))
        context.eval(self.ast, self, self.value)
        return self.value

class TwoOperatorExpression(Expression):
    PARAM_COUNT = 2
    OP = None
    EVAL_AS_BOOLS = True

    def __init__(self, ast, left, right):
        super(TwoOperatorExpression, self).__init__(ast)
        self.left = left
        self.right = right

    def __unicode__(self):
        return u'%s %s %s' % (self.left, self.KEY, self.right)

    def eval(self, context):
        self.value = self.OP(self.left.eval(context), self.right.eval(context))
        context.eval(self.ast, self, self.value)
        return self.value

class TwoOperatorBooleanExpression(TwoOperatorExpression):
    def eval(self, context):
        self.value = self.OP(bool(self.left.eval(context)), bool(self.right.eval(context)))
        context.eval(self.ast, self, self.value)
        return self.value         

class TerminalExpression(Expression):
    KEY = 'terminal'

    def __init__(self, ast, expression):
        super(TerminalExpression, self).__init__(ast)
        self.expression = expression

    def eval(self, context):
        """ Use context to eval the value
        Expression on TerminalExpression is feature reference or value
        context should handle the reference conversion to correct value
        """
        self.value = context.handle_terminal(self.expression)
        return self.value

    def __unicode__(self):
        return self.expression
    
    def __repr__(self):
        return self.expression

class NegExpression(OneParamExpression):
    PRECEDENCE = PRECEDENCES['PREFIX_OPERATORS']
    KEY= '-'
    OP = ops.neg

class AndExpression(TwoOperatorBooleanExpression):
    PRECEDENCE = PRECEDENCES['BOOLEAN_OPERATORS']
    KEY= 'and'
    OP = truth_and

class NandExpression(TwoOperatorBooleanExpression):
    PRECEDENCE = PRECEDENCES['BOOLEAN_OPERATORS']
    KEY = 'nand'
    OP = nand

class OrExpression(TwoOperatorBooleanExpression):
    PRECEDENCE = PRECEDENCES['BOOLEAN_OPERATORS']
    KEY = 'or'
    OP = ops.or_

class XorExpression(TwoOperatorBooleanExpression):
    PRECEDENCE = PRECEDENCES['BOOLEAN_OPERATORS']
    KEY = 'xor'
    OP = ops.xor

class NorExpression(TwoOperatorBooleanExpression):
    PRECEDENCE = PRECEDENCES['BOOLEAN_OPERATORS']
    KEY = 'nor'
    OP = nor

class EqualExpression(TwoOperatorExpression):
    PRECEDENCE = PRECEDENCES['COMPARISON_OPERATORS']
    KEY = '=='
    OP = ops.eq

class NotEqualExpression(TwoOperatorExpression):
    PRECEDENCE = PRECEDENCES['COMPARISON_OPERATORS']
    KEY = '!='
    OP = ops.ne

class LessThanExpression(TwoOperatorExpression):
    PRECEDENCE = PRECEDENCES['COMPARISON_OPERATORS']
    KEY = '<'
    OP = ops.lt

class GreaterThanExpression(TwoOperatorExpression):
    PRECEDENCE = PRECEDENCES['COMPARISON_OPERATORS']
    KEY = '>'
    OP = ops.gt

class LessThanEqualExpression(TwoOperatorExpression):
    PRECEDENCE = PRECEDENCES['COMPARISON_OPERATORS']
    KEY = '<='
    OP = ops.le

class GreaterThanEqualExpression(TwoOperatorExpression):
    PRECEDENCE = PRECEDENCES['COMPARISON_OPERATORS']
    KEY = '>='
    OP = ops.ge


def handle_require(expression, left, right):
    if left and right:
        return True
    elif not left:
        return True
    return False

class RequireExpression(TwoOperatorExpression):
    PRECEDENCE = PRECEDENCES['RELATION_OPERATORS']
    KEY = 'requires'
    OP = handle_require

    def eval(self, context):
        super(RequireExpression, self).eval(context)
        if not self.value:
            left_keys = []
            for ref in self.ast.extract_refs(unicode(self.left)):
                for key in context.get_keys(ref):
                    left_keys.append(key)

            for key in left_keys:
                self.ast.add_error(key, { 'error_string' : 'REQUIRES right side value is "False"',
                                          'left_key' : key,
                                          'rule' : self.ast.expression
                                          })
        return self.value

def handle_exclude(expression, left, right):
    if left and not right:
        return True
    elif not left:
        return True
    return False

class ExcludeExpression(TwoOperatorExpression):
    PRECEDENCE = PRECEDENCES['RELATION_OPERATORS']
    KEY = 'excludes'
    OP = handle_exclude

    def eval(self, context):
        super(ExcludeExpression, self).eval(context)
        if not self.value:
            left_keys = []
            for ref in self.ast.extract_refs(unicode(self.left)):
                for key in context.get_keys(ref):
                    left_keys.append(key)
                    
            for key in left_keys:
                self.ast.add_error(key, { 'error_string' : 'EXCLUDE right side value is "True"',
                                          'left_key' : key,
                                          'rule' : self.ast.expression
                                          })
        return self.value


class NotExpression(OneParamExpression):
    PRECEDENCE = PRECEDENCES['PREFIX_OPERATORS']
    KEY = 'not'
    OP = ops.not_

class TruthExpression(OneParamExpression):
    PRECEDENCE = PRECEDENCES['PREFIX_OPERATORS']
    KEY = 'truth'
    OP = ops.truth

LEFT_PARENTHESIS = '('
RIGHT_PARENTHESIS = ')'
class SimpleCondition(EqualExpression):
    """
    A simple condition object that can refer to a model object and evaluate if the value matches  
    """
    def __init__(self, left, right):
        lterm = TerminalExpression(None, left)
        rterm = TerminalExpression(None, right)
        EqualExpression.__init__(self, None, lterm, rterm)


# in format KEY : OPERATOR CLASS
OPERATORS = {
    'and' : AndExpression,
    'nand' : NandExpression,
    'or' : OrExpression,
    'xor' : XorExpression,
    'nor' : NorExpression,
    'not' : NotExpression,
    'truth' : TruthExpression,
    '==' : EqualExpression,
    '!=' : NotEqualExpression,
    '<' : LessThanExpression,
    '>' : GreaterThanExpression,
    '<=' : LessThanEqualExpression,
    '>=' : GreaterThanEqualExpression,
    'requires' : RequireExpression,
    'excludes' : ExcludeExpression,
    '-' : NegExpression
    }

def add_operator(key, operator_class=None, baseclass=RequireExpression):
    """
    Add new operator key and operator class.
    If operator class isn't provided the baseclass parameter is used as
    operator base. The baseclass parameter is RequireExpression by default
    which has success condition left_rule=True and right_rule=True
    
    """
    OPERATORS[key] = operator_class or create_new_class(key, baseclass)

def create_new_class(key, baseclass):
    ns = baseclass.__dict__.copy()
    ns['KEY'] = key
    key_pieces = key.split('_')
    class_prefix = ''.join([key_piece.capitalize() for key_piece in key_pieces])
    new_class = type(class_prefix + 'Expression', (baseclass,), ns)
    return new_class

class ParseException(Exception): pass

class ASTInterpreter(object):
    def __init__(self, infix_expression=None, context=None):
        """ Takes infix expression as string """
        self.context = context or DefaultContext(None)
        # logger.debug("AST init context: %s" % self.context)
        self._init_locals(infix_expression)
        if infix_expression:
            self.create_ast()

    def _init_locals(self, infix_expression):
        # The result value of full eval of the parse_tree
        self.value = None
        self.warnings = {}
        self.errors = {}
        self.postfix_array = []
        self.parse_tree = []
        self.expression = infix_expression

    def __unicode__(self):
        s = ''
        for expr in self.parse_tree:
            s += unicode(expr)
        return s

    def add_error(self, key, error_dict):
        if self.errors.has_key(key):
            self.errors[key].append(error_dict)
        else:
            self.errors[key] = [error_dict]

    def create_ast(self, infix_expression=None):
        if infix_expression:
            self._init_locals(infix_expression)
        self._infix_to_postfix()
        self._create_parse_tree()
        return self.parse_tree

    def _infix_to_postfix(self):
        """
        Shunting yard algorithm used to convert infix presentation to postfix.
        """
        if not self.expression:
            raise ParseException('Expression is None')
        tokens = get_tokens(self.expression) # [token for token in self.expression.split()]
        stack = []
        # logger.debug('TOKENS: %s' % tokens)
        for token in tokens:
            # logger.debug('TOKEN: %s' % token)
            if token.lower() in OPERATORS:
                op_class = OPERATORS.get(token)
                if stack:
                    while len(stack) != 0:
                        top = stack[-1]
                        if top in OPERATORS:
                            top_operator = OPERATORS.get(top)
                            if op_class.PRECEDENCE <= top_operator.PRECEDENCE:
                                self.postfix_array.append(stack.pop())
                            else:
                                # Break from loop if top operator precedence is less.
                                break
                        else:
                            # If top not operator break from loop
                            break
                stack.append(token)
            elif token == LEFT_PARENTHESIS:
                # logger.debug('Left parenthesis')
                stack.append(token)
            elif token == RIGHT_PARENTHESIS:
                # logger.debug('Right parenthesis')
                left_par_found = False
                stack_token = stack.pop()
                while stack_token:
                    if stack_token != LEFT_PARENTHESIS:
                        self.postfix_array.append(stack_token)
                    else:
                        left_par_found = True
                        break
                    if stack:
                        stack_token = stack.pop()
                    else:
                        stack_token = None
                        
                if not left_par_found:
                    raise ParseException('Mismatched parenthesis "%s".' % LEFT_PARENTHESIS)
            else:
                # logger.debug('Adding value to output. %s' % repr((token)))
                self.postfix_array.append((token))
            
        # There should be only operators left in the stack
        if stack:
            # logger.debug('Operators in stack.')
            operator = stack.pop()
            while operator:
                if operator != LEFT_PARENTHESIS:
                    self.postfix_array.append(operator)
                else:
                    raise ParseException('Mismatched parenthesis "%s".' % LEFT_PARENTHESIS)
                if stack:
                    operator = stack.pop()
                else:
                    operator = None

        # logger.debug('Infix to postfix conversion: %s' % self.postfix_array)
        return self.postfix_array
    
    def _create_parse_tree(self):
        self.parse_tree = []
        for token in self.postfix_array:
            if token in OPERATORS:
                # logger.debug('OP: %s' % (token))
                expression_class = OPERATORS[token]
                params = []
                for i in range(expression_class.PARAM_COUNT):
                    try:
                        params.append(self.parse_tree.pop())
                    except IndexError, e:
                        raise ParseException('Syntax error: "%s"' % self.expression)
                params.reverse()
                expression = expression_class(self, *params)

                # logger.debug('The operation: %s' % expression)
                self.parse_tree.append(expression)
            else:
                expression = TerminalExpression(self, token)
                self.parse_tree.append(expression)

        #logger.debug('THE STACK: %s' % self.parse_tree)
        #for s in self.parse_tree:
        #    logger.debug('Stack e: %s' % str(s))

        return self.parse_tree

    def eval(self):
        """ Evals the AST
        If empty expression is given, None is returned
        """
        for expression in self.parse_tree:
            self.value = expression.eval(self.context)
        return self.value

    @staticmethod
    def extract_refs(expression):
        tokens = get_tokens(expression)
        refs = []
        for token in tokens:
            if not token.lower() in OPERATORS and token != LEFT_PARENTHESIS and token != RIGHT_PARENTHESIS:
                refs.append(token.strip('%s%s' % (LEFT_PARENTHESIS, RIGHT_PARENTHESIS)))
        return refs

##################################################################
# Create and configure the main level logger
logger = logging.getLogger('cone')
