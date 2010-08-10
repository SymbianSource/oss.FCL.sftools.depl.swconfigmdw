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
'''
Configuration flattener
'''


import os
import sys
import logging
import pkg_resources

pkg_resources.require('lxml')

from cone.public import exceptions

class XsltTransformer():
    """
    XSLT Transformer
    """
    
    def _init(self,ref,configuration):
        self.logger = logging.getLogger('cone.gcfml(%s)' % self.ref)


    def transform_lxml(self, input, xslt, enc, linesep=os.linesep):
        """
        XSLT transform with lxml.
        """
        from lxml import etree
        
        if not enc:
            enc = sys.getdefaultencoding()
        try:
            xslt_doc = etree.parse(xslt)
            transform = etree.XSLT(xslt_doc)
            
            input_doc = etree.parse(input)
            result = str(transform(input_doc))                   
            postprocessed_result = post_process_result(result, enc, linesep)
            return postprocessed_result
          
        except Exception, e:
            logging.getLogger('cone.gcfml').error('Failed to do XSLT transformation: %s' % e)
            raise exceptions.ConeException('Failed to do XSLT transformation: %s' % (e))


def post_process_result(string, enc, linesep):
    """
    Does post process for result from XSLT transform
        - encoding
        - removes extra line separators
        - changes line separators
    """
    output_string = None
    
    try:
        output_string = string.decode(enc)
        if not output_string.startswith('<'):
            output_string = '\n' + output_string
        output_string = output_string.replace('<?xml version="1.0" encoding="UTF-16"?>', '<?xml version="1.0" encoding="UTF-16"?>\n\n')
        output_string = output_string.replace('<?xml version="1.0" encoding="UTF-8"?>', '<?xml version="1.0" encoding="UTF-8"?>\n\n')
        output_string = output_string.replace('\n\n','\n')
        output_string = output_string.replace('\n', linesep)
        output_string+= linesep
    except Exception, e:
        logging.getLogger('cone.gcfml').error('Cannot post process result: %s \nException: %s' % (string, e))
        raise exceptions.ConeException('Cannot post process result: %s \nException: %s' % (string, e))
    
    return output_string



