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


"""
Test the CPF root file parsing routines
"""

import zipfile
import unittest
import string
import token
import sys,os,re
import __init__

from cone.public import utils, rules, api, exceptions

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
testdata  = os.path.abspath(os.path.join(ROOT_PATH,'utils-testdata'))

class T(object): 
    def __init__(self,str=""): self.str = str

class TestResourceRefs(unittest.TestCase):
    def test_join_two_refs(self):
        self.assertEquals(utils.resourceref.join_refs(['foo/bar/test','fancy.ref']),'foo/bar/test/fancy.ref')
        self.assertEquals(utils.resourceref.join_refs(['foo/bar/test','/absref/fancy.ref']),'/absref/fancy.ref')

    def test_join_three_refs(self):
        self.assertEquals(utils.resourceref.join_refs(['foo/bar/test','fancy/ref','test1.12']),'foo/bar/test/fancy/ref/test1.12')

    def test_join_two_refs_with_empty_first_ref(self):
        self.assertEquals(utils.resourceref.join_refs(['','fancy/ref']),'fancy/ref')

    def test_join_two_refs_with_empty_last_ref(self):
        self.assertEquals(utils.resourceref.join_refs(['fancy/ref','']),'fancy/ref/')

    def test_join_two_refs_with_two_emtpy_refs(self):
        self.assertEquals(utils.resourceref.join_refs(['','']),'')

    def test_join_three_refs_with_empty(self):
        self.assertEquals(utils.resourceref.join_refs(['foo/bar/test','','test1/12']),'foo/bar/test/test1/12')

    def test_join_three_refs_with_extra_slashes(self):
        self.assertEquals(utils.resourceref.join_refs(['foo/bar/test/','/','one/']),'/one/')

    def test_join_three_refs_with_extra_slashes_and_begin_slash(self):
        self.assertEquals(utils.resourceref.join_refs(['/foo/bar/test/','/','one/']),'/one/')

    def test_filter_files(self):
        filtered = utils.resourceref.filter_resources(['test.txt','foo.dat','teat/data/bar.confml'],"\.txt")
        self.assertEquals(filtered[0],'test.txt')
    
    def test_filter_files_confmls(self):
        filtered = utils.resourceref.filter_resources(['test.txt','foo.confml','test/data/bar.confml'],"\.confml")
        self.assertEquals(filtered[0],'foo.confml')

    def test_neg_filter_resources(self):
        filtered = utils.resourceref.neg_filter_resources(['test.txt','foo.dat','teat/data/bar.confml'],"\.txt")
        self.assertEquals(filtered[0],'foo.dat')
        self.assertEquals(filtered[1],'teat/data/bar.confml')

    def test_filter_files_with_extension(self):
        filtered = utils.resourceref.filter_resources(['test.txt','foo.dat','teat/data/bar.confml'],".*\.dat")
        self.assertEquals(filtered[0],'foo.dat')

    def test_neg_filter_resources(self):
        filtered = utils.resourceref.neg_filter_resources(['/test/.svn/test.txt','.svn/test/foo.dat','teat/data/bar.confml'],"\.svn")
        self.assertEquals(filtered[0],'teat/data/bar.confml')

    def test_insert_begin_slash_without(self):
        self.assertEquals(utils.resourceref.insert_begin_slash('data/folder/siitake.txt'),'/data/folder/siitake.txt')

    def test_insert_begin_slash_with(self):
        self.assertEquals(utils.resourceref.insert_begin_slash('/data/folder/siitake.txt'),'/data/folder/siitake.txt')

    def test_remove_begin_slash_without(self):
        self.assertEquals(utils.resourceref.remove_begin_slash('data/folder/siitake.txt'),'data/folder/siitake.txt')

    def test_remove_beging_slash_with(self):
        self.assertEquals(utils.resourceref.remove_begin_slash('/data/folder/siitake.txt'),'data/folder/siitake.txt')

    def test_add_end_slash_without(self):
        self.assertEquals(utils.resourceref.add_end_slash('data/folder'),'data/folder/')

    def test_add_end_slash_with(self):
        self.assertEquals(utils.resourceref.add_end_slash('data/folder/'),'data/folder/')

    def test_remove_end_slash_without(self):
        self.assertEquals(utils.resourceref.remove_end_slash('data/folder'),'data/folder')

    def test_remove_end_slash_with(self):
        self.assertEquals(utils.resourceref.remove_end_slash('/data/folder/'),'/data/folder')

    def test_split_ref_with_empty_elem(self):
        self.assertEquals(utils.resourceref.split_ref(''),[])

    def test_split_ref_two_elems(self):
        self.assertEquals(utils.resourceref.split_ref('aaa/bbb'),['aaa','bbb'])

    def test_split_ref_two_elems_and_begin_slash(self):
        self.assertEquals(utils.resourceref.split_ref('/aaa/bbb'),['aaa','bbb'])

    def test_split_ref_two_elems_and_end_slash(self):
        self.assertEquals(utils.resourceref.split_ref('aaa/bbb/'),['aaa','bbb'])

    def test_psplit_ref_with_tree_elems(self):
        self.assertEquals(utils.resourceref.psplit_ref('aaa/bbb/ccc.txt'),('aaa/bbb','ccc.txt'))

    def test_psplit_ref_with_two_elems(self):
        self.assertEquals(utils.resourceref.psplit_ref('aaa/bbb'),('aaa','bbb'))

    def test_psplit_ref_with_one_elems(self):
        self.assertEquals(utils.resourceref.psplit_ref('aaa.conf'),('','aaa.conf'))

    def test_psplit_ref_with_empty_elem(self):
        self.assertEquals(utils.resourceref.psplit_ref(''),('',''))

    def test_norm_ref(self):
        self.assertEquals(utils.resourceref.norm('dir/with/something/skeleton.txt'),
                                     'dir/with/something/skeleton.txt')

    def test_norm_ref_with_begin_dot(self):
        self.assertEquals(utils.resourceref.norm('./skeleton.txt'),
                                     'skeleton.txt')

    def test_norm_ref_with_begin_dot(self):
        self.assertEquals(utils.resourceref.norm('.svn'),
                                     '.svn')

    def test_norm_ref_with_empty_string(self):
        self.assertEquals(utils.resourceref.norm(''),
                                     '')

    def test_norm_ref_with_backslash(self):
        self.assertEquals(utils.resourceref.norm('dir\\with\\something\\skeleton.txt'),
                                     'dir/with/something/skeleton.txt')

    def test_norm_ref_with_backslash_and_forward_slash(self):
        self.assertEquals(utils.resourceref.norm('dir\\with/something\\skeleton.txt'),
                                     'dir/with/something/skeleton.txt')

    def test_norm_ref_with_begin_slash(self):
        self.assertEquals(utils.resourceref.norm('/dir/with/something\\skeleton.txt'),
                                     '/dir/with/something/skeleton.txt')

    def test_norm_ref_with_begin_backslash(self):
        self.assertEquals(utils.resourceref.norm('\\dir\\with\\something\\skeleton.txt'),
                                     '/dir/with/something/skeleton.txt')

    def test_norm_ref_with_end_slash(self):
        self.assertEquals(utils.resourceref.norm('/dir/with/something/'),
                                     '/dir/with/something')

    def test_norm_ref_with_end_backslash(self):
        self.assertEquals(utils.resourceref.norm('dir/with/something\\'),
                                     'dir/with/something')

    def test_norm_ref_with_spaces(self):
        self.assertEquals(utils.resourceref.norm('dir/with/some thing/some.txt'),
                                     'dir/with/some thing/some.txt')

    def test_norm_ref_with_spaces_and_hyphens(self):
        self.assertEquals(utils.resourceref.norm('"dir/with/some thing/some.txt"'),
                                     'dir/with/some thing/some.txt')

    def test_norm_ref_with_spaces_and_hyphens_and_begin_slash(self):
        self.assertEquals(utils.resourceref.norm('"/dir/with/some thing/some.txt"'),
                                     '/dir/with/some thing/some.txt')

    def test_replace_dir_part(self):
        filename = utils.resourceref.replace_dir('dir/to/replace/with/something/skeleton.txt',
                                  'dir/to\\replace',
                                  'somethingelse/123/')
        self.assertEquals(filename,'somethingelse/123/with/something/skeleton.txt')

    def test_replace_dir_part_with_one_part(self):
        filename = utils.resourceref.replace_dir('dir/to/replace/with/dir/dir.txt',
                                  'dir',
                                  'somethingelse/123/')
        self.assertEquals(filename,'somethingelse/123/to/replace/with/dir/dir.txt')

    def test_replace_dir_part_with_empty_target(self):
        filename = utils.resourceref.replace_dir('dir/to/replace/with/dir/dir.txt',
                                  'dir',
                                  '')
        self.assertEquals(filename,'to/replace/with/dir/dir.txt')

    def test_replace_dir_part_with_no_match(self):
        filename = utils.resourceref.replace_dir('foo\\skeleton.txt',
                                  'dir/to\\replace',
                                  'somethingelse/123/')
        self.assertEquals(filename,'foo/skeleton.txt')

    def test_replace_dir_part_with_begin_slash(self):
        filename = utils.resourceref.replace_dir('dir/to/replace/with/dir/dir.txt',
                                  'dir/to/replace',
                                  '/epoc32/testing')
        self.assertEquals(filename,'/epoc32/testing/with/dir/dir.txt')

    def test_replace_dir_with_match(self):
        filename = utils.resourceref.replace_dir('foo/test',
                                  'foo/test',
                                  '')
        self.assertEquals(filename,'')

    def test_replace_dir_from_empty(self):
        filename = utils.resourceref.replace_dir('foo/test',
                                  '',
                                  'output/bar')
        self.assertEquals(filename,'output/bar/foo/test')

    def test_remove_ext(self):
        self.assertEquals(utils.resourceref.remove_ext('fii/faa/foo.confml'),'fii/faa/foo')

    def test_remove_ext_from_dot_beginning_file(self):
        self.assertEquals(utils.resourceref.remove_ext('.metadata'),'.metadata')

    def test_remove_ext_from_file_without_ext(self):
        self.assertEquals(utils.resourceref.remove_ext('fii/faa/foo'),'fii/faa/foo')

    def test_remove_ext_from_file_without_path(self):
        self.assertEquals(utils.resourceref.remove_ext('fii.faa.foo'),'fii.faa')

    def test_get_ext(self):
        self.assertEquals(utils.resourceref.get_ext('fii/faa/foo.confml'),'confml')

    def test_get_ext_without_ext(self):
        self.assertEquals(utils.resourceref.get_ext('fii/faa/foo'),'')

    def test_get_filename(self):
        self.assertEquals(utils.resourceref.get_filename('fii/faa/foo.confml'),'foo.confml')

    def test_get_filename_without_filename(self):
        self.assertEquals(utils.resourceref.get_filename('fii/faa/'),'')

    def test_get_filename_with_onepart(self):
        self.assertEquals(utils.resourceref.get_filename('fii'),'fii')

    def test_get_path(self):
        self.assertEquals(utils.resourceref.get_path('fii/faa/foo.confml'),'fii/faa')

    def test_get_path_without_filename(self):
        self.assertEquals(utils.resourceref.get_path('fii/faa/'),'fii/faa')

    def test_get_path_with_onepart(self):
        self.assertEquals(utils.resourceref.get_path('fii'),'')

    def test_to_dottedref(self):
        self.assertEquals(utils.resourceref.to_dottedref('fii/faa/foo.confml'),'fii_faa_foo')

    def test_to_dottedref_from_single_elem(self):
        self.assertEquals(utils.resourceref.to_dottedref('fii'),'fii')

    def test_to_dottedref_from_dotted(self):
        self.assertEquals(utils.resourceref.to_dottedref('fii.faa.foo'),'fii.faa')

    def test_to_dottedref_with_ext(self):
        self.assertEquals(utils.resourceref.to_dottedref('.metadata'),'metadata')

    def test_to_objref_dotted_start(self):
        self.assertEquals(utils.resourceref.to_objref('../foo/bar/test.confml'),'____foo__bar__test_confml')

    def test_to_objref_dot_in_name_start(self):
        self.assertEquals(utils.resourceref.to_objref('/foo.bar/test.confml'),'_foo_bar_test_confml')

    def test_to_objref_number_in_name_start(self):
        self.assertEquals(utils.resourceref.to_objref('_1.0.test_one'),'_1_0_test_one')
        self.assertEquals(utils.resourceref.to_objref('0.test_one'),'_0_test_one')
        self.assertEquals(utils.resourceref.to_objref('1.0.test_one'),'_1_0_test_one')

    def test_to_objref_unicode(self):
        self.assertEquals(utils.resourceref.to_objref(u'fooäbar'),'foo_bar')
        self.assertEquals(utils.resourceref.to_objref(u'foo:bar-testöne'),'foo_bar_test_ne')
        self.assertEquals(utils.resourceref.to_objref('foo1.1test.confml'),'foo1_1test_confml')
        self.assertEquals(utils.resourceref.to_objref('sub:417-48964:_hw_drv:_display_driver_common_features_-_thermal_event_handling_in_rdisplaykernel_and_thermal_management_for_display_module_behind_feature_flag'),
                          'sub_417_48964__hw_drv__display_driver_common_features___thermal_event_handling_in_rdisplaykernel_and_thermal_management_for_display_module_behind_feature_flag')

    def test_to_objref_dot_in_name_start(self):
        self.assertEquals(utils.resourceref.to_objref('/foo.bar/test.confml'),'__foo_bar__test_confml')

    def test_to_hash_dotted_start(self):
        self.assertEquals(utils.resourceref.to_hash('../foo/bar/test.confml'),'0x5a063087')
        self.assertEquals(utils.resourceref.to_hash('../foo/bar/test.confml'),'0x5a063087')

    def test_to_hash(self):
        self.assertEquals(utils.resourceref.to_hash('../fo.o/number.txt'),'-0x1b381b13')

    def test_to_dref(self):
        self.assertEquals(utils.resourceref.to_dref('fii/faa/foo.confml'),'fii.faa.foo')

    def test_to_dref_with_ext(self):
        self.assertEquals(utils.resourceref.to_dref('.metadata'),'metadata')

    def test_to_dref_from_single_elem(self):
        self.assertEquals(utils.resourceref.to_dref('fii'),'fii')

    def test_to_dref_from_dotted(self):
        self.assertEquals(utils.resourceref.to_dref('fii.faa.foo'),'fii.faa')

class TestUtils(unittest.TestCase):    
    def test_distinct_array_with_single_values(self):
        self.assertEquals(utils.distinct_array(['1','2','1','1']),['1','2'])

    def test_distinct_array_with_single_values(self):
        self.assertEquals(utils.distinct_array(['1','2','3','1','2','4']),['1','2','3','4'])

    def test_list_files_from_testdata(self):
        files = utils.list_files(testdata)
        self.assertTrue(files[0].endswith('scrot.txt'))
        self.assertTrue(files[1].endswith('test.txt'))

    def test_list_files_from_current_dir(self):
        files = utils.list_files('.')
        self.assertTrue(len(files)>0)

    def test_pathmatch_with_same_path(self):
        self.assertEquals(utils.pathmatch('test.foo','test.foo'),True)

    def test_pathmatch_with_diff_path(self):
        self.assertEquals(utils.pathmatch('test.bar','test.foo'),False)

    def test_pathmatch_with_star(self):
        self.assertEquals(utils.pathmatch('test.foo.*','test.foo.bar'),True)

    def test_pathmatch_with_star(self):
        self.assertEquals(utils.pathmatch('test.foo.*','test.foo.bar.fiba'),False)

    def test_pathmatch_with_twostar(self):
        self.assertEquals(utils.pathmatch('test.foo.**','test.foo.bar.fiba'),True)

    def test_filter_objs_ref(self):
        obj = T("com.nokia.foo.bar")
        filters = []
        filters.append(lambda x: re.match(".*nokia.*", x.str))
        self.assertEquals(utils.filter(obj,filters),True)

    def test_filter_objs_ref_not(self):
        obj = T("foo.bar")
        filters = []
        filters.append(lambda x: re.match("foo$", x.str))
        self.assertEquals(utils.filter(obj,filters),False)

    def test_filter_objs_type(self):
        obj = T()
        filters = []
        filters.append(lambda x: isinstance(x,T))
        self.assertEquals(utils.filter(obj,filters),True)

    def test_filter_objs_type_not(self):
        class F(object): pass
        obj = T()
        filters = []
        filters.append(lambda x: isinstance(x,F))
        self.assertEquals(utils.filter(obj,filters),False)

class TestDottedRefs(unittest.TestCase):
    def test_join_two_refs(self):
        self.assertEquals(utils.dottedref.join_refs(['foo.bar.test','fancy.ref']),'foo.bar.test.fancy.ref')

    def test_join_three_refs(self):
        self.assertEquals(utils.dottedref.join_refs(['foo.bar.test','fancy.ref','test1.12']),'foo.bar.test.fancy.ref.test1.12')

    def test_join_two_refs_with_empty_first_ref(self):
        self.assertEquals(utils.dottedref.join_refs(['','fancy.ref']),'fancy.ref')

    def test_join_two_refs_with_empty_last_ref(self):
        self.assertEquals(utils.dottedref.join_refs(['fancy.ref','']),'fancy.ref')

    def test_join_two_refs_with_two_emtpy_refs(self):
        self.assertEquals(utils.dottedref.join_refs(['','']),'')

    def test_join_three_refs_with_empty(self):
        self.assertEquals(utils.dottedref.join_refs(['foo.bar.test','','test1.12']),'foo.bar.test.test1.12')

    def test_split_ref_with_tree_elems(self):
        self.assertEquals(utils.dottedref.split_ref('aaa.bbb.ccc'),['aaa','bbb','ccc'])

    def test_split_ref_with_empty_elem(self):
        self.assertEquals(utils.dottedref.split_ref(''),[])

    def test_split_ref_with_empty_elem_between(self):
        self.assertEquals(utils.dottedref.split_ref('aaa..bbb'),['aaa','bbb'])

    def test_psplit_ref_with_tree_elems(self):
        self.assertEquals(utils.dottedref.psplit_ref('aaa.bbb.ccc'),('aaa.bbb','ccc'))

    def test_psplit_ref_with_two_elems(self):
        self.assertEquals(utils.dottedref.psplit_ref('aaa.bbb'),('aaa','bbb'))

    def test_psplit_ref_with_one_elems(self):
        self.assertEquals(utils.dottedref.psplit_ref('aaa'),('','aaa'))

    def test_psplit_ref_with_empty_elem(self):
        self.assertEquals(utils.dottedref.psplit_ref(''),('',''))

    def test_ref2filter_with_one_elem(self):
        self.assertEquals(utils.dottedref.ref2filter('test'),'test$')

    def test_ref2filter_with_two_elems(self):
        self.assertEquals(utils.dottedref.ref2filter('test.foo'),'test\.foo$')

    def test_ref2filter_with_three_elems(self):
        self.assertEquals(utils.dottedref.ref2filter('test.foo.bar'),'test\.foo\.bar$')

    def test_ref2filter_with_one_star(self):
        self.assertEquals(utils.dottedref.ref2filter('*'),'[^\.]*$')

    def test_ref2filter_with_two_elems_one_star(self):
        self.assertEquals(utils.dottedref.ref2filter('test.foo.*'),'test\.foo\.[^\.]*$')

    def test_ref2filter_with_two_elems_two_stars(self):
        self.assertEquals(utils.dottedref.ref2filter('test.foo.*'),'test\.foo\.[^\.]*$')

    def test_remove_extension(self):
        self.assertEquals(utils.dottedref.remove_last('fii/foo.dat'),'fii/foo')

    def test_remove_last_elem(self):
        self.assertEquals(utils.dottedref.remove_last('fii.foo.faa.dat'),'fii.foo.faa')

    def test_remove_last_elem_from_single(self):
        self.assertEquals(utils.dottedref.remove_last('fii'),'fii')

    def test_get_last_elem_from_single(self):
        self.assertEquals(utils.dottedref.get_last('fii'),'fii')

    def test_get_last_elem_from_empty(self):
        self.assertEquals(utils.dottedref.get_last(''),'')

    def test_get_last_elem_from_multi(self):
        self.assertEquals(utils.dottedref.get_last('fii.faa.foo'),'foo')

    def test_remove_begin_dot_without(self):
        self.assertEquals(utils.dottedref.remove_begin_dot('data.folder.siitake'),
                                                               'data.folder.siitake')

    def test_remove_beging_dot_with(self):
        self.assertEquals(utils.dottedref.remove_begin_dot('.data.folder.siitake'),
                                                        'data.folder.siitake')

    def test_get_list_index(self):
        self.assertEquals(utils.dottedref.get_index('data[0]'),0)

    def test_get_list_with_long_index(self):
        self.assertEquals(utils.dottedref.get_index('data[123]'),123)

    def test_get_list_index_with_no_index(self):
        self.assertEquals(utils.dottedref.get_index('data'),None)

    def test_get_name_with_index(self):
        self.assertEquals(utils.dottedref.get_name('data[0]'),'data')

    def test_get_name_normal(self):
        self.assertEquals(utils.dottedref.get_name('data'),'data')
        
    def test_extract_delimited_tokens(self):
        def check(expected, string, delimiters=None):
            if delimiters != None:  actual = utils.extract_delimited_tokens(string, delimiters)
            else:                   actual = utils.extract_delimited_tokens(string)
            self.assertEquals(expected, actual)
        
        check([], '')
        check(['x'], '${x}')
        check(['x'], '@{x}', delimiters=('@{', '}'))
        check(['my.ref1', 'my.ref2'],"test1 ${my.ref1} test2 ${ my.ref1 } ${my.ref2}")
        check(['my.ref1', 'my\nmultiline\nref'],"test1 ${my.ref1} test2 ${ my.ref1 } ${my\nmultiline\nref}")
        check(['my.ref1', 'my.ref2', u'????????.????????'], u"test1 ${my.ref1} test2 ${ my.ref2 } ${????????.????????}")
    
    def test_extract_delimited_token_tuples(self):
        def check(expected, string, delimiters=None):
            if delimiters != None:  actual = utils.extract_delimited_token_tuples(string, delimiters)
            else:                   actual = utils.extract_delimited_token_tuples(string)
            self.assertEquals(expected, actual)
        
        check([], '')
        check([('x', '${x}')], '${x}')
        check([('x', '@{x}')], '@{x}', delimiters=('@{', '}'))
        check([('my.ref1', '${my.ref1}'), ('my.ref1', '${ my.ref1 }'), ('my.ref2', '${my.ref2}')],
              "test1 ${my.ref1} test2 ${ my.ref1 } ${my.ref2} yeah ${my.ref2}")
        check([('my.ref1', '${my.ref1}'), ('my.ref1', '${ my.ref1 }'), ('my\nmultiline\nref', '${my\nmultiline\nref}')],
              "test1 ${my.ref1} test2 ${ my.ref1 } ${my\nmultiline\nref}")
        check([('my.ref1', '${my.ref1}'), ('my.ref2', '${ my.ref2 }'), (u'????????.????????', u'${????????.????????}')],
              u"test1 ${my.ref1} test2 ${ my.ref2 } ${????????.????????}")
    
    def test_expand_delimited_tokens(self):
        def check(expected, string, delimiters=None):
            def expand(ref, index):
                return "<%d: %s>" % (index, ref)
            if delimiters != None:  actual = utils.expand_delimited_tokens(string, expand, delimiters)
            else:                   actual = utils.expand_delimited_tokens(string, expand)
            self.assertEquals(expected, actual)
        
        check('test', 'test')
        check('<0: x>', '${x}')
        check('<0: x>', '@{x}', delimiters=('@{', '}'))
        check('<0: x>  <1: y> <0: x>', '${x}  ${y} ${ x }')
        check(u'<0: my.ref1>  test <1: ????????.????????>', u'${ my.ref1 }  test ${????????.????????}')
        check('<0: my.ref1>  test <1: my\nmultiline\nref>', '${ my.ref1}  test ${my\nmultiline\nref}')
    
    def test_expand_refs_by_default_view(self):
        VALUES = {'Test.Color'  : 'brown',
                  'Test.Animal1': 'fox',
                  'Test.Animal2': 'dog'}
        class DummyFeature(object):
            def __init__(self, ref):
                self.ref = ref
            def get_original_value(self):
                return VALUES[self.ref]
        class DummyDefaultView(object):
            def get_feature(self, ref):
                if ref in VALUES: return DummyFeature(ref)
                else:             raise exceptions.NotFound()
        dview = DummyDefaultView()
        
        result = utils.expand_refs_by_default_view(
            "The quick ${Test.Color} ${Test.Animal1} jumps over the lazy ${Test.Animal2}.",
            dview)
        self.assertEquals(result, "The quick brown fox jumps over the lazy dog.")
        
        # Test expanding with a non-existent ref
        result = utils.expand_refs_by_default_view(
            "The quick ${Test.Color} ${Test.Foo} jumps over the lazy ${Test.Animal2}.",
            dview)
        self.assertEquals(result, "The quick brown  jumps over the lazy dog.")
        
        # Test expanding with a non-existent ref and a custom default value
        result = utils.expand_refs_by_default_view(
            "The quick ${Test.Color} ${Test.Foo} jumps over the lazy ${Test.Animal2}.",
            dview,
            default_value_for_missing = 'giraffe')
        self.assertEquals(result, "The quick brown giraffe jumps over the lazy dog.")
        

class TestUtilsSubclasses(unittest.TestCase):    

    def setUp(self):
        pass

    def test_all_subclasses_with_none(self):
        class base(object): pass
        classnames = utils.all_subclasses(base)
        self.assertEquals(len(classnames),0)

    def test_all_subclasses_class_tree(self):
        class base(object): pass
        class class1(base): pass
        class class2(base): pass
        class class12(class1): pass
        class class123(class2): pass
        classnames = utils.all_subclasses(base)
        self.assertEquals(len(classnames),4)

class TestUtilsDataMapRef(unittest.TestCase):    

    def setUp(self):
        pass

    def test_get_feature_ref(self):
        map = "foo/bar[@key='key 1']"
        ref = utils.DataMapRef.get_feature_ref(map)
        self.assertEquals(ref,'foo/bar')

    def test_get_key_value(self):
        map = "foo/bar[@key='key 1']"
        value = utils.DataMapRef.get_key_value(map)
        self.assertEquals(value,'key 1')


class TestMakeList(unittest.TestCase):
    def test_get_list_string(self):
        self.assertEquals(utils.get_list('test'), ['test'])

    def test_get_list_from_list(self):
        self.assertEquals(utils.get_list(['test']), ['test'])

    def test_get_list_from_list2(self):
        self.assertEquals(utils.get_list(['test','test2']), ['test','test2'])

    def test_is_list(self):
        self.assertEquals(utils.is_list(['test','test2']), True)

    def test_is_list_false(self):
        self.assertEquals(utils.is_list('test'), False)

    def test_add_list_with_list(self):
        self.assertEquals(utils.add_list(['test','test2'], 'foo'), ['test','test2','foo'])

    def test_add_list_with_none(self):
        self.assertEquals(utils.add_list([], 'foo'), ['foo'])

    def test_add_list_with_string(self):
        self.assertEquals(utils.add_list('bar', 'foo'), ['bar','foo'])

    def test_add_list_with_string2(self):
        self.assertEquals(utils.add_list(['bar','test'], 'foo'), ['bar','test','foo'])

    def test_prepend_list_with_none(self):
        self.assertEquals(utils.prepend_list([], 'foo'), ['foo'])

    def test_prepend_string_with_string(self):
        self.assertEquals(utils.prepend_list('bar', 'foo'), ['foo','bar'])

    def test_prepend_list_with_string(self):
        self.assertEquals(utils.prepend_list(['bar','test'], 'foo'), ['foo','bar','test'])

from cone.confml import model as confmlmodel
        
class TestModelGetters(unittest.TestCase):
    def test_get_module_specific_class(self):
        cls = utils.get_class(confmlmodel,api.Configuration)
        self.assertEquals(cls, confmlmodel.ConfmlConfiguration)

    def test_get_module_specific_class_with_None_model(self):
        cls = utils.get_class(None,api.Configuration)
        self.assertEquals(cls, api.Configuration)

class TestXmlUtilFunctions(unittest.TestCase):
    def test_split_tag_namespace(self):
        self.assertEquals(
            utils.xml.split_tag_namespace("test"),
            (None, 'test'))
        
        self.assertEquals(
            utils.xml.split_tag_namespace("{http://www.test.com/xml/1}test"),
            ('http://www.test.com/xml/1', 'test'))

if __name__ == '__main__':
    unittest.main()
      
