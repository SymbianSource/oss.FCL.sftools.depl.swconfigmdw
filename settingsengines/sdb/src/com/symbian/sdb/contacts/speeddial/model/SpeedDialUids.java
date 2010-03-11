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
// ContactHint.java
//



package com.symbian.sdb.contacts.speeddial.model;

/**
 * Enum class for speed dial UIDs that go into field contact type.
 * @author tanaslam1
 *
 */
public enum SpeedDialUids {
	
	UIDSPEEDDIAL_NULL		(0x00000000),
	UIDSPEEDDIAL_ONE		(0x100067C8),
	UIDSPEEDDIAL_TWO		(0x100067C9),
	UIDSPEEDDIAL_THREE		(0x100067CA),
	UIDSPEEDDIAL_FOUR		(0x100067CB),
	UIDSPEEDDIAL_FIVE		(0x100067CC), 
	UIDSPEEDDIAL_SIX		(0x100067CD),
	UIDSPEEDDIAL_SEVEN		(0x100067CE),
	UIDSPEEDDIAL_EIGHT		(0x100067CF),
	UIDSPEEDDIAL_NINE		(0x100067D0);
	
	private int uid;

	private SpeedDialUids(int value) {
		this.uid = value;
	}

	public int getValue() {
		return uid;
	}
}
