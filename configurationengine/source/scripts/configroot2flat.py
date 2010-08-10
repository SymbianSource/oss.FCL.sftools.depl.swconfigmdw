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
#!/usr/bin/env python
## 
# @author Teemu Rytkonen

from optparse import OptionParser
from cone.action import configroot2flat

def get_parser():
    parser = OptionParser()
    parser.add_option("-c", "--configuration",
                        dest="configs",
                        action="append",
                        help="Defines the name of the configuration for the action, can be "\
                             "specified multiple times to include multiple configurations.",
                        metavar="CONFIG",
                        default=[])
    
    parser.add_option("--config-wildcard",
                      action="append",
                      dest="config_wildcards",
                      help="Wildcard pattern for including configurations, e.g. "\
                           "product_langpack_*_root.confml",
                      metavar="WILDCARD",
                      default=[])
    
    parser.add_option("--config-regex",
                      action="append",
                      dest="config_regexes",
                      help="Regular expression for including configurations, e.g. "\
                           "product_langpack_\\d{2}_root.confml",
                      metavar="REGEX",
                      default=[])
    
    parser.add_option("-p", "--project",\
                       dest="project",\
                       help="defines the location of current project. Default is the current working directory.",\
                       default=".",\
                       metavar="STORAGE")
    return parser

def main():
    """ 
    Configuration root flattener.
    """
    parser = get_parser()
    options, _ = parser.parse_args()
    
    action = configroot2flat.ConeConfigroot2FlatAction(
        project          = options.project,
        configs          = options.configs,
        config_wildcards = options.config_wildcards,
        config_regexes   = options.config_regexes)
        
    try:
        status = action.run()
        if status:
            action.save()
            action.close()
    except configroot2flat.Configroot2FlatFailed, e:
        parser.error(str(e))
    
if __name__ == "__main__":
    main()