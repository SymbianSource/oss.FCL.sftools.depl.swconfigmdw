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
// DatabaseManagerTest.java
//



package com.symbian.sdb.database;

import java.io.File;
import java.sql.Connection;
import java.sql.SQLException;

import org.jmock.Mock;
import org.jmock.cglib.MockObjectTestCase;

import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.mode.DBType;

public class DBManagerTest extends MockObjectTestCase {

	DBManager fDbManager = null;
	
	private String fDbName = "tests/config/TEST_DB.db";

	protected void setUp() throws Exception {
		super.setUp();
		System.setProperty("org.sqlite.lib.path", "lib/");
		System.setProperty("com.symbian.dbms.lib.path", "lib/");
		
		if (null == fDbManager)    {
		    fDbManager = new DBManager();    
		}
	}
	
	/**
	 * Tests the Database is opening correctly
	 * 
	 */
	public void testOpenSqliteDb(){
		
		try {
			fDbManager.openConnection(DBType.SQLITE, fDbName);
			assertFalse(fDbManager.dbConn == null);
			assertTrue(fDbManager.dbConn.getClass().toString().contains("sqlite"));
		} catch(SDBExecutionException ex){
			fail("Unexpected SDBExecutionException in opening DB " + ex.getMessage());
		}
		
	}
	
	   /**
     * Tests the dbms Database is opening correctly
     * 
     */
    public void testOpenDbmsDb(){
        
        try {
            fDbManager.openConnection(DBType.DBMS, fDbName);
            assertFalse(fDbManager.dbConn == null);
            assertTrue(fDbManager.dbConn.getClass().toString().contains("dbms"));
            fDbManager.closeConnection();
        } catch(SDBExecutionException ex){
            fail("Unexpected SDBExecutionException in opening DB " + ex.getMessage());
        } 
        
    }
	
	/**
	 * Tests the closing of the databaseManager. After closing, the connection
	 * should be null or closed
	 *
	 */
	public void testCloseSqliteDb(){	
		
		try{
			fDbManager.openConnection(DBType.SQLITE, fDbName);
			fDbManager.closeConnection();
			assertTrue((fDbManager.dbConn == null)|| (fDbManager.dbConn.isClosed()));					
		} catch(SQLException ex){
			fail("Unexpected SQLException: "+ex.getMessage());
		} catch(SDBExecutionException ex){
			fail("Unexpected CommandException: "+ex.getMessage());
		}
	}
	
	   /**
     * Tests the closing of the databaseManager. After closing, the connection
     * should be null or closed
     *
     */
    public void testCloseDbmsDb(){    
        
        try{
            fDbManager.openConnection(DBType.DBMS, fDbName);
            fDbManager.closeConnection();
            assertTrue((fDbManager.dbConn == null)|| (fDbManager.dbConn.isClosed()));                   
        } catch(SQLException ex){
            fail("Unexpected SQLException: "+ex.getMessage());
        } catch(SDBExecutionException ex){
            fail("Unexpected CommandException: "+ex.getMessage());
        }
    }
	
	/**
	 * Tests the execution of the SQL statements from a file
	 *
	 */
//	public void testExecuteSqlFromFile(){
//		
//		try{
//			fDbManager.openConnection(fDbName);
//			fDbManager.executeSQLFile(new File(fTestSqlFile));
//			fDbManager.closeConnection();
//			File lFile = new File(fDbName);
//			assertTrue(lFile.exists());
//		}
//		catch(SDBExecutionException ex){
//			fail("Unexpected CommandException: "+ex.getMessage());
//		}
//		catch(IOException ex){
//			fail("Unexpected IOException: "+ex.getMessage());
//		}
//		catch(SQLException ex){
//			fail("Unexpected SQLException: "+ex.getMessage());
//		}
//		
//		
//	}
	
	/**
	 * This tests a SQLException is thrown when bad SQL is passed through
	 */
//	public void testExecuteBadSql(){
//		
//		try{
//			fDbManager.openConnection(fDbName);
//			fDbManager.executeSQLFile(new File(fTestBadSqlFile));
//			fDbManager.closeConnection();
//			fail(" Expected SQLEXception not thrown");
//		}
//		catch(SDBExecutionException ex){
//			fail("Unexpected CommandException: "+ex.getMessage());
//		}
//		catch(IOException ex){
//			fail("Unexpected IOException: "+ex.getMessage());
//		}
//		catch(SQLException ex){
//			//Get here = succeed
//			fDbManager.closeConnection();
//		}
//	}
	
	/**
	 * This tests attempting SQL Execution on a closed databaseManager
	 */
//	public void testExecuteOnClosedDB(){
//		
//		try{			
//			fDbManager.executeSQLFile(new File(fTestSqlFile));
//			fDbManager.closeConnection();
//			fail(" Expected SQLEXception not thrown");
//		}		
//		catch(IOException ex){
//			fail("Unexpected IOException: "+ex.getMessage());
//		}
//		catch(SQLException ex){
//			//Get here = succeed
//			fDbManager.closeConnection();
//		}
//	}
	
	/**
	 * Test execute of sql string
	 */
//	public void testExecuteSqlString(){
//		
//		try{
//			fDbManager.openConnection(fDbName);
//			fDbManager.executeSQL(fTestSql1);
//			fDbManager.executeSQL(fTestSql2);
//			fDbManager.executeSQL(fTestSql3);
//			fDbManager.closeConnection();
//			//get here = suceed
//		}
//		catch(SQLException ex){
//			fail("Unexpected SQLException thrown: "+ ex.getMessage());
//		}
//		catch(SDBExecutionException ex){
//			fail("Unexpected CommandException thrown: "+ex.getMessage());
//		}			
//	}
	
	/**
	 * Tests execution of bad sql string
	 */
//	public void testExecuteBadSqlString(){
//		
//		try{
//			fDbManager.openConnection(fDbName);
//			fDbManager.executeSQL(fTestBadSql);
//			fail("Expected SQLException to be thrown...");
//		}
//		catch(SQLException ex){
//			fDbManager.closeConnection();
//			//get here = success
//		}
//		catch(SDBExecutionException ex){
//			fail("Unexpected CommandException thrown: "+ex.getMessage());
//		}
//	}
	
	/**
	 * Test execution of sqlstring on closed databaseManager
	 */
//	public void testExecuteSqlStringClosedDb(){
//		
//		try{
//			fDbManager.executeSQL(fTestSql1);
//			fail("Expected SQLException to be thrown...");
//		}
//		catch(SQLException ex){
//			fDbManager.closeConnection();
//			//get here = success
//		}		
//	}
	
	/**
	 * Test fail close databaseManager
	 */
	public void testCloseDatabase(){
		
		Mock lMockDbConnection = mock(Connection.class);
		lMockDbConnection.expects(once()).method("close").will(throwException(new SQLException("Expected")));
		lMockDbConnection.expects(once()).method("isClosed").will(returnValue(false));
		
		fDbManager.setConnection((Connection)lMockDbConnection.proxy());	
		fDbManager.closeConnection();	
		
		fDbManager.setConnection(null);
	}

	/**
	 * Test get Connection
	 */
	public void testGetDbConnection(){
		
		Mock lMockDbConnection = mock(Connection.class);
		fDbManager.dbConn = (Connection)lMockDbConnection.proxy();
		assertNotNull(fDbManager.getConnection());
		fDbManager.setConnection(null);
	}
	
	/**
	 * Tear Down
	 */
	public void tearDown(){
		//deletes the DB file created so further tests can start from scratch		
		fDbManager.closeConnection();
		File lFile = new File(fDbName);		
		lFile.delete();
	}
}

