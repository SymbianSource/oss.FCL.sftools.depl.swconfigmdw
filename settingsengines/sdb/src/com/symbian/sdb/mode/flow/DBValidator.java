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

import com.symbian.sdb.contacts.dbms.ContactsDbValidator;
import com.symbian.sdb.exception.SDBValidationException;

/**
 * @author krzysztofZielinski
 *
 */
public interface DBValidator {

	/**
	 * @param inputDbFile
	 * @throws SDBValidationException 
	 */
	void validate(File inputDbFile) throws SDBValidationException;

	public void setContactsDbValidator(ContactsDbValidator contactsDbValidator);

}
