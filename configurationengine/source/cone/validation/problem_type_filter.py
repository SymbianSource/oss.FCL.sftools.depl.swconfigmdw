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

class ProblemTypeFilter(object):
    """
    Class for filtering problem types.
    
    An instance of this class can be constructed with includes
    and excludes, and then it can be asked if a certain problem
    type matches and should be included.
    """
    def __init__(self, includes, excludes):
        self._includes = [Pattern(expr) for expr in includes]
        self._excludes = [Pattern(expr) for expr in excludes]
    
    def match(self, problem_type):
        """
        Check whether the given problem type matches the filter or not.
        @return: True if matches (should be included), False if not.
        """
        # No filters: always match
        if not self._includes and not self._excludes:
            return True
        
        # Filter out entries that don't match includes
        if self._includes and not self._match(self._includes, problem_type):
            return False
        
        # Filter out entries that match excludes
        if self._excludes and self._match(self._excludes, problem_type):
            return False
        
        return True
    
    def filter(self, lst, key=lambda item: item.type):
        result = []
        for item in lst:
            if self.match(key(item)):
                result.append(item)
        return result
    
    def _match(self, patterns, problem_type):
        for p in patterns:
            if p.match(problem_type):
                return True
        return False

class Pattern(object):
    def __init__(self, pattern):
        self.elements = pattern.split('.')
    
    def match(self, problem_type):
        type_elements = problem_type.split('.')
        for i in xrange(max(len(type_elements), len(self.elements))):
            if i < len(type_elements):
                type_elem = type_elements[i]
            else:
                # The pattern is longer than the type, so it cannot
                # possibly match.
                # E.g. type = 'foo', pattern = 'foo.bar.baz'
                return False
            
            if i < len(self.elements):
                pattern_elem = self.elements[i]
            else:
                # The pattern ends and we have matched so far, so the
                # type is a sub-type of an included one.
                # E.g. type = 'foo.bar.baz', pattern = 'foo.bar'
                return True
            
            if pattern_elem != '*' and type_elem != pattern_elem:
                return False
        
        return True
        