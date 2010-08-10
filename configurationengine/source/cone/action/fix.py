
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
import logging

from cone.public import api, exceptions
from cone.validation import confmlvalidation
from cone.validation.problem_type_filter import ProblemTypeFilter

logger    = logging.getLogger('cone')

class ConeFixAction(object):
    def     __init__(self, **kwargs):
        # all action attributes are given as keyword arguments
        self.include_filter = kwargs.get('include_filter',[])
        self.exclude_filter = kwargs.get('exclude_filter',[])
        self.username = kwargs.get('username',None)
        self.password = kwargs.get('password',None)
        self.project_name = kwargs.get('project_name', '.')
        self.configuration_name = kwargs.get('configuration_name', None)
        self.project = kwargs.get('project', None)
        self.config = kwargs.get('configuration', None)
        
        
    def run(self):
        filter = ProblemTypeFilter(includes = self.include_filter,
                                   excludes = self.exclude_filter)
        
        # Open the project if it is not already opened
        if self.project == None:
            storage = api.Storage.open(self.project_name, 
                                       "a", 
                                       username=self.username, 
                                       password=self.password)
            self.project = api.Project(storage)
        if self.config == None:
            if not self.configuration_name:
                logging.getLogger('cone').error("No configuration given! Use -c / --configuration")
                return False
            try:
                self.config  = self.project.get_configuration(self.configuration_name)
            except exceptions.NotFound:
                logging.getLogger('cone').error("No such configuration: %s" % self.configuration_name)
                return False
        
        fixers = confmlvalidation.get_fixer_classes(filter)
        
        vc = confmlvalidation.fix_configuration(self.config, None, fixers)
        
        if vc.fixes:
            print "Fixed %d problem(s). See log for details" % len(vc.fixes)
        else:
            print "No problems to fix found. See log for details"
        return True

    def save(self):
        self.project.save()
        
    def close(self):
        self.project.close()


def get_class():
    return ConeFixAction