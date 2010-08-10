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

import os
import re
import logging
import xml.parsers.expat
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
            
from cone.public import exceptions  
from cone.public import api, utils, parsecontext
#from cone.storage.configurationpersistence import ConfigurationReader, ConfigurationWriter
from cone.storage import metadata, common, zipstorage
from cone.confml import persistentconfml
debug = 0

class FileStorage(common.StorageBase):
    """
    A file system based implementation for Storage.
    @param path : path to the storage folder
    @param mode: the mode for the folder. Default is a=append that expects the folder to exist.
    """
    
    def __init__(self, path, mode="r", **kwargs):
        super(FileStorage, self).__init__(path, mode)
        logging.getLogger('cone').debug("FileStorage path %s" % self.get_path())
        self.persistentmodule = persistentconfml
        if mode.find("a")!=-1 or mode.find("r")!=-1:
            # check that the given folder exists and is a folder    
            if not os.path.isdir(self.get_path()):
                raise exceptions.StorageException("The given data folder for storage does not exist! %s" % self.get_path())
        elif mode.find("w")!=-1:
            # check if the given folder exists and create it if it does not
            if not os.path.exists(os.path.abspath(self.get_path())):
                os.makedirs(self.get_path())
        else:
            raise exceptions.StorageException("Unsupported creation mode given! %s" % mode)
        
        

    @classmethod
    def supported_storage(cls,path):
        """
        Class method for determing if the given clas supports a storage by given path. 
        E.g. foo.zip, foo.cpd, foo/bar, http://foo.com/
        @param path:
        @return: Boolean value. True if the storage of the path is supported. False if not.  
        """
        if path.startswith('http://'):
            return False
        path = os.path.abspath(path)
        (name,ext) = os.path.splitext(path)
        if path != "" and ext == "":
            return True
        elif os.path.isdir(path):
            return True
        else:
            return False

    def open_resource(self,path,mode="r"):
        # make sure that path exists if we are creating a file
        path = utils.resourceref.remove_end_slash(path)
        path = utils.resourceref.remove_begin_slash(path)
        path = utils.resourceref.join_refs([self.get_current_path(), path])
        fullpath = utils.resourceref.join_refs([self.get_path(),path])
        if mode.find("w") != -1:
            dirpath = os.path.dirname(fullpath)
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
        try:
            res = FileResource(self,path,mode,open(fullpath,mode)) 
            self.__opened__(res)
            return res
        except IOError,e:
            raise exceptions.NotResource("%s, %s" % (path,e) )

    def delete_resource(self,path):
        if self.is_resource(path):
            try:
                path = utils.resourceref.remove_begin_slash(path)
                path = utils.resourceref.join_refs([self.get_path(),self.get_current_path(),path])
                for res in self.__get_open__(path):
                    res.close()
                    self.__closed__(res)
                os.unlink(path)
            except IOError:
                raise exceptions.NotResource(path)
        else:
            raise exceptions.NotResource(path)

    def close_resource(self, res):
        """
        Close the given resource instance. Normally this is called by the Resource object 
        in its own close.
        @param res: the resource object to close. 
        """
        try:
            self.__closed__(res)
            #if not res.get_mode() == api.Storage.MODE_READ:
            #    self._get(utils.resourceref.to_dref(res.path)).data = res.getvalue()
        except KeyError,e:
            raise exceptions.StorageException("No such %s open resource! %s" % (res.path,e))
            

    def save_resource(self, res):
        """
        Flush the changes of a given resource instance. Normally this is called by the Resource object 
        in its own save.
        @param res: the resource to the resource to save. 
        """
        if not self.__has_resource__(res):
            raise exceptions.NotResource("No such %s open resource!" % res.path)
        else:
            res.save()

    def is_resource(self,path):
        path = utils.resourceref.remove_begin_slash(path)
        path = utils.resourceref.join_refs([self.get_current_path(), path])
        path = utils.resourceref.join_refs([self.get_path(),path])
        norm_path = os.path.normpath(path)
        return os.path.isfile(norm_path)

    def fix_entry(self,entry,current_root):
        entry = entry.replace(current_root,'')
        entry = entry.replace("\\","/")
        entry = utils.resourceref.remove_begin_slash(entry)
        return entry


    def list_resources(self, path, **kwargs):
        """
        Get an array of files in a folder
        """
        
        retarray = []
        path = utils.resourceref.remove_begin_slash(path)
        fullpath = utils.resourceref.join_refs([self.get_path(),self.get_current_path(),path])
        joined = os.path.join(self.get_path(), self.get_current_path())
        current_root = os.path.normpath(os.path.abspath(joined))
        # return always unix type file paths
        if kwargs.get('recurse', False):    
            # Walk through all files in the layer
            for root, dirs, files in os.walk(fullpath):
                # ensure that the directories and files are returned
                # with alphabetical sorting in all platforms (e.g linux)
                dirs.sort()
                files.sort()
                for name in files:
                    entry = os.path.join(root, name)
                    entry = os.path.normpath(os.path.abspath(entry))
                    if os.path.isfile(entry):
                        retarray.append(self.fix_entry(entry,current_root))
                        
                if kwargs.get('empty_folders', False): 
                    for name in dirs:
                        entry = os.path.join(root, name)
                        entry = os.path.normpath(os.path.abspath(entry))
                        if  os.path.isdir(entry)  and  len(os.listdir(entry)) ==0:
                            retarray.append(self.fix_entry(entry,current_root))
                        
        else:
            filelist = sorted(os.listdir(fullpath))
            for name in filelist:
                entry = os.path.join(path, name)
                entry = os.path.normpath(entry)
                entry = entry.replace("\\","/")               
                entry = utils.resourceref.remove_begin_slash(entry)
                # ignore non file entries
                fileentry = os.path.join(current_root,entry)
                if os.path.isfile(fileentry):
                    if debug: print "list_resources adding %s" % entry
                    retarray.append(entry)
                    
                if os.path.isdir(fileentry) and kwargs.get('empty_folders', False):
                    if debug: print "list_resources adding %s" % entry
                    retarray.append(entry)
        return retarray

    def import_resources(self,paths,storage):
        for path in paths:
            if not storage.is_resource(path):
                logging.getLogger('cone').warning("The given path is not a Resource in the storage %s! Ignoring from export!" % path)
                continue
            wres = self.open_resource(path,'wb')
            res  = storage.open_resource(path,"rb")
            wres.write(res.read())
            wres.close()
            res.close()
    
    def export_resources(self,paths,storage,empty_folders=False):
        """
        
        
        """
        for path in paths:
            if not self.is_resource(path) and empty_folders==False:
                logging.getLogger('cone').warning("The given path is not a Resource in this storage %s! Ignoring from export!" % path)
                continue
            if self.is_resource(path):
                # Optimization for direct file to ZIP export.
                # There's no need to juggle the data through ConE code
                # when we can just write the file directly into the ZIP
                if isinstance(storage, zipstorage.ZipStorage):
                    source_abspath = os.path.join(self.rootpath, path)
                    logging.getLogger("cone").debug("Exporting directly from file to ZIP: %r -> %r" % (source_abspath, path))
                    storage.zipfile.write(source_abspath, path)
                else:
                    wres = storage.open_resource(path,'wb')
                    res  = self.open_resource(path,"rb")
                    wres.write(res.read())
                    wres.close()
                    res.close()
                
                
            if  self.is_folder(path) and  empty_folders:
                storage.create_folder(path)
    
                
                

    def create_folder(self,path):
        """
        Create a folder entry to a path
        @param path : path to the folder
        """
        path = utils.resourceref.remove_begin_slash(path)
        path = utils.resourceref.join_refs([self.get_path(), self.get_current_path(), path])
        if not os.path.exists(path):
            os.makedirs(path)

    def delete_folder(self,path):
        """
        Delete a folder entry from a path. The path must be empty.
        @param path : path to the folder
        """
        path = utils.resourceref.join_refs([self.get_path(), self.get_current_path(), path])
        if os.path.isdir(path):
            os.rmdir(path)
        else:
            raise exceptions.StorageException("Not a folder %s" % path)

    def is_folder(self,path):
        """
        Check if the given path is an existing folder in the storage
        @param path : path to the folder
        """
        path = utils.resourceref.join_refs([self.get_path(), self.get_current_path(), path])
        return os.path.isdir(path)

    def unload(self, path, object):
        """
        Dump a given object to the storage (reference is fetched from the object)
        @param object: The object to dump to the storage, which is expected to be an instance 
        of Base class.
        """
        # Add the current path in front of the given path
        path = utils.resourceref.join_refs([self.get_current_path(), path])
        if not isinstance(object, api.Configuration):
            raise exceptions.StorageException("Cannot dump object type %s" % object.__class__)
        # Skip the unload storing to storage if the storage is opened in read mode
        if self.get_mode(self.mode) != api.Storage.MODE_READ:
            res = self.open_resource(path,"wb")
            data = self.persistentmodule.dumps(object)
            res.write(data)
            res.close()
        return


    def load(self, path):
        """
        Load an from a reference.
        """
        # Add the current path in front of the given path
        path = utils.resourceref.join_refs([self.get_current_path(), path])
        if not utils.resourceref.get_ext(path) == "confml":
            raise exceptions.StorageException("Cannot load reference type %s" % utils.resourceref.get_ext(path))
        if self.is_resource(path):
            res = self.open_resource(path,"r")
            # read the resource with persistentmodule
            parsecontext.get_confml_context().current_file = path
            try:
                obj = self.persistentmodule.loads(res.read())
                #obj.set_path(path)
                res.close()
                return obj
            except exceptions.ParseError,e:
                parsecontext.get_confml_context().handle_exception(e)
                #logging.getLogger('cone').error("Resource %s parsing failed with exception: %s" % (path,e))
                # returning an empty config in case of xml parsing failure.
                return api.Configuration(path)
        else:
            raise exceptions.NotResource("No such %s resource!" % path)


class FileResource(api.Resource):
    def __init__(self,storage,path,mode,handle):
        api.Resource.__init__(self,storage,path,mode)
        self.handle = handle
        
    def read(self,bytes=0):
        if bytes == 0:
            return self.handle.read()
        else:
            return self.handle.read(bytes)
    
    def write(self,string):
        if self.get_mode() == api.Storage.MODE_READ:
            raise exceptions.StorageException("Writing attempted to %s in read-only mode." % self.path)
        else:
            self.handle.write(string)

    def truncate(self, size=0):
        self.handle.truncate(0)
        self.handle.seek(size, 0)

    def save(self):
        if not self.handle.closed:
            self.handle.save()

    def close(self):
        self.storage.close_resource(self)
        self.handle.close()
    
    def get_size(self):
        if self.get_mode() == api.Storage.MODE_WRITE:
            raise exceptions.StorageException("Reading size attempted to %s in write-only mode." % self.path)
        orig_pos = self.handle.tell()
        self.handle.seek(0, os.SEEK_END)
        try:        return self.handle.tell()
        finally:    self.handle.seek(orig_pos, os.SEEK_SET)
    
    def get_content_info(self):
        orig_pos = self.handle.tell()
        self.handle.seek(0, os.SEEK_SET)
        data = self.handle.read()
        self.handle.seek(orig_pos, os.SEEK_SET)
        if self.content_info == None:
            self.content_info = api.make_content_info(self, data)
        
        return self.content_info
