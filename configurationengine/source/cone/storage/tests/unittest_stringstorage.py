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

import unittest
import string
import sys,os
import pickle
import __init__

from cone.public import api
from cone.storage import stringstorage

class TestStringStorage(unittest.TestCase):
    def test_internal_add_and_list(self):
        store = api.Storage.open("test.pk","w")
        store._add_to_path("test.foo.bar",stringstorage._StringStorageObject("test1.txt"))
        store._add_to_path("test.foo.bar",stringstorage._StringStorageObject("test2.txt"))
        self.assertEquals(store._get("test.foo.bar")._list(), 
                          ['test1',
                          'test2'])
        store.close()
        os.unlink("test.pk")

    def test_internal_add_get_and_list(self):
        store = api.Storage.open("test.pk","w")
        obj = stringstorage._StringStorageObject("test1.txt")
        store._add_to_path("test.foo.bar",obj)
        store._add_to_path("test.foo.bar",stringstorage._StringStorageObject("test2.txt"))
        obj.data = "Fooo"
        self.assertEquals(store._get("test.foo.bar")._list(), 
                          ['test1',
                          'test2'])
        self.assertEquals(store.test.foo.bar.test1.data,'Fooo')
        store.close()
        os.unlink("test.pk")

    def test_internal_add_get_and_list_all(self):
        store = api.Storage.open("test.pk","w")
        store._add_to_path("test.foo.bar",stringstorage._StringStorageObject("test1.txt"))
        store._add_to_path("test.foo.bar",stringstorage._StringStorageObject("test2.txt"))
        store._add(stringstorage._StringStorageObject("root.txt"))
        self.assertEquals(store._list_traverse(type=stringstorage._StringStorageObject), ['test.foo.bar.test1',
                                                      'test.foo.bar.test2',
                                                      'root'])
        store.close()
        os.unlink("test.pk")

