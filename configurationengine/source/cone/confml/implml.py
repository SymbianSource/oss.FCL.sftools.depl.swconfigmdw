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

import sys
import os

from cone.public import plugin, utils, exceptions

debug = 0

class Implml(plugin.ImplBase):
    """
    Base class for any  implementation plugin. 
    """
    def __init__(self,ref,configuration,output='output'):
        plugin.ImplBase.__init__(self,ref,configuration)
        self.set_output_root(output)
        pass

    def list_output_files(self):
        return utils.list_files(self.output)


    def has_ref(self, refs):
        """
        Return True if the implementation uses the given ref as input value. Otherwise return False.
        """
        raise exceptions.NotSupportedException()
