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


import posixpath
import datetime


"""
Base class for Carbon specific elements.
Attributes:
"""
from cone.public import api, exceptions, container, utils
from cone.confml import model as confmlmodel
from cone.carbon import resourcemapper

class ResourceList(object):
    def __init__(self):
        self.resources = {}

    def add_resource(self,resource):
        self.resources[resource.get_path()] = resource

    def get_resource(self,path):
        return self.resources[path]

    def remove_resource(self,path):
        del self.resources[path]

    def list_resources(self):
        return self.resources.keys()

    def __len__(self):
        return len(self.resources)

    def __getitem__(self, key):
        return self.resources[key]

    def __setitem__(self, key, value):
        self.resources[key] = value

    def __delitem__( self, key):
        del self.resources[key]

    def __iter__(self):
        return iter(self.resources.values())


class ConfigurationResource(object):
    FILE_EXTENSION = '/root.confml'
    def __init__(self, **kwargs):
        self.name          = kwargs.get('configuration_name', None)
        self.path          = kwargs.get('path', None)
        self.parent_config = kwargs.get('parent_config', None)
        self.version       = kwargs.get('version_identifier', None)

    def get_path(self):
        path = utils.resourceref.remove_begin_slash(self.path)
        path = utils.resourceref.remove_end_slash(path)
        return path + self.FILE_EXTENSION

    def __str__(self):
        return "%s = %s : %s:%s" % (self.get_path(),self.path,self.name, self.version)

class FeatureListResource(object):
    CONFML_EXTENSION = '.confml'
    CARBON_EXTENSION = '.featurelist'
    def __init__(self, **kwargs):
        self.path                   = kwargs.get('path', None)
        self.version_title          = kwargs.get('version_title', None)
        self.type                   = kwargs.get('type', None)
        self.list_id                = kwargs.get('list_id', None)
        self.expanded               = kwargs.get('expanded', None)
        self.list_version_id        = kwargs.get('list_version_id', None)
        self.version_identifier     = kwargs.get('version_identifier', None)
        self.is_latest_version      = kwargs.get('is_latest_version', None)
        self.can_be_released        = kwargs.get('can_be_released', None)
        self.has_external_relations = kwargs.get('has_external_relations', None)

    def get_path(self):
        path = utils.resourceref.remove_begin_slash(self.version_title)
        path = utils.resourceref.remove_end_slash(path)
        return path + self.CONFML_EXTENSION

    def get_carbon_path(self):
        path = utils.resourceref.remove_begin_slash(self.version_title)
        path = utils.resourceref.remove_end_slash(path)
        return path + self.CARBON_EXTENSION

    def __str__(self):
        return "%s = %s : %s" % (self.get_path(),self.path,self.version_title)

class CarbonElement(object):
    pass

    def _get_mapper(self,modelname):
        """
        Return a instance of appropriate mapper for given model.
        """
        mapmodule = __import__('cone.carbon.mapping')
        return mapmodule.carbon.mapping.MAPPERS[modelname]()


class CarbonConfiguration(CarbonElement, confmlmodel.ConfmlConfiguration):
    def __init__(self, ref='', **kwargs):
        super(CarbonConfiguration, self).__init__(ref, **kwargs)
        if self.meta == None:
            self.meta = {}
        self.name = kwargs.get('name') or utils.resourceref.remove_ext(utils.resourceref.psplit_ref(self.path)[-1])
        if self.type == None:
            self.type = 'configurationroot'
        self._version_identifier = kwargs.get('version_identifier', None)

    @property
    def version_identifier(self):
        if self._version_identifier == None:
            dt = datetime.datetime.today()
            self._version_identifier = "%dwk%02d" % dt.isocalendar()[0:2]
        return self._version_identifier

    def get_type(self):
        if self.meta and self.meta.get('type'):
            return self.meta.get_property_by_tag('type').value
        else:
            return 'configurationroot'
        
    def set_type(self, type):
        if not self.meta:
            self.meta = {}
        self.meta.set_property_by_tag('type',type)
        
    def del_type(self):
        del self.meta['type']
    
    type = property(get_type, set_type, del_type)

    def get_version_identifier(self):
        if self._version_identifier == None:
            dt = datetime.datetime.today()
            self._version_identifier = "%dwk%02d" % dt.isocalendar()[0:2]
        return self._version_identifier
        
    def set_version_identifier(self, value):
        self._version_identifier = value
        
    def del_version_identifier(self):
        del self._version_identifier
    
    version_identifier = property(get_version_identifier, set_version_identifier, del_version_identifier)

class FeatureList(CarbonConfiguration):
    def __init__(self, ref='', **kwargs):
        if not kwargs.get('path'):
            if kwargs.get('name'):
                kwargs['path']          = str(kwargs.get('name', '')+'.confml')
            else:
                kwargs['path'] = ref
        
        pathmapper = resourcemapper.CarbonResourceMapper()
        tpath = pathmapper.map_confml_resource("featurelist",kwargs['path'])
        kwargs['path'] = pathmapper.map_carbon_resource(tpath)

        super(FeatureList, self).__init__(ref, **kwargs)
        self._version_identifier = kwargs.get('version_identifier', 'working')
        self.type = 'featurelist'

    def _default_object(self, name):
        return CarbonFeature(name)

class CarbonFeature(CarbonElement, confmlmodel.ConfmlSetting):
    def __init__(self, ref,**kwargs):
        ref = utils.resourceref.to_dottedref(ref)
        super(CarbonFeature,self).__init__(ref,**kwargs)
        

class CarbonSetting(CarbonFeature, confmlmodel.ConfmlSetting):
    def __init__(self, ref,**kwargs):
        super(CarbonSetting,self).__init__(ref,**kwargs)
        self.type = 'boolean'

class CarbonIntSetting(CarbonFeature, confmlmodel.ConfmlIntSetting):
    def __init__(self, ref,**kwargs):
        super(CarbonIntSetting,self).__init__(ref,**kwargs)
        self.type = 'int'

class CarbonBooleanSetting(CarbonFeature, confmlmodel.ConfmlBooleanSetting):
    def __init__(self, ref,**kwargs):
        super(CarbonBooleanSetting,self).__init__(ref,**kwargs)
        self.type = 'boolean'

class CarbonSelectionSetting(CarbonFeature, confmlmodel.ConfmlSelectionSetting):
    def __init__(self, ref,**kwargs):
        super(CarbonSelectionSetting,self).__init__(ref,**kwargs)
        self.type = 'selection'

class CarbonStringSetting(CarbonFeature, confmlmodel.ConfmlSetting):
    def __init__(self, ref,**kwargs):
        super(CarbonStringSetting,self).__init__(ref,**kwargs)
        self.type = 'string'

    pass

def get_mapper(modelname):
    """
    Return a instance of appropriate mapper for given model.
    """
    mapmodule = __import__('cone.carbon.mapping')
    return mapmodule.carbon.mapping.MAPPERS[modelname]()

