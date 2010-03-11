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


import re
import os
import sys
import codecs
import logging
import xml.parsers.expat
import unittest, os, sys, pkg_resources

pkg_resources.require('lxml')

try:
    from cElementTree import ElementTree
except ImportError:
    try:    
        from elementtree import ElementTree
    except ImportError:
        try:
            from xml.etree import cElementTree as ElementTree
        except ImportError:
            from xml.etree import ElementTree

import __init__

from cone.public import exceptions,plugin,utils,api

class XsltTransformer():
    """
    XSLT Transformer
    """
    
    def _init(self,ref,configuration):
        self.logger = logging.getLogger('cone.gcfml(%s)' % self.ref)


    def transform_lxml(self, input, xslt, output, enc, linesep=os.linesep):
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
          
          if not filter_file_writing(postprocessed_result):
              write_string_to_file(postprocessed_result, output, enc)
        
      except Exception, e:
          logging.getLogger('cone.gcfml').error('Failed to do XSLT transformation: %s' % e)
          raise exceptions.ConeException('Failed to do XSLT transformation: %s' % (e))


    def transform_4s(self, input, xslt, output, enc, linesep=os.linesep):
      """
      XSLT transform with 4Suite
      """
      from Ft.Xml.Xslt import Transform
      from Ft.Xml.Xslt import Processor
      from Ft.Xml import InputSource
      from Ft.Lib.Uri import OsPathToUri  

      
      if not enc:
          enc = sys.getdefaultencoding()
      
      try:
          processor = Processor.Processor()
          
          srcAsUri = OsPathToUri(input)
          source = InputSource.DefaultFactory.fromUri(srcAsUri)

          ssAsUri = OsPathToUri(xslt)
          transform = InputSource.DefaultFactory.fromUri(ssAsUri)

          processor.appendStylesheet(transform)
          result = processor.run(source)
          
          postprocessed_result = post_process_result(result, enc, linesep)
          
          if not filter_file_writing(postprocessed_result):
              write_string_to_file(postprocessed_result, output, enc)
        
      except Exception, e:
          logging.getLogger('cone.gcfml').error('Failed to do XSLT transformation: %s' % e)
          raise exceptions.ConeException('Failed to do XSLT transformation: %s' % (e))

def filter_file_writing(string):
    """
    Returns True if writing result file should be ignored.
    """
    string = string.rstrip('\n\r')
    if string == '' or string == '<?xml version="1.0" encoding="UTF-16"?>' or \
        string == '<?xml version="1.0" encoding="UTF-8"?>':
        return True
    
    return False


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

def write_string_to_file(string, output, enc):
  """
  Writes string to file
  """
  try:
      outfile = os.path.abspath(output)
      
      if not os.path.exists(os.path.dirname(outfile)):
          os.makedirs(os.path.dirname(outfile))
          
      fl = codecs.open(outfile, 'w', enc)
      fl.write(string)
      fl.close()
      
  except Exception, e:
      logging.getLogger('cone.gcfml').error('Cannot write Element to file (%s). Exception: %s' % (output, e))
      raise exceptions.ConeException('Cannot write Element to file (%s). Exception: %s' % (output, e))



