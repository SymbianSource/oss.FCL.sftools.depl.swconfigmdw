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
Test the configuration
"""
import unittest
import string
import sys
import os
import subprocess
import shutil
import __init__
from testautomation.base_testcase import BaseTestCase
from testautomation import unzip_file
from scripttest_common import get_cmd
from cone.public import api

try:
    from cElementTree import ElementTree
except ImportError:
    try:    
        from elementtree import ElementTree
    except ImportError:
        try:
            from xml.etree import cElementTree as ElementTree
        except ImportError:
            from xml.etree import ElementTree

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR  = os.path.join(ROOT_PATH, 'temp/update')
TEST_PROJECT_CPF = os.path.join(ROOT_PATH, 'test_project.cpf')

class TestUpdate(BaseTestCase):

    def test_get_help(self):
        cmd = '%s -h' % get_cmd('update')
        out = self.run_command(cmd)
        lines = out.split('\r\n')
        self.assertTrue('Options:' in lines)
        self.assertTrue('  Update options:' in lines)

    def test_add_and_remove_meta_in_filesystem_project(self):
        TEST_PROJECT_DIR = os.path.join(ROOT_PATH, 'temp/update/project')
        unzip_file.unzip_file(TEST_PROJECT_CPF, TEST_PROJECT_DIR, delete_if_exists=True)
        
        rootfile = os.path.join(TEST_PROJECT_DIR, "root5.confml")
        self._run_test_add_and_remove_meta_in_project(
            project          = TEST_PROJECT_DIR,
            root_file_reader = lambda: self.read_data_from_file(rootfile))

    def test_add_and_remove_meta_in_cpf(self):
        cpf = os.path.join(ROOT_PATH, "temp/metadata/project.cpf")
        self.remove_if_exists(cpf)
        self.create_dir_for_file_path(cpf)
        shutil.copy2(TEST_PROJECT_CPF, cpf)
        
        self._run_test_add_and_remove_meta_in_project(
            project          = cpf,
            root_file_reader = lambda: self.read_data_from_zip_file(cpf, "root5.confml"))
    
    def _run_test_add_and_remove_meta_in_project(self, project, root_file_reader):
        """
        Run test for adding and removing metadata in a project.
        
        @param project: Path to the project that is being modified.
        @param root_file_reader: Function that will be called to read the raw binary
            data of the configuration project's root ConfML file.
        """
        # -------------------------------------
        # Step 1: Add metadata and description
        # -------------------------------------
        self.set_modification_reference_time(project)
        cmd = ('%s '\
            '--project "%s" --configuration root5.confml '\
            '--add-meta owner="test person" '\
            '--add-meta product="test product" '\
            '--add-meta date="2009-05-11" '\
            '--add-cpf-meta product_type="XYZ-123" '\
            '--add-cpf-meta platform="Platform X" '\
            '--add-cpf-meta platform_version="1.0.0" '\
            '--add-desc "Testing description"') % (get_cmd('update'), project)
        out = self.run_command(cmd)
        #print out
        self.assert_modified(project)
        
        
        # Check that the metadata is correct
        root_elem = ElementTree.fromstring(root_file_reader())
        
        desc_elem = root_elem.find("{http://www.s60.com/xml/confml/2}desc")
        self.assertEquals(desc_elem.text, "Testing description")
        
        meta_elem = root_elem.find("{http://www.s60.com/xml/confml/2}meta")
        self.assertEquals(self._get_meta_entry(meta_elem, 'owner'), 'test person')
        self.assertEquals(self._get_meta_entry(meta_elem, 'product'), 'test product')
        self.assertEquals(self._get_meta_entry(meta_elem, 'date'), '2009-05-11')
        self.assertEquals(self._get_cpf_meta_entry(meta_elem, 'product_type'), 'XYZ-123')
        self.assertEquals(self._get_cpf_meta_entry(meta_elem, 'platform'), 'Platform X')
        self.assertEquals(self._get_cpf_meta_entry(meta_elem, 'platform_version'), '1.0.0')
        
        
        # -----------------------------------------------
        # Step 2: Remove and modify some of the metadata
        # -----------------------------------------------
        self.set_modification_reference_time(project)
        cmd = ('%s '\
            '--project "%s" --configuration root5.confml '\
            '--add-meta product="Prod-1" '\
            '--remove-meta date '\
            '--add-cpf-meta platform_version=1.0.1 '\
            '--remove-meta product_type ') % (get_cmd('update'), project)
        out = self.run_command(cmd)
        #print out
        self.assert_modified(project)
        
        # Check that the metadata is correct
        root_elem = ElementTree.fromstring(root_file_reader())
        
        desc_elem = root_elem.find("{http://www.s60.com/xml/confml/2}desc")
        self.assertEquals(desc_elem.text, "Testing description")
        
        meta_elem = root_elem.find("{http://www.s60.com/xml/confml/2}meta")
        self.assertEquals(self._get_meta_entry(meta_elem, 'owner'), 'test person')
        self.assertEquals(self._get_meta_entry(meta_elem, 'product'), 'Prod-1')
        self.assertEquals(self._get_meta_entry(meta_elem, 'date'), None)
        self.assertEquals(self._get_cpf_meta_entry(meta_elem, 'product_type'), None)
        self.assertEquals(self._get_cpf_meta_entry(meta_elem, 'platform'), 'Platform X')
        self.assertEquals(self._get_cpf_meta_entry(meta_elem, 'platform_version'), '1.0.1')
        
        
        # ------------------------------------------------------------
        # Step 3: Remove the description and the rest of the metadata
        # ------------------------------------------------------------
        self.set_modification_reference_time(project)
        cmd = ('%s '\
            '--project "%s" --configuration root5.confml '\
            '--remove-meta owner '\
            '--remove-meta product '\
            '--remove-meta platform '\
            '--remove-meta platform_version '\
            '--remove-desc ') % (get_cmd('update'), project)
        out = self.run_command(cmd)
        #print out
        self.assert_modified(project)
        
        
        # Check that the metadata is correct
        root_elem = ElementTree.fromstring(root_file_reader())
        
        desc_elem = root_elem.find("{http://www.s60.com/xml/confml/2}desc")
        self.assertEquals(desc_elem, None)
        
        meta_elem = root_elem.find("{http://www.s60.com/xml/confml/2}meta")
        self.assertEquals(0, len(meta_elem.getchildren()))

    
    def _get_meta_entry(self, meta_elem, entry_name):
        elem =  meta_elem.find("{http://www.s60.com/xml/confml/2}%s" % entry_name)
        if elem != None:    return elem.text
        else:               return None
    
    def _get_cpf_meta_entry(self, meta_elem, entry_name):
        elem = None
        for e in meta_elem.findall("{http://www.nokia.com/xml/cpf-id/1}configuration-property"):
            if e.get('name') == entry_name:
                elem = e
                break
        
        if elem != None:    return elem.get('value')
        else:               return None
    
    def test_add_data_to_cpf(self):
        # Copy from the test data
        cpf = os.path.join(ROOT_PATH, "temp/metadata/add_data_test_project.cpf")
        self.remove_if_exists(cpf)
        self.create_dir_for_file_path(cpf)
        shutil.copy2(TEST_PROJECT_CPF, cpf)
        
        CONFIG = 'root3.confml'
        
        def get_setting_value(project_location, ref):
            prj = api.Project(api.Storage.open(project_location, 'r'))
            try:
                config = prj.get_configuration(CONFIG)
                dview = config.get_default_view()
                feature = dview.get_feature(ref)
                return feature.get_value()
            finally:
                prj.close()
        
        self.assertEquals(get_setting_value(cpf, 'Feature1.BooleanSetting'), False)
        
        self.set_modification_reference_time(cpf)
        cmd = '%s -p "%s" -c %s --add-data Feature1.BooleanSetting=true' % (get_cmd('update'), cpf, CONFIG)
        self.run_command(cmd)
        self.assert_modified(cpf)
        
        self.assertEquals(get_setting_value(cpf, 'Feature1.BooleanSetting'), True)
    
    def _run_test_add_meta_to_multiple_roots_in_filesystem_project(self, project, args, updated_configs):
        TEST_PROJECT_DIR = os.path.join(ROOT_PATH, 'temp/update', project)
        unzip_file.unzip_file(TEST_PROJECT_CPF, TEST_PROJECT_DIR, delete_if_exists=True)
        self.assert_exists_and_contains_something(TEST_PROJECT_DIR)
        
        self.set_modification_reference_time(TEST_PROJECT_DIR)
        cmd = ('%(cmd)s '\
            '--project "%(project)s" %(args)s '\
            '--add-meta owner="test person" '\
            '--add-meta product="test product" '\
            '--add-cpf-meta product_type="XYZ-123" '\
            '--add-cpf-meta platform="Platform X" '\
            '--add-desc "Testing description"')\
            % {'cmd'    : get_cmd('update'),
               'project': TEST_PROJECT_DIR,
               'args'   : args}
        out = self.run_command(cmd)
        #print out
        self.assert_modified(TEST_PROJECT_DIR)
        
        # Check that the metadata is correct for all roots
        project = api.Project(api.Storage.open(TEST_PROJECT_DIR, 'r'))
        for config in project.list_configurations():
            config_file_path = os.path.join(TEST_PROJECT_DIR, config)
            root_elem = ElementTree.fromstring(self.read_data_from_file(config_file_path))
            
            if config in updated_configs:
                try:
                    desc_elem = root_elem.find("{http://www.s60.com/xml/confml/2}desc")
                    self.assertNotEquals(desc_elem, None)
                    self.assertEquals(desc_elem.text, "Testing description")
                    
                    meta_elem = root_elem.find("{http://www.s60.com/xml/confml/2}meta")
                    self.assertEquals(self._get_meta_entry(meta_elem, 'owner'), 'test person')
                    self.assertEquals(self._get_meta_entry(meta_elem, 'product'), 'test product')
                    self.assertEquals(self._get_cpf_meta_entry(meta_elem, 'product_type'), 'XYZ-123')
                    self.assertEquals(self._get_cpf_meta_entry(meta_elem, 'platform'), 'Platform X')
                except AssertionError:
                    self.fail("Root '%s' was not updated when it should have been!" % config)
            else:
                try:
                    desc_elem = root_elem.find("{http://www.s60.com/xml/confml/2}desc")
                    self.assertEquals(desc_elem, None)
                    
                    meta_elem = root_elem.find("{http://www.s60.com/xml/confml/2}meta")
                    self.assertEquals(meta_elem, None)
                except AssertionError:
                    self.fail("Root '%s' was updated when it should not have been!" % config)

    def test_update_multiple_configurations(self):
        self._run_test_add_meta_to_multiple_roots_in_filesystem_project(
            project         = 'multi_project',
            args            = '-c root2.confml '
                              '-c root4.confml',
            updated_configs = ['root2.confml',
                               'root4.confml'])
    
    def test_update_multiple_configurations_with_wildcard(self):
        self._run_test_add_meta_to_multiple_roots_in_filesystem_project(
            project         = 'multi_project_wildcard',
            args            = '--config-wildcard root*.confml',
            updated_configs = ['root1.confml',
                               'root2.confml',
                               'root3.confml',
                               'root4.confml',
                               'root5.confml'])
    
    def test_update_multiple_configurations_with_regex(self):
        self._run_test_add_meta_to_multiple_roots_in_filesystem_project(
            project         = 'multi_project_regex',
            args            = '--config-regex root[135].confml',
            updated_configs = ['root1.confml',
                               'root3.confml',
                               'root5.confml'])
    
    def test_update_multiple_configurations_with_mixed_args(self):
        self._run_test_add_meta_to_multiple_roots_in_filesystem_project(
            project         = 'multi_project_mixed_args',
            args            = '-c root2.confml --config-regex root[13].confml',
            updated_configs = ['root1.confml',
                               'root2.confml',
                               'root3.confml'])

if __name__ == '__main__':
      unittest.main()