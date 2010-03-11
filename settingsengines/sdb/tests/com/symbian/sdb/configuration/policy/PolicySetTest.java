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

package com.symbian.sdb.configuration.policy;

import java.io.File;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.ArrayList;

import org.jmock.Mock;
import org.jmock.cglib.MockObjectTestCase;
import org.jmock.core.Constraint;

import com.symbian.sdb.configuration.policy.type.PolicyType;
import com.symbian.sdb.constraints.PolicySetBlobIs;
import com.symbian.sdb.constraints.PolicyTypeIs;
import com.symbian.sdb.exception.ValidationException;

public class PolicySetTest extends MockObjectTestCase {

	private PolicySet fPolicySet;
	private String fPolicyType = "Default";
	private String TMP_DB_NAME = "";
	
	public void setUp() throws Exception{
		
		fPolicySet = new PolicySet(fPolicyType);				
		System.setProperty("org.sqlite.lib.path", "lib\\");
		
		// This section will check whether a tempdir has been specified and if so it
		// will put the temp db in that location. 
		//
		String lTempdir = System.getProperty("test.temp.dir");
		
		if(lTempdir!=null){
			TMP_DB_NAME = lTempdir;
		}
		TMP_DB_NAME += "test.db";
				
	}
	
	/**
	 * Tests the policy type is correctly set
	 *
	 */
	public void testSetPolicyType(){
		
		try{
			fPolicySet.setPolicyType("Read");
			assertTrue(fPolicySet.fPolicyType.equals(PolicyType.READ));
		}
		catch(ValidationException ex){
			fail("Unexpected ValidationException: "+ex.getMessage());
		}
		
		try{
			fPolicySet.setPolicyType("IamWrong");
			fail("Expected Exception was not thrown");
		}
		catch(ValidationException ex){
			
		}
	}

	
	/**
	 * Tests object construction
	 *
	 */
	public void testConstructor(){
		try{
			fPolicySet = new PolicySet(fPolicyType);
		}
		catch(ValidationException ex){
			fail("Unexpected Exception: "+ex.getMessage());
		}
		
		try{
			fPolicySet = new PolicySet("ihs");
			fail("Expected Exception was not thrown");
		}
		catch(ValidationException ex){
			
		}
	}

	/**
	 * Tests capabilities are succesfully added
	 *
	 */
	public void testAddCapability(){
		
		try{
			fPolicySet.addCapability("CommDD");
			assertTrue(fPolicySet.getCapabilities().size()==1);
		}
		catch(ValidationException ex){
			fail("Unexpected Exception thrown: "+ex.getMessage());
		}
		
		try{
			fPolicySet.addCapability("ImWrong");
			fail("Expected Exception was not thrown");
		}
		catch(ValidationException ex){
			
		}		
		
	}

	/**
	 * Tests capabilities are succesfully cleared
	 *
	 */
	public void testClearCapabilities(){
		
		try{
			fPolicySet.addCapability("CommDD");
		}
		catch(ValidationException ex){
			fail("Unexpected Exception: "+ex.getMessage());
		}
		
		fPolicySet.clearCapabilities();
		assertTrue(fPolicySet.getCapabilities().size()==0);
	}
	
	/**
	 * Tests the generated SQL
	 *
	 */
	public void testGenerateSql(){	
		
		try{
			fPolicySet.setPolicyType("DEFAULT");
			fPolicySet.addCapability("ALLFILES");
			fPolicySet.addCapability("COMMDD");
			fPolicySet.addCapability("DISKADMIN");
			fPolicySet.addCapability("DRM");
		}
		catch(ValidationException ex){
			fail("Unexpected Exception: "+ex.getMessage());
		}
		
		Mock lMockDbConnection = mock(Connection.class);
		Mock lMockPreparedStatement = mock(PreparedStatement.class);			
		
		//The Database Connection will generate our prepared statement
		lMockDbConnection.expects(once()).method("prepareStatement").will(returnValue((PreparedStatement)lMockPreparedStatement.proxy()));
		
		//Now the prepared statement calls...		
		lMockPreparedStatement.expects(once()).method("setInt").with(eq(1), ANYTHING).id("first");		
		lMockPreparedStatement.expects(once()).method("setInt").with(eq(2), policyTypeConstraint()).after("first").id("second");		
		lMockPreparedStatement.expects(once()).method("setBytes").with(eq(3), policyBlobConstraint()).after("second").id("third");		
		
		try{
			fPolicySet.generateSql((Connection)lMockDbConnection.proxy());			
		}
		catch(SQLException ex){
			
		}
	}	
	
	/**
	 * Tests the validation methods
	 *
	 */
	public void testValidate(){		
		
		try {
			fPolicySet.validate();
		} catch (ValidationException ex) {
			fail("Unexpected Exception: "+ex.getMessage());
		}
	}

	public void testGetPolicy(){
		assertEquals(PolicyType.DEFAULT, fPolicySet.getPolicyType());
	}
	
	public void tearDown(){
		new File(TMP_DB_NAME).delete();
	}
	
	/**
	 * Gets our Constraint for the policyBlob
	 * @return
	 */
	private Constraint policyBlobConstraint(){		
		
    	ArrayList<Byte> lCapabilitiesList = new ArrayList<Byte>();
    	lCapabilitiesList.add(new Integer(9).byteValue()); // DiskAdmin
    	lCapabilitiesList.add(new Integer(11).byteValue());//Allfiles
    	lCapabilitiesList.add(new Integer(6).byteValue());//DRM
    	lCapabilitiesList.add(new Integer(1).byteValue());//CommDD
    	lCapabilitiesList.add(new Integer(-1).byteValue());
    	
		return new PolicySetBlobIs(lCapabilitiesList, 3);
	}
	
	/**
	 * Gets our Constraint for the policyType
	 * @return
	 */
	private Constraint policyTypeConstraint(){		
		return new PolicyTypeIs();
	}


	
	
}
