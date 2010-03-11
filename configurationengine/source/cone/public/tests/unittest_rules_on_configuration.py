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
import unittest
import sys, os
import __init__
import tokenize
import StringIO

from cone.public import api,exceptions, utils
from cone.public.rules import ASTInterpreter, RelationContainerImpl
from cone.public.rules import ParseException, DefaultContext, BaseRelation
from cone.public import rules

#### TEST RELATIONS ####

AA_BA = 'a.a == "foo" requires b.b != 0'
AB_BB = 'a.b configures b.b = a.b+":"+ "test"'
BA_CA = 'b.a requires c.a and c.b and a.b'

CB_DA = 'c.b requires d.a'
DA_DB = 'd.a requires d.b'

AC_AB_BA = 'a.c and a.a requires b.a'

EA_FSTAR = 'e.a requires f.*'

TEST_RELATIONS = {
    'a.a' : [AA_BA, 'a.a == "test" requires b.a'],
    'a.b' : [AB_BB],
    'a.c' : [AC_AB_BA],
    'b.a' : [BA_CA],
    'c.b' : [CB_DA],
    'd.a' : [DA_DB],
    'e.a' : [EA_FSTAR]
}

def get_test_configuration():
    config = api.Configuration()
    config.add_feature(api.Feature('a'))
    config.add_feature(api.Feature('a'),'a')
    config.add_feature(api.Feature('b'),'a')
    config.add_feature(api.Feature('c'),'a')
    config.add_feature(api.Feature('b'))
    config.add_feature(api.Feature('a'),'b')
    config.add_feature(api.Feature('b'),'b')
    config.add_feature(api.Feature('c'))
    config.add_feature(api.Feature('a'),'c')
    config.add_feature(api.Feature('b'),'c')
    config.add_feature(api.Feature('d'))
    config.add_feature(api.Feature('a'),'d')
    config.add_feature(api.Feature('b'),'d')
    config.add_feature(api.Feature('e'))
    config.add_feature(api.Feature('a'),'e')
    dview = config.get_default_view()
    dview.get_feature('a.a').set_value('test')
    dview.get_feature('a.b').set_value('hey')
    dview.get_feature('a.c').set_value(False)
    dview.get_feature('b.a').set_value(True)
    dview.get_feature('b.b').set_value(True)
    dview.get_feature('c.a').set_value(True)
    dview.get_feature('c.b').set_value(True)
    dview.get_feature('d.a').set_value(False)
    dview.get_feature('d.b').set_value(False)
    return config

class TestFactory():
    def get_relations_for(self, configuration, ref):
        rels = TEST_RELATIONS.get(ref)
        if rels:
            relation_container = RelationContainerImpl()
            for rel in rels:
                (left_expression,relation_name,right_expression) = parse_rule(rel)
                relation = rules.RELATIONS.get(relation_name)(configuration, left_expression, right_expression)
                relation_container.add_relation(relation)
                propagated_relations = self.get_relations_for(configuration, right_expression)
                if propagated_relations:
                    for relation in propagated_relations:
                        relation_container.add_relation(relation)
            return relation_container
        return None

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

class ConfigurationContext(DefaultContext):
    def handle_terminal(self, expression):
        try:
            value = self.data.get_feature(expression).get_value()
            if value != None:
                #print "handle_terminal %s = %s" % (expression,value)
                return value
            else:
                raise exceptions.NotBound('Feature %s has no value' % expression)
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
        
class ConfigurationBaseRelation(BaseRelation):
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
        super(ConfigureRelation, self).__init__(data, left, right)
        self.context = ConfigurationContext(data)

def handle_configure(self, left, right):
    if left and right:
        return True
    elif not left:
        return True
    return False

def handle_set(self, left, right):
    left.set_value(right)

class ConfigureExpression(rules.TwoOperatorExpression):
    PRECEDENCE = rules.PRECEDENCES['RELATION_OPERATORS']
    KEY = 'configures'
    OP = handle_configure

    def eval(self, context):
        super(ConfigureExpression, self).eval(context)
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

def handle_plus(self, a,b):
    #print "%s adding a: %s to b: %s" % (self, a,b)
    return a + b

class ConcatExpression(rules.TwoOperatorExpression):
    PRECEDENCE = rules.PRECEDENCES['ADDSUB_OPERATORS']
    KEY= '+'
    OP = handle_plus


class SetExpression(rules.TwoOperatorExpression):
    PRECEDENCE = rules.PRECEDENCES['SET_OPERATORS']
    KEY= '='
    OP = handle_set

    def eval(self, context):
        try:
            variable = context.data.get_feature(self.left.expression)
            variable.set_value(self.right.eval(context))
            return True
        except exceptions.NotFound:
            return False

class TestRelations(unittest.TestCase):

    def setUp(self):
        self.configuration = get_test_configuration()
        
        self.RELATIONS_BACKUP = rules.RELATIONS
        self.OPERATORS_BACKUP = rules.OPERATORS
        rules.RELATIONS = rules.RELATIONS.copy()
        rules.OPERATORS = rules.OPERATORS.copy()
        self.assertTrue(self.RELATIONS_BACKUP is not rules.RELATIONS)
        self.assertTrue(self.OPERATORS_BACKUP is not rules.OPERATORS)
        
        rules.RELATIONS[RequireRelation.KEY] = RequireRelation
        rules.RELATIONS[ConfigureRelation.KEY] = ConfigureRelation
        rules.OPERATORS[ConfigureExpression.KEY] = ConfigureExpression
        rules.OPERATORS[ConcatExpression.KEY] = ConcatExpression
        rules.OPERATORS[SetExpression.KEY] = SetExpression
    
    def tearDown(self):
        rules.RELATIONS = self.RELATIONS_BACKUP
        rules.OPERATORS = self.OPERATORS_BACKUP

    def test_has_ref(self):
        """
        Tests the relation and relation container
        """
        factory = TestFactory()
        rels = factory.get_relations_for(self.configuration, 'a.a')
        ret= rels.execute()
        self.assertTrue(ret)

    def test_has_ref(self):
        """
        Tests the relation and relation container
        """
        factory = TestFactory()
        rels = factory.get_relations_for(self.configuration, 'a.a')
        ret= rels.execute()
        self.assertTrue(ret)
        
    def test_not_has_ref(self):
        factory = TestFactory()
        # depends on c.a which has no value in conf
        rels = factory.get_relations_for(self.configuration, 'b.a')
        ret = rels.execute()
        self.assertTrue(ret)

    def test_not_has_ref_in_container(self):
        factory = TestFactory()
        rels = factory.get_relations_for(self.configuration, 'c.b')
        ret = rels.execute()
        self.assertFalse(ret)

    def test_two_on_the_left(self):
        factory = TestFactory()
        rels = factory.get_relations_for(self.configuration, 'a.c')
        ret = rels.execute()
        self.assertTrue(ret)

    def test_configure_right_side(self):
        factory = TestFactory()
        rels = factory.get_relations_for(self.configuration, 'a.b')
        ret = rels.execute()
        self.assertTrue(ret)
        self.assertEquals(self.configuration.get_default_view().get_feature('b.b').get_value(),'hey:test')

if __name__ == '__main__':
    unittest.main()
