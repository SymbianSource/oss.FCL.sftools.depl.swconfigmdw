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
import string
import sys
import __init__

from cone.public import api, exceptions
from cone.confml import model


class TestConfmlMeta(unittest.TestCase):
    def test_create_meta(self):
        metaelem = model.ConfmlMeta()
        self.assertTrue(metaelem)

    def test_create_with_data(self):
        prop1 = model.ConfmlMetaProperty("foo", 123)
        prop2 = model.ConfmlMetaProperty("bar", 312)
        prop3 = model.ConfmlMetaProperty("test", 'testing string')
        prop4 = model.ConfmlMetaProperty("testName", 'testing string2', \
                                         "http://www.nokia.com/xml/cpf-id/1", \
                                         attrs={"name":"name1", "value": "value1"})            
        metaelem = model.ConfmlMeta([prop1, prop2, prop3, prop4])
        self.assertEquals(metaelem[0].tag, "foo")
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

    def test_find_data(self):
        metaelem = model.ConfmlMeta()
        metaelem.append(model.ConfmlMetaProperty('test', 123, "abc",\
                                                  attrs = {"foo":"bar", "abc":1}))
        metaelem.append(model.ConfmlMetaProperty('abc', "efg", None,\
                                                  attrs = {"foo2":"bar2", "abc2":2}))
        self.assertEquals(metaelem.find_by_tag("test"), 0)
        self.assertEquals(metaelem.get_property_by_tag("test").tag, 'test')
        self.assertEquals(metaelem.get_property_by_tag("test").value, 123)
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

    def test_getters(self):
        elem = model.ConfmlSetting('foo')
        self.assertTrue(elem.get_ref(),'foo')
        self.assertEquals(elem.get_type(),None)
        self.assertTrue(elem.get_name(),'foo')

    def test_set_type(self):
        elem = model.ConfmlSetting('foo')
        elem.type = 'string'
        self.assertTrue(elem.ref,'foo')
        self.assertTrue(elem.type,'string')
        self.assertTrue(elem.name,'foo')

    def test_setting_with_options(self):
        elem = model.ConfmlSetting('foo',type='selection')
        elem.create_option('foo','1')
        elem.create_option('bar','bar')
        elem.create_option('hou','sut')
        self.assertTrue('1' in elem.get_valueset()) 
        self.assertEquals(elem.options['1'].name, 'foo')
        self.assertEquals(elem.options['1'].value, '1')
        self.assertEquals(elem.options['bar'].name, 'bar')

    def test_setting_create_with_nonetype(self):
        elem = model.ConfmlSetting('foo',type=None)
        self.assertEqual(elem.type,None) 

    def test_setting_with_properties(self):
        elem = model.ConfmlSetting('foo')
        elem.add_property(name='foo',value='bar/foo')
        elem.add_property(name='bar',value='only/bar')
        elem.add_property(name='testing',value='1', unit='mB')
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
        elem.add_property(name='foo',value='bar/foo')
        elem.add_property(name='bar',value='only/bar')
        elem.add_property(name='testing',value='1', unit='mB')
        self.assertEquals(elem.properties['foo'].value,'bar/foo')
        self.assertEquals(elem.properties['bar'].value,'only/bar')

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

    def test_setting_rfs_casting(self):
        elem = model.ConfmlSetting('foo', minLength=10)
        self.assertEquals(elem.get_rfs_cast('true'),True)
        self.assertEquals(elem.get_rfs_cast('false'),False)
        self.assertEquals(elem.set_rfs_cast(True),'true')
        self.assertEquals(elem.set_rfs_cast(False),'false')
        self.assertEquals(elem.set_rfs_cast(1),'true')

class TestConfmlSelectionSetting(unittest.TestCase):
    def test_create_selection_setting(self):
        elem = model.ConfmlSelectionSetting('foo')
        self.assertTrue(elem)
        self.assertEquals(elem.type, 'selection')
        self.assertEquals(elem.desc, None)
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
        elem = model.ConfmlMultiSelectionSetting('mset1')
        self.assertTrue(elem)
        self.assertEquals(elem.type, 'multiSelection')
        self.assertEquals(elem.desc, None)
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
        elem.value = "\"sel1\" \"sel2\""
        self.assertEquals(elem.type, 'multiSelection')
        self.assertEquals(elem.get_data_cast("\"sel1\" \"sel2\""), ["sel1", "sel2"])
        self.assertEquals(elem.get_value(), ["sel1", "sel2"])

    def test_set_data_cast(self):
        elem = model.ConfmlMultiSelectionSetting('mset3', type='multiSelection')
        self.assertEquals(elem.set_data_cast('"sel1" "sel2 with some spaces"'), '"sel1" "sel2 with some spaces"')
        self.assertEquals(elem.set_data_cast(["sel1", "sel2 with some spaces"]), '"sel1" "sel2 with some spaces"')
        self.assertEquals(elem.set_data_cast(["1", "1"]), '"1" "1"')
        self.assertEquals(elem.set_data_cast([1, 2, 3]), '"1" "2" "3"')


    def test_get_data_cast(self):
        elem = model.ConfmlMultiSelectionSetting('mset3', type='multiSelection')
        self.assertEquals(elem.get_data_cast('"sel1" "sel2 with some spaces"'), ["sel1", "sel2 with some spaces"])
        self.assertEquals(elem.get_data_cast('"sel1" "sel2 space" "foo bar"'), ["sel1", "sel2 space", "foo bar"])

    def test_setting_value_to_multiselection2(self):
        conf = model.ConfmlConfiguration('test.confml')
        elem = model.ConfmlMultiSelectionSetting('mset3', type='multiSelection')
        conf.add_feature(elem)
        elem.value = '"sel1" "sel2 with some spaces"'
        self.assertEquals(elem.type, 'multiSelection')
        self.assertEquals(elem.get_value(), ["sel1", "sel2 with some spaces"])
        elem.value = ["sel1", "sel2 with some spaces"]
        self.assertEquals(elem.get_value(), ["sel1", "sel2 with some spaces"])
        
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
        self.assertEquals(elem.get_value(), ["li1", "li2"])
        self.assertEquals(elem.get_data().get_value(), '"li1" "li2"')

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

    def test_setting_value_to_int(self):
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
        elem = model.ConfmlSequenceSetting('test')
        self.assertTrue(elem)
        self.assertEquals(elem.desc, None)

    def test_setting_with_properties_property(self):
        elem = model.ConfmlSequenceSetting('foo')
        elem.add_property(name='foo',value='bar/foo')
        elem.add_property(name='bar',value='only/bar')
        elem.add_property(name='testing',value='1', unit='mB')
        self.assertEquals(elem.properties['foo'].value,'bar/foo')
        self.assertEquals(elem.properties['bar'].value,'only/bar')

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

    def test_create_feature_seq_with_int_bool_settings_access_feature_value_with_property(self):
        config = api.Configuration('foo.confml')
        fea= model.ConfmlSequenceSetting("foo")
        fea.add_feature(model.ConfmlIntSetting('child1'))
        fea.add_feature(model.ConfmlBooleanSetting('child2'))
        fea.add_feature(model.ConfmlSetting('child3'))
        config.add_feature(fea)
        dview = config.get_default_view()
        foofea = dview.get_feature('foo')
        # Test adding a data row with array
        foofea.set_value([['1','2','3'],
                         ['4','5','6'],
                         ['7','8','9']
                         ])
        self.assertEquals(foofea.value, [['1','2','3'],
                                         ['4','5','6'],
                                         ['7','8','9']
                                        ])

        foofea.value = [['1','2','3'],
                         ['7','8','9']
                        ]
        
        self.assertEquals(foofea.data[0].value,['1','2','3'])
        self.assertEquals(foofea.data[1].value,['7','8','9'])
        self.assertEquals(foofea.data[1][1].value,'8')
        self.assertEquals(foofea.get_value(), [['1','2','3'],
                                               ['7','8','9']
                                               ])
        self.assertEquals(foofea.child1.value,['1','7'])

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
        self.assertEquals(max.value, '100')

    def test_create_minLength(self):
        min = model.ConfmlMinLength('100')
        self.assertEquals(min.value, '100')

class TestConfmlFacets(unittest.TestCase):
    def test_create_inclusive(self):
        min = model.ConfmlMinInclusive('-10')
        max = model.ConfmlMaxInclusive('10')
        self.assertEquals(min.value, '-10')
        self.assertEquals(max.value, '10')

    def test_create_exclusive(self):
        min = model.ConfmlMinExclusive('0')
        max = model.ConfmlMaxExclusive("9")
        self.assertEquals(min.value, '0')
        self.assertEquals(max.value, '9')

    def test_create_pattern(self):
        pattern = model.ConfmlPattern("[a-zA-Z]")
        self.assertEquals(pattern.value, "[a-zA-Z]")

    def test_create_totalDigits(self):
        digits = model.ConfmlTotalDigits("3")
        self.assertEquals(digits.value, '3')

class TestConfmlConfiguration(unittest.TestCase):
    def test_create_configuration(self):
        config = model.ConfmlConfiguration("test/foo/bar.jpg")
        self.assertEquals(config.meta, None)
        self.assertEquals(config.desc, None)
        self.assertEquals(config.name, 'test__foo__bar_jpg')
        self.assertEquals(config.ref, 'test__foo__bar_jpg')
        self.assertEquals(config.path, 'test/foo/bar.jpg')

#    def test_configuration_access_meta(self):
#        config = model.ConfmlConfiguration("test/foo/bar.jpg", meta={'test':'foo','bar':' hd dd'})
#        self.assertEquals(config.meta.dict, {'test':'foo','bar':' hd dd'})
#        self.assertEquals(config.meta['test'],'foo')
#        config.meta = {'test':'123'}
#        self.assertEquals(config.meta['test'],'123')
#        del config.meta
#        self.assertEquals(config.meta, None)
        
    def test_configuration_access_desc(self):
        config = model.ConfmlConfiguration("test/foo/bar.jpg", desc="testing description")
        self.assertEquals(config.desc, "testing description")
        config.desc = 'new desc'
        self.assertEquals(config.desc, "new desc")
        del config.desc
        self.assertEquals(config.desc, None)

class TestConfmlProperty(unittest.TestCase):
    def test_create_property(self):
        property = model.ConfmlProperty(name='test',value='foo', unit='kB')
        self.assertEquals(property.name, 'test')
        self.assertEquals(property.value, 'foo')
        self.assertEquals(property.unit, 'kB')
        property.name = 'testnew'
        property.value = 'foo faa'
        self.assertEquals(property.name, 'testnew')
        self.assertEquals(property.value, 'foo faa')
        