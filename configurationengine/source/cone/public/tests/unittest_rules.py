# *-* coding: utf8 *-*
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

import unittest

from cone.public import rules

#### TEST RELATIONS ####

AA_BA = '${a.a} require ${b.b}'
AB_BB = '${a.b} require ${b.b}'
BA_CA = '${b.a} require ${c.a} and ${c.b} and ${a.b}'

CB_DA = '${c.b} require ${d.a}'
DA_DB = '${d.a} require ${d.b}'

AC_AB_BA = '${a.c} and ${a.a} require ${b.a}'

EA_FSTAR = '${e.a} require ${f.*}'

TEST_RELATIONS = {
    'a.a' : [AA_BA],
    'a.b' : [AB_BB],
    'a.c' : [AC_AB_BA],
    'b.a' : [BA_CA],
    'c.b' : [CB_DA],
    'd.a' : [DA_DB],
    'e.a' : [EA_FSTAR]
}

#rules.RELATIONS[rules.BaseRelation.KEY] = rules.BaseRelation
#rules.OPERATORS[rules.BaseRelation.KEY] = rules.BaseRelation

class DummyRelationFactory():
    def get_relations_for(self, configuration, ref):
        rels = TEST_RELATIONS.get(ref)

        if rels:
            relation_container = rules.RelationContainerImpl()
            for rel in rels:
                rel_s = rel.split(' ')
                from_ref = rel_s[0]
                relation_name = 'require'
                to_ref = ' '.join(rel_s[2:])
                relation = rules.RELATIONS.get(relation_name)(configuration, from_ref, to_ref)
                relation_container.add_relation(relation)
                propagated_relations = self.get_relations_for(configuration, to_ref)
                if propagated_relations:
                    for relation in propagated_relations:
                        relation_container.add_relation(relation)
                
            return relation_container
        return None

class DummyConfiguration(object):
    VALUES = {
        'a.a' : True,
        'a.b' : False,
        'a.c' : False,
        'b.a' : True,
        'b.b' : True,
        'c.b' : False,
        'd.a' : True,
        'e.a' : True,
        }

    def get_feature(self, ref):
        return DummyConfiguration.VALUES.get(ref, False)

class DummyContext(rules.DefaultContext):
    def handle_terminal(self, expression):
        return DummyConfiguration.VALUES.get(expression, False)

class DictContext(rules.DefaultContext):    
    def handle_terminal(self, expression):
        return self.data.get(expression, None)

    def convert_value(self, value):
        if isinstance(value, (str, unicode)):
            return eval(value)
        else:
            return value
        
    def set(self, expression, value):
        self.data[expression] =  value
        

class DummyBaseRelation(rules.BaseRelation):
    def __init__(self, data, left, right):
        self.context = DummyContext(data)
        super(DummyBaseRelation, self).__init__(data, left, right)

class DummyRequireRelation(DummyBaseRelation):
    KEY = 'require'

    def __init__(self, data, left, right):
        self.context = DummyContext(data)
        super(DummyRequireRelation, self).__init__(data, left, right)

rules.RELATIONS[DummyRequireRelation.KEY] = DummyRequireRelation
rules.OPERATORS['require'] = rules.RequireExpression
multilines = \
"""
APs.AP configures KCRUidCommsDatCreator.KCommsDatCreatorInputFileName = 'VariantData_commsdat.xml' and
  KCRUidStartupSettings.KCRKeyAccessPointPlugin = '0' and
  KCRUidStartupSettings.KCRKeyStreamingPlugin = '0' and
  KCRUidStartupSettings.KCRKeyMusicShopPlugin = '0' and
   KCRUidStartupSettings.KCRKeyDeviceManagementPlugin = '0' and
  KCRUidStartupSettings.KCRKeyAGPSPlugin = '0'
"""

class TestRelations(unittest.TestCase):

    def setUp(self):
        self.configuration = DummyConfiguration()

    def test_has_ref(self):
        """
        Tests the relation and relation container
        """
        factory = DummyRelationFactory()
        rels = factory.get_relations_for(self.configuration, 'a.a')
        ret= rels.execute()
        self.assertTrue(ret)
        
    def test_not_has_ref(self):
        factory = DummyRelationFactory()
        # depends on c.a which has no value in conf
        rels = factory.get_relations_for(self.configuration, 'b.a')
        ret = rels.execute()
        self.assertFalse(ret)

        for rel in rels:
            ip = rel.interpreter
            self.assertTrue(ip.errors)
            errors = ip.errors
            self.assertTrue(errors.get('b.a'))

    def test_not_has_ref_in_container(self):
        factory = DummyRelationFactory()
        rels = factory.get_relations_for(self.configuration, 'c.b')
        ret = rels.execute()
        self.assertTrue(ret)

    def test_two_on_the_left(self):
        factory = DummyRelationFactory()
        rels = factory.get_relations_for(self.configuration, 'a.c')
        ret = rels.execute()
        self.assertTrue(ret)

class TestExpressions(unittest.TestCase):
    def test_one_param_expression(self):
        exp = rules.OneParamExpression(None, rules.ValueTerminal(None, "10"))
        c = DictContext({})
        self.assertEquals(exp.eval(c), 10)
        exp = rules.OneParamExpression(None, rules.ReferenceTerminal(None, "${foo}"))
        c = DictContext({'foo' : 'Foo string'})
        self.assertEquals(exp.eval(c), 'Foo string')
        
    def test_neg_expression(self):
        exp = rules.NegExpression(None, rules.ValueTerminal(None, "10"))
        c = DictContext({})
        self.assertEquals(exp.eval(c), -10)
        exp = rules.NegExpression(None, rules.ReferenceTerminal(None, "${foo}"))
        c = DictContext({'foo' : 2})
        self.assertEquals(exp.eval(c), -2)

    def test_and_expression(self):
        exp = rules.AndExpression(None, rules.ValueTerminal(None, True),
                                  rules.ReferenceTerminal(None, "${foo}"))
        c = DictContext({'foo' : 1})
        self.assertEquals(exp.eval(c), True)
        c = DictContext({'foo' : 0})
        self.assertEquals(exp.eval(c), False)
        c = DictContext({'foo' : ""})
        self.assertEquals(exp.eval(c), False)
        c = DictContext({'foo' : False})
        self.assertEquals(exp.eval(c), False)
        c = DictContext({'foo' : True})
        self.assertEquals(exp.eval(c), True)

    def test_minus_expression(self):
        exp = rules.MinusExpression(None, rules.ValueTerminal(None, "10"), rules.ReferenceTerminal(None, "${foo}"))
        c = DictContext({'foo' : 10})
        self.assertEquals(exp.eval(c), 0)

    def test_plus_expression(self):
        exp = rules.PlusExpression(None, rules.ValueTerminal(None, "10"), rules.ReferenceTerminal(None, "${foo}"))
        c = DictContext({'foo' : 10})
        self.assertEquals(exp.eval(c), 20)

    def test_mul_expression(self):
        exp = rules.MultiplyExpression(None, rules.ValueTerminal(None, "10"), rules.ReferenceTerminal(None, "${foo}"))
        c = DictContext({'foo' : 10})
        self.assertEquals(exp.eval(c), 100)

    def test_div_expression(self):
        exp = rules.DivideExpression(None, rules.ValueTerminal(None, "10"), rules.ReferenceTerminal(None, "${foo}"))
        c = DictContext({'foo' : 10}) 
        self.assertEquals(exp.eval(c), 1)

    def test_get_expressions_from_relation(self):
        rel = rules.RequireRelation(None,"${foo} == True","${test} = 2 and ${aaa} == ${bbb}")
        self.assertEquals(len(rel.get_expressions()), 11)

    def test_get_refs_from_relation(self):
        rel = rules.BaseRelation(None,"${foo} == True","${test} = 2 and ${aaa} == ${bbb}")
        self.assertEquals(rel.get_refs(), ['foo'])

    def test_set_expression(self):
        exp = rules.SetExpression(None,rules.ReferenceTerminal(None, "${t}"),  rules.ValueTerminal(None, "10"))
        c = DictContext({'foo' : 10, 't' :None}) 
        self.assertEquals(exp.eval(c), True)
        self.assertEquals(c.data['t'], 10)

    def test_set_expression_in_relation(self):
        rel = rules.RequireRelation(None,"1","${test} = 1")        
        c = DictContext({'test' : None, 't' :None})
        rel.execute(c) 
        self.assertEquals(c.data['test'], 1)
        rel = rules.RequireRelation(None,"1","${test} = 2 and ${t} = 3")
        rel.execute(c) 
        self.assertEquals(c.data['test'], 2)
        self.assertEquals(c.data['t'], 3)

    def test_set_expression_in_relation_and_get_set_elements(self):
        rel = rules.RequireRelation(None,"1","${test} = 2")        
        self.assertEquals(rel.get_set_expressions()[0].left.get_ref(), 'test')

        rel = rules.RequireRelation(None,"1","${test} = 2 and ${t} = 3")
        self.assertEquals(len(rel.get_set_expressions()), 2)
        self.assertEquals(rel.get_set_expressions()[0].left.get_ref(), 'test')
        self.assertEquals(rel.get_set_expressions()[1].left.get_ref(), 't')

    def test_set_expression_in_relation_and_get_refs(self):
        rel = rules.RequireRelation(None,"${foo}","${test} = 2")
        self.assertEquals(rel.get_refs(), ['foo'])
        rel = rules.RequireRelation(None,"${foo}","${test} = 2 and ${t} = 3")
        self.assertEquals(rel.get_refs(), ['foo'])

    def test_set_expression_in_relation_and_get_set_refs(self):
        rel = rules.RequireRelation(None,"1","${test} = 2")
        self.assertEquals(rel.get_set_refs(), ['test'])

        rel = rules.RequireRelation(None,"1","${test} = 2 and ${t} = 3")
        self.assertEquals(rel.get_set_refs(),['test','t'])

    def test_set_expression_in_relation_with_string(self):
        rel = rules.RequireRelation(None,"1",'${test} = "foo "')
        c = DictContext({'test' : None, 't' :None})
        rel.execute(c) 
        self.assertEquals(c.data['test'], 'foo ')

    def test_set_expression_in_relation_with_string_concat(self):
        rel = rules.RequireRelation(None,"1",'${test} = "foo " + "bar"')
        c = DictContext({'test' : None, 't' :None})
        rel.execute(c) 
        self.assertEquals(c.data['test'], 'foo bar')

    def test_set_expression_in_relation_with_ref_concat(self):
        rel = rules.RequireRelation(None,"1",'${test} = ${s1} + " " + u"bar" + ${s2}')
        c = DictContext({'test' : None, 's1' : 'test', 's2' : 'one'})
        rel.execute(c) 
        self.assertEquals(c.data['test'], 'test barone')

class TestRuleUtils(unittest.TestCase):
    def test_is_str_literal(self):
        self.assertEquals(rules.is_str_literal(1), False)
        self.assertEquals(rules.is_str_literal([]), False)
        self.assertEquals(rules.is_str_literal("foo"), False)
        self.assertEquals(rules.is_str_literal("'foo'"), True)
        self.assertEquals(rules.is_str_literal('foo'), False)
        self.assertEquals(rules.is_str_literal('"foo bar"'), True)

    def test_get_str_literal(self):
        self.assertEquals(rules.get_str_literal(1), None)
        self.assertEquals(rules.get_str_literal([]), None)
        self.assertEquals(rules.get_str_literal("foo"), None)
        self.assertEquals(rules.get_str_literal("'foo'"), 'foo')
        self.assertEquals(rules.get_str_literal('foo'), None)
        self.assertEquals(rules.get_str_literal('"foo bar"'), 'foo bar')

class TestASTInterpreter(unittest.TestCase):
    def test_require(self):
        ip = rules.ASTInterpreter('a excludes b require 0')
        ret = ip.eval()

    def test_get_tokens(self):
        self.assertEquals(rules.get_tokens("foo=(2+1) * 3"),['foo','=','(','2','+','1',')','*','3'])
        self.assertEquals(rules.get_tokens("Arithmetic.MixedResult3 = (Arithmetic.Value2 / 2 + Arithmetic.Value1 * 9) - 7"),['Arithmetic.MixedResult3', '=', '(', 'Arithmetic.Value2', '/', '2', '+', 'Arithmetic.Value1', '*', '9', ')', '-', '7'])
        self.assertEquals(len(rules.get_tokens(multilines)),25)
    
    def test_get_unindented_multiline_tokens(self):
        self.assertEquals(
            rules.get_tokens("foo = 2+bar\nand foobar = 3 and\nfubar=4"),
            ['foo', '=', '2', '+', 'bar', 'and', 'foobar', '=', '3', 'and', 'fubar', '=', '4'])
    
    def test_get_tab_separated_tokens(self):
        self.assertEquals(
            rules.get_tokens("foo\tconfigures\t\tbar\t=\t5"),
            ['foo', 'configures', 'bar', '=', '5'])

    def test_get_unicode_tokens(self):
        self.assertEquals(
            rules.get_tokens(u'xÿz configures xzÿ = ÿxá'),
            [u'xÿz', 'configures', u'xzÿ', '=', u'ÿxá'])
    
    def test_get_unicode_tokens_2(self):
        self.assertEquals(
            rules.get_tokens(u'ελληνικά configures ünicode = u"test string" + ελληνικά'),
            [u'ελληνικά', 'configures', u'ünicode', '=', 'u"test string"', '+', u'ελληνικά'])
    
    def test_get_unicode_tokens_3(self):
        self.assertEquals(
            rules.get_tokens(u'oöoä äöoö oöo öoö äaäa'),
            [u'oöoä', u'äöoö', u'oöo', u'öoö', u'äaäa'])
    
    def test_get_unicode_tokens_4(self):
        self.assertEquals(
            rules.get_tokens(u'ünicode.rêf1 require rêf2 . ελληνικά'),
            [u'ünicode.rêf1', u'require', u'rêf2.ελληνικά'])
    
    def test_get_unicode_tokens_multiline(self):
        tokenstr = u"""
            foo=(2+1) * 3
            xÿz configures xzÿ = ÿxá
            ελληνικά configures ünicode = u"test string" + ελληνικά"""
        expected = [
            'foo', '=', '(', '2', '+', '1', ')', '*', '3',
            u'xÿz', 'configures', u'xzÿ', '=', u'ÿxá',
            u'ελληνικά', 'configures', u'ünicode', '=', 'u"test string"', '+', u'ελληνικά',
        ]
        actual = rules.get_tokens(tokenstr)
        self.assertEquals(actual, expected, '\n%r \n!= \n%r' % (actual, expected))
    
    def test_multiline_string(self):
        tokenstr = '''
"""
tes-
ti
"""
        '''
        expected = ['"""\ntes-\nti\n"""']
        self.assertEquals(rules.get_tokens(tokenstr), expected)

    def test_syntax_error(self):
        try:
            ip = rules.ASTInterpreter('a and and')
            self.assertTrue(False)
        except rules.ParseException:
            self.assertTrue(True)

    def test_empty_expression(self):
        expression = ''
        ip = rules.ASTInterpreter(expression)
        result = ip.eval()
        self.assertFalse(result)

    def test_no_expression(self):
        ip = rules.ASTInterpreter()
        result = ip.eval()
        self.assertFalse(result)       

        try:
            ip.create_ast(None)
            self.assertFalse(True)
        except rules.ParseException:
            self.assertTrue(True)

        ip.create_ast('1 and 1')
        result = ip.eval()
        self.assertTrue(result)       

    def test_one_param_ops(self):
        ip = rules.ASTInterpreter('1 and truth 1')
        result = ip.eval()
        self.assertTrue(result)
        
        ip.create_ast('1 and truth 0')
        result = ip.eval()
        self.assertFalse(result)

        ip.create_ast(u'1 and truth not 0')
        result = ip.eval()
        self.assertTrue(result)

    def test_infix_to_postfix(self):
        expression = '1 and not 1'
        ip = rules.ASTInterpreter(expression)
        self.assertEqual(ip.postfix_array, ['1', '1', 'not', 'and'])
        self.assertFalse(ip.eval())

    def test_infix_to_postfix_with_minus(self):
        expression = '1 - 1'
        ip = rules.ASTInterpreter(expression)
        self.assertEqual(ip.postfix_array, ['1', '1', '-'])
        self.assertFalse(ip.eval())

    def test_infix_to_postfix_pars(self):
        expression = '1 and ( 0 or 1 and 1 )'
        ip = rules.ASTInterpreter(expression)
        self.assertEqual(ip.postfix_array, ['1', '0', '1', 'or', '1', 'and', 'and'])
        self.assertTrue(ip.eval())

    def test_not(self):
        ip = rules.ASTInterpreter(u'not 1',)
        ret = ip.eval()
        self.assertFalse(ret)

        ip.create_ast(u'not 1')
        ret = ip.eval()
        self.assertFalse(ret)

        ip.create_ast('not STRING_VALUE')
        ret = ip.eval()
        self.assertFalse(ret)

    def test_not_with_multiple(self):
        ip = rules.ASTInterpreter(u'1 and not 0')
        ret = ip.eval()
        self.assertTrue(ret)
        ip.create_ast(u'1 and not 1')
        ret = ip.eval()
        self.assertFalse(ret)

    def test_and(self):
        ip = rules.ASTInterpreter(u'1 and 1 and 0')
        ret = ip.eval()
        self.assertFalse(ret)

        ip.create_ast(u'1 and 1 and 1')
        ret = ip.eval()
        self.assertTrue(ret)

    def test_nand(self):
        ip = rules.ASTInterpreter(u'1 nand 1 nand 1')
        ret = ip.eval()
        self.assertTrue(ret)

        ip.create_ast(u'1 nand 1 nand 0')
        ret = ip.eval()
        self.assertTrue(ret)

        ip.create_ast(u'1 nand 0 nand 1')
        ret = ip.eval()
        self.assertFalse(ret)

        ip.create_ast(u'0 nand 0 nand 0')
        ret = ip.eval()
        self.assertTrue(ret)

    def test_or(self):
        ip = rules.ASTInterpreter(u'1 or 1 or 0')
        ret = ip.eval()
        self.assertTrue(ret)

    def test_or_for_exclude(self):
        """
        On exclude case if OR returns True -> some element is selected
        and the rule evaluation should fail, the exclude rule should
        evaluate if PostfixRuleEngine.eval(expression) -> return False
        """
        ip = rules.ASTInterpreter(u'1 or 1 or 1')
        ret = ip.eval()
        self.assertTrue(ret)

        ip.create_ast(u'1 or 1 or 0')
        ret = ip.eval()
        self.assertTrue(ret)

        ip.create_ast(u'1 or 0 or 1')
        ret = ip.eval()
        self.assertTrue(ret)

        ip.create_ast(u'0 or 1 or 1')
        ret = ip.eval()
        self.assertTrue(ret)

        ip.create_ast(u'1 or 0 or 0')
        ret = ip.eval()
        self.assertTrue(ret)

        ip.create_ast(u'0 or 0 or 1')
        ret = ip.eval()
        self.assertTrue(ret)

        ip.create_ast(u'0 or 0 or 0')
        ret = ip.eval()
        self.assertFalse(ret)

    def test_nor(self):
        ip = rules.ASTInterpreter(u'1 nor 1 nor 1')
        ret = ip.eval()
        self.assertFalse(ret)

        ip.create_ast(u'1 nor 1 nor 0')
        ret = ip.eval()
        self.assertTrue(ret)

        ip.create_ast(u'0 nor 1 nor 0')
        ret = ip.eval()
        self.assertTrue(ret)

        ip.create_ast(u'0 nor 0 nor 0')
        ret = ip.eval()
        self.assertFalse(ret)


    def test_xor(self):
        ip = rules.ASTInterpreter(u'1 xor 1')
        ret = ip.eval()
        self.assertFalse(ret)

        ip.create_ast(u'1 xor 0 xor 0')
        ret = ip.eval()
        self.assertTrue(ret)  

    def test_eq_cmp(self):
        ip = rules.ASTInterpreter(u'1 == 0')
        ret = ip.eval()
        self.assertFalse(ret)
        
        ip.create_ast(u'1 == 1')
        ret = ip.eval()
        self.assertTrue(ret)

        ip.create_ast(u'DEFINED == DEFINED')
        ret = ip.eval()
        self.assertTrue(ret)        

        ip.create_ast(u'DEFINED == UNDEFINED')
        ret = ip.eval()
        self.assertFalse(ret)

    def test_neq_cmp(self):
        ip = rules.ASTInterpreter(u'1 != 1')
        ret = ip.eval()
        self.assertFalse(ret)

        ip.create_ast(u'1 != 0')
        ret = ip.eval()
        self.assertTrue(ret)   

    def test_lt_cmp(self):
        ip = rules.ASTInterpreter(u'0 < 1')
        ret = ip.eval()
        self.assertTrue(ret)

        ip.create_ast(u'0-1 < 1')
        ret = ip.eval()
        self.assertTrue(ret)

        ip.create_ast(u'0-1 < 0-2')
        ret = ip.eval()
        self.assertFalse(ret)

        ip.create_ast(u'2 < 0')
        ret = ip.eval()
        self.assertFalse(ret)

    def test_gt_cmp(self):
        ip = rules.ASTInterpreter(u'0 > 0-1')
        ret = ip.eval()
        self.assertTrue(ret)

        ip.create_ast(u'2 > 1')
        ret = ip.eval()
        self.assertTrue(ret)

        ip.create_ast(u'0 > 1')
        ret = ip.eval()
        self.assertFalse(ret)

        ip.create_ast(u'0-1 > 1')
        ret = ip.eval()
        self.assertFalse(ret)

    def test_lte_cmp(self):
        ip = rules.ASTInterpreter(u'0 <= 1')
        ret = ip.eval()
        self.assertTrue(ret)

        ip.create_ast(u'0 <= 0')
        ret = ip.eval()
        self.assertTrue(ret)

        ip.create_ast(u'1 <= 0')
        ret = ip.eval()
        self.assertFalse(ret)

    def test_gte_cmp(self):
        ip = rules.ASTInterpreter(u'1 >= 0')
        ret = ip.eval()
        self.assertTrue(ret)

        ip.create_ast(u'0 >= 0')
        ret = ip.eval()
        self.assertTrue(ret)

        ip.create_ast(u'0 >= 1')
        ret = ip.eval()
        self.assertFalse(ret)
 
    def test_extract_refs(self):
        refs = rules.ASTInterpreter.extract_refs('${a.a} and ( ${b.c} and ${d.e} )')
        self.assertTrue('a.a' in refs)
        self.assertTrue('b.c' in refs)
        self.assertTrue('d.e' in refs)
        self.assertTrue('and' not in refs)

    def test_one_of(self):
        """ Test for showing that relation one-of is basically "LEFT and R1 xor R2"
        """
        ip = rules.ASTInterpreter(u'1 and 1 and 1 xor 0')
        ret = ip.eval()
        self.assertTrue(ret)

if __name__ == '__main__':
    unittest.main()
