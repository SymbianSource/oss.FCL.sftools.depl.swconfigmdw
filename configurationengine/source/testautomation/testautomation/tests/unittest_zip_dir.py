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

import os, unittest, zipfile
from testautomation import zip_dir

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
test_data_dir = os.path.join(ROOT_PATH, 'testdata/zip_dir/test')
temp_dir      = os.path.join(ROOT_PATH, 'temp/zip_dir')

class TestZipDir(unittest.TestCase):
    def test_zip_dir(self):
        zip_file = os.path.join(temp_dir, 'test.zip')
        if os.path.exists(zip_file):
            os.remove(zip_file)
        
        zip_dir.zip_dir(test_data_dir, zip_file, [zip_dir.SVN_IGNORE_PATTERN, r'^ignored.txt$'])
        
        self.assertTrue(os.path.isfile(zip_file))
        
        zf = zipfile.ZipFile(zip_file, 'r')
        namelist = zf.namelist()
        zf.close()
        
        expected = [
            'test.txt',
            'subdir1/test.txt',
            'subdir1/empty_dir/',
            'subdir1/subsubdir/test.txt',
            'subdir2/empty_dir/',
        ]
        self.assertEquals(sorted(expected), sorted(namelist))