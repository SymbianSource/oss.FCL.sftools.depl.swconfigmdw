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
'''
Configuration flattener
'''

import re
import os
import sys
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

import __init__

from cone.public import exceptions,plugin,utils,api
import copy



class ConfigurationFlattener():
    """
    Configuration flattener
    """
    
    def _init(self):
        self.logger = logging.getLogger('cone.gcfml(%s)' % self.ref)
        pass
        

    def flat(self, conf_from_org, settings, to_config):
        """
        Flats configuration to one element xml element
        """
        """ 
        Get the default view
        Create the new flat configuration 
         """
        dview_from = conf_from_org.get_default_view()
        
        """ Go through the required settings """
        for setting in settings:
            setting_name = setting.replace('/', '.')
            try:
                for fea in dview_from.get_features(setting_name):
                    """ Add the given feature ref and its children """
                    newfea = copy.copy(fea._obj)
                    to_config.add_feature(newfea, fea.namespace)
                    for subfeaname in fea.list_features():
                        subfea = fea.get_feature(subfeaname)
                        newfea = copy.copy(subfea._obj)
                        to_config.add_feature(newfea, subfea.namespace)
            except exceptions.NotFound, e:
                logging.getLogger('cone.gcfml').warning('Failed to get feature: %s , %s %s' % (setting_name, type(e), e) )
            except Exception, e:
                logging.getLogger('cone.gcfml').warning('Failed to flat feature: %s , %s %s' % (setting_name, type(e), e) )
                
        """ Copy all data values from the existing configuration to the new configuration """
        toview = to_config.get_default_view()
        for fea in toview.get_features('**'):
            fromfea = dview_from.get_feature(fea.fqr)
            # If the value is an empty list, don't add it.
            # This is because an empty list means that we have
            # a sequence setting or sequence sub-setting that doesn't have
            # any contents, and calling set_value() would create an empty
            # data element to mark the sequence as empty, as the
            # ConfML specification says
            val = fromfea.get_value()
            if val not in (None, []):
                fea.set_value(val)
        return to_config

    def create_configuration(self, conf_from_org, settings, path="tempfile.confml"):
        """
        Flats configuration to one feature and data confml
        """
        """ 
        Get the default view
        Create the new flat configuration 
         """
        prj = conf_from_org.get_project()
        flat = prj.create_configuration(path)
        (root,ext) = os.path.splitext(path)
        dataname = "%s_data%s" % (root,ext)
        flat.create_configuration(dataname)
        self.flat(conf_from_org, settings, flat)
        flat.close()
