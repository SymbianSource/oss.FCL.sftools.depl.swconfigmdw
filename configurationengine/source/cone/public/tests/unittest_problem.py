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

import unittest



from cone.public import api, exceptions

class TestProblems(unittest.TestCase):
    
    def test_create_from_generic_exception(self):
        ex = RuntimeError('foobar')
        self.assertEquals(
            api.Problem.from_exception(ex),
            api.Problem('foobar', severity = api.Problem.SEVERITY_ERROR))
    
    def test_create_from_cone_exception_simple(self):
        ex = exceptions.ConeException('foobar')
        self.assertEquals(
            api.Problem.from_exception(ex),
            api.Problem('foobar',
                        type     = '',
                        severity = api.Problem.SEVERITY_ERROR))
    
    def test_create_from_cone_exception_all_attributes(self):
        ex = exceptions.ConeException('foobar',
                                      problem_lineno = 101,
                                      problem_msg    = 'foobar2',
                                      problem_type   = 'foo.bar')
        self.assertEquals(
            api.Problem.from_exception(ex),
            api.Problem('foobar2',
                        type     = 'foo.bar',
                        line     = 101,
                        severity = api.Problem.SEVERITY_ERROR))
    
    def test_create_from_xml_parse_error(self):
        ex = exceptions.XmlParseError('XML parse error',
                                      problem_lineno = 1)
        self.assertEquals(
            api.Problem.from_exception(ex),
            api.Problem('XML parse error',
                        type     = 'xml',
                        line     = 1,
                        severity = api.Problem.SEVERITY_ERROR))

if __name__ == '__main__':
    unittest.main()
      
