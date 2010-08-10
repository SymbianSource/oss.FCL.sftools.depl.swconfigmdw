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
import os

from cone.storage import filestorage, zipstorage
from cone.public.tests import unittest_layer
from testautomation.utils import remove_if_exists

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
LAYER_TMP_FOLDER = os.path.join(ROOT_PATH, "temp/layertest")
LAYER_TMP_ZIP = os.path.join(ROOT_PATH, "temp/layertest.zip")

##########################################################################
# FileStorage tests for folder and layer actions

class TestFolderOnFileStorage(unittest_layer.TestFolder):
    def setUp(self):
        self.store = filestorage.FileStorage(LAYER_TMP_FOLDER,"w")

    def tearDown(self):
        remove_if_exists(LAYER_TMP_FOLDER)

class TestLayerOnFileStorage(unittest_layer.TestLayer):
    def setUp(self):
        self.store = filestorage.FileStorage(LAYER_TMP_FOLDER,"w")

    def tearDown(self):
        remove_if_exists(LAYER_TMP_FOLDER)

class TestCompositeLayerOnFileStorage(unittest_layer.TestCompositeLayer):
    def setUp(self):
        self.store = filestorage.FileStorage(LAYER_TMP_FOLDER,"w")

    def tearDown(self):
        remove_if_exists(LAYER_TMP_FOLDER)

##########################################################################
# ZipStorage


#class TestFolderOnZipStorage(unittest_layer.TestFolder):
#    def setUp(self):
#        self.store = zipstorage.ZipStorage(LAYER_TMP_ZIP,"w")
#
#    def tearDown(self):
#        self.store.close()
#        remove_if_exists(LAYER_TMP_ZIP)
#
#class TestLayerOnZipStorage(unittest_layer.TestLayer):
#    def setUp(self):
#        self.store = zipstorage.ZipStorage(LAYER_TMP_ZIP,"w")
#
#    def tearDown(self):
#        self.store.close()
#        remove_if_exists(LAYER_TMP_ZIP)
#
#class TestCompositeLayerOnZipStorage(unittest_layer.TestCompositeLayer):
#    def setUp(self):
#        self.store = zipstorage.ZipStorage(LAYER_TMP_ZIP,"w")
#
#    def tearDown(self):
#        self.store.close()
#        remove_if_exists(LAYER_TMP_ZIP)


if __name__ == '__main__':
    unittest.main()

