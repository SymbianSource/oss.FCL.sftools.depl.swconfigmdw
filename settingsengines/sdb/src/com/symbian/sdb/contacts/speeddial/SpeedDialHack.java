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
 * Temporary hack class to provide speed dial functionality (only one phone number added in execution)
 * 
 * @author krzysztofZielinski
 *
 */
public class SpeedDialHack {

	private static String phoneNumber = "";
	private static long contactId = -1;
	private static int speedDialIndex = -1;
	private static String deplymentDbLocation = "";
	
	public static int getSpeedDialIndex() {
		return speedDialIndex;
	}

	public static void setSpeedDialIndex(int speedDialNumber) {
		SpeedDialHack.speedDialIndex = speedDialNumber;
	}
	/**
	 * @return the phoneNumber
	 */
	public static String getPhoneNumber() {
		return phoneNumber;
	}
	/**
	 * @param phoneNumber the phoneNumber to set
	 */
	public static void setPhoneNumber(String phoneNumber) {
		SpeedDialHack.phoneNumber = phoneNumber;
	}
	/**
	 * @return the contactId
	 */
	public static long getContactId() {
		return contactId;
	}
	/**
	 * @param contactId the contactId to set
	 */
	public static void setContactId(long contactId) {
		SpeedDialHack.contactId = contactId;
	}

	/**
	 * @return the deplymentDbLocation
	 */
	public static String getDeplymentDbLocation() {
		return deplymentDbLocation;
	}

	/**
	 * @param deplymentDbLocation the deplymentDbLocation to set
	 */
	public static void setDeplymentDbLocation(String deplymentDbLocation) {
		SpeedDialHack.deplymentDbLocation = deplymentDbLocation;
	}
}
