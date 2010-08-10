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

from cone.storage import authenticate

ROOT_PATH   = os.path.dirname(os.path.abspath(__file__))

class TestCarbonAuthHandler(unittest.TestCase):
    def setUp(self):
        self.test_user   = "admin"
        self.test_passwd = "minda"
        
    def callback_username(self):
        return self.test_user

    def callback_password(self):
        return self.test_passwd
        
    def test_username_password_func(self):
        carbon_handler = authenticate.CarbonAuthHandler()
        carbon_handler.add_username_func(self.callback_username)
        carbon_handler.add_password_func(self.callback_password)
        username = carbon_handler.get_username()
        password = carbon_handler.get_password()
        self.assertEqual(self.test_user,username)
        self.assertEqual(self.test_passwd,password)        
   
if __name__ == '__main__':
    unittest.main()

