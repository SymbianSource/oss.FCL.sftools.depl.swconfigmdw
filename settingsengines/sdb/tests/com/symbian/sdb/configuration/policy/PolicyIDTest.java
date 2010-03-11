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

import com.symbian.sdb.configuration.policy.type.IDType;
import com.symbian.sdb.constraints.PolicyIdBlobIs;
import com.symbian.sdb.constraints.PolicyTypeIs;
import com.symbian.sdb.exception.ValidationException;

public class PolicyIDTest extends MockObjectTestCase {
	
	private PolicyID fPolicyID;
	private String fPolicyType = "Default";
	private String fIdType = "SID";
	private String fId = "4D2";
	
	public void setUp() throws Exception{		
		fPolicyID = new PolicyID(fPolicyType, fId, fIdType);
		
		System.setProperty("org.sqlite.lib.path", "lib\\");
		Class.forName("org.sqlite.JDBC");
	}
		
	/**
	 * This tests the object construction
	 *
	 */
	public void testConstructor(){
		
		try{
			fPolicyID = new PolicyID(fPolicyType, fId, fIdType);
		}
		catch(ValidationException ex){
			fail("Unexpected Exception thrown: "+ex.getMessage());
		}
		
		try{
			fPolicyID = new PolicyID(fPolicyType, "IMwrong", fId);
			fail("Expected Exception not thrown");
		}
		catch(ValidationException ex){
			
		}		
	}
	
	/**
	 * This checks the correct IDType is returned
	 *
	 */
	public void testGetIDType(){
		assertEquals(fPolicyID.getIDType(), IDType.SID);
	}
	
	/**
	 * This checks the correct ID is returned
	 *	 
	 */
	public void testGetID(){
		assertEquals(Integer.toString(Integer.parseInt(fId, 16)), fPolicyID.getID());
	}
	
	/**
	 * Tests generation of SQL
	 *
	 */
	public void testGenerateSql(){
		
		try{
			fPolicyID.addCapability("ALLFILES");
			fPolicyID.addCapability("COMMDD");
			fPolicyID.addCapability("DISKADMIN");
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
		
		try {
			fPolicyID.generateSql((Connection)lMockDbConnection.proxy());
		} 
		catch (SQLException ex) {
			fail("Unexpected Exception: "+ex.getMessage());
		}
	}
	
	/**
	 * Tests validation
	 */
	public void testValidate(){
		try{
			fPolicyID.validate();			
		}
		catch(ValidationException ex){
			fail("Unexpected Exception: "+ex.getMessage());
		}
		
		//Now we try bad PolicyID's
		//1. = Bad ID defined
		try {
			PolicyID fBad1 = new PolicyID(fPolicyType, "Triple Crown - easy.", "SID");
			fBad1.validate();
			fail("Expected Exception not thrown");
		} 
		catch (ValidationException ex) {
		}
		
		//2. Too many capabilities defined
		try {
			fPolicyID.addCapability("COMMDD");
			fPolicyID.addCapability("DRM");
			fPolicyID.addCapability("TCB");
			fPolicyID.addCapability("ALLFILES");
			fPolicyID.validate();
			fail("Expected Exception not thrown");
		} 
		catch (ValidationException ex) {			
		}
	}
	
	public void tearDown(){
		new File("test.db").delete();
	}
	
	/**
	 * Gets our Constraint for the policyType
	 * @return
	 */
	private Constraint policyTypeConstraint(){
		return new PolicyTypeIs();
	}
	
	/**
	 * Gets our Constraint for the policyBlob
	 * @return
	 */
	private Constraint policyBlobConstraint(){
		
		ArrayList<Byte> lCapabilitiesList = new ArrayList<Byte>();
		lCapabilitiesList.add(new Integer(9).byteValue()); // DiskAdmin
		lCapabilitiesList.add(new Integer(11).byteValue());//Allfiles 
		lCapabilitiesList.add(new Integer(1).byteValue());//CommDD
		lCapabilitiesList.add(new Integer(-1).byteValue());

		
		return new PolicyIdBlobIs(lCapabilitiesList, 1234, IDType.SID);
	}
}
