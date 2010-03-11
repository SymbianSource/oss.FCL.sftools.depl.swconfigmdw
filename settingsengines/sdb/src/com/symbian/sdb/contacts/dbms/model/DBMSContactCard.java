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

import java.util.HashSet;
import java.util.Set;

/**
 * @author krzysztofZielinski
 *
 */
public class DBMSContactCard extends AbstractDBMSContact {
    
    // ~ Fields ================================================================
    
    private Set<DBMSPhoneNumber> phoneNumbers = new HashSet<DBMSPhoneNumber>();
    private Set<DBMSEmailAddress> emailAddresses = new HashSet<DBMSEmailAddress>();
    
    // ~ Constructors ==========================================================
    
    public DBMSContactCard() {
        super();
        this.type = ContactType.CARD;
        this.identityTable = new IdentityTable(this.type);
    }
    
    // ~ Business Methods ======================================================

    public Set<DBMSPhoneNumber> getPhoneNumbers() {
        return phoneNumbers;
    }

    public Set<DBMSEmailAddress> getEmailAddresses() {
        return emailAddresses;
    }

    public void setPrefTemplateRefId(Integer prefTemplateRefId) {
        this.prefTemplateRefId = prefTemplateRefId;
    }

}
