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

import os
import re
import sys
import logging
import copy
import sets

import exceptions, utils, container, mapping

class Base(container.ObjectContainer):
    """
    The Base class is intended for capturing same kind of naming scheme.
    """
    
    
    def __init__(self, ref="", **kwargs):
        if len(utils.dottedref.split_ref(ref)) > 1:
            raise exceptions.InvalidRef("Invalid reference for Base object %s!" % ref)
        self.ref = ref
        container.ObjectContainer.__init__(self, ref)
        for arg in kwargs.keys():
            if kwargs.get(arg) != None:
                setattr(self, arg, kwargs.get(arg))

    def __repr__(self):
        dict = self._dict()
        return "%s(%s)" % (self.__class__.__name__, dict)

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
        
        self.set_storage(storage)
        self.update()
        self.loaded = {}

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
            return True
        
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
        if isinstance(storage, Storage):
            self.storage = storage
        else:
            raise exceptions.StorageException("The given storage is not a instance of Storage!")

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
        return [obj.get_path() for obj in self._traverse(type=(Configuration, ConfigurationProxy))]

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
        return path in self.list_configurations()

    def add_configuration(self, config):
        """
        Add a Configuration object to this project
        """
        if isinstance(config, Configuration):
            if self.is_configuration(config.get_path()):
                raise exceptions.AlreadyExists("%s" % config.get_path())
            self._add(config)
            self.__add_loaded__(config.get_path(), config)
            self.__loaded__(config.get_path())
        else:
            raise exceptions.IncorrectClassError("Only Configuration instance can be added to Project!")

    def create_configuration(self, path, namespace=""):
        """
        Create a Configuration object to this project
        """
        config = self.get_configuration_class()(utils.resourceref.norm(path), namespace=namespace)
        self.add_configuration(config)
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

    def export_configuration(self, configuration, export_storage, empty_folders=False):
        """
        Export a configuration object to another storage
        """
        # First clone the configuration and then import the rest of the configuration resources
        if isinstance(configuration, ConfigurationProxy):
            configuration = configuration._get_obj()
        
        export_storage.unload(configuration.get_full_path(),configuration)
        for child in configuration._traverse(type=Configuration):
            export_storage.unload(child.get_full_path(),child)
        
        #If the configuration is not in the root of the project adding the path 
        #to final exporting source path.
        #l = []
        cpath = utils.resourceref.get_path(configuration.get_path()) 
        resr = [utils.resourceref.join_refs([cpath,related]) \
                for related in configuration.get_layer().list_all_related(empty_folders)]        
        self.storage.export_resources(resr ,export_storage, empty_folders)
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

    def add_configuration(self, config):
        """
        Add an existing Configuration to this configuration
        @param config: A Configuration instance:
        @return: None 
        """
        """
        Merge the default view features from added config to this configs _default_view.
        """
        self._add(config)

    def include_configuration(self, configref):
        """
        Add an existing Configuration to this configuration by its resource reference
        @param config: A Configuration instance:
        @return: None 
        """
        # add the configuration load proxy to this configuration instead 
        # adding the configuration directly
        self._add(ConfigurationProxy(configref))

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
        cklass = self.get_configuration_class()
        conf = cklass(normpath, namespace=self.namespace)
        proxy = ConfigurationProxy(normpath)
        self.add_configuration(proxy)
        proxy._set_obj(conf)
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
        # TODO
        # huge performance problem 
        return [config.get_path() for config in self._traverse(type=(Configuration, ConfigurationProxy))] 

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

    def get_configuration_class(self):
        """
        return the default configuration class retrieved from the project if it is found.
        Otherwise return cone.public.api.Configuration. 
        """
        try:
            return self.get_project().get_configuration_class()
        # catch the Parent/Project NotFound exception
        except exceptions.NotFound:
            return Configuration

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
            self.add_configuration(child)
        elif isinstance(child, Base):
            self._add(child)
        else:
            raise exceptions.IncorrectClassError("Cannot add %s to %s" % (child, self))

    def layered_content(self, layers=None):
        """
        fetch content from first to last and override content 
        if it is found from a later layer 
        Create an array of the layers based on the layer indexes.
        """
        configuration_array = []
        if layers == None:
            configuration_array = self.list_configurations()
        else:
            all = self.list_configurations()
            for i in layers:
                configuration_array.append(all[i])

        content = container.DataContainer()
        for configuration_path in configuration_array:
            content_folder = self.get_configuration(configuration_path).get_layer().content_folder()
            content_path = content_folder.get_current_path()
            for content_file in content_folder.list_resources("", True):
                source_file = utils.resourceref.join_refs([content_path, content_file])
                content.add_value(content_file, source_file)
                
        return content


class Configuration(CompositeConfiguration):
    """
    A Configuration is a container that can hold several Layer objects.
    """

    def __init__(self, ref="", **kwargs):
        self.path = kwargs.get('path') or ref
        self.namespace = kwargs.get('namespace', '')
        self.name = utils.resourceref.to_objref(self.path)
        super(Configuration, self).__init__(utils.resourceref.to_objref(self.path))
        self.container = True

    def _default_object(self, name):
        return Feature(name)

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
        #self.name = utils.resourceref.to_objref(self.path)
        self.set_ref(utils.resourceref.to_objref(self.path))

    #@property
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
        #self.root.set_namespace(namespace)

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

    def list_resources(self, empty_folders=False):
        """
        List all resources used in this configuration
        """
        """
        1. First ensure that all configuration resource files are added 
        2. Then add all layer resources 
        3. Make the list distinct
        """
        
        
        resources = [self.get_full_path()]
        for config in self._traverse(type=Configuration):
            resources.append(config.get_full_path())
        layer = self.get_layer()
        for resref in layer.list_all_resources(empty_folders):
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

    def add_feature(self, feature, namespace=""):
        """
        Add a feature object to the configuration.
        @param feature: The Feature object to add.
        @param namespace: The sub namespace for the feature. 
        e.g. to add fea2 under fea1 add_feature(fea2, 'fea1')
        @return: None
        """
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
        @param data: The Data object to add.
        @return: None
        """ 
        if not self._has(data.attr):
            self._add(DataContainer(data.attr, container=True))
        (namespace, name) = utils.dottedref.psplit_ref(data.get_fearef())
        self._get(data.attr)._add_to_path(namespace, data, policy)

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

    def add_view(self, viewname):
        """
        Add a view object to the configuration.
        @param viewname: The name of the view to add. 
        @return: None
        """
        return self._add(View(viewname))

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
        for child in self._objects():
            if isinstance(child, (Configuration,ConfigurationProxy)):
                child.save()
        self.get_project().unload(self.get_full_path(), self)

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
                if not hasattr(self, '_default_view'):
                    self._create_default_view()
                return self._default_view
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
        self._default_view = View("_default_view", data=True)
        self._default_view._parent= self
        # First add all features of the configuration to the view. 
        # Then add all data elements under the features
        for child in self._traverse(type=Feature):
            self._default_view.add_feature(child, child.namespace)
        for child in self._traverse(type=Data):
            #parent_config = child._find_parent_or_default(type=Configuration)
            #print "Adding data %s: fqr: %s from file %s." % (child.get_value(), child.fqr, parent_config.get_path())
            try:
                fea = self._default_view.get_feature(child.fqr)
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
        container.LoadProxy.__init__(self, path)
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
        self.name = ref
        self.support_data = kwargs.get("data", False)

    def _supported_type(self, obj):
        if isinstance(obj, (Group, \
                           Base, \
                           _FeatureProxy, \
                           FeatureLink)): 
            return True
        else:
            return False

    def _default_object(self, name):
        return Group(name)

    def get_name(self):
        """
        Return the name of the configuration
        """
        return self.name

    def set_name(self, name):
        """
        Set the name
        """
        self.name

    def add(self, child, policy=container.REPLACE):
        """
        A generic add function to add child objects. The function is intended to act as
        proxy function that call the correct add function based on the child objects class.
        
        Example: obj.add(Feature("test")), actually obj.add_feature(Feature("test"))
        @param child: the child object to add
        @raise IncorrectClassError: if the given class cannot be added to this object.  
        """
        if isinstance(child, (Group, \
                              Base, \
                              _FeatureProxy, \
                              FeatureLink)):
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

    def get_features(self, ref, **kwargs):
        """
        Get a list of features that match the ref. 
        Example1: get_features('foo.bar') would be the same as get_feature('foo.bar'), but this returns 
        always a list [<Feature>].
        Example2: get_features('foo.*') would try to retrieve a list of all foo children.
        Example3: get_features('foo.*', type='') would try to retrieve a list of all foo children, 
        that have a defined type.
        @param path: The path (ref) to the given feature or xpath like expression 
        @return: A list of features.
        """
        (startref, last) = utils.dottedref.psplit_ref(ref)
        startelem = self._get(startref)
        if last == '**':
            return [fea for fea in startelem._traverse(**kwargs)]
        elif last == '*':
            return [fea for fea in startelem._objects(**kwargs)] 
        else:
            return [self._get(ref)]

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

    def add_group(self, groupname):
        """
        """
        self._add(Group(groupname))

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
        return [group.get_name() for group in self._objects(type=Group)]

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
        self.name = ref
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
        self.name = kwargs.get('name', ref)
        self.type = kwargs.get('type', None)
        self._dataproxy = None

    def __copy__(self):
        dict = {}
        for key in self.__dict__.keys():
            if key.startswith('_') or key == 'ref':
                continue
            else:
                dict[key] = self.__dict__[key]
        fea = self.__class__(self.ref, **dict)
        return fea


    def _supported_type(self, obj):
        # For now support added for desc element via support for Base
        if isinstance(obj, (Feature, Option, Base)):
            return True
        else:
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
            self._add(child, policy)
        elif isinstance(child, Base):
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

    def get_type(self):
        return self.type

    def set_type(self, type):
        self.type = type

    def add_feature(self, feature, path=""):
        """
        @param feature: The Feature object to add 
        """
        configuration = self.find_parent(type=Configuration)
        if configuration:
            feapath = utils.dottedref.join_refs([self._path(configuration), path])
            configuration.add_feature(feature, feapath)
        else:
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
        configuration = self.find_parent(type=Configuration)
        if configuration:
            fullfqr = utils.dottedref.join_refs([self._path(configuration), ref])
            configuration.remove_feature(fullfqr)
        else:
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

    def get_value(self, attr=None):
        """
        Get the current value of the feature
        @param attr: The attribute name of the data. E.g. attr='data', attr='rfs' 
        """
        # Do not allow getting of setting of sequence values directly with Feature object
        if not self.is_sequence():
            return self.get_value_cast(self.dataproxy._get_value(attr), attr)
        else:
            """ get the feature specific data from sequence => a column of data table """
            coldata =  []
            feasequence = self.get_sequence_parent()
            feapath = self._path(feasequence)
            for row in feasequence.data:
                feadata = row.get_feature(feapath)
                coldata.append(feadata.value)
            return coldata

    def set_value(self, value, attr=None):
        """
        Set the current value for this feature. Set the value on the topmost layer.
        @param value: the value to set
        """
        # Do not allow setting of setting of sequence values directly with Feature object
        if not self.is_sequence():
            value = self.set_value_cast(value, attr)
            self.dataproxy._set_value(value, attr)

    def del_value(self, attr=None):
        """
        Delete the topmost value for this feature.
        """
        if not self.is_sequence():
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
        # Do not allow getting of setting of sequence values directly with Feature object
        if not self.is_sequence():
            return self.dataproxy._get_value(attr)
        else:
            """ get the feature specific data from sequence => a column of data table """
            coldata =  []
            feasequence = self.get_sequence_parent()
            feapath = self._path(feasequence.data)
            for row in feasequence.data:
                feadata = row.get_feature(feapath)
                coldata.append(feadata.value)
            return coldata

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
    value = property(get_value, set_value, del_value)

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
        super(FeatureSequence, self).__init__(ref)
        self.name = kwargs.get('name', ref)
        self.type = 'sequence'
        self.mapKey   = kwargs.get('mapKey')
        self.mapValue = kwargs.get('mapValue')
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
        # If template data is not existing, create it
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
        if dataobj == None:
            dataobj = Data(fqr=self.fqr)
        elif dataobj.attr != 'data':
            # Add data rows only for data objects (not e.g. RFS)
            return
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
            rowproxy.add_feature(FeatureSequenceSub(fearef), pathto_fea)
            subproxy = rowproxy.get_feature(feaname)
            subproxy._obj._parent = subproxy._parent 
            if not dataobj._has(feaname):
                dataobj._add_to_path(pathto_fea, Data(ref=fearef))
            subproxy._add_data(dataobj._get(feaname))

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

    def add_sequence(self, data=None, policy=POLICY_APPEND):
        """
        Add a feature data row for a new data in this sequence 
        """
        self._add_datarow(None, policy)
        # set the initial data if it is given
        rowproxy = utils.get_list(self.dataproxy._get(self.dataelem_name))[-1]
        if data != None:
            for index in range(len(data)):
                rowproxy[index].set_value(data[index])
        # add the new data sequence/row to the last configuration layer
        dataobj = rowproxy._get_data()
        last_config = self.get_root_configuration().get_last_configuration()
        last_config.add_data(dataobj, container.APPEND)
        return dataobj

    def set_template(self, data=None):
        """
        Set the template of the feature sequence  
        """
        # If template data is not existing, create it
        if self._templatedata == None:
            self._set_template_data(Data(ref=self.ref, template=True))
            # Add the template data to parent config
            pconfig = self.find_parent(type=Configuration)
            pconfig.add_data(self._templatedata)

        if data != None:
            templdatas = self._templatedata._objects()
            for index in range(len(data)):
                templdatas[index].set_value(data[index])

    def get_template(self):
        """
        Add a feature data row for a new data in this sequence 
        """
        #self._set_template(None)
        # set the initial data if it is given
        if self._templatedata:
            return [data.get_value() for data in self._templatedata._objects()]
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
    
    def get_map_key(self):
        """
        Returns the setting that corresponds to mapKey attribute of this sequence feature.
        """
        if self.mapKey != None:
            mapkey = self.get_feature(self.mapKey)
            return mapkey
        else:
            return None

    def get_map_key_value(self,key):
        """
        Returns the setting that corresponds to mapKey attribute of this sequence feature.
        """
        value = None
        if self.mapKey != None and self.mapValue != None:
            data = self.get_data()
            for item in data:
                kv = item.get_feature(self.mapKey).get_value()
                if kv == key:
                    value = item.get_feature(self.mapValue).get_value()
        return value

    def get_map_value(self):
        """
        Returns the setting that corresponds to mapValue attribute of this sequence feature.
        """
        if self.mapValue != None:
            mapvalue = self.get_feature(self.mapValue)
            return mapvalue
        else:
            return None
        
    def get_value(self, attr=None):
        """
        Helper function to get the topmost data value from the default view.
        """
        datatable =  self.get_data()
        rettable = [] 
        for row in datatable:
            rowvalues = row.value
            rettable.append(rowvalues)
        return rettable

    def set_value(self, value, attr=None):
        """
        Set the current value for this feature. Set the value on the topmost layer.
        @param value: the value to set. The value must be a two dimensional array (e.g. matrix)
        """
        # sets the first data element to replace policy
        try:
            self.add_sequence(value.pop(0), self.POLICY_REPLACE)
        # ignore the index error of an empty list
        except IndexError:
            pass
        for row in value:
            self.add_sequence(row)

    def is_sequence(self):
        """ Return always true from a sequence object """
        return True

    def get_sequence_parent(self):
        """ Return this object as a sequence parent """
        return self

    value = property(get_value, set_value)
    data = property(get_data)

class FeatureSequenceCell(Feature):
    """
    A Feature class. Feature is the base for all Configurable items in a Configuration.
    """
    def __init__(self, ref="", **kwargs):
        super(Feature, self).__init__(ref)
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
        super(Feature, self).__init__(ref)
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
            self.dataproxy.get_data().set_value(value)

    def get_value(self, attr=None):
        """
        Set the current value for this feature. Set the value on the topmost layer.
        @param value: the value to set
        """
        # dataproxy = self.get_default_view().get_feature(self.get_fullfqr())
        # The sequence cell only updates the latest value in the proxy
        childdatas = self.dataproxy._objects()
        if len(childdatas) > 0:
            return [subdata.value for subdata in childdatas]
        else: 
            return self.dataproxy._get_value(attr=attr)

    value = property(get_value, set_value)


class FeatureLink(Base):
    """
    A _FeatureProxy class. _FeatureProxy is the object that is added to View as a 
    link to the actual Feature object. 
    """
    def __init__(self, link="", **kwargs):
        # Store the fully qualified reference to this object
        self.link = link
        ref = link.replace('.', '_')
        super(FeatureLink, self).__init__(ref)
        self._obj = None
        self._populated = False

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
                # add the found features to the parent
                for fea in feas:
                    self._get_parent().add_feature(fea._obj)
        except exceptions.NotFound, e:
                parent_view = self._find_parent_or_default(type=View)
                view_name = parent_view.get_name()
                logging.getLogger('cone').info("Warning: Feature '%s' in view '%s' not found." % (self.link, view_name))


class _FeatureProxy(container.ObjectProxyContainer, Base):
    """
    A _FeatureProxy class. _FeatureProxy is the object that is added to View as a 
    link to the actual Feature object. 
    """
    def __init__(self, ref="", obj=None, **kwargs):
        super(_FeatureProxy, self).__init__(obj, ref)
        Base.__init__(self, ref)
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
        raise exceptions.NotSupported()

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
            self._obj.dataproxy = self
        
        if name in Feature.PROPERTIES:
            return getattr(self._obj, name)
        else:
            return super(_FeatureDataProxy, self).__getattr__(name)
    
    def __setattr__(self, name, value):
        """
        """
        if object.__getattribute__(self, '_obj') is not None:
            self._obj.dataproxy = self
            
        if name in Feature.PROPERTIES:
            return setattr(self._obj, name, value)
        else:
            super(_FeatureDataProxy, self).__setattr__(name, value)

    def __delattr__(self, name):
        """
        """
        if name in Feature.PROPERTIES:
            return delattr(self._obj, name)
        else:
            return super(_FeatureDataProxy, self).__delattr__(name)

    def _add_data(self, data):
        """
        Add a data value.
        @param data: A Data object  
        """
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
        return self.datas[dataattr]

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

    def get_fearef(self):
        if self.fearef:
            return self.fearef
        else:
            return self.fqr

    def get_value(self):
        if self.map != None:
            ref = utils.resourceref.to_dref(self.get_map_ref())
            key = self.get_map_key_value()
            dview = self.get_root_configuration().get_default_view()
            fea = dview.get_feature(ref)
            return fea.get_map_key_value(key)
        else:
            return self.value

    def get_map(self):
        return self.map

    def set_map(self, map):
        self.map = map
        if self.value:
            #Either value or mapping can be defined. Not both.
            self.value = None

    def get_map_ref(self):
        if self.map != None:
            return utils.DataMapRef.get_feature_ref(self.map)
        else:
            return None

    def get_map_key_value(self):
        if self.map != None:
            return utils.DataMapRef.get_key_value(self.map)
        else:
            return None

    def set_value(self, value):
        self.value = value
        if self.map:
            #Either value or mapping can be defined. Not both.
            self.map = None

    def get_policy(self): return self._policy
    def set_policy(self, value): self._policy = value
    def del_policy(self):  self._policy = None
    policy = property(get_policy, set_policy, del_policy)


class ValueSet(sets.Set):
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

    def __init__(self, path):
        """
        @param path: the reference to the root of the storage.
        """
        self.rootpath = path
        self.curpath = ""
        self.container = True
        self.__opened_res__ = {}

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

    def list_resources(self, path, recurse=False):
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

    def close_resource(self, path):
        """
        Close a given resource instance. Normally this is called by the Resource object 
        in its own close.
        @param ref the reference to the resource to close. 
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
        raise NotSupportedException()

    def save(self, size=0):
        """
        Save all changes to data to storage.
        """
        raise NotSupportedException()

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
        
class Folder(object):
    """
    A Folder object is a subfolder of a Storage, offering access to part of the Storages resources.
    """
    def __init__(self, storage, path):
        """
        Create a layer folder to the storage if it does not exist.
        """
        #if not storage.is_folder(path):
        #    storage.create_folder(path)
        self.storage = copy.copy(storage)
        self.storage.set_current_path(path)

    def __getattr__(self, name):
        return getattr(self.storage, name)

class CompositeLayer(object):
    """
    A base class for composite Configuration objects.  
    """
    def __init__(self, path="", **kwargs):
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

    def list_implml(self):
        """
        @return: array of implml file references.
        """
        lres = []
        for layerpath in self.list_layers():
            for respath in self.get_layer(layerpath).list_implml():
                lres.append(utils.resourceref.join_refs([layerpath, respath]))
        return lres

    def list_content(self):
        """
        @return: array of content file references.
        """
        lres = []
        for layerpath in self.list_layers():
            for respath in self.get_layer(layerpath).list_content():
                lres.append(utils.resourceref.join_refs([layerpath, respath]))
        return lres

    def list_doc(self):
        """
        @return: array of document file references.
        """
        lres = []
        for layerpath in self.list_layers():
            for respath in self.get_layer(layerpath).list_doc():
                lres.append(utils.resourceref.join_refs([layerpath, respath]))
        return lres

    def list_all_resources(self, empty_folders=False):
        """
        Returns a list of all layer related resource paths with full path in the storage.
        """
        lres = []
        for layerpath in self.list_layers():
            sublayer = self.get_layer(layerpath)
            for respath in sublayer.list_all_resources(empty_folders):
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
        super(Layer, self).__init__(path, **kwargs)
        #if not storage.is_folder(path):
        #    storage.create_folder(path)
        self.storage = copy.copy(storage)
        self.storage.set_current_path(path)
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

    def list_confml(self):
        """
        @return: array of confml file references.
        """
        res = self.storage.list_resources(self.predefined['confml_path'], True)
        res += super(Layer, self).list_confml()
        return res 

    def list_implml(self):
        """
        @return: array of implml file references.
        """
        res = self.storage.list_resources(self.predefined['implml_path'], True)
        res += super(Layer, self).list_implml()
        return res 

    def list_content(self):
        """
        @return: array of content file references.
        """
        res = self.storage.list_resources(self.predefined['content_path'], True)
        res += super(Layer, self).list_content()
        return res

    def list_doc(self):
        """
        @return: array of document file references.
        """
        res = self.storage.list_resources(self.predefined['doc_path'], True)
        res += super(Layer, self).list_doc()
        return res

    def confml_folder(self):
        cpath = self.storage.get_current_path()
        spath = self.predefined['confml_path']
        return Folder(self.storage,  utils.resourceref.join_refs([cpath, spath]))

    def implml_folder(self):
        cpath = self.storage.get_current_path()
        spath = self.predefined['implml_path']
        return Folder(self.storage,  utils.resourceref.join_refs([cpath, spath]))

    def content_folder(self):
        cpath = self.storage.get_current_path()
        spath = self.predefined['content_path']
        return Folder(self.storage,  utils.resourceref.join_refs([cpath, spath]))

    def doc_folder(self):
        cpath = self.storage.get_current_path()
        spath = self.predefined['doc_path']
        return Folder(self.storage,  utils.resourceref.join_refs([cpath, spath]))

    def list_all_resources(self, empty_folders=False):
        """
        Returns a list of all layer related resource paths with full path in the storage.
        """
        lres = []
        mypath = self.get_current_path()
        
        for folderpath in sorted(self.predefined.values()):
            lres += self.storage.list_resources(folderpath, recurse=True, empty_folders=empty_folders)
                 
        lres += super(Layer, self).list_all_resources(empty_folders)
        
        return lres

    def list_all_related(self, empty_folders=False):
        """
        Returns a list of all (non confml) layer related resource paths with full path in the storage.
        """
        lres = []
        predef = self.predefined.copy()
        del predef['confml_path']
        mypath = self.get_current_path()
        for folderpath in sorted(predef.values()):
            lres += self.storage.list_resources(folderpath, recurse=True, empty_folders=empty_folders)
        lres += super(Layer, self).list_all_resources(empty_folders=empty_folders)
       
        return lres


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


##################################################################
class NullHandler(logging.Handler):
    """
    Default handler that does not do anything.
    """
    def emit(self, record):
        pass

#Initialization of default logger that contains NullHandler.
logger = logging.getLogger('cone')
logger.addHandler(NullHandler())
