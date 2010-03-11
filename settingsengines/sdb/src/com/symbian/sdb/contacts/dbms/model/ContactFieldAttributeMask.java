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

public enum ContactFieldAttributeMask {
	
	DBMS_CONTACT_FIELD_MASK_ATTRIB					(0x00000FFF),
	DBMS_CONTACT_FIELD_MASK_STORAGETYPE				(0x0003F000), 
	DBMS_CONTACT_FIELD_MASK_ADDITIONALFIELDSCOUNT	(0x003C0000),
	DBMS_CONTACT_FIELD_MASK_TEMPLATEID				(0xFFC00000),
	DBMS_CONTACT_FIELD_MASK_CATEGORY   				(0x000000F0);
	
	private long value;

	private ContactFieldAttributeMask(long value) {
		this.value = value;
	}

	public long getValue() {
		return value;
	}	

}
