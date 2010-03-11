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
// ContactFieldAttributeFlag.java
//



package com.symbian.sdb.contacts.dbms.model;

public enum ContactFieldExtendedAttributeFlag {

	PRIVATE				(0x00000001),
	SPEEDIAL			(0x00000002),
	USERDEFINEDFILTER	(0x00000004),
	USERDEFINEDFILTER1	(0x00000008),
	USERDEFINEDFILTER2	(0x00000010),
	USERDEFINEDFILTER3	(0x00000020),
	USERDEFINEDFILTER4	(0x00000040);
	
	private int extAttribute;

	public int getValue() {
		return extAttribute;
	}

	private ContactFieldExtendedAttributeFlag(int extAttribute) {
		this.extAttribute = extAttribute;
	}
}
