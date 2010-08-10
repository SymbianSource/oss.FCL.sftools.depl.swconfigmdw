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

from cone.public import api, parsecontext

class ValidationParseContext(parsecontext.ParseContext):
    """
    Parse context that collects all exceptions and problems that
    occur during parsing into a problem list.
    """
    def __init__(self):
        parsecontext.ParseContext.__init__(self)
        self.problems = []
        
    def _handle_exception(self, exception, file_path):
        problem = api.Problem.from_exception(exception)
        problem.file = file_path
        self.problems.append(problem)
    
    def _handle_problem(self, problem, file_path):
        problem.file = file_path
        self.problems.append(problem)