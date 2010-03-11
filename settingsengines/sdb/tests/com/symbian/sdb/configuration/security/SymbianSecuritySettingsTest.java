// Copyright (c) 2007-2009 Nokia Corporation and/or its subsidiary(-ies).
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

package com.symbian.sdb.configuration.security;

import java.io.File;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

import org.jmock.cglib.MockObjectTestCase;

import com.symbian.sdb.configuration.policy.PolicySet;
import com.symbian.sdb.exception.ValidationException;

public class SymbianSecuritySettingsTest extends MockObjectTestCase {

	private SecuritySettings fSymSec;
	private Connection fDbConn = null;
	
	public void setUp() throws Exception{
		fSymSec = new SecuritySettings();
		
		System.setProperty("org.sqlite.lib.path", "lib\\");
		Class.forName("org.sqlite.JDBC");
		
		// This section will check whether a tempdir has been specified and if so it
		// will put the temp db in that location. 
		//
		String testDBLocation = "";
		String lTempdir = System.getProperty("tempdir");
		
		if(lTempdir!=null && lTempdir.length()>0){
			testDBLocation = lTempdir+"\\";
		}
		testDBLocation += "test.db";
		fDbConn = DriverManager.getConnection("jdbc:sqlite:"+testDBLocation);
	}

	/**
	 * Tests construction
	 *
	 */
	public void testConstructor(){
		
		assertNotNull(fSymSec.fPolicies);
	}
	
	/**
	 * Test policy validation
	 *
	 */
	public void testValidate(){
		//assertTrue(fSymSec.validate());
	}
	
	/**
	 * Tests a policy is correctly added
	 *
	 */
	public void testAddPolicy(){
		
		try{
			fSymSec.addPolicy(new PolicySet("Default"));
			assertTrue(fSymSec.fPolicies.size()==1);
		}
		catch(ValidationException ex){
			fail("Unexpected Exception: "+ex.getMessage());
		}
	}	
	
	/**
	 * Tests the list of policies returned is correct
	 *
	 */
	public void testGetPolicies(){
		
		try{
			fSymSec.addPolicy(new PolicySet("Default"));
			assertNotNull(fSymSec.getPolicies());
		}
		catch(ValidationException ex){
			fail("Unexpected Exception: "+ex.getMessage());
		}
	}
	
	/**
	 * Test get sql
	 */
	public void testGetSecuritySchemaSQL(){			
		
		try {
			assertNotNull(SecuritySettings.getSymbianSecuritySchema(fDbConn));
		} 
		catch (SQLException ex) {
			fail("Unexpected exception: "+ex.getMessage());
		}
	}
	
	public void tearDown(){
		new File("test.db").delete();
	}
	
	
}
