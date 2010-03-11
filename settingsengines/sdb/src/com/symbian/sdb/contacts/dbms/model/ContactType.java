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

package com.symbian.sdb.contacts.dbms.model;

import com.symbian.sdb.contacts.ContactsExeption;
import com.symbian.sdb.contacts.template.MappingMissingException;
import com.symbian.sdb.contacts.template.TemplateMapper;


/**
 * Represents contact type for DBMS database
 *
 */
public class ContactType {

    // ~ Global Constant Fields ================================================
	
    public static final ContactType CARD =          new ContactType("KUidContactCardValue");
    public static final ContactType GROUP =         new ContactType("KUidContactGroupValue");
    public static final ContactType OWN_Card =      new ContactType("KUidContactOwnCardValue");
    public static final ContactType ICC_ENTRY =     new ContactType("KUidContactICCEntryValue");
    public static final ContactType TEMPLATE =      new ContactType("KUidContactTemplateValue");
    public static final ContactType CARD_TEMPLATE = new ContactType("KUidContactCardTemplateValue");

    private String value;
    
    // ~ Constructors ========================================================== 
    
    public ContactType(String uid) {
    	value = uid;
    }
 
    // ~ Getters/Setters =======================================================

    public int getValue() throws ContactsExeption {
    	Integer result = null;
    	try {
    		result = TemplateMapper.getInstance().getContactTypeMapping(value);
    	} catch (MappingMissingException ex) {
    		throw new ContactsExeption("Mapping for " + value + " not resolved: " + ex.getMessage(), ex);
    	} 
        return result;
    }
}
