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

import org.jmock.Mock;
import org.jmock.cglib.MockObjectTestCase;
import org.jmock.core.Constraint;

import com.symbian.sdb.configuration.policy.type.AlwaysType;
import com.symbian.sdb.configuration.policy.type.PolicyType;
import com.symbian.sdb.constraints.PolicyAlwaysIs;
import com.symbian.sdb.constraints.PolicyTypeIs;
import com.symbian.sdb.exception.ValidationException;

public class PolicyAlwaysTest extends MockObjectTestCase {
	
	private PolicyAlways fPolicyAlways;
	private String fPolicyType = "Default";
	private String fAlwaysType = "Pass";	
	
	public void setUp() throws Exception{		
		
		fPolicyAlways = new PolicyAlways(fPolicyType, fAlwaysType);				
				
	}		
	
	/**
	 * This tests the constructor
	 *
	 */
	public void testConstructor(){
		
		try{
			fPolicyAlways = new PolicyAlways("Default", "Pass");
		}
		catch(ValidationException ex){
			fail("Unexpected Exception thrown: "+ex.getMessage());
		}
		
		try{
			fPolicyAlways = new PolicyAlways("Imwrong", "Pass");
			fail("Expected Exception was not thrown");
		}
		catch(ValidationException ex){
			//succeed
		}
		
		try{
			fPolicyAlways = new PolicyAlways("Default", "Imwrong");
			fail("Expected Exception was not thrown");
		}
		catch(ValidationException ex){
			//succeed
		}
		
	}

	/**
	 * Ensures we get the right policy Type
	 *
	 */
	public void testGetPolicyType(){
		assertEquals(PolicyType.DEFAULT, fPolicyAlways.getPolicyType());
	}
	
	
	public void testGetAlwaysPolicy(){
		assertEquals(AlwaysType.PASS, fPolicyAlways.getAlwaysType());		
	}
	
	public void testGenerateSql(){			
		
		Mock lMockDbConnection = mock(Connection.class);
		Mock lMockPreparedStatement = mock(PreparedStatement.class);
		
		//The Database Connection will generate our prepared statement
		lMockDbConnection.expects(once()).method("prepareStatement").will(returnValue((PreparedStatement)lMockPreparedStatement.proxy()));
		
		//Now the prepared statement calls...		
		lMockPreparedStatement.expects(once()).method("setInt").with(eq(1), ANYTHING).id("first");		
		lMockPreparedStatement.expects(once()).method("setInt").with(eq(2), policyTypeConstraint()).after("first").id("second");		
		lMockPreparedStatement.expects(once()).method("setBytes").with(eq(3), policyBlobConstraint()).after("second").id("third");
		
		try {
			fPolicyAlways.generateSql((Connection)lMockDbConnection.proxy());
		} 
		catch (SQLException ex) {
			fail("Unexpected Exception: "+ex.getMessage());
		}
		
	}
	
	public void testValidate(){
		
		try{
			fPolicyAlways.validate();
		}
		catch(ValidationException ex){
			fail("Unexpected Exception thrown: "+ex.getMessage());
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
		return new PolicyAlwaysIs(1, -1);
	}
}
