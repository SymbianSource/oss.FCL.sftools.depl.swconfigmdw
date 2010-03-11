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
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

import org.apache.log4j.Logger;

import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.mode.DBMode;

public class SystemSettings {
    private Connection connection;
    private static final Logger logger = Logger.getLogger(SystemSettings.class);
    private DBMode mode;
    
    public SystemSettings(Connection connection, DBMode mode) {
        this.connection = connection;
        this.mode = mode;
    }
    
    public boolean hasSettingsTable() throws SDBExecutionException {
    	boolean result = false;
    	Statement statement = null;
        ResultSet resultSet = null;
        try {  
            statement = connection.createStatement();
            resultSet = statement.executeQuery("select name from sqlite_master where type='table' and name='symbian_settings'");   
            result = resultSet.next();
        } catch (SQLException e) {
            throw new SDBExecutionException("Querying system settings failed: " + e.getMessage(), e);
        } finally {
        	closeStatement(statement);
        	closeResultSet(resultSet);
        }
        return result;
    }

    public void applySystemSettings() throws SDBExecutionException {
        Statement statement = null;
        try {
            statement = connection.createStatement();
            statement.execute("CREATE TABLE symbian_settings(Id INTEGER, Reserved INTEGER, CollationDllName TEXT)");
            statement.execute("INSERT INTO symbian_settings VALUES(3, 0, \""+mode.getCollationDllName()+"\")");
        } catch (SQLException e) {
            throw new SDBExecutionException("Creating system settings failed: " + e.getMessage(), e);
        } finally {
        	closeStatement(statement);
        }
    }

    private void closeStatement(Statement statement) {
        try {
            if (statement != null) {
                statement.close();
            }
        } catch (SQLException e) {
            logger.warn("error closing statement");
        }
    }
    
    private void closeResultSet(ResultSet resultSet) {
        try {
            if (resultSet != null) {
            	resultSet.close();
            }
        } catch (SQLException e) {
            logger.warn("error closing result set");
        }
    }
    
     
}


