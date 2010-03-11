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

import java.util.Set;

import com.symbian.sdb.contacts.model.Contact;
import com.symbian.sdb.contacts.template.ITemplateModel;
import com.symbian.sdb.exception.SDBValidationException;

/**
 * Is responsible for persisting contacts in a database
 * 
 * @author krzysztofZielinski
 *
 */
public interface ContactsPersister {

	void persistContacts(Set<Contact> contacts, ITemplateModel templateModel);
	/**
	 * @throws SDBValidationException 
	 * 
	 */
	void validateContactsDbSchema() throws SDBValidationException;
}
