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
import sys
import os
import shutil
import datetime

from cone.public import api, exceptions
from cone.carbon import resourcemapper, model
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class TestCarbonResourceMapper(unittest.TestCase):
    def test_map_confmL_configuration_to_carbon_path(self):
        self.assertEquals(resourcemapper.CarbonResourceMapper().map_confml_resource("configurationroot","test.confml"),"test.configurationroot")
        self.assertEquals(resourcemapper.CarbonResourceMapper().map_confml_resource("configurationlayer","test/root.confml"),"test.configurationlayer")
        self.assertEquals(resourcemapper.CarbonResourceMapper().map_confml_resource("featurelist","featurelists/test (WORKING).confml"),"test (WORKING).featurelist")

    def test_map_carbon_configuration_to_confml_path(self):
        self.assertEquals(resourcemapper.CarbonResourceMapper().map_carbon_resource("test.configurationroot"),"test.confml")
        self.assertEquals(resourcemapper.CarbonResourceMapper().map_carbon_resource("foobar_test_one.configurationroot"),"foobar_test_one.confml")
        self.assertEquals(resourcemapper.CarbonResourceMapper().map_carbon_resource("foobar (WORKING).featurelist"),"featurelists/foobar (WORKING).confml")
        self.assertEquals(resourcemapper.CarbonResourceMapper().map_carbon_resource("foobar.featurelist"),"featurelists/foobar.confml")

