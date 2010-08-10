# *-* coding: utf-8 *-*
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

import unittest, os, sys
import logging

try:
    from cElementTree import ElementTree, ElementInclude
except ImportError:
    try:    
        from elementtree import ElementTree, ElementInclude
    except ImportError:
        try:
            from xml.etree import cElementTree as ElementTree
        except ImportError:
            from xml.etree import ElementTree

from templatemlplugin import templatemlplugin
from testautomation.base_testcase import BaseTestCase
from testautomation.utils import hex_to_bindata

from cone.public import exceptions,plugin,api,utils
from cone.storage import filestorage
from cone.confml import implml

# Hardcoded value of testdata folder that must be under the current working dir
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
testdata  = os.path.join(ROOT_PATH,'project')

TEMPML_DOC1 = "<?xml version=\"1.0\" encoding=\"ascii\"?> " \
          "<templateml xmlns=\"http://www.s60.com/xml/templateml/1\" xmlns:xi=\"http://www.w3.org/2001/XInclude\">" \
            "<desc>Desc</desc>" \
            "<output file=\"test.txt\" encoding=\"UTF-16\">" \
                "<template extension=\"foo/foobar:MyClass\">ABCDF</template>" \
             "</output>" \
             "<filter name=\"test_filter\">lambda a,b: a+b</filter>" \
          "</templateml>"
          
TEMPML_DOC2 = "<?xml version=\"1.0\" encoding=\"ascii\"?> " \
          "<templateml xmlns=\"http://www.s60.com/xml/templateml/1\" xmlns:xi=\"http://www.w3.org/2001/XInclude\">" \
            "<desc>Desc</desc>" \
            "<output file=\"test.txt\" encoding=\"UTF-16\">" \
                "<template extension=\"foo/foobar:MyClass\"><xi:include href=\"project/templates/template.xml\" parse=\"xml\"/></template>" \
             "</output>" \
             "<filter name=\"test_filter\">lambda a,b: a+b</filter>" \
          "</templateml>"

TEMPML_DOC3 = "<?xml version=\"1.0\" encoding=\"ascii\"?> " \
          "<templateml xmlns=\"http://www.s60.com/xml/templateml/1\" xmlns:xi=\"http://www.w3.org/2001/XInclude\">" \
            "<desc>Desc</desc>" \
            "<output file=\"test.txt\" encoding=\"UTF-16\">" \
                "<template extension=\"foo/foobar:MyClass\"><xi:include href=\"project/templates/template.xml\" parse=\"xml\"/></template>" \
             "</output>" \
             "<filter name=\"test_filter\">lambda a,b: a+b</filter>" \
          "</templateml>"

TEMPML_DOC4 = "<?xml version=\"1.0\" encoding=\"ascii\"?> " \
          "<templateml xmlns=\"http://www.s60.com/xml/templateml/1\">" \
            "<output file=\"test.txt\" encoding=\"ascii\">" \
                "<template file=\"../../templates/template.xml\"/>" \
             "</output>" \
             "<filter name=\"test_filter\" file=\"../../filter/filter.py\"/>" \
          "</templateml>"

TEMPML1 = "<ns0:output encoding=\"ASCII\" file=\"test.txt\" xmlns:ns0=\"http://www.s60.com/xml/templateml/1\" newline=\"win\">" \
          "<ns0:template extension=\"foo/foobar:MyClass\">ABCDF</ns0:template>" \
          "</ns0:output>"

TEMPML1_LINUX = "<ns0:output encoding=\"ASCII\" file=\"test.txt\" xmlns:ns0=\"http://www.s60.com/xml/templateml/1\">" \
          "<ns0:template extension=\"foo/foobar:MyClass\" newline=\"unix\">ABCDF</ns0:template>" \
          "</ns0:output>"

TEMPML2 = "<ns0:output encoding=\"ASCII\" file=\"test.txt\" xmlns:ns0=\"http://www.s60.com/xml/templateml/1\" xmlns:xi=\"http://www.w3.org/2001/XInclude\">" \
          "<ns0:template extension=\"foo/foobar:MyClass\">" \
          "include AABBCC" \
          "</ns0:template>" \
          "</ns0:output>"

TEMPML3 = "<ns0:output encoding=\"ASCII\" file=\"test.txt\" xmlns:ns0=\"http://www.s60.com/xml/templateml/1\" xmlns:xi=\"http://www.w3.org/2001/XInclude\">" \
          "<ns0:template extension=\"foo/foobar:MyClass\">" \
          "include AABBCC" \
          "</ns0:template>" \
          "<filter name=\"test_filter\">lambda a,b: a+b</filter>" \
          "</ns0:output>"

TEMPML4 = "<ns0:output encoding=\"ASCII\" file=\"test.txt\" xmlns:ns0=\"http://www.s60.com/xml/templateml/1\" xmlns:xi=\"http://www.w3.org/2001/XInclude\">" \
          "<ns0:template file=\"../../templates/template.xml\"/>" \
          "<filter name=\"test_filter\" file=\"../../filter/filter.py\"/>" \
          "</ns0:output>"
          
          
def impl_from_resource(resource_ref, configuration):
    impls = plugin.ImplFactory.get_impls_from_file(resource_ref, configuration)
    assert len(impls) == 1
    return impls[0]
          
class TestTemplatemlPlugin(BaseTestCase):    
    def setUp(self):
        self.curdir = os.getcwd()
        self.output = os.path.join(ROOT_PATH, 'output')
        os.chdir(os.path.join(ROOT_PATH))

    def tearDown(self):
        os.chdir(self.curdir)
    
    def load_config(self, config):
        fs = filestorage.FileStorage(testdata)
        p = api.Project(fs)
        return p.get_configuration(config)
    
    def load_impl(self, resource_ref, config='root1.confml'):
        configuration = self.load_config(config)
        pattern = '^' + resource_ref.replace('.', r'\.') + '$'
        impls = plugin.get_impl_set(configuration, pattern)
        impls.output = self.output
        impl_list = impls.get_implementations_by_file(resource_ref)
        self.assertEquals(1, len(impl_list))
        return (configuration,impl_list[0])
    
    def test_parse_desc(self):
        (config,impl) = self.load_impl('Layer1/implml/file1.templateml')
        self.assertEqual("Description field text", impl.reader.desc)

    def test_parse_output_with_file_ref(self):
        (config,impl) = self.load_impl('Layer1/implml/output_with_ref.templateml')
        self.assertEquals(impl.list_output_files(), [os.path.normpath('confmlref_filename.txt')])
        
    def test_parse_outputs(self):
        (config,impl) = self.load_impl('Layer1/implml/file1.templateml')
        outputs = []
        output1 = templatemlplugin.OutputFile()
        output1.set_encoding("UTF-16")
        output1.set_filename("test.txt")
        output1.set_path('')
        output1.set_newline('unix')
        temp1 = templatemlplugin.TempFile()
        temp1.set_template(u'ABC kissa k\xe4velee')
        output1.set_template(temp1)
        outputs.append(output1)

        output2 = templatemlplugin.OutputFile()
        output2.set_encoding("UTF-16")
        output2.set_filename("test2.txt")
        output2.set_path("output")
        output2.set_newline('win')
        temp2 = templatemlplugin.TempFile()
        temp2.set_template('AABBCC')
        output2.set_template(temp2)
        outputs.append(output2)

        output3 = templatemlplugin.OutputFile()
        output3.set_encoding("UTF-8")
        output3.set_filename("test3.txt")
        output3.set_path('')
        temp3 = templatemlplugin.TempFile()
        temp3.set_template(u'ABC kissa k\xe4velee')
        output3.set_template(temp3)

        outputs.append(output3)
        
        self.assertNotEqual(impl.reader.outputs, None)
        self.assertEqual(outputs[0].encoding, impl.reader.outputs[0].encoding)
        self.assertEqual(outputs[0].filename, impl.reader.outputs[0].filename)
        self.assertEqual(outputs[0].path, impl.reader.outputs[0].path)
        self.assertEqual(outputs[0].newline, impl.reader.outputs[0].newline)
        self.assertEqual(outputs[0].template.template, impl.reader.outputs[0].template.template)
        self.assertEqual(outputs[0].template.extensions, impl.reader.outputs[0].template.extensions)
        self.assertEqual(outputs[0].template.filters, impl.reader.outputs[0].template.filters)
        self.assertEqual(outputs[0].template, impl.reader.outputs[0].template)
        self.assertEqual(outputs[0], impl.reader.outputs[0])

        self.assertEqual(outputs[1].encoding, impl.reader.outputs[1].encoding)
        self.assertEqual(outputs[1].filename, impl.reader.outputs[1].filename)
        self.assertEqual(outputs[1].path, impl.reader.outputs[1].path)
        self.assertEqual(outputs[1].newline, impl.reader.outputs[1].newline)
        #self.assertEqual(outputs[1].template.template, impl.reader.outputs[1].template.template)
        self.assertEqual(outputs[1].template.extensions, impl.reader.outputs[1].template.extensions)
        self.assertEqual(outputs[1].template.filters, impl.reader.outputs[1].template.filters)
        #self.assertEqual(outputs[1].template, impl.reader.outputs[1].template)
        #self.assertEqual(outputs[1], impl.reader.outputs[1])

        self.assertEqual(outputs[2].encoding, impl.reader.outputs[2].encoding)
        self.assertEqual(outputs[2].filename, impl.reader.outputs[2].filename)
        self.assertEqual(outputs[2].path, impl.reader.outputs[2].path)
        #self.assertEqual(outputs[2].template.template, impl.reader.outputs[2].template.template)
        self.assertEqual(outputs[2].template.extensions, impl.reader.outputs[2].template.extensions)
        self.assertEqual(outputs[2].template.filters, impl.reader.outputs[2].template.filters)
        #self.assertEqual(outputs[2].template, impl.reader.outputs[2].template)

        #self.assertEqual(outputs[2], impl.reader.outputs[2])

    def test_parse_outputfile(self):
        output1 = templatemlplugin.OutputFile()
        output2 = templatemlplugin.OutputFile()
        
        self.assertEqual(output1, output2)
        self.assertEqual(output1.encoding, output2.encoding)
        self.assertEqual(output1.path, output2.path)
        self.assertEqual(output1.filename, output2.filename)
        
        output1.set_encoding("utf-8")
        output2.set_encoding("utf-8")
        
        self.assertEqual(output1, output2)# utf-8, utf-8
        
        output1.set_encoding("utf-16")
        
        self.assertNotEqual(output1, output2)#utf-16, utf-8
        
        output2.set_encoding("utf-16")
        
        self.assertEqual(output1, output2)#utf-16, utf-16

    def test_parse_template(self):
        reader = templatemlplugin.TemplatemlImplReader()
        reader.fromstring(TEMPML_DOC1)
        
        temp1 = reader.parse_template(ElementTree.fromstring(TEMPML1))
        temp2 = templatemlplugin.TempFile()
        temp2.set_template("ABCDF")
        
        self.assertEqual(temp1.template, temp2.template)
        self.assertEqual(temp1.extensions, temp2.extensions)
        self.assertEqual(temp1.filters, temp2.filters)
        self.assertEqual(temp1, temp2)

    def test_parse_template_from_xinclude(self):
        try:
            reader = templatemlplugin.TemplatemlImplReader()
            reader.fromstring(TEMPML_DOC2)
            
            temp1 = reader.parse_template(ElementTree.fromstring(TEMPML2))
            temp2 = templatemlplugin.TempFile()
            temp2.set_template("include AABBCC")
        except exceptions.ParseError, e:
            self.fail("Known bug: ticket #2007")
        
        self.assertEqual(temp1.template, temp2.template)
        self.assertEqual(temp1.extensions, temp2.extensions)
        self.assertEqual(temp1.filters, temp2.filters)
        self.assertEqual(temp1, temp2)

    def test_parse_template_filter(self):
        try:
            reader = templatemlplugin.TemplatemlImplReader()
            reader.fromstring(TEMPML_DOC3)
            filters1 = reader.filters
            filter2 = templatemlplugin.Filter()
            filter2.set_code("lambda a,b: a+b")
            filter2.set_name("test_filter")
        except exceptions.ParseError, e:
            self.fail( "Known bug: ticket #2007")
        self.assertEqual(filters1[0].name, filter2.name)
        self.assertEqual(filters1[0].code, filter2.code)
        self.assertEqual(filters1[0], filter2)
        
    def test_parse_template_filter_2(self):
        class DummyConfiguration(object):
            def get_resource(self, ref):
                class DummyResource(object):
                    def read(self): return ''
                    def close(self): return None
                return DummyResource()
            def get_default_view(self): return None
        reader = templatemlplugin.TemplatemlImplReader('foo/implml/bar.implml', DummyConfiguration())
        reader.fromstring(TEMPML_DOC4)
        
        filters1 = reader.filters
        filter2 = templatemlplugin.Filter()
        filter2.set_code(None)
        filter2.set_name("test_filter")
        filter2.set_path("../../filter/filter.py")
        temp1 = reader.parse_template(ElementTree.fromstring(TEMPML4))
        temp2 = templatemlplugin.TempFile()
        temp2.set_template('')
        temp2.set_path('')

        self.assertEqual(filters1[0].name, filter2.name)
        self.assertEqual(filters1[0].code, filter2.code)
        self.assertEqual(filters1[0].path, filter2.path)
        self.assertEqual(filters1[0], filter2)
        self.assertEqual(temp1.template, temp2.template)
        self.assertEqual(temp1.extensions, temp2.extensions)
        self.assertEqual(temp1.filters, temp2.filters)
        self.assertEqual(temp1, temp2)
        
    def test_simple_generate_prj(self):
        
        self.remove_if_exists(os.path.normpath("output/output/test.txt"))
        
        (config,impl) = self.load_impl('Layer1/implml/file2.templateml')
        #impl.context = {'name' : 'some value'}
        gc = plugin.GenerationContext(configuration=config)
        impl.generate(gc)
        
        self.assertTrue(os.path.exists(os.path.normpath("output/output/test.txt")))
        result_file = None
        try:
            result_file = open(os.path.normpath("output/output/test.txt"))
            for line in result_file:
                self.assertTrue(line == "include AABBCC")
        finally:
            if result_file != None: result_file.close()
    
    def test_simple_generate_newline(self):
        
        self.remove_if_exists(os.path.normpath("output/output/test_newline_win.txt"))
        self.remove_if_exists(os.path.normpath("output/output/test_newline_unix.txt"))
        
        (config,impl) = self.load_impl('Layer1/implml/newline.templateml')
        gc = plugin.GenerationContext(configuration=config)
        impl.generate(gc)
        
        self.assertTrue(os.path.exists(os.path.normpath("output/output/test_newline_win.txt")))
        self.assertTrue(os.path.exists(os.path.normpath("output/output/test_newline_unix.txt")))

        result_file_win = None
        try:
            result_file_win = open(os.path.normpath("output/output/test_newline_win.txt"),'rb')
            line = result_file_win.read()
            self.assertEquals(line, "line1\r\nline2")
        finally:
            if result_file_win != None: result_file_win.close()

        result_file_unix = None
        try:
            result_file_unix = open(os.path.normpath("output/output/test_newline_unix.txt"), 'rb')
            line = result_file_unix.read()
            self.assertEquals(line, "line1\nline2")
        finally:
            if result_file_unix != None: result_file_unix.close()

    def test_simple_generate_prj3(self):
        
        self.remove_if_exists(os.path.normpath("output/output/test3.txt"))
        
        (config,impl) = self.load_impl('Layer1/implml/file3.templateml')
        gc = plugin.GenerationContext(configuration=config)
        impl.generate(gc)
        
        self.assertTrue(os.path.exists(os.path.normpath("output/output/test3.txt")))
        result_file = None
        try:
            result_file = open(os.path.normpath("output/output/test3.txt"))
            for line in result_file:
                self.assertTrue(line == "'Hello John Doe!'")
        finally:
            if result_file != None: result_file.close()


    def test_simple_generate_prj4_with_filters(self):
        
        self.remove_if_exists(os.path.normpath("output/output/test4a.txt"))
        self.remove_if_exists(os.path.normpath("output/output/test4b.txt"))
        self.remove_if_exists(os.path.normpath("output/output/test4c.txt"))
        self.remove_if_exists(os.path.normpath("output/output/test4d.txt"))
        
        (config,impl) = self.load_impl('Layer1/implml/file4.templateml')
        #impl.context = {'name' : 'John Doe'}
        gc = plugin.GenerationContext(configuration=config)
        impl.generate(gc)
        
        self.assertTrue(os.path.exists(os.path.normpath("output/output/test4a.txt")))
        self.assertTrue(os.path.exists(os.path.normpath("output/output/test4b.txt")))
        self.assertTrue(os.path.exists(os.path.normpath("output/output/test4c.txt")))
        self.assertTrue(os.path.exists(os.path.normpath("output/output/test4d.txt")))
        
        result_file1 = None
        result_file2 = None
        result_file3 = None
        result_file4 = None
        
        try:
            result_file1 = open(os.path.normpath("output/output/test4a.txt"))
            result_file2 = open(os.path.normpath("output/output/test4b.txt"))
            result_file3 = open(os.path.normpath("output/output/test4c.txt"))
            result_file4 = open(os.path.normpath("output/output/test4d.txt"))
            
            if result_file1 != None: 
                for line in result_file1:
                    self.assertTrue(line == "'Hello John Doe!'")
            else:
                self.fail("No result file found: output/output/test4a.txt")
            
            if result_file2 != None: 
                for line in result_file2:
                    self.assertTrue(line == "'Hello John Doe again!'")
            else:
                self.fail("No result file found: output/output/test4b.txt")
            
            if result_file3 != None:
                for line in result_file3:
                    self.assertTrue(line == "2+3=5")
            else:
                self.fail("No result file found: output/output/test4c.txt")

            if result_file4 != None:
                for line in result_file4:
                    self.assertTrue(line == "--6")
            else:
                self.fail("No result file found: output/output/test4d.txt")
                
        finally:
            if result_file1 != None: result_file1.close()
            if result_file2 != None: result_file2.close()
            if result_file3 != None: result_file3.close()
            if result_file4 != None: result_file4.close()

    def test_simple_generate_prj_extfiles_with_filters(self):
        
        self.remove_if_exists(os.path.normpath("output/output/test_ext_temp_file.txt"))
        
        (config,impl) = self.load_impl('Layer1/implml/external_tempfile.templateml')
        gc = plugin.GenerationContext(configuration=config)
        impl.generate(gc)
        
        self.assertTrue(os.path.exists(os.path.normpath("output/output/test_ext_temp_file.txt")))
        
        result_file1 = None
        
        try:
            result_file1 = open(os.path.normpath("output/output/test_ext_temp_file.txt"))
            lines = 0

            if result_file1 != None: 
                for line in result_file1:
                    self.assertTrue(line == "2+3=-1")
                    lines += 1
            else:
                self.fail("No result file found: output/output/test_ext_temp_file.txt")
            
            self.assertTrue(lines == 1, "Wrong number of lines generated.")
            
        finally:
            if result_file1 != None: result_file1.close()

    def test_generate_prj1(self):
        
        self.remove_if_exists(os.path.normpath("output/output/test5a.txt"))
        
        (config,impl) = self.load_impl('Layer1/implml/file5.templateml')
        gc = plugin.GenerationContext(configuration=config)
        impl.generate(gc)
        self.assertTrue(os.path.exists(os.path.normpath("output/output/test5a.txt")))
        
        result_file1 = None
        try:
            result_file1 = open(os.path.normpath("output/output/test5a.txt"))
            
            if result_file1 != None: 
                for line in result_file1:
                    self.assertTrue(line == "'Hello John Doe'")
            else:
                self.fail("No result file found: output/output/test5a.txt")
        finally:
            if result_file1 != None: result_file1.close()

    def test_generate_access_configuration(self):
        
        self.remove_if_exists(os.path.normpath("output/access_configuration.txt"))
        
        (config,impl) = self.load_impl('Layer1/implml/access_configuration.templateml')
        gc = plugin.GenerationContext(configuration=config)
        impl.generate(gc)
        self.assertTrue(os.path.exists(os.path.normpath("output/access_configuration.txt")))
        
        result_file1 = None
        try:
            result_file1 = open(os.path.normpath("output/access_configuration.txt"))
            data = result_file1.read() 
            if result_file1 != None: 
                self.assertTrue(data.startswith("Configuration name: root1.confml"))
            else:
                self.fail("No result file found: output/access_configuration.txt")
        finally:
            if result_file1 != None: result_file1.close()
    
    def test_create_context_dict1(self):
        (config,impl) = self.load_impl('Layer1/implml/file6.templateml')
        impl.context = impl.create_dict()
        gc = plugin.GenerationContext(configuration=config)
        impl.generate(gc)
    
    def test_list_output_files(self):
        (config,impl) = self.load_impl('Layer1/implml/file1.templateml')
        impl.set_output_root('outdir')
        output_files = impl.list_output_files()
        expected = map(lambda n: os.path.normpath(n), [
            'outdir/test.txt',
            'outdir/output/test2.txt',
            'outdir/test3.txt',
            'outdir/output/test4.txt',
            'outdir/some/test/path/test5.txt',
        ])
        self.assertEquals(sorted(output_files), sorted(expected))
    
    def test_has_ref(self):
        (config,impl) = self.load_impl('Layer1/implml/has_ref_template_test2.templateml')
        self.assertEquals(impl.has_ref('Feature1.StringSetting_not_found'), False)
        self.assertEquals(impl.has_ref('Feature1.StringSetting1'), True)
        self.assertEquals(impl.has_ref('Feature2'), True)
        self.assertEquals(impl.has_ref('Feature2.set1.sub1'), True)
        self.assertEquals(impl.has_ref('Feature2.set1.sub2'), True)
        self.assertEquals(impl.has_ref('Feature1.UnicodeValueSetting'), True)
    
    def test_has_ref_external_template(self):
        (config,impl) = self.load_impl('Layer1/implml/has_ref_template_test3.templateml')
        self.assertEquals(impl.has_ref('Feature1.StringSetting_not_found'), False)
        self.assertEquals(impl.has_ref('Feature1.StringSetting1'), True)
        self.assertEquals(impl.has_ref('Feature2'), True)
        self.assertEquals(impl.has_ref('Feature2.set1.sub1'), True)
        self.assertEquals(impl.has_ref('Feature2.set1.sub2'), True)
        self.assertEquals(impl.has_ref('Feature1.UnicodeValueSetting'), True)

    def test_has_ref_with_featree(self):
        (config,impl) = self.load_impl('Layer1/implml/has_ref_template_test.templateml')
        self.assertEquals(impl.has_ref('Feature1.StringSetting'), True)
        self.assertEquals(impl.has_ref('Feature2.StringSetting'), True)
    
    def test_unicode_in_template_and_value(self):
        OUTPUT_DIR = os.path.join(ROOT_PATH, 'output', 'unicode_test')
        self.remove_if_exists(OUTPUT_DIR)
        
        fs = filestorage.FileStorage(testdata)
        p = api.Project(fs)
        config = p.get_configuration('root1.confml')
        impls = plugin.get_impl_set(config,'unicode_template_test\.templateml$')
        gc = plugin.GenerationContext(output=OUTPUT_DIR,
                                      configuration=config)
        impls.generate(gc)
        self.assert_exists_and_contains_something(os.path.join(OUTPUT_DIR, "unicode_template_test.txt"))
        
        # Check that the output exists and contains expected lines
        f = open(os.path.join(OUTPUT_DIR, "unicode_template_test.txt"), "rb")
        try:        data = f.read().decode('utf-8')
        finally:    f.close()
        self.assertTrue(data.find(u'Value of Feature1.UnicodeValueSetting: カタカナ') != -1)
        self.assertTrue(data.find(u'Unicode from template: ελληνικά') != -1)
    
    def test_create_context_dict_and_list(self):
        config = self.load_config('create_dict_test.confml')
        impls = plugin.get_impl_set(config, r'^create_dict_test/implml/test\.templateml$')
        self.assertEquals(1, len(impls))
        impl = iter(impls).next()
        context = impl.create_dict()
        feat_tree = context['feat_tree']
        feat_list = context['feat_list']
        self.assertEqual(context['configuration'], config)
        
        # Check the created dictionary
        expected_tree_file = os.path.join(ROOT_PATH, 'create_dict_test', 'expected_tree.txt')
        expected_tree = eval(self.read_data_from_file(expected_tree_file).replace('\r', ''))
        if feat_tree != expected_tree:
            dir = os.path.join(ROOT_PATH, "temp", "create_dict_test", "tree")
            self.create_dir(dir)
            filename = os.path.join(dir, "expected.txt")
            self.write_data_to_file(filename, self.feature_tree_to_str(expected_tree))
            filename = os.path.join(dir, "actual.txt")
            self.write_data_to_file(filename, self.feature_tree_to_str(feat_tree))
            self.fail("Feature tree is not what was expected, see the files in '%s'" % dir)
        
        # Check the created list
        expected_list_file = os.path.join(ROOT_PATH, 'create_dict_test', 'expected_list.txt')
        expected_list = eval(self.read_data_from_file(expected_list_file).replace('\r', ''))
        if feat_list != expected_list:
            dir = os.path.join(ROOT_PATH, "temp", "create_dict_test", "list")
            self.create_dir(dir)
            filename = os.path.join(dir, "expected.txt")
            self.write_data_to_file(filename, self.feature_list_to_str(expected_list))
            filename = os.path.join(dir, "actual.txt")
            self.write_data_to_file(filename, self.feature_list_to_str(feat_list))
            self.fail("Feature list is not what was expected, see the files in '%s'" % dir)
    
    def feature_tree_to_str(self, d, indent_amount=0):
        """
        Pretty-print a feature tree dictionary into a string.
        """
        INDENT_AMOUNT = 4
        indent = indent_amount * ' '
        temp = ['{']
        if len(d) > 0: temp.append('\n')
        
        indent += (INDENT_AMOUNT + indent_amount) * ' '
        
        # Function for sorting the dict contents so that keys starting with
        # '_' are first
        def key_func(key_and_value):
            key = key_and_value[0]
            if key.startswith('_'): return '\x00' + key
            else:                   return key
        
        for key, value in sorted(d.items(), key=key_func):
            temp.append(indent)
            if isinstance(value, (dict, templatemlplugin.FeatureDictProxy)):
                temp.append("%r: %s," % (key, self.feature_tree_to_str(value, indent_amount + INDENT_AMOUNT)))
            else:
                temp.append("%r: %r," % (key, value))
            temp.append('\n')
            
        if len(d) > 0: temp.append(indent)
        temp.append('}')
        return ''.join(temp)
    
    def feature_list_to_str(self, lst):
        """
        Pretty-print a feature list into a string.
        """
        temp = ['[\n']
        for item in lst:
            if isinstance(item, (dict, templatemlplugin.FeatureDictProxy)):  temp.append(self.feature_tree_to_str(item))
            else:                       temp.append(repr(item))
            temp.append(',\n')
        temp.append(']')
        return ''.join(temp)
    
    
    def test_utf_bom_support(self):
        OUTPUT_DIR = os.path.join(ROOT_PATH, 'temp/utf_bom_test')
        self.recreate_dir(OUTPUT_DIR)
        (config,impl) = self.load_impl('Layer1/implml/utf_bom_test.templateml')
        gc = plugin.GenerationContext(output=OUTPUT_DIR,
                                      configuration=config)
        impl.generate(gc)
        
        def check(file, contents):
            FILE = os.path.join(OUTPUT_DIR, file)
            self.assert_file_content_equals(FILE, contents)
        
        h = hex_to_bindata
        
        # The all-around default should be UTF-8 without BOM
        check('default.txt',           h('31 30 30 E282AC'))
        
        check('iso_8859_15_default.txt',    h('31 30 30 A4'))
        check('utf8_default.txt',           h('31 30 30 E282AC'))
        check('utf16be_default.txt',        h('0031 0030 0030 20AC'))
        check('utf16le_default.txt',        h('3100 3000 3000 AC20'))

        check('iso_8859_15_no_bom.txt',     h('31 30 30 A4'))
        check('utf8_no_bom.txt',            h('31 30 30 E282AC'))
        check('utf16be_no_bom.txt',         h('0031 0030 0030 20AC'))
        check('utf16le_no_bom.txt',         h('3100 3000 3000 AC20'))
        
        check('iso_8859_15_with_bom.txt',   h('31 30 30 A4'))
        check('utf8_with_bom.txt',          h('EFBBBF 31 30 30 E282AC'))
        check('utf16be_with_bom.txt',       h('FEFF 0031 0030 0030 20AC'))
        check('utf16le_with_bom.txt',       h('FFFE 3100 3000 3000 AC20'))
        
        if sys.byteorder == 'little':
            check('utf16_default.txt',  h('FFFE 3100 3000 3000 AC20'))
            check('utf16_no_bom.txt',   h('3100 3000 3000 AC20'))
            check('utf16_with_bom.txt', h('FFFE 3100 3000 3000 AC20'))
        else:
            check('utf16_default.txt',  h('FEFF 0031 0030 0030 20AC'))
            check('utf16_no_bom.txt',   h('0031 0030 0030 20AC'))
            check('utf16_with_bom.txt', h('FEFF 0031 0030 0030 20AC'))
    
    def test_invalid_encoding(self):
        DATA = """<?xml version="1.0" encoding="UTF-8"?>
          <templateml xmlns=\"http://www.s60.com/xml/templateml/1\">
            <output file="test.txt" encoding="foocode">foo</output>
          </templateml>"""
        reader = templatemlplugin.TemplatemlImplReader()
        reader.fromstring(DATA)
        self.assertRaises(exceptions.ParseError, reader.expand_output_refs_by_default_view)
    
    def test_generate_from_template_with_feat_tree_iteration(self):
        OUTPUT_DIR = os.path.join(ROOT_PATH, 'temp/feat_tree_iteration')
        self.recreate_dir(OUTPUT_DIR)
        (config,impl) = self.load_impl('Layer1/implml/feat_tree_iteration_test.templateml')
        gc = plugin.GenerationContext(output=OUTPUT_DIR,
                                      configuration=config)
        impl.generate(gc)
        
        OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'feat_tree_iteration_test.txt')
        self.assert_exists_and_contains_something(OUTPUT_FILE)
        self.assert_file_content_equals(OUTPUT_FILE,
            u"\n"\
            u"Boolean setting = True\n"\
            u"File setting = default_file.txt\n"\
            u"Folder setting = default_folder\n"\
            u"Int setting = 10\n"\
            u"Real setting = 3.14\n"\
            u"Selection setting = 1\n"\
            u"Sequence setting = [[[None, None], 1.25, [None, None], 128, 'def1', False, '1'], [[None, None], 1.5, [None, None], 256, 'def2', False, '1']]\n"\
            u"String setting = John Doe\n"\
            u"String for unicode value test = カタカナ\n".encode('utf-8'))
    
    def test_generate_from_template_generation_context_accessed(self):
        OUTPUT_DIR = os.path.join(ROOT_PATH, 'temp/access_context')
        self.recreate_dir(OUTPUT_DIR)
        (config,impl) = self.load_impl('Layer1/implml/access_context.templateml')
        context = plugin.GenerationContext(output=OUTPUT_DIR,
                                           configuration=config)
        context.tags = {'sometag': ['foo', 'bar']}
        impl.generate(context)
        
        OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'access_context.txt')
        self.assert_exists_and_contains_something(OUTPUT_FILE)
        self.assert_file_content_equals(OUTPUT_FILE,
            "Tags: {'sometag': ['foo', 'bar']}")
    
    def test_invalid_ref_in_template(self):
        OUTPUT_DIR = os.path.join(ROOT_PATH, 'temp/invalid_ref')
        self.recreate_dir(OUTPUT_DIR)
        (config,impl) = self.load_impl('Layer1/implml/invalid_ref.templateml')
        context = plugin.GenerationContext(output=OUTPUT_DIR,
                                           configuration=config)
        
        log_file, handler, logger = self._prepare_log('invalid_refs.log')
        impl.generate(context)
        logger.removeHandler(handler)
        
        self.assert_file_content_equals(os.path.join(OUTPUT_DIR, 'invalid_ref_1.txt'), "")
        self.assert_file_content_equals(os.path.join(OUTPUT_DIR, 'invalid_ref_2.txt'), "")
        self.assert_file_content_equals(os.path.join(OUTPUT_DIR, 'invalid_ref_3.txt'), "")
        
        self.assert_file_contains(log_file,
            ["TemplatemlImpl(ref='Layer1/implml/invalid_ref.templateml', type='templateml', lineno=2): Failed to generate output: NotFound: Feature 'Foo' not found",
             "TemplatemlImpl(ref='Layer1/implml/invalid_ref.templateml', type='templateml', lineno=2): Failed to generate output: NotFound: Feature 'Feature1.Nonexistent' not found",
             "TemplatemlImpl(ref='Layer1/implml/invalid_ref.templateml', type='templateml', lineno=2): Failed to generate output: NotFound: Feature 'Feature1.SequenceSetting.Nonexistent' not found"])
    
    def _prepare_log(self, log_file, level=logging.DEBUG, formatter="%(levelname)s - %(name)s - %(message)s", logger='cone'):
        FULL_PATH = os.path.join(ROOT_PATH, "temp/logs", log_file)
        self.remove_if_exists(FULL_PATH)
        self.create_dir_for_file_path(FULL_PATH)
        
        handler = logging.FileHandler(FULL_PATH)
        handler.setLevel(level)
        frm = logging.Formatter(formatter)
        handler.setFormatter(frm)
        logger = logging.getLogger(logger)
        logger.addHandler(handler)
        
        return [FULL_PATH, handler, logger]

class TestExtractRefsFromTemplate(unittest.TestCase):
    def test_extract_refs_from_template(self):
        def t(data, expected_refs):
            actual_refs = templatemlplugin.TemplatemlImpl._extract_refs_from_template(data)
            self.assertEquals(expected_refs, actual_refs)
        
        t("some text {{ feat_tree.Foo }} more text",
          ['Foo'])
        t("some text {{ feat_tree.Foo.Bar }} more text",
          ['Foo.Bar'])
        t("some text {{feat_tree.Foo.Bar}} more text",
          ['Foo.Bar'])
        t("some text {{ feat_tree.Foo.Bar.Baz }} more text",
          ['Foo.Bar.Baz'])
        t("some text {{ feat_tree.Foo.Bar.Baz._value }} more text",
          ['Foo.Bar.Baz'])
        t(u"some text {{ feat_tree.ударения.ελληνικά }} more text",
          [u'ударения.ελληνικά'])
        t(u"some text {{ feat_tree.ударения.ελληνικά._value }} more text",
          [u'ударения.ελληνικά'])
        t("some text {{ feat_tree.MyFeature.MySetting|some_filter }} more text",
          ['MyFeature.MySetting'])
        t(u"some text {{ feat_tree.MyFeature.MySetting|some_filter }} more text",
          ['MyFeature.MySetting'])
        t("some text {{ feat_tree.MyFeature.MySetting | some_filter }} more text",
          ['MyFeature.MySetting'])
        t("some text {{ feat_tree.MyFeature.MySetting._value|some_filter }} more text",
          ['MyFeature.MySetting'])
        t("some text {{ feat_tree.Xyz.Zyx._type }} more {{feat_tree.Xyz.Zyx._type}} text",
          ['Xyz.Zyx', 'Xyz.Zyx'])
        t("some text {% for x in feat_tree.MyFeature.MySetting._value|sort %} more text",
          ['MyFeature.MySetting'])
        
if __name__ == '__main__':
  unittest.main()
