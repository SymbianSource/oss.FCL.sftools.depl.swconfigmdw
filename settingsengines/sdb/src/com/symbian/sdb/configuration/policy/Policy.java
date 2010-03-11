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

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;

import org.apache.log4j.Logger;

import com.symbian.sdb.configuration.policy.type.PolicyType;
import com.symbian.sdb.exception.ValidationException;

public abstract class Policy {	
	
	protected static final String INSERT_STATEMENT = "INSERT INTO symbian_security (ObjectType, PolicyType, PolicyData)" +
		" VALUES(?, ?, ?)";	
	protected static final byte NO_POLICY = -1;
	
	/** Static logger */
	protected static final Logger sLogger = Logger.getLogger(Policy.class);	

	/**
	 * This method generates SQL to insert the security data
	 * @return
	 */
	public PreparedStatement generateSql(Connection aDbConn) throws SQLException{
		
		PreparedStatement lStmt = aDbConn.prepareStatement(INSERT_STATEMENT);
		sLogger.debug(INSERT_STATEMENT);
		
		//First parameter is the ObjectType
		lStmt.setInt(1, getPolicyType().getObjectTypeID());
		sLogger.debug("Param 1 = "+getPolicyType().getObjectTypeID());
		
		//Second parameter is the PolicyType 
		lStmt.setInt(2, getPolicyType().getPolicyTypeID());
		sLogger.debug("Param 2 = "+getPolicyType().getPolicyTypeID());
		
		//Third Parameter is the BLOB
		byte[] lBlobData = getBlobData();
		lStmt.setBytes(3, lBlobData);
		
		sLogger.debug("Param 3 (BLOB) = "+lBlobData[0]+" "+lBlobData[1]+" "+lBlobData[2]+" "+lBlobData[3]+" "
				+lBlobData[4]+" "+lBlobData[5]+" "+lBlobData[6]+" "+lBlobData[7]);
		
		return lStmt;
			
	}	
	
	public abstract void validate() throws ValidationException;
	public abstract PolicyType getPolicyType();
	public abstract byte[] getBlobData();
}
