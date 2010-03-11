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


import java.util.HashSet;
import java.util.Set;

import com.symbian.sdb.contacts.model.Contact;

/**
 * Contacts model class for SQLite database schema 
 * 
 * @author krzysztofZielinski
 *
 */
public class SQLiteContactCard extends AbstractSQLiteContact {
    
    // ~ Fields ================================================================

    private Contact basicContact;
    private Set<SQLiteEmailAddress> emailAddresses = new HashSet<SQLiteEmailAddress>();
    private Set<SQLitePhoneNumber> phoneNumbers = new HashSet<SQLitePhoneNumber>();
    
    // ~ Constructors ==========================================================
    
    public SQLiteContactCard(Contact contact) {
        super();
        this.basicContact = contact;
    }
    
    // ~ Getters/Setters =======================================================

    public String getFirstName() {
        return this.basicContact.getFirstName();
    }

    public String getLastName() {
        return this.basicContact.getLastName();
    }

    public Set<SQLitePhoneNumber> getPhoneNumbers() {
        return phoneNumbers;
    }

    public Set<SQLiteEmailAddress> getEmailAddresses() {
        return emailAddresses;
    }

    public String getCompanyName() {
        return this.basicContact.getCompanyName();
    }

    public String getFirstNamePrn() {
        return this.basicContact.getFirstNamePrn();
    }

    public String getLastNamePrn() {
        return this.basicContact.getLastNamePrn();
    }

    public String getCompanyNamePrn() {
        return this.basicContact.getCompanyNamePrn();
    }

}
