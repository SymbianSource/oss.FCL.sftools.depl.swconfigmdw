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

import com.symbian.sdb.contacts.model.common.AbstractByteType;


/**
 * Contact Type is bit-flags to identify the card type of the contact item 
 * and the type can be 1 of following and the types are stored in first byte 
 * of the 4 bytes integer (type_flags column).
 * These values are exclusive (i.e. a contact item can only be one of these types only. 
 * Therefore, an item cannot be, for example, the own card and an ICC entry).
 */
public class ContactType extends AbstractByteType {

    // ~ Global Constant Fields ================================================
    
    public static final ContactType CARD = new ContactType((byte)0);
    public static final ContactType OWN_Card = new ContactType((byte)1);
    public static final ContactType ICC_ENTRY = new ContactType((byte)2);
    public static final ContactType GROUP = new ContactType((byte)3);
    
    public static final ContactType TEMPLATE = new ContactType((byte)4);
    public static final ContactType CardTemplate = new ContactType((byte)5);
    public static final ContactType UnknownType = new ContactType((byte)6);
    
    // ~ Constructors ==========================================================
    
    private ContactType(byte value) {
        super(value);
    }
}
