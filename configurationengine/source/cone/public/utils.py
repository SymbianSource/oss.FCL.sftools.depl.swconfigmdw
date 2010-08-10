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
import re
import posixpath
import StringIO
import tokenize
import inspect
import traceback
import logging
import shlex
from xml.parsers import expat
import imghdr
from token import ENDMARKER, NAME, NUMBER, STRING
from cone.public import exceptions

import _etree_wrapper
etree = _etree_wrapper.ElementTreeWrapper()

class resourceref(object):
    """
    Class container for set of resource reference related functions
    """
    @classmethod
    def filter_resources(cls, resources, regexp):
        """
        Filter out all resources that do not match the given regexp
        @return a array of resources that match the given resource
        """
        test = re.compile(regexp, re.IGNORECASE)
        return [r for r in resources if test.search(r)]
    
    @classmethod
    def neg_filter_resources(cls, resources, regexp):
        """
        Filter out all resources that do match the given regexp
        @return a array of resources that dont match the given resource
        """
        test = re.compile(regexp, re.IGNORECASE)
        return [r for r in resources if not test.search(r)]

    @classmethod
    def insert_begin_slash(cls, ref):
        if not ref.startswith('/'): 
            return '/' + ref
        return ref
    
    @classmethod
    def remove_begin_slash(cls, ref):
        while ref.startswith('/'): 
            ref = ref.replace('/', '', 1)
        return ref
    
    @classmethod
    def remove_end(self, path, str):
        try:
            (ret, sep, rest) = path.partition(str)
            return ret
        except ValueError:
            return path

    @classmethod
    def add_end_slash(cls, ref):
        if not ref.endswith('/'): 
            return ref+'/'
        return ref
    
    @classmethod
    def remove_end_slash(cls, ref):
        if ref.endswith('/'): 
            return ref[:-1]
        return ref
    
    @classmethod
    def norm(cls, ref):
        """
        Normalize the reference to common cone form. 
        1. Always with forward slashes 
        2. no beginning slash
        3. no end slash
        @return: A normalized reference string
        """
        
        # Do not modify emtpy string at all
        if not ref == '':
            normref = os.path.normpath(ref)
            normref = normref.replace('\\','/').replace('"','')
            normref = posixpath.normpath(normref)
            normref = normref.rstrip('\\/')
        else:
            normref = ref
        return normref
    
    @classmethod
    def replace_dir(cls, ref, frompart, topart):
        """
        Replace a part of directory beginning from ref.
        @param ref: the resource reference
        @param frompart: the part of directory name to be replaced
        @param topart: the partial name which replaces the frompart
        @return: a refenence with forward slashes
        """
        # Normalize all paths and replace the name with string replace
        # 
        normref = cls.norm(ref)
        normfrom = cls.norm(frompart)
        normto = cls.norm(topart)
        # Add the end slash to from and to as it should be a dir (if not empty)
        if normto != "": normto = cls.add_end_slash(normto)
        if normfrom != "": normfrom = cls.add_end_slash(normfrom)
        if normref != "": normref = cls.add_end_slash(normref)
        retref = cls.norm(normref.replace(normfrom, normto, 1))
        if retref  != "": retref = cls.remove_end_slash(retref)
        return retref

    @classmethod
    def join_refs(cls, refs):
        """
        join a list of dotted references together with dots
        1. ignore empty refs
        2. no dot include begin dot
        3. no dot include end dot
        @param refs: a list of references
        @return: A normalized dotted reference
        """
        # Create a copy of references without any empty strings
        import posixpath
        paramdict = {}
        retref = posixpath.join(*refs)
        #retref = "/".join([ref for ref in refs if ref != ''])
        #subs = re.sub('/+', '/', retref)
        return retref

    @classmethod
    def split_ref(cls, ref):
        """
        Replace a part of directory beginning from ref.
        @param ref: the resource reference
        @return: a list of path elems
        """
        return [r for r in ref.split('/') if r]
    
    @classmethod
    def psplit_ref(cls, ref):
        """
        pop split that splits the last element of the array 
        1. empty ref returns an empty list
        @param ref: a resource references string (e.g. aaa/bbb/ccc.txt)
        @return: A tuple of references (with given param ('aaa/bbb','ccc.txt')
        """
        refs = ref.rsplit('/', 1)
        return ("".join(refs[0:-1]), refs[-1])

    @classmethod
    def remove_ext(cls, ref):
        """
        Remove file extension from ref 
        1. remove file extension
        @return: a reference. E.g. (foo/test.confml) => foo/test
        """
        filenameparts = cls.get_filename(ref).rsplit('.', 1)
        path = cls.get_path(ref)
        if len(filenameparts)==2 and filenameparts[0] != "":
            return cls.join_refs([path, filenameparts[0]])
        else:
            return ref

    @classmethod
    def get_ext(cls, ref):
        """
        get file extension from ref 
        1. get file extension
        @return: a reference. E.g. (foo/test.confml) => confml
        """
        if len(ref.rsplit('.', 1)) == 2: 
            return ref.rsplit('.', 1)[1]
        else:
            return ""

    @classmethod
    def get_filename(cls, ref):
        """
        get file name part from ref 
        1. get file name
        @return: a reference. E.g. (foo/test.confml) => test.confml
        """
        return ref.rsplit('/', 1)[-1]

    @classmethod
    def get_path(cls, ref):
        """
        get path part from ref 
        1. get path from ref
        @return: a reference. E.g. (foo/test.confml) => foo
        """
        if len(ref.rsplit('/', 1)) == 2: 
            return ref.rsplit('/', 1)[0]
        else:
            return ""

    @classmethod
    def to_dottedref(cls, ref):
        """
        Convert a resource ref to dotted ref 
        1. remove file extension
        2. convert path delims to dots
        @return: a dotted reference. E.g. (foo/test.confml) => foo_test
        """
        newref = cls.remove_ext(ref).replace('/', '_').replace(' ', '_')
        return dottedref.remove_begin_dot(newref)


    @classmethod
    def to_objref(cls, ref):
        """
        Convert a resource ref to dotted ref 
        1. remove file extension
        2. convert path delims to dots
        3. using double underscores for directory separation
        @return: a dotted reference. E.g. (foo/test.confml) => foo_test
        """
        ref = ref.replace('/', '__')
        # Change the python comment character also as underscore so that the tokenizer 
        # does not leave anything out
        ref = ref.replace('#', '_')
        newref = ''
        first_token = True
        try:
            for toknum, tokval, spos, epos, _ in tokenize.generate_tokens(StringIO.StringIO(unicode(ref)).readline):
                if toknum == ENDMARKER:
                    break
                elif toknum == NAME:
                    newref += str(tokval)
                elif toknum == NUMBER:
                    # Add a character before the number token if the first token is a number
                    if first_token:
                        newref += '_'
                    # replace a possible dot in number .123
                    newref += str(tokval.replace('.','_'))
                elif toknum == STRING:
                    newref += str(tokval.replace('"', ''))
                else:
                    newref += '_'
                # After first round set the first token to false
                first_token = False
        except tokenize.TokenError:
            pass
        return newref
        
    @classmethod
    def to_dref(cls, ref):
        """
        Convert a resource ref to dotted ref 
        1. remove file extension
        2. convert path delims to dots
        @return: a dotted reference. E.g. (foo/test.confml) => foo.test
        """
        return dottedref.remove_begin_dot(cls.remove_ext(ref).replace('/','.'))

    @classmethod
    def to_hash(cls, ref):
        """
        Convert a resource ref to to hash 32 bit integer
        @return: 
        """
        return "%s" % hex(hash(ref))

    @classmethod
    def is_path(cls, ref):
        """
        returns true if the ref seems like a path
        @return: Boolean value [True|False]
        """
        if cls.get_ext(ref) or cls.get_path(ref):
            return True
        return False

class dottedref(object):
    """
    Class container for set of dotted reference related functions
    """
    @classmethod
    def join_refs(cls, refs):
        """
        join a list of dotted references together with dots
        1. ignore empty refs
        2. no dot include begin dot
        3. no dot include end dot
        @param refs: a list of references
        @return: A normalized dotted reference
        """
        # Create a dotted reference without any empty strings
        return '.'.join([ref for ref in refs if ref.strip()])
    
    @classmethod
    def split_ref(cls, ref):
        """
        split a dotted references string to a list of ref elements
        1. empty ref returns an empty list
        @param ref: a dotted references string (e.g. aaa.bbb.ccc)
        @return: A list of references (with given param ['aaa','bbb','ccc']
        """
        # list of reference parts without any empty strings
        return [r for r in ref.split('.') if r]
    
    @classmethod
    def psplit_ref(cls, ref):
        """
        pop split that splits the last element of the array 
        1. empty ref returns an empty list
        @param ref: a dotted references string (e.g. aaa.bbb.ccc)
        @return: A tuple of references (with given param ('aaa.bbb','ccc')
        """
        refs = ref.rsplit('.', 1)
        return ("".join(refs[0:-1]), refs[-1])
    
    @classmethod
    def remove_last(cls, ref):
        """
        removes the last element of the ref 
        1. empty ref returns an empty list
        @param ref: a dotted references string (e.g. aaa.bbb.ccc)
        @return: A reference (with given param ('aaa.bbb')
        """
        return ref.rsplit('.', 1)[0]

    @classmethod
    def get_last(cls, ref):
        """
        returns the last element of the ref 
        1. empty ref returns an empty string
        @param ref: a dotted references string (e.g. aaa.bbb.ccc)
        @return: A reference (with given param ('ccc')
        """
        return ref.rsplit('.', 1)[-1]

    @classmethod
    def get_name(cls, ref):
        """
        returns the last element of the ref 
        1. empty ref returns an empty string
        @param ref: a dotted references string (e.g. aaa.bbb.ccc)
        @return: A reference (with given param ('ccc')
        """
        if re.match('^(.*)\[.*\]$', ref):
            return re.match('^(.*)\[.*\]$', ref).group(1)
        else:
            return ref

    @classmethod
    def get_index(cls, ref):
        """
        returns the last element of the ref 
        1. empty ref returns an empty string
        @param ref: a dotted references string (e.g. aaa.bbb.ccc)
        @return: A reference (with given param ('ccc')
        """
        if re.match('^.*\[(\d+)\]$', ref):
            return int( re.match('^.*\[(\d+)\]$', ref).group(1) )
        else:
            return None

    @classmethod
    def remove_begin_dot(cls, ref):
        """
        removes all the dots from the begin of the ref 
        @param ref: a dotted references string (e.g. .aaa.bbb.ccc)
        @return: A reference (with given param ('aaa.bbb.ccc')
        """
        return ref.lstrip('.')

    @classmethod
    def ref2filter(cls, ref):
        elems = []
        for refelem in dottedref.split_ref(ref):
            if refelem == "**":
                elems.append(".*")
            else:
                elems.append(refelem.replace("*","[^\.]*"))
        return "\\.".join(elems)+"$"
    
    @classmethod
    def has_wildcard(cls, ref):
        """
        Tests if the ref has any wildcards '*' in it.
        @return: Boolean value. True when wildcards are found.
        """
        return ref.find('*') != -1

    @classmethod
    def get_static_ref(cls, ref):
        """
        Checks if the ref has any wildcards and return the non wildcard part of ref.
        @return: string.
        """
        retparts = []
        for part in cls.split_ref(ref):
            if cls.has_wildcard(part):
                break
            else:
                retparts.append(part)
        return ".".join(retparts)

def extract_delimited_tokens(string, delimiters=('${', '}')):
    """
    Return a list of all tokens delimited by the given strings in the given string.
    This function returns basically the first row of the result of
    extract_delimited_token_tuples(), with duplicates removed.
    
    >>> dottedref.extract_refs("test1 ${my.ref1} test2 ${ my.ref1 } ${my.ref2}")
    ['my.ref1', 'my.ref2']
    """
    ref_tuples = extract_delimited_token_tuples(string, delimiters)
    return distinct_array([u'%s' % ref for ref, raw_ref in ref_tuples])

def extract_delimited_token_tuples(string, delimiters=('${', '}')):
    """
    Extract a list of (token, raw_token) tuples from the given string.
    'token' is the the token extracted from the string and trimmed (surrounding
    whitespace removed), and raw_token is the unmodified match from the
    string, which can be used for replacing.
    
    >>> dottedref.extract_ref_tuples("test1 ${my.ref1} test2 ${ my.ref1 } ${my.ref2}")
    [('my.ref1', '${my.ref1}'), ('my.ref1', '${ my.ref1 }'), ('my.ref2', '${my.ref2}')]
    """
    pattern = '%s.*?%s' % (re.escape(delimiters[0]), re.escape(delimiters[1]))
    matches = distinct_array(re.findall(pattern, string, re.DOTALL))
    
    result = []
    for match in matches:
        ref = match[len(delimiters[0]):-len(delimiters[1])].strip()
        result.append((ref, match))
    return result

def expand_delimited_tokens(string, expander_func, delimiters=('${', '}')):
    """
    Expand all tokens in the given string using the given expander function.
    
    @param string: The string to expand.
    @param expander_func: The function used for expanding. Should take two parameters:
        1 - The token to expand.
        2 - The index of the token in the string.
    @param delimiters: Tuple specifying the delimiters for tokens.
    @return: The expanded string.
    """
    # Collect a dictionary of token-entry pairs
    class Entry(object):
        pass
    tokens = {}
    for index, (token, raw_token) in enumerate(extract_delimited_token_tuples(string, delimiters)):
        if token not in tokens:
            entry = Entry()
            entry.index = index
            entry.raw_tokens = []
            entry.value = unicode(expander_func(token, index))
            tokens[token] = entry
        else:
            entry = tokens[token]
        
        entry.raw_tokens.append(raw_token)
    
    # Replace all tokens with the expanded values
    result = string
    for entry in tokens.itervalues():
        for raw_token in entry.raw_tokens:
            result = result.replace(raw_token, entry.value)
    return result

def expand_refs_by_default_view(string, default_view, delimiters=('${', '}'), default_value_for_missing='',
                                catch_not_found=True):
    """
    Convenience function for expanding the refs in a string using setting values.
    @param default_value_for_missing: The default value used if a setting for
        a reference cannot be found. Has no effect if catch_not_found is False.
    @param catch_not_found: If True, the NotFound exception raised when a setting
        is not found is caught and the value of default_value_for_missing is inserted
        in its place.
    @return: The expanded string.
    """
    def expand(ref, index):
        if catch_not_found:
            try:
                return default_view.get_feature(ref).get_original_value()
            except exceptions.NotFound:
                logging.getLogger('cone').error("Feature '%s' not found" % ref)
                return default_value_for_missing
        else:
            return default_view.get_feature(ref).get_original_value()
    return expand_delimited_tokens(string, expand, delimiters)

def distinct_array(arr):
    newarray = []
    for val in arr:
        try:
            # test to see whether the value already is in thearray
            newarray.index(val)
        except ValueError:
            newarray.append(val)
    return newarray


def list_files(path):    
    """
    Get an array of files in a folder
    """
    retarray = []
    # Walk through all files in the layer
    path = os.path.abspath(path)
    for root, dirs, files in os.walk(path):
        for name in files:
            entry = os.path.join(root, name)
            entry = os.path.normpath(os.path.abspath(entry))
            if os.path.isfile(entry):
                retarray.append(entry)
    return retarray

def all_subclasses(classname):
    """
    @return: A list of all subclasses of classname
    """
    subclasses = classname.__subclasses__()
    # Create copy of the subclasses list for the iteration, 
    # so that added items are not recursed again
    for subclass in classname.__subclasses__():
        subclasses += all_subclasses(subclass)
    return subclasses

def pathmatch(pattern, refpath):
    """
    Check for matching pattern for a ref path
    """
    filter = dottedref.ref2filter(pattern)
    return re.match(filter, refpath) != None

def filter(obj, filters):
    for filter in filters:
        if not filter(obj):
            return False
    return True

def get_list(elem):
    if not isinstance(elem, list):
        return [elem]
    else:
        return elem

def add_list(elem, add):
    retlist = get_list(elem)
    retlist.append(add)
    return retlist

def prepend_list(elem, prepend):
    retlist = get_list(elem)
    retlist.insert(0, prepend)
    return retlist

def is_list(elem):
    return isinstance(elem, list)

def is_float(value):
    """
    Test if the fiven value (which can be a string) is a floating point value. 
    """
    fvalue = float(value)
    ivalue = int(fvalue)
    
    return (fvalue - ivalue) != 0

def get_class(modelinstance, classinstance):
    """
    Get the actual model specific implementation class for a classinstance
    """
    for attr in dir(modelinstance):
        modelclass = getattr(modelinstance, attr)
        if inspect.isclass(modelclass): 
            if issubclass(modelclass, classinstance):
                return modelclass
    return classinstance

class OProperty(object):
    """Based on the emulation of PyProperty_Type() in Objects/descrobject.c
    from http://infinitesque.net/articles/2005/enhancing%20Python%27s%20property.xhtml"""
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = doc
 
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError, "unreadable attribute"
        if self.fget.__name__ == '<lambda>' or not self.fget.__name__:
            return self.fget(obj)
        else:
            return getattr(obj, self.fget.__name__)()
 
    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError, "can't set attribute"
        if self.fset.__name__ == '<lambda>' or not self.fset.__name__:
            self.fset(obj, value)
        else:
            getattr(obj, self.fset.__name__)(value)
 
    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError, "can't delete attribute"
        if self.fdel.__name__ == '<lambda>' or not self.fdel.__name__:
            self.fdel(obj)
        else:
            getattr(obj, self.fdel.__name__)()

class xml(object):
    """
    Class container for set of XML-related helper functions.
    """
    
    @classmethod
    def split_tag_namespace(cls, xml_tag):
        """
        Split the given XML tag into a (namespace, tag) tuple.
        
        >>> ReaderBase._split_tag_namespace("test")
        (None, 'test')
        >>> ReaderBase._split_tag_namespace("{http://www.test.com/xml/1}test")
        ('http://www.test.com/xml/1', 'test')
        """
        if xml_tag.startswith('{'):
            parts = xml_tag[1:].split('}')
            return (parts[0], parts[1])
        else:
            return (None, xml_tag)

    @classmethod
    def get_xml_root(cls, resource):
        """
        Get a (namespace, tag) tuple of the root element in the XML data
        read from the given resource.
        
        @param resource:  The resource from which to read data. Should be a
            file-like object (i.e. should have a read() method).
        @return: A (namespace, tag) tuple. Note that the namespace may
            be None.
        
        @raise exceptions.XmlParseError: The resource contains invalid XML data.
        """
        class RootElementFound(RuntimeError):
            def __init__(self, root_name):
                self.root_name = root_name
        
        def handle_start(name, attrs):
            raise RootElementFound(name)
        
        p = expat.ParserCreate(namespace_separator=':')
        p.StartElementHandler = handle_start
        
        BUFSIZE = 128
        while True:
            data = resource.read(BUFSIZE)
            try:
                p.Parse(data, len(data) < BUFSIZE)
            except RootElementFound, e:
                parts = e.root_name.rsplit(':', 1)
                if len(parts) > 1:
                    return parts[0], parts[1]
                else:
                    return None, parts[0]
            except expat.ExpatError, e:
                raise exceptions.XmlParseError(
                    "XML parse error on line %d: %s" % (e.lineno, e),
                    e.lineno, str(e))

def update_dict(todict, fromdict):
    """
    Merges the elements of two dictionaries together.
    @param todict: the target dictionary where data is merged. 
    @param fromdict: the source dict where data is read 
    @return: the modified todict.  
    """
    for key in fromdict:
        todict.setdefault(key, []).extend(fromdict[key])
    return todict

def log_exception(logger, msg, msg_level=logging.ERROR, traceback_level=logging.DEBUG):
    """
    Log an exception so that the given message and the exception's
    traceback are logged separately with the given log levels.
    
    The purpose is to print minimal information to the user when running
    the CLI (default level for STDOUT logging is WARNING), but the traceback
    should still be available in the log file (which uses the level DEBUG
    by default).
    
    Note that this function should be only used in an exception handler.
    """
    logger.log(msg_level, msg)
    logger.log(traceback_level, traceback.format_exc())


def grep(string,list):
    """
    Grep throught the items in the given list to find matching entries. 
    """
    expr = re.compile(string)
    return filter(expr.search,list)

def grep_tuple(string,list):
    """
    Grep throught the items in the given list to find matching entries. 
    @return: a list of tuples (index,text) 
    """
    results = []
    expr = re.compile(string)
    for (index,text) in enumerate(list):
        match = expr.search(text)
        if match != None:
            results.append((index,match.string))
    return results

def grep_dict(string,list):
    """
    Grep throught the items in the given list to find matching entries. 
    @return: a dictionary with list index as key and matching text as value.
    """
    results = {}
    expr = re.compile(string)
    for (index,text) in enumerate(list):
        match = expr.search(text)
        if match != None:
            results[index]  = match.string
    return results

def cmdsplit(s, comments=False, os_name='nt'):
    """
    Copy of shlex split method to allow parsing of command line parameters in operating system specific mode.
    
    """
    posix = True
    lex = shlex.shlex(s, posix=posix)
    lex.whitespace_split = True
    if not comments:
        lex.commenters = ''
    if os_name == 'nt':
        lex.escape = '^'
    return list(lex)


import sys
sys_version = "%d.%d" % (sys.version_info[0],sys.version_info[1])
if sys_version >= "2.6":
    def relpath(path, start=os.curdir):
        return os.path.relpath(path, start)
else:
    def relpath(path, start=os.curdir):
        """Return a relative version of a path"""
    
        if not path:
            raise ValueError("no path specified")
        start_list = os.path.abspath(start).split(os.sep)
        path_list = os.path.abspath(path).split(os.sep)
        if start_list[0].lower() != path_list[0].lower():
            unc_path, rest = os.path.splitunc(path)
            unc_start, rest = os.path.splitunc(start)
            if bool(unc_path) ^ bool(unc_start):
                raise ValueError("Cannot mix UNC and non-UNC paths (%s and %s)"
                                                                    % (path, start))
            else:
                raise ValueError("path is on drive %s, start on drive %s"
                                                    % (path_list[0], start_list[0]))
        # Work out how much of the filepath is shared by start and path.
        for i in range(min(len(start_list), len(path_list))):
            if start_list[i].lower() != path_list[i].lower():
                break
        else:
            i += 1
    
        rel_list = [os.pardir] * (len(start_list)-i) + path_list[i:]
        if not rel_list:
            return os.curdir
        return os.path.join(*rel_list) 