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


import os,sys,unittest
from optparse import OptionParser, OptionGroup

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT_PATH,'..'))
#sys.path.insert(0, os.path.join(ROOT_PATH,'../testautomation'))

import cone.storage.tests
import cone.core.tests
import cone.confml.tests
import cone.carbon.tests
import cone.public.tests
#from testautomation import testcli

def collect_suite():
    suite = unittest.TestSuite()
    suite.addTests(cone.storage.tests.collect_suite())
    suite.addTests(cone.core.tests.collect_suite())
    suite.addTests(cone.confml.tests.collect_suite())
    suite.addTests(cone.carbon.tests.collect_suite())
    suite.addTests(cone.public.tests.collect_suite())
    return suite

if __name__ == '__main__':
    import nose
    setuptools_incompat = ('report', 'prepareTest',
                           'prepareTestLoader', 'prepareTestRunner',
                           'setOutputStream')

    plugins = nose.plugins.manager.RestrictedPluginManager(exclude=setuptools_incompat)
    allfiles = nose.config.all_config_files() + ['nose_unittests.cfg']
    conf = nose.config.Config(files=allfiles,
                  plugins=plugins)
    conf.configure(argv=['collector'])
    print "conf :", conf.include
    nose.main(config=conf)

#if __name__ == '__main__':
#    testcli.run(collect_suite())

