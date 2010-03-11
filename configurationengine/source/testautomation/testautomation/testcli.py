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


from optparse import OptionParser, OptionGroup
import os
import sys
import shutil
import unittest

def run(suite):
    parser = OptionParser(version="%%prog %s" % 1.0)
    parser.add_option("-f","--format",\
                    dest="format",\
                    help="The output format of the test results, which can be either stdout or xml file [stdout|xml]. Default is stdout",\
                    metavar="FORMAT",\
                    default="stdout")
    parser.add_option("-o","--output",\
                    dest="output",\
                    help="The output directory of xml output. Default is test-results",\
                    metavar="FOLDER",\
                    default="test-results")

    (options, args) = parser.parse_args()
    results = None
    if options.format == "stdout":
        results = unittest.TextTestRunner(verbosity=2).run(suite)
    elif options.format == "xml":
        if not os.path.exists(options.output):
            os.mkdir(options.output)
        else:
            shutil.rmtree(options.output)
            os.mkdir(options.output)
        runner = unittest.TextTestRunner(None,options.output)#Add support for xmlrunner
        results = runner.run(suite)
        print "Output file created %s" % os.path.join(options.output,runner.filename)
    else:
        parser.error("Unrecognized output format %s! See --help." % parser.format)
    
    if results.errors > 0 or results.failures > 0:
        return -1
    
    
  
 
