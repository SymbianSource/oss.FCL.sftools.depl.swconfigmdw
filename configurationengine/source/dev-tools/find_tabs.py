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

import os, os.path

def main(start):
    for root, dirs, files in os.walk(start):
        for fn in files:
            if not fn.endswith('.py'):
                continue
            full_name = os.path.join(root, fn)
            f = open(full_name)
            for index, line in enumerate(f.readlines()):
                if '\t' in line:
                    print '%s:%s: %s' % (full_name, index, line.rstrip())
            f.close()

if __name__ == '__main__':
    import sys
    if len(sys.argv):
        main(sys.argv[1])
    else:
        main('.')