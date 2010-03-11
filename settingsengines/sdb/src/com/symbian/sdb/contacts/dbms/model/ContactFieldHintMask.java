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



package com.symbian.sdb.contacts.dbms.model;

public enum ContactFieldHintMask {
	
	DBMS_CONTACT_FIELD_MASK_INDEX			(0xFFC00000),
	DBMS_CONTACT_FIELD_MASK_HINT    		(0x001FFFFF),
	DBMS_CONTACT_FIELD_HAS_ADDITIONAL_UIDS	(0x00200000);
		
	private long value;

	private ContactFieldHintMask(long value) {
		this.value = value;
	}

	public long getValue() {
		return value;
	}
	
}
