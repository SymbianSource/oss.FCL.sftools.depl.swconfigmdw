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
import os
import logging
import ConfigParser

DEFAULT_SECTION = 'DEFAULT'
class ConeSettings(object):
    def __init__(self, parser, section=DEFAULT_SECTION):
        self.parser = parser
        self.section = section
    
    def get(self, property, default=None, vars=None):
        """
        Try to get a single property from the ConeSettings section. The method support the
        ConfigParser interpolation of variables and deliver extra variables via the vars param.
       
        1. Try to get the property from configured section.
        2. If section is not found try to get it from DEFAULT section.
        3. Still if property is not found return the default values
        @param property: the name of the setting property get
        @param default: the default value to return if the property is not found from settings
        @param vars: a dictionary of variables that are given to the ConfigParser get 
        for interpolation. e.g. {'output':'testing'}.
        
        """
        try:
            return self.parser.get(self.section, property, False, vars)
        # if the section is not found try to use default
        except ConfigParser.NoSectionError:
            try:
                return self.parser.get(DEFAULT_SECTION, property, False, vars)
            except ConfigParser.NoOptionError:
                if default != None:
                    return self.parser._interpolate(DEFAULT_SECTION,property,default,vars)
                else:
                    return default
        # if the option is not found return the default value
        except ConfigParser.NoOptionError:
            if default != None:
                return self.parser._interpolate(DEFAULT_SECTION,property,default,vars)
            else:
                return default
            #return default
            

class SettingsFactory(object):
    configsettings = None
    configpath    = ''
    defaultconfig = 'cone_defaults.cfg'
    
    @classmethod
    def get_defaultconfig_path(cls):
        return os.path.join(cls.configpath,cls.defaultconfig)
    
    @classmethod
    def cone_parser(cls):
        """
        Get a singleton instance of ConfigParser.
        """
        if not cls.configsettings:
            cls.configsettings = ConfigParser.ConfigParser()
            
            try:
                cls.configsettings.readfp(open(cls.get_defaultconfig_path()))
            except IOError:
                logging.getLogger('cone').warning("Could not read default configuration file %s" % cls.get_defaultconfig_path())
        return cls.configsettings
    
    @classmethod
    def clear(cls):
        """
        Clear everything back to default so that the next time the settings are re-parsed.
        
        This method is provided for unit testing purposes.
        """
        cls.configsettings = None
        cls.configpath    = ''
        cls.defaultconfig = 'cone_defaults.cfg'