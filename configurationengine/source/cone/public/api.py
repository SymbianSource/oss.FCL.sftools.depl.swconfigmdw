from __future__ import with_statement
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
"""
Cone public API.
The core interface to the ConE functionality.
"""

import re
import sys
import logging
import mimetypes

from cone.public import exceptions, utils, container, mapping

def get_file_logger():
    return logger

class Base(container.ObjectContainer):
    """
    The Base class is intended for capturing same kind of naming scheme.
    """
    
    
    def __init__(self, ref="", **kwargs):
        if len(utils.dottedref.split_ref(ref)) > 1:
            raise exceptions.InvalidRef("Invalid reference for Base object %s!" % ref)
        self.ref = ref
        container.ObjectContainer.__init__(self, ref)
        try:
            for arg in kwargs.keys():
                if kwargs.get(arg) != None:
                    setattr(self, arg, kwargs.get(arg))
        except AttributeError,e:
            raise e
        
    def __repr__(self):
        dict = self._dict()
        return "%s(%s)" % (self.__class__.__name__, dict)

#    def __reduce_ex__(self, protocol_version):
#        tpl = super(Base, self).__reduce_ex__(protocol_version)
#        return tpl

#    def __getstate__(self):
#        state = self._dict(internals=True, ignore_empty=True)
#        # pop out the _name so that it wont appear as redundant data (ref is the same)
#        state.pop('_name', None)
#        state.pop('_parent', None)
#        return state
#
#    def __setstate__(self, state):
#        super(Base, self).__setstate__(state)
#        self.ref = state.get('ref','')
#        for arg in state.keys():
#            self.__dict__.setdefault(arg, state.get(arg))
        
    def _get_mapper(self,modelname):
        """
        Return a instance of appropriate mapper for given model.
        """
        return mapping.BaseMapper()

    def _compare(self, other, dict_keys=None):
        """ 
        Compare the attributes of elements 
        """
        if isinstance(other, Base):
            keys = dict_keys or self._dict().keys() 
            for key in keys:
                self_attr = None
                other_attr = None
                try:
                    self_attr = getattr(self, key)
                    other_attr = getattr(other, key)
                except AttributeError:
                    # If the attribute is not found from either elements
                    # ignore it entirely
                    if self_attr == None and other_attr == None: 
                        continue
                if  self_attr != other_attr:
                    return False
            # If all given keys match report this as as similar element
            return True
        else:
            return False

    def _clone(self, **kwargs):
        """
        A generic implementation for cloning the object.
        Copies all (public) members in dictionary.
        To clone objects recursively set the recursion level with recursion param.
        @param recursion: Boolean to define recursion on or off
        @param recursion_depth: positive integer to define recursion depth. default is -1 which will 
        perform recursion to all objects.
        """
        dict = self._dict()
        if kwargs.get('class_instance'):
            class_instance = kwargs.get('class_instance')
            del kwargs['class_instance']
        else:
            class_instance = self.__class__
        obj = class_instance(**dict)
        # Remove all children created at the construction phase 
        # This is needed when the recursion adds children to the object so that there are not duplicates
        obj._order = []
        obj._children = {}
        
        # handle the recursion argument
        recursion = kwargs.get('recursion', False)
        if recursion:
            recursion_depth = kwargs.get('recursion_depth', -1)
            if recursion_depth < 0 or recursion_depth > 0:
                # decrease the recursion
                kwargs['recursion_depth'] = recursion_depth - 1 
                for child in self._objects():
                    obj._add(child._clone(**kwargs), container.APPEND)
        return obj

    def _dict(self, **kwargs):
        """
        Return the public variables in a dictionary
        """
        dict = {}
        # loop through the items in this object internal __dict__
        # and add all except internal variables and function overrides  
        for (key,value) in self.__dict__.items():
            if not kwargs.get('internals', False) and key.startswith('_'):
                continue
            elif not kwargs.get('callables', False) and callable(value):
                continue
            elif kwargs.get('ignore_empty') and not value:
                # ignore empty values
                pass
            else:
                dict[key] = value
        return dict

    def _default_object(self, name):
        return Base(name)

    @property
    def fqr(self):
        """
        Return a Fully Qualified Ref, which is the full name of the reference. 
        Joins the namespace and ref to one string.
        @return: A string 
        """
        return utils.dottedref.join_refs([self.namespace, self.get_ref()])

    @property
    def namespace(self):
        """
        @return: The namespace of the object.
        """
        containerpath = ""
        path = ""
        parentcontainer = self.find_parent(container=True)
        parent = self.find_parent(type=Base)
        paths = []
        while parent and parent != parentcontainer:
            """ Skip the element if it is supposed to be hidden. Begins with _. """
            if not parent.get_ref().startswith('_'):
                paths.append(parent.get_ref())
            parent = parent._get_parent()
        if parentcontainer:
            paths.append(parentcontainer.namespace)
        paths.reverse()
        return utils.dottedref.join_refs(paths)

    def path(self, toparent=None):
        """
        Get the path to this Base object..
        @param toparent: the _parent object up to which the path is relative. Default value is None.,
        which gives the fully qualified path in the topology.
        @return: The path to this Base object from toparent
        """
        return self._path(toparent)

    def parent_path(self, toparent=None):
        """
        Get the path to the parent of this Base object..
        @param toparent: the _parent object up to which the path is relative. Default value is None.,
        which gives the fully qualified path in the topology.
        @return: The path to this Base object from toparent
        """
        if self._parent != None:
            return self._parent.path(toparent)
        else:
            return ''

    def get_fullref(self):
        """
        Return a full reference, reference including a 
        possible index of the object in list. 
        e.g. ref can be bar[1] or just the normal bar. 
        
        @return: The full reference of the object.
        """
        if self.parent and utils.is_list(self.parent._get(self.ref)):
            return "%s[%s]" % (self.ref, self.get_index())
        else:
            return self.ref

    def get_fullfqr(self):
        """
        Return a full reference, reference including a 
        possible index of the object in list. 
        ref and adds index.
        @return: A string 
        """
        return utils.dottedref.join_refs([self.get_fullnamespace(), self.get_fullref()])

    def get_fullnamespace(self):
        """
        @return: The full namespace of the object with possible indexes of the parent objects
        """
        containerpath = ""
        path = ""
        parentcontainer = self.find_parent(container=True)
        parent = self.find_parent(type=Base)
        paths = []
        while parent and parent != parentcontainer:
            paths.append(parent.get_fullref())
            parent = parent.parent
        if parentcontainer:
            paths.append(parentcontainer.namespace)
        paths.reverse()
        return utils.dottedref.join_refs(paths)

    def get_storage(self):
        """
        Get the root storage from the root object.
        """
        if self._find_parent():
            return self._find_parent().get_storage()
        else:
            raise exceptions.StorageException("Storage is not found from root!")

    def get_project(self):
        """
        Get the root project from the root object.
        """
        if isinstance(self, Project):
                return self
        elif self._find_parent():
            return self._find_parent().get_project()
        else:
            raise exceptions.NotFound("Project not found!!")

    def get_default_view(self):
        """
        Get the default view from the root object.
        """
        try:
            return self._find_parent().get_default_view()
        except exceptions.NotFound:
            raise exceptions.NotFound("Default View is not found! No root configuration?")

    def get_root(self):
        """
        Get the root object
        """
        try:
            return self._find_parent().get_root()
        except exceptions.NotFound:
            return self

    def get_root_configuration(self):
        """
        Get the root object
        """
        if self.find_parent(type=Configuration):
            return self.find_parent(type=Configuration).get_root_configuration()
        elif isinstance(self, Configuration):
            return self
        else:
            return None

    def get_configuration(self):
        """
        Return the containing configuration of this object.
        """
        parent = self._find_parent_or_default(type=Configuration)
        return parent

    def get_configuration_path(self):
        """
        Return the path of containing configuration of this object.
        """
        parent = self._find_parent_or_default(type=Configuration)
        try:
            return parent.get_full_path()
        except AttributeError:
            return None
    
    def get_index(self):
        """
        @return : the index of the data element for sequential data defined inside the same configuration.
        0 for normal data.
        """
        # Get the list of items from parent which contains this element and ask my own index
        # Make sure that the returned element is a list with get_list
        selflist = utils.get_list(self._get_parent()._get(self.get_ref()))
        return selflist.index(self)

    def find_parent(self, **kwargs):
        """
        find the closest parent object of given type.
        e.g. find_parent(type=Configuration) returns the closest parent 
        Configuration parent instance
        @param type: class definitiob
        """
        type = kwargs.get('type', None)
        container = kwargs.get('container', False)
        try:
            parent = self._find_parent()
            if type and isinstance(parent, type):
                    return parent
            elif container and hasattr(parent, 'container'):
                    return parent
            else:
                return parent.find_parent(**kwargs)
        except exceptions.NotFound:
            return None

    def add(self, child, policy=container.REPLACE):
        """
        A generic add function to add child objects. The function is intended to act as
        proxy function that call the correct add function based on the child objects class.
        
        Example: obj.add(Feature("test")), actually obj.add_feature(Feature("test"))
        @param child: the child object to add
        @raise IncorrectClassError: if the given class cannot be added to this object.  
        """
        raise exceptions.NotSupportedException("Cannot add %s object to %s" % (child, self))

    def get_elem(self, fqr):
        """
        A generic get function to get child objects and members. The function uses getattr
        to traverse downwards the the object tree. The returned object is the final object or attribute 
        if it is found. Raises AttributeError if the child is not found.
        
        Example: obj.get('test.bar'), returns child obj.test.bar
        @param fqr: the fully qualified ref to the object
        @raise AttributeError: if the given ref is not found.  
        """
        return None

    def get_store_interface(self):
        # if the project cannot be retrieved return None
        try:
            return self.get_project()
        except exceptions.NotFound:
            return None
    
    def get_id(self): 
        try:
            return self._id
        except AttributeError:
            return None

    def set_id(self,value): 
        self._id = value

    def del_id(self): 
        delattr(self,'_id')

    """ The id as a property """
    id = property(get_id,set_id, del_id)

class Project(Base):
    """
    A project is a container that can hold several Configuration objects.
    """

    def __init__(self, storage, **kwargs):
        """
        Project constructor
        """
        Base.__init__(self, "")
        """ Try to set the model and tet the actual configuration class """
        try:
            self._model = storage.persistentmodule.MODEL
        except AttributeError:
            self._model = None
        self.loaded = {}
        self.set_storage(storage)
        self.update()

    def __getstate__(self):
        state = {}
        state['storage'] = self.storage
        return state

    def __setstate__(self, state):
        self.__init__(state['storage'])

    def __add_loaded__(self, ref, obj):
        """
        Add the object to loaded 
        """
        self.loaded[ref] = {'counter': 0, 'obj': obj}

    def __get_loaded__(self, ref):
        """
        Get a loaded object if it is existing and increase the reference counter
        @param ref: 
        @return: The loaded object if it exists. None if it does not. 
        """
        if self.loaded.has_key(ref):
            return self.loaded[ref]['obj']
        else:
            return None

    def __loaded__(self, ref):
        """
        Get a loaded object if it is existing and increase the reference counter
        @param ref: 
        @return: The loaded object if it exists. None if it does not. 
        """
        if self.loaded.has_key(ref):
            self.loaded[ref]['counter'] += 1
        else:
            raise exceptions.NotFound("ref %s is not found from loaded!" % ref)

    def __unloaded__(self, ref):
        """
        returns True when the reference count is zero and object can be released.
        """
        if self.loaded.has_key(ref):
            self.loaded[ref]['counter'] -= 1
            if self.loaded[ref]['counter'] == 0:
                del self.loaded[ref]
                return True
            else: 
                return False
        else:
            # Return False in case the object is loaded at all in this project 
            # increases performance as unloading is not done on unchanged objects
            return False
        
    def _supported_type(self, obj):
        if isinstance(obj, Configuration) \
        or isinstance(obj, ConfigurationProxy): 
            return True
        else:
            return False


    def update(self):
        """
        update the root confml files as configurations
        """
        root_confmls = self.get_storage().list_resources(".")
        root_confmls = utils.resourceref.filter_resources(root_confmls, "\.confml")
        for rootml in root_confmls:
            self._add(ConfigurationProxy(rootml))
    
    def get_storage(self):
        """
        Get the Storage instance of this Project.
        """
        return self.storage

    def set_storage(self, storage):
        """
        Set the Storage instance of this Project.
        """
        if storage != None and not isinstance(storage, Storage):
            raise exceptions.StorageException("The given storage is not a instance of Storage!")
        self.storage = storage

    def list_configurations(self, filter_or_filters=None):
        """
        List the direct child objects of the project (Root configurations)
        @param filter_or_filters: A regular expression or list of regular expressions
            used for filtering the configuration paths. If None, all configurations are
            returned.
        @return: a list for configuration file paths
        """
        filters = None
        if isinstance(filter_or_filters, basestring):   filters = [filter_or_filters]
        elif filter_or_filters is not None:             filters = filter_or_filters
        
        configs = [obj.get_path() for obj in self._objects()]
        
        if filters is not None:
            result = []
            for config in configs:
                for filter in filters:
                    if re.match(filter, config) is not None:
                        result.append(config)
                        break
            return result
        else:
            return configs

    def list_all_configurations(self):
        """
        List all configuration objects of the project (all configurations)
        @return: a list for configuration file paths
        """
        # TODO
        # huge performance problem 
        return [obj.get_full_path() for obj in self._traverse(type=(Configuration, ConfigurationProxy))]

    def get_configuration(self, path):
        """
        Get a configuration object from the given path
        @param path: path to configuration 
        @return: a instance of Configuration.
        """
        # Load the configuration object if it is not already loaded
        try:
            return self._get(utils.resourceref.to_objref(utils.resourceref.norm(path)))
        except exceptions.NotFound, e:
            if self.storage.is_resource(utils.resourceref.norm(path)):
                proxy = ConfigurationProxy(utils.resourceref.norm(path))
                proxy._set_parent(self)
                return proxy
            else:
                raise e

    def is_configuration(self, path):
        """
        Return true if the given path is a configuration object in this Project.
        @param path: path to configuration 
        @return: Boolean return value.
        """
        # Changed from list_all_configurations to list_configurations
        # (list_all_configurations causes a insane performance problem with _traverse)
        #
        try:
            return self.storage.is_resource(path)
        except exceptions.NotSupportedException:
            return path in self.list_configurations()
        
    def add_configuration(self, config, overwrite_existing=False):
        """
        Add a Configuration object to this project
        @param config: The configuration object to add
        @param overwrite_existing: When this is set true any existing configuration is 
        overwritten. 
        """ 
        if isinstance(config, Configuration):
            if not overwrite_existing and self.is_configuration(config.get_path()):
                raise exceptions.AlreadyExists("%s" % config.get_path())
            
            proxy = ConfigurationProxy(config.path)
            proxy._set_obj(config)
            self._add(proxy)
            #self._add(config)
            self.__add_loaded__(config.get_path(), config)
            self.__loaded__(config.get_path())
        else:
            raise exceptions.IncorrectClassError("Only Configuration instance can be added to Project!")

    def create_configuration(self, path, overwrite_existing=False, **kwargs):
        """
        Create a Configuration object to this project
        @param path: The path of the new configuration file
        @param overwrite_existing: When this is set true any existing configuration is 
        overwritten. 
        @param **kwargs: normal keyword arguments that are passed on to the newly 
        created Configuration object. See Configuration object constructor description on what
        you can pass on here.  
        """
        config = self.get_configuration_class()(utils.resourceref.norm(path), **kwargs)
        self.add_configuration(config, overwrite_existing)
        return config

    def remove_configuration(self, path):
        """
        Remove a Configuration by its reference
        """
        # remove configuration as an object and try to remove it from the storage
        self._remove(utils.resourceref.to_objref(path))
        try:
            self.storage.delete_resource(path)
        except exceptions.NotSupportedException:
            pass
        return

    def import_configuration(self, configuration):  
        """
        Import a configuration object from another storage
        """
        self.storage.import_resources(configuration.list_resources(), configuration.get_storage())
        return

    def export_configuration(self, configuration, export_storage, **kwargs):
        """
        Export a configuration object to another storage
        """
        # First clone the configuration and then import the rest of the configuration resources
        if isinstance(configuration, ConfigurationProxy):
            configuration = configuration._get_obj()
        
        export_storage.unload(configuration.get_full_path(),configuration)
        for child in configuration._traverse(type=Configuration):
            export_storage.unload(child.get_full_path(),child)
        
        ruleml_eval_globals_files = []
        for child in configuration._traverse(type=RulemlEvalGlobals):
            if child.file != None:
                ruleml_eval_globals_files.append(RulemlEvalGlobals.get_script_file_full_path(child))
        
        #If the configuration is not in the root of the project adding the path 
        #to final exporting source path.
        #l = []
        empty_folders = kwargs.get('empty_folders',False)
        layer = configuration.get_layer()
        all_resources = []
        layer_content = layer.list_content(empty_folders)
        layer_doc = layer.list_doc(empty_folders)
        layer_implml = layer.list_implml(empty_folders)

        include_filters = kwargs.get('include_filters',{})
        exclude_filters = kwargs.get('exclude_filters',{})
        
        include_content_filter = include_filters.get('content')
        exclude_content_filter = exclude_filters.get('content')
        
        # perform filtering of content files
        if exclude_content_filter:
            f = lambda x: not re.search(exclude_content_filter, x, re.IGNORECASE)
            layer_content = filter(f,layer_content)

        if include_content_filter:
            f = lambda x: re.search(include_content_filter, x, re.IGNORECASE)
            layer_content = filter(f,layer_content)
        
        all_resources.extend(layer_content) 
        all_resources.extend(layer_doc)
        all_resources.extend(layer_implml)
        
        cpath = utils.resourceref.get_path(configuration.get_path()) 
        resr = [utils.resourceref.join_refs([cpath,related]) \
                for related in all_resources]
        resr.extend(ruleml_eval_globals_files)
        
        self.storage.export_resources(resr ,export_storage, kwargs.get("empty_folders", False))
        return

    def get_configuration_class(self):
        """
        return the default configuration class that is used with the model. 
        """
        return utils.get_class(self._model, Configuration)

    def save(self):
        """
        Save the object to the permanent Storage object. Calls the save operation for 
        all the children and also for the Storage.
        """
        for child in self._objects():
            if isinstance(child, (Configuration, ConfigurationProxy)):
                child.save()
        self.storage.save()

    def close(self):
        """
        Close the Project.
        """
        for child in self._objects():
            if isinstance(child, (Configuration, ConfigurationProxy)):
                child.close()
        self.storage.close()

    def load(self, path):
        """
        Load an object from a reference. The given reference is loaded once from storage
        and stored as a loaded object to the Project. Sequential loads to the same ref will
        return the same object.
        @param path: The reference where to load the object 
        @raise StorageException: if the given object cannot be loaded as an 
        object from this storage 
        """
        if not self.__get_loaded__(path):
            configuration = self.get_storage().load(path)
            if configuration.get_ref() == 'unknown':
                configuration.set_ref(utils.resourceref.to_dref(path))
            self.__add_loaded__(path, configuration)
        """ increase the ref counter """
        self.__loaded__(path)
        return self.__get_loaded__(path)

    def unload(self, path, object):
        """
        Release the given ref, which decreases the reference counter of the given ref.
        @param path: The reference where to store the object 
        @param object: The object instance to dump 
        @raise StorageException: if the given object cannot be dumped to this storage 
        """
        if self.__unloaded__(path):
            self.get_storage().unload(path, object)
            # remove the configuration from this this project, 
            # with proxy set the _obj reference to None
            try:
                conf =  self.get_configuration(path)
                if isinstance(conf, ConfigurationProxy):
                    conf._set_obj(None)
            except exceptions.NotFound:
                # if the configuration is not found at all then ignore the resetting
                pass

    def get_path(self):
        """
        Return the path of the project, which is always root
        """
        return ""


class CompositeConfiguration(Base):
    """
    A base class for composite Configuration objects.  
    """
    def __init__(self, ref="", **kwargs):
#        self.meta       = {}
#        self.desc       = ""
        super(CompositeConfiguration, self).__init__(ref, **kwargs)
        self.container = True

    def _configuration_class(self):
        return Configuration

    def add_configuration(self, config):
        """
        Add an existing Configuration to this configuration
        @param config: A Configuration instance:
        @return: None 
        """
        """
        Merge the default view features from added config to this configs _default_view.
        """
        # if the Configuration has a separate resource path, add it automatically behind proxy 
        if utils.resourceref.is_path(config.path) and isinstance(config, Configuration):
            proxy = ConfigurationProxy(config.path)
            proxy._set_obj(config)
            self._add(proxy)
            # Add the new configuration to the list of "modified/loaded" configurations
            try:
                prj = self.get_project()
                prj.__add_loaded__(config.get_full_path(), config)
                prj.__loaded__(config.get_full_path())
            except exceptions.NotFound:
                # if the parent is not found this configuration is not (yet) a part of project and cant be stored 
                pass
        else:
            self._add(config)

    def include_configuration(self, configref, policy=0):
        """
        Add an existing Configuration to this configuration by its resource reference
        @param config: A Configuration instance:
        @return: None 
        """
        # add the configuration load proxy to this configuration instead 
        # adding the configuration directly
        self._add(ConfigurationProxy(configref), policy)

    def create_configuration(self, path):
        """
        Create a new configuration by its name to the Configuration. 
        1. Create new Configuration object
        2. Create new ConfigurationProxy 
        3. Add proxy to this object
        4. Set proxy to point to the created Configuration object
        @param path: The reference of the configuration to create
        @return: The new configuration object.
        """
        # normalise the path
        normpath = utils.resourceref.norm(path)
        cklass = self._configuration_class()
        conf = cklass(normpath, namespace=self.namespace)
        self.add_configuration(conf)
        return conf

    def remove_configuration(self, path):
        """
        Remove a Layer object from the Configuration by its reference.
        """
        self._remove(utils.resourceref.to_objref(path))

    def list_configurations(self):
        """
        List all Layer objects in the Configuration
        @return: a copy array of layer references.
        """
        return [config.get_path() for config in self._objects(type=(Configuration, ConfigurationProxy))] 

    def list_all_configurations(self):
        """
        List all Layer objects in the Configuration
        @return: a copy array of layer references.
        """
        return [config.get_path_for_parent(self) for config in self._traverse(type=(Configuration, ConfigurationProxy))] 

    def get_configuration(self, path):
        """
        Get a Layer object by if path
        @return: a Layer object
        """
        return self._get(utils.resourceref.to_objref(path))

    def get_configuration_by_index(self, index):
        """
        Get a Layer object by if indexing number
        @return: a Layer object
        """
        configs = self._objects(type=(Configuration, ConfigurationProxy))
        return configs[index]

    def get_last_configuration(self):
        """
        Get the last Layer object from this configuration hierarchy.
        @return: a Layer object
        """
        last_config = self
        try: 
            last_config = last_config.get_configuration_by_index(-1)
            return last_config.get_last_configuration()
        except IndexError:
            return self 

    def add(self, child, policy=container.REPLACE):
        """
        A generic add function to add child objects. The function is intended to act as
        proxy function that call the correct add function based on the child objects class.
        
        Example: obj.add(Feature("test")), actually obj.add_feature(Feature("test"))
        @param child: the child object to add
        @raise IncorrectClassError: if the given class cannot be added to this object.  
        """
        if isinstance(child, Configuration):
            self.add_configuration(child)
        elif isinstance(child, ConfigurationProxy):
            self._add(child)
        elif isinstance(child, Base):
            self._add(child)
        else:
            raise exceptions.IncorrectClassError("Cannot add %s to %s" % (child, self))

    def layered_resources(self, layers=None, empty_folders=False, folder=None, resource_type=None):
        """
        Fetch resource paths by layers so that if a resource with the same name
        exists on multiple layers, the one on the latest layer is the active one.
        @param layers: List of layer indices to specify the layer to use, None
            for all layers.
        @param empty_folders: If True, empty folders are returned also.
        @param folder: Name of a specific folder from which to get resources, or None.
            If None, resource_type must be specified.
        @param resource_type: Type of the resources to find. Must be one of
            ('confml', 'implml', 'content', 'doc') or None.
            If None, folder must be specified.
        @return: A container.DataContainer instance containing the resource paths.
            For example: {'foo.txt': ['layer1/content/foo.txt',
                                      'layer2/content/foo.txt'],
                          'bar.txt': ['layer1/content/bar.txt']}
        """
        MAPPING = {'confml':    lambda layer: layer.confml_folder(),
                   'implml':    lambda layer: layer.implml_folder(),
                   'content':   lambda layer: layer.content_folder(),
                   'doc':       lambda layer: layer.doc_folder()}
        if resource_type is not None and resource_type not in MAPPING:
            raise ValueError("Invalid resource type %r, should be one of %r" % (resource_type, MAPPING.keys()))
        
        if folder and resource_type:
            raise ValueError('Only one of folder and resource_type must be specified!')
        if not folder and not resource_type:
            raise ValueError('Either folder or resource_type must be specified!')
        
        configuration_array = []
        if layers == None:
            configuration_array = self.list_configurations()
        else:
            all = self.list_configurations()
            for i in layers:
                configuration_array.append(all[i])
        
        # Add the current configuration as the last one in the list, in case
        # the current configuration happens to be a layer root itself
        configuration_array.append('')
        
        # Set up the get_folder function based on the parameters
        if resource_type:
            get_folder = MAPPING[resource_type]
        else:
            def get_folder(layer):
                cpath = layer.get_current_path()
                return Folder(layer.storage, utils.resourceref.join_refs([cpath, folder]))
        
        result = container.DataContainer()
        for configuration_path in configuration_array:
            folder_obj = get_folder(self.get_configuration(configuration_path).get_layer())
            folder_path = folder_obj.get_current_path()
            for res_path in folder_obj.list_resources("", recurse=True, empty_folders=empty_folders):
                if res_path == '': continue # ZipStorage sometimes returns empty paths
                res_fullpath = utils.resourceref.join_refs([folder_path, res_path])
                result.add_value(res_path, res_fullpath)
        return result
    
    def layered_confml(self, layers=None, empty_folders=False):
        return self.layered_resources(layers, empty_folders, resource_type='confml')
    
    def layered_implml(self, layers=None, empty_folders=False):
        return self.layered_resources(layers, empty_folders, resource_type='implml')
    
    def layered_content(self, layers=None, empty_folders=False):
        return self.layered_resources(layers, empty_folders, resource_type='content')
    
    def layered_doc(self, layers=None, empty_folders=False):
        return self.layered_resources(layers, empty_folders, resource_type='doc')
    
    
    
class Configuration(CompositeConfiguration):
    """
    A Configuration is a container that can hold several Layer objects.
    """

    def __init__(self, ref="", **kwargs):
        self.path = kwargs.get('path') or ref
        self.namespace = kwargs.get('namespace', '')
        self.name = kwargs.get('name',utils.resourceref.to_objref(self.path))
        self.version = kwargs.get('version')
        super(Configuration, self).__init__(utils.resourceref.to_objref(self.path), **kwargs)
        self.container = True

    def __getstate__(self):
        state = self.__dict__.copy()
        if state.has_key('_children'):
            childs = state.get('_children')
            if childs.has_key('?default_view'):
                childs.pop('?default_view')
                state['_children'] = childs
        return state

    def _default_object(self, name):
        return self._default_class()(name)

    def _default_class(self):
        return self._feature_class()

    def _feature_class(self):
        return Feature

    def _view_class(self):
        return View

    def _supported_type(self, obj):
        if isinstance(obj, Configuration) \
        or isinstance(obj, Feature) \
        or isinstance(obj, Data) \
        or isinstance(obj, ConfigurationProxy) \
        or isinstance(obj, View) \
        or isinstance(obj, Base): 
            return True
        else:
            return False

    def _dict(self, **kwargs):
        """
        Return the public variables in a dictionary
        """
        dict = super(Configuration, self)._dict(**kwargs)
        dict['namespace'] = self.namespace
        return dict
    
    def get_name(self):
        """
        Return the name of the configuration
        """
        return self.name

    def set_name(self, name):
        """
        Set the name
        """
        self.name = name

    def get_path(self):
        """
        Return the path of the configuration resource
        """
        return self.path

    def set_path(self, path):
        """
        Set the path of the configuration resource, and update the name and ref to correspond
        """
        self.path = path
        self.set_ref(utils.resourceref.to_objref(self.path))

    def get_full_path(self):
        """
        Return the path of the configuration resource
        """
        try:
            parentconfig = self._find_parent(type=Configuration)
            parent_path = utils.resourceref.get_path(parentconfig.get_path()) 
        except exceptions.NotFound:
            parent_path = ""
        return utils.resourceref.join_refs([parent_path, self.path])

    def get_path_for_parent(self, parent):
        """
        Return the path to this configuration for a defined parent Configuration object.
        """
        parent_path = ""
        try:
            parentconfig = self._find_parent(type=Configuration)
            if parent != parentconfig:
                parent_path = utils.resourceref.get_path(parentconfig.get_path_for_parent(parent)) 
        except exceptions.NotFound:
            pass
        return utils.resourceref.join_refs([parent_path, self.path])

    def get_layer(self):
        """
        Get the layer object where this Configuration is located. 
        """
        if not hasattr(self, "layer"):
            layerpath = utils.resourceref.get_path(self.get_path())
            # hardcoded removal of confml folder from the layer path it is there
            layerpath = utils.resourceref.remove_end(layerpath, '/confml')
            self.layer = Layer(self.get_storage(), layerpath)
            """ Add the sublayers to this layer if they are different from this configuration """
            for configpath in self.list_configurations():
                sublayer_path = utils.resourceref.get_path(self.get_configuration(configpath).get_full_path())
                sublayer_path = utils.resourceref.remove_end(sublayer_path, '/confml')
                if sublayer_path != utils.resourceref.get_path(self.get_path()):
                    self.layer.add_layer(self.get_configuration(configpath).get_layer())
        return self.layer

    def set_namespace(self, namespace):
        """
        @param namespace: The new namespace of the object
        """
        self._namespace =  namespace

    def get_namespace(self):
        """
        @return: The reference of the object.
        """
        return self._namespace

    def del_namespace(self):
        """
        @return: The reference of the object.
        """
        self._namespace = None
    namespace = property(get_namespace, set_namespace, del_namespace)

    def list_resources(self, **kwargs):
        """
        List all resources used in this configuration
        """
        """
        1. First ensure that all configuration resource files are added 
        2. Then add all layer resources 
        3. Make the list distinct
        """
        
        
        resources = [self.get_full_path()]
        for config in self._traverse(type=(Configuration,ConfigurationProxy)):
            resources.append(config.get_full_path())
        layer = self.get_layer()
        for resref in layer.list_all_resources():
            resources.append(utils.resourceref.join_refs([layer.get_current_path(), resref]))
    
        return utils.distinct_array(resources)

    def get_resource(self, ref, mode="r"):
        """
        Get the given resource as a Resource object. The resource is searched relative to the 
        Configuration path, e.g. Configuration('test/foo/root.confml') => searches from 'test/foo'.
        @param ref: the reference path to the requested resource
        @return: a instance of Resource. 
        """
        mypath = utils.resourceref.get_path(self.path)
        myref = utils.resourceref.join_refs([mypath, ref])
        return self.get_storage().open_resource(myref, mode)

    def get_all_resources(self):
        """
        Get all resources in resource list of Resource objects
        """
        resources = []
        res_list = self.list_resources()
        for res in res_list:
            resources.append(self.get_storage().open_resource(res))
        return resources

    def get_root_resource(self):
        """
        Get the configuration reference resource.
        """
        return self.get_storage().open_resource(self.get_path())

    def get_feature(self, ref):
        """
        Get a feature object by its reference.
        @param ref: The reference to the feature object.
        @return: A Feature object
        """
        return self._get(ref)

    def create_feature(self, ref, **kwargs):
        """
        Create a feature object to the configuration.
        @param ref: The ref for the Feature object.
        @param **kwargs: keyword arguments  
        e.g. to add fea2 under fea1 add_feature(fea2, 'fea1')
        @return: the new feature object.
        """
        fea = self._feature_class()(ref, **kwargs)
        self._add(fea)
        return fea

    def add_feature(self, feature, namespace=""):
        """
        Add a feature object to the configuration.
        @param feature: The Feature object to add.
        @param namespace: The sub namespace for the feature. 
        e.g. to add fea2 under fea1 add_feature(fea2, 'fea1')
        @return: None
        """
        if namespace and self._has(namespace):
            # Add the feature directly with an existing feature's add_feature functionality
            self.get_feature(namespace).add_feature(feature)
        else:
            self._add_to_path(namespace, feature)

    def remove_feature(self, ref):
        """
        remove feature by its reference
        @param ref: 
        """
        self._remove(ref)

    def list_features(self):
        """
        List immediate features found under the this configuration (the top nodes). 
        The features are also available via the _default_view of the configuration.
        @return: a list of feature references. 
        """
        return [fea.get_ref() for fea in self._objects(type=Feature)]

    def list_all_features(self):
        """
        List all features found under the this configuration. The features are also 
        available via the _default_view of the configuration.
        @return: a list of feature references. 
        """
        return [fea.fqr for fea in self._traverse(type=Feature)]

    def add_data(self, data, policy=container.REPLACE):
        """
        Add a data object to this configuration object.
        @param data: The Data object or list of Data objects to add.
        @return: None
        """
        data_objs = utils.get_list(data)
        
        if policy == container.PREPEND:
            data_objs = reversed(data_objs)
            policy_first = container.PREPEND
            policy_rest = container.PREPEND
        else:
            policy_first = policy
            policy_rest = container.APPEND
        
        for i, data_obj in enumerate(data_objs):
            if not self._has(data_obj.attr):
                self._add(DataContainer(data_obj.attr, container=True))
            (namespace, name) = utils.dottedref.psplit_ref(data_obj.get_fearef())
            
            if i == 0:  p = policy_first
            else:       p = policy_rest
            self._get(data_obj.attr)._add_to_path(namespace, data_obj, p)

    def get_data(self, ref):
        """
        Get a data object by its reference.
        @param ref: The reference to the data object.
        @return: A Data object
        """
        return self.data._get(ref)

    def remove_data(self, ref):
        """
        remove feature by its reference
        @param ref: 
        """
        self.data._remove(ref)

    def list_datas(self):
        """
        List all datas found under the this configuration. 
        @return: a list of Data references. 
        """
        if self._has('data'):
            return [dataelem.fqr for dataelem in self.data._objects(type=Data)]
        else:
            return []

    def get_datas(self):
        """
        List immediate datas found under the this configuration (the top nodes). 
        @return: a list of Data references. 
        """
        if self._has('data'):
            return [dataelem for dataelem in self.data._objects(type=Data)]
        else:
            return []

    def list_all_datas(self):
        """
        List all Data elements found under the this configuration (or subconfigurations). 
        @return: a list of Data references. 
        """
        return [dataelem.fqr for dataelem in self._traverse(type=Data)]

    def get_all_datas(self):
        """
        List all Data elements found under the this configuration (or subconfigurations). 
        @return: a list of Data references. 
        """
        return [dataelem for dataelem in self._traverse(type=Data)]

    def list_leaf_datas(self):
        """
        List all leaf Data elements (i.e. actually modified settings) found under this configuration (or subconfigurations). 
        @return: A list of Data references. 
        """
        return [dataelem.fqr for dataelem in self._find_leaves(type=Data)]
    
    def get_leaf_datas(self):
        """
        Get all leaf Data elements (i.e. actually modified settings) found under this configuration (or subconfigurations). 
        @return: A list of Data objects. 
        """
        return [dataelem for dataelem in self._find_leaves(type=Data)]

    def get_view(self, ref):
        """
        Get a view object by its reference.
        @param ref: The reference to the view object.
        @return: A View object
        """
        # Populate the view object before returning it
        view = self._get(ref)
        view.populate()
        return view

    def create_view(self, viewname):
        """
        Create a view object to the configuration.
        @param viewname: The name of the view to add. 
        @return: view object
        """
        viewobj = self._view_class()(viewname)
        self.add_view(viewobj)
        return viewobj

    def add_view(self, viewobj):
        """
        Add a view object to the configuration.
        @param viewobj: The existing view object to add. 
        @return: None
        """
        assert(isinstance(viewobj, View))
        return self._add(viewobj)

    def remove_view(self, ref):
        """
        Remove a view object from the configuration.
        @param ref: The reference to the View. 
        @return: None
        @raise NotFound: when view is not found.
        """
        return self._remove(ref)

    def list_views(self):
        """
        List all views found under the this configuration.
        @return: a list of view references. 
        """
        return [view._path(self) for view in self._traverse(type=View)]

    def save(self):
        """
        Save the object to the permanent Storage object. Calls the save operation of 
        all the children.
        """
        # Change the recursion order so that the current object 
        # is saved first and then its childen.
        # This increases performance in cases where this object requires information about its childen (no unload -> load cases)
        self.get_project().unload(self.get_full_path(), self)
        for child in self._objects():
            if isinstance(child, (Configuration,ConfigurationProxy)):
                child.save()

    def close(self):
        """
        Close the configuration
        """
        for child in self._objects():
            if isinstance(child, (Configuration, ConfigurationProxy)):
                child.close()
#        if self.get_full_path() != "":
#            self.get_project().unload(self.get_full_path(), self)

    def add(self, child, policy=container.REPLACE):
        """
        A generic add function to add child objects. The function is intended to act as
        proxy function that call the correct add function based on the child objects class.
        
        Example: obj.add(Feature("test")), actually obj.add_feature(Feature("test"))
        @param child: the child object to add
        @raise IncorrectClassError: if the given class cannot be added to this object.  
        """
        if isinstance(child, Feature):
            self.add_feature(child)
        elif isinstance(child, View):
            self._add(child)
        elif isinstance(child, (Data)):
            self.add_data(child)
        else:
            super(Configuration, self).add(child)

    def get_default_view(self):
        """
        Get the default view from this configuration hierarchy.
        This returns always the view from the Root configuration point of view.
        """
        try:
            parent = self._find_parent_or_default()
            if parent and isinstance(parent, Configuration):
                return parent.get_default_view()
            else:
                if not self._has('?default_view'):
                    self._create_default_view()
                return self._get('?default_view')
        except exceptions.NotFound, e:
            raise e
        # raise exceptions.NotFound("Default View is not found! No root configuration?")
    
    def recreate_default_view(self):
        try:
            parent = self._find_parent_or_default() 
            if parent and isinstance(parent, Configuration):
                parent.recreate_default_view()
            else:
                self._create_default_view()
        except exceptions.NotFound, e:
            raise e
        # raise exceptions.NotFound("Default View is not found! No root configuration?")
    
    def _create_default_view(self):
        # Rebuild the default view for this Configuration
        default_view = View("?default_view", data=True)
        #self._default_view._parent= self
        self._add(default_view)
        # First add all features of the configuration to the view. 
        # Then add all data elements under the features
        for child in self._traverse(type=Feature):
            # TODO print "Adding : %s -> %s" % (child.namespace, child)
            default_view.add_feature(child, child.namespace)
        for child in self._traverse(type=Data):
            #parent_config = child._find_parent_or_default(type=Configuration)
            #print "Adding data %s: fqr: %s from file %s." % (child.get_value(), child.fqr, parent_config.get_path())
            try:
                fea = default_view.get_feature(child.fqr)
                fea.add_data(child)
            except exceptions.NotFound, e:
                data_parent_config = child._find_parent_or_default(type=Configuration)
                logging.getLogger('cone').info("Warning: Feature '%s' for data in %s not found." % (child.fqr, data_parent_config.get_path()))

class ConfigurationProxy(container.LoadProxy):
    """
    Configuration loading proxy. Loads the configuration from the given reference, when needed.
    """
    def __init__(self, path, **kwargs):
        """
        The ConfigurationProxy that represents a configuration that is included in another configuration.
        @param ref: the reference to the storage resource 
        The ConfigurationProxy trust to get the store_interface from the parent object with get_storage() function.
        
        """
        super(ConfigurationProxy,self).__init__(path, **kwargs)
        self.set('_name', utils.resourceref.to_objref(path))
    
    def _clone(self, **kwargs):
        """
        A ConfigurationProxy specific implementation for cloning.
        Copies all (public) members in dictionary.
        To clone call the actual object that is proxied as well if the reqursion is on.
        @param recursion: Boolean to define recursion on or off
        @param recursion_depth: positive integer to define recursion depth. default is -1 which will 
        perform recursion to all objects.
        """
        dict = self._dict()
        obj = self.__class__(**dict)
        # handle the recursion argument
        recursion = kwargs.get('recursion', False)
        if recursion:
            recursion_depth = kwargs.get('recursion_depth', -1)
            if recursion_depth < 0 or recursion_depth > 0:
                # decrease the recursion
                kwargs['recursion_depth'] = recursion_depth - 1
                newobj = self._get_obj()._clone(**kwargs) 
                obj._set_obj(newobj)
        return obj
    
    def _dict(self):
        """
        Return the public variables in a dictionary
        """
        dict = {}
        for key in self.__dict__.keys():
            if key.startswith('_'):
                continue
            else:
                dict[key] = self.__dict__[key]
        return dict
    
    def _get_mapper(self,modelname):
        """
        Return a instance of appropriate mapper for given model.
        """
        return mapping.BaseMapper()

class Group(Base):
    """
    A Group class. Group is used in View to group up other Group/Feature objects.
    """
    def __init__(self, ref="", **kwargs):
        super(Group, self).__init__(ref, **kwargs)
        self.name = kwargs.get('name', ref)
        self.support_data = kwargs.get("data", False)

    def _supported_type(self, obj):
        if isinstance(obj, (Group, \
                           Base, \
                           _FeatureProxy, \
                           FeatureLink, \
                           ConfigurationProxy)): 
            return True
        else:
            return False

    def _default_object(self, name):
        return self._group_class()(name)

    def _group_class(self):
        return Group

    def _featurelink_class(self):
        return FeatureLink

    def add(self, child, policy=container.REPLACE):
        """
        A generic add function to add child objects. The function is intended to act as
        proxy function that call the correct add function based on the child objects class.
        
        Example: obj.add(Feature("test")), actually obj.add_feature(Feature("test"))
        @param child: the child object to add
        @raise IncorrectClassError: if the given class cannot be added to this object.  
        """
        if self._supported_type(child):
            self._add(child)
        else:
            raise exceptions.IncorrectClassError("Cannot add %s to %s" % (child, self))

    def get_name(self):
        """
        Return the name of the configuration
        """
        return self.name

    def set_name(self, name):
        """
        Set the name
        """
        self.name = name

    def create_featurelink(self, feature_ref, **kwargs):
        """
        create a feature link object to this element, with the given ref
        @param feature_ref: the reference for the featurelink which should
        point to a exising feature in the configuration.
        @param **kwargs: keyword arguments are passed to the featurelink object 
        directly.
        """
        fealink = self._featurelink_class()(feature_ref, **kwargs)
        self.add(fealink)
        return fealink

    def get_featurelink(self, ref):
        return self._get(FeatureLink.get_featurelink_ref(ref))
    
    def add_feature(self, feature, path=""):
        """
        Add feature to this Group.
        """
        if not isinstance(feature, Feature):
            raise exceptions.IncorrectClassError("add_feature requires instance of Feature!! Given %s" % feature)
        if not self.support_data:
            self._add_to_path(path, _FeatureProxy(feature._name, feature))
        else:
            self._add_to_path(path, _FeatureDataProxy(feature._name, feature))

    def remove_feature(self, ref):
        """
        remove a given feature from this view by reference. 
        @param ref: 
        """
        self._remove(ref)

    def get_feature(self, ref):
        """
        @param path: The path (ref) to the given feature 
        """
        try:
            return self._get(ref)
        except exceptions.NotFound:
            raise exceptions.NotFound("Feature '%s' not found." % ref)

    def get_features(self, refs, **kwargs):
        """
        Get a list of features that match the ref. 
        
        @param refs: The paths (refs) to the given feature or xpath like expression. The refs
        argument can be a single reference or a list of references to features. 
        @return: A list of features.
        
        NOTE! the invalid references will not raise an exception.
         
        Example1: get_features('foo.bar') would be the same as get_feature('foo.bar'), but this returns 
        always a list [<Feature>].
        Example2: get_features('foo.*') would try to retrieve a list of all foo children.
        Example3: get_features('foo.*', type='') would try to retrieve a list of all foo children, 
        that have a defined type.
        Example4: get_features(['foo','bar.set1']) would try to retrieve a foo and then bar.set1.
        
        """
        
        if utils.is_list(refs):
            features = []
            for ref in refs:
                features += self.get_matching_features(ref, **kwargs)
            return features
        else:
            return self.get_matching_features(refs, **kwargs)

    def get_matching_features(self, ref, **kwargs):
        """
        Get a list of features that match the ref. 
        
        @param refs: The paths (refs) to the given feature or xpath like expression. The refs
        argument can be a single reference or a list of references to features. 
        @return: A list of features.

        NOTE! the invalid references will not raise an exception but return an empty list.
        
        Example1: get_features('foo.bar') would be the same as get_feature('foo.bar'), but this returns 
        always a list [<Feature>].
        Example2: get_features('foo.*') would try to retrieve a list of all foo children.
        Example3: get_features('foo.*', type='') would try to retrieve a list of all foo children, 
        that have a defined type.
        
        """
        try:
            (startref, last) = utils.dottedref.psplit_ref(ref)
            startelem = self._get(startref)
            kwargs['type'] = _FeatureProxy
            if last == '**':
                return [fea for fea in startelem._traverse(**kwargs)]
            elif last == '*':
                return [fea for fea in startelem._objects(**kwargs)] 
            elif ref != "":
                return [self._get(ref)]
            else:
                return []
        except exceptions.NotFound:
            return []
         
    def list_features(self):
        """
        Return a array of all Feature children references under this object.
        """
        return [fea.get_ref() for fea in self._objects(type=(_FeatureProxy))]

    def list_all_features(self):
        """
        Return a array of all Feature children references under this object.
        """
        return [fea.fqr for fea in self._traverse(type=(_FeatureProxy))]

    def create_group(self, groupname, **kwargs):
        """
        create a group object to this element with given group name.
        @param groupname: the name for the new group
        @param **kwargs: keyword arguments are passed on to the new group object.  
        """
        grp = self._group_class()(groupname, **kwargs)
        self.add_group(grp)
        return grp

    def add_group(self, grp):
        """
        """
        self._add(grp)

    def remove_group(self, ref):
        """
        remove a given feature from this view by reference. 
        @param ref: 
        """
        self._remove(ref)

    def get_group(self, ref):
        """
        @param path: The path (ref) to the given feature 
        """
        return self._get(ref)

    def list_groups(self):
        """
        """
        return [group.ref for group in self._objects(type=Group)]

    def populate(self):
        """
        Populate or fetch the link to the actual feature for this featureproxy.
        This method fetches the feature to the _obj member variable and populates also 
        subfeatures. 
        """
        for child in self._traverse(type=FeatureLink):
            child.populate()
        


class View(Group):
    """
    A View class. View is intended to create new or different hierarchies of existing features. A View can contain Group and/or Feature objects.
    """
    def __init__(self, ref="", **kwargs):
        super(View, self).__init__(self.to_ref(ref), **kwargs)
        self.container = True

    @classmethod
    def to_ref(cls, ref):
        """ 
        return a view reference converted from name 
        """
        return ref.replace('.', '').replace('/', '')


class Feature(Base):
    """
    A Feature class. Feature is the base for all Configurable items in a Configuration.
    """
    PROPERTIES = ['value']
    def __init__(self, ref="", **kwargs):
        super(Feature, self).__init__(ref, **kwargs)
        self.name = kwargs.get('name', None)
        self.type = kwargs.get('type', None)
        self.relevant = kwargs.get('relevant', None)
        self.constraint = kwargs.get('constraint', None)
        self._dataproxy = None
        self.extensionAttributes = []

    def __copy__(self):
        dict = {}
        for key in self.__dict__.keys():
            if key.startswith('_') or key == 'ref':
                continue
            else:
                dict[key] = self.__dict__[key]
        fea = self.__class__(self.ref, **dict)
        return fea

    def __getstate__(self):
        state = super(Feature, self).__getstate__()
        # remove the dataproxy value so that it is not stored in serializings
        state.pop('_dataproxy', None)
        # remove instancemethods so that those are not stored in serializings
        state.pop('get_original_value', None)
        state.pop('get_value', None)
        state.pop('set_value', None)
        state.pop('add_feature', None)
        return state

    def __setstate__(self, state):
        super(Feature, self).__setstate__(state)
        self._dataproxy = None

        
    def _supported_type(self, obj):
        # For now support added for desc element via support for Base
        if isinstance(obj, (Feature, Option, Base)):
            return True
        else:
            return False

    def _feature_class(self):
        return Feature

    def add(self, child, policy=container.REPLACE):
        """
        A generic add function to add child objects. The function is intended to act as
        proxy function that call the correct add function based on the child objects class.
        
        Example: obj.add(Feature("test")), actually obj.add_feature(Feature("test"))
        @param child: the child object to add
        @raise IncorrectClassError: if the given class cannot be added to this object.  
        """
        if isinstance(child, Feature):
            self.add_feature(child)
        elif isinstance(child, Option):
            self._add(child, policy)
        elif isinstance(child, Base):
            self._add(child, policy)
        elif isinstance(child, Property):
            self._add(child, policy)
        else:
            raise exceptions.IncorrectClassError("Cannot add %s to %s" % (child, self))

    def get_name(self):
        """
        Return the name of the configuration
        """
        return self.name

    def set_name(self, name):
        """
        Set the name
        """
        self.name = name

    def get_relevant(self):
        """
        Return the relevant attribute of the feature
        """
        return self.relevant

    def set_relevant(self, relevant):
        """
        Set the relevant attribute
        """
        self.relevant = relevant

    def get_constraint(self):
        """
        Return the constraint attribute of the feature
        """
        return self.constraint

    def set_constraint(self, constraint):
        """
        Set the constraint attribute
        """
        self.constraint = constraint

    def get_type(self):
        return self.type

    def set_type(self, type):
        self.type = type

    def create_feature(self, ref, **kwargs):
        """
        Create a feature object to the configuration.
        @param ref: The ref for the Feature object.
        @param **kwargs: keyword arguments  
        e.g. to add fea2 under fea1 add_feature(fea2, 'fea1')
        @return: the new feature object.
        """
        fea = self._feature_class()(ref, **kwargs)
        self.add_feature(fea)
        return fea

    def add_feature(self, feature, path=""):
        """
        @param feature: The Feature object to add 
        """
        self._add_to_path(path, feature)

    def get_feature(self, path):
        """
        @param path: The path (ref) to the given feature 
        """
        return self._get(path)

    def remove_feature(self, ref):
        """
        remove a given feature from this view by reference. 
        @param ref: 
        """
        self._remove(ref)

    def list_features(self):
        """
        Return a array of all Feature children references under this object.
        """
        return [fea.get_ref() for fea in self._objects(type=Feature)]

    def list_all_features(self):
        """
        Return a array of all Feature children references under this object.
        """
        return [fea._path(self) for fea in self._traverse(type=Feature)]

    def add_option(self, option):
        """
        @param option: option object
        """
        if not isinstance(option, Option):
            raise TypeError("%r is not an instance of Option!" % option)
        self._add(option)
    
    def create_option(self, name, value):
        """
        @param name: option name
        @param value: option value
        """
        self._add(Option(name, value))

    def get_option(self, ref):
        """
        @param name: The option reference of the option (as returned by list_options()) 
        """
        real_ref = 'opt_' + ref
        obj = self._get(real_ref)
        if not isinstance(obj, Option):
            raise TypeError('Object %r is not an instance of Option (%r instead)' % (real_ref, type(obj)))
        return obj

    def remove_option(self, ref):
        """
        remove a given option from this feature by option reference. 
        """
        real_ref = 'opt_' + ref
        obj = self._get(real_ref)
        if not isinstance(obj, Option):
            raise TypeError('Trying to remove option with ref %r, but object with ref %r is not an instance of Option (%s instead)' % (ref, real_ref, type(obj)))
        self._remove(real_ref)

    def list_options(self):
        """
        Return a array of all Option children references under this object.
        """
        # Return option refs without the leading 'opt_'
        return [opt.ref[4:] for opt in self._objects(type=Option)]

    def add_property(self, property):
        """
        @param property: property object to add
        """
        if not isinstance(property, Property):
            raise TypeError("%r is not an instance of Property!" % property)
        self._add(property)

    def create_property(self, **kwargs):
        """
        @param name=str: property name 
        @param value=str: property value
        @param unit=str: property unit, e.g. kB
        """
        self._add(Property(**kwargs))


    def get_property(self, ref):
        """
        @param ref: The ref of the property
        """
        obj = self._get(Property.to_propertyref(ref))
        
        if not isinstance(obj, Property):
            raise TypeError('Object %r is not an instance of Property (%r instead)' % (Property.to_propertyref(ref), type(obj)))
        return obj

    def remove_property(self, ref):
        """
        remove a given property from this feature by ref. 
        @param ref: 
        """
        obj = self._get(Property.to_propertyref(ref))
        if not isinstance(obj, Property):
            raise TypeError('Trying to remove property with ref %r, but object with ref %r is not an instance of Property (%s instead)' % (ref, Property.to_propertyref(ref), type(obj)))
        self._remove(Property.to_propertyref(ref))

    def list_properties(self):
        """
        Return a array of all Feature properties under this object.
        """
        
        return [Property.to_normref(property.ref) for property in self._objects(type=Property)]

    def get_value(self, attr=None):
        """
        Get the current value of the feature. 
        @param attr: The attribute name of the data. E.g. attr='data', attr='rfs' 
        """
        return self.convert_data_to_value(self.dataproxy._get_datas(attr=attr), cast=True, attr=attr)

    def set_value(self, value, attr=None):
        """
        Set the current value for this feature. Set the value on the topmost layer.
        @param value: the value to set
        """
        data_objs = self.convert_value_to_data(value, attr)
        
        # Set the created data objects to the dataproxy and the
        # last configuration, overriding any existing elements
        self.dataproxy._set_datas(data_objs, attr)
        last_config = self.get_root_configuration().get_last_configuration()
        last_config.add_data(data_objs, container.REPLACE)
    
    def convert_data_to_value(self, data_objects, cast=True, attr=None):
        """
        Convert the given list of Data objects into a suitable value
        for this setting.
        @param data_objects: The Data object list.
        @param cast: If True, the value should be cast to its correct Python type
            (e.g. int), if False, the value should remain in the string form
            it was in the data objects.
        @param attr: The attribute name of the data. E.g. attr='data', attr='rfs'
        @return: The converted value.
        """
        if not data_objects:    return None
        
        data_obj = data_objects[-1]
        if data_obj.map:
            value = self._resolve_name_id_mapped_value(data_obj.map, cast_value=cast)
        else:
            value = data_obj.value
            if cast: value = self.get_value_cast(value, attr)
        return value
    
    def convert_value_to_data(self, value, attr=None):
        """
        Convert the given value to a list of Data objects that can be placed
        in the configuration's last layer's data section (DataContainer object).
        @param value: The value to convert.
        @param attr: The attribute name of the data. E.g. attr='data', attr='rfs'
        @return: The converted Data objects.
        """
        value = self.set_value_cast(value, attr)
        return [Data(fqr=self.fqr, value=value, attr=attr)]
    
    def del_value(self, attr=None):
        """
        Delete the topmost value for this feature.
        """
        self.dataproxy._del_value(attr)

    def get_value_cast(self, value, attr=None):
        """
        A function to perform the value type casting in get operation  
        @param value: the value to cast 
        @param attr: the attribute which is fetched from model (normally in confml either None='data' or 'rfs')
        """
        return value 
    
    def set_value_cast(self, value, attr=None):
        """
        A function to perform the value type casting in the set operation  
        @param value: the value to cast 
        @param attr: the attribute which is fetched from model (normally in confml either None='data' or 'rfs')
        """
        return value 

    def get_original_value(self, attr=None):
        """
        Get the current value of the feature
        @param attr: The attribute name of the data. E.g. attr='data', attr='rfs' 
        """
        return self.convert_data_to_value(self.dataproxy._get_datas(attr=attr), cast=False, attr=attr)

    def add_data(self, data):
        """
        Add a data value.
        @param data: A Data object  
        """
        try:
            return self.dataproxy._add_data(data)
        except AttributeError:
            self.dataproxy = self.get_default_view().get_feature(self.get_fullfqr()) 
            return self.dataproxy._add_data(data)

    def get_data(self, attr=None):
        """
        Helper function to get the topmost data value from the default view.
        @param attr: The attribute name of the data. E.g. attr='data', attr='rfs' 
        """
        try:
            return self.dataproxy._get_data(attr)
        except AttributeError:
            self.dataproxy = self.get_default_view().get_feature(self.get_fullfqr()) 
            return self.dataproxy._get_data(attr)

    def get_datas(self):
        """
        Helper function to get the data values from the default view.
        """
        try:
            return self.dataproxy._get_datas()
        except AttributeError:
            self.dataproxy = self.get_default_view().get_feature(self.get_fullfqr()) 
            return self.dataproxy._get_datas()

    def get_valueset(self):
        """
        Get the ValueSet object for this feature, that has the list of available values.
        """
        if self.get_type() == 'boolean':
            return ValueSet([True, False])
        elif self.get_type() == 'int':
            return ValueRange(0, sys.maxint)
        elif self.get_type() == 'string':
            return ValueRe('.*')
        elif self.get_type() in ('selection', 'multiSelection'):
            values = []
            for opt in self._objects(type=Option):
                v = opt.get_value()
                if v is not None: values.append(v)
            return ValueSet(values)

    def is_sequence(self):
        """ Return true if the feature is a sequence or part of a sequence """
        try:
            return self._parent.is_sequence()
        except AttributeError:
            return False

    def is_sequence_root(self):
        """ Return true if this feature is a sequence object it self """
        return False

    def get_sequence_parent(self):
        """ Try to get a FeatureSequence object for this Feature if it is found """
        try:
            return self._parent.get_sequence_parent()
        except AttributeError:
            return None

    def getdataproxy(self): 
        if self._dataproxy == None:
            self.dataproxy = self.get_default_view().get_feature(self.get_fullfqr())
        return self._dataproxy
    def setdataproxy(self, value): self._dataproxy = value
    def deldataproxy(self): self._dataproxy = None
    dataproxy = property(getdataproxy, setdataproxy, deldataproxy)
    """ Use custom OProperty to enable overriding value methods in subclasses """
    value = utils.OProperty(get_value, set_value, del_value)

    def get_column_value(self, attr=None):
        """
        Get the value of the featuresequence column
        @param ref: the reference to the column   
        @param attr: The attribute name of the data. E.g. attr='data', attr='rfs' 
        """
        """ get the feature specific data from sequence => a column of data table """
        seq_parent = self.get_sequence_parent()
        if seq_parent._has_empty_sequence_marker():
            return []
        
        coldata =  []
        colref = self.path(seq_parent)
        for row in seq_parent.data:
            feadata = row.get_feature(colref)
            coldata.append(feadata.get_value(attr))
        return coldata
    
    def get_column_original_value(self, attr=None):
        """
        Get the value of the featuresequence column
        @param feasequence: the feature sequence object
        @param ref: the reference to the column   
        @param attr: The attribute name of the data. E.g. attr='data', attr='rfs' 
        """
        """ get the feature specific data from sequence => a column of data table """
        seq_parent = self.get_sequence_parent()
        if seq_parent._has_empty_sequence_marker():
            return []
        
        coldata =  []
        colref = self.path(seq_parent)
        for row in seq_parent.data:
            feadata = row.get_feature(colref)
            coldata.append(feadata.get_original_value(attr))
        return coldata
    
    def set_column_value(self, value, attr=None):
        """
        Get the value of the featuresequence column
        @param feasequence: the feature sequence object
        @param ref: the reference to the column   
        @param value: the value to set. This must be a list instance. 
        @param attr: The attribute name of the data. E.g. attr='data', attr='rfs' 
        """
        seq_parent = self.get_sequence_parent()
        colref = self.path(seq_parent)
        
        if not isinstance(value,list): 
            raise exceptions.ConeException("The value for feature sequence '%s' column '%s' must be a list instance. Got %r" % (self.get_sequence_parent().fqr, colref, value))
        
        # Handle the special case where the sequence is marked as empty
        # with the empty sequence marker (single empty data element)
        if seq_parent._has_empty_sequence_marker():
            seqrows = []
        else:
            seqrows = seq_parent.data
        
        if len(seqrows) < len(value):
            raise exceptions.ConeException("Too many values for feature sequence '%s' column '%s'. Sequence holds only %d rows. Got %d data values in %r" % (self.get_sequence_parent().fqr, colref, len(seqrows), len(value), value))
        for i in range(0, len(value)):
            feadata = seqrows[i].get_feature(colref)
            feadata.set_value(value[i])

    def add_sequence_feature(self, feature, path=""):
        """
        Override of the add_feature function in sequence to set the sequence childs to act 
        as columns of the feature sequence
        @param feature: The Feature object to add 
        @param path: path to feature if it not added directly under parent_fea 
        """
        # modify all possible children of feature
        for fea in feature._traverse(type=Feature):
            to_sequence_feature(fea)
            
        # Finally modify and add this feature to parent_feat
        to_sequence_feature(feature)
        self._add_to_path(path, feature)
    
    def _resolve_name_id_mapped_value(self, mapping_string, cast_value=True):
        """
        Resolve the name-ID mapped value based on the given mapping string.
        @param mapping_string: The name-ID mapping string in the data element, e.g.
            "FooFeature/FooSequence[@key='123']"
        @param cast_value: If True, the resolved value will be cast to the corresponding
            Python type, otherwise the raw string representation of the value in the
            data element will be returned.
        @return: The resolved value.
        """
        def fail(msg): raise exceptions.NameIdMappingError(msg)
        
        pattern = r"^([\w/]+)\[@key='(.*)'\]$"
        m = re.match(pattern, mapping_string)
        if m is None: fail("Malformed mapping expression: %s" % mapping_string)
        
        source_seq_ref = m.group(1).replace('/', '.')
        mapping_key = m.group(2)
        
        dview = self.get_root_configuration().get_default_view()
        
        try:
            source_seq = dview.get_feature(source_seq_ref)
        except exceptions.NotFound:
            fail("Mapping source sequence '%s' does not exist" % source_seq_ref)
        
        if source_seq.type != 'sequence':
            fail("Mapping source setting '%s' is not a sequence setting" % source_seq_ref)
        if not source_seq.mapKey or not source_seq.mapValue:
            fail("Source sequence '%s' must have both mapKey and mapValue specified" % source_seq_ref)
        
        def get_subsetting(ref):
            """
            Return the sub-setting by the given mapKey or mapValue ref from the
            source sequence.
            @param ref: The reference in the format it is in the ConfML file.
                E.g. 'SubSetting', 'FileSubSetting/localPath', 'FileSubSetting/targetPath'
            """
            subsetting = source_seq.get_feature(ref.replace('/', '.'))
            # Use localPath for file and folder settings by default
            if subsetting.type in ('file', 'folder'):
                subsetting = subsetting.get_feature('localPath')
            return subsetting
        
        try:
            key_subsetting = get_subsetting(source_seq.mapKey)
        except exceptions.NotFound:
            fail("Invalid mapKey in source sequence '%s': no sub-setting with ref '%s'" % (source_seq_ref, source_seq.mapKey))
        
        
        # Get possible override for mapValue from options
        value_subsetting_ref = source_seq.mapValue
        value_subsetting_ref_overridden = False
        for opt in self._objects(type=Option):
            if not opt.map or not opt.map_value: continue
            if opt.map.replace('/', '.') == source_seq_ref:
                value_subsetting_ref = opt.map_value
                value_subsetting_ref_overridden = True
        
        try:
            value_subsetting = get_subsetting(value_subsetting_ref)
        except exceptions.NotFound:
            if value_subsetting_ref_overridden:
                fail("Invalid mapValue override in option: sub-setting '%s' does not exist under source sequence '%s'" % (value_subsetting_ref, source_seq_ref))
            else:
                fail("Invalid mapValue in source sequence '%s': no sub-setting with ref '%s'" % (source_seq_ref, value_subsetting_ref))
        
        key_list = key_subsetting.get_original_value()
        if mapping_key not in key_list:
            fail("No item-setting in source sequence '%s' matches key '%s'" % (source_seq_ref, mapping_key))
        
        if cast_value:  value_list = value_subsetting.get_value()
        else:           value_list = value_subsetting.get_original_value()
        return value_list[key_list.index(mapping_key)]

    def set_extension_attributes(self, attributes):
        self.extensionAttributes = attributes
        
    def get_extension_attributes(self):
        return self.extensionAttributes
    
    def add_extension_attribute(self, attribute):
        self.extensionAttributes.append(attribute)

class FeatureSequence(Feature):
    POLICY_REPLACE = 0
    POLICY_APPEND = 1
    POLICY_PREPEND = 2
    """
    A Feature class. Feature is the base for all Configurable items in a Configuration.
    """
    dataelem_name = '?datarows'
    template_name = '?template'
    def __init__(self, ref="", **kwargs):
        super(FeatureSequence, self).__init__(ref, **kwargs)
        self.name = kwargs.get('name', ref)
        self.type = 'sequence'
        self._templatedata = None

    def _get_policy(self, data):
        """
        parse the policy from a policy string and return a constant
        @return: POLICY_* constant
        """
        try:
            containerdata = utils.get_list(data._get_parent()._get(data.get_ref()))
            firstdata = containerdata[0]
        except AttributeError:
            firstdata = data
        
        if firstdata.policy == 'append':
            return self.POLICY_APPEND
        elif firstdata.policy == 'prefix':
            return self.POLICY_PREPEND
        elif firstdata == data:
            # otherwise the policy is either replace or undefined
            # (firstdata.policy == 'replace' or firstdata.policy == ''):
            return self.POLICY_REPLACE
        else:
            return self.POLICY_APPEND
        
    def _set_template_data(self, data=None):
        """
        Set the template of the feature sequence  
        """
        if data != None:
            self._templatedata = data
            for feaname in self.list_features():
                if self._templatedata._has(feaname):
                    self.get_feature(feaname)._templatedata = self._templatedata._get(feaname)
                else:
                    subdata = Data(ref=feaname)
                    self.get_feature(feaname)._templatedata = subdata
                    self._templatedata._add(subdata) 

    def _add_datarow(self, dataobj=None, policy=POLICY_APPEND):
        """
        Add a feature data row for a new data in this sequence 
        """
        create_sub_data_objs = True
        if dataobj == None:
            dataobj = Data(fqr=self.fqr)
        elif dataobj.attr != 'data':
            # Add data rows only for data objects (not e.g. RFS)
            return
        else:
            # If the data object is given, but it doesn't contain any child
            # elements, don't add them automatically. This is to account for the
            # case where there is only one empty data element that specifies
            # that the sequence is set to be empty
            if len(dataobj._order) == 0:
                create_sub_data_objs = False
        fea = FeatureSequenceSub(self.dataelem_name)
        rowproxy = _FeatureDataProxy(fea._name, fea)
        """ the imaginary features share the parent relation of the proxy objects """
        self.dataproxy._add(rowproxy, policy)
        fea._parent = rowproxy._parent
        rowproxy._add_data(dataobj)
        """ update the FeatureSequenceSub index from the index number of dataproxy """
        fea._index = utils.get_list(self.dataproxy._get(self.dataelem_name)).index(rowproxy)
        # Create a the subfeatures / columns for the parent feature and 
        # add a data element under each feature.
        for feaname in self.list_all_features():
            (pathto_fea, fearef) = utils.dottedref.psplit_ref(feaname)
            subfea = self.get_feature(feaname)
            cellfea = FeatureSequenceSub(fearef)
            cellfea.set_value_cast = subfea.set_value_cast
            cellfea.get_value_cast = subfea.get_value_cast
            cellfea.convert_data_to_value = subfea.convert_data_to_value
            cellfea.convert_value_to_data = subfea.convert_value_to_data
            rowproxy.add_feature(cellfea, pathto_fea)
            subproxy = rowproxy.get_feature(feaname)
            subproxy._obj._parent = subproxy._parent
            if create_sub_data_objs and not dataobj._has(feaname):
                dataobj._add_to_path(pathto_fea, Data(ref=fearef))
            subproxy._add_data(dataobj._get(feaname))
        return dataobj
    
    def _has_empty_sequence_marker(self):
        """
        Return True if the sequence setting has the empty sequence marker (a single
        empty data element), which denotes that the sequence is set to empty.
        """
        datatable = self.get_data()
        if len(datatable) == 1:
            data_elem = datatable[0].get_datas()[0]
            if len(data_elem._order) == 0:
                return True
        return False
    
    def add(self, child, policy=container.REPLACE):
        """
        A generic add function to add child objects. The function is intended to act as
        proxy function that call the correct add function based on the child objects class.
        
        Example: obj.add(Feature("test")), actually obj.add_feature(Feature("test"))
        @param child: the child object to add
        @raise IncorrectClassError: if the given class cannot be added to this object.  
        """
        if isinstance(child, Feature):
            self.add_feature(child)
        elif isinstance(child, Option):
            self._add(child)
        elif isinstance(child, Base):
            self._add(child)
        else:
            raise exceptions.IncorrectClassError("Cannot add %s to %s" % (child, self))
    
    def add_feature(self, feature, path=""):
        """
        Override of the add_feature function in sequence to set the sequence childs to act 
        as columns of the feature sequence
        @param feature: The Feature object to add 
        """
        add_sequence_feature(self, feature, path)

    def add_sequence(self, data=None, policy=POLICY_APPEND):
        """
        Add a feature data row for a new data in this sequence 
        """
        if self._has_empty_sequence_marker():
            # We currently have the empty sequence marker (single empty data
            # element), so this one that we are adding should replace it
            policy = self.POLICY_REPLACE
            
        datarow = self._add_datarow(None, policy)
        # add the new data sequence/row to the last configuration layer
        last_config = self.get_root_configuration().get_last_configuration()
        
        container_policy = {self.POLICY_REPLACE: container.REPLACE,
                            self.POLICY_APPEND:  container.APPEND,
                            self.POLICY_PREPEND: container.PREPEND}[policy]
        last_config.add_data(datarow, container_policy)
        
        # set the initial data if it is given
        rowproxy = utils.get_list(self.dataproxy._get(self.dataelem_name))[-1]
        if data != None:
            for index in range(len(data)):
                if data[index] != None:
                    rowproxy[index].set_value(data[index])

    def set_template(self, data=None):
        """
        Set the template of the feature sequence  
        """
        if data is None:
            self._templatedata = None
            return
        
        if not isinstance(data, list):
            raise TypeError('data must be a list (got %r)' % data)
        
        # Create the new template data object
        templatedata = Data(fqr=self.fqr, template=True)
        
        # Add all sub-objects to the data object
        def add_data_objects(feature, data_obj, value_list):
            refs = feature.list_features()
            if len(refs) != len(value_list):
                raise ValueError("Data value list is invalid")
            for i, ref in enumerate(refs):
                value = value_list[i]
                subfea = feature.get_feature(ref)
                if isinstance(value, list):
                    subdata = Data(ref=ref)
                    data_obj.add(subdata)
                    add_data_objects(feature.get_feature(ref), subdata, value)
                else:
                    if value is not None:
                        subdata = Data(ref=ref, value=subfea.set_value_cast(value))
                        data_obj.add(subdata)
        add_data_objects(self, templatedata, data)
        
        self._set_template_data(templatedata)
        
        # Remove any existing template data
        pconfig = self.find_parent(type=Configuration)
        dataobjs = pconfig._traverse(type=Data, filters=[lambda x: x.template and x.fqr == self.fqr])
        if dataobjs:
            for dataobj in dataobjs:
                dataobj._parent._remove(dataobj.get_fullref())
        
        # Add the template data to the parent config (beginning of the data section)
        pconfig.add_data(self._templatedata, policy=container.PREPEND)

    def get_template(self):
        """
        Add a feature data row for a new data in this sequence 
        """
        #self._set_template(None)
        # set the initial data if it is given
        if self._templatedata:
            def get_data_items(feature, data_obj):
                refs = feature.list_features()
                if refs:
                    result = []
                    for ref in refs:
                        if data_obj._has(ref):
                            result.append(get_data_items(feature.get_feature(ref), data_obj._get(ref)))
                        else:
                            result.append(None)
                    return result
                else:
                    return data_obj.value
            return get_data_items(self, self._templatedata)
        else:
            return None

    def get_data(self):
        """
        Helper function to get the topmost data value from the default view.
        """
        if self.dataproxy._has(self.dataelem_name):
            return utils.get_list(self.dataproxy._get(self.dataelem_name))
        else:
            return []

    def add_data(self, data):
        """
        Add a data value.
        @param data: A Data object  
        """
        # Skip template data adding
        if data.template:
            self._set_template_data(data)
        else:
            # Get the data index
            self._add_datarow(data, self._get_policy(data))
        return
        
    def get_value(self, attr=None):
        """
        Helper function to get the topmost data value from the default view.
        """
        if self._has_empty_sequence_marker():
            return []
        
        datatable =  self.get_data()
        rettable = []
        for row in datatable:
            rowvalues = row.value
            rettable.append(rowvalues)
        return rettable

    def get_original_value(self, attr=None):
        """
        Get the current value of the feature
        @param attr: The attribute name of the data. E.g. attr='data', attr='rfs' 
        """
        if self._has_empty_sequence_marker():
            return []
        
        datatable =  self.get_data()
        rettable = []
        for row in datatable:
            rowvalues = row.get_original_value()
            rettable.append(rowvalues)
        return rettable
    
    def set_value(self, value, attr=None):
        """
        Set the current value for this feature. Set the value on the topmost layer.
        @param value: the value to set. The value must be a two dimensional array (e.g. matrix)
        """
        if value:
            # Add the first item with replace policy
            self.add_sequence(value[0], self.POLICY_REPLACE)
            for row in value[1:]:
                self.add_sequence(row)
        else:
            # Setting the sequence to empty, so add one empty item-setting
            # to signify that
            self.add_sequence(None, self.POLICY_REPLACE)
            
            # Strip all sub-elements from the data element just created,
            # since the ConfML spec says that an empty sequence is denoted
            # by a single empty data element
            data_elem = self.get_data()[0].get_datas()[0]
            for r in list(data_elem._order):
                data_elem._remove(r)

    def is_sequence(self):
        """ Return always true from a sequence object """
        return True

    def is_sequence_root(self):
        """ Return true if this feature is a sequence object it self """
        return True

    def get_column_features(self):
        """ Return a list of sequence subfeature, which are the columns of the sequence """
        columns = []
        for subref in self.list_features():
            columns.append(self.get_feature(subref))
        return columns

    def get_sequence_parent(self):
        """ Return this object as a sequence parent """
        return self

    value = property(get_value, set_value)
    data = property(get_data)


def add_sequence_feature(parent_feature, feature, path=""):
    """
    Override of the add_feature function in sequence to set the sequence childs to act 
    as columns of the feature sequence
    @param parent_feature: The parent feature where the feature object is added 
    @param feature: The Feature object to add 
    @param path: path to feature if it not added directly under parent_fea 
    """
    # modify all possible children of feature
    for fea in feature._traverse(type=Feature):
        to_sequence_feature(fea)
        
    # Finally modify and add this feature to parent_feat
    to_sequence_feature(feature)
    parent_feature._add_to_path(path, feature)

def to_sequence_feature(feature):
    """
    modify a Feature object to sequence feature that will return column like data from a sequence.
    @param feature: The Feature object for which is modified.
    """
    feature.get_value = feature.get_column_value 
    feature.get_original_value = feature.get_column_original_value
    feature.set_value = feature.set_column_value
    feature.add_feature = feature.add_sequence_feature

def get_column_value(feasequence, ref, attr=None):
    """
    Get the value of the featuresequence column
    @param feasequence: the feature sequence object
    @param ref: the reference to the column   
    @param attr: The attribute name of the data. E.g. attr='data', attr='rfs' 
    """
    """ get the feature specific data from sequence => a column of data table """
    coldata =  []
    for row in feasequence.data:
        feadata = row.get_feature(ref)
        coldata.append(feadata.get_value(attr))
    return coldata

def get_column_original_value(feasequence, ref, attr=None):
    """
    Get the value of the featuresequence column
    @param feasequence: the feature sequence object
    @param ref: the reference to the column   
    @param attr: The attribute name of the data. E.g. attr='data', attr='rfs' 
    """
    """ get the feature specific data from sequence => a column of data table """
    coldata =  []
    for row in feasequence.data:
        feadata = row.get_feature(ref)
        coldata.append(feadata.get_original_value(attr))
    return coldata

def set_column_value(feasequence, ref, value, attr=None):
    """
    Get the value of the featuresequence column
    @param feasequence: the feature sequence object
    @param ref: the reference to the column   
    @param value: the value to set. This must be a list instance. 
    @param attr: The attribute name of the data. E.g. attr='data', attr='rfs' 
    """
    if not isinstance(value,list): 
        raise exceptions.ConeException("The value for feature sequence '%s' column '%s' must be a list instance. Got %r" % (feasequence.fqr, ref, value))
    seqrows = feasequence.data
    if len(seqrows) < len(value): 
        raise exceptions.ConeException("Too many values for feature sequence '%s' column '%s'. Sequence holds only %d rows. Got %d data values in %r" % (feasequence.fqr, ref, len(seqrows), len(value), value))
    for i in range(0, len(value)):
        feadata = seqrows[i].get_feature(ref)
        feadata.set_value(value[i])

class FeatureSequenceCell(Feature):
    """
    A Feature class. Feature is the base for all Configurable items in a Configuration.
    """
    def __init__(self, ref="", **kwargs):
        super(FeatureSequenceCell, self).__init__(ref)
        self.name = kwargs.get('name', ref)
        self.type = 'seqcell'
 
    def get_value(self, attr=None):
        """
        Get the current value of the feature
        @param attr: The attribute name of the data. E.g. attr='data', attr='rfs' 
        """
        return self.dataproxy._get_value(attr)

    def set_value(self, value):
        """
        Set the current value for this feature. Set the value on the topmost layer.
        @param value: the value to set
        """
        # The sequence cell only updates the latest value in the proxy  
        self.dataproxy.get_data().set_value(value)

    value = property(get_value, set_value)

class FeatureSequenceSub(Feature):
    """
    A Feature class. Feature is the base for all Configurable items in a Configuration.
    """
    def __init__(self, ref="", **kwargs):
        super(FeatureSequenceSub, self).__init__(ref)
        self.name = kwargs.get('name', ref)
        self.type = 'subseq'
        self._index = 0

    def get_index(self):
        """
        @return : the index of the data element for sequential data defined inside the same configuration.
        0 for normal data.
        """
        return self._index

    def set_value(self, value, attr=None):
        """
        Set the current value for this sequence row.
        @param value: the value row to set
        """
        if utils.is_list(value):
            for subindex in range(0, len(value)):
                self.dataproxy[subindex].get_data().set_value(value[subindex])
        else:
            data_objs = self.convert_value_to_data(value)
            data_object_where_to_add = self._parent._get_data()
            
            self.dataproxy._set_datas(data_objs, attr)
            data_object_where_to_add._add(data_objs, container.REPLACE)

    def get_value(self, attr=None):
        """
        Set the current value for this feature. Set the value on the topmost layer.
        @param value: the value to set
        """
        # Handle empty sequences
        if self.get_sequence_parent()._has_empty_sequence_marker():
            return []
        
        # The sequence cell only updates the latest value in the proxy
        childdatas = self.dataproxy._objects()
        if len(childdatas) > 0:
            return [subdata.value for subdata in childdatas]
        else: 
            return super(FeatureSequenceSub,self).get_value(attr)

    def get_original_value(self, attr=None):
        """
        Get the current value of the feature
        @param attr: The attribute name of the data. E.g. attr='data', attr='rfs' 
        """
        # Handle empty sequences
        if self.get_sequence_parent()._has_empty_sequence_marker():
            return []
        
        childdatas = self.dataproxy._objects()
        if len(childdatas) > 0:
            return [subdata.get_original_value() for subdata in childdatas]
        else:
            return self.dataproxy._get_value(attr)
        
    value = property(get_value, set_value)


class FeatureLink(Base):
    """
    A _FeatureProxy class. _FeatureProxy is the object that is added to View as a 
    link to the actual Feature object. 
    """
    """ class variable for defining the override attributes"""
    override_attributes = ['name']
    ref_prefix = 'link_'
    PROXYREF_PREFIX = 'proxy_'
    
    def __init__(self, ref="", **kwargs):
        # Store the fully qualified reference to this object
        self.link = kwargs.get('link', ref)
        self.name = kwargs.get('name', None)
        ref = self.get_featurelink_ref(self.link)
        # the reference of this particular object
        super(FeatureLink, self).__init__(ref, **kwargs)
        self._obj = None
        self._populated = False

    def add(self, child, policy=container.REPLACE):
        """
        Add an override to enable adding any override attribute to a featurelink object.
        
        A generic add function to add child objects. The function is intended to act as
        proxy function that call the correct add function based on the child objects class.
        
        Example: obj.add(Feature("test")), actually obj.add_feature(Feature("test"))
        @param child: the child object to add
        @raise IncorrectClassError: if the given class cannot be added to this object.  
        """
        if isinstance(child, Base):
            self._add(child, policy)
        else:
            raise exceptions.IncorrectClassError("Cannot add %s to %s" % (child, self))

    def get_name(self):
        """
        Return the name of the featurelink
        """
        return self.name

    def set_name(self, name):
        """
        Set the name
        """
        self.name = name

    @property
    def fqr(self):
        return self.link

    def populate(self):
        """
        Populate or fetch the link to the actual feature for this featureproxy.
        This method fetches the feature to the _obj member variable and populates also 
        subfeatures. 
        """
        try:
            if not self._populated:
                feas = self.get_default_view().get_features(self.link)
                # get the non wildcard part of ref
                static_ref = utils.dottedref.get_static_ref(self.link)
                # add the found features to the parent
                for fea in feas:
                    override_attrs = {}
                    # override the FeatureProxy object with exactly same reference 
                    # (in feat/* case dont override the children features)
                    if fea.fqr == static_ref:
                        override_attrs = self.get_attributes()
                    feature = fea._obj
                    proxy_ref = self.get_featureproxy_ref(feature.fqr)
                    proxy = _FeatureProxy(proxy_ref, feature, **override_attrs)
                    self._get_parent()._add(proxy)
                    
        except exceptions.NotFound, e:
                parent_view = self._find_parent_or_default(type=View)
                view_name = parent_view.get_name()
                logging.getLogger('cone').info("Warning: Feature '%s' in view '%s' not found." % (self.link, view_name))

    def get_attributes(self):
        """
        Returns a list of FeatureLink attributes that override settings of the original feature.
        @return: a dictionary of attribute key : value pairs.
        """
        attrs = {}
        for attr in self.override_attributes:
            # try to get the attribute from this object
            # and set it to the attribute list if it not None
            try:
                value = getattr(self, attr)
                if value != None: attrs[attr] = value
            except AttributeError:
                pass
        return attrs

    @classmethod
    def get_featurelink_ref(cls, ref):
        """
        return a featurelink ref from a feature ref. 
        This is needed to make the featurelink object refs unique in a container
        that has Features. 
        """
        return cls.ref_prefix + ref.replace('.', '_').replace('/','_')
    
    @classmethod
    def get_featureproxy_ref(cls, ref):
        """
        Return a ref for a given setting fqr to be used under a group.
        This is needed to make the featureproxy object refs unique in a container
        that has Features. 
        """
        return cls.PROXYREF_PREFIX + ref.replace('.', '_').replace('/','_')

class _FeatureProxy(container.ObjectProxyContainer, Base):
    """
    A _FeatureProxy class. _FeatureProxy is the object that is added to View as a 
    link to the actual Feature object. 
    """
    def __init__(self, ref="", obj=None, **kwargs):
        container.ObjectProxyContainer.__init__(self, obj, ref)
        Base.__init__(self, ref, **kwargs)
        self.support_data = False
        
    def __getattr__(self, name):
        """
        First check if the requested attr is a children then 
        direct all not found attribute calls to the sub object getattr
        """
        try:
            return self.__dict__['_children'][name] 
        except KeyError:
            return getattr(self._obj, name)

    def __getitem__(self, index):
        return self._objects()[index]

    def __setitem__(self, index, value):
        raise exceptions.NotSupportedException()

    def __delitem__(self, index):
        item = self.__getitem__(index)
        return self._remove(item.get_ref())

    def __len__(self):
        return len(self._order)

    def _supported_type(self, obj):
        if isinstance(obj, _FeatureProxy):
            return True
        else:
            return False

    def _default_object(self, name):
        return Group(name)

    def _set_parent(self, newparent):
        """
        @param newparent:  The new parent object
        @return: None
        """
        self._parent = newparent

    def get_proxied_obj(self):
        """
        @return: Returns proxied object.
        """
        return self._obj

    def add_feature(self, feature, path=""):
        """
        """
        if not isinstance(feature, Feature):
            raise exceptions.IncorrectClassError("add_feature requires instance of Feature!! Given %s" % feature)
        if not self.support_data:
            self._add_to_path(path, _FeatureProxy(feature._name, feature))
        else:
            self._add_to_path(path, _FeatureDataProxy(feature._name, feature))

    def remove_feature(self, ref):
        """
        remove a given feature from this view by reference. 
        @param ref: 
        """
        self._remove(ref)

    def get_feature(self, path):
        """
        @param path: The path (ref) to the given feature 
        """
        return self._get(path)

    def list_features(self):
        """
        Return a array of all Feature children references under this object.
        """
        return self._list()

    def list_all_features(self):
        """
        Return a array of all Feature children references under this object.
        """
        return [fea._path(self) for fea in self._traverse(type=_FeatureProxy)]

    def populate(self):
        """
        Dummy implementation of populate
        """
        pass

    def has_attribute(self, name):
        """
        Perform a check whether an attribute with given name is stored inside the 
        _FeatureProxy. The check does not extend to the proxied (_obj) insanses or 
        children of this proxy.
        
        @return: True when an attribute is a real attribute in this _FeatureProxy object. 
        """
        return self.__dict__.has_key(name)

    def get_option(self, ref):
        """
        @param name: The option reference of the option (as returned by list_options()) 
        """
        real_ref = 'opt_' + ref
        for op in self.options.values():
            if op.ref == real_ref:
                return op
        else:
            
            obj = self.get_proxied_obj()._get(real_ref)
            if not isinstance(obj, Option):
                raise TypeError('Object %r is not an instance of Option (%r instead)' % (real_ref, type(obj)))
            return obj

    def list_options(self):
        """
        Return a array of all Option children references under this object.
        """
        opts = self.get_proxied_obj().list_options()
        
        for opt in self.options:
            opts.append(self.options[opt].ref[4:])
        
        return opts

    def get_property(self, ref):
        """
        @param name: The property reference of the property (as returned by list_properties()) 
        """
        for prop in self.properties.values():
            if prop.ref == Property.to_propertyref(ref):
                return prop
        else:
            obj = self.get_proxied_obj()._get(Property.to_propertyref(ref))
            return obj

    def list_properties(self):
        """
        Return a array of all Property children references under this object.
        """
        props = self.get_proxied_obj().list_properties()
        
        for pr in self.properties:
            props.append(Property.to_normref(self.properties[pr].ref))
        
        return props

    
class _FeatureDataProxy(_FeatureProxy):
    """
    A Feature class. Feature is the base for all Configurable items in a Configuration.
    """
    DEFAULT_KEY = 'data'
    def __init__(self, ref="", obj=None, **kwargs):
        # Initialize _obj to None, because __getattr__(), __setattr__()
        # and __delattr__() access it.
        # Note that we cannot use self._obj = None here, since that would
        # invoke __setattr__(), causing a kind of a chicken-and-egg problem
        object.__setattr__(self, '_obj', None)
        
        super(_FeatureDataProxy, self).__init__(ref, obj)
        self.support_data = True
        """ Create the data container of all types of data. Add the key for the default key. """
        
        self.defaultkey = _FeatureDataProxy.DEFAULT_KEY
        self.datas = {self.defaultkey : []}

    def __getattr__(self, name):
        """
        """
        if object.__getattribute__(self, '_obj') is not None:
            self.get_proxied_obj().dataproxy = self
        
        if name in Feature.PROPERTIES:
            return getattr(self.get_proxied_obj(), name)
        else:
            return super(_FeatureDataProxy, self).__getattr__(name)
    
    def __setattr__(self, name, value):
        """
        """
        if object.__getattribute__(self, '_obj') is not None:
            self.get_proxied_obj().dataproxy = self
            
        if name in Feature.PROPERTIES:
            return setattr(self.get_proxied_obj(), name, value)
        else:
            super(_FeatureDataProxy, self).__setattr__(name, value)

    def __delattr__(self, name):
        """
        """
        if name in Feature.PROPERTIES:
            return delattr(self.get_proxied_obj(), name)
        else:
            return super(_FeatureDataProxy, self).__delattr__(name)

    def _add_data(self, data):
        """
        Add a data value or a list of data values.
        @param data: A Data object  
        """
        if isinstance(data, list):
            for d in data: self._add_data(d)
            return
        
        try:
            self.datas[data.attr].append(data)
        except KeyError:
            """ Create a list object for missing attribute """ 
            self.datas[data.attr] = []
            self.datas[data.attr].append(data)

    def _get_data(self, attr=None):
        """
        Get the data value. in sequence setting cases returns an array of data.
        """
        dataattr = attr or self.defaultkey
        try:
            if len(self.datas[dataattr]) > 0:
                return self.datas[dataattr][-1]
            else:
                return None
        except KeyError:
            """ return None for missing attribute """ 
            return None

    def _get_datas(self, attr=None):
        """
        Get the entire data array.
        """
        dataattr = attr or self.defaultkey
        return self.datas.get(dataattr, [])
    
    def _set_datas(self, datas, attr=None):
        """
        Set the entire data array.
        """
        dataattr = attr or self.defaultkey
        self.datas[dataattr] = list(datas)

    def _get_value(self, attr=None):
        """
        Get the topmost data value.
        """
        if self._get_data(attr):
            return self._get_data(attr).get_value()
        else:
            return None
    
    def _set_value(self, datavalue, attr=None):
        """
        Set the value for the feature the last configuration in the current hierarchy
        @param value: The value for the feature.
        @return: The created Data object.  
        """
        # Make sure that data value exists only once the the last configuration layer
        # So if last_data exists on last layer, update the value of that data element.
        # otherwise create a new data elem to the topmost layer
        dataobj = self._get_data(attr)
        last_config = self.get_root_configuration().get_last_configuration()
        if dataobj and dataobj.find_parent(type=Configuration) == last_config:
            dataobj.set_value(datavalue)
        else:
            dataobj = Data(fqr=self.fqr, value=datavalue, attr=attr)
            last_config.add_data(dataobj)
            self._add_data(dataobj)
        return dataobj

    def _del_value(self, attr=None):
        """
        Remove the 
        """
        data = self._get_data(attr)
        if data:
            dataattr = attr or self.defaultkey
            parentconfig = data.find_parent(type=Configuration)
            if parentconfig:
                parentconfig.remove_data(data.get_fullfqr())
            del self.datas[dataattr][-1]

    def _get_values(self, attr=None):
        """
        Get the topmost data value.
        """
        dataattr = attr or self.defaultkey
        return [dataelem.get_value() for dataelem in self.datas[dataattr]]


class DataBase(Base):
    def __init__(self, ref="", **kwargs):
        super(DataBase, self).__init__(ref, **kwargs)

    def _supported_type(self, obj):
        if isinstance(obj, (DataContainer, DataBase)):
            return True
        else:
            return False

    def _default_object(self, name):
        return Data(ref=name)

    def count(self):
        return len(self._objects())

    def add(self, child, policy=container.REPLACE):
        """
        A generic add function to add child objects. The function is intended to act as
        proxy function that call the correct add function based on the child objects class.
        
        Example: obj.add(Feature("test")), actually obj.add_feature(Feature("test"))
        @param child: the child object to add
        @raise IncorrectClassError: if the given class cannot be added to this object.  
        """
        if isinstance(child, (Data)):
                self._add(child, container.APPEND)
        else:
            raise exceptions.IncorrectClassError("Cannot add %s object to %s" % (child, self))


class DataContainer(DataBase):
    def __init__(self, ref="", **kwargs):
        super(DataContainer, self).__init__(ref, **kwargs)


class Data(DataBase):
    """
    The data element can contain any data setting for a feature. The data element can be 
    a value definition for any type of data. It basically just links some data to a feature. 
    The default Data attribute is 'data', but it can be any string. For example current use case 
    is 'rfs'.
    """
    def __init__(self, **kwargs):
        """
        @param ref: the reference to the feature. E.g. foo
        @param fqr: the full reference to the feature. E.g. 'foo.bar' 
        @param value: the value of the data
        @param attr: the attribute which the Data object defines. e.g. default is 'data'. But could be 
        for example 'rfs'
        """
        name = kwargs.get('ref', '')
        self.fearef = kwargs.get('fqr', None)
        if self.fearef:
            (namespace, name) = utils.dottedref.psplit_ref(self.fearef)
        super(Data, self).__init__(name)
        self.value  = kwargs.get('value', None)
        self.attr   = kwargs.get('attr') or 'data'
        self.policy = kwargs.get('policy', '')
        self.template = kwargs.get('template', False)
        self.map    = kwargs.get('map')
        self.empty  = kwargs.get('empty', False)
        self.lineno = None

    def __setstate__(self, state):
        super(Data, self).__setstate__(state)
        self.value = state.get('value', None)
        self.attr = state.get('attr', None)
        self.policy = state.get('policy', '')
        self.map = state.get('map', None)
        self.template = state.get('template', False)
        self.lineno = state.get('lineno', None)
        self.fearef = state.get('fearef', None)

    def get_fearef(self):
        if self.fearef:
            return self.fearef
        else:
            return self.fqr

    def get_value(self):
        return self.value

    def get_map(self):
        return self.map

    def set_map(self, map):
        self.map = map
        if self.value:
            #Either value or mapping can be defined. Not both.
            self.value = None

    def set_value(self, value):
        self.value = value
        if self.map:
            #Either value or mapping can be defined. Not both.
            self.map = None

    def get_policy(self): return self._policy
    def set_policy(self, value): self._policy = value
    def del_policy(self):  self._policy = None
    policy = property(get_policy, set_policy, del_policy)


class ValueSet(set):
    """
    A value set object to indicate a set of possible values for a feature. 
    e.g. A boolean feature ValueSet([True, False])
    """
    def __init__(self, initial_set=None):
        super(ValueSet, self).__init__(initial_set or [])


class ValueRange(object):
    """
    """
    def __init__(self, fromvalue, tovalue, step=1):
        self.fromvalue = fromvalue
        self.tovalue = tovalue
        self.step = step

    def __contains__(self, value):
        return self.fromvalue <= value and value <= self.tovalue and (value-self.fromvalue) % self.step == 0


class ValueRe(object):
    """
    """
    def __init__(self, regexp):
        self.regexp = re.compile(regexp)

    def __contains__(self, value):
        if isinstance(value, str):
            return self.regexp.match(value)
        else:
            return False
    

class Property(Base):
    """
    Confml property class
    """
    def __init__(self, **kwargs):
        """
        @param name=str: name string (mandatory)
        @param value=str: value for the property, string 
        @param unit=str: unit of the property
        """
        if kwargs.get('name',None) == None:
            raise ValueError("Property name cannot be None!")
        super(Property,self).__init__(Property.to_propertyref(kwargs.get('name',None)))
        self.name = kwargs.get('name',None)
        self.value = kwargs.get('value',None)
        self.unit = kwargs.get('unit',None)

    @classmethod
    def to_propertyref(cls, name):
        """ 
        @param name: name of the property 
        @return: A property reference.
        """
        if name is not None:
            return "property_%s" % name
        else:
            raise ValueError("Property name cannot be None!")
    
    @classmethod
    def to_normref(cls, ref):
        """
        @param ref: a property reference 
        @return: normalized property reference
        """
        return ref[9:]

    def get_name(self):
        return self.name

    def get_value(self):
        return self.value

    def get_unit(self):
        return self.unit

class Option(Base):
    """
    Confml option class.
    """
    def __init__(self, name, value, **kwargs):
        super(Option, self).__init__(Option.to_optref(value, kwargs.get('map', None)))
        self.name = name
        self.value = value
        self.map = kwargs.get('map', None)
        self.relevant = kwargs.get('relevant', None)
        self.map_value = kwargs.get('map_value', None)
        self.display_name = kwargs.get('display_name', None)
        self.extensionAttributes = []

    @classmethod
    def to_optref(cls, value, map):
        """ 
        @return: An option reference converted from value or map, depending
            on which one is not None.
        """
        if value is not None:
            return "opt_value_%s" % value.replace('.', '').replace('/', '').replace(' ', '')
        elif map is not None:
            return "opt_map_%s" % map.replace('.', '').replace('/', '').replace(' ', '')
        else:
            raise ValueError("Both value and map are None!")

    def get_name(self):
        return self.name

    def get_value(self):
        return self.value

    def __cmp__(self, other):
        try:
            ref = getattr(other, 'ref')
        except AttributeError:
            ref = other
        if self.ref < ref:
            return -1
        elif self.ref == ref:
            return 0
        else:
            return 1

    def set_extension_attributes(self, attributes):
        self.extensionAttributes = attributes
        
    def get_extension_attributes(self):
        return self.extensionAttributes
    
    def add_extension_attribute(self, attribute):
        self.extensionAttributes.append(attribute)

class Storage(object):
    """
    A general base class for all storage type classes
    """
    """ File open modes """ 
    MODE_UNKNOWN= -1
    MODE_READ   = 1
    MODE_WRITE  = 2
    MODE_APPEND = 3
    MODE_DELETE = 4

    def __init__(self, path, mode=''):
        """
        @param path: the reference to the root of the storage.
        """
        self.rootpath = path
        self.curpath = ""
        self.container = True
        self.__opened_res__ = {}
        self.mode = mode
        self.cpath_stack = []
        
    def __opened__(self, res):
        """
        Internal function to add a newly opened Resource object to the list of open resources.
        @param res: The resource object 
        """
        if self.__opened_res__.has_key(res.path):
            self.__opened_res__[res.path].append(res)
        else:
            self.__opened_res__[res.path] = [res]

    def __closed__(self, res):
        """
        Internal function to remove a Resource object from the list of open resources.
        @param res: The resource object to remove
        @raise StorageException if the given resource object is not found: 
        """
        try:
            self.__opened_res__[res.path].remove(res)
            if len(self.__opened_res__[res.path]) == 0:
                del self.__opened_res__[res.path]
        except KeyError, e:
            raise exceptions.StorageException("No such %s open resource! %s" % (res, e))

    def __has_open__(self, ref):
        """
        Internal function to find out if any Resource objects are open from given ref.
        @param ref: The resource ref
        @return: True if resources found. Otherwise False.   
        """
        return self.__opened_res__.has_key(ref)

    def __get_open__(self, path):
        """
        Internal function to get all resource opened on a certain ref .
        @param ref: The resource ref
        @return: A list of open resources. Empty list if nothing is found   
        """
        if self.__has_open__(path):
            # return a copy of currently open resources
            return self.__opened_res__[path][:]
        else:
            return []

    def __has_resource__(self, res):
        """
        Internal function to find out if the given Resource objects is open in this storage.
        @param ref: The resource object
        @return: True if resources found. Otherwise False.   
        """
        try:
            res = self.__opened_res__[res.path].index(res)
            return True
        except KeyError, e:
            return False

    @classmethod
    def open(cls,path, mode="r", **kwargs):
        """
        Class method for opening an instance of Storage
        @param path: path to storage, which will determine what type of storage is initiated. 
        """
        # import all storage instances
        from cone.storage import storages
        for storagename in storages:
            storagemodule = 'cone.storage.'+storagename
            module = __import__(storagemodule)
        for storage_class in utils.all_subclasses(Storage):
            if storage_class.supported_storage(path):
                if hasattr(storage_class, '__open__'):
                    return storage_class.__open__(path, mode, **kwargs)
                else:
                    return storage_class(path, mode, **kwargs)
        
        obj = Storage(path)
        return obj

    @classmethod
    def supported_storage(cls, path):
        """
        Class method for determing if the given clas supports a storage by given path. 
        E.g. foo.zip, foo.cpd, foo/bar, http://foo.com/
        @param path:
        @return: Boolean value. True if the storage of the path is supported. False if not.  
        """
        return False

    def set_path(self, path):
        """
        """
        self.rootpath = path

    def get_path(self):
        """
        """
        return self.rootpath

    def push(self, path):
        """
        Set the current path under the Storage to the given path and push the possible existing path to a stack. 
        The current path can be reverted with pop method.
        
        @return: None 
        @param path: The path which is set as current path.
        """
        self.cpath_stack.append(self.curpath)
        self.curpath = path

    def pop(self):
        """
        Pop a path from path stack and set the current path to the popped element. The path can be pushed to the 
        current path stack with push. 
        
        NOTE! if the pop is called when the current path stack is empty, the path will just remain is empty path 
        keeping the active path in the storages root path. 
        
        @return: The new path.
        """
        try:
            path = self.cpath_stack.pop()
            self.curpath = path
        except IndexError:
            pass
        return self.curpath

    def set_current_path(self, path):
        """
        @param path: the current path under the Storage. 
        """
        self.curpath = utils.resourceref.remove_end_slash(utils.resourceref.remove_begin_slash(path))

    def get_current_path(self):
        """
        get the current path under the Storage. 
        """
        return self.curpath

    def close(self):
        """
        Close the repository, which will save and close all open resources.  
        """
        for openref in self.__opened_res__.keys():
            for res in self.__get_open__(openref):
                self.close_resource(res)

    def save(self):
        """
        Flush changes from all resources to the repository.  
        """        
        for openref in self.__opened_res__.keys():
            for res in self.__get_open__(openref):
                self.save_resource(res)

    def open_resource(self, path, mode="r"):
        """
        Open the given resource and return a File object.
        @param path : reference to the resource 
        @param mode : the mode in which to open. Can be one of r = read, w = write, a = append.
        raises a NotResource exception if the ref item is not a resource.
        """  
        raise exceptions.NotSupportedException()

    def delete_resource(self, path):
        """
        Delete the given resource from storage
        @param path: reference to the resource 
        raises a NotSupportedException exception if delete operation is not supported by the storage
        """  
        raise exceptions.NotSupportedException()

    def close_resource(self, path):
        """
        Close a given resource instance. Normally this is called by the Resource object 
        in its own close.
        @param path the reference to the resource to close. 
        """
        raise exceptions.NotSupportedException()

    def is_resource(self, path):
        """
        Return true if the ref is a resource
        @param ref : reference to path where resources are searched
        """
        raise exceptions.NotSupportedException()

    def list_resources(self, path, **kwargs):
        """
        find the resources under certain ref/path 
        @param ref : reference to path where resources are searched
        @param recurse : defines whether to return resources directly under the path or does the listing recurse to subfolders. 
        Default value is False. Set to True to enable recursion.
        """  
        return []

    def import_resources(self, paths, storage):
        """
        import resources from a list of resources to this storage
        @param paths : a list of Resourse objects.
        @param storage : the external storage from which files are imported.
        """  
        raise exceptions.NotSupportedException()

    def export_resources(self, paths, storage):
        """
        export resources from this storage based on a list of reference to this storage
        @param path : a list of resource paths in this storage (references).
        @param storage : the external storage where to export.
        """  
        raise exceptions.NotSupportedException()

    def save_resource(self, path):
        """
        Flush the changes of a given resource instance. Normally this is called by the Resource object 
        in its own save.
        @param ref the reference to the resource to close. 
        """
        raise exceptions.NotSupportedException()

    def create_folder(self, path):
        """
        Create a folder entry to a path
        @param path : path to the folder
        """  
        raise exceptions.NotSupportedException()

    def delete_folder(self, path):
        """
        Delete a folder entry from a path. The path must be empty.
        @param path : path to the folder
        """  
        raise exceptions.NotSupportedException()

    def is_folder(self, path):
        """
        Check if the given path is an existing folder in the storage
        @param path : path to the folder
        """
        raise exceptions.NotSupportedException()

    def get_mode(self, mode_str):
        if mode_str.find("w") != -1: 
            return self.MODE_WRITE
        elif mode_str.find("r") != -1:
            return self.MODE_READ
        elif mode_str.find("a") != -1:
            return self.MODE_APPEND
        elif mode_str.find("d") != -1:
            return self.MODE_DELETE
        else:
            return self.MODE_UNKNOWN

    def unload(self, path, object):
        """
        Dump a given object to the storage 
        @param object: The object to dump to the storage, which is expected to be an instance 
        of Base class.
        @param path: The reference where to store the object 
        @param object: The object instance to dump 
        @raise StorageException: if the given object cannot be dumped to this storage 
        """
        raise exceptions.NotSupportedException()

    def load(self, path):
        """
        Load an object from a reference.
        @param path: The reference where to load the object 
        @raise StorageException: if the given object cannot be loaded as an object from this storage 
        """
        raise exceptions.NotSupportedException()

    path = property(get_path, set_path)

class Resource(object):
    STATE_OPEN = 0
    STATE_CLOSE = 1
    def __init__(self, storage, path, mode=Storage.MODE_READ):
        self.storage = storage
        self.path = path
        self.mode = mode
        self.state = Resource.STATE_OPEN
        self.content_info = None

    def get_path(self):
        return self.path

    def close(self):
        """
        Close the resource. 
        Note1: the resource object cannot be accessed anymore after it has been closed.
        Note2: the changes are not automatically saved. The save operation must be explicitly called, 
        to save data. 
        """
        self.storage.close_resource(self.path)
        self.state = Resource.STATE_OPEN

    def read(self, bytes=0):
        """
        Read data.
        """
        raise exceptions.NotSupportedException()

    def write(self, string):
        """
        Write data.
        """
        raise exceptions.NotSupportedException()

    def truncate(self, size=0):
        """
        Trunkate this resource data to the given size.
        @param size: The size to trunkate. Default value is zero, which make the resource empty. 
        """
        raise exceptions.NotSupportedException()

    def save(self, size=0):
        """
        Save all changes to data to storage.
        """
        raise exceptions.NotSupportedException()

    def get_mode(self):
        return self.storage.get_mode(self.mode)
    
    def get_size(self):
        """
        Return the size of this resource in bytes.
        
        Note that this does not work in write mode.
        @return: The resource size in bytes:
        @raise exceptions.StorageException: The resource was opened in write mode.
        """
        raise exceptions.NotSupportedException()
    
    def get_content_info(self):
        """
        Return the ContentInfo class that contains content information about
        resource.
        """
        raise exceptions.NotSupportedException()
        
class ContentInfo(object):
    """
    A ContentInfo object is used to describe content of Resource. 
    """
    logger = logging.getLogger('cone.contentinfo')

    
    def __init__(self, mimetype, mimesubtype):
        #: MIME Media type (http://www.iana.org/assignments/media-types/)
        #: as a string. E.g. 'image' or 'application'
        self.mimetype = mimetype
        #: MIME Media subtype as a string. E.g. 'svg+xml' or 'bmp'.
        self.mimesubtype = mimesubtype
    
    @property
    def content_type(self):
        """
        Returns MIME Media type (http://www.iana.org/assignments/media-types/) 
        and subtype as a string. E.g. 'image/bmp'. 
        """
        return self.mimetype + '/' + self.mimesubtype

class ImageContentInfo(ContentInfo):
    
    """
    A ImageContentInfo object is used to describe content of image Resources.
    """
    def __init__(self):
        ContentInfo.__init__(self, 'image', '')

class BmpImageContentInfo(ImageContentInfo):
    """
    A BmpImageContentInfo object is used to describe content of bmp image 
    Resources.
    """
    
    _BMP_BITS_PER_PIXEL_OFFSET_ = int('0x1C', 16)
    
    def __init__(self, resource, data):
        ContentInfo.__init__(self, 'image', 'bmp')
        
        #: Color depth as bits per pixel.
        self.color_depth = None
        if (resource != None):
            try:
                self.color_depth = ord(data[self._BMP_BITS_PER_PIXEL_OFFSET_])
            except Exception, e:
                self.logger.warning("Invalid BMP-file: %s" % resource.get_path())
        

class currentdir(object):
    def __init__(self, storage, curdir):
        self.storage = storage
        # make sure that the curdir does not contain path prefix
        self.curdir = curdir.lstrip('/')

    def __enter__(self):
        self.storage.push(self.curdir)

    def __exit__(self, type, value, tb):
        self.storage.pop()


class Folder(object):
    """
    A Folder object is a subfolder of a Storage, offering access to part of the Storages resources.
    """
    def __init__(self, storage, path, **kwargs):
        """
        Create a layer folder to the storage if it does not exist.
        """
        self.curpath = path
        self.storage = storage

    def set_path(self, path):
        """
        """
        self.curpath = path

    def get_path(self):
        """
        """
        return self.curpath

    def set_current_path(self, path):
        """
        @param path: the current path under the Storage. 
        """
        self.curpath = utils.resourceref.remove_end_slash(utils.resourceref.remove_begin_slash(path))

    def get_current_path(self):
        """
        get the current path under the Storage. 
        """
        return self.curpath

    def close(self):
        """
        Close the repository, which will save and close all open resources.  
        """
        self.storage.close()

    def save(self):
        """
        Flush changes from all resources to the repository.  
        """        
        return self.storage.save()

    def open_resource(self, path, mode="r"):
        """
        Open the given resource and return a File object.
        @param path : reference to the resource 
        @param mode : the mode in which to open. Can be one of r = read, w = write, a = append.
        raises a NotResource exception if the ref item is not a resource.
        """  
        with currentdir(self.storage, self.curpath):
            res = self.storage.open_resource(path, mode)
            return res
        
    def delete_resource(self, path):
        """
        Delete the given resource from storage
        @param path: reference to the resource 
        raises a NotSupportedException exception if delete operation is not supported by the storage
        """  
        with currentdir(self.storage, self.curpath):
            res = self.storage.delete_resource(path)
            return res

    def close_resource(self, path):
        """
        Close a given resource instance. Normally this is called by the Resource object 
        in its own close.
        @param path the reference to the resource to close. 
        """
        with currentdir(self.storage, self.curpath):
            res = self.storage.close_resource(path)
            return res

    def is_resource(self, path):
        """
        Return true if the ref is a resource
        @param ref : reference to path where resources are searched
        """
        with currentdir(self.storage, self.curpath):
            res = self.storage.is_resource(path)
            return res

    def list_resources(self, path, **kwargs):
        """
        find the resources under certain ref/path 
        @param ref : reference to path where resources are searched
        @param recurse : defines whether to return resources directly under the path or does the listing recurse to subfolders. 
        Default value is False. Set to True to enable recursion.
        """  
        with currentdir(self.storage, self.curpath):
            res = self.storage.list_resources(path, **kwargs)
            return res

    def import_resources(self, paths, storage):
        """
        import resources from a list of resources to this storage
        @param paths : a list of Resourse objects.
        @param storage : the external storage from which files are imported.
        """  
        with currentdir(self.storage, self.curpath):
            res = self.storage.import_resources(paths, storage)
            return res

    def export_resources(self, paths, storage):
        """
        export resources from this storage based on a list of reference to this storage
        @param path : a list of resource paths in this storage (references).
        @param storage : the external storage where to export.
        """  
        with currentdir(self.storage, self.curpath):
            res = self.storage.export_resources(paths, storage)
            return res

    def save_resource(self, path):
        """
        Flush the changes of a given resource instance. Normally this is called by the Resource object 
        in its own save.
        @param ref the reference to the resource to close. 
        """
        with currentdir(self.storage, self.curpath):
            res = self.storage.save_resource(path)
            return res

    def create_folder(self, path):
        """
        Create a folder entry to a path
        @param path : path to the folder
        """  
        with currentdir(self.storage, self.curpath):
            res = self.storage.create_folder(path)
            return res

    def delete_folder(self, path):
        """
        Delete a folder entry from a path. The path must be empty.
        @param path : path to the folder
        """  
        with currentdir(self.storage, self.curpath):
            res = self.storage.delete_folder(path)
            return res

    def is_folder(self, path):
        """
        Check if the given path is an existing folder in the storage
        @param path : path to the folder
        """
        with currentdir(self.storage, self.curpath):
            res = self.storage.is_folder(path)
            return res

    def get_mode(self, mode_str):
        return self.storage.get_mode()

    def unload(self, path, object):
        """
        Dump a given object to the storage 
        @param object: The object to dump to the storage, which is expected to be an instance 
        of Base class.
        @param path: The reference where to store the object 
        @param object: The object instance to dump 
        @raise StorageException: if the given object cannot be dumped to this storage 
        """
        with currentdir(self.storage, self.curpath):
            res = self.storage.unload(path, object)
            return res

    def load(self, path):
        """
        Load an object from a reference.
        @param path: The reference where to load the object 
        @raise StorageException: if the given object cannot be loaded as an object from this storage 
        """
        with currentdir(self.storage, self.curpath):
            res = self.storage.load(path)
            return res

    path = property(get_path, set_path)


class CompositeLayer(Folder):
    """
    A base class for composite Configuration objects.  
    """
    def __init__(self, storage, path="", **kwargs):
        super(CompositeLayer, self).__init__(storage, path, **kwargs)
        self.layers = kwargs.get('layers', [])
        self.path = path

    def add_layer(self, layer):
        self.layers.append(layer)

    def remove_layer(self, path):
        if self.get_layer(path):
            self.layers.remove(self.get_layer(path))
        else:
            raise exceptions.NotFound('Layer with given path %s not found!' % path)

    def get_layer(self, path):
        for layer in self.layers:
            if layer.get_current_path() == path:
                return layer
        return None

    def list_layers(self):
        return [layer.get_current_path() for layer in self.layers]

    def list_confml(self):
        """
        @return: array of confml file references.
        """
        lres = []
        for layerpath in self.list_layers():
            for respath in self.get_layer(layerpath).list_confml():
                lres.append(utils.resourceref.join_refs([layerpath, respath]))
        return lres

    def list_implml(self,empty_folders=False):
        """
        @return: array of implml file references.
        """
        lres = []
        for layerpath in self.list_layers():
            for respath in self.get_layer(layerpath).list_implml(empty_folders):
                lres.append(utils.resourceref.join_refs([layerpath, respath]))
        return lres

    def list_content(self,empty_folders=False):
        """
        @return: array of content file references.
        """
        lres = []
        for layerpath in self.list_layers():
            for respath in self.get_layer(layerpath).list_content(empty_folders):
                lres.append(utils.resourceref.join_refs([layerpath, respath]))
        return lres

    def list_doc(self,empty_folders=False):
        """
        @return: array of document file references.
        """
        lres = []
        for layerpath in self.list_layers():
            for respath in self.get_layer(layerpath).list_doc(empty_folders):
                lres.append(utils.resourceref.join_refs([layerpath, respath]))
        return lres

    def list_all_resources(self, **kwargs):
        """
        Returns a list of all layer related resource paths with full path in the storage.
        """
        lres = []
        for layerpath in self.list_layers():
            sublayer = self.get_layer(layerpath)
            for respath in sublayer.list_all_resources(**kwargs):
                lres.append(utils.resourceref.join_refs([layerpath, respath]))
        return lres
    
    def list_all_related(self, **kwargs):
        """
        Returns a list of all (non confml) layer related resource paths with full path in the storage.
        """
        lres = []
        for layerpath in self.list_layers():
            sublayer = self.get_layer(layerpath)
            for respath in sublayer.list_all_related(**kwargs):                
                lres.append(utils.resourceref.join_refs([layerpath, respath]))
        
        return lres
    
class Layer(CompositeLayer):
    """
    A Layer object is a subfolder of a Storage, offering access to part of the Storages resources.
    """
    def __init__(self, storage, path, **kwargs):
        """
        Create a layer folder to the storage if it does not exist.
        @param storage: a reference to the Storage object
        @param path: path for the layer 
        @param confml_path: optional parameter for confml files path (give in confml_path="something") 
        @param imlpml_path: optional parameter for implml files path (give in implml_path="something")
        @param content_path: optional parameter for content files path (give in content_path="something")
        @param doc_path: optional parameter for doc files path (give in doc_path="something")
        """
        super(Layer, self).__init__(storage, path, **kwargs)
        #if not storage.is_folder(path):
        #    storage.create_folder(path)
        self.predefined = {'confml_path' : 'confml', 
                           'implml_path' : 'implml', 
                           'content_path' : 'content', 
                           'doc_path' : 'doc'}
        # list through all "hardcoded" paths and check whether the 
        # hardcoded or given path exists under this Layer. 
        # if it does then create a folder instance to that path 
        for (pretag, prevalue) in self.predefined.items():
            self.predefined[pretag] = kwargs.get(pretag, prevalue)

    def __getattr__(self, name):
        return getattr(self.storage, name)

    def __getstate__(self):
        state = {}
        state['predefined'] = self.predefined
        state['path'] = self.path
        state['layers'] = self.layers
        return state

    def __setstate__(self, state):
        state = {}
        self.predefined = state.get('predefined',{})
        self.path = state.get('path','')
        self.layers = state.get('layers',[])
        
        return state
    
    def list_confml(self):
        """
        @return: array of confml file references.
        """
        res = self.list_resources(self.predefined['confml_path'], recurse=True)
        res += super(Layer, self).list_confml()
        return res 

    def list_implml(self,empty_folders=False):
        """
        @return: array of implml file references.
        """
        res = self.list_resources(self.predefined['implml_path'], recurse=True,empty_folders=empty_folders)
        res += super(Layer, self).list_implml(empty_folders)
        return res 

    def list_content(self,empty_folders=False):
        """
        @return: array of content file references.
        """
        res = self.list_resources(self.predefined['content_path'], recurse=True,empty_folders=empty_folders)
        res += super(Layer, self).list_content(empty_folders)
        return res

    def list_doc(self,empty_folders=False):
        """
        @return: array of document file references.
        """
        res = self.list_resources(self.predefined['doc_path'], recurse=True,empty_folders=empty_folders)
        res += super(Layer, self).list_doc(empty_folders)
        return res

    def confml_folder(self):
        cpath = self.get_current_path()
        spath = self.predefined['confml_path']
        return Folder(self.storage,  utils.resourceref.join_refs([cpath, spath]))

    def implml_folder(self):
        cpath = self.get_current_path()
        spath = self.predefined['implml_path']
        return Folder(self.storage,  utils.resourceref.join_refs([cpath, spath]))

    def content_folder(self):
        cpath = self.get_current_path()
        spath = self.predefined['content_path']
        return Folder(self.storage,  utils.resourceref.join_refs([cpath, spath]))

    def doc_folder(self):
        cpath = self.get_current_path()
        spath = self.predefined['doc_path']
        return Folder(self.storage,  utils.resourceref.join_refs([cpath, spath]))

    def list_all_resources(self, **kwargs):
        """
        Returns a list of all layer related resource paths with full path in the storage.
        """
        lres = []
        for folderpath in sorted(self.predefined.values()):
            lres += self.list_resources(folderpath, recurse=True)
                 
        lres += super(Layer, self).list_all_resources()
        return lres

    def list_all_related(self, **kwargs):
        """
        Returns a list of all (non confml) layer related resource paths with full path in the storage.
        """
        
        lres = []
        exclude_filters = kwargs.get('exclude_filters', {})
        kwargs['recurse'] = True
        predef = self.predefined.copy()
        del predef['confml_path']
        for folderpath in sorted(predef.values()):
            filter = exclude_filters.get(folderpath, None)
            resources = self.list_resources(folderpath, **kwargs)
            if filter:
                lres += [res for res in resources if not re.search(filter, res, re.IGNORECASE)]
            else:            
                lres += resources
        lres += super(Layer, self).list_all_related(**kwargs)
       
        return lres


class Include(Base, container.LoadLink):
    """
    A common include element that automatically loads a resource 
    and its object under this include element.
    """
    def __init__(self, ref="", **kwargs):
        path = kwargs.get('path') or ref
        store_interface = kwargs.get('store_interface',None)
        ref = utils.resourceref.to_objref(path)
        container.LoadLink.__init__(self, path, store_interface)
        Base.__init__(self, ref)
    
    def get_store_interface(self):
        if not self._storeint and self._parent:
            try:
                self._storeint = self._parent.get_store_interface()
            except exceptions.NotFound:
                # If project is not found, let the store interface be None 
                pass
        return self._storeint


class Rule(object):
    """
    Base class for Rules in the system.
    """
    def __init__(self):
        raise exceptions.NotSupportedException()
            

class FactoryBase(object):
    pass

class Factory(object):
    def __getattr__(self, name):
        """
        The Factory getattr find all subclasses for the Factory and searches for given attr 
        in those.
        """
        for sub_factory in utils.all_subclasses(FactoryBase):
            try:
                return getattr(sub_factory(), name)
            except AttributeError:
                continue 
        raise AttributeError("type object %s has no attribute '%s'" % (self.__class__, name))

def get_mapper(modelname):
    """
    Return a instance of appropriate mapper for given model.
    """
    mapmodule = __import__('cone.public.mapping')
    return mapmodule.public.mapping.BaseMapper()

class RulemlEvalGlobals(Base):
    """
    Ruleml subelement of extensions element
    """
    refname = "_extension"
    def __init__(self, value = None, file = None, **kwargs):
        """
        """
        super(RulemlEvalGlobals,self).__init__(self.refname)
        self.value = value
        self.file = file
    
    @classmethod
    def get_script_file_full_path(self, child): 
        parent_config = child._find_parent(type=Configuration)
        cpath = parent_config.get_full_path()
        cpath = utils.resourceref.psplit_ref(cpath)[0]
        path = utils.resourceref.join_refs([cpath, child.file])
        return path

class Problem(object):
    SEVERITY_ERROR      = "error"
    SEVERITY_WARNING    = "warning"
    SEVERITY_INFO       = "info"
    
    def __init__(self, msg, **kwargs):
        self.msg = msg
        self.type = kwargs.get('type', '')
        self.line = kwargs.get('line', None)
        self.file = kwargs.get('file', None)
        self.severity = kwargs.get('severity', self.SEVERITY_ERROR)
        self.traceback = kwargs.get('traceback', None)
        # A slot for any problem specific data 
        self.problem_data = kwargs.get('problem_data', None)
    
    def log(self, logger, current_file=None):
        """
        Log this problem with the given logger.
        """
        file = self.file or current_file
        if self.line is None:
            msg = "(%s) %s" % (file, self.msg)
        else:
            msg = "(%s:%d) %s" % (file, self.line, self.msg)
        
        mapping = {self.SEVERITY_ERROR:   logging.ERROR,
                   self.SEVERITY_WARNING: logging.WARNING,
                   self.SEVERITY_INFO:    logging.INFO}
        level = mapping.get(self.severity, logging.ERROR)
        logger.log(level, msg)
        
        if self.traceback:
            logger.debug(self.traceback)
    
    @classmethod
    def from_exception(cls, ex):
        """
        Create a Problem object from an exception instance.
        
        If the exception is a sub-class of ConeException, then it may contain
        extra information (like a line number) for the problem.
        """
        if isinstance(ex, exceptions.ConeException):
            return Problem(msg      = ex.problem_msg or unicode(ex),
                           type     = ex.problem_type or '',
                           line     = ex.problem_lineno,
                           severity = cls.SEVERITY_ERROR)
        else:
            return Problem(msg      = unicode(ex),
                           severity = cls.SEVERITY_ERROR)
    
    def __repr__(self):
        var_data = []
        for varname in ('msg', 'type', 'line', 'file', 'severity'):
            var_data.append("%s=%r" % (varname, getattr(self, varname)))
        return "%s(%s)" % (self.__class__.__name__, ', '.join(var_data))
    
    def __eq__(self, other):
        if not isinstance(other, Problem):
            return False
        for varname in ('msg', 'type', 'line', 'file', 'severity'):
            self_val = getattr(self, varname)
            other_val = getattr(other, varname)
            if self_val != other_val:
                return False
        return True
    
    def __ne__(self, other):
        return self == other
    
    def __lt__(self, other):
        if not isinstance(other, Problem):
            return False
        return (self.file, self.line) < (other.file, other.line)

def make_content_info(resource, data):
    """
    Factory for ContentInfo
    """
    cnt_inf = None
    
    if resource != None:
        guessed_type = mimetypes.guess_type(resource.get_path())
        mimetype = None
        mimesubtype = None
        
        if guessed_type != None:
            mimetype, mimesubtype = guessed_type[0].split('/') 
        
        if mimetype == 'image' and mimesubtype == 'x-ms-bmp':
            cnt_inf = BmpImageContentInfo(resource, data)
        else:
            cnt_inf = ContentInfo(mimetype, mimesubtype)
    return cnt_inf

def open_storage(path, mode="r", **kwargs):
    return Storage.open(path, mode="r", **kwargs)

class NullHandler(logging.Handler):
    """
    Default handler that does not do anything.
    """
    def emit(self, record):
        pass

#Initialization of default logger that contains NullHandler.
logger = logging.getLogger('cone')
logger.addHandler(NullHandler())
