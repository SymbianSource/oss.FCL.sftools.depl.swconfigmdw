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
// DatatabaseSpeedDialData.java
//



package com.symbian.sdb.contacts.speeddial.model;

import java.util.ArrayList;
import java.util.List;

/**
 * Represents container for speed dial entries in speed dial INI file specific for single database
 * 
 * @author krzysztofZielinski
 *
 */
public class DatabaseSpeedDialData {

	private static int numberOfSpeedDialPerDatabase = 9;
	
	private String databaseName;
	private List<SpeedDialEntry> speedDialEntries = new ArrayList<SpeedDialEntry>();
	

	private DatabaseSpeedDialData(String databaseName) {
		super();
		this.databaseName = databaseName;
	}

	/**
	 * Returns empty speedDial container i.e. container with empty ("NULL" value) entries
	 * 
	 * @param databaseName
	 * @return
	 */
	public static DatabaseSpeedDialData newEmptySpeedDialData(String databaseName)	{
		DatabaseSpeedDialData emptyDatabaseSpeedDialData = new DatabaseSpeedDialData(databaseName);
		for (int i = 0; i < numberOfSpeedDialPerDatabase; i++) {
			emptyDatabaseSpeedDialData.speedDialEntries.add(SpeedDialEntry.getEmptyEntry());
		}
		return emptyDatabaseSpeedDialData;
	}
	
	/**
	 * Returns speed dial entry for given speed dial number
	 * 
	 * @param speedDial number from range 1-9
	 */
	public SpeedDialEntry getSpeedDialEntry(int speedDial)	{
		 return this.speedDialEntries.get(speedDial - 1);
	}
	
	/**
	 * Replaces speed dial entry on given for given speed dial number 
	 * 
	 * @param speedDial number from range 1-9
	 * @param newSpeedDialEntry 
	 */
	public void setSpeedDialEntry(int speedDial, SpeedDialEntry newSpeedDialEntry)	{
		 this.speedDialEntries.set(speedDial - 1, newSpeedDialEntry);
	}

	/**
	 * Replaces speed dial entry on given for given speed dial number 
	 * 
	 * @param speedDial number from range 1-9
	 * @param newSpeedDialEntry 
	 * @return 
	 */
	public DatabaseSpeedDialData setSpeedDialEntry(int speedDial, long contactId, String phoneNumber)	{
		SpeedDialEntry entry = new SpeedDialEntry(contactId, phoneNumber); 
		this.speedDialEntries.set(speedDial - 1, entry);
		return this;
	}

	public String getDatabaseName() {
		return databaseName;
	}

	public int size()	{
		return this.speedDialEntries.size();
	}
	
	/* (non-Javadoc)
	 * @see java.lang.Object#hashCode()
	 */
	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result
				+ ((databaseName == null) ? 0 : databaseName.hashCode());
		result = prime
				* result
				+ ((speedDialEntries == null) ? 0 : speedDialEntries.hashCode());
		return result;
	}

	/* (non-Javadoc)
	 * @see java.lang.Object#equals(java.lang.Object)
	 */
	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		DatabaseSpeedDialData other = (DatabaseSpeedDialData) obj;
		if (databaseName == null) {
			if (other.databaseName != null)
				return false;
		} else if (!databaseName.equals(other.databaseName))
			return false;
		if (speedDialEntries == null) {
			if (other.speedDialEntries != null)
				return false;
		} else if (!speedDialEntries.equals(other.speedDialEntries))
			return false;
		return true;
	}
}
