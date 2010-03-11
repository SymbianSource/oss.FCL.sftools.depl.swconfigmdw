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

import com.symbian.sdb.contacts.ContactsExeption;

@SuppressWarnings("serial")
public class VCardParseException extends ContactsExeption {

	public VCardParseException() {
		super();
	}

	public VCardParseException(String message, Throwable cause) {
		super(message, cause);
	}

	public VCardParseException(String message) {
		super(message);
	}

	public VCardParseException(Throwable cause) {
		super(cause);
	}

}
