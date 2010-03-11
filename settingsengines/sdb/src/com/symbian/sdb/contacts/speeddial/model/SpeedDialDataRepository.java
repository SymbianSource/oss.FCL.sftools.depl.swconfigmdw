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
// SpeedDialEntry.java
//



package com.symbian.sdb.contacts.speeddial.model;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Represents data stored in speed dial INI file
 * 
 * @author krzysztofZielinski
 *
 */
public class SpeedDialDataRepository {

	private List<DatabaseSpeedDialData> speedDialDataForDatabases = new ArrayList<DatabaseSpeedDialData>();
	
	public int getCount()	{
		return speedDialDataForDatabases.size();
	}

	/**
	 * Returns databaseSpeedDialData for given database name or new databaseSpeedDialData if there was no data for given database (adds this db data to current repository)
	 * 
	 * @param databaseName
	 * @return
	 */
	public DatabaseSpeedDialData getSpeedDialDataForDatabase(String databaseName)	{
		for (DatabaseSpeedDialData databaseSpeedDialData : speedDialDataForDatabases) {
			if (databaseSpeedDialData.getDatabaseName().equals(databaseName))	{
				return databaseSpeedDialData;
			}
		}
		return addNewDatabaseSpeedDialData(databaseName);
	}
	
	public void addDatabaseSpeedDialData(DatabaseSpeedDialData databaseSpeedDialData)	{
		this.speedDialDataForDatabases.add(databaseSpeedDialData);
	}
	
	public List<DatabaseSpeedDialData> getAllSpeedDialData()	{
		return Collections.unmodifiableList(this.speedDialDataForDatabases);
	}

	/**
	 * @param string
	 * @return 
	 */
	public DatabaseSpeedDialData addNewDatabaseSpeedDialData(String databaseName) {
		DatabaseSpeedDialData newDatabaseSpeedDialData = DatabaseSpeedDialData.newEmptySpeedDialData(databaseName);
		this.addDatabaseSpeedDialData(newDatabaseSpeedDialData);
		return newDatabaseSpeedDialData;
	}

	/* (non-Javadoc)
	 * @see java.lang.Object#hashCode()
	 */
	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime
				* result
				+ ((speedDialDataForDatabases == null) ? 0
						: speedDialDataForDatabases.hashCode());
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
		SpeedDialDataRepository other = (SpeedDialDataRepository) obj;
		if (speedDialDataForDatabases == null) {
			if (other.speedDialDataForDatabases != null)
				return false;
		} else if (!speedDialDataForDatabases
				.equals(other.speedDialDataForDatabases))
			return false;
		return true;
	}
}
