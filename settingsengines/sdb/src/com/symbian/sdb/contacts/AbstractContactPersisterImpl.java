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

import java.util.HashSet;
import java.util.Set;

import com.symbian.sdb.contacts.model.Contact;
import com.symbian.sdb.contacts.template.ITemplateModel;


/**
 * Class responsible for persisting contacts in database i.e. database creation (db file, contact schema, basic data), 
 * SQL generation for contacts data, SQL execution.
 * 
 * @author krzysztofZielinski
 *
 */
public abstract class AbstractContactPersisterImpl<T extends DatabaseSpecificContact> implements ContactsPersister {

    // ~ Business Methods ======================================================

    public void persistContacts(Set<Contact> contacts, ITemplateModel templateModel) {
    	Set<T> databaseSpecificContacts = transform(contacts, templateModel);
    	persistContactsInDB(databaseSpecificContacts);
    }

    // ~ Internal Implementation Methods =======================================

    /**
     * Transform contacts from basic (generic) contact model to database specific model e.g. SQLite model, DBMS model
     * 
     * @param contacts
     */
    public Set<T> transform(Set<Contact> contacts, ITemplateModel templateModel)  {
        Set<T> dbSpecificContacts = new HashSet<T>();
        
        for (Contact contact : contacts) {
            T dbSpecificContact = transformContact(contact, templateModel);
            dbSpecificContacts.add(dbSpecificContact);
        }
        
        return dbSpecificContacts;
    }

    /**
     * Persists contact in database.
     * 
     */
    public void persistContactsInDB(Set<T> contacts)    {
        for (T contact : contacts) {
            createContactCard(contact);
        }
    }

    /**
     * Persists contact card for contact
     * 
     */
    public abstract void createContactCard(T dbSpecificContact);
    
    /**
     * Transform single contact from generic model to db specific model
     * 
     * @param contact
     * @return
     */
    public abstract T transformContact(Contact contact, ITemplateModel templateModel);

}
