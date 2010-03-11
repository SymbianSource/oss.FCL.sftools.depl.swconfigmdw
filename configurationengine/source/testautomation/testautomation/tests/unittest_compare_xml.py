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
from testautomation import compare_xml

class TestGetXmlEncoding(unittest.TestCase):
    def assert_enc_eq(self, encoding, xml_data):
        self.assertEquals(encoding, compare_xml._get_xml_encoding(xml_data))
    
    def test_get_encoding(self):
        self.assert_enc_eq('ASCII',         u"""<?xml version="1.0" encoding="ASCII"?><root x="\u0084"/>""".encode('ascii', 'xmlcharrefreplace'))
        self.assert_enc_eq('ISO-8859-1',    u"""<?xml version="1.0" encoding = "ISO-8859-1"?><root x="\u0084"/>""".encode('latin1'))
        self.assert_enc_eq('utf-8',         u"""<?xml version="1.0" encoding='utf-8'?><root x="\u0084"/>""".encode('utf-8'))
        self.assert_enc_eq('UTF-16',        u"""<?xml encoding = 'UTF-16' version="1.0"?><root x="\u0084"/>""".encode('utf-16'))
        self.assert_enc_eq('',              u"""<?xml version="1.0"?><root x="\u0084"/>""".encode('utf-8'))
        self.assert_enc_eq('',              u"""<root x="\u0084"/>""".encode('utf-8'))

class TestCompareXml(unittest.TestCase):
    REF_DATA = """<?xml version="1.0" encoding="UTF-8"?>
<rootElem my_attr="jeje">
    <subElem>a sub-element</subElem>
    <subElem>another sub-element</subElem>
    <subElem>yet another sub-element</subElem>
    <subElem attr1="attribute 1" attr2="attribute 2"/>
</rootElem>"""
    
    def assert_comparison_result_equals(self, data1, data2, expected_result, msg=None, **kwargs):
        class DebugStream:
            def __init__(self):
                self.messages = []
            def write(self, data):
                self.messages.append(data)
        
        ds = DebugStream()
        kwargs['debug_stream'] = ds
        result = compare_xml.compare_xml_documents(data1, data2, **kwargs)
        if result != expected_result:
            d = []
            if msg != None: d.append(msg + '\n')
            d.append("Comparison results are not equal (expected %s, got %s)\n" % (expected_result, result))
            d.append("Debug output:\n")
            d.extend(ds.messages)
            self.fail(''.join(d))

    def test_identical(self):
        self.assert_comparison_result_equals(self.REF_DATA, self.REF_DATA, True)
    
    def test_different_whitespace(self):
        DATA = """<?xml version="1.0" encoding="UTF-8"?>
    <rootElem
    my_attr="jeje">
<subElem>a sub-element</subElem><subElem>another sub-element</subElem>
<subElem>yet another sub-element</subElem>
<subElem
    attr1="attribute 1"
    attr2="attribute 2"/>
    </rootElem>"""
        self.assert_comparison_result_equals(self.REF_DATA, DATA, True)

    def test_attrs_in_different_order(self):
        DATA = """<?xml version="1.0" encoding="UTF-8"?>
<rootElem my_attr="jeje">
    <subElem>a sub-element</subElem>
    <subElem>another sub-element</subElem>
    <subElem>yet another sub-element</subElem>
    <subElem attr2="attribute 2" attr1="attribute 1"/>
</rootElem>"""
        self.assert_comparison_result_equals(self.REF_DATA, DATA, True)
    
    def test_elements_in_different_order(self):
        REF_DATA = """<?xml version="1.0" encoding="UTF-8"?>
<rootElem my_attr="jeje">
    <subElem><x>1</x><y/><z z_attr="1"></z></subElem>
    <subElem><x>2</x><y/><z z_attr="2"></z></subElem>
    <subElem><x>3</x><y/><z z_attr="3"></z></subElem>
    <subElem><x><y></y><z/></x></subElem>
    <subElem attr1="attribute 1" attr2="attribute 2"/>
    <subElem attr1="attribute 1" attr2="attribute 2"/>
    <test attr="yeah"/>
</rootElem>"""
        DATA = """<?xml version="1.0" encoding="UTF-8"?>
<rootElem my_attr="jeje">
    <subElem attr2="attribute 2" attr1="attribute 1"/>
    <subElem><z z_attr="3"></z><y/><x>3</x></subElem>
    <subElem><x>1</x><y/><z z_attr="1"></z></subElem>
    <test attr="yeah"/>
    <subElem><x><z/><y/></x></subElem>
    <subElem><y/><x>2</x><z z_attr="2"></z></subElem>
    <subElem attr1="attribute 1" attr2="attribute 2"/>
</rootElem>"""
        self.assert_comparison_result_equals(REF_DATA, DATA, True)
    
    def test_different_root_contents(self):
        DATA = """<?xml version="1.0" encoding="UTF-8"?>
<rootElem my_attr="jeje">
some text content in root
    <subElem>a sub-element</subElem>
    <subElem>another sub-element</subElem>
    <subElem>yet another sub-element</subElem>
    <subElem attr1="attribute 1" attr2="attribute 2"/>
</rootElem>"""
        self.assert_comparison_result_equals(self.REF_DATA, DATA, False)
    
    def test_different_subelem_contents(self):
        DATA = """<?xml version="1.0" encoding="UTF-8"?>
<rootElem my_attr="jeje">
    <subElem>a sub-element (with different content)</subElem>
    <subElem>another sub-element</subElem>
    <subElem>yet another sub-element</subElem>
    <subElem attr1="attribute 1" attr2="attribute 2"/>
</rootElem>"""
        self.assert_comparison_result_equals(self.REF_DATA, DATA, False)
    
    def test_different_attrs_in_root(self):
        DATA = """<?xml version="1.0" encoding="UTF-8"?>
<rootElem my_attr="jeh">
    <subElem>a sub-element (with different content)</subElem>
    <subElem>another sub-element</subElem>
    <subElem>yet another sub-element</subElem>
    <subElem attr1="attribute 1" attr2="attribute 2"/>
</rootElem>"""
        self.assert_comparison_result_equals(self.REF_DATA, DATA, False)
    
    def test_missing_attrs_in_root(self):
        DATA = """<?xml version="1.0" encoding="UTF-8"?>
<rootElem>
    <subElem>a sub-element (with different content)</subElem>
    <subElem>another sub-element</subElem>
    <subElem>yet another sub-element</subElem>
    <subElem attr1="attribute 1" attr2="attribute 2"/>
</rootElem>"""
        self.assert_comparison_result_equals(self.REF_DATA, DATA, False)
    
    def test_different_attrs_in_subelem(self):
        DATA = """<?xml version="1.0" encoding="UTF-8"?>
<rootElem my_attr="jeje">
    <subElem>a sub-element (with different content)</subElem>
    <subElem>another sub-element</subElem>
    <subElem>yet another sub-element</subElem>
    <subElem attr1="attribute I" attr2="attribute II"/>
</rootElem>"""
        self.assert_comparison_result_equals(self.REF_DATA, DATA, False)
    
    def test_different_whitespace_in_subelem_content(self):
        DATA = """<?xml version="1.0" encoding="UTF-8"?>
<rootElem my_attr="jeje">
    <subElem>   a sub-element </subElem>
    <subElem>another sub-element</subElem>
    <subElem>yet another sub-element</subElem>
    <subElem attr1="attribute 1" attr2="attribute 2"/>
</rootElem>"""
        self.assert_comparison_result_equals(self.REF_DATA, DATA, True)
    
    def test_ignore_root_namespace(self):
        DATA = """<?xml version="1.0" encoding="UTF-8"?>
<rootElem xmlns:myns="http://my.namespace.com/schema" my_attr="jeje">
    <subElem>a sub-element</subElem>
    <subElem>another sub-element</subElem>
    <subElem>yet another sub-element</subElem>
    <subElem attr1="attribute 1" attr2="attribute 2"/>
</rootElem>"""
        self.assert_comparison_result_equals(self.REF_DATA, DATA, True)
    
    def test_ignore_namespace(self):
        DATA = """<?xml version="1.0" encoding="UTF-8"?>
<myns:rootElem xmlns:myns="http://my.namespace.com/schema" my_attr="jeje">
    <myns:subElem>a sub-element</myns:subElem>
    <myns:subElem>another sub-element</myns:subElem>
    <myns:subElem>yet another sub-element</myns:subElem>
    <myns:subElem attr1="attribute 1" attr2="attribute 2"/>
</myns:rootElem>"""
        self.assert_comparison_result_equals(self.REF_DATA, DATA, True, ignore_namespaces=True)
    
    def test_ignore_empty_tags(self):
        REF_DATA = """<?xml version="1.0" encoding="UTF-8"?>
<rootElem my_attr="jeje">
    <subElem>a sub-element</subElem>
    <subElem>
        <subSubElem>1</subSubElem>
        <subSubElem>2</subSubElem>
        <emptySubElem/>
    </subElem>
    <emptySubElem/>
</rootElem>"""
        DATA = """<?xml version="1.0" encoding="UTF-8"?>
<rootElem my_attr="jeje">
    <subElem>a sub-element</subElem>
    <subElem>
        <subSubElem>1</subSubElem>
        <subSubElem>2</subSubElem>
    </subElem>
</rootElem>"""
        self.assert_comparison_result_equals(REF_DATA, DATA, False)
        self.assert_comparison_result_equals(DATA, REF_DATA, False)
        self.assert_comparison_result_equals(REF_DATA, DATA, False, ignored_empty_tags=['/rootElem/emptySubElem'])
        self.assert_comparison_result_equals(DATA, REF_DATA, False, ignored_empty_tags=['/rootElem/emptySubElem'])
        self.assert_comparison_result_equals(REF_DATA, DATA, False, ignored_empty_tags=['/rootElem/subElem/emptySubElem'])
        self.assert_comparison_result_equals(DATA, REF_DATA, False, ignored_empty_tags=['/rootElem/subElem/emptySubElem'])
        self.assert_comparison_result_equals(REF_DATA, DATA, True, ignored_empty_tags=['/rootElem/emptySubElem', '/rootElem/subElem/emptySubElem'])
        self.assert_comparison_result_equals(DATA, REF_DATA, True, ignored_empty_tags=['/rootElem/emptySubElem', '/rootElem/subElem/emptySubElem'])
        #self.assert_comparison_result_equals(DATA, REF_DATA, True, ignored_empty_tags=['emptySubElem'])
        #self.assert_comparison_result_equals(REF_DATA, DATA, False, ignored_empty_tags=[('emptySubElem', 1)])
        #self.assert_comparison_result_equals(DATA, REF_DATA, False, ignored_empty_tags=[('emptySubElem', 1)])
        #self.assert_comparison_result_equals(REF_DATA, DATA, False, ignored_empty_tags=[('emptySubElem', 2)])
        #self.assert_comparison_result_equals(DATA, REF_DATA, False, ignored_empty_tags=[('emptySubElem', 2)])
        #self.assert_comparison_result_equals(REF_DATA, DATA, True, ignored_empty_tags=[('emptySubElem', 1), ('emptySubElem', 2)])
        #self.assert_comparison_result_equals(DATA, REF_DATA, True, ignored_empty_tags=[('emptySubElem', 1), ('emptySubElem', 2)])
    
    def test_check_encoding(self):
        DATA_DICT = {
            'ASCII':        u"""<?xml version="1.0" encoding="ASCII"?><root x="\u0084"/>""".encode('ascii', 'xmlcharrefreplace'),
            'ISO-8859-1':   u"""<?xml version="1.0" encoding = "ISO-8859-1"?><root x="\u0084"/>""".encode('latin1'),
            'UTF8':         u"""<?xml version="1.0" encoding='UTF-8'?><root x="\u0084"/>""".encode('utf-8'),
            'UTF-16':       u"""<?xml version="1.0" encoding="UTF-16"?><root x="\u0084"/>""".encode('utf-16'),
            'None1':        u"""<?xml version="1.0"?><root x="\u0084"/>""".encode('utf-8'),
            'None2':        u"""<root x="\u0084"/>""".encode('utf-8'),
        }
        
        for key1 in DATA_DICT.keys():
            for key2 in DATA_DICT.keys():
                if key1 != key2 and not (key1.startswith('None') or key2.startswith('None')):
                    self.assert_comparison_result_equals(
                        DATA_DICT[key1], DATA_DICT[key2],
                        False, "Encoding check failed for '%s' vs. '%s'" % (key1, key2),
                        check_encoding=True)
                    self.assert_comparison_result_equals(
                        DATA_DICT[key1], DATA_DICT[key2],
                        True, "Comparison without encoding check failed for '%s' vs. '%s'" % (key1, key2),
                        check_encoding=False)