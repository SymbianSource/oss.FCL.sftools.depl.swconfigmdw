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

import sys, zipfile, os, os.path

def unzip_file_into_dir(file, dir):
    if (os.path.exists(file) is not True):
        return
    
    if (os.path.exists(dir) is not True):
        os.mkdir(dir, 0777)
        
    zfobj = zipfile.ZipFile(file)
    for name in zfobj.namelist():
        filePath = dir + name
        if name.endswith('/'):
            os.mkdir(filePath)
        else:
            createEmtyResource(filePath)
            outfile = open(dir+ name, 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()

def createEmtyResource(path):
    splitdrive = os.path.splitdrive(path)
    splitPath = os.path.split(splitdrive[1])

    pathS = os.path.split(splitPath[1])
    splited = path.split("/")
    tempPath = ""
    for i in range(0,len(splited)-1):
        tempPath = tempPath+splited[i]
        if (os.path.exists(tempPath) is not True):
             os.mkdir(tempPath)
        tempPath = tempPath+os.path.sep
    if (os.path.exists(path) is not True):
        file(path,'wt')
