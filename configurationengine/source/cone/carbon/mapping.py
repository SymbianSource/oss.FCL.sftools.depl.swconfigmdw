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
from cone.carbon import model

""" Carbon to confml model mapping is done in Carbon2confml """
from cone.confml import model as confmlmodel

class Carbon2confml(object):
    """
    Carbon2confml class maps Carbon model object to confml model objects.  
    """
    def __init__(self):
        self.MAPPING_TABLE = {model.CarbonConfiguration : self.configuration,
                              model.FeatureList : self.configuration,
                              model.CarbonFeature: self.setting,
                              model.CarbonSetting: self.setting,
                              model.CarbonIntSetting: self.setting,
                              model.CarbonBooleanSetting: self.setting,
                              model.CarbonStringSetting: self.setting,
                              model.CarbonSelectionSetting: self.setting}
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
        mapobj = confmlmodel.ConfmlConfiguration(**mapdict)
        return mapobj

    def setting(self, object):
        """
        Map a CarbonSetting object to a ConfmlSetting
        """
        mapdict = object._dict()
        if object.__class__ == model.CarbonFeature:
            mapobj = api.Feature(**mapdict)
        elif object.__class__ == model.CarbonIntSetting:
            mapobj = confmlmodel.ConfmlIntSetting(**mapdict)
        elif object.__class__ == model.CarbonBooleanSetting:
            mapobj = confmlmodel.ConfmlBooleanSetting(**mapdict)
        elif object.__class__ == model.CarbonSelectionSetting:
            mapobj = confmlmodel.ConfmlSelectionSetting(**mapdict)
        elif object.__class__ == model.CarbonStringSetting:
            mapobj = confmlmodel.ConfmlSetting(**mapdict)
        elif object.__class__ == model.CarbonSetting:
            mapobj = confmlmodel.ConfmlSetting(**mapdict)
        else:
            raise exceptions.IncorrectClassError('Cannot find a mapping object for this class %s!' % object.__class__)
        return mapobj

MAPPERS =  \
{ 'confml' : Carbon2confml,
  'carbon' : BaseMapper
}

