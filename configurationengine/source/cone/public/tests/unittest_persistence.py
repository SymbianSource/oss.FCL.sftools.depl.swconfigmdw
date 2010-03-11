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
import string
import sys,os
import __init__

from cone.public import persistence, exceptions

class ConeDummyReader(persistence.ConeReader):
    
    @classmethod
    def supported_elem(cls, elemname):
        if elemname.lower() == "dum":
            return True
        else:
            return False
  
    def __init__(self):
        super(persistence.ConeReader,self).__init__()
    

class ConeDummyWriter(persistence.ConeWriter):
    @classmethod
    def supported_class(cls, classname):
        if classname.lower() == "dum":
            return True
        else:
            return False
  
    def __init__(self):
        super(persistence.ConeWriter,self).__init__()
    

class TestFactory(unittest.TestCase):    
    def setUp(self):
        pass

    # @test 
    def test_get_reader_fails(self):
        try:
            persistence.PersistenceFactory.get_reader_for_elem("")
            self.fail("Not existing reader creation succeeds?")
        except exceptions.ConePersistenceError,e:
            self.assertTrue(True)

    def test_get_writer_fails(self):
        try:
            persistence.PersistenceFactory.get_writer_for_class("")
            self.fail("Not existing writer creation succeeds?")
        except exceptions.ConePersistenceError,e:
            self.assertTrue(True)

    def test_get_reader_ok(self):
        r = persistence.PersistenceFactory.get_reader_for_elem("Dum")
        self.assertTrue(isinstance(r,ConeDummyReader))

    def test_get_reader_low(self):
        r = persistence.PersistenceFactory.get_reader_for_elem("dum")
        self.assertTrue(isinstance(r,ConeDummyReader))

    def test_get_reader_upper(self):
        r = persistence.PersistenceFactory.get_reader_for_elem("DUM")
        self.assertTrue(isinstance(r,ConeDummyReader))

    def test_get_writer_ok(self):
        r = persistence.PersistenceFactory.get_writer_for_class("Dum")
        self.assertTrue(isinstance(r,ConeDummyWriter))

    def test_get_writer_ok_low(self):
        r = persistence.PersistenceFactory.get_writer_for_class("dum")
        self.assertTrue(isinstance(r,ConeDummyWriter))



if __name__ == '__main__':
    unittest.main()
      
