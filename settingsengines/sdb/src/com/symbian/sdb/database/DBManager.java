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
// DatabaseManager.java
//



package com.symbian.sdb.database;

import java.io.File;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

import org.apache.log4j.Logger;

import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.mode.DBType;

public class DBManager implements IDatabaseManager, IConnectionProvider {	

		/** Database Connection */
		protected Connection dbConn = null;
		
		/** Static logger */
		private static final Logger sLogger = Logger.getLogger(DBManager.class);
		
	    public boolean isConnectionOpen() {
	    	try {
	    		if (dbConn != null) {
	    			return !dbConn.isClosed();
	    		} else {
	    			return false;
	    		}
	    	} catch (SQLException e) {
	    		return false;
	    	}
	    }
	    
	    /* (non-Javadoc)
		 * @see com.symbian.sdb.database.DatabaseManager#setDbConnection(java.sql.Connection)
		 */
	    public void setConnection(Connection aConnection){
	    	dbConn = aConnection;
	    }
	    
	    /* (non-Javadoc)
		 * @see com.symbian.sdb.database.DatabaseManager#getDbConnection()
		 */
	    public Connection getConnection(){
	    	return dbConn;
	    }

	    public void openConnection(DBType dbType, String filename, String conParameters) throws SDBExecutionException {
            
            //This compensates for the fact that the JDBC driver cant handle relative
            //paths to directories that dont exist
            File aDbFile = new File(filename);
            if(aDbFile.getParentFile() != null){
                aDbFile.getParentFile().mkdirs();
            }
            
            try {       
                dbType.loadClass();
                String connectionString = dbType.getConnectionName() + filename;
                if (conParameters != null) {
                    connectionString += "?" + conParameters;
                }
                setConnection(DriverManager.getConnection(connectionString));
                sLogger.debug("Opening DB Connection to "+filename);
            } catch(ClassNotFoundException ex){         
                sLogger.debug("Stack Trace: ", ex); 
                throw new SDBExecutionException("Unable to open Database: "+ex.getMessage(), ex);
            } catch(SQLException ex){           
                sLogger.debug("Stack Trace: ", ex);
                throw new SDBExecutionException("Unable to open Database: "+ex.getMessage(), ex);
            } 
        }
	    
	    /* (non-Javadoc)
		 * @see com.symbian.sdb.database.DatabaseManager#openDatabase(java.lang.String)
		 */
	    public void openConnection(DBType dbType, String filename) throws SDBExecutionException {
	        this.openConnection(dbType, filename, null);
	    }
	    
	    /* (non-Javadoc)
		 * @see com.symbian.sdb.database.DatabaseManager#closeDatabase()
		 */
	    public void closeConnection() {
	    	
	    	try{
	    		if((dbConn != null)&& (!dbConn.isClosed())){
	    			dbConn.close();
	    			sLogger.debug("Closing database connection");
	    		}
	    	} catch(SQLException ex){
	    		sLogger.warn("Failed to close database: "+ex.getMessage());
	    		sLogger.debug("Stack Trace: ", ex);	    		
	    	}
	    }
}