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

__version__ = 0.1


import pkg_resources 
import sys,os

try:
  pkg_resources.require("Cone")
except pkg_resources.DistributionNotFound:
  ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
  sys.path.append(ROOT_PATH)
  sys.path.append(os.path.join(ROOT_PATH,'..'))
  sys.path.append(os.path.join(ROOT_PATH,'../..'))
