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


#add file to output folder
def test_add_file_to_output_folder():

    filename = "output_test.txt"
    try:
        output = ruleml.context.output
        f = open(output + '/' + filename,'w')
        f.writelines("Test!")
        f.close()
    except Exception, e:
        print e
        
    return output + '/' + filename
