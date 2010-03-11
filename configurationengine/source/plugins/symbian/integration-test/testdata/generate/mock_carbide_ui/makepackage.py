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

import sys, os, random

output_dir = ''
uid = None

for i, item in enumerate(sys.argv):
    if item == '-output' and i + 1 < len(sys.argv):
        output_dir = sys.argv[i + 1]
    elif item == '-uid' and i + 1 < len(sys.argv):
        uid = sys.argv[i + 1]

if uid is None:
    uid = "%016x" % random.getrandbits(64)
else:
    if uid.lower().startswith('0x'):
        uid = uid[2:]

#print "uid = %s" % uid


def write_file(file_path, data):
    dir = os.path.dirname(file_path)
    if dir != '' and not os.path.exists(dir):
        os.makedirs(dir)
    
    f = open(file_path, "wb")
    try:        f.write(data)
    finally:    f.close()

write_file(os.path.join(output_dir, 'themepackage.mbm'), 'xyz')
write_file(os.path.join(output_dir, 'themepackage.mif'), 'zyx')
write_file(os.path.join(output_dir, 'themepackage.skn'), 'foo')

pkg_data = r"""
IF PACKAGE(0X102032BE) ; CHECK FOR S60 3.1 STUB SIS
"themepackage.mbm" - "!:\resource\skins\%(uid)s\themepackage.mbm"
"themepackage.mif" - "!:\resource\skins\%(uid)s\themepackage.mif"
ELSE
"themepackage.mbm" - "!:\private\10207114\import\%(uid)s\themepackage.mbm"
"themepackage.mif" - "!:\private\10207114\import\%(uid)s\themepackage.mif"
ENDIF
"themepackage.skn" - "!:\private\10207114\import\%(uid)s\themepackage.skn"
;Dummy entry for the possible skin .ini file,so that it gets removed on uninstall
"" - "!:\private\10207114\import\%(uid)s\%(uid)s.ini",FN
""" % {'uid': uid}

write_file(os.path.join(output_dir, 'themepackage.pkg'), pkg_data)