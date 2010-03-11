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


"""
Methods for Mapping Carbon model to other data model objects 
"""
from cone.public import api, exceptions, container, utils
from cone.public.mapping import BaseMapper
from cone.carbon import model as carbonmodel

""" Carbon to confml model mapping is done in Carbon2confml """
from cone.confml import model 

class Confml2carbon(object):
    """
    Carbon2confml class maps Carbon model object to confml model objects.  
    """
    def __init__(self):
        self.MAPPING_TABLE = {model.ConfmlConfiguration: self.configuration,
                              model.ConfmlFeature: self.setting,
                              model.ConfmlSetting: self.setting,
                              model.ConfmlIntSetting: self.setting,
                              model.ConfmlBooleanSetting: self.setting,
                              model.ConfmlSelectionSetting: self.setting}
        pass

    def map_object(self, object):
        """
        Return a confml model object from Carbon object
        """
        try:
            return self.MAPPING_TABLE[object.__class__](object)
        except KeyError:
            return object

    def configuration(self, object):
        """
        Map a CarbonConfiguration object to a ConfmlConfiguration
        """
        mapdict = object._dict()
        if object.meta and object.meta.get('type') == 'featurelist':
            mapobj = object._clone(class_instance=carbonmodel.FeatureList, recursion=True)
        else:
            mapobj = object._clone(class_instance=carbonmodel.CarbonConfiguration, recursion=True)
        return mapobj

    def setting(self, object):
        """
        Map a CarbonSetting object to a ConfmlSetting
        """
        mapdict = object._dict()
        if object.__class__ == model.ConfmlFeature:
            mapobj = object._clone(class_instance=carbonmodel.CarbonFeature, recursion=True)
        elif object.__class__ == model.ConfmlIntSetting:
            mapobj = object._clone(class_instance=carbonmodel.CarbonIntSetting, recursion=True)
        elif object.__class__ == model.ConfmlBooleanSetting:
            mapobj = object._clone(class_instance=carbonmodel.CarbonBooleanSetting, recursion=True)
        elif object.__class__ == model.ConfmlSelectionSetting:
            mapobj = object._clone(class_instance=carbonmodel.CarbonSelectionSetting, recursion=True)
        elif object.__class__ == model.ConfmlSetting:
            mapobj = object._clone(class_instance=carbonmodel.CarbonSetting, recursion=True)
        else:
            raise exceptions.IncorrectClassError('Cannot find a mapping object for this class %s!' % object.__class__)
        return mapobj

MAPPERS =  \
{ 'carbon' : Confml2carbon,
  'confml' : BaseMapper
}

