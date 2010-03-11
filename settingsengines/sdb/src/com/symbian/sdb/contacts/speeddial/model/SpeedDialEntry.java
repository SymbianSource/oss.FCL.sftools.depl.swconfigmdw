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



package com.symbian.sdb.contacts.speeddial.model;


/**
 * Represents single speed dial data entry in speed dial INI file i.e. data identifying contact and its phone number
 * to assign speed dial (represented as a position in higher level container - {@link DatabaseSpeedDialData})  
 * 
 * @author krzysztofZielinski
 *
 */
public class SpeedDialEntry {

	private static SpeedDialEntry EMPTY_ENTRY = new SpeedDialEntry(-1,"");
	
	private long contactId;
	private String phoneNumber;

	public SpeedDialEntry(long contactId, String phoneNumber) {
		super();
		this.contactId = contactId;
		this.phoneNumber = phoneNumber;
	}

	public long getContactId() {
		return contactId;
	}

	public String getPhoneNumber() {
		return phoneNumber;
	}

	/**
	 * Returns NULL speed dial data i.e. no speed dial assignment to for entry
	 * 
	 * @return
	 */
	public static SpeedDialEntry getEmptyEntry() {
		return EMPTY_ENTRY;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + (int) (contactId ^ (contactId >>> 32));
		result = prime * result
				+ ((phoneNumber == null) ? 0 : phoneNumber.hashCode());
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		SpeedDialEntry other = (SpeedDialEntry) obj;
		if (contactId != other.contactId)
			return false;
		if (phoneNumber == null) {
			if (other.phoneNumber != null)
				return false;
		} else if (!phoneNumber.equals(other.phoneNumber))
			return false;
		return true;
	}
}
