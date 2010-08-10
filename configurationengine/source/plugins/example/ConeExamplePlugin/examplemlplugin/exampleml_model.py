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
import sys
import logging

from cone.public import utils

class Output(object):
    """
    Class representing an ExampleML output element.
    """
    
    def __init__(self, file, encoding, text, lineno=None):
        self.file = file
        self.encoding = encoding
        self.text = text
        self.lineno = lineno
    
    def get_refs(self):
        """
        Return a list of all ConfML refs used in this output object.
        """
        return utils.extract_delimited_tokens(self.text)
    
    def get_output_file(self, output_dir, config):
        """
        Return the path of the output file specified by this output object.
        """
        # Expand ConfML references
        file = utils.expand_refs_by_default_view(self.file, config.get_default_view())
        return os.path.normpath(os.path.join(output_dir, file))
    
    def write_to_file(self, output_dir, context):
        """
        Write the text file specified by this output object to the
        given output directory.
        """
        # Get the actual output path and encoding
        file_path = self.get_output_file(output_dir, context.configuration)
        encoding = utils.expand_refs_by_default_view(self.encoding, context.configuration.get_default_view())
        
        # Generate the binary data to write
        text = utils.expand_refs_by_default_view(self.text, context.configuration.get_default_view())
        data = text.encode(encoding)
        
        
        # Write the file.
        f = context.create_file(file_path, mode="wb")
        try:        f.write(data)
        finally:    f.close()
    
    def __eq__(self, other):
        if type(self) is type(other):
            for varname in ('file', 'encoding', 'text'):
                if getattr(self, varname) != getattr(other, varname):
                    return False
            return True
        else:
            return False
    
    def __ne__(self, other):
        return not (self == other)
    
    def __repr__(self):
        return "Output(file=%r, encoding=%r, text=%r)" % (self.file, self.encoding, self.text)
