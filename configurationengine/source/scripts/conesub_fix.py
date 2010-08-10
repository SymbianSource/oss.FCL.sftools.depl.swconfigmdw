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
from optparse import OptionParser, OptionGroup
import cone_common
from cone.public import api, exceptions
from cone.action import fix
from cone.validation import confmlvalidation

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

VERSION     = '1.0'

logger    = logging.getLogger('cone')

def main():
    """ Run automatic fixes for configurations. """
    parser = OptionParser(version="ConE validate %s" % VERSION)
    
    parser.add_options(cone_common.COMMON_OPTIONS)
    
    parser.add_option("-c", "--configuration",
                        dest="configuration",
                        help="Defines the name of the configuration for the action",
                        metavar="CONFIG")

    parser.add_option("-p", "--project",
                       dest="project",
                       default=".",
                       help="defines the location of current project. Default is the "\
                            "current working directory.",
                       metavar="STORAGE")
    
    group = OptionGroup(parser, 'Fix options',
                        'The fix action is intended for performing fixes on a     '\
                        'configuration.                                           ')

    group.add_option("--print-available-fixes",
                     action="store_true",
                     help="Print all configuration fixer objects available.",
                     default=False)

    group.add_option("--exclude-filter",
                     action="append",
                     help="Exclude problems by given filter. "\
                          "Examples: --exclude-filter=schema, --exclude-filter=schema.implml, --exclude-filter=schema.confml, --exclude-filter=schema.implml.ruleml",
                     default=None)

    group.add_option("--include-filter",
                     action="append",
                     help="Include problems by given filter."\
                          "Examples: --include-filter=schema.implml, --include-filter=schema.implml.ruleml",
                     default=None)

    parser.add_option_group(group)
    (options, _) = parser.parse_args()
    
    cone_common.handle_common_options(options)
    

    if options.print_available_fixes:
        print "Available fixers:"
        for fix_class in confmlvalidation.get_fixer_classes():
            print "%s: %s" % (fix_class, fix_class.__doc__)
        return 0
    else:
        if not options.configuration:
            parser.error("A configuration must be given! Use -c / --configuration option.")
        action = fix.ConeFixAction(include_filter=options.include_filter or [],
                               exclude_filter=options.exclude_filter or [],
                               username=options.username,
                               password=options.password,
                               project_name=options.project,
                               configuration_name=options.configuration)
        
        status = action.run()
        if status:
            action.save()
            action.close()
            
        return status
    

if __name__ == "__main__":
    main()
