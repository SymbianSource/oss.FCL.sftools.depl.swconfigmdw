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
import java.util.List;

import junit.framework.Assert;

import org.junit.Before;
import org.junit.Test;

import com.symbian.sdb.PropertyRestorerTestCase;
import com.symbian.sdb.contacts.SystemException;
import com.symbian.sdb.contacts.speeddial.model.DatabaseSpeedDialData;
import com.symbian.sdb.contacts.speeddial.model.SpeedDialDataRepository;
import com.symbian.sdb.contacts.speeddial.model.SpeedDialEntry;
import com.symbian.sdb.util.FileUtil;

public class SpeedDialStoreManagerTest extends PropertyRestorerTestCase {
	private SpeedDialStoreManager storeManager = new SpeedDialStoreManager();
	
	@Before
	public void setUp() {
		setPropertiesForDBPaths();
		
	}
	
	@Test
	public void testReadCorruptedFile() throws Exception {
		File temp = File.createTempFile("cntmodelcorrtmp", "ini");
		FileUtil.copy("tests/config/speeddial/CntModelCorrupted.ini", temp.getAbsolutePath());
		try {
			storeManager.readFile(temp);
			Assert.fail("should have failed with SystemException");
		} catch (SystemException e) {
			Assert.assertTrue(e.getMessage().matches(".*Error when reading SpeedDial INI file:.*"));
		}
	}
	
	@Test
	public void testReadFile() throws Exception {
		File temp = File.createTempFile("cntmodeltmp", "ini");
		FileUtil.copy("tests/config/speeddial/CntModel.ini", temp.getAbsolutePath());
		SpeedDialDataRepository repository = storeManager.readFile(temp);
		List<DatabaseSpeedDialData> databaseData = repository.getAllSpeedDialData();
		for (DatabaseSpeedDialData data : databaseData) {
			SpeedDialEntry entry = data.getSpeedDialEntry(9);
			Assert.assertEquals("44", entry.getPhoneNumber());
		}
	}

	@Test
	public void testCreateNewFile() {
		
        String phoneNumber1 = "078123456789";
		int contactId1 = 45;
        int speedDialNumber1 = 8;

        String phoneNumber2 = "078987654321";
		int contactId2 = 148;
        int speedDialNumber2 = 2;
        
        String databaseName = "test.db";
        
        final SpeedDialDataRepository speedDialDataRepository = new SpeedDialDataRepository();
        
		speedDialDataRepository.addNewDatabaseSpeedDialData(databaseName) 
					.setSpeedDialEntry(speedDialNumber1, contactId1, phoneNumber1)
					.setSpeedDialEntry(speedDialNumber2, contactId2, phoneNumber2);
		
		storeManager.createNewFile(speedDialDataRepository, new File("cntmodeltest.ini"));
		
		File rep = new File("cntmodeltest.ini");
		
		Assert.assertTrue(rep.exists());
		
		SpeedDialDataRepository repository = storeManager.readFile(rep);
		List<DatabaseSpeedDialData> databaseData = repository.getAllSpeedDialData();
		for (DatabaseSpeedDialData data : databaseData) {
			SpeedDialEntry entry = data.getSpeedDialEntry(8);
			Assert.assertEquals("078123456789", entry.getPhoneNumber());
			Assert.assertEquals(45, entry.getContactId());
			
			entry = data.getSpeedDialEntry(2);
			Assert.assertEquals("078987654321", entry.getPhoneNumber());
			Assert.assertEquals(148, entry.getContactId());
		}
		
		
	}

	
}
