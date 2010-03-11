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

package com.symbian.sdb.mode.flow;

import java.io.File;
import java.util.List;
import java.util.Set;

import com.symbian.sdb.contacts.dbms.ContactsDbValidator;
import com.symbian.sdb.contacts.model.Contact;
import com.symbian.sdb.contacts.model.Group;
import com.symbian.sdb.contacts.template.ITemplateModel;


/**
 * Interface for basic contacts use cases
 * 
 * @author krzysztofZielinski
 *
 */
public interface IContactsManager extends ContactsDbValidator {

	public void persistContacts(Set<Contact> contacts, ITemplateModel templateModel);

	public Set<Contact> importContacts(List<File> vCardFiles, ITemplateModel contactsTemplateModel);

	public void assignGroupsToContacts(Group group, Set<Contact> contacts);

}
