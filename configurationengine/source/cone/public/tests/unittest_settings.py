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
Test the configuration
"""
import unittest
import string
import StringIO
import sys,os
import __init__

from cone.public import api,exceptions,settings

import ConfigParser
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

configdata = \
'''
[DEFAULT]
output_root=output
output_subdir=
plugin_output=
output=%(output_root)s/%(output_subdir)s/%(plugin_output)s

plugin_targets = 'rofs2','rofs3'

generate_targets = 'rofs3'
generate_layers  = -1
generate_impls   =


[CRML]
plugin_output=%(plugin_output)s/private/1234567
tags={target : [%(plugin_targets)s]}

[CONTENT]
tags={target : ['rofs2','rofs3','uda']}

[ROFS3]
output_subdir=rofs3
'''

imagedefault = \
'''
[DEFAULT]
subdir=content
foobar=fs/content
'''

class TestConfigParser(unittest.TestCase):
    def tearDown(self):
        settings.SettingsFactory.clear()
        
    def test_config_parser_from_string(self):
        config = ConfigParser.ConfigParser()
        config.readfp(StringIO.StringIO(configdata))
        config.readfp(StringIO.StringIO(imagedefault))
        self.assertEquals(config.get('ROFS3','output'),'output/rofs3/')
        self.assertEquals(config.get('CRML','tags'),"{target : ['rofs2','rofs3']}")

    def test_get_parser(self):
        settings.SettingsFactory.defaultconfig = os.path.join(ROOT_PATH,'test_defaults.cfg')
        s = settings.SettingsFactory.cone_parser()
        cs = settings.ConeSettings(s)
        self.assertEquals(s.get('DEFAULT','output'),'output//')

    def test_cone_settings(self):
        settings.SettingsFactory.defaultconfig = os.path.join(ROOT_PATH,'test_defaults.cfg')
        s = settings.SettingsFactory.cone_parser()
        cs = settings.ConeSettings(s)
        self.assertEquals(cs.get('output'),'output//')
        self.assertEquals(cs.get('foobar'),None)
        self.assertEquals(cs.get('foobar', 'test'),'test')

    def test_cone_settings_with_invalid_section(self):
        settings.SettingsFactory.defaultconfig = os.path.join(ROOT_PATH,'test_defaults.cfg')
        settings.SettingsFactory.configsettings = None
        s = settings.SettingsFactory.cone_parser()
        cs = settings.ConeSettings(s,'FOOBAR')
        self.assertEquals(cs.get('output'),'output//')
        self.assertEquals(cs.get('foobar'),None)
        self.assertEquals(cs.get('foobar', 'test'),'test')
        self.assertEquals(cs.get('output','',{'output_subdir':'content',
                                              'output_subdir':'content'}),'output/content/')

if __name__ == '__main__':
      unittest.main()
      
