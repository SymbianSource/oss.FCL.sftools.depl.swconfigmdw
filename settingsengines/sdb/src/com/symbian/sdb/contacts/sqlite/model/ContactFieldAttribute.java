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

public enum ContactFieldAttribute {
	
	SQLITE_CONTACT_FIELD_ATT_HIDDEN				(0x00000001),
	SQLITE_CONTACT_FIELD_ATT_READYONLY			(0x00000002),
	SQLITE_CONTACT_FIELD_ATT_SYNCH				(0x00000004),
	SQLITE_CONTACT_FIELD_ATT_DISABLED			(0x00000008),
	SQLITE_CONTACT_FIELD_ATT_USERMASKED			(0x000000F0),
	SQLITE_CONTACT_FIELD_ATT_OVERIDELABEL		(0x00000100),
	SQLITE_CONTACT_FIELD_ATT_USETEMPLATEDATA	(0x00000200),
	SQLITE_CONTACT_FIELD_ATT_USERADDEDFIELD		(0x00000400),
	SQLITE_CONTACT_FIELD_ATT_TEMPLATE			(0x00000800),
	SQLITE_CONTACT_FIELD_ATT_LABELUNSPECIFIED	(0x40000000),
	SQLITE_CONTACT_FIELD_ATT_DELETED			(0x80000000),
	SQLITE_CONTACT_FIELD_ATT_TEMPLATEMASK		
		(
			
			SQLITE_CONTACT_FIELD_ATT_USERMASKED.getValue() |
			SQLITE_CONTACT_FIELD_ATT_SYNCH.getValue() |
			SQLITE_CONTACT_FIELD_ATT_READYONLY.getValue() |
			SQLITE_CONTACT_FIELD_ATT_HIDDEN.getValue()
		);
	
	
	private int value;

	private ContactFieldAttribute(int value) {
		this.value = value;
	}

	public int getValue() {
		return value;
	}

}
