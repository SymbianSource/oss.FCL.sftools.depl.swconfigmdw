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

from struct import pack, unpack
from hcrplugin.hcr_exceptions import InvalidHcrHeaderError

class HcrHeader(object):
    """
    """
    HEADER_FMT = '<4sHHIII12x'
    HEADER_SIGNATURE = 'HCRf'
    def __init__(self):
        self.version    = 0
        self.flags      = 0
        self.nrecords   = 0
        self.lsd_offset = 0
        self.lsd_size   = 0

    def loads(self, headerstr):
        if len(headerstr) != 32:
            raise InvalidHcrHeaderError('Invalid length of header data %r' % headerstr)
        
        result = unpack(self.HEADER_FMT, headerstr)
        if not result[0] == self.HEADER_SIGNATURE:
            raise InvalidHcrHeaderError('Invalid HCR signature in %r' % headerstr)
        self.version    = result[1]
        self.flags      = result[2]
        self.nrecords   = result[3]
        self.lsd_offset = result[4]
        self.lsd_size   = result[5]
        

    def dumps(self):
        return pack(self.HEADER_FMT, self.HEADER_SIGNATURE, self.version, 
                                    self.flags, 
                                    self.nrecords, 
                                    self.lsd_offset,
                                    self.lsd_size)