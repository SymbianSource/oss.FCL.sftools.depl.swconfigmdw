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
Container classes.
Mainly internal classed that the public data model uses internally.
"""

import re
import pickle
import logging
import utils
from cone.public import exceptions

def object_container_filter(obj,**kwargs):
    """ Create a list of filter functions for each argument """ 
    filters=[]
    if kwargs.has_key('name'):
        filters.append(lambda x: re.match(kwargs.get('name'), x._name))
    if kwargs.has_key('path'):
        filters.append(lambda x: re.match(kwargs.get('path'), x._path()))
    if kwargs.has_key('type'):
        filters.append(lambda x: isinstance(x, kwargs.get('type')))
    if kwargs.has_key('filters'):
        filters += kwargs.get('filters')
    ret = []
    for sobj in utils.get_list(obj):
        if utils.filter(obj,filters):
            ret.append(sobj)
        
    return ret

def _apply_filter(obj,filters):
    """ Create a list of filter functions for each argument """ 
    if utils.filter(obj,filters):
        return [obj]
    else:
        return []

""" object container adding policies """
REPLACE = 0
APPEND = 1
PREPEND = 2
ERROR = 3

class DataContainer(object):
    """
    Class for data containers. 
    Container is a data storage that can hold several keys, where each key is unique. Each key however 
    can hold several values, where the active value is the last one added. 
    
    Example:
    data = {'key1' :[1,2,3,4], 
            'key2' :['foo','bar],
            'key3' :['testing'],
            'path/to/key' :['some','value','in','here','too']}
    
    The active values for keys are the last ones in the array. E.g. key1 = 4.
    """
    def __init__(self):
        self.data = {}
        
    def list_keys(self):
        """
        List all keys of the DataStorage.
        """
        return self.data.keys()
    
    def add_value(self,key,value):
        """
        Add the value as a topmost item for the given key.
        @param key: name for the key to store the data.
        @param value: the value to store.  
        """
        if self.data.has_key(key):
            self.data[key].append(value)
        else:
            self.data[key] = [value]
        return
    
    def remove_value(self,key,value):
        """
        remove individual value of the key value array
        """
        self.data[key].remove(value)
        return 
    
    def remove_key(self,key):
        del self.data[key]
        return
    
    def get_value(self,key):
        """
        self.data = {'key1' :[1,2,3,4], 
                    'key2' :['foo','bar],
                    'key3' :['testing'],
                    'path/to/key' :['some','value','in','here','too']}
        self.get_value('key1')
        4
        """
        return self.data[key][-1]
        
    def get_values(self,key):
        """
        return a copy of data values inside the container
        """
        values = []
        values.extend(self.data[key])
        return values

    def flatten(self):
        """
        return a new dictionary of the DataContainer data with only single values for each key, 
        instead of the array of values.
        """
        rest = {}
        for key in self.data.keys():
            rest[key] = self.get_value(key)
        return rest

    def clear(self):
        """
        Remove all data from the container.
        """
        return self.data.clear()

class ContainerBase(object):
    def __init__(self, name="",**kwargs):
        if len(name.split(".")) > 1 or len(name.split("/")) > 1:
            raise exceptions.InvalidRef("Illegal name for ObjectContainer %s" % name)
        self._name = name
        self._parent = None
        self._order = []
        self._children = {}
        self._respath = ""
        for arg in kwargs.keys():
            setattr(self, arg, kwargs.get(arg))

    def __getstate__(self):
        state = self.__dict__.copy()
        return state
    
    def __setstate__(self, state):
        self.__dict__.update(state)

    def _set_parent(self, newparent):
        """
        @param newparent:  The new parent object
        @return: None
        """
        self._parent = newparent

    def _get_parent(self):
        """
        @return: existing parent object
        """
        return self._parent
    
    def _del_parent(self):
        """
        Set the current parent to None
        """
        self._parent = None

    def get_store_interface(self):
        """
        Get a possible store interface for this ContainerBase object
        """
        return None

    def get_path(self):
        """
        Return the path of the object
        """
        return self._respath

    parent = property(_get_parent, _set_parent,_del_parent)


class ObjectProxy(ContainerBase):
    """
    An object proxy class. The ObjectProxy overrides the python builtin methdo __getattr__
    to redirect any function/member access to the subobject.  
    """
    def __init__(self,obj=None):
        """
        """
        self._obj  = obj
        self._parent = None
    
    def __getattr__(self,name):
        """
        direct all not found attribute calls to the sub object getattr
        """
        return getattr(self._obj,name)

    
#    def _set_parent(self, newparent):
#        """
#        @param newparent:  The new parent object
#        @return: None
#        """
#        self._parent = newparent
#        if isinstance(self._obj, ContainerBase):
#            self._obj._set_parent(newparent)

class LoadInterface(ContainerBase):
    def load(self,ref):
        file = open(ref,"rb")
        self._parent = None
        return pickle.load(file)

    def unload(self,ref, obj):
        """
        unload or release
        """
        file = open(ref,"wb")
        pickle.dump(obj,file)
        file.close()

    def get_path(self):
        """
        Return the path of the configuration resource
        """
        return ""


class ObjectContainer(ContainerBase):
    """
    An object container class. The ObjectContainer is actually a Tree data structure. Any ObjectContainer 
    instance can include any number of children, that must be instances of ObjectContainer.  
    """
    def __init__(self,name="",**kwargs):
        """
        """
        super(ObjectContainer,self).__init__(name, **kwargs)

    def __getattr__(self,name):
        """
        direct all not found attribute calls to the sub object getattr
        """
        try:
            return self.__dict__['_children'][name]
        except KeyError:
            try:
                return getattr(super(ObjectContainer),name)
            except AttributeError,e:
                raise AttributeError("%s object has not attribute '%s'" % (self.__class__, name))

    def _path(self, toparent=None):
        """
        Get the path to this ObjectContainer.
        @param toparent: the _parent object up to which the path is relative. Default value is None.,
        which gives the fully qualified path
        @return: The path to the ObjectContainer from toparent
        """
        if self == toparent:
            return ""
        elif self._parent and self._parent != toparent:
            # return the path with list index if the given element is in a list
            if utils.is_list(self.parent._get(self._name)):
                return self._parent._path(toparent)+"."+"%s[%s]" % (self._name,self.get_index())
            else:
                return self._parent._path(toparent)+"."+self._name
        else:
            return self._name
    
    def _add(self, child_or_children, policy=REPLACE):
        """
        Add a child object or multiple child objects. 
        @param child_or_children: The child object or list of child objects to add.
            The children need to be instances of ObjectContainer. 
        @param policy: The policy which is used when an object with same name exists already  
        """
        if isinstance(child_or_children, list):
            objs = child_or_children
            if policy == PREPEND:
                objs = reversed(objs)
                policy_first = PREPEND
                policy_rest = PREPEND
            else:
                policy_first = policy
                policy_rest = APPEND
            
            for i, obj in enumerate(objs):
                if i == 0:  p = policy_first
                else:       p = policy_rest
                self._add(obj, p)
            return
        
        
        # check that the child is a supported type
        child = child_or_children
        if not self._supported_type(child):
            raise exceptions.IncorrectClassError("Cannot add instance of %s to %s." % (child.__class__,self.__class__))
        if policy == REPLACE:
            self._replace(child)
        elif policy == ERROR:
            self._error(child)
        elif policy == APPEND:
            self._append(child)
        elif policy == PREPEND:
            self._prepend(child)

    def _append(self, child):
        """
        Add the given child to the proper key. Create a list entry if necessary
        """
        child._set_parent(self)
        if not self._children.has_key(child._name):
            # skip all internal objects (that start with _)
            if not child._name.startswith('?'):
                self._order.append(child._name)
            self._children[child._name] = child
        else:
            """ Create a list under the child name """
            self._children[child._name] = utils.add_list(self._children[child._name], child)
        return

    def _prepend(self, child):
        """
        Add the given child to the proper key. Create a list entry if necessary
        """
        child._set_parent(self)
        if not self._children.has_key(child._name):
            # skip all internal objects (that start with _)
            if not child._name.startswith('?'):
                self._order.insert(0,child._name)
            self._children[child._name] = child
        else:
            """ Create a list under the child name """
            self._children[child._name] = utils.prepend_list(self._children[child._name], child)
        return

    def _replace(self, child):
        """
        If the given child already exists => Replace the child, 
        but maintain the current children of that child 
        """
        child._set_parent(self)
        # skip all internal objects (that start with _)
        if not self._children.has_key(child._name):
            if not child._name.startswith('?'):
                self._order.append(child._name)
        else:
            """ 
            if the existing child is a instance of ObjectContainer, 
            add all children of the existing container to this new object, except if the 
            child already exists in the new child. 
            """
            existingchild = self._children[child._name]
            if isinstance(existingchild, ObjectContainer):
                for subchild in existingchild._objects():
                    if not child._children.has_key(subchild._name):
                        child._add(subchild)
                     
        
        self._children[child._name] = child
        return

    def _error(self, child):
        """
        If the given child already exists => raise an exception.
        @raise exceptions.AlreadyExists: 
        """
        child._set_parent(self)
        if not self._children.has_key(child._name):
            # skip all internal objects (that start with _)
            if not child._name.startswith('?'):
                self._order.insert(0,child._name)
            self._children[child._name] = child
        else:
            raise exceptions.AlreadyExists('Child %s already exists' % child._name)
        return

    def _add_to_path(self, path, child, policy=REPLACE):
        """
        Add a child object.
        @param path: the path for the object
        @param child: The child object to add 
        @param namespace: The namespace of the object, which defines where the object is created  
        """
        # check that the child is a supported type
        if not self._supported_type(child):
            raise exceptions.IncorrectClassError("Cannot add instance of %s to %s Container" % (child.__class__,self.__class__))
        # ensure that the elements to the namespace exist  
        curelem = self
        for ppath in utils.dottedref.split_ref(path):
            
            if not curelem._children.has_key(ppath):
                # Create missing elem
                curelem._add(self._default_object(ppath))
            curelem = curelem._get(ppath)
        curelem._add(child,policy)

    def _get(self, path):
        """
        Get a child object by it path.
        @return: The child object if it is found. 
        @raise NotFound: when object is not found from the children.  
        """
        
        try:
            # traverse to the actual child element 
            curelem = self
            for pathelem in utils.dottedref.split_ref(path):
                if utils.dottedref.get_index(pathelem) == None:
                    curelem = curelem._children[pathelem]
                else:
                    # If the given pathelem is referring to a list 
                    name = utils.dottedref.get_name(pathelem)
                    index = utils.dottedref.get_index(pathelem)
                    curelem = utils.get_list(curelem._children[name])[index]
            return curelem
        # Catch the KeyError exception from dict and IndexError from list
        except (KeyError,IndexError), e: 
            raise exceptions.NotFound("Child %s not found from %s! %s" % (path, self, e))

    def _has(self, path):
        """
        Returns True if an element under the path is found.
        @return: Boolean value. 
        """
        
        try:
            # traverse to the actual child element 
            curelem = self
            for pathelem in utils.dottedref.split_ref(path):
                curelem = curelem._children[pathelem]
            return True
        except KeyError: 
            return False

    def _remove(self, path):
        """
        Remove a child object by it path.
        """
        # if the patherence is a long patherence (dotted name)
        # first get the _parent object and call the remove to the _parent
        (parentref,name) = utils.dottedref.psplit_ref(path)
        if parentref != "":
            self._get(parentref)._remove(name)
        elif utils.dottedref.get_index(path) != None and \
             self._get(utils.dottedref.get_name(path)):
            # Delete If the given pathelem is referring to a list 
            name = utils.dottedref.get_name(path)
            index = utils.dottedref.get_index(path)
            del self._children[name][index]
            if len(self._children[name]) == 0:
                del self._order[self._order.index(name)]
        elif self._get(path) != None: # delete if the child is found
            del self._children[path]
            # hidded children are not added to the order list 
            if not path.startswith('?'):
                del self._order[self._order.index(path)]
            
        else:
            raise exceptions.NotFound("Child %s not found!" % path)

    def _list_traverse(self,**kwargs):
        """
        Return a list of all children paths. This function calls internally __traverse__, see it for 
        more details.
        @return: an unordered list of children paths. The path is relative to this node. 
        """
        return [child._path(self) for child in self._traverse(**kwargs)]

    def _traverse(self, **kwargs):
        """
        The traverse goes recursively through the tree of children of this node and returns a result set as list.
        Arguments can be passed to it to filter out elements of the result set. All arguments are 
        given as dict, so they must be given with name. E.g. _traverse(name='test')
        @param name: The node name or part of name which is used as a filter. This is a regular expression (uses internally re.match()) 
        @param path: The path name or part of name which is used as a filter. This is a regular expression (uses internally re.match())
        @param type: The type (class) of the objects that should be returned (this can be a tuple of types)
        @param depth: The max recursion depth that traverse goes through. 
        @param filters: A list of predefined filters can be given as lambda functions. E.g. filters=[lambda x: isinstance(x._obj, FooClass)]  
        @return: a list of ObjectContainer objects.
        """
        filterlist=[]
        if kwargs.has_key('ref'):
            filterlist.append(lambda x: re.match(kwargs.get('ref'), x.ref))
        if kwargs.has_key('name'):
            filterlist.append(lambda x: re.match(kwargs.get('name'), x._name))
        if kwargs.has_key('path'):
            filterlist.append(lambda x: re.match(kwargs.get('path'), x._path()))
        if kwargs.has_key('type'):
            filterlist.append(lambda x: isinstance(x, kwargs.get('type')))
        if kwargs.has_key('filters'):
            filterlist += kwargs.get('filters')

        ret = []
        for child in self._objects():
            subchildren = child._tail_recurse(_apply_filter,filters=filterlist,depth=kwargs.get('depth',-1))
            ret += subchildren
        return ret
    
    def _find_leaves(self, **kwargs):
        """
        Find all leaf nodes in the tree that satisfy the given filtering criteria.
        
        For possible keyword arguments see _traverse().
        
        @return: A list of ObjectContainer objects.
        """
        # Find all children
        nodes = self._traverse(**kwargs)
        
        # Filter out non-leaves
        return filter(lambda node: len(node._objects()) == 0, nodes)

    def _tail_recurse(self, function, **kwargs):
        """
        Run a tail recursion on all container children and execute the given function.
        1. function will receive self as argument to it.
        2. function will receive all kwargs as argument to it.
        3. tail recursion means that the function is executed first and then the 
        recursion continues.
        @param function: the function which is executed
        @param kwargs: a list of arguments as dict
        @return: an list of objects, which can be anything that the funtion returns   
        """
        depth = kwargs.get('depth',-1)
        ret = []
        # check the if the recursion maximum depth has been reached
        # if not reached but set, decrease it by one and set that to subrecursion
        if depth != 0:
            ret += function(self,kwargs.get('filters',[]))
            kwargs['depth'] = depth - 1
            for child in self._objects():
                try:
                    # We wont add the object to the ret until we know that it is a valid object
                    subchildren = child._tail_recurse(function,**kwargs)
                    #ret += function(child,**kwargs)
                    ret += subchildren
                except exceptions.InvalidObject,e:
                    # remove the invalid object from this container
                    logging.getLogger('cone').warning('Removing invalid child because of exception %s' % e)
                    self._remove(child._name)
                    continue
        
        return ret

    def _head_recurse(self, function,**kwargs):
        """
        Run a tail recursion on all container children and execute the given function.
        1. function will receive self as argument to it.
        2. function will receive all kwargs as argument to it.
        3. head recursion means that the recursion continues to the leaf nodes and then the 
        execution of the function begins.
        @param function: the function which is executed
        @param kwargs: a list of arguments as dict
        @return: an list of objects, which can be anything that the funtion returns   
        """
        ret = []
        for child in self._objects():
            try:
                ret += child._head_recurse(function,**kwargs)
                ret += function(child,**kwargs)
            except exceptions.InvalidObject,e:
                # remove the invalid object from this container
                logging.getLogger('cone').warning('Removing invalid child because of exception %s' % e)
                self._remove(child._name)
                continue
        return ret

    def _list(self):
        """
        Return a array of immediate children names.
        @return: an unordered list of immediate children path-references
        """
        # skip all internal objects (that start with _)
        return [name for name in self._order if not name.startswith('?')] 

    def _objects(self, **kwargs):
        """
        Return a array of immediate children.
        @return: an unordered list of immediate children
        """
        ret = []
        for cname in self._order:
            try:
                if object_container_filter(self._children[cname], **kwargs):
                    ret += utils.get_list(self._children[cname])
            except exceptions.InvalidObject,e:
                # remove the invalid object from this container
                logging.getLogger('cone').warning('Removing invalid child because of exception %s' % e)
                self._remove(cname)
                continue
        return ret

    def _get_index(self, name):
        """
        Get the index of a child object by its name. The index matches the index
        of the child object in the _children array. 
        @return: integer. 
        @raise NotFound: when object is not found from the children.  
        """
        
        try:
            return self._order.index(name)
        except KeyError:
            raise exceptions.NotFound("Child %s not found!" % name)

    def _supported_type(self,obj):
        """
        An internal function to check that the given object is a supported for this Tree. 
        This is used in every __add__ operation to check whether the object can be added to the tree.
        This function should be overloaded by a subclass if the supported types need to be changed.
        @return: True if object is supported, otherwise false.  
        """
        return isinstance(obj, (ObjectContainer,ContainerBase))

    def _default_object(self,name):
        """
        An internal function to create a default object for this container in case of __add_to_path__, which
        creates the intermediate objects automatically. 
        This function should be overloaded by a subclass if the default object need to be changed.
        @return: A new object.  
        """
        return ObjectContainer(name)

    def _find_parent(self, **kwargs):
        """
        find a _parent object by arguments. You can define any number of object attributes that 
        have to match to the object. 
        Example1:
           _find_parent(foobar=True) searches for a _parent
          object which has a member attribute foobar and its value is True. 
        Example2:
           _find_parent(name="test") searches for a _parent
          object which has a member attribute name and its value is "test". 
        Example3: type is a special case
           _find_parent(type=Configuration) searches for a _parent
          object which is an instance of Configuration (checked with isinstance). 
        @param kwargs: 
        @return: The object that matches the arguments
        @raise exceptions.NotFound: When no matching parent is found
        """
        type = kwargs.get('type', None)
        if hasattr(self,'_parent') and self._parent != None:
            found = True
            for key in kwargs.keys():
                try:
                    # handle type as a special case
                    if key == 'type':
                        if not isinstance(self._parent, kwargs.get(key)):
                            found = False
                            break
                    elif key == 'match':
                        if not self._parent == kwargs.get(key):
                            found = False
                            break
                    elif not getattr(self._parent, key) == kwargs.get(key):
                        found = False
                        break
                except AttributeError:
                    found = False
                    break
            if found:
                return self._parent
            else:
                return self._parent._find_parent(**kwargs)
        else:
            raise exceptions.NotFound("Parent not found!")

    def _find_parent_or_default(self, default=None,**kwargs):
        """
        Calls internally the find parent function, which is encapsulated with try except 
        returns the given default value if find parent raises NotFound exception. 
        """
        try:
            return self._find_parent(**kwargs)
        except exceptions.NotFound:
            return default

    def set_ref(self,ref):
        """
        @param ref: The new reference of the object
        """
        self._name = ref
        self.ref = ref

    def get_ref(self):
        """
        @return: The reference of the object.
        """
        return self.ref

    def has_ref(self, ref):
        """
        Check if object container contains the given reference.
        @param ref: reference
        """
        return self._has(ref)

class ObjectProxyContainer(ObjectProxy,ObjectContainer):
    """
    Combines the Container and Proxy classes to one.
    """
    def __init__(self,obj=None,name=""):
        """
        """
        ObjectContainer.__init__(self,name)
        ObjectProxy.__init__(self,obj)

    def __getattr__(self,name):
        """
        First check if the requested attr is a children then 
        direct all not found attribute calls to the sub object getattr
        """
        try:
            return self.__dict__['_children'][name] 
        except KeyError:
            return getattr(self._obj,name)

class LoadContainer(ContainerBase):
    """
    This class is meant for loading & unloading an object(s), to a ObjectContainer. 
    The loading is done if the object container methods are accessed.
    """
    def __init__(self, path, store_interface=None):
        """
        @param path: the path which is used in loading
        @param store_interface: the loading interface object, which is used. 
        Expects load(path) and dump(obj) functions  
        """
        super(LoadContainer, self).__init__()
        self._parent = None
        self._container = None
        self._storeint = store_interface
        self._respath = path
    
    def __getattr__(self,name):
        """
        Load the container objects if they are not allready loaded
        """
        if not self._container:
            self._load()
        return getattr(self._container,name)
    
    def _load(self):
        """ If the loading of the object fails => Raise an InvalidObject exception """ 
        try:
            self._container = ObjectContainer()
            # this should be modified to support loading multiple elements 
            intf = self.get_store_interface()
            # Do not try to load the objects if interface cannot be found
            if intf:
                obj = intf.load(self.get_full_path())
                self._container._add(obj)
        except exceptions.NotResource,e:
            logging.getLogger('cone').warning("Loading %s from parent %s failed! %s" % (self.path,self.get_parent_path(), e))
            raise exceptions.InvalidObject("Invalid configuration object %s" % self.path)

    def _unload(self):
        # go through objects in the container
        intf = self.get_store_interface()
        for obj in self._container._objects():
            # remove the parent link 
            obj._parent = None
            if intf:
                intf.unload(self.get_full_path(), obj)
            self._container._remove(obj._name)
        # set the container back to None
        self._container = None
        
    def get_store_interface(self):
        if not self._storeint and self._parent:
            try:
                self._storeint = self._parent.get_store_interface()
            except exceptions.NotFound:
                # If project is not found, let the store interface be None 
                pass
        return self._storeint

    def get_parent_path(self):
        """
        Return the path of the configuration resource
        """
        if self._parent:
            return utils.resourceref.get_path(self._parent.get_path())
        else:
            return ""

    def get_full_path(self, obj=None):
        """
        Return the path of the configuration resource
        """
        if obj != None:
            try:
                return obj.get_full_path()
            except AttributeError:
                pass
        # default path processing returns the fullpath of this elem
        parent_path = self.get_parent_path() 
        return utils.resourceref.join_refs([parent_path,self.get_path()])


class LoadLink(ContainerBase):
    """
    This class is meant for loading & unloading an object(s), to a ObjectContainer. 
    The loading is done if the object container methods are accessed.
    """
    def __init__(self, path, store_interface=None):
        """
        @param path: the path which is used in loading
        @param store_interface: the loading interface object, which is used. 
        Expects load(path) and dump(obj) functions  
        """
        super(LoadLink, self).__init__()
        self._parent = None
        self._loaded = False
        self._storeint = store_interface
        self._respath = path
    
    def populate(self):
        """
        Populate the object to the parent
        """
        if self._parent == None:
            raise exceptions.NoParent("Cannot populate a LoadLink object without existing parent object")
        if not self._loaded:
            for obj in self._load():
                self._parent._add(obj)
    
    def _load(self):
        """ If the loading of the object fails => Raise an InvalidObject exception """ 
        objs = []
        try:
            # this should be modified to support loading multiple elements 
            intf = self.get_store_interface()
            # Do not try to load the objects if interface cannot be found
            if intf:
                obj = intf.load(self.get_full_path())
                objs.append(obj)
        except exceptions.NotResource,e:
            logging.getLogger('cone').warning("Loading %s from parent %s failed! %s" % (self.path,self.get_parent_path(), e))
            raise exceptions.InvalidObject("Invalid configuration object %s" % self.path)
        return objs
    
    def _unload(self):
        pass
    
    def get_store_interface(self):
        if not self._storeint and self._parent:
            try:
                self._storeint = self._parent.get_store_interface()
            except exceptions.NotFound:
                # If project is not found, let the store interface be None 
                pass
        return self._storeint

    def get_parent_path(self):
        """
        Return the path of the configuration resource
        """
        if self._parent:
            return utils.resourceref.get_path(self._parent.get_path())
        else:
            return ""

    def get_full_path(self, obj=None):
        """
        Return the path of the configuration resource
        """
        if obj != None:
            try:
                return obj.get_full_path()
            except AttributeError:
                pass
        # default path processing returns the fullpath of this elem
        parent_path = self.get_parent_path() 
        return utils.resourceref.join_refs([parent_path,self.get_path()])


class LoadProxy(ContainerBase):
    """
    This class is meant for representing any object loading & unloading an object, 
    when it is actually needed.  
    object 
    """
    def __init__(self, path, store_interface=None):
        """
        @param path: the path which is used in loadin
        @param store_interface: the loading interface object, which is used. 
        Expects load(path) and dump(obj) functions  
        """
        self.set('_obj', None)
        self.set('_parent', None)
        self.set('path', path)
        self.set('_storeint', store_interface)

    def __getattr__(self,name):
        """
        direct all not found attribute calls to the sub object getattr
        """
        if not self._obj: 
            self._load()
        return getattr(self._obj,name)

    def __getstate__(self):
        """
        Return a state which should have sufficient info to load the proxy object but 
        dont serialize the object itself.
        """
        state = {}
        state['path'] = self.path
        state['_obj'] = None
        # state['_parent'] = self._parent
        state['_storeint'] = self._storeint
        return state
    
    def __setstate__(self, state):
        self.set('_obj', state.get('_obj',None))
        self.set('_storeint', state.get('_storeint',None))
        self.set('_parent', state.get('_parent',self._storeint))
        self.set('path', state.get('path',''))

    def __setattr__(self, name, value):
        """
        direct attribute setting calls to the sub object setattr
        """
        if not self._obj: 
            self._load()
        setattr(self._obj,name,value)

    def __delattr__(self, name):
        """
        direct attribute setting calls to the sub object setattr
        """
        if not self._obj: 
            self._load()
        delattr(self._obj,name)

    def _set_parent(self, newparent):
        """
        @param newparent:  The new parent object
        @return: None
        """
        self.set('_parent',newparent)
        if self._obj:
            self._obj._parent = self._parent

    def _set_obj(self, obj):
        self.set('_obj',obj)
        # set the same _parent for the actual object as is stored for the proxy
        if self._obj:
            self._obj._parent = self._parent
            self._obj.set_path(self.path)

    def _get_obj(self):
        if not self._obj: 
            self._load()
        return self._obj

    def _load(self):
        # Should the loading of layer external resources be supported?
        # E.g. resources with absolute path relative to the storage (starts with slash)
        """ If the loading of the object fails => Raise an InvalidObject exception """ 
        try:
            obj = self.get_store_interface().load(self.fullpath)
            self._set_obj(obj)
            obj.set_ref(utils.resourceref.to_objref(self.path))
        except exceptions.NotResource,e:
            logging.getLogger('cone').warning("Loading %s from parent %s failed! %s" % (self.path,self.get_parent_path(), e))
            raise exceptions.InvalidObject("Invalid configuration object %s" % self.path)

    def _unload(self):
        if self._obj:
            self.get_store_interface().unload(self.fullpath, self._obj)
            self.set('_obj',None)

    def get_store_interface(self):
        if not self._storeint:
            self.set('_storeint',self._parent.get_store_interface())
        return self._storeint

    def set(self,name,value):
        """
        Proxy has a specific attribute setting function, because by default all attributes are 
        stored to the actual proxy object  
        """
        self.__dict__[name] = value

    def get(self,name):
        """
        Proxy has also a specific attribute getting function, because by default all attributes are 
        stored to the actual proxy object  
        """
        return self.__dict__[name]

    def save(self):
        if hasattr(self._obj,'save'):
            self._obj.save()
        self._unload()

    def close(self):
        if hasattr(self._obj,'close'):
            self._obj.close()

    def get_parent_path(self):
        """
        Return the path of the configuration resource
        """
        if self._parent:
            return utils.resourceref.get_path(self._parent.get_path())
        else:
            return ""

    def get_path(self):
        """
        Return the path of the configuration resource
        """
        if self._obj:
            return self._obj.get_path()
        else:
            return self.path

    @property
    def fullpath(self):
        """
        Return the path of the configuration resource
        """
        try:
            return self._obj.get_full_path() 
        except AttributeError:
            parent_path = self.get_parent_path() 
            return utils.resourceref.join_refs([parent_path,self.path])
