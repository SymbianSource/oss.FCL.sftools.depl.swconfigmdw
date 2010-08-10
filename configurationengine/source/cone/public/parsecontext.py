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

import threading
import logging

import cone.public.utils

class ParseContext(object):
    """
    Parse context class for handling exceptions and problems encountered
    when parsing a file (ConfML, ImplML or anything included from those).
    
    The context contains the path to the file that is currently being parsed,
    but the file path can also be overridden when calling a handler method
    (e.g. an ImplML file includes some other file, which in contains a problem).
    
    Sub-classes should override _handle_exception() and _handle_problem(),
    NOT handle_exception() and handle_problem().
    """
    def __init__(self):
        #: The file that is currently being parsed.
        self.current_file = None
    
    def handle_exception(self, exception, file_path=None):
        """
        Handle an exception that occurred while parsing a file.
        
        @param exception: The exception that occurred.
        @param file_path: Override for the name of the file that was being parsed.
            If this is None, self.current_file is used.
        """
        if file_path is None:
            file_path = self.current_file
        
        self._handle_exception(exception, file_path)
    
    def handle_problem(self, problem, file_path=None):
        """
        Handle a Problem that occurred while parsing a file.
        
        @param problem: The problem object.
        @param file_path: Override for the name of the file that was being parsed.
            If this is None, self.current_file is used.
        """
        if file_path is None:
            file_path = self.current_file
        
        self._handle_problem(problem, file_path)
    
    def _handle_exception(self, exception, file_path):
        """
        Called to handle an exception that occurred while parsing a file.
        
        Note that this should always be called in an exception handler,
        so you can safely use e.g. traceback.format_exc().
        
        @param exception: The exception that occurred.
        @param file_path: The file that was being parsed.
        """
        cone.public.utils.log_exception(
            logging.getLogger('cone'),
            "Error parsing '%s': %s" % (file_path, str(exception)))
    
    def _handle_problem(self, problem, file_path):
        """
        Called when parsing a file yields a problem.
        @param problem: The problem object.
        @param file_path: Override for the name of the file that was being parsed.
            If this is None, self.current_file is used.
        """
        problem.file = file_path
        problem.log(logging.getLogger('cone'))

# Thread-local storage for the contexts
_contexts = threading.local()

def _init_contexts():
    """
    Initialize thread-local contexts if they are not initialized yet.
    """
    if not hasattr(_contexts, 'implml'):
        _contexts.implml = None
        _contexts.confml = None
        _contexts.implml_default = ParseContext()
        _contexts.confml_default = ParseContext()

def get_implml_context():
    """
    Get the current ImplML parse context.
    """
    _init_contexts()
    if _contexts.implml is not None:
        return _contexts.implml
    else:
        return _contexts.implml_default

def set_implml_context(context):
    """
    Set the current ImplML parse context.
    @param context: The context to set. If None, the default context
        will be used.
    """
    _init_contexts()
    _contexts.implml = context

def get_confml_context():
    """
    Get the current ConfML parse context.
    """
    _init_contexts()
    if _contexts.confml is not None:
        return _contexts.confml
    else:
        return _contexts.confml_default

def set_confml_context(context):
    """
    Set the current ConfML parse context.
    @param context: The context to set. If None, the default context
        will be used.
    """
    _init_contexts()
    _contexts.confml = context
