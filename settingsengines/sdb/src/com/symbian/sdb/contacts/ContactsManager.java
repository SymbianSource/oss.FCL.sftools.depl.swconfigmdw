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

package com.symbian.sdb.contacts;

import java.io.File;
import java.util.List;
import java.util.Set;

import org.apache.log4j.Logger;

import com.symbian.sdb.contacts.dbms.ContactsDbValidator;
import com.symbian.sdb.contacts.importer.ContactsImporter;
import com.symbian.sdb.contacts.model.Contact;
import com.symbian.sdb.contacts.model.Group;
import com.symbian.sdb.contacts.template.ITemplateModel;
import com.symbian.sdb.database.IConnectionProvider;
import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.mode.flow.IContactsManager;


/**
 * Class representing common flow for contact database creation (common for SQLite and DBMS)
 * 
 * @author krzysztofZielinski
 *
 */
public class ContactsManager implements IContactsManager {

    // ~ Fields ================================================================
	private static final Logger logger = Logger.getLogger(ContactsManager.class);
    public ContactsImporter contactsImporter;
    public ContactsPersister contactsPersister;
    public IConnectionProvider connectionProvider;


    // ~ Business Methods ======================================================

	public void persistContacts(Set<Contact> contacts, ITemplateModel templateModel) {
		logger.info("Persisting vCards");
		contactsPersister.persistContacts(contacts, templateModel);
	}

	public Set<Contact> importContacts(List<File> vCardFiles, ITemplateModel contactsTemplateModel) {
		logger.info("Importing vCards");
		return contactsImporter.importContacts(vCardFiles, contactsTemplateModel);
	}

    public void assignGroupsToContacts(Group group, Set<Contact> contacts) {
        for (Contact contact : contacts) {
            contact.addGroup(group);
        }
    }

    // ~ Getters/Setters =======================================================

    public void setContactImporter(ContactsImporter contactsImporter) {
        this.contactsImporter = contactsImporter;
    }

    public void setContactPersister(ContactsPersister contactsPersister) {
        this.contactsPersister = contactsPersister;
    }

	public void setConnectionProvider(IConnectionProvider connectionProvider) {
		this.connectionProvider = connectionProvider;
	}

	public void validateContactsDbSchema() throws SDBValidationException {
		contactsPersister.validateContactsDbSchema();
	}
}
