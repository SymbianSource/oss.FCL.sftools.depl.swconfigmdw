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

package com.symbian.sdb.contacts.model;

import java.util.Set;

import com.symbian.sdb.contacts.importer.vcard.SpeedDialData;

/**
 * @author krzysztofZielinski
 *
 */
public interface Contact {

    String getFirstName();

    String getLastName();

    Set<Group> getGroups();

    Set<PhoneNumber> getPhoneNumbers();

    Set<EmailAddress> getEmails();

    String getCompanyName();

    String getFirstNamePrn();

    String getLastNamePrn();

    String getCompanyNamePrn();
    
    void addGroup(Group group);
    
    Set<ContactField> getFields();

    boolean hasHintField(ContactHint hint);
    
    Set<SpeedDialData> getSpeedDialData();
}
