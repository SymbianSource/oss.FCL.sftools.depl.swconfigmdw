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



def test_get_output_folder():
    output = ruleml.context.output
    return output


#add file to output folder
def test_add_file_to_output_folder():

    filename = "output_test.txt"
    output = ruleml.context.output
     
    f = open(output + '/' + filename,'w')
    f.writelines("Test!")
    f.close()
    
    return output + '/' + filename
