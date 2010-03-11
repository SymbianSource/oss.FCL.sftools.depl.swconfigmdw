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
import xml.etree.ElementTree as ElementTree
import unittest
import traceback

def compare_xml_documents(data1, data2, **kwargs):
    """
    Compare two XML documents for equality.
    @param data1: The raw byte data of the first XML document as a string.
    @param data2: The raw byte data of the second XML document as a string.
    
    Keyword arguments:
    @param check_encoding: If True, the encoding of the documents is checked to be the same.
    @param ignore_namespace: If True, XML namespaces are ignored in the comparison.
    @param ignored_empty_tags: List of tags that will be ignored in the comparison if empty,
        i.e. if the tags is empty on one side and does not exist on the other.
    @param debug_stream: If not None, the stream where debug messages are printed.
    
    @return: True if the documents are equal, False if not.
    """
    
    check_encoding = kwargs.get('check_encoding', False)
    ignore_namespaces = kwargs.get('ignore_namespaces', False)
    debug_stream = kwargs.get('debug_stream', None)
    ignored_empty_tags = kwargs.get('ignored_empty_tags', [])
    
    if data1 == data2:
        if debug_stream: print >>debug_stream, "Raw byte data equal"
        return True
    
    if check_encoding:
        enc1 = _get_xml_encoding(data1)
        enc2 = _get_xml_encoding(data2)
        if enc1.lower() != enc2.lower():
            if debug_stream: print >>debug_stream, "XML encoding is not the same (%s vs. %s)" % (repr(enc1), repr(enc2))
            return False
    
    try:
        et1 = ElementTree.fromstring(data1)
    except Exception:
        if debug_stream: print >>debug_stream, "Failure when parsing data1: %s" % traceback.format_exc()
        return False
    
    try:
        et2 = ElementTree.fromstring(data2)
    except Exception:
        if debug_stream: print >>debug_stream, "Failure when parsing data2: %s" % traceback.format_exc()
        return False
    
    return _xml_elements_equal(et1, et2, ignore_namespaces, debug_stream, '', ignored_empty_tags)

def _xml_elements_equal(elem1, elem2, ignore_namespaces, debug_stream, parent_path, ignored_empty_tags):
    ds = debug_stream
    
    elem1_tag = _get_tag(elem1, ignore_namespaces)
    elem2_tag = _get_tag(elem2, ignore_namespaces)
    
    full_path1 = parent_path + '/' + elem1_tag
    full_path2 = parent_path + '/' + elem2_tag
    if ds and parent_path == '':
        print >>ds, "Comparing '%s' vs. '%s'" % (full_path1, full_path2)
    
    if elem1_tag != elem2_tag:
        if ds and parent_path == '':
            print >>ds, "Tags don't match"
        return False
    
    def strip_string(data):
        if data == None:    return data
        else:               return data.strip(' \n\r\t')
    text1 = strip_string(elem1.text)
    text2 = strip_string(elem2.text)
    if text1 != text2:
        if ds and parent_path == '':
            print >>ds, "Element text %s does not match %s" % (repr(text1), repr(text2))
        return False
    
    def strip_namespace_attrs(attrib):
        if not ignore_namespaces:
            return attrib
        else:
            # Strip all attributes with a namespace if namespace are ignored
            result = {}
            for key, value in attrib.iteritems():
                if '{' not in key:
                    result[key] = value
            return result
    attrs1 = strip_namespace_attrs(elem1.attrib)
    attrs2 = strip_namespace_attrs(elem2.attrib)
    if attrs1 != attrs2:
        if ds and parent_path == '':
            print >>ds, "Element attributes don't match (%s vs. %s)" % (repr(attrs1), repr(attrs2))
        return False
    
    # Remove ignored empty sub-elements before comparing the sub-elems
    subelems1 = elem1.getchildren()
    subelems2 = elem2.getchildren()
    _remove_ignored_empty_subelems(subelems1, elem2.getchildren(), full_path1, ignore_namespaces, ignored_empty_tags, ds)
    _remove_ignored_empty_subelems(subelems2, elem1.getchildren(), full_path1, ignore_namespaces, ignored_empty_tags, ds)
    
    # Compare sub-elements without caring about their document order
    # NOTE: This approach will not scale well for very large documents
    len1 = len(elem1.getchildren())
    len2 = len(elem2.getchildren())
    if len1 != len2:    return False
    if len1 == 0:       return True
    matched_subelems2 = []
    for subelem1 in subelems1:
        matched = False
        for subelem2 in subelems2:
            # Try to match the sub-element in elem2 only if it
            # has not been matched yet
            if id(subelem2) not in matched_subelems2:
                if _xml_elements_equal(subelem1, subelem2, ignore_namespaces, ds, full_path1, ignored_empty_tags):
                    matched = True
                    matched_subelems2.append(id(subelem2))
                    break
        if not matched:
            if ds:
                print >>ds, "No match found for element '%s' under '%s'." % (subelem1.tag, full_path1)
                print >>ds, "Element data:"
                print >>ds, ElementTree.tostring(subelem1)
            return False
    
    # Everything matched
    return True

def _remove_ignored_empty_subelems(subelems1, subelems2, parent_path, ignore_namespaces, ignored_empty_tags, debug_stream):
    """Remove ignored empty sub-elements from list subelems1."""
    ds = debug_stream
    if ds: print >>ds, "parent_path: %s" % parent_path
    removed = []
    for i, subelem1 in enumerate(subelems1):
        if len(subelem1.getchildren()) > 0:
            continue
        
        # See if the tag should be ignored if it doesn't exist on
        # the other side
        is_ignored = False
        for ignored_tag in ignored_empty_tags:
            if ds: print >>ds, "ignored_tag = %s, tag = %s" % (ignored_tag, parent_path + "/" + _get_tag(subelem1, ignore_namespaces))
            if ignored_tag == parent_path + "/" + _get_tag(subelem1, ignore_namespaces):
                is_ignored = True
                break
        if not is_ignored:
            continue
        
        # See if the tag exists on the other side
        found = False
        for subelem2 in subelems2:
            if _get_tag(subelem1, ignore_namespaces) == _get_tag(subelem2, ignore_namespaces):
                found = True
                break
        if not found:
            removed.append(i)
    
    # Sort and reverse the removed list so that deleting starts from the
    # end and the indices are correct throughout the operation
    removed.sort()
    removed = removed[::-1]
    if len(removed) >= 2:
        if removed[0] < removed[-1]:
            raise RuntimeError("Internal error: list in wrong order: %s" % removed)
    
    for i in removed:
        del subelems1[i]
        
def _get_tag(elem, ignore_namespaces):
    tag = elem.tag
    if ignore_namespaces:
        pos = tag.find('}')
        if pos >= 0:
            tag = tag[pos + 1:]
    return tag

def _get_xml_encoding(xml_data):
    encoding = 'UTF-8'
    if xml_data.startswith('\xFE\xFF') or xml_data.startswith('\xFF\xFE'):
        encoding = 'UTF-16'
    
    # Decode only up to the first 200 bytes (should be enough for the header)
    decoded_data = xml_data[:200].decode(encoding, 'ignore')
    if decoded_data.startswith('<?xml'):
        header = decoded_data[:decoded_data.find('?>') + 2]
        # E.g header = '<?xml version="1.0" encoding = 'UTF-8'?>'
        
        def get_substr(string, sought_data):
            pos = string.find(sought_data)
            if pos >= 0:    return string[pos + len(sought_data):]
            else:           return None
        
        x = get_substr(header, "encoding")
        if not x: return ''
        # E.g x = ' = 'UTF-8'?>'
        x = x.replace(' ', '').replace('\t', '')
        # E.g x = '='UTF-8'?>'
        sgl_quoted = get_substr(x, "='")
        dbl_quoted = get_substr(x, '="')
        # E.g sgl_quoted = 'UTF-8'?>'
        if sgl_quoted:      return sgl_quoted[:sgl_quoted.find("'")]
        elif dbl_quoted:    return dbl_quoted[:dbl_quoted.find('"')]
        
    return ''
