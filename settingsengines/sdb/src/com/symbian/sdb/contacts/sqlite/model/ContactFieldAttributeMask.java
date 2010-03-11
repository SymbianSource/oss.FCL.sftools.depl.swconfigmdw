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

package com.symbian.sdb.contacts.sqlite.model;

public enum ContactFieldAttributeMask {
	
	SQLITE_CONTACT_FIELD_MASK_ATTRIB		(0xF0000FFF),
	SQLITE_CONTACT_FIELD_MASK_STORAGETYPE	(0x00F00000), 
	SQLITE_CONTACT_FIELD_MASK_EXTATTRIB		(0x000FF000);

	
	private int value;

	private ContactFieldAttributeMask(int value) {
		this.value = value;
	}

	public int getValue() {
		return value;
	}
	

}
