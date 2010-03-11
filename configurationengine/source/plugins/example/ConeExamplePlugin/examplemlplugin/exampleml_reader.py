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

from cone.public import exceptions, plugin
import exampleml_impl
import exampleml_model

class ExamplemlReader(plugin.ReaderBase):
    NAMESPACE = 'http://www.example.org/xml/exampleml/1'
    FILE_EXTENSIONS = ['exampleml']
    
    @classmethod
    def read_impl(cls, resource_ref, configuration, etree):
        reader = ExamplemlReader()
        outputs = reader._read_outputs(etree)
        return exampleml_impl.ExamplemlImpl(resource_ref, configuration, outputs)
    
    def _read_outputs(self, elem):
        """
        Read output objects from the given XML element.
        """
        result = []
        for subelem in elem.findall("{%s}output" % self.NAMESPACE):
            result.append(self._read_output_elem(subelem))
        return result
    
    def _read_output_elem(self, elem):
        """
        Read an <output> element into an Output object.
        """
        file = elem.get('file')
        if file is None:
            raise exceptions.ParseError("Element <output> does not have the mandatory 'file' attribute")
        return exampleml_model.Output(file     = file,
                                      encoding = elem.get('encoding', 'UTF-8'),
                                      text     = elem.text or '')