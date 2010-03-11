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

import sys, os

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

if sys.platform == "win32":
    CONE_SCRIPT = "cone.cmd"
else:
    CONE_SCRIPT = "cone.sh"

def get_cmd(action):
    """Return the command used to run the ConE sub-action"""
    if 'CONE_PATH' in os.environ:
        CONE_CMD = os.path.join(os.environ['CONE_PATH'], CONE_SCRIPT)
        if not os.path.exists(CONE_CMD):
            raise RuntimeError("'%s' does not exist!" % CONE_CMD)
        return '"%s" %s' % (CONE_CMD, action)
    else:
        return 'python "%s" %s' % (os.path.normpath(os.path.join(ROOT_PATH,'../cone_tool.py')), action)
