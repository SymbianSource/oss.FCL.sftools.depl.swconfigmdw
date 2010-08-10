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
from testautomation.copy_dir import copy_dir

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

def export_standalone(target_path):
    """
    Export any needed extra data for standalone tests.
    @param target_path: The path where the standalone tests are being exported.
    """
    copy_dir(source_dir             = os.path.join(ROOT_PATH, '../ConeRulePlugin/ruleplugin/evals/tests/layer_filtering_project'),
             target_dir             = os.path.join(target_path, 'testdata/uses_layer_test_project'),
             dir_ignore_functions   = [lambda d: d == '.svn'])
