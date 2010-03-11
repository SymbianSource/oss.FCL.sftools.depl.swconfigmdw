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

package com.symbian.sdb.contacts.importer;

import java.util.Set;

import com.symbian.sdb.contacts.importer.vcard.SpeedDialData;
import com.symbian.sdb.contacts.model.Contact;
import com.symbian.sdb.contacts.model.ContactField;
import com.symbian.sdb.contacts.model.ContactHint;
import com.symbian.sdb.contacts.model.ContactImpl;
import com.symbian.sdb.contacts.model.EmailAddress;
import com.symbian.sdb.contacts.model.Group;
import com.symbian.sdb.contacts.model.PhoneNumber;

/**
 * @author krzysztofZielinski
 *
 */
public class ContactWrapper implements Contact  {

    private ContactImpl contactImpl;

    public ContactWrapper(ContactImpl contactImpl) {
        super();
        this.contactImpl = contactImpl;
    }


    /* (non-Javadoc)
     * @see com.symbian.sdb.contacts.model.Contact#getCompanyName()
     */
    public String getCompanyName() {
        return (contactImpl.getCompanyName() != null ? contactImpl.getCompanyName().getTextValue(): null);
    }

    /* (non-Javadoc)
     * @see com.symbian.sdb.contacts.model.Contact#getCompanyNamePrn()
     */
    public String getCompanyNamePrn() {
        return (contactImpl.getCompanyNamePrn() != null ? contactImpl.getCompanyNamePrn().getTextValue(): null);
    }

    /* (non-Javadoc)
     * @see com.symbian.sdb.contacts.model.Contact#getEmails()
     */
    public Set<EmailAddress> getEmails() {
        
        return contactImpl.getEmails();
    }

    /* (non-Javadoc)
     * @see com.symbian.sdb.contacts.model.Contact#getFirstName()
     */
    public String getFirstName() {
        return (contactImpl.getFirstName() != null ? contactImpl.getFirstName().getTextValue(): null);
    }

    /* (non-Javadoc)
     * @see com.symbian.sdb.contacts.model.Contact#getFirstNamePrn()
     */
    public String getFirstNamePrn() {
        return (contactImpl.getFirstNamePrn() != null ? contactImpl.getFirstNamePrn().getTextValue(): null);
    }

    /* (non-Javadoc)
     * @see com.symbian.sdb.contacts.model.Contact#getGroups()
     */
    public Set<Group> getGroups() {
        return contactImpl.getGroups();
    }

    /* (non-Javadoc)
     * @see com.symbian.sdb.contacts.model.Contact#getLastName()
     */
    public String getLastName() {
        return (contactImpl.getLastName() != null ? contactImpl.getLastName().getTextValue(): null);
    }

    /* (non-Javadoc)
     * @see com.symbian.sdb.contacts.model.Contact#getLastNamePrn()
     */
    public String getLastNamePrn() {
        return (contactImpl.getLastNamePrn() != null ? contactImpl.getLastNamePrn().getTextValue(): null);
    }

    /* (non-Javadoc)
     * @see com.symbian.sdb.contacts.model.Contact#getPhoneNumbers()
     */
    public Set<PhoneNumber> getPhoneNumbers() {
        return contactImpl.getPhoneNumbers();
    }
    
    public void addGroup(Group group)   {
    	if(group != null){
    		this.contactImpl.addGroup(group);
    	}
    }

    /* (non-Javadoc)
     * @see com.symbian.sdb.contacts.model.Contact#getFields()
     */
    public Set<ContactField> getFields() {
        return this.contactImpl.getFields();
    }
	
    /**
     * returns true if the contact supports the specified hint value.
     */
	public boolean hasHintField(ContactHint hint){
		return contactImpl.hasHintField(hint);
	}
	
	public Set<SpeedDialData> getSpeedDialData()	{
		return contactImpl.getSpeedDialData();
	}
}
