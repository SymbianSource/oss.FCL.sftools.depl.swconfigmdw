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

from shutil import copy
import os, re

class ThemeResource:   
    """
    This class represents the records about the theme resources which are saved in *.pkg file.
    Every record contains a filename of the resource (for example "themepackage.mbm"
    and a path where this resource will be copied in the output directory
    (for example "!:\private\10207114\import\99d49b086e6097b8\themepackage.mbm")
    """
   
    def __init__(self):
        self.list_resource=[]
        
    def parse_pkg_file(self,file_path):
        """
        parses *.pkg file and returns a array of classes ThemeResource
        The class ThemeResource contains a name of theme resource 
        and a path where this resource will be copied in the output directory
        """
        
        resource_pattern = re.compile(r'"(.*)"\s+-\s+"!:\\(.*)"')
        # for every row in pkg file
        for row in open(file_path, 'r'):
            mo = resource_pattern.match(row)
            if mo:
                resource = Resource(mo.group(1), os.path.split(mo.group(2))[0])
                self.list_resource.append(resource)
    
    def copy_files_from_theme(self, source_path, output_path):
        """
        copies theme resources from  source directory to theirs target paths 
        """
        for resource in self.list_resource:
            source_file = os.path.join(source_path, resource.get_filename())
            target_dir =  os.path.join(output_path, resource.get_path())
            self.copy_files(source_file, target_dir)          
        
    def copy_files(self, source_path, target_path):
        """
        copy files from source to target. If the target directory doesn't exist then it is created
        """
        if os.path.exists(source_path) != True or os.path.isdir(source_path):
            return
        
        if os.path.exists(target_path) != True:
            os.makedirs(target_path)
        copy(source_path, target_path)  
        
    def modify_resource_path(self, path):
        """
        Modifies the path of them resource. 
        If the paths contains string "private" or "Data" (it says that the path is target path) then it removes 
        these chars "!:\" from the path of theme resource
        """
        if path.find("private") != -1 or path.find("Data") != -1:
            if path.startswith("!:\\"):
                index = path.rfind("\\")
                path =  path[3:index]
            
        return path

        
class Resource(object):   
    """
    This class represents a record about the theme resource. It contains a filename of the resource 
    (for example "themepackage.mbm" and a path where this resource will be copied in the output directory
    (for example "!:\private\10207114\import\99d49b086e6097b8\themepackage.mbm")
    """
    
    def __init__(self, filename,path):
        # the name of theme resource
        self.filename = filename
        # the path of theme resource
        self.path = path
        
    def get_filename(self):
        return self.filename
    
    def get_path(self):
        return self.path
    
    def set_path(self,path):
        self.path = path
        
    def set_filename(self,filename):
        self.filename = filename        