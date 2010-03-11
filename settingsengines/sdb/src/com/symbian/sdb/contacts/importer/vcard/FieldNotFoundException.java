// Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
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



package com.symbian.sdb.contacts.importer.vcard;

import com.symbian.sdb.contacts.SystemException;

/**
 * @author krzysztofZielinski
 *
 */
public class FieldNotFoundException extends SystemException {

	/**
	 * @param message
	 * @param cause
	 */
	private FieldNotFoundException(String message, Throwable cause) {
		super(message, cause);
	}

	/**
	 * @param arg0
	 */
	FieldNotFoundException(String arg0) {
		super(arg0);
	}

	/**
	 * @param cause
	 */
	private FieldNotFoundException(Throwable cause) {
		super(cause);
	}

}
