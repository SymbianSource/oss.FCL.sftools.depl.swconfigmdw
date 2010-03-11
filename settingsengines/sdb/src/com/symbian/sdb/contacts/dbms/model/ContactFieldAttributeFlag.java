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

package com.symbian.sdb.contacts.dbms.model;

public enum ContactFieldAttributeFlag {
	
	
	DBMS_CONTACT_FIELD_ATT_HIDDEN					(0x00000001),
	DBMS_CONTACT_FIELD_ATT_READYONLY				(0x00000002),
	DBMS_CONTACT_FIELD_ATT_SYNCH					(0x00000004),
	DBMS_CONTACT_FIELD_ATT_DISABLED					(0x00000008),
	DBMS_CONTACT_FIELD_ATT_USERFLAG					(0x00000010),
	DBMS_CONTACT_FIELD_ATT_OVERIDELABEL				(0x00000100),
	DBMS_CONTACT_FIELD_ATT_USETEMPLATEDATA			(0x00000200),
	DBMS_CONTACT_FIELD_ATT_USERADDEDFIELD			(0x00000400),
	DBMS_CONTACT_FIELD_ATT_TEMPLATE					(0x00000800),
	DBMS_CONTACT_FIELD_ATT_LABELUNSPECIFIED			(0x40000000),
	DBMS_CONTACT_FIELD_ATT_DELETED					(0x80000000),
	DBMS_CONTACT_FIELD_ATT_TEMPLATEID				(0x000003FF),
	DBMS_CONTACT_FIELD_ATT_TEMPLATEMASK		
		(
			
			ContactFieldAttributeMask.DBMS_CONTACT_FIELD_MASK_CATEGORY.getValue() |
			DBMS_CONTACT_FIELD_ATT_SYNCH.getValue() |
			DBMS_CONTACT_FIELD_ATT_READYONLY.getValue() |
			DBMS_CONTACT_FIELD_ATT_HIDDEN.getValue()
		);
	
	
	private long value;

	private ContactFieldAttributeFlag(long value) {
		this.value = value;
	}

	public long getValue() {
		return value;
	}


}
