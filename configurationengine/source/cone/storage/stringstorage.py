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

import StringIO
import os
import pickle
import copy
import logging

from cone.public import *
from cone.storage import persistentdictionary


class _StringStorageObject(container.ObjectContainer):
    def __init__(self, name):
        container.ObjectContainer.__init__(self, utils.resourceref.to_dottedref(name))
        self.path = name
        self.data = ""

    def get_path(self):
        """
        Return the path of the configuration resource
        """
        return self.path

    def set_path(self,path):
        """
        Set the path of the configuration resource
        """
        self.path = path

    def path_to_elem(self, toparent=None):
        parent_path = ""
        # check if the parent is found at all from this hierarchy
        if toparent and not self._find_parent_or_default(match=toparent):
            toparent = self._find_parent_or_default(container=True)
        if self._find_parent():
            parent_path = self._find_parent()._path(toparent).replace(".","/") 
        return utils.resourceref.join_refs([parent_path,self.get_path()])
    
    def __getstate__(self):
        return self.__dict__.copy()
        
    def __setstate__(self,dict):
        self.__dict__ =  dict.copy()
        
class StringStorage(api.Storage, container.ObjectContainer):
    """
    A general base class for all storage type classes
    @param path : the reference to the root of the storage.
    """
    def __init__(self, path):
        container.ObjectContainer.__init__(self,"")
        api.Storage.__init__(self,path)

    def __getstate__(self):
        dict = self.__dict__.copy()
        del dict['__opened_res__']
        return dict

    def __setstate__(self,dict):
        self.__dict__ =  dict.copy()
        self.__dict__['__opened_res__'] = {}

    def __dump__(self):
        """
        Dump the storage to the reference file
        """
        file = open(self.get_path(),"w")
        pickle.dump(self,file)
        file.close()

    @classmethod
    def __open__(cls,path, mode="r"):
        if mode.find("a")!=-1 or mode.find("r")!=-1:
            if os.path.exists(path) and os.path.isfile(path):
                file = open(path,"r")
                obj = pickle.load(file)
                file.close()
            else:
                raise exceptions.StorageException("The given data file for storage does not exist! %s" % path)
        elif mode.find("w")!=-1:
            # check if the given storage path exists and delete it if it does
            if os.path.dirname(path) != '' and not os.path.exists(os.path.dirname(path)):
                 os.makedirs(os.path.dirname(path))
            obj = StringStorage(path)
            """ key value pairs of data. Key path = datastring """ 
        else:
            raise exceptions.StorageException("Unsupported creation mode given! %s" % mode)
        return obj

    @classmethod
    def supported_storage(cls,path):
        """
        Class method for determing if the given clas supports a storage by given path. 
        E.g. foo.zip, foo.cpd, foo/bar, http://foo.com/
        @param path:
        @return: Boolean value. True if the storage of the path is supported. False if not.  
        """
        if utils.resourceref.get_ext(path) == "pk":
            return True
        else:
            return False

    def close(self):
        """
        Close the repository, which will save and close all open resources.  
        """
        super(StringStorage,self).close()
        self.__dump__()

    def save(self):
        """
        Save changes from all resources to the repository.  
        """        
        super(StringStorage,self).save()
        self.__dump__()

    def open_resource(self,path,mode="r"):
        """
        Open the given resource and return a File object.
        @param path : reference to the resource 
        @param mode : the mode in which to open. Can be one of r = read, w = write, a = append.
        raises a NotResource exception if the path item is not a resource.
        """
        res = None
        # Add the current path in front of the given path
        path = utils.resourceref.join_refs([self.get_current_path(), path])
        dottedref = utils.resourceref.to_dref(path)
        (pathto,name)= utils.resourceref.psplit_ref(path)
        (dpath, dref) = utils.dottedref.psplit_ref(dottedref)
        
        # check for existence
        if self.get_mode(mode) == self.MODE_READ:
            try:
                # Try to create a new StringResource in any case
                
                res = StringResource(self, path, self._get(dottedref).data,mode) 
            except exceptions.NotFound,e:
                raise exceptions.NotResource("Not found %s" % path)
        elif self.get_mode(mode) == self.MODE_WRITE:
            # Create a new StringResource in any case
            self._add_to_path(dpath,_StringStorageObject(name))
            res = StringResource(self, path, self._get(dottedref).data,mode) 
        elif self.get_mode(mode) == self.MODE_APPEND:
            # Append case, create the data reference if it is not existing
            if not self._has(dottedref):
                self._add_to_path(dpath,_StringStorageObject(name))
                        # Create a new StringResource in any case
            res = StringResource(self, path, self._get(dottedref).data,mode)
            res.seek(0, os.SEEK_END)
        self.__opened__(res)
        return res

    def delete_resource(self,path):
        """
        Delete the given resource from storage
        @param res : Resource objcet to the resource 
        raises a NotSupportedException exception if delete operation is not supported by the storage
        """
        # First close all open resources
        # Add the current path in front of the given path
        path = utils.resourceref.join_refs([self.curpath, path])
        for res in self.__get_open__(path):
            self.__closed__(res)
        self._remove(utils.resourceref.to_dref(path))

    def close_resource(self, res):
        """
        Close the given resource instance. Normally this is called by the Resource object 
        in its own close.
        @param res: the resource object to close. 
        """
        try:
            self.__closed__(res)
            if not res.get_mode() == api.Storage.MODE_READ:
                self._get(utils.resourceref.to_dref(res.path)).data = res.getvalue()
        except KeyError,e:
            raise StorageException("No such %s open resource! %s" % (res.path,e))
            

    def save_resource(self, res):
        """
        Flush the changes of a given resource instance. Normally this is called by the Resource object 
        in its own save.
        @param res: the resource to the resource to save. 
        """
        if not self.__has_resource__(res):
            raise exceptions.NotResource("No such %s open resource!" % res.path)
        else:
            if not res.get_mode() == api.Storage.MODE_READ:
                self._get(utils.resourceref.to_dref(res.path)).data = res.getvalue()

    def is_resource(self,path):
        """
        Return true if the path is a resource
        @param path : reference to path where resources are searched
        """
        # Add the current path in front of the given path
        path = utils.resourceref.join_refs([self.get_current_path(), path])
        return self._has(utils.resourceref.to_dref(path))

    def list_resources(self,path,recurse=False,empty_folders=False):
        """
        find the resources under certain path/path 
        @param path : reference to path where resources are searched
        @param recurse : defines whether to return resources directly under the path or does the listing recurse to subfolders. 
        Default value is False. Set to True to enable recursion.
        """
        """ Get the given curpath element """
        try:
            curelem = self._get(utils.resourceref.to_dref(self.get_current_path()))
            dref = utils.resourceref.to_dref(path)
            if recurse:
                return sorted([child.path_to_elem(curelem) for child in curelem._get(dref)._traverse(type=_StringStorageObject)])
            else:
                return sorted([child.path_to_elem(curelem) for child in curelem._get(dref)._objects(type=_StringStorageObject)])
        except exceptions.NotFound:
            return []
        
    def import_resources(self,paths,storage,empty_folders=False):
        for path in paths:
            if not storage.is_resource(path):
                logging.getLogger('cone').warning("The given path is not a Resource in the storage %s! Ignoring from export!" % path)
                continue
            wres = self.open_resource(path,'wb')
            res  = storage.open_resource(path,"rb")
            wres.write(res.read())
            wres.close()
            res.close()
            

    def create_folder(self,path):
        """
        Create a folder entry to a path
        @param path : path to the folder
        """
        if not self._has(utils.resourceref.to_dref(path)):
            (dpath,name) = utils.dottedref.psplit_ref(utils.resourceref.to_dref(path))
            self._add_to_path(dpath, self._default_object(name))

    def delete_folder(self,path):
        """
        Delete a folder entry from a path. The path must be empty.
        @param path : path to the folder
        """
        self._remove(utils.resourceref.to_dref(path))

    def is_folder(self,path):
        """
        Check if the given path is an existing folder in the storage
        @param path : path to the folder
        """
        return self._has(utils.resourceref.to_dref(path))

    def export_resources(self,refs,storage,empty_folders=False):
        """
        export resources from this storage based on a list of reference to this storage
        @param refs : a list of resource names in this storage (references).
        @param storage : the external storage where to export.
        """  
        storage.import_resources(refs, self, empty_folders=empty_folders)

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
        res = self.open_resource(path,"w")
        data = persistentdictionary.dumps(object)
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
            raise exceptions.StorageException("Cannot load object from given path = %s!" % path)
        if self.is_resource(path):
            res = self.open_resource(path,"r")
            # read the dictionary from the resource with eval
            obj = persistentdictionary.loads(res.read())
            res.close()
            return obj
        else:
            raise exceptions.NotResource("No such %s resource!" % path)

class StringResource(api.Resource):
    """
    A StringResource class that works on top of StringIO buffer. This class in 
    intended mainly for testing purposes.
    """    
    def __init__(self,storage,path,stringdata, mode=api.Storage.MODE_READ):
        strio = StringIO.StringIO(stringdata)    
        api.Resource.__init__(self,storage,path, mode)
        self.handle = strio
        self.read = self.handle.read
        self.tell = self.handle.tell
        self.seek = self.handle.seek
        self.readline = self.handle.readline
        self.getvalue = self.handle.getvalue
    
    def write(self, string):
        if self.get_mode() == api.Storage.MODE_READ:
            raise exceptions.StorageException("Writing attempted to %s in read-only mode." % self.path)
        else:
            self.handle.write(string)

    def read(self, bytes=0):
        if self.get_mode() == api.Storage.MODE_WRITE:
            raise exceptions.StorageException("Reading attempted to %s in write-only mode." % self.path)
        else:
            self.handle.read(string)

    def save(self):
        self.storage.save_resource(self)

    def close(self):
        self.storage.close_resource(self)
        self.handle.close()
    
    def get_size(self):
        if self.get_mode() == api.Storage.MODE_WRITE:
            raise exceptions.StorageException("Reading resource size attempted to %s in write-only mode." % self.path)
        return len(self.handle.getvalue())

    def get_content_info(self):
        if self.content_info == None:
            self.content_info = utils.make_content_info(self, self.handle.getvalue())
        
        return self.content_info
