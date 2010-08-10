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

from cone.public import api, exceptions, mapping

class TestMapping(unittest.TestCase):
    def test_get_mapper(self):
        mapper = api.get_mapper('confml')
        self.assertTrue(isinstance(mapper, mapping.BaseMapper))

    def test_map_feature(self):
        fea = api.Feature("test")
        mapper = fea._get_mapper('confml')
        fea2 = mapper.map_object(fea)
        self.assertEquals(fea,fea2)