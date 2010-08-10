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
import sys
from cone.public import api, exceptions
from cone.confml import model


class TestConfmlMeta(unittest.TestCase):
    def test_create_meta(self):
        metaelem = model.ConfmlMeta()
        self.assertEquals(str(metaelem),"ConfmlMeta object\n")

    def test_create_with_data(self):
        prop1 = model.ConfmlMetaProperty("foo", 123)
        prop2 = model.ConfmlMetaProperty("bar", 312)
        prop3 = model.ConfmlMetaProperty("test", 'testing string')
        prop4 = model.ConfmlMetaProperty("testName", 'testing string2', \
                                         "http://www.nokia.com/xml/cpf-id/1", \
                                         attrs={"name":"name1", "value": "value1"})            
        metaelem = model.ConfmlMeta([prop1, prop2, prop3, prop4])
        self.assertEquals(metaelem[0].tag, "foo")
        self.assertEquals(metaelem[0].attrs, {})
        self.assertEquals(metaelem[0].value, 123)
        self.assertEquals(metaelem[1].tag, "bar")
        self.assertEquals(metaelem[1].value, 312)
        self.assertEquals(metaelem[2].tag, "test")
        self.assertEquals(metaelem[2].value, "testing string")
        self.assertEquals(metaelem[3].tag, "testName")
        self.assertEquals(metaelem[3].value, "testing string2")
        self.assertEquals(metaelem[3].ns, "http://www.nokia.com/xml/cpf-id/1")
        
    def test_add_data(self):
        metaelem = model.ConfmlMeta()
        metaelem.append(model.ConfmlMetaProperty('test', 123, "abc", attrs = {"foo":"bar", "abc":1}))
        self.assertEquals(metaelem[0].tag, 'test')
        self.assertEquals(metaelem[0].value, 123)
        self.assertEquals(metaelem[0].ns, "abc")
        self.assertEquals(metaelem[0].attrs, {"foo":"bar", "abc":1})

    def test_update_data(self):
        metaelem = model.ConfmlMeta()
        metaelem.append(model.ConfmlMetaProperty('test', 123, "abc", attrs = {"foo":"bar", "abc":1}))
        metaelem.set_property_by_tag('foo', 3)
        metaelem.set_property_by_tag('bar', None, 'http://me.com', {'name':'me', 'value':1})
        self.assertEquals(metaelem[0].tag, 'test')
        self.assertEquals(metaelem[0].value, 123)
        self.assertEquals(metaelem[0].ns, "abc")
        self.assertEquals(metaelem[0].attrs, {"foo":"bar", "abc":1})
        self.assertEquals(metaelem[1].tag, 'foo')
        self.assertEquals(metaelem[1].value, 3)
        self.assertEquals(metaelem[2].tag, "bar")
        self.assertEquals(metaelem[2].attrs, {'name':'me', 'value':1})

        metaelem1 = model.ConfmlMeta()
        metaelem.set_property_by_tag('foo', 2)
        metaelem.set_property_by_tag('bar', None, 'http://me.com', {'name':'me', 'value':2})
        metaelem.update(metaelem1)
        self.assertEquals(len(metaelem), 3)
        self.assertEquals(metaelem[0].tag, 'test')
        self.assertEquals(metaelem[0].value, 123)
        self.assertEquals(metaelem[0].ns, "abc")
        self.assertEquals(metaelem[0].attrs, {"foo":"bar", "abc":1})
        self.assertEquals(metaelem[1].tag, 'foo')
        self.assertEquals(metaelem[1].value, 2)
        self.assertEquals(metaelem[2].tag, "bar")
        self.assertEquals(metaelem[2].attrs, {'name':'me', 'value':2})
        
        
    def test_find_data(self):
        metaelem = model.ConfmlMeta()
        metaelem.append(model.ConfmlMetaProperty('test', 123, "abc",\
                                                  attrs = {"foo":"bar", "abc":1}))
        metaelem.append(model.ConfmlMetaProperty('abc', "efg", None,\
                                                  attrs = {"foo2":"bar2", "abc2":2}))
        metaelem.append(model.ConfmlMetaProperty('test', None, "demons",\
                                                  attrs = {"name":"bar1", "value":"foo1"}))
        metaelem.append(model.ConfmlMetaProperty('test', None, "demons",\
                                                  attrs = {"name":"bar2", "value":"foo2"}))
        self.assertEquals(metaelem.find_by_tag("test"), 0)
        self.assertEquals(metaelem.get_property_by_tag("test").tag, 'test')
        self.assertEquals(metaelem.get_property_by_tag("test").value, 123)
        self.assertEquals(metaelem.get_property_by_tag("test", {'name' : 'bar1'}).tag, 'test')
        self.assertEquals(metaelem.get_property_by_tag("test", {'name' : 'bar1'}).attrs['value'], 'foo1')
        self.assertEquals(metaelem.get("test"), 123)
        self.assertEquals(metaelem.get("test", 'ddd'), 123)
        # test get_value with not found elem
        self.assertEquals(metaelem.get("notthere"), None)
        self.assertEquals(metaelem.get("notthere", 'fooman'), 'fooman')
        self.assertEquals(metaelem.find_by_attribute("foo2", "bar2"), 1)
        self.assertEquals(metaelem.find_by_attribute("qwerty", ""), -1)

    def test_clone_meta(self):
        prop1 = model.ConfmlMetaProperty("foo", 123)
        prop2 = model.ConfmlMetaProperty("bar", 312)
        prop3 = model.ConfmlMetaProperty("test", 'testing string')        
        metaelem1 = model.ConfmlMeta([prop1, prop2, prop3])        
        metaelem2 = metaelem1.clone()
        self.assertEquals(metaelem1, metaelem2)

    def test_meta_set_property_by_tag(self):
        meta = model.ConfmlMeta()
        meta.set_property_by_tag('test', 'fooval')
        self.assertEquals(meta.get('test'), 'fooval')
        self.assertEquals(meta.get_property_by_tag('test').attrs, {})
        meta.set_property_by_tag('test', 'newval')
        self.assertEquals(meta.get_property_by_tag('test').attrs, {})
        self.assertEquals(meta.get('test'), 'newval')
        meta.add('test', 'twoval')
        self.assertEquals(meta.get_property_by_tag('test').attrs, {})
        self.assertEquals(meta.get('test'), 'newval')
        meta.set_property_by_tag('test', 'trheval')
        self.assertEquals(meta.get('test'), 'trheval')
        
class TestConfmlDescription(unittest.TestCase):
    def test_create_desc(self):
        descelem1 = model.ConfmlDescription("testing")
        descelem2 = model.ConfmlDescription()
        descelem3 = model.ConfmlDescription()
        descelem3.text = "changed"
        self.assertEquals(descelem1.text, "testing")
        self.assertEquals(descelem2.text, "")
        self.assertEquals(descelem3.text, "changed")

    def test_clone_desc(self):
        descelem1 = model.ConfmlDescription("testing")
        descelem2 = descelem1._clone()
        self.assertEquals(descelem1.text, descelem2.text)

class TestConfmlGroup(unittest.TestCase):
    def test_create_group(self):
        group1 = model.ConfmlGroup("foo")
        self.assertEquals(group1.ref, "foo")
        self.assertEquals(group1.icon, None)
        self.assertEquals(group1.desc, None)

    def test_group_access_icon(self):
        group1 = model.ConfmlGroup("foo", icon='first/icon.bmp')
        self.assertEquals(group1.icon, "first/icon.bmp")
        group1.icon = 'foo/bar.jpg'
        self.assertEquals(group1.icon, "foo/bar.jpg")
        del group1.icon
        self.assertEquals(group1.icon, None)

    def test_group_access_description(self):
        group1 = model.ConfmlGroup("foo", desc='Testing description. for this something!')
        self.assertEquals(group1.desc, "Testing description. for this something!")
        group1.desc = 'Something else'
        self.assertEquals(group1.desc, "Something else")
        del group1.desc
        self.assertEquals(group1.icon, None)

    def test_clone_group(self):
        group1 = model.ConfmlGroup("foo")
        group2 = group1._clone()
        self.assertEquals(group1.ref, group2.ref)
        self.assertEquals(group1.desc, group2.desc)
        self.assertEquals(group1.icon, group2.icon)

        group1 = model.ConfmlGroup("foo", desc='testing desc', icon='link.bmp')
        group2 = group1._clone(recursion=True)
        self.assertEquals(group1.ref, group2.ref)
        self.assertEquals(group1.desc, group2.desc)
        self.assertEquals(group1.icon, group2.icon)


class TestConfmlSetting(unittest.TestCase):
    def test_create_setting(self):
        elem = model.ConfmlSetting('test')
        self.assertTrue(elem)
        self.assertEquals(elem.desc, None)
        self.assertEquals(elem.readOnly, None)
        self.assertEquals(elem.constraint, None)
        self.assertEquals(elem.required, None)
        self.assertEquals(elem.relevant, None)
        self.assertEquals(elem.id, None)

    def test_setting_id(self):
        elem = model.ConfmlSetting('foo', id="test id")
        self.assertEquals(elem.id,'test id')
        elem.id = "new id"
        self.assertEquals(elem.id,'new id')
        del elem.id
        self.assertEquals(elem.id,None)

    def test_getters(self):
        elem = model.ConfmlSetting('foo', name="foo")
        self.assertEquals(elem.get_ref(),'foo')
        self.assertEquals(elem.get_type(),None)
        self.assertEquals(elem.get_name(),'foo')

    def test_set_type(self):
        elem = model.ConfmlSetting('foo', name="bar")
        elem.type = 'string'
        self.assertEquals(elem.ref,'foo')
        self.assertEquals(elem.type,'string')
        self.assertEquals(elem.name, "bar")

    def test_setting_with_options(self):
        elem = model.ConfmlSetting('foo',type='selection')
        elem.create_option('foo','1')
        elem.create_option('bar','bar')
        elem.create_option('hou','sut')
        self.assertTrue('1' in elem.get_valueset()) 
        self.assertEquals(elem.options['1'].name, 'foo')
        self.assertEquals(elem.options['1'].value, '1')
        self.assertEquals(elem.options['bar'].name, 'bar')

    def test_create_options(self):
        elem = model.ConfmlSetting('foo',type='property', name='foo')
        self.assertEquals(elem.name, 'foo')
        self.assertEquals(elem.type, 'property')

    def test_setting_create_with_nonetype(self):
        elem = model.ConfmlSetting('foo',type=None)
        self.assertEqual(elem.type,None) 

    def test_setting_with_properties(self):
        elem = model.ConfmlSetting('foo')
        elem.create_property(name='foo',value='bar/foo')
        elem.create_property(name='bar',value='only/bar')
        elem.create_property(name='testing',value='1', unit='mB')
        self.assertEquals(elem.list_properties(), ['foo','bar','testing'])
        self.assertEquals(elem.get_property('foo').value, 'bar/foo')
        elem.remove_property('foo')
        try:
            elem.remove_property('bss')
            self.fail('removing invalid succeeds')
        except exceptions.NotFound:
            pass
        self.assertEquals(elem.list_properties(), ['bar','testing'])
        for property_name in elem.list_properties():
            elem.remove_property(property_name)
        self.assertEquals(elem.list_properties(), [])
        

    def test_setting_with_properties_property(self):
        elem = model.ConfmlSetting('foo')
        elem.create_property(name='foo',value='bar/foo')
        elem.create_property(name='bar',value='only/bar')
        elem.create_property(name='testing',value='1', unit='mB')
        self.assertEquals(elem.property_foo.value,'bar/foo')
        self.assertEquals(elem.property_bar.value,'only/bar')

    def test_setting_with_readOnly_value(self):
        elem = model.ConfmlSetting('foo', readOnly=True)
        self.assertEquals(elem.readOnly,True)
        elem.readOnly = False
        self.assertEquals(elem.readOnly,False)

    def test_setting_with_constaint(self):
        elem = model.ConfmlSetting('foo', constraint=". &gt; '1'")
        self.assertEquals(elem.constraint,". &gt; '1'")
        elem.constraint = 'foobar'
        self.assertEquals(elem.constraint,"foobar")

    def test_setting_with_required_value(self):
        elem = model.ConfmlSetting('foo', required=False)
        self.assertEquals(elem.required,False)
        elem = model.ConfmlSetting('foo', required=True)
        self.assertEquals(elem.required,True)
        elem.required = False
        self.assertEquals(elem.required,False)

    def test_setting_with_relevant_value(self):
        elem = model.ConfmlSetting('foo', relevant='ffoo oss')
        self.assertEquals(elem.relevant,'ffoo oss')
        elem.relevant = ''
        self.assertEquals(elem.relevant,'')

    def test_setting_with_max_length(self):
        elem = model.ConfmlSetting('foo', maxLength=10)
        self.assertEquals(elem.maxLength,10)
        elem.maxLength = 20
        self.assertEquals(elem.maxLength,20)
        self.assertTrue(elem._has(model.ConfmlMaxLength.refname))

    def test_setting_with_min_length(self):
        elem = model.ConfmlSetting('foo', minLength=10)
        self.assertEquals(elem.minLength,10)
        elem.minLength = 20
        self.assertEquals(elem.minLength,20)
        self.assertTrue(elem._has(model.ConfmlMinLength.refname))
    
    def test_setting_with_length(self):
        elem = model.ConfmlSetting('foo', length=10)
        self.assertEquals(elem.length,10)
        elem.length = 20
        self.assertEquals(elem.length,20)
        self.assertTrue(elem._has(model.ConfmlLength.refname))
        self.assertEquals(elem._get(model.ConfmlLength.refname).value, 20)

    def test_setting_rfs_casting(self):
        elem = model.ConfmlSetting('foo', minLength=10)
        self.assertEquals(elem.get_rfs_cast('true'),True)
        self.assertEquals(elem.get_rfs_cast('false'),False)
        self.assertEquals(elem.set_rfs_cast(True),'true')
        self.assertEquals(elem.set_rfs_cast(False),'false')
        self.assertEquals(elem.set_rfs_cast(1),'true')
    
    def test_get_rfs_with_no_value(self):
        conf = api.Configuration("test.confml")
        conf.add_feature(model.ConfmlSetting("foo"))
        
        # Test that initially the RFS value is None
        fea = conf.get_default_view().get_feature('foo')
        self.assertEquals(fea.get_value(attr='rfs'), None)
        self.assertEquals(fea.get_original_value(attr='rfs'), None)
    
    def test_get_rfs_true(self):
        conf = api.Configuration("test.confml")
        conf.add_feature(model.ConfmlSetting("foo"))
        conf.add_data(api.Data(ref='foo', attr='rfs', value='true'))
        
        fea = conf.get_default_view().get_feature('foo')
        self.assertEquals(fea.get_value(attr='rfs'), True)
        self.assertEquals(fea.get_original_value(attr='rfs'), 'true')
    
    def test_get_rfs_false(self):
        conf = api.Configuration("test.confml")
        conf.add_feature(model.ConfmlSetting("foo"))
        conf.add_data(api.Data(ref='foo', attr='rfs', value='false'))
        
        fea = conf.get_default_view().get_feature('foo')
        self.assertEquals(fea.get_value(attr='rfs'), False)
        self.assertEquals(fea.get_original_value(attr='rfs'), 'false')
    
    def test_set_rfs(self):
        conf = api.Configuration("test.confml")
        conf.add_feature(model.ConfmlSetting("foo"))
        
        def check_data_elements(expected):
            actual = []
            for d in conf._traverse(type=api.Data):
                actual.append((d.fqr, d.attr, d.value))
            self.assertEquals(actual, expected)
        
        fea = conf.get_default_view().get_feature('foo')
        
        fea.set_value(True, attr='rfs')
        self.assertEquals(fea.get_value(attr='rfs'), True)
        self.assertEquals(fea.get_original_value(attr='rfs'), 'true')
        check_data_elements([('foo', 'rfs', 'true')])
        
        fea.set_value(False, attr='rfs')
        self.assertEquals(fea.get_value(attr='rfs'), False)
        self.assertEquals(fea.get_original_value(attr='rfs'), 'false')
        check_data_elements([('foo', 'rfs', 'false')])

class TestConfmlSelectionSetting(unittest.TestCase):
    def test_create_selection_setting(self):
        elem = model.ConfmlSelectionSetting('foo', desc="Test desc", name="Foo fea")
        self.assertTrue(elem)
        self.assertEquals(elem.type, 'selection')
        self.assertEquals(elem.name, 'Foo fea')
        self.assertEquals(elem.desc, "Test desc")
        self.assertEquals(elem.readOnly, None)
        self.assertEquals(elem.constraint, None)
        self.assertEquals(elem.required, None)
        self.assertEquals(elem.relevant, None)
    
    def test_selection_valueset(self):
        elem = model.ConfmlSelectionSetting('foo')
        self.assertEquals(elem.type, 'selection')
        elem.create_option('foo', '1')
        elem.create_option('bar', '2')
        elem.create_option('baz', '3')
        self.assertEquals(elem.get_valueset(), api.ValueSet(['1', '2', '3']))

class TestConfmlMultiSelectionSetting(unittest.TestCase):
    def test_create_multiselection_setting(self):
        elem = model.ConfmlMultiSelectionSetting('mset1', name="Setting 1", desc="de")
        self.assertTrue(elem)
        self.assertEquals(elem.type, 'multiSelection')
        self.assertEquals(elem.name, "Setting 1")
        self.assertEquals(elem.desc, "de")
        self.assertEquals(elem.readOnly, None)
        self.assertEquals(elem.constraint, None)
        self.assertEquals(elem.required, None)
        self.assertEquals(elem.relevant, None)
    
    def test_multiselection_valueset(self):
        elem = model.ConfmlMultiSelectionSetting('foo')
        self.assertEquals(elem.type, 'multiSelection')
        elem.create_option('foo', '1')
        elem.create_option('bar', '2')
        elem.create_option('baz', '3')
        self.assertEquals(elem.get_valueset(), api.ValueSet(['1', '2', '3']))

    def test_setting_value_to_multiselection(self):
        conf = model.ConfmlConfiguration('test.confml')
        elem = model.ConfmlMultiSelectionSetting('mset2', type='multiSelection')
        conf.add_feature(elem)
        elem.value = ["sel1", "sel2"]
        self.assertEquals(elem.type, 'multiSelection')
        self.assertEquals(elem.get_value(), ("sel1", "sel2"))

    def test_setting_value_to_multiselection2(self):
        conf = model.ConfmlConfiguration('test.confml')
        elem = model.ConfmlMultiSelectionSetting('mset3', type='multiSelection')
        conf.add_feature(elem)
        elem.value = ["sel1", "sel2 with some spaces"]
        self.assertEquals(elem.type, 'multiSelection')
        self.assertEquals(elem.get_value(), ("sel1", "sel2 with some spaces"))
        elem.value = ["sel1", "sel2 with some spaces"]
        self.assertEquals(elem.get_value(), ("sel1", "sel2 with some spaces"))
        
    def test_setting_not_list_value_to_multiselection(self):
        conf = model.ConfmlConfiguration('test.confml')
        elem = model.ConfmlMultiSelectionSetting('mset4', type='multiSelection')
        conf.add_feature(elem)
        self.assertRaises(ValueError, elem.set_value, "not list")
        
    def test_setting_list_value_to_multiselection(self):
        conf = model.ConfmlConfiguration('test.confml')
        elem = model.ConfmlMultiSelectionSetting('mset5', type='multiSelection')
        conf.add_feature(elem)
        elem.set_value(["li1", "li2"])
        self.assertEquals(elem.get_value(), ("li1", "li2"))
        self.assertEquals(elem.get_datas()[0].get_value(), 'li1')
        self.assertEquals(elem.get_datas()[1].get_value(), 'li2')
    
    def test_get_value_from_old_style_data(self):
        def check(data_value, expected):
            config = api.Configuration('foo.confml')
            fea = model.ConfmlMultiSelectionSetting('multisel', type='multiSelection')
            config.add_feature(fea)
            config.add_data(api.Data(ref='multisel', value=data_value))
            
            dview = config.get_default_view()
            foofea = dview.get_feature('multisel')
            self.assertEquals(foofea.value, expected)

        check('x', ('x',))
        check('"x"', ('x',))
        check('"x" "y"', ('x', 'y'))
        check('"x" "y" "" "z"', ('x', 'y', '', 'z'))
    
    def test_get_value_with_new_style_data(self):
        def check(data_object_values, expected_value, empty_option=False):
            config = api.Configuration('foo.confml')
            fea = model.ConfmlMultiSelectionSetting('multisel', type='multiSelection')
            if empty_option:
                fea.add_option(api.Option('Empty option', ''))
            config.add_feature(fea)
            for dv in data_object_values:
                config.add_data(api.Data(ref='multisel', value=dv), policy=api.container.APPEND)
            
            dview = config.get_default_view()
            foofea = dview.get_feature('multisel')
            self.assertEquals(foofea.value, expected_value)
        
        check([], ())
        check(['x'], ('x',))
        check(['x', 'y'], ('x', 'y'))
        check(['y', 'x', 'y',], ('y', 'x'))
        check(['"foo"', '"bar"'], ('"foo"', '"bar"'))
        check(['foo bar'], ('foo bar',))
        check(['foo bar', 'foo baz'], ('foo bar', 'foo baz'))
        check(['foo "bar"'], ('foo "bar"',))
        
        # Element with no data is interpreted as meaning the option ''
        # if it is allowed, otherwise it is ignored
        check([None], (), empty_option=False)
        check([None], ('',), empty_option=True)
    
    def test_get_value_from_data_with_empty_attribute(self):
        config = api.Configuration('foo.confml')
        fea = model.ConfmlMultiSelectionSetting('multisel', type='multiSelection')
        config.add_feature(fea)
        config.add_data(api.Data(ref='multisel', empty=True))
        
        dview = config.get_default_view()
        foofea = dview.get_feature('multisel')
        self.assertEquals(foofea.value, ())
        
        
    def test_set_value(self):
        def check(value, expected_data_object_values):
            config = api.Configuration('foo.confml')
            fea = model.ConfmlMultiSelectionSetting('multisel', type='multiSelection')
            config.add_feature(fea)
            
            dview = config.get_default_view()
            foofea = dview.get_feature('multisel')
            self.assertEquals(foofea.value, ())
            
            foofea.value = value
            # Check that the value is visible directly after setting
            # (the 'or' is because setting to None actually set the value
            # to an empty tuple)
            self.assertEquals(foofea.value, value or ())
            
            # Check that the data elements have been set as expected
            actual = []
            for d in config._traverse(type=api.Data):
                actual.append((d.fqr, d.value, d.empty))
            expected = []
            for val, empty in expected_data_object_values:
                expected.append(('multisel', val, empty))
            self.assertEquals(actual, expected)

        # Setting empty should create a single data object with empty=True
        check((), [(None, True)])
        check([], [(None, True)])
        check(None, [(None, True)])
        
        check(('x',), [('x', False)])
        check(('x', 'y'), [('x', False), ('y', False)])
        check(('"foo"', '"bar"'), [('"foo"', False), ('"bar"', False)])
        check(('foo bar',), [('foo bar', False)])
        check(('foo bar', 'foo baz'), [('foo bar', False), ('foo baz', False)])
        check(('foo "bar"',), [('foo "bar"', False)])
    
    def test_old_style_data_pattern(self):
        def check(value, expected):
            m = model.ConfmlMultiSelectionSetting.OLD_STYLE_DATA_PATTERN.match(value)
            self.assertEquals(m is not None, expected)
        
        check('', False)
        check('""', True)
        check('foo', False)
        check('foo bar', False)
        check('"foo bar"', True)
        check('"foo bar " " foo baz" "  yeah  " ""', True)
        check('"foo"', True)
        check('"foo" "bar"', True)
        check('"foo" "bar" "baz"', True)
        check('"a" "b" "c" "d" "e" "f" "g" "h"', True)
        check('a b c d e f g h', False)
        check('"a b c d e f g h"', True)

class TestConfmlIntSetting(unittest.TestCase):
    def test_create_setting(self):
        elem = model.ConfmlIntSetting('test')
        self.assertTrue(elem)
        self.assertEquals(elem.type, 'int')
        self.assertEquals(elem.desc, None)
        self.assertEquals(elem.readOnly, None)
        self.assertEquals(elem.constraint, None)
        self.assertEquals(elem.required, None)
        self.assertEquals(elem.relevant, None)
        self.assertEquals(elem.get_valueset().fromvalue, 0)
        self.assertEquals(elem.get_valueset().tovalue, sys.maxint)

    def test_setting_value_to_int(self):
        conf = model.ConfmlConfiguration('test.confml')
        elem = model.ConfmlIntSetting('foo', type='int')
        conf.add_feature(elem)
        elem.value = 1
        self.assertEquals(elem.value,1)
        self.assertEquals(elem.get_original_value(),'1')
        self.assertEquals(elem.get_data().get_value(),'1')

    def test_setting_value_with_incompatible_values(self):
        conf = model.ConfmlConfiguration('test.confml')
        elem = model.ConfmlIntSetting('foo')
        conf.add_feature(elem)
        try:
            elem.value = 'hh'
            self.fail('setting string to int succeeds')
        except ValueError:
            pass
        elem.value = '1234'
        self.assertEquals(elem.value, 1234)
        elem.value = 0xA
        self.assertEquals(elem.value, 10)
        del elem.value
        self.assertEquals(elem.value, None)

    def test_setting_value_to_int_with_aritmethic_operations(self):
        conf = model.ConfmlConfiguration('test.confml')
        elem1 = model.ConfmlIntSetting('foo')
        elem2 = model.ConfmlIntSetting('bar')
        conf.add_feature(elem1)
        conf.add_feature(elem2)
        elem1.value = 1
        elem2.value = 2
        test = elem1.value + elem2.value
        self.assertEquals(test,3)
        elem1.value = elem1.value + elem2.value + 5
        self.assertEquals(elem1.value,8)

class TestConfmlHexBinarySetting(unittest.TestCase):
    def test_hexbinary_default_value_set(self):
        setting = model.ConfmlHexBinarySetting('test')
        vset = setting.get_valueset()
        self.assertTrue('' in vset)
        self.assertTrue('0123456789ABCDEF' in vset)
        self.assertTrue('00112233445566778899AABBCCDDEEFF' in vset)
        
        self.assertFalse('foobar' in vset)
        self.assertFalse('1' in vset)
        self.assertFalse('F' in vset)
        self.assertFalse('1G' in vset)
        self.assertFalse('0123456789abcdef' in vset)
        self.assertFalse('00112233445566778899aabbccddeeff' in vset)
        
        self.assertTrue('foobar' not in vset)

    def test_hexbinary_get_value_none(self):
        conf = model.ConfmlConfiguration('test.confml')
        setting = model.ConfmlHexBinarySetting('foo')
        conf.add_feature(setting)
        self.assertEquals(setting.value, None)
    
    def test_hexbinary_get_value_empty(self):
        conf = model.ConfmlConfiguration('test.confml')
        setting = model.ConfmlHexBinarySetting('foo')
        conf.add_feature(setting)
        conf.add_data(api.Data(ref='foo', value=None))
        self.assertEquals(setting.value, '')
    
    def test_hexbinary_get_value(self):
        conf = model.ConfmlConfiguration('test.confml')
        setting = model.ConfmlHexBinarySetting('foo')
        conf.add_feature(setting)
        conf.add_data(api.Data(ref='foo', value='0123456789ABCDEF'))
        self.assertEquals(setting.value, '\x01\x23\x45\x67\x89\xab\xcd\xef')
        self.assertEquals(setting.get_original_value(), '0123456789ABCDEF')
    
    def test_hexbinary_set_value(self):
        conf = model.ConfmlConfiguration('test.confml')
        setting = model.ConfmlHexBinarySetting('foo')
        conf.add_feature(setting)
        
        setting.value = '\x01\xab'
        self.assertEquals(setting.value, '\x01\xab')
        
        data_list = conf.get_all_datas()
        self.assertEquals(len(data_list), 1)
        d = data_list[0]
        self.assertEquals(d.attr, 'data')
        self.assertEquals(d.fqr, 'foo')
        self.assertEquals(d.value, '01AB')
        self.assertEquals(d.empty, False)
    
    def test_hexbinary_get_data_cast(self):
        setting = model.ConfmlHexBinarySetting('foo')
        
        self.assertEquals(setting.get_data_cast(''), '')
        self.assertEquals(setting.get_data_cast(None), '')
        self.assertEquals(setting.get_data_cast('0123456789ABCDEF'), '\x01\x23\x45\x67\x89\xab\xcd\xef')
        
        self.assertRaises(ValueError, setting.get_data_cast, 'X')
        self.assertRaises(ValueError, setting.get_data_cast, '1')
        self.assertRaises(ValueError, setting.get_data_cast, 'XX')
    
    def test_hexbinary_set_data_cast(self):
        setting = model.ConfmlHexBinarySetting('foo')
        
        self.assertEquals(setting.set_data_cast(''), '')
        self.assertEquals(setting.set_data_cast('\x01'), '01')
        self.assertEquals(setting.set_data_cast('x'), '78')
        self.assertEquals(setting.set_data_cast('\x01\x23\x45\x67\x89\xab\xcd\xef'), '0123456789ABCDEF')
        
class TestConfmlBooleanSetting(unittest.TestCase):
    def test_create_setting(self):
        elem = model.ConfmlBooleanSetting('test')
        self.assertTrue(elem)
        self.assertEquals(elem.type, 'boolean')
        self.assertEquals(elem.desc, None)
        self.assertEquals(elem.readOnly, None)
        self.assertEquals(elem.constraint, None)
        self.assertEquals(elem.required, None)
        self.assertEquals(elem.relevant, None)

    def test_setting_value_to_int(self):
        conf = model.ConfmlConfiguration('test.confml')
        elem = model.ConfmlBooleanSetting('foo', type='int')
        self.assertEquals(elem.type, 'boolean')
        conf.add_feature(elem)
        elem.value = 1
        # Set elem rfs value
        elem.set_value(True, 'rfs')
        self.assertEquals(elem.get_value('rfs'),True)
        self.assertEquals(elem.get_original_value('rfs'),'true')
        self.assertEquals(elem.value,1)
        self.assertEquals(elem.get_original_value(),'true')
        self.assertEquals(elem.get_data().get_value(),'true')

    def test_setting_value_with_incompatible_values(self):
        conf = model.ConfmlConfiguration('test.confml')
        elem = model.ConfmlBooleanSetting('foo')
        conf.add_feature(elem)
        elem.value = '1234'
        self.assertEquals(elem.value, True)
        elem.value = 0xA
        self.assertEquals(elem.value, True)
        elem.value = False
        self.assertEquals(elem.value, False)
        elem.value = ''
        self.assertEquals(elem.value, False)
        del elem.value
        self.assertEquals(elem.value, None)
    
    def test_setting_value_with_supported_values(self):
        conf = model.ConfmlConfiguration('test.confml')
        elem = model.ConfmlBooleanSetting('foo')
        conf.add_feature(elem)
        elem.value = '1'
        self.assertEquals(elem.value, True)
        elem.value = 'true'
        self.assertEquals(elem.value, True)
        elem.value = True
        self.assertEquals(elem.value, True)
        elem.value = '0'
        self.assertEquals(elem.value, False)
        elem.value = 'false'
        self.assertEquals(elem.value, False)
        elem.value = False
        self.assertEquals(elem.value, False)
        del elem.value
        self.assertEquals(elem.value, None)

class TestConfmlSequenceSetting(unittest.TestCase):
    def test_create_setting(self):
        elem = model.ConfmlSequenceSetting('test', name="testing fea", desc="Test desc")
        self.assertTrue(elem)
        self.assertEquals(elem.name, "testing fea")
        self.assertEquals(elem.desc, "Test desc")
        subfea = elem.create_feature("subfea")
        self.assertEquals(subfea.is_sequence(), True)
        subfea.is_sequence = lambda : False
        self.assertEquals(subfea.is_sequence(), False)
        
    def test_create_sequence_setting_with_mapping(self):
        elem = model.ConfmlSequenceSetting('test', name="testing fea", desc="Test desc", mapKey="setting", mapValue="setval")
        self.assertTrue(elem)
        self.assertEquals(elem.name, "testing fea")
        self.assertEquals(elem.desc, "Test desc")
        self.assertEquals(elem.mapKey, "setting")
        self.assertEquals(elem.mapValue, "setval")

    def test_setting_with_properties_property(self):
        elem = model.ConfmlSequenceSetting('foo')
        elem.create_property(name='foo',value='bar/foo')
        elem.create_property(name='bar',value='only/bar')
        elem.create_property(name='testing',value='1', unit='mB')
        self.assertEquals(elem.property_foo.value,'bar/foo')
        self.assertEquals(elem.property_bar.value,'only/bar')

    def test_setting_with_min_occurs(self):
        elem = model.ConfmlSequenceSetting('foo', minOccurs=1)
        self.assertEquals(elem.minOccurs,1)
        elem.minOccurs = 2
        self.assertEquals(elem.minOccurs,2)

    def test_setting_with_max_occurs(self):
        elem = model.ConfmlSequenceSetting('foo', maxOccurs=10)
        self.assertEquals(elem.maxOccurs,10)
        elem.maxOccurs = 20
        self.assertEquals(elem.maxOccurs,20)

    def test_create_feature_seq_with_values(self):
        import logging
        logger = logging.getLogger('cone')
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        logger.addHandler(ch)
        
        config = api.Configuration('foo.confml')
        fea= model.ConfmlSequenceSetting("foo", displayName='TestDisplayName')
        fea.add_feature(model.ConfmlIntSetting('child1'))
        fea.add_feature(model.ConfmlBooleanSetting('child2'))
        fea.add_feature(model.ConfmlSetting('child3'))
        config.add_feature(fea)
        dview = config.get_default_view()
        foofea = dview.get_feature('foo')
        # Test adding a data row with array
        foofea.set_value([[1,True,'foo'],
                         [2,False,'bar'],
                         [3,True,'sumthin']
                         ])
        
        self.assertEquals(foofea.displayName, 'TestDisplayName')
        self.assertEquals(foofea.data[0][0].get_original_value(), '1')
        self.assertEquals(foofea.data[0].get_original_value(), ['1', 'true', 'foo'])
        
        self.assertEquals(foofea.value, [[1,True,'foo'],
                                        [2,False,'bar'],
                                        [3,True,'sumthin']
                                        ])

        self.assertEquals(foofea.get_original_value(), [['1','true','foo'],
                                                        ['2','false','bar'],
                                                        ['3','true','sumthin']
                                                        ])
        self.assertEquals(foofea.data[0].get_original_value(), ['1','true','foo'])
        self.assertEquals(foofea.data[1].get_original_value(), ['2','false','bar'])
        self.assertEquals(foofea.data[2].get_original_value(), ['3', 'true', 'sumthin'])
        self.assertEquals(foofea.child1.get_original_value(), ['1', '2', '3'])
        self.assertEquals(foofea.child2.get_original_value(), ['true', 'false', 'true'])
        self.assertEquals(foofea.child3.get_original_value(), ['foo', 'bar', 'sumthin'])

        foofea.value = [[1,True,'foo'],
                        [2,False,'bar']
                        ]
        
        self.assertEquals(foofea.data[0].value,[1,True,'foo'])
        self.assertEquals(foofea.data[1].value,[2,False,'bar'])
        self.assertEquals(foofea.data[1][1].value,False)
        self.assertEquals(foofea.get_value(), [[1,True,'foo'],
                                               [2,False,'bar']
                                               ])
        self.assertEquals(foofea.child1.value,[1,2])
    
    def test_sequence_with_mapped_data(self):
        config = api.Configuration('foo.confml')
        
        fea = model.ConfmlSequenceSetting("SourceSequence", mapKey='KeySubSetting', mapValue="ValueSubSetting")
        fea.add_feature(model.ConfmlIntSetting("KeySubSetting"))
        fea.add_feature(model.ConfmlStringSetting("ValueSubSetting"))
        config.add_feature(fea)
        
        fea = model.ConfmlSelectionSetting('TargetSetting')
        config.add_feature(fea)
        
        data = api.Data(ref='SourceSequence')
        data.add(api.Data(ref='KeySubSetting', value='1'))
        data.add(api.Data(ref='ValueSubSetting', value='Value 1'))
        config.add_data(data)
        
        data = api.Data(ref='TargetSetting', map="SourceSequence[@key='1']")
        config.add_data(data)
        
        fea = config.get_default_view().get_feature('TargetSetting')
        self.assertEquals(fea.get_value(), 'Value 1')
    
    def test_sequence_with_mapped_data_in_sequence(self):
        config = api.Configuration('foo.confml')
        
        fea = model.ConfmlSequenceSetting("SourceSequence", mapKey='KeySubSetting', mapValue="ValueSubSetting")
        fea.add_feature(model.ConfmlIntSetting("KeySubSetting"))
        fea.add_feature(model.ConfmlStringSetting("ValueSubSetting"))
        config.add_feature(fea)
        
        fea = model.ConfmlSequenceSetting('TargetSequence')
        fea.add_feature(model.ConfmlSelectionSetting("Setting"))
        config.add_feature(fea)
        
        data = api.Data(ref='SourceSequence')
        data.add(api.Data(ref='KeySubSetting', value='1'))
        data.add(api.Data(ref='ValueSubSetting', value='Value 1'))
        config.add_data(data)
       
        data = api.Data(ref='TargetSequence')
        data.add(api.Data(ref='Setting', map="SourceSequence[@key='1']"))
        config.add_data(data)
        
        fea = config.get_default_view().get_feature('TargetSequence')
        self.assertEquals(fea.get_value(), [['Value 1']])
    
    def test_sequence_with_multiselection_set_value(self):
        config = api.Configuration('foo.confml')
        
        fea = model.ConfmlSequenceSetting("fooseq")
        fea.add_feature(model.ConfmlMultiSelectionSetting("msel"))
        config.add_feature(fea)
        
        dview = config.get_default_view()
        fea = dview.get_feature(fea.fqr)
        self.assertEquals(fea.value, [])
        
        def check_data_elements(expected_data_object_values):
            actual = []
            for d in config._traverse(type=api.Data):
                actual.append((d.fqr, d.value, d.empty))
            expected = []
            for fqr, val, empty in expected_data_object_values:
                expected.append((fqr, val, empty))
            self.assertEquals(actual, expected)
        
        fea.value = []
        self.assertEquals(fea.value, [])
        check_data_elements(
            [('fooseq', None, False),])
        
        fea.value = [[()]]
        self.assertEquals(fea.value, [[()]])
        check_data_elements(
            [('fooseq', None, False),
             ('fooseq.msel', None, True),])
        
        fea.value = [[('x',)]]
        self.assertEquals(fea.value, [[('x',)]])
        check_data_elements(
            [('fooseq', None, False),
             ('fooseq.msel', 'x', False),])
        
        fea.value = [[('x',)], [('y',)]]
        self.assertEquals(fea.value, [[('x',)], [('y',)]])
        check_data_elements(
            [('fooseq', None, False),
             ('fooseq.msel', 'x', False),
             ('fooseq', None, False),
             ('fooseq.msel', 'y', False),])
        
        fea.value = [[('x', 'y')],
                     [('a', 'b', 'c')],
                     [()],
                     [('d', 'e', 'f')]]
        self.assertEquals(fea.value, [[('x', 'y')],
                                      [('a', 'b', 'c')],
                                      [()],
                                      [('d', 'e', 'f')]])
        check_data_elements(
            [('fooseq', None, False),
             ('fooseq.msel', 'x', False),
             ('fooseq.msel', 'y', False),
             ('fooseq', None, False),
             ('fooseq.msel', 'a', False),
             ('fooseq.msel', 'b', False),
             ('fooseq.msel', 'c', False),
             ('fooseq', None, False),
             ('fooseq.msel', None, True),
             ('fooseq', None, False),
             ('fooseq.msel', 'd', False),
             ('fooseq.msel', 'e', False),
             ('fooseq.msel', 'f', False),])
    
    def test_sequence_with_multiselection_get_value(self):
        config = api.Configuration('foo.confml')
        fea = model.ConfmlSequenceSetting("fooseq")
        fea.add_feature(model.ConfmlMultiSelectionSetting("msel"))
        config.add_feature(fea)
        
        seqdata1 = api.Data(ref='fooseq')
        seqdata1._add([api.Data(ref='msel', value='x'),
                       api.Data(ref='msel', value='y')])
        seqdata2 = api.Data(ref='fooseq')
        seqdata2._add([api.Data(ref='msel', empty=True)])
        seqdata3 = api.Data(ref='fooseq')
        seqdata3._add([api.Data(ref='msel', value='a'),
                       api.Data(ref='msel', value='b'),
                       api.Data(ref='msel', value='c')])
        config.add_data([seqdata1, seqdata2, seqdata3])
        
        dview = config.get_default_view()
        fea = dview.get_feature(fea.fqr)
        self.assertEquals(fea.value, [[('x', 'y')], [()], [('a', 'b', 'c')]])
    
    def test_simple_name_id_mapping(self):
        config = api.Configuration('foo.confml')
        seq = model.ConfmlSequenceSetting('seq', mapKey='strsub', mapValue='strsub')
        seq.add_feature(model.ConfmlStringSetting('strsub'))
        seq.add_feature(model.ConfmlIntSetting('intsub'))
        seq.add_feature(model.ConfmlRealSetting('realsub'))
        seq.add_feature(model.ConfmlBooleanSetting('boolsub'))
        config.add_feature(seq)
        config.add_feature(api.Feature('target'))
        
        config.add_data(api.Data(fqr='seq.strsub', value='foo'))
        config.add_data(api.Data(fqr='seq.intsub', value='123'))
        config.add_data(api.Data(fqr='seq.realsub', value='1.5'))
        config.add_data(api.Data(fqr='seq.boolsub', value='true'))
        config.add_data(api.Data(fqr='target', map="seq[@key='foo']"))
        
        fea = config.get_default_view().get_feature('target')
        self.assertEquals(fea.value, 'foo')
        self.assertEquals(fea.get_original_value(), 'foo')
        
        seq.mapValue = 'intsub'
        self.assertEquals(fea.value, 123)
        self.assertEquals(fea.get_original_value(), '123')
        
        seq.mapValue = 'realsub'
        self.assertEquals(fea.value, 1.5)
        self.assertEquals(fea.get_original_value(), '1.5')
        
        seq.mapValue = 'boolsub'
        self.assertEquals(fea.value, True)
        self.assertEquals(fea.get_original_value(), 'true')
    
    def test_simple_name_id_mapping_with_multiselection(self):
        config = api.Configuration('foo.confml')
        seq = model.ConfmlSequenceSetting('seq', mapKey='strsub', mapValue='intsub')
        seq.add_feature(model.ConfmlStringSetting('strsub'))
        seq.add_feature(model.ConfmlIntSetting('intsub'))
        config.add_feature(seq)
        config.add_feature(model.ConfmlMultiSelectionSetting('target'))
        
        d = api.Data(fqr='seq')
        d.add(api.Data(ref='strsub', value='foo'))
        d.add(api.Data(ref='intsub', value='123'))
        config.add_data(d, api.container.APPEND)
        
        d = api.Data(fqr='seq')
        d.add(api.Data(ref='strsub', value='bar'))
        d.add(api.Data(ref='intsub', value='321'))
        config.add_data(d, api.container.APPEND)
        
        d = api.Data(fqr='seq')
        d.add(api.Data(ref='strsub', value='baz'))
        d.add(api.Data(ref='intsub', value='456'))
        config.add_data(d, api.container.APPEND)
        
        config.add_data([api.Data(fqr='target', map="seq[@key='bar']"),
                         api.Data(ref='target', map="seq[@key='baz']"),
                         api.Data(ref='target', map="seq[@key='foo']")])
        
        fea = config.get_default_view().get_feature('target')
        self.assertEquals(fea.value, (321, 456, 123))
        self.assertEquals(fea.get_original_value(), ('321', '456', '123'))
    
    def test_simple_name_id_mapping_with_file_and_folder_setting(self):
        def _run_test(subsetting_class):
            config = api.Configuration('foo.confml')
            seq = model.ConfmlSequenceSetting('seq')
            seq.add_feature(subsetting_class('filefoldersub'))
            config.add_feature(seq)
            config.add_feature(model.ConfmlSelectionSetting('target'))
            
            def _add_seq_data(local_path, target_path):
                d = api.Data(fqr='seq')
                subd = api.Data(ref='filefoldersub')
                subd.add(api.Data(ref='localPath', value=local_path))
                subd.add(api.Data(ref='targetPath', value=target_path))
                d.add(subd)
                config.add_data(d, api.container.APPEND)
            _add_seq_data('local/path/1', 'target/path/1')
            _add_seq_data('local/path/2', 'target/path/2')
            _add_seq_data('local/path/3', 'target/path/3')
            target_data = api.Data(fqr='target')
            config.add_data(target_data)

            fea = config.get_default_view().get_feature('target')
    
            seq.mapKey = 'filefoldersub'
            seq.mapValue = 'filefoldersub'
            target_data.map = "seq[@key='local/path/1']"
            self.assertEquals(fea.value, 'local/path/1')
            
            seq.mapKey = 'filefoldersub/localPath'
            seq.mapValue = 'filefoldersub/localPath'
            target_data.map = "seq[@key='local/path/1']"
            self.assertEquals(fea.value, 'local/path/1')
            
            seq.mapKey = 'filefoldersub/targetPath'
            seq.mapValue = 'filefoldersub/targetPath'
            target_data.map = "seq[@key='target/path/2']"
            self.assertEquals(fea.value, 'target/path/2')
            
            seq.mapKey = 'filefoldersub/localPath'
            seq.mapValue = 'filefoldersub/targetPath'
            target_data.map = "seq[@key='local/path/3']"
            self.assertEquals(fea.value, 'target/path/3')
        
        _run_test(subsetting_class=model.ConfmlFileSetting)
        _run_test(subsetting_class=model.ConfmlFolderSetting)
    
    def test_simple_name_id_mapping_override_map_value_in_option(self):
        config = api.Configuration('foo.confml')
        fea = model.ConfmlFeature('fea')
        config.add_feature(fea)
        seq = model.ConfmlSequenceSetting('seq', mapKey='strsub', mapValue='strsub')
        seq.add_feature(model.ConfmlStringSetting('strsub'))
        seq.add_feature(model.ConfmlIntSetting('intsub'))
        fea.add_feature(seq)
        target = api.Feature('target')
        target.add_option(api.Option(None, None, map='fea/seq', map_value='intsub'))
        fea.add_feature(target)
        
        config.add_data(api.Data(fqr='fea.seq.strsub', value='foo'))
        config.add_data(api.Data(fqr='fea.seq.intsub', value='123'))
        config.add_data(api.Data(fqr='fea.target', map="fea/seq[@key='foo']"))
        
        fea = config.get_default_view().get_feature('fea.target')
        self.assertEquals(fea.value, 123)
        self.assertEquals(fea.get_original_value(), '123')
    
    def _assert_raises(self, exception_class, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
            self.fail("No exception raised")
        except exception_class, e:
            return e
    
    def test_name_id_mapping_errors(self):
        config = api.Configuration('foo.confml')
        seq = model.ConfmlSequenceSetting('seq')
        seq.add_feature(model.ConfmlStringSetting('strsub'))
        seq.add_feature(model.ConfmlIntSetting('intsub'))
        config.add_feature(seq)
        
        config.add_feature(model.ConfmlIntSetting('foosetting'), 'foofea')
        
        target = api.Feature('target')
        target_option = api.Option(None, None, map='seq')
        target.add_option(target_option)
        config.add_feature(target)
        
        config.add_data(api.Data(fqr='seq.strsub', value='foo'))
        config.add_data(api.Data(fqr='seq.intsub', value='123'))
        target_data = api.Data(fqr='target', map="seq[@key='123']")
        config.add_data(target_data)
        
        fea = config.get_default_view().get_feature('target')
        
        e = self._assert_raises(exceptions.NameIdMappingError, fea.get_value)
        self.assertEquals(str(e), "Source sequence 'seq' must have both mapKey and mapValue specified")
        
        seq.mapKey = 'strsub'
        e = self._assert_raises(exceptions.NameIdMappingError, fea.get_value)
        self.assertEquals(str(e), "Source sequence 'seq' must have both mapKey and mapValue specified")
        
        seq.mapKey = None
        seq.mapValue = 'strsub'
        e = self._assert_raises(exceptions.NameIdMappingError, fea.get_value)
        self.assertEquals(str(e), "Source sequence 'seq' must have both mapKey and mapValue specified")
        
        seq.mapKey = 'intsub'
        seq.mapValue = 'strsub'
        
        target_data.map = "foobar"
        e = self._assert_raises(exceptions.NameIdMappingError, fea.get_value)
        self.assertEquals(str(e), "Malformed mapping expression: foobar")
        
        target_data.map = "foo/bar[key='321']"
        e = self._assert_raises(exceptions.NameIdMappingError, fea.get_value)
        self.assertEquals(str(e), "Malformed mapping expression: foo/bar[key='321']")
        
        target_data.map = "foo/bar[@key='321'"
        e = self._assert_raises(exceptions.NameIdMappingError, fea.get_value)
        self.assertEquals(str(e), "Malformed mapping expression: foo/bar[@key='321'")
        
        target_data.map = "foo/nonexistent[@key='321']"
        e = self._assert_raises(exceptions.NameIdMappingError, fea.get_value)
        self.assertEquals(str(e), "Mapping source sequence 'foo.nonexistent' does not exist")
        
        target_data.map = "foofea/foosetting[@key='321']"
        e = self._assert_raises(exceptions.NameIdMappingError, fea.get_value)
        self.assertEquals(str(e), "Mapping source setting 'foofea.foosetting' is not a sequence setting")
        
        target_data.map = "seq[@key='321']"
        e = self._assert_raises(exceptions.NameIdMappingError, fea.get_value)
        self.assertEquals(str(e), "No item-setting in source sequence 'seq' matches key '321'")
        
        seq.mapKey = 'foo'
        target_data.map = "seq[@key='321']"
        e = self._assert_raises(exceptions.NameIdMappingError, fea.get_value)
        self.assertEquals(str(e), "Invalid mapKey in source sequence 'seq': no sub-setting with ref 'foo'")
        
        seq.mapKey = 'intsub'
        seq.mapValue = 'foo'
        target_data.map = "seq[@key='321']"
        e = self._assert_raises(exceptions.NameIdMappingError, fea.get_value)
        self.assertEquals(str(e), "Invalid mapValue in source sequence 'seq': no sub-setting with ref 'foo'")
        
        seq.mapValue = 'strsub'
        target_data.map = "seq[@key='123']"
        target_option.map_value = 'foobar'
        e = self._assert_raises(exceptions.NameIdMappingError, fea.get_value)
        self.assertEquals(str(e), "Invalid mapValue override in option: sub-setting 'foobar' does not exist under source sequence 'seq'")
        
        # Test successful mapping for good measure
        seq.mapKey = 'intsub'
        seq.mapValue = 'strsub'
        target_data.map = "seq[@key='123']"
        target_option.map_value = 'intsub'
        self.assertEquals(fea.get_value(), 123)
        self.assertEquals(fea.get_original_value(), '123')

class TestConfmlFile(unittest.TestCase):
    def test_create_localpath_elem(self):
        elem = model.ConfmlLocalPath()
        self.assertTrue(elem)
        self.assertEquals(elem.get_ref(),'localPath')

    def test_create_targetpath_elem(self):
        elem = model.ConfmlTargetPath()
        self.assertTrue(elem)
        self.assertEquals(elem.get_ref(),'targetPath')

    def test_create_file_elem(self):
        elem = model.ConfmlFileSetting('test')
        self.assertTrue(elem)
        self.assertEquals(elem.get_ref(),'test')
        self.assertEquals(elem.list_features(), ['localPath','targetPath'])
        self.assertEquals(elem.get_feature('localPath').fqr, 'test.localPath')
        self.assertEquals(elem.get_feature('targetPath').fqr, 'test.targetPath')
        self.assertEquals(elem.get_feature('localPath').name, 'localPath')
        self.assertEquals(elem.get_feature('targetPath').name, 'targetPath')

    def test_create_file_elem_and_set_value(self):
        config = api.Configuration('test.confml')
        elem = model.ConfmlFileSetting('test', localpath='test.txt')
        config.add_feature(elem)
        dview = config.get_default_view()
        self.assertEquals(dview.list_all_features(),['test','test.localPath','test.targetPath'])
        dview.get_feature('test.localPath').set_value('foo/test.txt')
        dview.get_feature('test.targetPath').set_value('Z:\\test\test.txt')
        dview.get_feature('test.localPath').set_value('now/test.txt')
        self.assertEquals(dview.get_feature('test.localPath').get_value(),'now/test.txt')
        self.assertEquals(len(dview.get_feature('test.localPath').get_datas()),1)

    def test_clone_file_elem(self):
        elem1 = model.ConfmlFileSetting('test')
        elem2 = elem1._clone(recursion=True)
        

    def test_create_file_elem_to_a_sequence(self):
        config = model.ConfmlConfiguration('foo.confml')
        seq = model.ConfmlSequenceSetting('foo')
        elem = model.ConfmlFileSetting('test')
        seq.add_feature(elem)
        config.add_feature(seq)
        seq.value = [[['local file', 'targetfile']],
                     [['local file2', 'targetfile2']]]
        
        self.assertEquals(seq.test.localPath.get_value(), ['local file',
                                                           'local file2'])
        
    def test_create_folder_elem_to_a_sequence(self):
        config = model.ConfmlConfiguration('foo.confml')
        seq = model.ConfmlSequenceSetting('foo')
        elem = model.ConfmlFolderSetting('test')
        seq.add_feature(elem)
        config.add_feature(seq)
        seq.value = [[['local file', 'targetfile']],
                     [['local file2', 'targetfile2']]]
        
        self.assertEquals(seq.test.localPath.get_value(), ['local file',
                                                           'local file2'])

        
class TestConfmlIcon(unittest.TestCase):
    def test_create_icon(self):
        icon = model.ConfmlIcon("test/foo/bar.jpg")
        self.assertEquals(icon.href, "test/foo/bar.jpg")
        icon.href = 'new/icon.jpg'
        self.assertEquals(icon.href, "new/icon.jpg")

    def test_clone_icon(self):
        icon1 = model.ConfmlIcon("test/foo/bar.jpg")
        icon2 = icon1._clone()
        self.assertEquals(icon1.href, icon2.href)


class TestLengths(unittest.TestCase):
    def test_create_maxLength(self):
        max = model.ConfmlMaxLength('100')
        self.assertEquals(max.value, 100)
        max.value = 10
        self.assertEquals(max.value, 10)
        max.value = '1000'
        self.assertEquals(max.value, 1000)
        
    def test_create_minLength(self):
        min = model.ConfmlMinLength('100')
        self.assertEquals(min.value, 100)
        min.value = 10
        self.assertEquals(min.value, 10)
        min.value = '1000'
        self.assertEquals(min.value, 1000)

    def test_create_length(self):
        len = model.ConfmlLength('100')
        self.assertEquals(len.value, 100)
        len.value = 10
        self.assertEquals(len.value, 10)
        len.value = '1000'
        self.assertEquals(len.value, 1000)

class TestConfmlFacets(unittest.TestCase):
    def test_numeric_base_classs(self):
        numeric = model.ConfmlNumericValue()
        numeric.value = 3
        self.assertEquals(numeric.value, 3)
        numeric.value = 0.3
        self.assertEquals(numeric.value, 0.3)
        numeric.value = '22'
        self.assertEquals(numeric.value, 22)
        numeric.value = '0.1'
        self.assertEquals(numeric.value, 0.1)
        try:
            numeric.value = 'foo'
            self.fail("setting string to float property succeeded!")
        except ValueError:
            pass

    def test_create_inclusive(self):
        min = model.ConfmlMinInclusive('-10')
        max = model.ConfmlMaxInclusive('10')
        self.assertEquals(min.value, -10)
        self.assertEquals(max.value, 10)
        min.value = 10
        self.assertEquals(min.value, 10)
        min.value = '1000'
        self.assertEquals(min.value, 1000)
        max.value = 10
        self.assertEquals(max.value, 10)
        max.value = '1000'
        self.assertEquals(max.value, 1000)

    def test_create_exclusive(self):
        min = model.ConfmlMinExclusive('0')
        max = model.ConfmlMaxExclusive("9")
        self.assertEquals(min.value, 0)
        self.assertEquals(max.value, 9)
        max.value = 10
        self.assertEquals(max.value, 10)
        max.value = '1000'
        self.assertEquals(max.value, 1000)
        min.value = 10
        self.assertEquals(min.value, 10)
        min.value = '1000'
        self.assertEquals(min.value, 1000)

    def test_create_pattern(self):
        pattern = model.ConfmlPattern("[a-zA-Z]")
        self.assertEquals(pattern.value, "[a-zA-Z]")

    def test_create_totalDigits(self):
        digits = model.ConfmlTotalDigits("3")
        self.assertEquals(digits.value, 3)
        digits.value = 10
        self.assertEquals(digits.value, 10)
        digits.value = '1000'
        self.assertEquals(digits.value, 1000)

class TestConfmlConfiguration(unittest.TestCase):
    def test_create_configuration(self):
        config = model.ConfmlConfiguration("test/foo/bar.jpg")
        self.assertEquals(config.meta, None)
        self.assertEquals(config.desc, None)
        self.assertEquals(config.name, 'test__foo__bar_jpg')
        self.assertEquals(config.ref, 'test__foo__bar_jpg')
        self.assertEquals(config.path, 'test/foo/bar.jpg')

    def test_create_configuration_and_features(self):
        conf = model.ConfmlConfiguration("simple.confml")
        fea = conf.create_feature("test")
        self.assertTrue(isinstance(fea, model.ConfmlFeature))
        self.assertEquals(conf.get_feature('test'), fea)
        fea = conf.create_feature("test1", name="test name")
        self.assertEquals(conf.get_feature('test1').name, 'test name')
        subfea = fea.create_feature("subfea", name="subfea name")
        self.assertTrue(isinstance(subfea, model.ConfmlSetting))
        self.assertEquals(conf.list_all_features(), ['test','test1','test1.subfea'])

    def test_configuration_get_default_view(self):
        config = model.ConfmlConfiguration("test/foo/bar.jpg")
        config.add_feature(model.ConfmlFeature("test"))
        view = config.create_view("testview")
        group = view.create_group("group1")
        group.create_featurelink("test")
        self.assertEquals(config.list_all_features(), ['test'])
        
    def test_configuration_access_desc(self):
        config = model.ConfmlConfiguration("test/foo/bar.jpg", desc="testing description")
        self.assertEquals(config.desc, "testing description")
        config.desc = 'new desc'
        self.assertEquals(config.desc, "new desc")
        del config.desc
        self.assertEquals(config.desc, None)

    def test_use_create_configuration(self):
        config = model.ConfmlConfiguration("test/foo/bar.jpg")
        subconfig = config.create_configuration("sub/jee.confml")
        self.assertEquals(subconfig.get_full_path(),'test/foo/sub/jee.confml')
        self.assertTrue(isinstance(subconfig,model.ConfmlConfiguration))

        
class TestConfmlView(unittest.TestCase):
    def test_create_view(self):
        view = model.ConfmlView("test", id="test")
        self.assertTrue(view)
        self.assertEquals(view.get_ref(),'test')
        self.assertEquals(view.id,"test")

    def test_create_view_with_create_view(self):
        config = model.ConfmlConfiguration("test")
        view = config.create_view("test")
        group = view.create_group("group1")
        fl = group.create_featurelink("intset1")
        self.assertTrue(isinstance(view, model.ConfmlView))
        self.assertTrue(isinstance(group, model.ConfmlGroup))
        self.assertTrue(isinstance(fl, model.ConfmlFeatureLink))

    def test_create_confml_featurelink(self):
        fealink = model.ConfmlFeatureLink("test")
        self.assertTrue(fealink)
        self.assertEquals(fealink.get_ref(),'link_test')

    def test_create_confml_featurelink_with_overrides(self):
        fealink = model.ConfmlFeatureLink("test")
        fealink.desc = "test desc"
        self.assertEquals(fealink.desc,'test desc')
        self.assertEquals(fealink._has('_desc'),True)
        self.assertEquals(fealink.get_attributes(),{'properties': {},'options': {}, 'desc' : 'test desc'})

    def test_create_confml_featurelink_with_option_overrides(self):
        fealink = model.ConfmlFeatureLink("test")
        fealink.add(api.Option('opt2', '2'))
        self.assertEquals(fealink.options['2'].name,'opt2')

    def test_create_view_with_groups(self):
        view = model.ConfmlView("test")
        view.create_group("group1")
        view.create_group("group2")
        self.assertEquals(view.list_groups(),['group1','group2'])

    def test_create_configuration_with_featurelinks(self):
        config = model.ConfmlConfiguration("test")
        config.add_feature(model.ConfmlFeature("fea1", name="Feature 1"))
        intset1 = model.ConfmlIntSetting("intset1", name="Setting 1")
        intset1.desc = "int setting desc"
        config.add_feature(intset1, "fea1")

        view = config.create_view("test")
        group = view.create_group("group1")
        fl = group.create_featurelink("intset1")
        self.assertTrue(isinstance(fl, model.ConfmlFeatureLink))
        self.assertTrue(len(config.get_default_view().get_features('**')), 2)
        
        
    def test_create_configuration_with_view_and_featurelink_overrides(self):
        config = model.ConfmlConfiguration("test")
        config.add_feature(model.ConfmlFeature("fea1", name="Feature 1"))
        intset1 = model.ConfmlIntSetting("intset1", name="Setting 1")
        intset1.desc = "int setting desc"
        config.add_feature(intset1, "fea1")
        
        view = config.create_view("test")
        view.create_group("group1")
        fl = model.ConfmlFeatureLink("fea1.intset1", name="override name")
        fl.desc = "override desc"
        fl.minLength = 2
        fl.maxLength = 10
        fl.minOccurs = 2
        fl.maxOccurs = 10
        
        fl.pattern = '^.*@.*$'
        fl.totalDigits = 10
        fl.minInclusive = 0
        fl.maxInclusive = 10
        fl.minExclusive = 0
        fl.maxExclusive = 10
        
        fl.add(api.Option('opt1', '1'))
        
        view.get_group('group1').add(fl)
        view.populate()
        self.assertEquals(view.list_all_features(),['group1.proxy_fea1_intset1'])
        self.assertEquals(view.get_feature('group1.proxy_fea1_intset1').desc, "override desc")
        self.assertEquals(view.get_feature('group1.proxy_fea1_intset1').name, "override name")
        self.assertEquals(view.get_feature('group1.proxy_fea1_intset1').minLength, 2)
        self.assertEquals(view.get_feature('group1.proxy_fea1_intset1').maxLength, 10)
        self.assertEquals(view.get_feature('group1.proxy_fea1_intset1').minOccurs, 2)
        self.assertEquals(view.get_feature('group1.proxy_fea1_intset1').maxOccurs, 10)
        self.assertEquals(view.get_feature('group1.proxy_fea1_intset1').pattern, '^.*@.*$')
        self.assertEquals(view.get_feature('group1.proxy_fea1_intset1').totalDigits, 10)
        self.assertEquals(view.get_feature('group1.proxy_fea1_intset1').minInclusive, 0)
        self.assertEquals(view.get_feature('group1.proxy_fea1_intset1').maxInclusive, 10)
        self.assertEquals(view.get_feature('group1.proxy_fea1_intset1').minExclusive, 0)
        self.assertEquals(view.get_feature('group1.proxy_fea1_intset1').maxExclusive, 10)
        self.assertEquals(view.get_feature('group1.proxy_fea1_intset1').options['1'].name,'opt1')
        
if __name__ == '__main__':
    unittest.main()
