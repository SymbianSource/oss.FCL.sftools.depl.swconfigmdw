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

import os, zipfile, shutil

def unzip_file(file, dir, delete_if_exists=False):
    if os.path.exists(dir):
        if delete_if_exists == True:
            shutil.rmtree(dir)
        else:
            raise RuntimeError("Directory '%s' already exists" % dir)
    if not os.path.exists(file):
        raise RuntimeError("File '%s' does not exist" % file)
    
    os.makedirs(dir)
    zf = zipfile.ZipFile(file)
    
    try:
        for name in zf.namelist():
            if name.endswith('/'):
                path = os.path.join(dir, name)
                if not os.path.exists(path):
                    os.makedirs(path)
            else:
                path = os.path.join(dir, name)
                dirname = os.path.dirname(path)
                if dirname != '' and not os.path.exists(dirname):
                    os.makedirs(dirname)
                f = open(path, 'wb')
                try:        f.write(zf.read(name))
                finally:    f.close()
    finally:
        zf.close()

def unzip_file_if_newer(file, dir):
    if not os.path.exists(file):
        raise RuntimeError("File '%s' does not exist" % file)
    
    if not os.path.exists(dir) or os.stat(file)[8] > os.stat(dir)[8]:
        unzip_file(file, dir, True)
