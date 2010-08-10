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
    nose.main(config=conf)

