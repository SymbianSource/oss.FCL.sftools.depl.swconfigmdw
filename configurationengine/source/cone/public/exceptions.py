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
    pass

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
    """
    Exception raised when invalid data is attempted to be parsed.
    
    The attributes ``desc`` and ``lineno`` contain a description of
    the error and the line on which the error occurred, if available.
    The exception message itself may be composed of these two to make it more
    readable, but it may also just be the same as the description.
    
    @message: Exception message.
    @param lineno: The line number where the error occurred. Can be None to
        signify that the line number is not available.
    @param desc: Error description. If None, the exception message will be
        used here also.
    """
    def __init__(self, message, lineno=None, desc=None):
        ConeException.__init__(self, message)
        self.lineno = lineno
        self.desc = desc or message

class XmlParseError(ParseError):
    pass

class IncorrectClassError(ConeException):
    pass
    
class InvalidRef(ConeException):
    pass
    
class InvalidObject(ConeException):
    """ This error is raised inside the ObjectContainer class when in any container 
    operation an invalid object is encountered. 
    """
    pass
