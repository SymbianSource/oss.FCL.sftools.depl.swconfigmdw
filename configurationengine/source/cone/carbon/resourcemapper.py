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
import re
import logging

class CarbonResourceMapper(object):
    def __init__(self):
        self.CARBON_RESOURCE_TYPE_MAP = {'configurationroot' : self.map_carbon_configurationroot,
                             'configurationlayer' : self.map_carbon_configurationlayer,
                             'featurelist' : self.map_carbon_featurelist}
        self.CONFML_RESOURCE_TYPE_MAP = {'configurationroot' : self.map_confml_configurationroot,
                             'configurationlayer' : self.map_confml_configurationlayer,
                             'featurelist' : self.map_confml_featurelist}

    def map_carbon_resource(self, resourcepath):
        for resourceext in self.CARBON_RESOURCE_TYPE_MAP:
            if resourcepath.endswith(resourceext):
                return self.CARBON_RESOURCE_TYPE_MAP[resourceext](resourcepath)
        return resourcepath

    def map_confml_resource(self, resourcetype, resourcepath):
        return self.CONFML_RESOURCE_TYPE_MAP[resourcetype](resourcepath)

    def map_carbon_configurationroot(self, resourcepath):
        return resourcepath.replace('.configurationroot', '.confml')

    def map_carbon_configurationlayer(self, resourcepath):
        return resourcepath.replace('.configurationlayer', '/root.confml')

    def map_carbon_featurelist(self, resourcepath):
        return "featurelists/%s" % resourcepath.replace('.featurelist', '.confml')

    def map_confml_configurationroot(self, resourcepath):
        return resourcepath.replace('.confml', '.configurationroot')

    def map_confml_configurationlayer(self, resourcepath):
        return resourcepath.replace('/root.confml', '.configurationlayer')

    def map_confml_featurelist(self, resourcepath):
        path = resourcepath.replace('featurelists/','').replace('.confml', '')
        version_identifier = 'working'
        m = re.match('^(.*) \((.*)\)', path)
        # if the resourcepath does not have version information 
        # use default WORKING
        if m:
            path = m.group(1)
            version_identifier = m.group(2)
        return '%s (%s).featurelist' % (path, version_identifier)
