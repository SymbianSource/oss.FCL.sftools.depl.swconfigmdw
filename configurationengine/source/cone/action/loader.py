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

import os
import sys
import fnmatch 
import re
import logging


def get_class(action_name):
    """
    Try to get the SubAction class if it is available
    """
    module = get_module(action_name)
    return module.get_class()

def get_module(action_name):
    """
    Try to get the SubAction class if it is available
    """
    # trust that the scripts are all in scripts module
    _temp = __import__('cone.action', globals(), locals(), [action_name], -1)
    module = _temp.__getattribute__(action_name)
    return module