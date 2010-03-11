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

package com.symbian.sdb.configuration;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

import org.apache.log4j.Logger;

import com.symbian.sdb.configuration.policy.Policy;
import com.symbian.sdb.configuration.security.SecuritySettings;
import com.symbian.sdb.exception.SDBExecutionException;

/**
 *
 */
public class PlatsecConfigurator {
    private Connection connection;
	private static final Logger logger = Logger.getLogger(PlatsecConfigurator.class);

	public PlatsecConfigurator(Connection connection) {
	    this.connection = connection;
	}
	
	/**
	 * This applies the security settings to our database
	 * TODO: change DBManager to nice interface or create settings model and hand off to sqlgen
	 */
	public void applySecuritySettings(SecuritySettings securitySettings) throws SDBExecutionException{
		
		try {
			logger.info("Applying security settings...");
			
			//Remove any existing sec tables
			if (doesDbHaveSecuritySettings()){
				removeExistingSecurityTables();				
			}
	
			//Get Schema and execute
			PreparedStatement lSymbianSecuritySchema = SecuritySettings.getSymbianSecuritySchema(connection);
			try{
				lSymbianSecuritySchema.execute();
			} finally{
				lSymbianSecuritySchema.close();
			}
			
			//Get data and execute - symbian_security
			for(Policy lPol : securitySettings.getPolicies()){
				PreparedStatement lPolicyStatement = lPol.generateSql(connection); 
				try {
					lPolicyStatement.execute();
				} finally{
					lPolicyStatement.close();
				}
			}
		} catch (SQLException e) {
			throw new SDBExecutionException("Problem occured when applying platsec settings to DB", e);
		}
		
	}
	
   /* (non-Javadoc)
     * @see com.symbian.sdb.database.DatabaseManager#doesDbHaveSecuritySettings()
     */
    protected boolean doesDbHaveSecuritySettings() throws SQLException{
        PreparedStatement lTablesStatement 
        	= connection.prepareStatement("select name from sqlite_master where type='table' and name='symbian_security';");
        ResultSet lTables = null;
        boolean result = true;
        
        try {
            lTables = lTablesStatement.executeQuery();
            result = lTables.next();
        } finally {
            lTables.close();
            lTablesStatement.close();
        }               
        
        return result;
    }
    
    /* (non-Javadoc)
     * @see com.symbian.sdb.database.DatabaseManager#removeExistingSecurityTables()
     */
    protected void removeExistingSecurityTables() throws SQLException{
        logger.debug("Removing Symbian security tables from existing database");
        PreparedStatement lDropSec = connection.prepareStatement("DROP TABLE symbian_security;");
        try {
            lDropSec.execute();
        } finally {
            lDropSec.close();
        }
    }
}
