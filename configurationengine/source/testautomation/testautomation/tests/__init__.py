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

import unittest, os, sys

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(ROOT_PATH,'../..'))

# Find all unittest_*.py files in this folder
import re
__all__ = filter(lambda name: re.match(r'^unittest_.*\.py$', name) != None, os.listdir(ROOT_PATH))
# Strip .py endings
__all__ = map(lambda name: name[:-3], __all__)

def collect_suite():  
    suite = unittest.TestSuite()
    for test_module in __all__:
        # Load the test module dynamically and add it to the test suite
        module = __import__(test_module)
        suite.addTests(unittest.TestLoader().loadTestsFromModule(module))
    return suite      

def runtests():
    unittest.TextTestRunner(verbosity=2).run(collect_suite())

if __name__ == '__main__':
    runtests()
