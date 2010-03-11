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

import java.io.File;

import com.symbian.sdb.mode.flow.SpeedDialModeType;



/**
 * @author krzysztofZielinski
 *
 */
public interface SpeedDialManager {

	/**
	 * Sets location of database generated speedDial.ini file refers to.
	 * @param dbLocation
	 */
	void setDeploymentDbLocation(String dbLocation);
	
	/**
	 * Adds entry to speedDial.ini file
	 * @param entry
	 */
	void addSpeeDialEntry(SpeedDialAssignmentEntry entry);
	
	/**
	 * Creates speedDial.ini file
	 * 
	 * @param speedDialAssignmentData
	 * @param databaseName
	 * @param speedDialIniFileName
	 */
	void createSpeedDialIniFile(File speedDialIniFileName);

	/**
	 * @param speedDialAssignmentData
	 * @param string
	 * @param iniFileName
	 */
	public void updateSpeedDialIniFile(File iniFile);

	/**
	 * @param mode the mode to set
	 */
	public void setMode(SpeedDialModeType mode);

	/**
	 * @return the mode
	 */
	public SpeedDialModeType getMode();
}
