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

from xml.parsers import expat

# Import ElementTree (should always be available)
try:
    from elementtree import ElementTree
except ImportError:
    from xml.etree import ElementTree

import exceptions


class ElementTreeBackendWrapperBase(object):
    def get_module(self):
        raise NotImplementedError()
    
    def get_lineno(self, element):
        raise NotImplementedError()

    def get_elem_from_lineno(self, root, lineno):
        raise NotImplementedError()

class ElementTreeBackendWrapper(ElementTreeBackendWrapperBase):

    class CustomTreeBuilder(ElementTree.TreeBuilder):
        """
        Custom TreeBuilder for ElementTree that records line numbers
        of the elements.
        """
        def start(self, tag, attrs):
            elem = ElementTree.TreeBuilder.start(self, tag, attrs)
            lineno = self._xmltreebuilder._parser.CurrentLineNumber
            # print "Tag: %s, line: %r" % (tag, lineno)
            elem.sourceline = lineno
            return elem
    
    def get_module(self):
        return ElementTree
    
    def fromstring(self, text):
        try:
            treebuilder = self.CustomTreeBuilder()
            parser = ElementTree.XMLTreeBuilder(target=treebuilder)
            treebuilder._xmltreebuilder = parser
            parser.feed(text)
            self.root = parser.close()
            return self.root
        except expat.ExpatError, e:
            raise exceptions.XmlParseError(
                "XML parse error on line %d: %s" % (e.lineno, e),
                e.lineno, str(e))
    
    def tostring(self, etree, encoding=None):
        return ElementTree.tostring(etree, encoding)
    
    def get_lineno(self, element):
        try:
            return element.sourceline
        except AttributeError:
            return None

    def get_elem_from_lineno(self, root, lineno):
        for elem in root.getiterator():
            if elem.sourceline == lineno:
                return elem
        return None

class CElementTreeBackendWrapper(ElementTreeBackendWrapperBase):
    def __init__(self):
        try:
            from cElementTree import cElementTree
        except ImportError:
            from xml.etree import cElementTree
        
        self.cElementTree = cElementTree
    
    def get_module(self):
        return self.cElementTree
    
    def fromstring(self, text):
        try:
            self.root = self.cElementTree.fromstring(text)
            return self.root
        except SyntaxError, e:
            # cElementTree raises a SyntaxError, but does not set
            # its lineno attribute, so look for the line number
            # in the exception text
            import re
            match = re.search(r'line (\d+)\, column \d+$', str(e))
            if match:   lineno = int(match.group(1))
            else:       lineno = None
            
            raise exceptions.XmlParseError(
                "XML parse error on line %s: %s" % (lineno, e),
                lineno, str(e))
    
    def tostring(self, etree, encoding=None):
        return self.cElementTree.tostring(etree, encoding)
    
    def get_lineno(self, element):
        # cElementTree does not support line numbers
        return None

    def get_elem_from_lineno(self, root, lineno):
        # cElementTree does not support line numbers
        return None

class LxmlBackendWrapper(ElementTreeBackendWrapperBase):
    
    def __init__(self):
        import lxml.etree
        self.lxml = lxml
    
    def get_module(self):
        return self.lxml.etree
    
    def fromstring(self, text):
        try:
            self.root = self.lxml.etree.fromstring(text)
            self.remove_comments(self.root)
            return self.root
        except self.lxml.etree.XMLSyntaxError, e:
            raise exceptions.XmlParseError(
                "XML parse error on line %d: %s" % (e.position[0], e),
                e.position[0], str(e))
    
    def remove_comments(self, elem):
        """
        lxml parses also comments, but ConE does not expect those,
        so remove them to prevent any errors on that account
        """
        # Find the comments under this element
        comments = []
        for x in elem:
            if isinstance(x, self.lxml.etree._Comment):
                comments.append(x)
        
        # Remove them
        for c in comments:
            elem.remove(c)
        
        # Recurse to sub-elements
        for subelem in elem:
            self.remove_comments(subelem)
            
    def tostring(self, etree, encoding=None):
        return self.lxml.etree.tostring(etree, encoding=encoding)
    
    def get_lineno(self, element):
        try:
            return element.sourceline
        except AttributeError:
            return None

    def get_elem_from_lineno(self, root, lineno):
        for elem in root.getiterator():
            if elem.sourceline == lineno:
                return elem
        return None
    
# ============================================================================
#
# ============================================================================

class ElementTreeWrapper(object):
    """
    ElementTree wrapper class for providing a unified interface to different
    ElementTree implementations.
    
    Currently supported are the pure Python ElementTree implementation,
    cElementTree and lxml.etree
    """
    BACKEND_ELEMENT_TREE     = 'ElementTree'
    BACKEND_C_ELEMENT_TREE   = 'cElementTree'
    BACKEND_LXML             = 'lxml'
    
    # Import order for the default back-end. The list is traversed
    # top-down and the first back-end whose importing is successful is
    # used as the default back-end
    DEFAULT_BACKEND_IMPORT_ORDER = [BACKEND_LXML,
                                    BACKEND_C_ELEMENT_TREE,
                                    BACKEND_ELEMENT_TREE]
    
    _backend_mapping = {BACKEND_ELEMENT_TREE:     ElementTreeBackendWrapper,
                        BACKEND_C_ELEMENT_TREE:   CElementTreeBackendWrapper,
                        BACKEND_LXML:             LxmlBackendWrapper}
    
    _backend_id = None
    _backend_wrapper = None

    def get_backend_id(self):
        """
        Return the ID of the currently used ElementTree back-end.
        """
        # Make sure that the default back-end is set, so _backend_id
        # will not be None
        self._get_backend()
        assert self._backend_id is not None
        return self._backend_id
    
    def set_backend_id(self, backend_id):
        """
        Set the used ElementTree back-end by back-end ID.
        """
        if backend_id not in self._backend_mapping:
            raise ValueError("Invalid ElementTree back-end ID: %r" % backend_id)
        
        if backend_id == self._backend_id:
            return
        
        backend_wrapper_class = self._backend_mapping[backend_id]
        self._backend_wrapper = backend_wrapper_class()
        self._backend_id = backend_id
    
    def _get_backend(self):
        """
        Return the currently set ElementTree back-end wrapper object.
        """
        if self._backend_wrapper is None:
            # Back-end not set, so set the default back-end.
            # The default is the C version of ElementTree, but if that
            # is not available, the pure Python version is used
            for backend_id in self.DEFAULT_BACKEND_IMPORT_ORDER:
                try:
                    self.set_backend_id(backend_id)
                    #break
                except ImportError:
                    pass
            
            if self._backend_wrapper is None:
                raise RuntimeError("Failed to set any ElementTree backend! Tried these: %r" % self.DEFAULT_BACKEND_IMPORT_ORDER)
        
        return self._backend_wrapper
    
    def get_lineno(self, element):
        """
        Return the source line number of the given XML element.
        
        Note that for the cElementTree parser this will always return
        None, since that parser does not support line numbers.
        """
        return self._get_backend().get_lineno(element)
    
    def get_elem_from_lineno(self, root, lineno):
        """
        Return the element from the given line number of the given XML element.
        
        @param root: the root element to search from
        @param lineno: the line number to search for  
        
        Note that for the cElementTree parser this will always return
        None, since that parser does not support line numbers.
        """
        return self._get_backend().get_elem_from_lineno(root, lineno)

    def __getattribute__(self, attrname):
        try:
            # Try to get the attribute from this object (the top-level wrapper)
            return object.__getattribute__(self, attrname)
        except AttributeError:
            # If not overridden here, try to get it from the back-end wrapper
            backend = self._get_backend()
            try:
                return getattr(backend, attrname)
            except AttributeError:
                # Last resort: try to get it from the module
                # the back-end wrapper wraps
                backend_module = backend.get_module()
                return getattr(backend_module, attrname)
