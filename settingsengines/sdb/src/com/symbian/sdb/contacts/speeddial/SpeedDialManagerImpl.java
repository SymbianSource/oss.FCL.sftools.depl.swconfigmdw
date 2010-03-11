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

import com.symbian.sdb.contacts.speeddial.model.DatabaseSpeedDialData;
import com.symbian.sdb.contacts.speeddial.model.SpeedDialDataRepository;
import com.symbian.sdb.mode.flow.SpeedDialModeType;

/**
 * @author krzysztofZielinski
 *
 */
public class SpeedDialManagerImpl implements SpeedDialManager {

	private SpeedDialModeType mode = SpeedDialModeType.NONE;
	private SpeedDialIniFileManager speedDialIniFileManager; 
	private SpeedDialAssignmentData speedDialAssignmentData = new SpeedDialAssignmentData();
	private String deploymentDbLocation = "";
	
	public void createSpeedDialIniFile(File speedDialIniFile) {
		SpeedDialDataRepository speedDialDataRepository = new SpeedDialDataRepository();

		DatabaseSpeedDialData databaseSpeedDialData = DatabaseSpeedDialData.newEmptySpeedDialData(deploymentDbLocation);
		
		for (SpeedDialAssignmentEntry speedAssignmentEntry : speedDialAssignmentData.getAllEntries()) {
			int speedDialNumber = speedAssignmentEntry.getSpeedDialNumber();
			String phoneNumber = speedAssignmentEntry.getPhoneNumber();
			long contactId = speedAssignmentEntry.getContactId();			
						
			databaseSpeedDialData.setSpeedDialEntry(speedDialNumber, contactId, phoneNumber);
		}
		
		speedDialDataRepository.addDatabaseSpeedDialData(databaseSpeedDialData);
		
		writeToIniFile(speedDialDataRepository, speedDialIniFile);
	}

	void writeToIniFile(SpeedDialDataRepository speedDialDataRepository, File speedDialIniFile) {
		speedDialIniFileManager.createNewFile(speedDialDataRepository, speedDialIniFile);
	}

	// Getters/Setters for injection
	
	public void setSpeedDialIniFileManager(SpeedDialIniFileManager speedDialIniFileManager) {
		this.speedDialIniFileManager = speedDialIniFileManager;
	}

	/**
	 * @param speedDialAssignmentData
	 * @param string
	 * @param iniFileName
	 */
	public void updateSpeedDialIniFile(File iniFile) {
		SpeedDialDataRepository speedDialDataRepository = readIniFile(iniFile);
		DatabaseSpeedDialData databaseSpeedDialData = speedDialDataRepository.getSpeedDialDataForDatabase(deploymentDbLocation);
		
		for (SpeedDialAssignmentEntry speedAssignmentEntry : speedDialAssignmentData.getAllEntries()) {
			int speedDialNumber = speedAssignmentEntry.getSpeedDialNumber();
			String phoneNumber = speedAssignmentEntry.getPhoneNumber();
			long contactId = speedAssignmentEntry.getContactId();			
						
			databaseSpeedDialData.setSpeedDialEntry(speedDialNumber, contactId, phoneNumber);
		}
		
		writeToIniFile(speedDialDataRepository, iniFile);
	}

	/**
	 * @param speedDialIniFileName
	 * @return
	 */
	SpeedDialDataRepository readIniFile(File speedDialIniFile) {
		return speedDialIniFileManager.readFile(speedDialIniFile);
	}

	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.speeddial.SpeedDialManager#addSpeeDialEntry(java.lang.String, int)
	 */
	public void addSpeeDialEntry(SpeedDialAssignmentEntry entry) {
		speedDialAssignmentData.addEntry(entry);
	}

	/* (non-Javadoc)
	 * @see com.symbian.sdb.contacts.speeddial.SpeedDialManager#setDeplymentDbLocation(java.lang.String)
	 */
	public void setDeploymentDbLocation(String dbLocation) {
		this.deploymentDbLocation = dbLocation;
	}

	/**
	 * @param mode the mode to set
	 */
	public void setMode(SpeedDialModeType mode) {
		this.mode = mode;
	}

	/**
	 * @return the mode
	 */
	public SpeedDialModeType getMode() {
		return mode;
	}
}
