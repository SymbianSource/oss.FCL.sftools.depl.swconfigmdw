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
//
package com.symbian.sdb.contacts.speeddial;


import java.io.File;
import java.util.List;

import junit.framework.Assert;

import org.junit.Before;
import org.junit.Test;

import com.symbian.sdb.PropertyRestorerTestCase;
import com.symbian.sdb.contacts.speeddial.model.DatabaseSpeedDialData;
import com.symbian.sdb.contacts.speeddial.model.SpeedDialDataRepository;
import com.symbian.sdb.contacts.speeddial.model.SpeedDialEntry;
import com.symbian.sdb.util.FileUtil;

public class SpeedDialManagerImplIntegrationTest extends PropertyRestorerTestCase {

	private SpeedDialManagerImpl speedDialManager;
	private String iniFile = "tests/config/speeddial/CntModel.ini";
	
	@Before
	public void onSetUp() throws Exception {
		speedDialManager = new SpeedDialManagerImpl();
		setPropertiesForDBPaths();
	}

	@Test
	public void testUpdateSpeedDialIniFileWithNewDB() throws Exception {
		
        String phoneNumber1 = "078123456789";
		int contactId1 = 45;
        int speedDialNumber1 = 9;

        String phoneNumber2 = "078987654321";
		int contactId2 = 148;
        int speedDialNumber2 = 2;

        String databaseName = "c:yrd.cdb";

        final File speedDialIniFile = File.createTempFile("cntmodeltmp", "ini");
        
        FileUtil.copy(iniFile, speedDialIniFile.getAbsolutePath());

        
        speedDialManager.setDeploymentDbLocation(databaseName);
        
        // entry 1
		SpeedDialAssignmentEntry speedDialEntry1 = new SpeedDialAssignmentEntry(phoneNumber1, speedDialNumber1, contactId1);
		speedDialManager.addSpeeDialEntry(speedDialEntry1);
		
        // entry 2
		SpeedDialAssignmentEntry speedDialEntry2 = new SpeedDialAssignmentEntry(phoneNumber2, speedDialNumber2, contactId2);
		speedDialManager.addSpeeDialEntry(speedDialEntry2);

        final SpeedDialDataRepository speedDialDataRepository = new SpeedDialDataRepository();
        
		speedDialDataRepository.addNewDatabaseSpeedDialData(databaseName) 
					.setSpeedDialEntry(speedDialNumber1, contactId1, phoneNumber1)
					.setSpeedDialEntry(speedDialNumber2, contactId2, phoneNumber2);
        
		SpeedDialStoreManager speedDialIniFileManager = new SpeedDialStoreManager();
		speedDialManager.setSpeedDialIniFileManager(speedDialIniFileManager);

		SpeedDialAssignmentData speedDialAssignmentData = new SpeedDialAssignmentData();
        speedDialAssignmentData.addEntry(new SpeedDialAssignmentEntry(phoneNumber1, speedDialNumber1, contactId1));
        speedDialAssignmentData.addEntry(new SpeedDialAssignmentEntry(phoneNumber2, speedDialNumber2, contactId2));
        
        
		SpeedDialDataRepository repository = speedDialIniFileManager.readFile(speedDialIniFile);
		List<DatabaseSpeedDialData> databaseData = repository.getAllSpeedDialData();
		for (DatabaseSpeedDialData data : databaseData) {
			SpeedDialEntry entry = data.getSpeedDialEntry(9);
			Assert.assertEquals("44", entry.getPhoneNumber());
		}
        
        speedDialManager.updateSpeedDialIniFile(speedDialIniFile);
        
		repository = speedDialIniFileManager.readFile(speedDialIniFile);
		databaseData = repository.getAllSpeedDialData();
		for (DatabaseSpeedDialData data : databaseData) {
			if (data.getDatabaseName().equals("c:yrd.cdb")) {
				SpeedDialEntry entry = data.getSpeedDialEntry(9);
				Assert.assertEquals("078123456789", entry.getPhoneNumber());
			} else if (data.getDatabaseName().equals("c:contacts.cdb")) {
				SpeedDialEntry entry = data.getSpeedDialEntry(9);
				Assert.assertEquals("44", entry.getPhoneNumber());
			}			
		}

	}
	
	@Test
	public void testUpdateSpeedDialIniFile() throws Exception {
		
        String phoneNumber1 = "078123456789";
		int contactId1 = 45;
        int speedDialNumber1 = 9;

        String phoneNumber2 = "078987654321";
		int contactId2 = 148;
        int speedDialNumber2 = 2;

        String databaseName = "c:contacts.cdb";
        
        final File speedDialIniFile = File.createTempFile("cntmodeltmp", "ini");
     
        FileUtil.copy(iniFile, speedDialIniFile.getAbsolutePath());

        
        speedDialManager.setDeploymentDbLocation(databaseName);
        
        // entry 1
		SpeedDialAssignmentEntry speedDialEntry1 = new SpeedDialAssignmentEntry(phoneNumber1, speedDialNumber1, contactId1);
		speedDialManager.addSpeeDialEntry(speedDialEntry1);
		
        // entry 2
		SpeedDialAssignmentEntry speedDialEntry2 = new SpeedDialAssignmentEntry(phoneNumber2, speedDialNumber2, contactId2);
		speedDialManager.addSpeeDialEntry(speedDialEntry2);

        final SpeedDialDataRepository speedDialDataRepository = new SpeedDialDataRepository();
        
		speedDialDataRepository.addNewDatabaseSpeedDialData(databaseName) 
					.setSpeedDialEntry(speedDialNumber1, contactId1, phoneNumber1)
					.setSpeedDialEntry(speedDialNumber2, contactId2, phoneNumber2);
        
		SpeedDialStoreManager speedDialIniFileManager = new SpeedDialStoreManager();
		speedDialManager.setSpeedDialIniFileManager(speedDialIniFileManager);

		SpeedDialAssignmentData speedDialAssignmentData = new SpeedDialAssignmentData();
        speedDialAssignmentData.addEntry(new SpeedDialAssignmentEntry(phoneNumber1, speedDialNumber1, contactId1));
        speedDialAssignmentData.addEntry(new SpeedDialAssignmentEntry(phoneNumber2, speedDialNumber2, contactId2));
        
        
		SpeedDialDataRepository repository = speedDialIniFileManager.readFile(speedDialIniFile);
		List<DatabaseSpeedDialData> databaseData = repository.getAllSpeedDialData();
		for (DatabaseSpeedDialData data : databaseData) {
			SpeedDialEntry entry = data.getSpeedDialEntry(9);
			Assert.assertEquals("44", entry.getPhoneNumber());
		}
        
        speedDialManager.updateSpeedDialIniFile(speedDialIniFile);
        
		repository = speedDialIniFileManager.readFile(speedDialIniFile);
		databaseData = repository.getAllSpeedDialData();
		for (DatabaseSpeedDialData data : databaseData) {
			SpeedDialEntry entry = data.getSpeedDialEntry(9);
			Assert.assertEquals("078123456789", entry.getPhoneNumber());
			Assert.assertEquals(45, entry.getContactId());
			
			entry = data.getSpeedDialEntry(2);
			Assert.assertEquals("078987654321", entry.getPhoneNumber());
		}

	}
	
}
