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
// GenericFlowInputDatabaseValidator.java
//



package com.symbian.sdb.mode.flow;

import java.io.File;

import com.symbian.sdb.contacts.dbms.ContactsDbValidator;
import com.symbian.sdb.exception.SDBValidationException;

/**
 * @author krzysztofZielinski
 *
 */
public class ContactsFlowInputDatabaseValidator implements DBValidator {

	private GenericFlowInputDatabaseValidator genericFlowInputDatabaseValidator = new GenericFlowInputDatabaseValidator();
	ContactsDbValidator contactsDbValidator;
	
	public void validate(File inputDbFile) throws SDBValidationException {
		genericFlowInputDatabaseValidator.validate(inputDbFile);
		contactsDbValidator.validateContactsDbSchema();
	}

	public void setContactsDbValidator(ContactsDbValidator contactsDbValidator) {
		this.contactsDbValidator = contactsDbValidator;
	}

}
