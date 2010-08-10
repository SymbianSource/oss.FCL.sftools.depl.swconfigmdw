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

import sys, re

if len(sys.argv) not in (2, 3):
    print "Expected 1 or 2 arguments: "
    print "  <target_file> <revision> - Set revision to the supplied value"
    print "  <target_file>            - Set revision to ''"
    sys.exit(1)

filename = sys.argv[1]

if len(sys.argv) == 3:
    svnrevision = sys.argv[2]
    # Use the revision provided from command line only if it's valid
    if re.match('^[0-9]+(:[0-9]+)?M?S?$', svnrevision) is None:
        svnrevision = ''
else:
    svnrevision = ''

f = open(filename, "rt")
lines = f.readlines()
f.close()

# Replace the line with the svn revision variable
replaced = False
for i, line in enumerate(lines):
    if line.startswith('_svnrevision = "'):
        lines[i] = '_svnrevision = "%s"' % svnrevision
        replaced = True
    else:
        lines[i] = line.rstrip('\r\n')

if replaced:
    f = open(filename, "wt")
    for line in lines:
        print >>f, line
    f.close()
    print "Revision updated to '%s'" % svnrevision
else:
    print "Revision not updated: _svnrevision not found"
