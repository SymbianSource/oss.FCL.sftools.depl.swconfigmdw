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
import shutil

import zipfile,zlib, StringIO, os, logging
import datetime
import tempfile

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

from cone.public import api, utils, persistence, exceptions, parsecontext
from cone.public.api import Resource, Storage, Configuration, Folder
from cone.storage import metadata, common
from cone.confml import persistentconfml


class ZipException(exceptions.StorageException):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)  


class ZipStorage(common.StorageBase):
    """
    A storage for zip file 
    """
    def __init__(self, path, mode, **kwargs):
        """
        Open the given filename object as a cpf zipfile
        """
        self.mode        = mode
        self.persistentmodule = persistentconfml
        self.compression = zipfile.ZIP_DEFLATED
        self.modified = False
        self.logger = logging.getLogger('cone')
        self.logger.debug("ZipStorage path %s open in mode %s" % (path,self.mode))
        try:
            # If opening the file in read/append mode check that the given file is a zipfile
            if self.get_mode(mode) != self.MODE_WRITE:
                if os.path.exists(path) and not zipfile.is_zipfile(path):
                    raise ZipException("The file %s is not a zip file!" % path)
            # If creating a new file make sure that the path to the file exists
            elif self.get_mode(mode) in (self.MODE_APPEND, self.MODE_WRITE):
                dirname = os.path.dirname(path)
                if dirname != '' and not os.path.exists(dirname):
                    os.makedirs(dirname)
            self.zipfile = zipfile.ZipFile(path,self.mode,self.compression)
        except IOError,e:
            raise ZipException("ZipFile open error: %s" % e)
        super(ZipStorage, self).__init__(path, mode)

    def _zippath(self, path):
        """
        Convert a norm path to zipfile path  
        """
        normpath = utils.resourceref.norm(path)
        return normpath.lstrip('.')

    @classmethod
    def supported_storage(cls,path):
        """
        Class method for determing if the given clas supports a storage by given path. 
        E.g. foo.zip, foo.cpd, foo/bar, http://foo.com/
        @param path:
        @return: Boolean value. True if the storage of the path is supported. False if not.  
        """
        if utils.resourceref.get_ext(path) == "zip" or \
           utils.resourceref.get_ext(path) == "cpf":
            return True
        else:
            return False

    def open_resource(self,path,mode="r"):
        strio = None
        path = utils.resourceref.remove_begin_slash(path)
        fullpath = utils.resourceref.join_refs([self.get_current_path(),path])
        try:
            if self.get_mode(mode) == self.MODE_READ:
                if not self.is_resource(fullpath):
                    raise exceptions.NotResource("Resource is not found %s" % fullpath)
                bytes = self.zipfile.read(fullpath)
                strio = StringIO.StringIO(bytes)    
            elif self.get_mode(mode) == self.MODE_APPEND:
                if not self.is_resource(fullpath):
                    raise exceptions.NotResource("Resource is not found %s" % fullpath)
                bytes = self.zipfile.read(fullpath)
                # delete the "old" resource
                self.delete_resource(fullpath)
                strio = StringIO.StringIO(bytes)
                strio.seek(0, os.SEEK_END)
                
            elif self.get_mode(mode) == self.MODE_WRITE:
                if self.is_resource(fullpath):
                    # delete the "old" resource
                    self.delete_resource(fullpath)
                # Create a new string buffer because the resource is overwritten
                strio = StringIO.StringIO()
            else:
                raise ZipException("Unrecognized mode %s" % mode)
            res = ZipFileResource(self,fullpath,mode,strio)
            self.__opened__(res)
            return res
        except KeyError:
            raise exceptions.NotResource(path)

    def is_resource(self,path):
        path = utils.resourceref.remove_begin_slash(path)
        files = self.zipfile.namelist()
        try:
            i = files.index(path)
            return True
        except ValueError:
            return False

    def is_dir(self,path):
        """
        Get an array of files in a folder
        """
        try:
            zinfo = self.zipfile.getinfo(utils.resourceref.add_end_slash(path))
            return True
        except KeyError:
            return False 

    def list_resources(self, path, **kwargs): 
        """
        Get an array of files in a folder  
        """
        path = utils.resourceref.remove_begin_slash(path)
        fullpath = utils.resourceref.join_refs([self.get_current_path(),path])
        fullpath = self._zippath(fullpath)
        retarray = []
        filelist = self.zipfile.namelist()
        for name in filelist:
            (filepath,filename) = os.path.split(name)
            curname = utils.resourceref.replace_dir(name, self.get_current_path(),'')
            # return directories only if specified
            if kwargs.get('empty_folders', False) == True or not self.is_dir(name):
                # Skip the filename if it is marked as deleted
                if self.__has_open__(name) and self.__get_open__(name)[-1].get_mode() == api.Storage.MODE_DELETE:
                    continue
                if filepath == fullpath:
                    retarray.append(curname)
                elif kwargs.get('recurse', False) and filepath.startswith(fullpath):
                    retarray.append(curname)
        #retarray = sorted(utils.distinct_array(retarray))
        return retarray

    def import_resources(self,paths,storage,empty_folders=False):
        for path in paths:
            path = utils.resourceref.remove_begin_slash(utils.resourceref.norm(path))
            if not storage.is_resource(path) and empty_folders==False:
                logging.getLogger('cone').warning("The given path is not a Resource in the storage %s! Ignoring from export!" % path)
                continue
            if storage.is_resource(path):
                wres = self.open_resource(path,'wb')
                res  = storage.open_resource(path,"rb")
                wres.write(res.read())
                wres.close()
                res.close()
                
            elif storage.is_folder(path) and empty_folders:
                self.create_folder(path)

    def export_resources(self,paths,storage,empty_folders=False):
        
        for path in paths:
            if not self.is_resource(path) and empty_folders==False:
                logging.getLogger('cone').warning("The given path is not a Resource in this storage %s! Ignoring from export!" % path)
                continue
            if  self.is_resource(path):
                wres = storage.open_resource(path,'wb')
                res  = self.open_resource(path,"rb")
                wres.write(res.read())
                wres.close()
                res.close()
            
            if  self.is_folder(path) and  empty_folders:
                storage.create_folder(path)
                

    def close_resource(self, res):
        """
        Close the given resource instance. Normally this is called by the Resource object 
        in its own close.
        @param res: the resource object to close. 
        """
        try:
            self.__closed__(res)
            if self.get_mode(self.mode) != api.Storage.MODE_READ and \
               (res.get_mode() == api.Storage.MODE_WRITE or res.get_mode() == api.Storage.MODE_APPEND):
                self.zipfile.writestr(res.path,res.getvalue())
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
            self.zipfile.writestr(res.path,res.getvalue())

    def delete_resource(self,path):
        """
        Delete the given resource from storage
        @param res : Resource object to the resource 
        raises a NotSupportedException exception if delete operation is not supported by the storage
        """
        # First close all open resources
        for res in self.__get_open__(path):
            self.__closed__(res)
        self.modified = True 
        self.zipfile.filelist.remove(self.zipfile.NameToInfo[path])
        del self.zipfile.NameToInfo[path]
            

    def create_folder(self,path):
        """
        Create a folder entry to a path
        @param path : path to the folder
        """
        fullpath = utils.resourceref.join_refs([self.get_current_path(),path])
        fullpath = utils.resourceref.add_end_slash(self._zippath(fullpath))
        if self.is_folder(fullpath):
            # delete the "old" resource
            self.delete_resource(fullpath)
        now = datetime.datetime.now()
        zinfo = zipfile.ZipInfo(fullpath,
                                (now.year,now.month, now.day, 
                                 now.hour, now.minute, now.second)
                                )
        # set an external attribute for directory entry
        zinfo.external_attr = 0x10
        zinfo.extract_version = 10
        self.zipfile.writestr(zinfo,'') 

    def delete_folder(self,path):
        """
        Delete a folder entry from a path. The path must be empty.
        @param path : path to the folder
        """
        pass

    def is_folder(self,path):
        """
        Check if the given path is an existing folder in the storage
        @param path : path to the folder
        """
        fullpath = utils.resourceref.join_refs([self.get_current_path(),path])
        folderpath = self._zippath(fullpath)
        return self.is_dir(folderpath)

    def close(self):
        if self.zipfile:
            super(ZipStorage,self).close()
            self.zipfile.close()
            # Recreate the zip file if the zip has been modified to make a zip without 
            # duplicate local file entries
            if self.modified:
                oldfile = None
                newzipfile = None
                fh, tmp_path = tempfile.mkstemp(suffix='.zip')
                shutil.move(self.path, tmp_path)
                oldfile = zipfile.ZipFile(tmp_path,"r")
                newzipfile = zipfile.ZipFile(self.path,"w",self.compression)
                for fileinfo in oldfile.infolist():
                    newzipfile.writestr(fileinfo, oldfile.read(fileinfo.filename))
                if oldfile: oldfile.close()
                if newzipfile: newzipfile.close()
                os.close(fh)
                os.unlink(tmp_path)
            self.zipfile = None
        else:
            raise exceptions.StorageException('Storage %s has been already closed!' % self.path)

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
        if self.get_mode(self.mode) != api.Storage.MODE_READ:
            res = self.open_resource(path,"wb")
            data = "%s" % self.persistentmodule.dumps(object)
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
                obj.set_path(path)
                res.close()
                return obj
            except exceptions.ParseError,e:
                parsecontext.get_confml_context().handle_exception(e)
                #logging.getLogger('cone').error("Resource %s parsing failed with exception: %s" % (path,e))
                # returning an empty config in case of xml parsing failure.
                return api.Configuration(path)
        else:
            raise exceptions.NotResource("No such %s resource!" % path)


class ZipFileResource(Resource):
    def __init__(self,storage,path,mode,handle):
        Resource.__init__(self,storage,path,mode)
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

    def truncate(self,size=0):
        raise exceptions.NotSupportedException()

    def save(self):
        self.storage.save_resource(self)

    def close(self):
        self.storage.close_resource(self)
        self.handle.close()
    
    def get_size(self):
        if self.get_mode() == api.Storage.MODE_WRITE:
            raise exceptions.StorageException("Reading resource size attempted to %s in write-only mode." % self.path)
        return len(self.handle.getvalue())
    
    def getvalue(self):
        return self.handle.getvalue()

    def get_content_info(self):
        if self.content_info == None:
            self.content_info = api.make_content_info(self, self.handle.getvalue())
        
        return self.content_info