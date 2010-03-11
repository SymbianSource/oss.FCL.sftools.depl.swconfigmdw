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
## 
# @author Teemu Rytkonen


"""
Method base for Mapping model 2 model 
"""

class BaseMapper(object):
    """
    BaseMapper returns the object itself
    """
    def __init__(self):
        pass

    def map_object(self, object):
        """
        Return the object self
        """
        return object

