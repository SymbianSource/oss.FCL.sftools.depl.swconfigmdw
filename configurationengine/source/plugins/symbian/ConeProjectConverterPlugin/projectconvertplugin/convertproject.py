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
'''
Convert project ConE plugin
'''

import re
import os
import sys
import logging
import xml.parsers.expat
import shutil
import fnmatch

try:
    from cElementTree import ElementTree
except ImportError:
    try:    
        from elementtree import ElementTree
    except ImportError:
        try:
            from xml.etree import cElementTree as ElementTree
        except ImportError:
            from xml.etree import ElementTree

import __init__

from cone.storage import filestorage
from cone.public import exceptions,plugin,utils,api

class ConvertProjectImpl(plugin.ImplBase):
    """
    Class to implements ConE plugin that convert old configuration to
    configuration project. Some extra functions supported in the top
    of normal file copying functions. For example creation of layer and
    configuration root files automatically. 
    """
    
    IMPL_TYPE_ID = "convertprojectml"
    
    
    def __init__(self,ref,configuration):
        """
        Overloading the default constructor
        """
        plugin.ImplBase.__init__(self,ref,configuration)
        self.desc = ""
        self.logger = logging.getLogger('cone.convertprojectml(%s)' % self.ref)
        self.errors = False
        
        #Internal plugin data
        self.project_data = {}
        self.layers = []

    def generate(self, context=None):
        """
        Generate the given implementation.
        """
        
        #Generating content
        fullOutputPath = self.output
        if self.project_data.has_key("path"): 
            targetPath = utils.resourceref.norm(self.project_data["path"])
            if targetPath and targetPath != "":
                fullOutputPath = os.path.join(fullOutputPath, targetPath)             
        
        fs = filestorage.FileStorage(fullOutputPath, "w")
        newProject = api.Project(fs)        
        for layer in self.layers:
            layer.generate(newProject, self.configuration.get_storage().get_path())        
        newProject.close()
        
        #Opening project again to validate the content and remove illegal includes.
        if self.project_data.has_key("validate") and self.project_data["validate"] != "false":            
            fs = filestorage.FileStorage(fullOutputPath, "w")
            validateProject = api.Project(fs)
            for conf in validateProject.list_configurations():
                validateProject.get_configuration(conf).list_all_configurations()
            validateProject.close()
        
        return 
    
    def generate_layers(self,layers):
        """
        Generate the given Configuration layers.
        """
        self.logger.info('Generating layers %s' % layers)
        self.generate()
        
        return 
    
    def has_ref(self,ref):
        """
        @returns True if the implementation uses the given ref as input value.
        Otherwise return False.
        """
        
        return None

#=================================================================
class ConvertProjectLayer(object):
    """
    Object presenting layer in convertprojectml file.
    """
    
    def __init__(self, path):
        if path != None:
            self.path = path
        else:
            self.path = ""
        self.folders = []
        self.files = []        

    def __str__(self):
        retStr = ""
        retStr += "\nPath: %s\n" % self.path
        retStr +="Folders:\n"        
        for folder in self.folders: 
            retStr += folder.__str__()
        retStr +="Files:\n"
        for file in self.files:
            retStr += file.__str__()    
        return retStr
    
    def generate(self, project, old_structure_root):
        """
        Function to handle generation to one folder.
        """
        
        #Create layer folder.
        project.get_storage().create_folder(utils.resourceref.norm(self.path))
        #print "Created Layer:", utils.resourceref.norm(self.path)
        
        for folder in self.folders:
            folder.generate(project, old_structure_root)
        
        for f in self.files:
            f.generate(project, old_structure_root)
        
        return
    
    def addFolder(self, folder):
        self.folders.append(folder)

    def addFile(self, file):
        self.files.append(file)

    def getProjectPath(self):
        return self.path

                
class ConvertProjectFolder(object):
    """
    Object presenting folder in convertprojectml file.
    """
        
    def __init__(self, path, parent=None):
        if path != None:
            self.path = path
        else:
            self.path = ""        
        self.filters = []
        self.parent = parent

    def __str__(self):
        retStr = ""
        retStr += "\tPath: %s\n" % self.path
        retStr +="\tFilters:\n"
        for filter in self.filters: 
            retStr += filter.__str__()
        return retStr 
    
    def generate(self, project, old_structure_root):
        
        #Adding new folder to project.
        project.get_storage().create_folder(utils.resourceref.norm(self.getProjectPath()))
        #print "Created folder:", utils.resourceref.norm(self.getProjectPath())
        
        for filter in self.filters:
            filter.generate(project, old_structure_root, "folder")
        return
    
    def addFilter(self, filter):
        self.filters.append(filter)

    def getProjectPath(self):
        return os.path.join(self.parent.getProjectPath(), self.path)
    
class ConvertProjectFile(object):
    """
    Object presenting file in convertprojectml file.
    """
        
    def __init__(self, path, type, parent=None):
        if path != None:
            self.path = path
        else:
            self.path = ""
        if type != None:
            self.type = type
        else:
            self.type = ""        
            
        self.filters = []
        self.parent = parent
        self.meta = []
        self.desc = ""
        
    def __str__(self):
        retStr = ""
        retStr += "\tPath: %s\n" % self.path
        retStr += "\tType: %s\n" % self.type
        retStr +="\tFilters:\n"
        for filter in self.filters:
            retStr += filter.__str__()
        return retStr             

    def generate(self, project, old_structure_root):
        for filter in self.filters:            
            filter.generate(project, old_structure_root, self.type)                        

        if self.type == "configuration_root":
            #Adding metadata                
            config = project.get_configuration(utils.resourceref.norm(self.path))
            if self.meta:                
                if not config.meta:
                    config.meta = []
                for meta in self.meta:
                    config.meta.add(meta[0], meta[1], meta[2], meta[3])                        
            if self.desc:
                config.desc = self.desc
                
            config.save()                    
        return

    def addFilter(self, filter):
        self.filters.append(filter)

    def addMeta(self, meta):
        self.meta = meta

    def addDescription(self, desc):
        self.desc = desc

    def getProjectPath(self):
        return os.path.join(self.parent.getProjectPath(), self.path)

class ConvertProjectFilter(object):
    """
    Object presenting filter in convertprojectml file.
    """
        
    def __init__(self, action, data, parent=None, remove_includes = "false", recursive = "false"):
        self.action = action
        self.data = data
        self.parent = parent
        if remove_includes:
            self.remove_includes = remove_includes
        else:
            self.remove_includes = "false"
        if recursive:
            self.recursive = recursive
        else:
             self.recursive = "false"

    def __str__(self):
        retStr = ""
        retStr += "\t\tAction: %s\n" % self.action
        retStr += "\t\tData: %s\n" % self.data
        return retStr    
        
    def generate(self, project, old_structure_root, type="none"):
        """
        @param project: New configuration project
        @type project:
        @param old_structure_root: Path to old projects root.
        @type old_structure_root:
        
        """
               
        if type == "" or type == "folder":
            self.handleAddRemove(project, old_structure_root)
        elif type == "layer_root":
            self.handleLayerRoot(project)
        elif type == "configuration_root":
            self.handleConfigurationRoot(project)
        else:
            #raise exceptions.NotSupportedException("Type: %s not supported as file type" % repr(type))
            pass            
        return

    def handleAddRemove(self, project, old_structure_root):
        """
        """
        
        pathPart, wildCardPart = self.separatePathAndWildcard(self.data)
        filesToProcess = []
        if wildCardPart == "":
            #No wildcards found.
            if self.recursive == "false":
                source = os.path.join(old_structure_root, pathPart)
                targetDir = self.resolveTargetDir(project, source)                
                filesToProcess.append({"source": source, "targetDir": targetDir})                
            else:
            #recursive search for directory entries.               
                directoryPath = os.path.join(old_structure_root, pathPart)
                if os.path.isdir(directoryPath):
                    for root, dirs, files in os.walk(directoryPath):
                        for f in files:
                            #Handling files.
                            source = os.path.join(root, f)
                            targetDir = self.resolveTargetDir(project, source)                
                            filesToProcess.append({"source": source, "targetDir": targetDir})
                        
                        for d in dirs:
                            #Handling directories to get empty folders included also.
                            source = os.path.join(root, d)
                            targetDir = self.resolveTargetDir(project, source)
                            filesToProcess.append({"source": source, "targetDir": targetDir})                            
                            
        else:
            #Need to handle wildcard part
            filesToProcess = self.getFilesByWildcard(os.path.join(old_structure_root, pathPart)\
                                                     ,wildCardPart, project)
                        
        for f in filesToProcess:
            source = f["source"]
            targetDir = f["targetDir"]
                      
            if source.lower().find(".svn") != -1:
            #Ignoring svn files
                continue
            
            if os.path.isfile(source):
                #targetDir = self.resolveTargetDir(project, f)                    
                if self.action == "add":
                    if not os.path.exists(targetDir):
                        os.makedirs(targetDir)
                    shutil.copy2(source, targetDir)                    
                elif self.action == "remove":
                    targetFile = os.path.join(targetDir, os.path.split(source)[1])
                    os.remove(targetFile)
            elif os.path.isdir(source):
                folderToCreate = os.path.join(targetDir, os.path.split(source)[1])
                if not os.path.isdir(folderToCreate):
                    os.makedirs(folderToCreate)

    def resolveTargetDir(self, project, filepath):
        """
        """
        if self.recursive == "false":
            return os.path.join(project.get_storage().get_path(), self.getProjectPath())
        else:            
            retPath = os.path.join(project.get_storage().get_path(), self.getProjectPath())            
            startFound = 0
            
            for item in os.path.normpath(filepath).split("\\"):
                if self.data.find(item) != -1:
                    startFound = 1
                if startFound and self.data.find(item) == -1:
                    retPath = os.path.join(retPath, item)                
            return os.path.split(retPath)[0]
                        

    def handleLayerRoot(self, project):
        """
        """
        
        pathPart, wildCardPart = self.separatePathAndWildcard(self.data) 
        filesToProcess = []
        
        if wildCardPart == "":
            #No wildcards found. Checking still if path has folder and file elements
            
            folderPath, filePart = os.path.split(pathPart)
            if folderPath == "":
                #filename only
                pathPart = ""
            else:
                #file and folder
                pathPart = folderPath
            
            source = os.path.join(project.get_storage().get_path(), self.getProjectPath(), pathPart, filePart)    
            filesToProcess.append({"source": source, "targetDir": None})
            
        else:
            #Need to handle wildcard part
            fullSearchPath = os.path.join(project.get_storage().get_path(), self.getProjectPath(), pathPart)
            filesToProcess = self.getFilesByWildcard(fullSearchPath, wildCardPart, project)
        
        #Creating rootfile.        
        rootFilePath = os.path.join(self.getProjectPath(), self.parent.path)        
        config = project.create_configuration(utils.resourceref.norm(rootFilePath))
        
        #Adding defined includes.
        for f in filesToProcess:
            source = f["source"]
            #Getting path in configuration project and adding it as include.
            filePath = utils.resourceref.norm(os.path.join(pathPart, os.path.split(source)[1]))
            config.include_configuration(filePath)
            if self.remove_includes == "true":
                self.removeIncludes(config.get_configuration(filePath))                        
        config.save()
    
    def removeIncludes(self, config):
        """
        @param config: Configuration object that is processed
        
        @return: None
        """

        #Getting all configurations from included configuration.
        configList = config.list_configurations()
        for item in configList:
            config.remove_configuration(utils.resourceref.norm(item))            
        
        config.save()
        

    def handleConfigurationRoot(self, project):
        """
        """        
        #Always in the root of the project
        configname = utils.resourceref.norm(self.parent.path)
        if configname in project.list_configurations():
            config = project.get_configuration(configname)
        else:
            config = project.create_configuration(utils.resourceref.norm(self.parent.path))
        config.include_configuration(utils.resourceref.norm(self.data))                
        config.save()


    def getProjectPath(self):
        if isinstance(self.parent, ConvertProjectFile):
            #print "FILE", self.parent.parent.getProjectPath()
            return self.parent.parent.getProjectPath() 
        else:
            #print "other"
            return self.parent.getProjectPath()
        

    def getFilesByWildcard(self, folder, wildcard, project):
        """
        @param folder: folder where matching is made
        @type folder: string
        @param wildcard: wildcard pattern
        @type wildcard: string   
        """
                
        #Array of files and folders matching with the wildcard.        
        retArray = []
        if os.path.isdir(folder):     
            for root, dirs, files in os.walk(folder):
                if self.recursive == "false" and os.path.normpath(root) != os.path.normpath(folder):
                #No recursive search used and therefore only topmost directory is handled.
                    continue
                else:
                    for f in files:
                        if fnmatch.fnmatch(os.path.join(root, f), wildcard):
                            source = os.path.join(root, f)
                            targetDir = self.resolveTargetDir(project, source)                
                            retArray.append({"source": source, "targetDir": targetDir})

                    for d in dirs:
                        if fnmatch.fnmatch(os.path.join(root, d), wildcard):
                            source = os.path.join(root, d)
                            targetDir = self.resolveTargetDir(project, source)                
                            retArray.append({"source": source, "targetDir": targetDir})                            
                            
        return retArray

    def separatePathAndWildcard(self, data):
        """        
        @param data: data from XML that may contain path and wildcard parts
        @type data: string
        
        @return: Path and wildcard parts separately. 
        """
        pathPart = ""
        wildCardPart = ""

        if data.find("*") == -1:
        #Only supported wildcard is currently *
            pathPart = data
            wildCardPart =""
        else:
        #Some wildcards found. Wildcards are supported only in the last segment.
            pathPart, wildCardPart = os.path.split(data)

        return pathPart, wildCardPart


#=================================================================
    
class ConvertProjectReader(plugin.ReaderBase):
    """
    Parses a single convertprojectml  file
    """ 
    
    NAMESPACE = 'http://www.s60.com/xml/convertprojectml/1'
    FILE_EXTENSIONS = ['convertprojectml']
    
    def __init__(self):
        self.desc = None
        self.output_dir = None
        self.input_dir = None
        self.namespaces = [self.NAMESPACE]
        self.project_data = {}
        self.layers = []
    
    @classmethod
    def read_impl(cls, resource_ref, configuration, etree):
        reader = ConvertProjectReader()
        reader.from_etree(etree, configuration.get_storage().get_path())
        
        impl = ConvertProjectImpl(resource_ref, configuration)
        impl.project_data   = reader.project_data
        impl.layers         = reader.layers
        return impl
    
    def from_etree(self, etree, old_structure_root = ""):
        self.project_data = self.parse_attributes(etree, "targetProject")        
        self.layers = self.parse_layers(etree) 
        for fe in self.parse_foreach(etree, old_structure_root):
            self.layers.append(fe)
        
        #for l in self.layers:
            #print l
        return    
    
    def parse_foreach(self, etree, old_structure_root):
        layersTmp = []
        for fe in etree.findall("{%s}foreach" % self.namespaces[0]):
            variable = fe.get("variable")
            data = fe.get("data")
            folders = [] 
            for item in os.listdir(os.path.join(old_structure_root, data)):
                if os.path.isdir(os.path.join(old_structure_root, data, item)) and item != '.svn':
                    folders.append(item)
            
            for folder in folders:
                mapping_data = {variable: folder}                                             
                for layer in fe.findall("{%s}layer" % self.namespaces[0]):            
                    layersTmp.append(self.parse_layer(layer, mapping_data))
                                
        return layersTmp
    
    def parse_layers(self,etree):
        layersTmp = []
        for layer in etree.findall("{%s}layer" % self.namespaces[0]):            
            layersTmp.append(self.parse_layer(layer))
            
        return layersTmp
    
    def parse_layer(self, etree, mapping_data=None):        
        path = self.handleMapping(etree.get("path"), mapping_data)
        
        layerObject = ConvertProjectLayer(path)        
        for folder in etree.findall("{%s}folder" % self.namespaces[0]):
            layerObject.addFolder(self.parse_folder(folder, layerObject, mapping_data))

        for f in etree.findall("{%s}file" % self.namespaces[0]):
            layerObject.addFile(self.parse_file(f, layerObject, mapping_data))
        
        return layerObject
    
    def parse_folder(self, etree, parent, mapping_data=None):        
        path = self.handleMapping(etree.get("path"), mapping_data)
        
        folderObject = ConvertProjectFolder(path, parent)
        for filter in etree.findall("{%s}filter" % self.namespaces[0]):                        
            #Remove includes supported only for files.
            folderObject.addFilter(self.parse_filter(filter, folderObject, mapping_data))                
        return folderObject

    def parse_file(self, etree, parent, mapping_data=None):
        path = self.handleMapping(etree.get("path"), mapping_data)
        type = self.handleMapping(etree.get("type"), mapping_data)
        
        fileObject = ConvertProjectFile(path, type, parent)        
        for filter in etree.findall("{%s}filter" % self.namespaces[0]):
            fileObject.addFilter(self.parse_filter(filter, fileObject, mapping_data))
        
        metaElement = etree.find("{%s}meta" % self.namespaces[0])
        namespacePattern = re.compile("\{(.*)\}(.*)")
        metaArray = [] #tag, value, ns, attrs
        if metaElement:
            for item in metaElement.getiterator():
                mo = namespacePattern.search(item.tag)
                if mo:        
                    if mo.group(2) != "meta":
                        tmpArray = []                        
                        tmpArray.append(mo.group(2))    #Tag name
                        tmpArray.append(item.text)      #value
                        tmpArray.append(mo.group(1))    #Namespace
                        tmpDict = {}
                        for attribute in item.keys():
                            tmpDict[attribute] = item.get(attribute)
                        tmpArray.append(tmpDict)
                        metaArray.append(tmpArray)
        
        descElement = etree.find("{%s}desc" % self.namespaces[0])
        description = ""
        if descElement != None:
            description = descElement.text                
                         
        fileObject.addMeta(metaArray)
        fileObject.addDescription(description)                
        return fileObject

    def parse_filter(self, etree, parent, mapping_data=None):
        """
        """
        data = self.handleMapping(etree.get("data"), mapping_data)
        action = self.handleMapping(etree.get("action"), mapping_data)
        remove_includes = self.handleMapping(etree.get("remove_includes"), mapping_data)
        recursive = self.handleMapping(etree.get("recursive"), mapping_data)
        
        return ConvertProjectFilter(action, data, parent, remove_includes, recursive)
    

    def parse_rule(self, etree, parent):
        return {"name": etree.get("name"), "type": etree.get("type"), "data": etree.get("data")}

    def parse_attributes(self, etree, tagName):
        tmpDict = {}        
        tmpElement = etree.find("{%s}%s" % (self.namespaces[0], tagName))
        for attribute in tmpElement.keys():
            tmpDict[attribute] = tmpElement.get(attribute)
        return tmpDict
    
    def handleMapping(self, data, mapping):
        """
        """
        
        retStr = data
        
        if mapping != None and data != None:                        
            for key in mapping.keys():
                retStr = retStr.replace(key, mapping[key])
        return retStr
        
        
        
        
        
        


    
    
    