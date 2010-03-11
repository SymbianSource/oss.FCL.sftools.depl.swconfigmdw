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
import sys,os,shutil

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

import __init__
from cone.public.exceptions import *
from cone.public.api import Resource
from cone.storage import zipstorage

TEMP_DIR = os.path.join(ROOT_PATH, 'temp')
tempzip   = os.path.join(ROOT_PATH,"zipres_test.zip")


class TestFileResource(unittest.TestCase):
    
    def _prepare_tempzip(self, filename):
        """
        Prepare a temporary ZIP file with the given name.
        @return: Absolute path to the newly copied ZIP file.
        """
        new_zip = os.path.join(TEMP_DIR, '%s' % filename)
        
        if os.path.exists(new_zip):
            os.unlink(new_zip)
        
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
        
        shutil.copyfile(tempzip, new_zip)
        return new_zip
    
    def test_open_and_write_resource(self):
        ZIPFILE = self._prepare_tempzip('test1.zip')
        store = zipstorage.ZipStorage(ZIPFILE,"a")
        res = store.open_resource("temp/testwrite.txt","w")
        testdata = "Testing writing func!"
        res.write(testdata)
        res.close()
        store.close()
        zf = zipfile.ZipFile(ZIPFILE,"r")
        data = zf.read("temp/testwrite.txt")
        self.assertEquals(data,testdata)

    def test_open_and_read_resource(self):
        ZIPFILE = self._prepare_tempzip('test2.zip')
        store = zipstorage.ZipStorage(ZIPFILE,"a")
        res = store.open_resource("temp/testread.txt","r")
        resdata = res.read()
        res.close()
        store.close()
        self.assertTrue(resdata.startswith("Hello"))  
    
    def test_get_size(self):
        ZIPFILE = self._prepare_tempzip('test_getsize.zip')
        store = zipstorage.ZipStorage(ZIPFILE, "r")
        res = store.open_resource("temp/testread.txt","r")
        self.assertEquals(res.get_size(), 28)
        # Try a second time just in case
        self.assertEquals(res.get_size(), 28)
        res.close()
        store.close()
    
    def test_get_size_largefile(self):
        ZIPFILE = self._prepare_tempzip('test_getsize_largefile.zip')
        store = zipstorage.ZipStorage(ZIPFILE, "r")
        res = store.open_resource("largefile.bin","r")
        self.assertEquals(res.get_size(), 25000)
        # Try a second time just in case
        self.assertEquals(res.get_size(), 25000)
        res.close()
        store.close()
    
    def test_get_size_fails_in_write_mode(self):
        ZIPFILE = os.path.join(TEMP_DIR, 'getsize_fails_in_write_mode.zip')
        store = zipstorage.ZipStorage(ZIPFILE, "w")
        res = store.open_resource("test_getsize.txt", "w")
        res.write("Writing foobar")
        self.assertRaises(StorageException, res.get_size)
        res.close()
        store.close()

    def test_get_content_info_and_read_data(self):
        ZIPFILE = self._prepare_tempzip('test2.zip')
        store = zipstorage.ZipStorage(ZIPFILE,"a")
        res = store.open_resource("temp/testread.txt","r")
        ci = res.get_content_info()
        self.assertEquals('text/plain', ci.content_type)
        resdata = res.read()
        self.assertEquals('Hello!\r\nHow is my reading?\r\n', resdata)
        res.close()
        store.close()

        
if __name__ == '__main__':
      unittest.main()
