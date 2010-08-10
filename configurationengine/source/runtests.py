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
# Script for running all ConE unit tests (cone, plug-ins and scripts).
#

if __name__ == '__main__':
    import nose
    nose.run(argv=['collector',
                    'cone',
                    'scripts',
                    'plugins/common',
                    'plugins/example',
                    'plugins/symbian',
                    'testautomation/testautomation',
                    '--include=unittest', 
                    '--with-xunit',
                    '--xunit-file=cone-alltests.xml',
                    '--verbosity=3'])