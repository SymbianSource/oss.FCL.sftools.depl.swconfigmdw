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

import unittest, os, shutil

from commandplugin import commandml 

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
TMP_PATH = os.path.join(ROOT_PATH, 'temp')
TMP_FILE1 = os.path.join(TMP_PATH, 'sub/one.txt')
TMP_FILE2 = os.path.join(TMP_PATH, 'foobar/two.txt')
TMP_FILE3 = os.path.join(TMP_PATH, 'three.txt')

def norm(path):
    return os.path.normpath(path)

def create_file(path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    f = open(path, "w")
    f.write('something...')
    f.close()
        
class TestCommandUtil(unittest.TestCase):
    def test_get_folder_set(self):
        if os.path.exists(TMP_PATH):
            shutil.rmtree(TMP_PATH)
        os.mkdir(TMP_PATH)
        create_file(TMP_FILE1)
        fset1 = commandml.get_folder_set(TMP_PATH)

        self.assertEquals(len(fset1), 1)
        self.assertEquals(fset1, set([norm('sub/one.txt')]))
        
        create_file(TMP_FILE2)
        create_file(TMP_FILE3)
        fset2 = commandml.get_folder_set(TMP_PATH)
        nset = fset2 - fset1
        self.assertEquals(nset, set([norm('foobar/two.txt'), 
                                     norm('three.txt')]))
        

if __name__ == '__main__':
    unittest.main()
