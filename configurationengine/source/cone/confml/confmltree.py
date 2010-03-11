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

try:
    from elementtree.ElementTree import *
except ImportError:
    from xml.etree.ElementTree import *


class ElementTreeNs(ElementTree):
    """ 
    A class inherited from elementtree.ElementTree that can write
    xml elements with qualified names. The xml namespaces that are defined 
    to the self.namespases are written out to the root element of the given
    root element.
    
    Example:
    
    elem = ElementTreeNs.Element('{http://www.test.com}test') 
    etreens = ElementTreeNs(elem, None, {'foo' : 'http://www.test.com'})
    outf = open('test.xml','w')
    ElementTreeNs.write(outf)
    
    content of test.xml would be
    <foo:test xmlns:foo="http://www.test.com"/>
    """
    def __init__(self, element=None, file=None, namespaces={}):
        ElementTree.__init__(self, element, file)
        self.namespaces = namespaces

    def write(self, file, encoding="us-ascii"):
        """
        Writes the element tree to a file, as XML with the existing namespaces
        
        @param file A file name, or a file object opened for writing.
        @param encoding Optional output encoding (default is US-ASCII).
        """
        assert self._root is not None
        if not hasattr(file, "write"):
            file = open(file, "wb")
        if not encoding:
            encoding = "us-ascii"
        elif encoding != "utf-8" and encoding != "us-ascii":
            file.write("<?xml version='1.0' encoding='%s'?>\n" % encoding)
        # set the namespaces for the root element
        for ns in self.namespaces:
            self._root.set('xmlns:%s' % self.namespaces[ns], ns)
        self._write(file, self._root, encoding, self.namespaces)


def tostring(element, namespaces, encoding=None):
    """
    """
    class dummy:
        pass
    data = []
    file = dummy()
    file.write = data.append
    ElementTreeNs(element, None, namespaces).write(file, encoding)
    return "".join(data)

