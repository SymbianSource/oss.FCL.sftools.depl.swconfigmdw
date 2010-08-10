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
import string
import sys
import os
import shutil

from cone.public import api, exceptions, persistence
from cone.storage import filestorage
from cone.confml import persistentconfml, model, confmltree

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class TestConfmlXml(unittest.TestCase):
       
    def test_namespaces(self):
        root = confmltree.Element('root')
        elem = confmltree.Element('{http://spam.effbot.org}egg')
        root.append(elem)
        elem.append(confmltree.Element('{http://spam.effbot.org}ham'))
        elem.append(confmltree.Element('{http://test.com}foo'))
        str = confmltree.tostring(root, {'http://spam.effbot.org': 'ham',
                              'http://test.com': 'bar'})
        et = confmltree.fromstring(str)
        self.assertTrue(et)
        self.assertEquals(str,'<root xmlns:bar="http://test.com" xmlns:ham="http://spam.effbot.org"><ham:egg><ham:ham /><bar:foo /></ham:egg></root>')


if __name__ == '__main__':
    unittest.main()
