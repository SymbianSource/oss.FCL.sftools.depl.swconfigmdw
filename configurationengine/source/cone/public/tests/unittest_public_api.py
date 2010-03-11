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
import os
import __init__
from cone.public import *

class TestPublicApiConfiguration(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_api_configuration_creation(self):
        config = api.Configuration("test")
        self.assertTrue(config!=None)


class TestPluginFactory(unittest.TestCase):
    class FactoryTestImplReader(plugin.ReaderBase):
        FILE_EXTENSIONS = ['factorytest']
    
    class ConeDummyReader(persistence.ConeReader):
        @classmethod
        def supported_elem(cls, elemname):
            if elemname.lower() == "dummy":
                return True
            else:
                return False
        def __init__(self):
            super(persistence.ConeReader,self).__init__()
            
    class ConeDummyWriter(persistence.ConeWriter):
        @classmethod
        def supported_class(cls, classname):
            if classname.lower() == "dummy":
                return True
            else:
                return False

        def __init__(self):
            super(persistence.ConeWriter,self).__init__()
    


    def test_factory_is_supported_impl_file(self):
        plugin.ImplFactory.set_reader_classes_override([self.FactoryTestImplReader])
        try:
            self.assertTrue(api.Factory().is_supported_impl_file("some_file.factorytest"))
            self.assertTrue(api.Factory().is_supported_impl_file("SOME_FILE.FACTORYTEST"))
            self.assertFalse(api.Factory().is_supported_impl_file("some_file.foo"))
        finally:
            plugin.ImplFactory.set_reader_classes_override(None)
    
    def test_get_reader_fails(self):
        try:
            api.Factory().get_reader_for_elem("")
            self.fail("Not existing reader creation succeeds?")
        except exceptions.ConePersistenceError,e:
            self.assertTrue(True)

    def test_get_writer_fails(self):
        try:
            api.Factory().get_writer_for_class("")
            self.fail("Not existing writer creation succeeds?")
        except exceptions.ConePersistenceError,e:
            self.assertTrue(True)

    def test_get_reader_ok(self):
        r = api.Factory().get_reader_for_elem("Dummy")
        self.assertTrue(isinstance(r,TestPluginFactory.ConeDummyReader))

    def test_get_reader_low(self):
        r = api.Factory().get_reader_for_elem("dummy")
        self.assertTrue(isinstance(r,TestPluginFactory.ConeDummyReader))

    def test_get_reader_upper(self):
        r = api.Factory().get_reader_for_elem("DUMMY")
        self.assertTrue(isinstance(r,TestPluginFactory.ConeDummyReader))

    def test_get_writer_ok(self):
        r = api.Factory().get_writer_for_class("Dummy")
        self.assertTrue(isinstance(r,TestPluginFactory.ConeDummyWriter))
