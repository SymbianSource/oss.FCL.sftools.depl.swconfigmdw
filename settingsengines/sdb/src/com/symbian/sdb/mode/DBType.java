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

package com.symbian.sdb.mode;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.InputStream;

import com.symbian.sdb.exception.SDBExecutionException;


public enum DBType {
	SQLITE("org.sqlite.JDBC", "jdbc:sqlite:"),
	DBMS("com.symbian.dbms.jdbc.DbmsDriver", "jdbc:dbms:/"),
	CED;
	
	private DBType(String className, String connectionName) {
        this.className = className;
        this.connectionName = connectionName;
    }
	
    private DBType() {}
    
	private String className, connectionName;
	
	public void loadClass() throws ClassNotFoundException {
	    if (className != null) {
	        Class.forName(className);
	    } 
	}
	
	public String getConnectionName() {
	    return connectionName;
	}
	
	public InputStream getContactsSchema() throws SDBExecutionException {
		String propertyName = "sdb.contacts.schema." + name().toLowerCase();
		String schema = System.getProperty(propertyName);
		if (schema == null) {
			throw new SDBExecutionException("Contacts schema for '" + name() + "' not found. " +
					"Please set " + propertyName + " to schema location.");
		}
		
		InputStream stream = getClass().getClassLoader().getResourceAsStream(schema);
		
		if (stream == null) {
			File file = new File(schema);
			if (!file.exists() || file.isDirectory()) {
				throw new SDBExecutionException("File " + file.getAbsolutePath() + " is not valid contacts schema. " +
					"Please set " + propertyName + " to schema location.");
			}
			try { 
				stream = new FileInputStream(file);
			} catch (FileNotFoundException ex) {}
		}
		
		return stream;
	}

//	public void validateDb(File inputDb) throws SDBValidationException {
//		try {
//			this.loadClass();
//		} catch (ClassNotFoundException ex ) {
//			throw new SDBValidationException(ex.getLocalizedMessage());
//		}
//		Connection connection = null;
//		try {
//			connection = DriverManager.getConnection(connectionName + inputDb.getAbsolutePath());
//			connection.isClosed();
//			connection.getCatalog();
//			connection.getMetaData().getTableTypes();
//		} catch(SQLException ex){           
//            throw new SDBValidationException("Unable to open databaseManager: "+ex.getMessage());
//        } 
//		
//		try {
//			connection.getMetaData();
//		} catch(SQLException ex){           
//	        throw new SDBValidationException("Wrong databaseManager type: "+ex.getMessage());
//	    } finally {
//			try {
//				connection.close();
//			} catch(SQLException ex){           
//		        throw new SDBValidationException("Unable to close databaseManager: "+ex.getMessage());
//		    } 
//	    }
//
//
//	}
	
}
