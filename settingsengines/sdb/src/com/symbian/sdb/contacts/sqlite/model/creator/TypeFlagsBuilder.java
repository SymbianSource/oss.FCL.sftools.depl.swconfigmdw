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

package com.symbian.sdb.contacts.sqlite.model.creator;

import com.symbian.sdb.contacts.model.Contact;
import com.symbian.sdb.contacts.model.ContactHint;
import com.symbian.sdb.contacts.sqlite.model.ContactHintField;
import com.symbian.sdb.contacts.sqlite.model.ContactType;
import com.symbian.sdb.contacts.sqlite.model.SQLiteContactAttribute;
import com.symbian.sdb.contacts.sqlite.model.TypeFlags;

/**
 * @author krzysztofZielinski
 *
 */
public class TypeFlagsBuilder {

    private TypeFlags typeFlags;
    
    public TypeFlagsBuilder() {
        super();
    }

    public void createNewTypeFlags(ContactType contactType) {
        this.typeFlags = new TypeFlags(contactType);
    }

    public TypeFlags getTypeFlags() {
        return typeFlags;
    }

    public void createContactHintFields(Contact contact) {
        ContactHintField contactHintFields = new ContactHintField();
        
        for (ContactHint contactHint : ContactHint.sqliteValues()) {
            if (contact.hasHintField(contactHint)) {
                contactHintFields.addHint(contactHint);
            }
        }
        
        typeFlags.setContactHintField(contactHintFields);
    }

    public void createAttributes() {
        typeFlags.setContactAttributes(SQLiteContactAttribute.COMPRESSED_GUID);
    }
}
