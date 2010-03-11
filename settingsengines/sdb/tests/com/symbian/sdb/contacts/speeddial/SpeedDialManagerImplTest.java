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

import org.jmock.Expectations;
import org.jmock.Mockery;
import org.junit.Before;
import org.junit.Test;

import com.symbian.sdb.contacts.speeddial.model.SpeedDialDataRepository;


/**
 * @author krzysztofZielinski
 *
 */
public class SpeedDialManagerImplTest {

    private Mockery context = new Mockery();

    private SpeedDialIniFileManager speedDialIniFileManager;
    
    private SpeedDialManagerImpl speedDialManager;
    
    @Before
    public void setUp() throws Exception {
    	speedDialManager = new SpeedDialManagerImpl();
    	
    	speedDialIniFileManager = context.mock(SpeedDialIniFileManager.class);
    	
    	speedDialManager.setSpeedDialIniFileManager(speedDialIniFileManager);
    }
    
	@Test
	public void testCreateNewSpeedDialIniFile() throws Exception {

        String phoneNumber1 = "078123456789";
		int contactId1 = 45;
        int speedDialNumber1 = 8;

        String phoneNumber2 = "078987654321";
		int contactId2 = 148;
        int speedDialNumber2 = 2;

        String databaseName = "test.db";
        final File speedDialIniFile = new File("speeddial.ini");
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
        
		
		context.checking(new Expectations() {{
            one (speedDialIniFileManager).createNewFile(with(equal(speedDialDataRepository)),with(equal(speedDialIniFile)));
        }});

		SpeedDialAssignmentData speedDialAssignmentData = new SpeedDialAssignmentData();
        speedDialAssignmentData.addEntry(new SpeedDialAssignmentEntry(phoneNumber1, speedDialNumber1, contactId1));
        speedDialAssignmentData.addEntry(new SpeedDialAssignmentEntry(phoneNumber2, speedDialNumber2, contactId2));
        
        speedDialManager.createSpeedDialIniFile(speedDialIniFile);
	}
}
