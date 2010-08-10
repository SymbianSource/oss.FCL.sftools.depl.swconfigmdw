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

import unittest
import os
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

from cone.public.exceptions import StorageException
from cone.public import api
from cone.storage import filestorage


class TestFileResource(unittest.TestCase):    
    def setUp(self):
        self.spath = os.path.join(ROOT_PATH,"fileres_test")
        self.storage = filestorage.FileStorage(self.spath)

    def tearDown(self):
        self.storage.close()
    
    def test_open_and_write_resource(self):
        res = self.storage.open_resource("testwrite.txt","w")
        res.write("Testing writing func!")
        res.close()
        f = open(self.spath+"/testwrite.txt","r")
        data = f.read()
        self.assertEquals(data,"Testing writing func!")
        f.close()
        os.unlink(os.path.join(ROOT_PATH,"fileres_test/testwrite.txt"))

    def test_open_and_read_resource(self):
        res = self.storage.open_resource("testread.txt","r")
        resdata = res.read()
        res.close()
        f = open(self.spath+"/testread.txt","r")
        data = f.read()
        f.close()
        self.assertEquals(data,resdata)  

    def test_open_and_write_resource_and_trunk_it(self):
        res = self.storage.open_resource("testtrunk.txt","w")
        res.write("Testing writing func!")
        res.truncate()
        res.close()
        f = open(self.spath+"/testtrunk.txt","r")
        data = f.read()
        self.assertEquals(data,"")
        f.close()
        os.unlink(os.path.join(ROOT_PATH,"fileres_test/testtrunk.txt"))
    
    def test_get_size(self):
        res = self.storage.open_resource("testread.txt", "r")
        self.assertEquals(res.get_size(), 15)
        # Try a second time just in case
        self.assertEquals(res.get_size(), 15)
        res.close()
    
    def test_get_size_largefile(self):
        res = self.storage.open_resource("largefile.bin", "r")
        self.assertEquals(res.get_size(), 25000)
        # Try a second time just in case
        self.assertEquals(res.get_size(), 25000)
        res.close()
    
    def test_get_size_fails_in_write_mode(self):
        res = self.storage.open_resource("test_getsize.txt","w")
        res.write("Writing foobar")
        self.assertRaises(StorageException, res.get_size)
        res.close()

    def test_bmp_content_info_24bit(self):
        res = self.storage.open_resource("image-bmp-24bit.bmp", "r")
        content_info = res.get_content_info()
        self.assertEquals(api.BmpImageContentInfo, type(content_info))
        self.assertEquals(24, res.get_content_info().color_depth)
        self.assertEquals(24, content_info.color_depth)
        self.assertEquals('image', content_info.mimetype)
        self.assertEquals('bmp', content_info.mimesubtype)
        self.assertEquals('image/bmp', content_info.content_type)
        res.close()

    def test_bmp_content_info_8bit(self):
        res = self.storage.open_resource("image-bmp-8bit.bmp", "r")
        content_info = res.get_content_info()
        self.assertEquals(api.BmpImageContentInfo, type(content_info))
        self.assertEquals(8, res.get_content_info().color_depth)
        self.assertEquals(8, content_info.color_depth)
        self.assertEquals('image', content_info.mimetype)
        self.assertEquals('bmp', content_info.mimesubtype)
        self.assertEquals('image/bmp', content_info.content_type)
        res.close()

    def test_bmp_content_info_4bit(self):
        res = self.storage.open_resource("image-bmp-4bit.bmp", "r")
        content_info = res.get_content_info()
        self.assertEquals(api.BmpImageContentInfo, type(content_info))
        self.assertEquals(4, res.get_content_info().color_depth)
        self.assertEquals(4, content_info.color_depth)
        self.assertEquals('image', content_info.mimetype)
        self.assertEquals('bmp', content_info.mimesubtype)
        self.assertEquals('image/bmp', content_info.content_type)
        res.close()

    def test_bmp_content_info_1bit(self):
        res = self.storage.open_resource("image-bmp-1bit.bmp", "r")
        content_info = res.get_content_info()
        self.assertEquals(api.BmpImageContentInfo, type(content_info))
        self.assertEquals(1, res.get_content_info().color_depth)
        self.assertEquals(1, content_info.color_depth)
        self.assertEquals('image', content_info.mimetype)
        self.assertEquals('bmp', content_info.mimesubtype)
        self.assertEquals('image/bmp', content_info.content_type)
        res.close()

    def test_content_info_with_jpg(self):
        res = self.storage.open_resource("image-jpeg-1bit.jpg", "r")
        content_info = res.get_content_info()
        self.assertEquals('image/jpeg', content_info.content_type)
        self.assertEquals('image', content_info.mimetype)
        self.assertEquals('jpeg', content_info.mimesubtype)
        res.close()


    def test_content_info_invalid_bmp(self):
        res = self.storage.open_resource("invalid.bmp", "r")
        content_info = res.get_content_info()
        self.assertEquals('image/bmp', content_info.content_type)
        self.assertEquals('image', content_info.mimetype)
        self.assertEquals('bmp', content_info.mimesubtype)
        res.close()
        
    def test_get_content_info_and_read_data(self):
        res = self.storage.open_resource("testread.txt", "rb")
        ci = res.get_content_info()
        self.assertEquals('text/plain', ci.content_type)
        data = res.read()
        self.assertEquals('foo bar test.\r\n', data)
        res.close()
        
if __name__ == '__main__':
    unittest.main()
