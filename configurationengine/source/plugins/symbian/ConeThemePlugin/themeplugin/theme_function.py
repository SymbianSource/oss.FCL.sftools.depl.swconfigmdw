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

from shutil import copy
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

import os
import logging

def convert_hexa_to_decimal(hexa_number):
    """
    convert hexa number to decimal number. Hexa number has to have 16 digitals.
    This method split hexa number to two half and convert them to decimal format.
    First decimal format is modified using by binary operations. This is for reasons that
    AknSkinDescCompiler from SDK can't work with big integer numbers
    """
    
    if len(hexa_number) == 16:
       hexa1 = hexa_number[0:8]
       hexa2 = hexa_number[8:16]

       decimal1 = long(hexa1,16)
       decimal2 = long(hexa2,16)
       
       max = 0x7fffffff
       
       if decimal1 >= max:
           pow = 2**31
           num = decimal1 - pow
           result = max ^ num
           decimal1 = 0 - (result + 1);

       decimal = str(decimal1)+" " +str(decimal2)
       return decimal   
   
    
def get_tdf_file(path):
    """
    This method takes the name of the tdf file from the .project file 
    """
    
    path = os.path.join(path,".project")
    etree = ElementTree.parse(path)
    
    el_name =  etree.find("name")
    if el_name != None:
        return el_name.text
    else:
        logging.getLogger('cone.thememl').error("The element name is not in %s" % path)
        


def find_text_in_file(file_path, start_text, end_text):
    """
    This method goes over the file and searches text which is located 
    between start_text and end_text
    """

    pkg_file=file(file_path,'r')  
    for row in pkg_file:  
        pid = find_text_in_string(row, start_text, end_text)
        if pid != None:
            pkg_file.close()
            return pid

    pkg_file.close()  
    return None


def find_text_in_string(string, start_text, end_text):
    """
    This method return text which is located between start_text and end_text
    """
    index_start = string.rfind(start_text)
    if not index_start==-1:
        index_end = string.rfind(end_text)
        str = string[index_start+len(start_text):index_end]
        return str




    


    
    
