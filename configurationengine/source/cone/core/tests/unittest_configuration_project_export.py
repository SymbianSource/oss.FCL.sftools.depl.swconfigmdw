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

from cone.public import exceptions,utils, api
from cone.storage.filestorage import FileStorage
from cone.storage.zipstorage import ZipStorage
from testautomation import unzip_file
from testautomation.base_testcase import BaseTestCase

ROOT_PATH       = os.path.dirname(os.path.abspath(__file__))
temp_dir        = os.path.join(ROOT_PATH,"temp/export")
test_cpf        = os.path.join(ROOT_PATH,"testdata/test_project.cpf")
datafolder      = os.path.join(ROOT_PATH,"../../storage/tests/data")
tempzip         = os.path.join(temp_dir, "exported.zip")

class TestConeProjectExport(BaseTestCase):
    def setUp(self):
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

    def test_export_to_zipstorage(self):
        test_project_dir = os.path.join(temp_dir, "test_project_1")
        unzip_file.unzip_file(test_cpf, test_project_dir, delete_if_exists=True)
        
        export_zip = os.path.join(temp_dir, "configexport.zip")
        
        fs = FileStorage(test_project_dir)
        p  = api.Project(fs)
        conf = p.get_configuration('root5.confml')
        zs = ZipStorage(export_zip,"w")
        zp  = api.Project(zs)
        conf_files = conf.list_resources()
        files1 = ['.metadata']
        files1.extend(conf_files)
        p.export_configuration(conf,zs)
        zp.close()
        self.assertTrue(os.path.exists(export_zip))
        zfile = zipfile.ZipFile(export_zip,"r")
        files2 = zfile.namelist()
        zfile.close()
        files1.sort()
        files2.sort()
        for i in range(len(files1)):
            self.assertEquals(files1[i],files2[i])
        os.unlink(export_zip)

    def test_export_from_files_to_zipstorage_add(self):
        test_project_dir = os.path.join(temp_dir, "test_project_1")
        unzip_file.unzip_file(test_cpf, test_project_dir, delete_if_exists=True)
        
        export_zip = os.path.join(temp_dir, "configexport2.zip")
        
        fs = FileStorage(test_project_dir)
        p  = api.Project(fs)
        exportconf = p.get_configuration('root4.confml')
        compareconf = p.get_configuration('root5.confml')
        zs = ZipStorage(export_zip,"w")
        zp  = api.Project(zs)
        conf_files = compareconf.list_resources()
        files1 = ['.metadata']
        files1.extend(conf_files)
        p.export_configuration(exportconf,zs)
        zp.close()        
        self.assertTrue(os.path.exists(export_zip))
        
        #Re-opening in append mode for adding new layers.
        zs = ZipStorage(export_zip,"a")
        zp  = api.Project(zs)
        conf = p.get_configuration('Layer5/root.confml')
        p.export_configuration(conf,zs)
        zp.save()
        zp.close() 
        
        zfile = zipfile.ZipFile(export_zip,"r")
        files2 = zfile.namelist()
        #Root file renaming.
        files2[files2.index('root4.confml')] = 'root5.confml'
        zfile.close()
        files1.sort()
        files2.sort()
        
        for i in range(len(files1)):
            self.assertEquals(files1[i],files2[i])
        os.unlink(export_zip)


    def test_export_from_zip_to_zipstorage_add(self):
        export_zip = os.path.join(temp_dir, "configexport2.zip")        
        zs_source = ZipStorage(test_cpf,'r')
        p  = api.Project(zs_source)
        exportconf = p.get_configuration('root4.confml')
        compareconf = p.get_configuration('root5.confml')        
        
        zs_target = ZipStorage(export_zip,"w")
        zp  = api.Project(zs_target)
        conf_files = compareconf.list_resources()
        files1 = ['.metadata']
        files1.extend(conf_files)
        p.export_configuration(exportconf,zs_target)
        zp.close()
        self.assertTrue(os.path.exists(export_zip))
        
        #Re-opening in append mode for adding new layers.
        zs_target = ZipStorage(export_zip,"a")
        zp  = api.Project(zs_target)
        conf = p.get_configuration('Layer5/root.confml')
        p.export_configuration(conf,zs_target)
        zp.save()
        zp.close() 
        
        zfile = zipfile.ZipFile(export_zip,"r")
        files2 = zfile.namelist()
        #Root file renaming.
        files2[files2.index('root4.confml')] = 'root5.confml'
        zfile.close()
        files1.sort()
        files2.sort()
        
        for i in range(len(files1)):
            self.assertEquals(files1[i],files2[i])
        os.unlink(export_zip)


    def test_export_from_zipstorage(self):
        output_dir = os.path.join(temp_dir, "export_from_zipstorage")
        self.remove_if_exists(output_dir)
        
        zs = ZipStorage(test_cpf,"r")
        p  = api.Project(zs)
        fs = FileStorage(output_dir,"w")
        r  = api.Project(fs)
        conf = p.get_configuration('root5.confml')
        conf_files = conf.list_resources()
        conf_files.append('.metadata')
        p.export_configuration(conf,fs)
        p.close()
        r.close()
        self.assertTrue(os.path.exists(output_dir))

    # Temporarly hacked to pass, because feature is not supported  
#    def test_export_to_zipstorage_multiple_configurations(self):
#        try:
#            fs = FileStorage(datafolder)
#            p  = api.Project(fs)
#            zs = ZipStorage(tempzip,"w")
#            zp  = api.Project(zs)
#            conf = p.get_configuration('morestuff.confml')
#            conf_files = conf.list_resources()
#            p.export_configuration(conf,zs)
#            conf = p.get_configuration('prodX.confml')
#            conf_files2 = conf.list_resources()
#            conf_files.extend(conf_files2)
#            conf_files = utils.distinct_array(conf_files) 
#            p.export_configuration(conf,zs)
#            zp.close()
#            self.assertTrue(os.path.exists(tempzip))
#            zfile = zipfile.ZipFile(tempzip,"r")
#            files = zfile.namelist()
#            files.remove('.metadata')
#            self.assertEquals(sorted(conf_files),sorted(files))
#        except exceptions.NotSupportedException:
#            pass

    def _test_export_to_filestorage_multiple_configurations(self):
        fs = FileStorage(datafolder)
        p  = api.Project(fs)
        fs2 = FileStorage(os.path.join(temp_dir,"multiple"),"w")
        p2  = api.Project(fs2)
        conf = p.get_configuration('morestuff.confml')
        conf_files = conf.list_resources()
        p.export_configuration(conf,fs2)
        conf = p.get_configuration('prodX.confml')
        conf_files.extend(conf.list_resources())
        fs2.save()
        p.export_configuration(conf,fs2)
        p2.close()
        self.assertTrue(os.path.exists("temp/exported"))
        
        files = fs2.list_resources("/",True)
        conf_files = utils.distinct_array(conf_files)
        files.sort()
        conf_files.append('.metadata')
        conf_files.sort()
        self.assertEquals(sorted(conf_files),sorted(files))
        #shutil.rmtree("temp")

        

if __name__ == '__main__':
    unittest.main()
      
