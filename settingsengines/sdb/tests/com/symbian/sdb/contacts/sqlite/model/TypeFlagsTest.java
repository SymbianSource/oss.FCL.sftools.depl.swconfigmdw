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

package com.symbian.sdb.contacts.sqlite.model;

import junit.framework.Assert;

import org.junit.Test;

import com.symbian.sdb.contacts.model.ContactHint;


/**
 * @author krzysztofZielinski
 *
 */
public class TypeFlagsTest {

    @Test
    public void testSetContactAttributes() throws Exception {
        TypeFlags typeFlags = new TypeFlags(ContactType.CARD);
        typeFlags.setContactAttributes(SQLiteContactAttribute.SYSTEM);
        typeFlags.setContactAttributes(SQLiteContactAttribute.DELETED);
        
        Assert.assertEquals(0x00090000, typeFlags.getValue());
    }
    
    @Test
    public void testTypeFlags() throws Exception {

        // 0x03
        TypeFlags typeFlags = new TypeFlags(ContactType.GROUP);

        // 0x0C
        typeFlags.setContactAttributes(SQLiteContactAttribute.COMPRESSED_GUID);
        typeFlags.setContactAttributes(SQLiteContactAttribute.DELETED);
        
        // 0x0244
        ContactHintField contactHintField = new ContactHintField();
        contactHintField.addHint(ContactHint.HOME);
        contactHintField.addHint(ContactHint.IM_ADDRESS);
        contactHintField.addHint(ContactHint.LAND_LINE);
        
        typeFlags.setContactHintField(contactHintField);
        
        Assert.assertEquals(0x30C0244, typeFlags.getValue());
    }
    
}
