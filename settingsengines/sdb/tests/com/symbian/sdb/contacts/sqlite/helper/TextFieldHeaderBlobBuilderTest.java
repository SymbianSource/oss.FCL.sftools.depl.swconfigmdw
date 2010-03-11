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

import static junit.framework.Assert.assertEquals;

import org.junit.Before;
import org.junit.Test;

import com.symbian.sdb.PropertyRestorerTestCase;
import com.symbian.sdb.contacts.helper.HexStringConverter;
import com.symbian.sdb.contacts.sqlite.model.SQLiteContactFieldAttributes;
import com.symbian.sdb.contacts.sqlite.model.StorageType;


/**
 * @author krzysztofZielinski
 *
 */
public class TextFieldHeaderBlobBuilderTest extends PropertyRestorerTestCase    {

    /**
     * 
     */
    private static final int FAMILY_NAME_TEMPLATE_FIELD_ID = 3;

    @Before
    public void setUp() throws Exception {
        setPropertiesForDBPaths();
    }
    
    @Test
    public void testCreateSimpleTextFieldHeaderBlob() throws Exception {

        byte[] blob = createTextFieldsHeaderBlob();
        String blobAsHexString = HexStringConverter.convertByteArrayToHexString(blob);
        
        String expectedString = "0400000002040200000300000003000000";
        
        assertEquals(expectedString, blobAsHexString);
    }
    private byte[] createTextFieldsHeaderBlob() {
        
        TextFieldHeaderBlobBuilder blobBuilder = new TextFieldHeaderBlobBuilder();
        FieldHeader fieldHeader = createFieldHeader();
        blobBuilder.addTextFieldHeader(fieldHeader);
        blobBuilder.tryToBuildBlob();
        
        return blobBuilder.getBlob();
    }

    private FieldHeader createFieldHeader() {
        FieldHeader fieldHeader = new TextFieldHeaderImpl();
        fieldHeader.createNewFieldHeader();
        
        ContactFieldAttributes contactFieldAttributes = createFieldAttributes();
        fieldHeader.setContactFieldAttributes(contactFieldAttributes.getValue());
        
        int templateIdForCurrentField = 0;
        fieldHeader.setTemplateFieldId(templateIdForCurrentField);
        fieldHeader.setContactFieldGuid(FAMILY_NAME_TEMPLATE_FIELD_ID);

        return fieldHeader;
    }

    private ContactFieldAttributes createFieldAttributes() {
        ContactFieldAttributes contactFieldAttributes = new ContactFieldAttributes();
        contactFieldAttributes.addAttribute(SQLiteContactFieldAttributes.SYNCHRONIZE);
        contactFieldAttributes.addAttribute(SQLiteContactFieldAttributes.USE_TEMPLATE_DATA);
        contactFieldAttributes.setStorageType(StorageType.TEXT.getValue());

        return contactFieldAttributes;
    }
    
}
