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



package com.symbian.sdb.contacts.speeddial;

/**
 * Represents data entry provided by user assigning phone number with speed dial number
 * 
 * @author krzysztofZielinski
 *
 */
public class SpeedDialAssignmentEntry {

	private String phoneNumber;
	private int speedDialNumber;
	private long contactId;
	
	public SpeedDialAssignmentEntry(String phoneNumber, int speedDialNumber, long contactId) {
		super();
		this.phoneNumber = phoneNumber;
		this.speedDialNumber = speedDialNumber;
		this.contactId = contactId;
	}
	
	public String getPhoneNumber() {
		return phoneNumber;
	}

	public int getSpeedDialNumber() {
		return speedDialNumber;
	}

	public long getContactId() {
		return contactId;
	}
}
