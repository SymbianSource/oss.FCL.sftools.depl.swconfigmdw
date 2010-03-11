// Copyright (c) 2008-2009 Nokia Corporation and/or its subsidiary(-ies).
// All rights reserved.
// This component and the accompanying materials are made available
// under the terms of "Eclipse Public License v1.0"
// which accompanies this distribution, and is available
// at the URL "http://www.eclipse.org/legal/epl-v10.html".
//
// Initial Contributors:
// Nokia Corporation - initial contribution.
//
// Contributors:
//
// Description:
//

package com.symbian.sdb.contacts.sqlite.helper;

import java.util.Arrays;

import junit.framework.TestCase;


/**
 * @author krzysztofZielinski
 *
 */
public class TextFieldHeaderTest extends TestCase   {

    public void testCreateSimpleTextFieldsHeader() throws Exception {
        byte[] expectedFieldHeaderAsBytes = { 0x00, 0x00, 0x02, 0x04, // contact field attributes
                                              0x00, 0x00, 0x00, 0x03, // contact field GUID
                                              0x00, 0x00, 0x00, 0x03};// template field id 
        
        byte[] fieldHeader = createFieldHeader();
        
        assertTrue(Arrays.equals(expectedFieldHeaderAsBytes, fieldHeader));
    }

    private byte[] createFieldHeader() {
        FieldHeader fieldHeaderBuilder = new TextFieldHeaderImpl();
        
        fieldHeaderBuilder.createNewFieldHeader();
        
        int contactFieldAttributes = 0x00000204;
        fieldHeaderBuilder.setContactFieldAttributes(contactFieldAttributes);
        fieldHeaderBuilder.setContactFieldGuid(3);
        fieldHeaderBuilder.setTemplateFieldId(3);
        
        byte[] blobBytes = fieldHeaderBuilder.getFieldHeader();
        return blobBytes;
    }


}
