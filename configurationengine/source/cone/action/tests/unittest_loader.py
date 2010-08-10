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
from cone.action import loader


class TestGetAction(unittest.TestCase):
    
    def test_create_fix_action(self):
        
        self.assertTrue(loader.get_module('fix'))
        self.assertTrue(loader.get_class('fix'))
 
if __name__ == '__main__':
    unittest.main()
