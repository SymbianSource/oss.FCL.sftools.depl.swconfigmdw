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
Test the CPF configuration
"""
import unittest
import string
import sys,os,shutil
import difflib, zipfile
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
            
from testautomation import unzip_file

from cone.public import exceptions, utils, api
from cone.storage.filestorage import FileStorage
from cone.storage.zipstorage import ZipStorage

ROOT_PATH  = os.path.dirname(os.path.abspath(__file__))
temp_dir   = os.path.join(ROOT_PATH, "temp/import")
test_cpf   = os.path.join(ROOT_PATH,"testdata/test_project.cpf")
datafolder = os.path.join(ROOT_PATH,"../../storage/tests/data")


class TestConeProjectImport(unittest.TestCase):    
    def setUp(self):
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
    def test_import_to_zipstorage(self):
        test_project_dir = os.path.join(temp_dir, "test_project_1")
        unzip_file.unzip_file(test_cpf, test_project_dir, delete_if_exists=True)
        
        imported_zip = os.path.join(temp_dir, "imported1.zip")
        
        fs = FileStorage(test_project_dir)
        p  = api.Project(fs)
        zs = ZipStorage(imported_zip,"w")
        zp  = api.Project(zs)
        conf = p.get_configuration('root5.confml')
        conf_files = conf.list_resources()
        conf_files.append('.metadata')
        zp.import_configuration(conf)
        zp.close()
        p.close()
        self.assertTrue(os.path.exists(imported_zip))
        zfile = zipfile.ZipFile(imported_zip,"r")
        files = zfile.namelist()
        conf_files.sort()
        files.sort()
        self.assertEquals(conf_files,files)
        zfile.close()
        os.unlink(imported_zip)

    def test_import_to_zipstorage_multiple_configurations(self):
        imported_zip = os.path.join(temp_dir, "imported2.zip")
        fs = FileStorage(datafolder)
        p  = api.Project(fs)
        zs = ZipStorage(imported_zip,"w")
        zp  = api.Project(zs)
        conf = p.get_configuration('morestuff.confml')
        conf_files = conf.list_resources()
        zp.import_configuration(conf)
        conf = p.get_configuration('prodX.confml')
        conf_files.extend(conf.list_resources())
        zp.import_configuration(conf)
        zp.close()
        p.close()
        self.assertTrue(os.path.exists(imported_zip))
        zfile = zipfile.ZipFile(imported_zip,"r")
        files = zfile.namelist()
        files.remove('.metadata')
        conf_files = utils.distinct_array(conf_files)
        conf_files.sort()
        files.sort()
        for i in range(len(conf_files)):
            self.assertEquals(conf_files[i], files[i])        
        zfile.close()
        os.unlink(imported_zip)

    def test_import_to_filestorage_multiple_configurations(self):        
        fs = FileStorage(datafolder)
        p  = api.Project(fs)
        fs2 = FileStorage("temp/imported","w")
        p2  = api.Project(fs2)
        conf = p.get_configuration('morestuff.confml')
        conf_files = conf.list_resources()
        p2.import_configuration(conf)
        conf = p.get_configuration('prodX.confml')
        conf_files.extend(conf.list_resources())
        
        p2.import_configuration(conf)
        p2.close()
        self.assertTrue(os.path.exists("temp/imported"))
        files = fs2.list_resources("/",recurse=True)
        
        conf_files = utils.distinct_array(conf_files)
        conf_files.append('.metadata')
        files.sort()
        conf_files.sort()
        self.assertEquals(conf_files,files)
        shutil.rmtree("temp")

    def test_import_from_zipstorage_to_filestorage(self):
        imported_folder = os.path.join(temp_dir, 'imported1_folder')
        p  = api.Project(api.Storage.open(test_cpf))
        rp  = api.Project(api.Storage.open(imported_folder,"w"))
        conf = p.get_configuration(p.get_storage().get_active_configuration())
        conf_files = conf.list_resources()
        conf_files.append('.metadata')
        rp.import_configuration(conf)
        rp.close()
        p.close()
        self.assertTrue(os.path.exists(imported_folder))
        store = api.Storage.open(imported_folder)
        files = store.list_resources('',recurse=True)
        conf_files.sort()
        files.sort()
        self.assertEquals(conf_files,files)
        shutil.rmtree(imported_folder)

if __name__ == '__main__':
    unittest.main()
      
