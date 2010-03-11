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

import java.io.File;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import com.symbian.sdb.contacts.model.Contact;
import com.symbian.sdb.contacts.model.ContactImpl;
import com.symbian.sdb.contacts.template.ITemplateModel;

/**
 * @author krzysztofZielinski
 *
 */
public class VCardContactImporter implements ContactsImporter {

    // ~ Injected Fields =======================================================
    private ContactReader contactReader;
    
    // ~ Business Methods ======================================================
    
    public Set<Contact> importContacts(List<File> filesWithContacts, ITemplateModel contactsTemplateModel) {
        Set<ContactImpl> contactsImpl = contactReader.readContacts(filesWithContacts,contactsTemplateModel);
        Set<Contact> contacts = covertToContacts(contactsImpl);
        return contacts;
    }

    /**
     * @param contactsImpl
     * @return
     */
    private Set<Contact> covertToContacts(Set<ContactImpl> contactsImpl) {
        Set<Contact> contacts = new HashSet<Contact>();
        Contact contact = null;
        for (ContactImpl contactImpl : contactsImpl) {
            contact = new ContactWrapper(contactImpl);
            contacts.add(contact);
        }
        return contacts;
    }

	/**
	 * @param contactReader the contactReader to set
	 */
	public void setContactReader(ContactReader contactReader) {
		this.contactReader = contactReader;
	}

}
