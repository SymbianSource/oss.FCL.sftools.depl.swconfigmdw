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
ExampleML implementation, for use as a template when creating new plug-ins.

The example implementation language simply writes text data into output files
using the specified encoding. The text data may contain ConfML setting references
of the form ${SomeFeature.SomeSetting}.
"""

import os
import sys
import logging

from cone.public import plugin

class ExamplemlImpl(plugin.ImplBase):
    IMPL_TYPE_ID = 'exampleml'

    def __init__(self, resource_ref, configuration, output_objects):
        plugin.ImplBase.__init__(self, resource_ref, configuration)
        self.logger = logging.getLogger('cone.exampleml(%s)' % resource_ref)
        self.output_objects = output_objects
        
    def generate(self, context=None):
        for output in self.output_objects:
            self.logger.debug("Generating '%s'" % output.get_output_file(self.output, self.configuration))
            output.write_to_file(self.output, self.configuration)
    
    def list_output_files(self):
        files = []
        for output in self.output_objects:
            files.append(output.get_output_file(self.output, self.configuration))
        return files

    def get_refs(self):
        refs = []
        for output in self.output_objects:
            refs.extend(output.get_refs())
        return refs
