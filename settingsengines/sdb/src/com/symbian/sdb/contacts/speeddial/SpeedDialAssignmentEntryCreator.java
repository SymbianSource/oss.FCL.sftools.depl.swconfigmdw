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
 * @author krzysztofzielinski
 *
 */
public class SpeedDialAssignmentEntryCreator {

	private String phoneNumber;
	private int speedDialNumber;
	private long contactId;

	/**
	 * @param phoneNumber the phoneNumber to set
	 */
	public void setPhoneNumber(String phoneNumber) {
		this.phoneNumber = phoneNumber;
	}
	/**
	 * @param speedDialNumber the speedDialNumber to set
	 */
	public void setSpeedDialNumber(int speedDialNumber) {
		this.speedDialNumber = speedDialNumber;
	}
	/**
	 * @param contactId the contactId to set
	 */
	public void setContactId(long contactId) {
		this.contactId = contactId;
	}

	public SpeedDialAssignmentEntry buildSpeedDialAssignmentEntry()	{
		return new SpeedDialAssignmentEntry(phoneNumber,speedDialNumber,contactId);
	}
	/**
	 * @return the speedDialNumber
	 */
	public int getSpeedDialNumber() {
		return speedDialNumber;
	}
	/**
	 * @return the phoneNumber
	 */
	public String getPhoneNumber() {
		return phoneNumber;
	}
	/**
	 * @return the contactId
	 */
	public long getContactId() {
		return contactId;
	}
}
