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

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

import com.symbian.sdb.configuration.policy.Policy;
import com.symbian.sdb.configuration.policy.type.PolicyType;
import com.symbian.sdb.exception.ValidationException;

public class SecuritySettings {

	protected List<Policy> fPolicies;
	
	/**
	 * Constructor
	 *
	 */
	public SecuritySettings(){
		fPolicies = new ArrayList<Policy>(4);
	}
	
	/**
	 * This method validates that the policies are ok
	 * @return
	 */
	public void validate() throws ValidationException{
		
		//Must ensure that we have a default policy
		for(Policy lPol : fPolicies){			
			if(lPol.getPolicyType().equals(PolicyType.DEFAULT)){
				return;
			}						
		}		
		if (fPolicies.size() > 0) {
		    throw new ValidationException("One Policy of type Default is required. ");
		}
	}
	
	/**
	 * Adds a policy to the list
	 * @param aPol
	 */
	public void addPolicy(Policy aPol) throws ValidationException{		
				
		if(!isPolicyTypeUnique(aPol)){
			throw new ValidationException("Cannot have more than one policy of a given type. ");
		}
		fPolicies.add(aPol);
	}
	

	public boolean isPolicyTypeUnique(Policy aPol){
		
		for(Policy lPol : fPolicies){
			if(lPol.getPolicyType().equals(aPol.getPolicyType())){
				return false;
			}
		}
		
		return true;
	}
	

	
	/**
	 * Returns the List of policies in this object
	 * @return
	 */
	public List<Policy> getPolicies(){
		return fPolicies;
	}
	
	/**
	 * Returns the schema for the symbian_security table
	 * @param aDbConn
	 * @return
	 * @throws SQLException
	 */
	public static PreparedStatement getSymbianSecuritySchema(Connection aDbConn) throws SQLException{
		
		return aDbConn.prepareStatement("CREATE TABLE symbian_security"
				+"("
				+"Id INTEGER PRIMARY KEY AUTOINCREMENT,"
				+"ObjectType INTEGER,"
				+"ObjectName VARCHAR(255),"
				+"PolicyType INTEGER,"
				+"PolicyData BLOB"
				+");");
	}

}
