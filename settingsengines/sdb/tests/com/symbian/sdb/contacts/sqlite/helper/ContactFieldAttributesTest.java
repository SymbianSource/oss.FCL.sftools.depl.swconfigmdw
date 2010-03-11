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

import junit.framework.TestCase;

import com.symbian.sdb.contacts.sqlite.model.SQLiteContactFieldAttributes;
import com.symbian.sdb.contacts.sqlite.model.SQLiteExtendedAttributes;
import com.symbian.sdb.contacts.sqlite.model.StorageType;

/**
 * @author krzysztofZielinski
 *
 */
public class ContactFieldAttributesTest extends TestCase   {

    public void testAddAttribute() throws Exception {

        ContactFieldAttributes attributeBuilder = new ContactFieldAttributes();
        attributeBuilder.resetAttributes();
        attributeBuilder.addAttribute(SQLiteContactFieldAttributes.SYNCHRONIZE);
        attributeBuilder.addAttribute(SQLiteContactFieldAttributes.USE_TEMPLATE_DATA);

        long value = attributeBuilder.getValue();
        
        assertEquals(0x0204, value);
    }
    
    public void testSetStorageTypeText() throws Exception {

        ContactFieldAttributes attributeBuilder = new ContactFieldAttributes();
        attributeBuilder.resetAttributes();
        attributeBuilder.setStorageType(StorageType.TEXT.getValue());

        long value = attributeBuilder.getValue();
        
        assertEquals(0x0, value);
    }
    
    public void testSetStorageTypeBinary() throws Exception {

        ContactFieldAttributes attributeBuilder = new ContactFieldAttributes();
        attributeBuilder.resetAttributes();
        attributeBuilder.setStorageType(StorageType.STORE.getValue());

        long value = attributeBuilder.getValue();
        
        assertEquals(0x00100000, value);
    }
    
    public void testAddExtendedAttribute() throws Exception {

        ContactFieldAttributes attributeBuilder = new ContactFieldAttributes();
        attributeBuilder.resetAttributes();
        attributeBuilder.addExtendedAttributes(SQLiteExtendedAttributes.PRIVATE.getValue());

        long value = attributeBuilder.getValue();
        
        assertEquals(0x00001000, value);
    }

}
