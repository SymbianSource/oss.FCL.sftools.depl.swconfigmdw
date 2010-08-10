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
## 
# @author Teemu Rytkonen

class ConeException(Exception):
    """
    Base class for ConE exceptions.
    
    The attributes ``problem_desc`` and ``problem_lineno`` contain a description of
    the error and the line on which the error occurred, if available.
    The exception message itself may be composed of these two to make it more
    readable, but it may also just be the same as the description.
    
    @message: Exception message.
    @param problem_lineno: The line number for api.Problem conversion. Can be None to
        signify that the line number is not available.
    @param problem_desc: Error description for api.Problem conversion. If None,
        the exception message will be used here also.
    @param problem_type: Problem type for api.Problem conversion. If None, the
        class-level default will be used.
    """
    
    #: Problem type for conversion to api.Problem.
    #: A default can be set on the exception class level, but it may
    #: also be set for individual exception instances.
    problem_type = None
    
    def __init__(self, message='', problem_lineno=None, problem_msg=None, problem_type=None):
        Exception.__init__(self, message)
        self.problem_lineno = problem_lineno
        self.problem_msg = problem_msg or message
        if problem_type is not None:
            self.problem_type = problem_type

class NotSupportedException(ConeException):
    def __init__(self, message=""):
        self.message = "Not supported! %s" % message
        ConeException.__init__(self, self.message)

class StorageException(ConeException):
    pass
    
class NotResource(StorageException):
    pass
    
class NotFound(ConeException):
    pass
    
class NotBound(ConeException):
    pass
    
class NoParent(ConeException):
    pass
    
class AlreadyExists(ConeException):
    pass
    
class ConePersistenceError(ConeException):
    pass
    
class ParseError(ConeException):
    pass

class XmlParseError(ParseError):
    problem_type = 'xml'

class XmlSchemaValidationError(ParseError):
    problem_type = 'schema'

class ConfmlParseError(ParseError):
    problem_type = 'model.confml'

class ImplmlParseError(ParseError):
    problem_type = 'model.implml'

class IncorrectClassError(ConeException):
    pass
    
class InvalidRef(ConeException):
    pass
    
class InvalidObject(ConeException):
    """ This error is raised inside the ObjectContainer class when in any container 
    operation an invalid object is encountered. 
    """
    pass

class NameIdMappingError(ConeException):
    """
    Exception raised when resolving a name-ID mapped value fails.
    """
    pass

