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

/**
 * Represents communication address for SQLite database
 * 
 * @author krzysztofZielinski
 *
 */
public abstract class SQLiteCommunicationAddress {

    // ~ Fields ================================================================
    
    private Long contactId = null;;
    private String value = "";
    private String extraValue ="";
    private SQLiteCommunicationAddressType type;
    
    // ~ Constructors ==========================================================
    
    protected SQLiteCommunicationAddress(SQLiteCommunicationAddressType type) {
        super();
        this.type = type;
    }

    // ~ Getters/Setters =======================================================

    public SQLiteCommunicationAddressType getType() {
        return type;
    }

    public Long getContactId() {
        return contactId;
    }

    public void setContactId(Long contactId) {
        this.contactId = contactId;
    }

    public String getValue() {
        return value;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public String getExtraValue() {
        return extraValue;
    }

    public void setExtraValue(String extraValue) {
        this.extraValue = extraValue;
    }
}
