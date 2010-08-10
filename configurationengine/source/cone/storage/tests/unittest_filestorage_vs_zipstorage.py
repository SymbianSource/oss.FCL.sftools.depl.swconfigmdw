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
Test the import export functionality
"""

import unittest
import sys, os, shutil

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

from cone.public.api import Resource
from cone.storage import filestorage, zipstorage

from testautomation.base_testcase import BaseTestCase
from testautomation.unzip_file import unzip_file

def abspath(p):
    return os.path.normpath(os.path.join(ROOT_PATH, p))
    
DATA_ZIP = abspath("file_vs_zip_data.zip")
TEMP_DIR = abspath("temp/file_vs_zip")

EXPECTED = [
    # These two are not used every time
    ('folder',      'dir'),
    ('folder',      'empty2'),
    
    ('folder',      'dir/emptysub'),
    ('folder',      'empty'),
    ('folder',      'empty2/sub'),
    ('resource',    'root.txt'),
    ('resource',    'dir/test1.txt'),
    ('resource',    'dir/test2.txt'),
]

class TestFileStorageVsZipStorage(BaseTestCase):
    def setUp(self):
        pass
    
    def get_temp_zip_storage(self, path, empty=False):
        """
        Get a new zip storage located in the temp/ directory.
        
        @param path: Path of the storage zip file relative to the temp/ directory.
        @param empty: If False, the DATA_ZIP is copied to the location specified
            by 'path' and returned as a read-only storage. If True, a new writable
            empty storage is returned.
        """
        full_path = os.path.join(TEMP_DIR, path)
        if not empty:
            self.create_dir_for_file_path(full_path)
            shutil.copy2(DATA_ZIP, full_path)
            return zipstorage.ZipStorage(full_path, 'r')
        else:
            if os.path.exists(full_path):
                os.remove(full_path)
            return zipstorage.ZipStorage(full_path, 'w')
    
    def get_temp_file_storage(self, path, empty=False):
        """
        Get a new file storage located in the temp/ directory.
        
        @param path: Path of the storage directory relative to the temp/ directory.
        @param empty: If False, the DATA_ZIP is extracted to the location specified
            by 'path' and returned as a read-only storage. If True, a new writable
            empty storage is returned.
        """
        full_path = os.path.join(TEMP_DIR, path)
        if not empty:
            unzip_file(DATA_ZIP, full_path, delete_if_exists=True)
            return filestorage.FileStorage(full_path, 'r')
        else:
            self.recreate_dir(full_path)
            return filestorage.FileStorage(full_path, 'w')
    
    def assert_storage_contains_expected(self, storage, empty_folders):
        # Always list also empty folders, because empty_folders is False,
        # they should not have been exported in the first place
        resource_list = storage.list_resources('', recurse=True, empty_folders=True)
        
        expected = list(EXPECTED)
        
        # Remove empty folders from expected if necessary
        if not empty_folders:
            for i in reversed(xrange(len(expected))):
                if expected[i][0] == 'folder':
                    del expected[i]
        
        # If the actual list contains exactly 2 less entries, they are
        # probably the root folders that are not present in every case
        # (e.g. there is a resource 'my_dir/file.txt', so sometimes there
        # is a folder 'my_dir' in the resource list, but not always)
        if len(resource_list) == len(expected) - 2:
            del expected[0:2]
        
        # Check that there is the same amount of resources/folders
        self.assertEquals(len(expected), len(resource_list), "Expected %r, actual %r" % (expected, resource_list))
        
        # Check that all expected resources/folders are present in the storage
        for type, ref in expected:
            if type == 'resource':
                self.assertTrue(storage.is_resource(ref), "(%r, %r) expected, but not a resource" % (type, ref))
            elif type == 'folder':
                self.assertTrue(storage.is_folder(ref), "(%r, %r) expected, but not a folder" % (type, ref))
            else:
                raise RuntimeError("Invalid type field in expected data")
    
    def _run_test_storage_to_storage(self, source_storage, target_storage, empty_folders):
        try:
            # Check that the source storage contains all expected in the first place
            self.assert_storage_contains_expected(source_storage, True)
            
            # Export resources
            resources = source_storage.list_resources('', recurse=True, empty_folders=empty_folders)
            source_storage.export_resources(resources, target_storage, empty_folders=empty_folders)
            
            # Check that resources have been exported properly
            self.assert_storage_contains_expected(target_storage, empty_folders)
        finally:
            source_storage.close()
            target_storage.close()
    
    def test_export_file_to_file(self):
        self._run_test_storage_to_storage(
            source_storage  = self.get_temp_file_storage('f2f/source'),
            target_storage  = self.get_temp_file_storage('f2f/target', empty=True),
            empty_folders   = False)
        
        self._run_test_storage_to_storage(
            source_storage  = self.get_temp_file_storage('f2f/ef_source'),
            target_storage  = self.get_temp_file_storage('f2f/ef_target', empty=True),
            empty_folders   = True)
    
    def test_export_zip_to_zip(self):
        self._run_test_storage_to_storage(
            source_storage  = self.get_temp_zip_storage('z2z/source.zip'),
            target_storage  = self.get_temp_zip_storage('z2z/target.zip', empty=True),
            empty_folders   = False)
        
        self._run_test_storage_to_storage(
            source_storage  = self.get_temp_zip_storage('z2z/ef_source.zip'),
            target_storage  = self.get_temp_zip_storage('z2z/ef_target.zip', empty=True),
            empty_folders   = True)
    
    def test_export_zip_to_file(self):
        self._run_test_storage_to_storage(
            source_storage  = self.get_temp_zip_storage('z2f/source.zip'),
            target_storage  = self.get_temp_file_storage('z2f/target', empty=True),
            empty_folders   = False)
        
        self._run_test_storage_to_storage(
            source_storage  = self.get_temp_zip_storage('z2f/ef_source.zip'),
            target_storage  = self.get_temp_file_storage('z2f/ef_target', empty=True),
            empty_folders   = True)
    
    def test_export_file_to_zip(self):
        self._run_test_storage_to_storage(
            source_storage  = self.get_temp_file_storage('f2z/source'),
            target_storage  = self.get_temp_zip_storage('f2z/target.zip', empty=True),
            empty_folders   = False)
        
        self._run_test_storage_to_storage(
            source_storage  = self.get_temp_file_storage('f2z/ef_source'),
            target_storage  = self.get_temp_zip_storage('f2z/ef_target.zip', empty=True),
            empty_folders   = True)
    

if __name__ == '__main__':
      unittest.main()
