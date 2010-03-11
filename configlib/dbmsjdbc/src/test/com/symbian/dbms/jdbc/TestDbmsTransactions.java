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

package com.symbian.dbms.jdbc;

import java.io.File;
import java.sql.Date;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.PreparedStatement;


import junit.framework.TestCase;

public class TestDbmsTransactions extends TestCase {

	protected void setUp() throws Exception {
		File f = new File("test.db");
		if ( f.exists() ) {
			f.delete();
		}
		if ( f.exists() ) {
			throw new Exception("file locked");
		}
	}

	protected void tearDown() throws Exception {
		File f = new File("test.db");
		if ( f.exists() ) {
			f.delete();
		}
		if ( f.exists() ) {
			throw new Exception("file locked");
		}
	}
	
	//test batch data definition operations
	public void testDdlOperations() throws Exception {
		
		//Table names in an array
		String[] tbl = {"TABLE1","TABLE2","TABLE3","TABLE4","TABLE5"};
		
		
		Class.forName("com.symbian.dbms.jdbc.DbmsDriver");
		String url = "dbms:/test.db?volumeio.BlockSize=8192";
		
		Connection conn = null;
		Statement st = null;
		
		try{
			//Open connection
			conn = DriverManager.getConnection(url);
			st = conn.createStatement();
			st.execute("BEGIN");
			//create five table in one go
			for (int i = 0; i < 5; i++)
				st.execute("CREATE TABLE " + tbl[i] + "(COL1 INTEGER, COL2 VARCHAR(30))");
			
			//commit transaction to DB
			// workaround for a known bug in driver
			// conn.commit();
			st.execute("COMMIT");
			
			//read tables back from DB
			for (int i = 0; i < 5; i++) {
				try {
					TableExist(conn, tbl [i]);
				}
				catch (SQLException e){
					fail("Query failed on table : "+tbl[i]);
				}
			}	
			
			//Alter tables in batch mode 
			st.execute("BEGIN");
			
			for (int i = 0; i < 5; i++)
				st.execute("ALTER TABLE " + tbl[i] + " ADD COL3 DATE");
			
			st.execute("COMMIT");
			
			//read tables back from DB
			for (int i = 0; i < 5; i++) {
				try {
					ColumnExist(conn, tbl [i], "COL3");
				}
				catch (SQLException e){
					fail("Query failed on table : "+tbl[i]);
				}
			}
			
			//Drop some tables
			st.execute("BEGIN");
			
			for (int i = 0; i < 5; i++)
				st.execute("DROP TABLE " + tbl[i]);
			
			st.execute("COMMIT");
			
			//read tables back from DB
			for (int i = 0; i < 5; i++) {
				try {
					TableExist(conn, tbl[i]);
					fail("All tables can not be deleted");
				}
				catch (SQLException e) {
					//pass
				}
			}
		} 
		finally {
			try{st.close();}catch(Exception e){}
			try{conn.close();}catch(Exception e){}
		}
	}
	
	private void TableExist(Connection conn, String tbl) throws Exception {
		Statement st = conn.createStatement();
		try {
		st.execute("SELECT * FROM "+tbl);
		}
		finally {
			try{st.close();}catch(Exception e){}
		}
	}
	
	private void ColumnExist(Connection conn, String tbl, String col) throws Exception {
		Statement st = conn.createStatement();
		try {
		st.execute("SELECT "+ col +" FROM "+tbl);
		}
		finally {
			try{st.close();}catch(Exception e){}
		}
	}
	
	//test batch data manipulation
	public void testDmlOperations() throws Exception {
		
		//Table value
		String[] valChar = {"VALUE1","VALUE2","VALUE3","VALUE4","VALUE5"};
		Integer[] valInt = {10,20,30,40,50};
		long valDate = 24L*60L*60L*2000L;
		
		int arrayIndex = 0;
		
		Class.forName("com.symbian.dbms.jdbc.DbmsDriver");
		String url = "dbms:/test.db?volumeio.BlockSize=8192";
		
		Connection conn = null;
		Statement st = null;
		PreparedStatement pst = null;
		ResultSet rs = null;
		
		try{
			//Open connection
			conn = DriverManager.getConnection(url);
			st = conn.createStatement();
			
			st.execute("BEGIN");
			//create test table 
			st.execute("CREATE TABLE DMLTEST (COL1 INTEGER, COL2 VARCHAR(30), COL3 DATE)");
			st.execute("COMMIT");
			
			st.execute("BEGIN");
			pst = conn.prepareStatement("INSERT INTO DMLTEST VALUES(?, ?, ?)");
			for (int i = 0; i < 5; i++) {
				pst.setInt(1, valInt[i]);
				pst.setString(2, valChar[i]);
				Date date = new Date(valDate);
				pst.setDate(3, date);
				pst.execute();
			}
			st.execute("COMMIT");
			
			
			//read column values back from DMLTES
			st.execute("SELECT * FROM DMLTEST");
			rs = st.getResultSet();
			arrayIndex = 0;
			if(rs != null) {
				if(!rs.first())
					fail("database is empty.");
				do{
					if( rs.getInt(1) != valInt[arrayIndex])
						fail("value of DMLTEST(COL1) doesn't match");
					if( ! rs.getString(2).equals(valChar[arrayIndex]))
						fail("value of DMLTEST(COL2) doesn't match");
					if( rs.getDate(3).getTime() != valDate)
						fail("value of DMLTEST(COL3) doesn't match");
					arrayIndex++;
				}while(rs.next());
			}
				
			rs.close();
			pst.close();
			//Update table column values in reverse
			pst = conn.prepareStatement("UPDATE DMLTEST SET COL1 = ? WHERE COL1 = ?");
		
			st.execute("BEGIN");
			for (int i = 0; i < 5; i++) {
				pst.setInt(1, valInt[4-i]);
				pst.setInt(2, valInt[i]);
				pst.execute();
			}
			st.execute("COMMIT");
			
			//read tables back from DB
			st.execute("SELECT * FROM DMLTEST ORDER BY COL1");
			rs = st.getResultSet();
			if(rs != null) {
				if(!rs.first())
					fail("database is empty.");
				do{
					// value 40 and 50 should be overwritten
					if( rs.getInt(1) == valInt[3] || 
							rs.getInt(1) == valInt[4] )
						fail("value of DMLTEST(COL1) doesn't match");
					
				}while(rs.next());
			}
			
			rs.close();
			pst.close();
			//Delete row from table
			st.execute("BEGIN");
			for (int i = 0; i < 5; i++) {
				st.execute("DELETE FROM DMLTEST WHERE COL2 = '" + valChar[i]+ "'" );
			}
			st.execute("COMMIT");
			
			//Read values from table
			st.execute("SELECT * FROM DMLTEST");
			
			rs = st.getResultSet();
			//pass if nothing in table
			if(rs != null) {
				if(rs.first())
					fail("table is not empty.");
			}
		} 
		catch (SQLException e){
			fail("SQL execution failed");
			}
		finally {
			try{rs.close();}catch(Exception e){}
			try{pst.close();}catch(Exception e){}
			try{st.close();}catch(Exception e){}
			try{conn.close();}catch(Exception e){}
		}
	}

	//Test transaction roll-back.   
	public void testRollback() throws Exception {
				
		Class.forName("com.symbian.dbms.jdbc.DbmsDriver");
		String url = "dbms:/test.db?volumeio.BlockSize=8192";
		
		Connection conn = null;
		Statement st = null;
		try{
			//Open connection
			conn = DriverManager.getConnection(url);
			st = conn.createStatement();
			
			st.execute("BEGIN"); 
			
			st.execute("CREATE TABLE ROLLBACKTEST (COL1 INTEGER, COL2 VARCHAR(30))");
			st = conn.prepareStatement("INSERT INTO DMLTEST VALUES(100, 'VALUE1')");
			st = conn.prepareStatement("UPDATE DMLTEST SET COL2 = 'NEWVALUE' WHERE COL1 = 100");
			
			st.execute("ROLLBACK");
			
			try {
			st.execute("COMMIT");
			fail("COMMIT performed while no open transaction");
			}
			catch (RuntimeException e){
				//pass
			}
			
			try {
				st.execute("SELECT * FROM ROLLBACKTEST WHERE COL2 = 'NEWVALUE'");
				fail("transaction rollback failed");
			}
			catch (SQLException sqlerr ){
				//pass
			}
		} 
		catch (SQLException e){
			fail("SQL execution failed");
			}
		finally {
			try{st.close();}catch(Exception e){}
			try{conn.close();}catch(Exception e){}
		}

	}
	
}
