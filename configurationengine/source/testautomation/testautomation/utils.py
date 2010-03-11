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

def hex_to_bindata(hexdata):
    hexdata = hexdata.replace(' ', '').replace('\r', '').replace('\n', '').replace('\t', '')
    if len(hexdata) % 2 != 0:
        raise ValueError("'%s' is not divisible by 2", hexdata)
    for c in hexdata:
        if c not in "0123456789abcdefABCDEF":
            raise ValueError("'%s' is not a valid hex string", hexdata)
    
    temp = []
    for i in xrange(len(hexdata) / 2):
        start = i * 2
        end   = start + 2 
        temp.append(chr(int(hexdata[start:end], 16)))
    return ''.join(temp)