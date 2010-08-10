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
## 
# @author Teemu Rytkonen

import getpass
import StringIO
import os
import re
import copy
import logging
import httplib
import urllib, urllib2
import simplejson
import posixpath

from cone.public import *
from cone.carbon import persistentjson, model, resourcemapper
from cone.storage import authenticate

class WebStorage(api.Storage):
    """
    A general base class for all storage type classes
    @param path : the reference to the root of the storage.
    """
    
    def __init__(self, path, mode="a", **kwargs):
        api.Storage.__init__(self,path)
        self.mode = mode
        self.extapi = CarbonExtapi(path, **kwargs)
        self.persistentmodule = persistentjson
        
        # resource cache is a intermediate solution to create a mapping between carbon objects and Configuration project
        self._resource_cache = None
        

    def _create_resource(self, path, object):
        """
        Create a new resource (configuration|featurelist) to carbon storage.
        """
        # Test the path, whether it is a featurelist or configuration
        try:
            object_type = object.meta.get('type')
        except (TypeError,AttributeError):
            logging.getLogger('cone').info('Cannot dump configuration %s to webstorage without a type.' % path)
            return False
        carbonpath = resourcemapper.CarbonResourceMapper().map_confml_resource(object_type, path)
        if object_type == 'featurelist':
            # Create a featurelist 
            success = self.extapi.create_featurelist(carbonpath, object)
            if success:
                self.resource_cache.add_resource_link(path, carbonpath)
            return success
        else:
            # Create a configuration
            success = self.extapi.create_configuration(carbonpath, object)
            if success:
                self.resource_cache.add_resource_link(path, carbonpath)
            return success

    @classmethod
    def supported_storage(cls,path):
        """
        Class method for determing if the given clas supports a storage by given path. 
        E.g. http://foo.com/
        @param path:
        @return: Boolean value. True if the storage of the path is supported. False if not.  
        """
        if path.startswith('http://'):
            return True
        else:
            return False

    @property
    def resource_cache(self):
        """
        Returns a resource cache dictionary of all the resources inside the Carbon storage. Works as an intermediate 
        solution to link Configuration project concepts to Carbon storage
        
        """
        if not self._resource_cache: 
            self._resource_cache = ResourceCache()
            try:
                reslist = self.extapi.list_resources("/", True)
            except urllib2.HTTPError, e:
                print e
                return []
            # Append all resources to resource cache
            for res in reslist:
                self._resource_cache.add_resource(res)
#                    if isinstance(res, model.ConfigurationResource):
#                        self._resource_cache.add_configuration(res)
#                    elif isinstance(res, model.FeatureListResource):
#                        self._resource_cache.add_featurelist(res)
        return self._resource_cache

    def list_resources(self,path, **kwargs):
        """
        find the resources under certain path/path 
        @param path : reference to path where resources are searched
        @param recurse : defines whether to return resources directly under the path or does the listing recurse to subfolders. 
        Default value is False. Set to True to enable recursion.
        @param empty_folders: parameters that defined whether empty folders are included. This parameter is ignored 
        in WebStorage. 
        """
        return self.resource_cache.list_resources(path, kwargs.get('recurse', False))


    def open_resource(self,path,mode="r"):
        path = utils.resourceref.remove_begin_slash(path)
        if self.resource_cache.get_resource_object(path):
            return self.resource_cache.get_resource_object(path)
        elif self.resource_cache.get_resource_link(path):
            path = self.resource_cache.get_resource_link(path)
        
#        path = path.replace(".confml", ".configuration")
#        path = utils.resourceref.join_refs([self.get_current_path(), path])
        try:
            if self.get_mode(mode) == self.MODE_READ:
                strio = self.extapi._get_stringio_from_path(path)
            elif self.get_mode(mode) == self.MODE_APPEND:
                strio = self.extapi._get_stringio_from_path(path)
                strio.seek(0, os.SEEK_END)
            elif self.get_mode(mode) == self.MODE_WRITE:
                strio = StringIO.StringIO()
            else:
                raise StorageException("Unrecognized mode %s" % mode)
            res = WebResource(self,path,mode,strio)
            self.__opened__(res)
            return res
        except KeyError:
            raise exceptions.NotResource("The given resource is not found %s" % path)

    def is_resource(self,path):
        ret= self.resource_cache.is_resource(path)
        if not ret:
            try:
                mapped = self.resource_cache.get_mapped_resource(path)
                ret = self.extapi.is_resource(mapped)
            except Exception:
                pass
        return ret
#        path = path.replace(".confml", ".configuration")
#        path = utils.resourceref.join_refs([self.get_current_path(), path])
#        try:
#            query = urllib.quote(self._get_action_url('is_resource', path))
#            self.conn.request("GET", query)
#            resp = self.conn.getresponse()
#            reader = persistentjson.HasResourceReader()
#            return reader.loads(resp.read())
#        except exceptions.NotFound:
#            return False

    def save_resource(self, res):
        """
        Close resource is no-operation action with webstorage for now
        """
        return 

    def close_resource(self, path):
        """
        Close resource is no-operation action with webstorage
        """
        return 

    def export_resources(self, paths, storage, empty_folders=False):
        for path in paths:
            if not self.is_resource(path):
                logging.getLogger('cone').warning("The given path is not a Resource in this storage %s! Ignoring from export!" % path)
                continue
            wres = storage.open_resource(path,'wb')
            res  = self.open_resource(path,"rb")
            wres.write(res.read())
            wres.close()
            res.close()

    def unload(self, path, object):
        """
        Dump a given object to the storage (reference is fetched from the object)
        @param object: The object to dump to the storage, which is expected to be an instance 
        of Base class.
        """
        # Add the current path in front of the given path
        path = utils.resourceref.join_refs([self.get_current_path(), path])
        print "unload %s" % path
        if not isinstance(object, api.Configuration):
            raise exceptions.StorageException("Cannot dump object type %s" % object.__class__)
        # Skip the unload storing to storage if the storage is opened in read mode
        if self.get_mode(self.mode) != api.Storage.MODE_READ:
            if self.resource_cache.get_resource_link(path):
                path = self.resource_cache.get_resource_link(path)
            elif self.is_resource(path):
                 path = self.resource_cache.get_mapped_resource(path)
            else:
                """ otherwise create the new resource first before update"""
                if self._create_resource(path, object):
                    path = self.resource_cache.get_resource_link(path)
                else:
                    # Creation failed
                    logging.getLogger('cone').info('Creation of %s resource failed' % path)
                    return 
            data = persistentjson.dumps(object)
            self.extapi.update_resource(path, data)
        else:
            raise exceptions.StorageException("Cannot dump object to readonly storage")
        return
    
    

    def load(self, path):
        """
        Load resource from a path.
        """
        # Check if the object is already cached or has a cached link to another resource to load
        path = utils.resourceref.remove_begin_slash(path)
        print "load %s" % path
        if self.resource_cache.get_resource_link(path):
            path = self.resource_cache.get_resource_link(path)
        elif self.resource_cache.get_mapped_resource(path):
            path = self.resource_cache.get_mapped_resource(path)
        elif not utils.resourceref.get_ext(path) == "confml":
            raise exceptions.StorageException("Cannot load reference type %s" % utils.resourceref.get_ext(path))
        else:
            # Add the current path in front of the given path
            path = utils.resourceref.join_refs([self.get_current_path(), path])
            if not self.is_resource(path):
                raise exceptions.NotResource("No such %s resource!" % path)

        res = self.open_resource(path,"r")
        # read the resource with persistentmodule
        try:
            obj = self.persistentmodule.loads(res.read())
            #obj.set_path(path)
            res.close()
            return obj
        except exceptions.ParseError,e:
            logging.getLogger('cone').error("Resource %s parsing failed with exception: %s" % (path,e))
            # returning an empty config in case of xml parsing failure.
            return api.Configuration(path)

    def close(self):
        """ No operation in web storage close """
        pass


class WebResource(api.Resource):
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

    def truncate(self,size=0):
        raise exceptions.NotSupportedException()

    def flush(self):
        self.storage.flush_resource(self)

    def close(self):
        self.storage.close_resource(self)
        self.handle.close()
    
    def get_size(self):
        if self.get_mode() == api.Storage.MODE_WRITE:
            raise exceptions.StorageException("Reading resource size attempted to %s in write-only mode." % self.path)
        return len(self.handle.getvalue())
    
    def getvalue(self):
        return self.handle.getvalue()


class CarbonExtapi(object):
    ACTIONS = { 'open_resource' : 'get_resource',
                'list_resources' : 'list_resources',
                'is_resource' : 'has_resource',
                'put_resource' : 'put_resource',
                'update_resource' : 'update_resource'   }
    
    """
    A general container for Carbon extapi action
    """
    def __init__(self, path, **kwargs):
        self.path = path
        self.server_path = ''
        self.service_path = ''
        if path.startswith('http://'):
            path = path.replace('http://','',1)
        pathelems = path.split('/',1)
        self.server_path = pathelems[0]
        if len(pathelems) > 1: 
            self.service_path = pathelems[1]
        self._username = kwargs.get('username', None)
        self._password = kwargs.get('password', None)     
        authhandler = authenticate.CarbonAuthHandler()
        authhandler.add_username_func(self.get_username)
        authhandler.add_password_func(self.get_password)
        self.conn = urllib2.build_opener(urllib2.HTTPCookieProcessor, authhandler, urllib2.ProxyHandler({}))
        
    def get_username(self):
        if self._username == None:
            self._username = getpass.getuser()
        return self._username 

    def get_password(self):
        if self._password == None:
            self._password = getpass.getpass("Password (%s):" % self._username)
        return self._password

    def checklogin(self):
        """
        Checks that we are logged in by loading the main page.
        If we are not logged in it will redirect us to login page.
        """
        loginurl = "http://%(host)s/" % dict(host=self.server_path)
        loginreq = urllib2.Request(loginurl)
        print 'Checking login by opening URL %s ...' % loginurl
        try:
            resp = self.conn.open(loginreq)
        except urllib2.URLError, e:
            print str(e)
            return False
        return True
    
    def _get_stringio_from_path(self,path):
        """ 
        return a StringIO object containing the data under a given path.
        @return: StringIO buffer
        @raise exception.NotResource: if the resource under path is not found 
        """
        path = utils.resourceref.remove_begin_slash(path)
        action_url = self._get_action_url('open_resource', path)
        req = urllib2.Request(action_url)
        try:
            resp = self.conn.open(req)
            bytes = resp.read()
            strio = StringIO.StringIO(bytes)
            return strio
        except urllib2.HTTPError,e:
            raise exceptions.NotResource("The given path %s could not be retrived from this storage. Server returned status %s." % (path, e))

    def _get_action_url(self, action, path, **kwargs):
        path = utils.resourceref.remove_begin_slash(path)
        return "%s/%s/%s" % (self.path,self.ACTIONS[action], urllib.quote(path))
    
    def list_resources_for_type(self,path,type, recurse=False):
        """
        find the resources under certain path/path 
        @param path : reference to path where resources are searched
        @param type : resources for particular carbon specific type. 
        @param recurse : defines whether to return resources directly under the path or does the listing recurse to subfolders. 
        Default value is False. Set to True to enable recursion.
        """
        try:
            path = utils.resourceref.join_refs([path,'.'+type])
            path = utils.resourceref.remove_begin_slash(path)
            query = self._get_action_url('list_resources', path)
            req = urllib2.Request(query)
            resp = self.conn.open(req)
            if resp.code == httplib.OK:
                bytes = resp.read()
                reader = persistentjson.ResourceListReader()
                reslist = reader.loads(bytes)
                return reslist
            else:
                return []
        except exceptions.NotFound:
            return []

    def list_resources(self,path, recurse=False):
        """
        find the resources under certain path/path 
        @param path : reference to path where resources are searched
        @param recurse : defines whether to return resources directly under the path or does the listing recurse to subfolders. 
        Default value is False. Set to True to enable recursion.
        """
        try:
            path = utils.resourceref.remove_begin_slash(path)
            query = self._get_action_url('list_resources', path)
            req = urllib2.Request(query)
            resp = self.conn.open(req)
            if resp.code == httplib.OK:
                bytes = resp.read()
                if bytes:
                    reslist = simplejson.loads(bytes)
                    return reslist.get('resources',[])
            else:
                return []
        except exceptions.NotFound:
            return []

    def is_resource(self, path):
        try:
            query = self._get_action_url('is_resource', path)
            req = urllib2.Request(query)
            resp = self.conn.open(req)
            if resp.code == httplib.OK:
                reader = persistentjson.HasResourceReader()
                ret = resp.read()
                return reader.loads(ret)
            else:
                return False
        except exceptions.NotFound:
            return False

        
    def update_resource(self, path, data):
        """
        Update a resource to carbon. The resource can be a CarbonConfiguration or FeatureList object.
        @param object: The object which is dumped to dict with persistentjson and then updated to server. 
        """
        try:
            path = utils.resourceref.remove_begin_slash(path)
            query = self._get_action_url('update_resource', path)
            jsondata = simplejson.dumps(data)
            encdata = urllib.urlencode({'data' : jsondata})
            req = urllib2.Request(query, encdata)
            
            resp = self.conn.open(req)
            if resp.code == httplib.OK:
                bytes = resp.read()
                respdata = simplejson.loads(bytes)
                success = respdata.get('success') == True
                if success:
                    logging.getLogger('cone').info('Carbon update succeeds to path %s.' % (respdata.get('path')))
                else:
                    logging.getLogger('cone').error('Carbon update %s failed!' % (path))
                if respdata.get('errors'):
                    formatted_err = "" 
                    for error in respdata.get('errors'):
                        formatted_err += "%s: %s\n" % (error,respdata.get('errors')[error])
                    logging.getLogger('cone').info('Carbon update to path %s returned %s' % (respdata.get('path'),formatted_err))
                return success
            else:
                logging.getLogger('cone').error('Carbon update %s failed %s: %s' % (path,resp.code, resp))
                return False
        except urllib2.HTTPError,e:
            utils.log_exception(logging.getLogger('cone'), "HTTPError in %s, %s" % (query,e))
            return False

    def create_feature(self,path, feature, parent=None):
        """
        Create new Carbon feature based on Feature object.
        @param path: The path to the featurelist where the feature is created. 
        @param feature: The feature object 
        @param parent: A possible parent feature ref
        """
        try:
            path = utils.resourceref.remove_begin_slash(path)
            query = self._get_action_url('put_resource', path)
            data = persistentjson.dumps(feature)
            if parent:
                data['parent'] = parent
            jsondata = simplejson.dumps(data)
            encdata = urllib.urlencode({'data' : jsondata})
            req = urllib2.Request(query, encdata)
            
            resp = self.conn.open(req)
            if resp.code == httplib.OK:
                bytes = resp.read()
                respdata = simplejson.loads(bytes)
                success = respdata.get('success') == True
                if success:
                    logging.getLogger('cone').info('New Carbon feature created to path %s.' % (respdata.get('path')))
                else:
                    logging.getLogger('cone').error('Feature %s creation failed %s' % (feature.fqr,respdata.get('errors')))
                return success
            else:
                logging.getLogger('cone').error('Feature %s creation failed %s: %s' % (feature.fqr,resp.code, resp))
                return False
        except urllib2.HTTPError,e:
            utils.log_exception(logging.getLogger('cone'), "HTTPError in %s, %s" % (query,e))
            return False

    def create_featurelist(self, path, featurelist):
        """
        Create new Carbon featurelist to carbon.
        @param featurelist: The FeatureList object which is created. 
        @return: tuple (success, created_path) where success indicates the success of the operation
        and created_path is the newly created featurelist path on success.
        """
        try:
            path = utils.resourceref.remove_begin_slash(path)
            query = self._get_action_url('put_resource', path)
            data = persistentjson.FeatureListCreateWriter().dumps(featurelist)
            jsondata = simplejson.dumps(data)
            encdata = urllib.urlencode({'data' : jsondata})
            req = urllib2.Request(query, encdata)
            
            resp = self.conn.open(req)
            if resp.code == httplib.OK:
                bytes = resp.read()
                respdata = simplejson.loads(bytes)
                success = respdata.get('success') == True
                newpath = respdata.get('path')
                if success:
                    logging.getLogger('cone').info('New Carbon featurelist created to path %s.' % (newpath))
                else:
                    logging.getLogger('cone').error('FeatureList %s creation failed %s' % (featurelist.path,respdata.get('errors')))
                return (success, newpath)
            else:
                logging.getLogger('cone').error('FeatureList %s creation failed %s: %s' % (featurelist.path,resp.code, resp))
                return (False,'')
        except urllib2.HTTPError,e:
            utils.log_exception(logging.getLogger('cone'), "HTTPError in %s, %s" % (query,e))
            return (False,'')

    def create_configuration(self, path, configuration):
        """
        Create new Carbon configuration to carbon.
        @param path: The path to the configuration 
        @param configuration: The CarbonConfiguration object
        @return: tuple (success, created_path) where success indicates the success of the operation
        and created_path is the newly created configuration path on success.
        """
        try:
            path = utils.resourceref.remove_begin_slash(path)
            query = self._get_action_url('put_resource', path)
            data = persistentjson.ConfigurationCreateWriter().dumps(configuration)
            jsondata = simplejson.dumps(data)
            encdata = urllib.urlencode({'data' : jsondata})
            req = urllib2.Request(query, encdata)
            
            resp = self.conn.open(req)
            if resp.code == httplib.OK:
                bytes = resp.read()
                respdata = simplejson.loads(bytes)
                success = respdata.get('success') == True
                newpath = respdata.get('path')
                if success:
                    logging.getLogger('cone').info('New Carbon configuration created to path %s.' % (newpath))
                else:
                    logging.getLogger('cone').error('CarbonConfiguration %s creation failed %s' % (configuration.path,respdata.get('errors')))
                return (success, newpath)
            else:
                logging.getLogger('cone').error('CarbonConfiguration %s creation failed %s: %s' % (configuration.path,resp.code, resp))
                return (False,'')
        except urllib2.HTTPError,e:
            utils.log_exception(logging.getLogger('cone'), "HTTPError in %s, %s" % (query,e))
            return (False,'')

class ResourceCache(object):
    """
    Resource cache maintains a list of ConE resource names and their actual links to Carbon resources.
    """
    def __init__(self):
        self._cache = {}

    def add_configuration(self, configuration):
        """
        Add a list of Carbon configurations. 
        """
        
        # Create the configuration as a layer and configuration root
        self._cache[configuration.get_path()] = configuration.path
        rootconf_path = configuration.name+'.confml'
        rootconf = model.CarbonConfiguration(rootconf_path)
        rootconf.include_configuration(configuration.get_path())
        self._cache[rootconf_path] = rootconf

    def add_featurelist(self, featurelist):
        """
        Add a list of Carbon configurations. 
        """
        # Add the feature list under feature list folder 
        self._cache["featurelists/"+featurelist.get_path()] = featurelist.get_carbon_path()
        pass

    def add_resource(self, resourcepath):
        """
        Add a resource 
        """
        confmlpath = resourcemapper.CarbonResourceMapper().map_carbon_resource(resourcepath)
        self._cache[confmlpath] = resourcepath 

    def list_resources(self, path, recurse=False):
        """
        List ConE resources under certain path 
        """
        resources = []
        path = utils.resourceref.insert_begin_slash(path)
        for res in self._cache.keys():
            (respath,resname) = posixpath.split(res)
            respath = utils.resourceref.insert_begin_slash(respath)
            if recurse:
                if posixpath.normpath(respath).startswith(posixpath.normpath(path)):
                     resources.append(res)
            else:
                if posixpath.normpath(respath) == posixpath.normpath(path):
                     resources.append(res)
        return resources

    def is_resource(self,path):
        return self._cache.has_key(path)

    def get_resource_link(self,path):
        """
        Get a the actual Carbon resource link if it is found from cached storage. 
        """
        linkpath = self._cache.get(path, None)
        if isinstance(linkpath, str):
             return linkpath
        else:
            return None

    def get_mapped_resource(self, path):
        # Try to make a carbon like resource path for a confml resource
        if path.startswith('featurelists'):
            object_type = 'featurelist'
        elif path.endswith('/root.confml'):
            object_type = 'configurationlayer'
        else:
            object_type = 'configurationroot'
        carbonpath = resourcemapper.CarbonResourceMapper().map_confml_resource(object_type, path)
        return carbonpath

    def add_resource_link(self,link, path):
        """
        Add a actual Carbon resource link. The link is the key which returns path when asked from get_resource_link.
        @param link: is linking path to the actual carbon resource path
        @param path: is the actual carbon path  
        """
        self._cache[link] = path

    def get_resource_object(self,path):
        """
        Get a the actual cached Carbon object if it is found. 
        """
        cachebj = self._cache.get(path, None)
        if isinstance(cachebj, model.CarbonConfiguration):
             return cachebj
        return None

