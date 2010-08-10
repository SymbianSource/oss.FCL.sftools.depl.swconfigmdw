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

import sys
import logging
import inspect

def load_plugin_classes(entry_point_group, base_class):
    """
    Load plugin classes from plug-in entry points.
    
    @param entry_point_group: Entry point group from which to load
        classes. Each entry point is expected to be an iterable of
        plugin class instances.
    @param base_class: The base class that every loaded class must inherit.
    @return: List of loaded plugin classes.
    """
    log = logging.getLogger('cone')
    log.setLevel(logging.DEBUG)
    validator_classes = []
    
    import pkg_resources
    working_set = pkg_resources.WorkingSet(sys.path)
    for entry_point in working_set.iter_entry_points(entry_point_group):
        class_list = entry_point.load()
        
        # Make sure that the class list is a list
        try:
            class_list = [c for c in class_list]
        except:
            log.warn("Entry point %s:%s is not iterable (%r)" % (entry_point_group, entry_point.name, class_list))
            continue
        
        for i, cls in enumerate(class_list):
            if not inspect.isclass(cls):
                log.warn("Object %d from entry point %s:%s is not a class (%r)" % (i, entry_point_group, entry_point.name, cls))
            elif not issubclass(cls, base_class):
                log.warn("Object %d from entry point %s:%s is not a sub-class of %s.%s (%r)" \
                         % (i, entry_point, entry_point.name,
                            base_class.__module__,
                            base_class.__name__,
                            cls))
            else:
                msg = "Validator class %r loaded from egg entry point %s:%s, item %d" % (cls, entry_point_group, entry_point.name, i)
                log.debug(msg)
                #print msg
                validator_classes.append(cls)
            
    return validator_classes

def filter_classes(classes, filter):
    """
    Filter the given list of validator by the given ProblemTypeFilter object.
    
    @param classes: The class list for filter. Each 
        class is assumed to have a PROBLEM_TYPES attribute that defines
        an iterable of the types of problems that the problem yields.
    @param filter: The filter object to use. Can be None, in which case
        the class list is simply returned back.
    @return: The filtered list.
    """
    if filter == None:
        return classes
    else:
        result = []
        for klass in classes:
            for problem_type in klass.PROBLEM_TYPES:
                if filter.match(problem_type):
                    result.append(klass)
                    break
        return result
