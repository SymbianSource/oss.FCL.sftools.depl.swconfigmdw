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
import java.util.Arrays;
import java.util.Locale;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.PreparedStatement;

import junit.framework.TestCase;

public class TestDbmsLocales extends TestCase {

	protected void setUp() throws Exception {
		File f = new File("test.db");
		if ( f.exists() ) {
			f.delete();
		}
	}

	protected void tearDown() throws Exception {
		File f = new File("test.db");
		if ( f.exists() ) {
			f.delete();
		}
	}
	
	public void testDummy(){}
	
	public void xtestSettingsDefualt() throws Exception {
		
		Character[] localisedChar = {'A','B','Z', '\u00C4'};
		Character[] localisedCharExpected = {'A','B','Z', '\u00C4'};
		
		Class.forName("com.symbian.dbms.jdbc.DbmsDriver");
		String url = "dbms:/test1.db";
		
		Connection conn = null;
		Statement st = null;
		PreparedStatement prepSt = null;
		ResultSet rs = null; 
		
		try{
			conn = DriverManager.getConnection(url);
			//create table in database
			st = conn.createStatement();
			st.execute("CREATE TABLE T1 (V1 VARCHAR(1))");
			//insert local specific chars
			prepSt = conn.prepareStatement("INSERT INTO T1 VALUES(?)");
			for(int i = 0; i < 4; i++) {
				prepSt.setString(1, localisedChar[i].toString());
				prepSt.execute();
			}			
			
			//Create collated index on T1
			st.execute("CREATE INDEX IDX_T1_1 ON T1(V1) COLLATE COLLATED");
			
			//read values from table
			Character[] dbChar = new Character[4];
			st.execute("SELECT V1 FROM T1 ORDER BY V1");
			rs = st.getResultSet();
			if(rs != null){
				if(!rs.first())
					fail("database is empty.");
				int inc = 0;
				do{
					dbChar[inc++] = rs.getString(1).charAt(0);		
				}while(rs.next());
			}
			rs.close();
			
			assertTrue(Arrays.equals(dbChar, localisedCharExpected));
			//compare order with char[]
//			if(localisedChar[0] != dbChar[0])
//				fail("Data remains unsorted");
			                        
			prepSt.close();
			st.close();
			 
		} 
		catch (SQLException e) {
			e.printStackTrace();
			fail("SQL execution failed");
		}
		finally {
			conn.close();
			tearDown();
		}		
	}
	
	public void xtestSettingsCollated() throws Exception {

		Character[] localisedChar = {'A','B','Z', '\u00C4'};
		Character[] localisedCharExpected = {'A','\u00C4','B','Z'};

		Class.forName("com.symbian.dbms.jdbc.DbmsDriver");
		String url = "dbms:/test2.db?localeDll=elocl.03";
		
		Connection conn = null;
		Statement st = null;
		PreparedStatement prepSt = null;
		ResultSet rs = null; 
		
		try{
			conn = DriverManager.getConnection(url);
			//create table in database
			st = conn.createStatement();
			st.execute("CREATE TABLE T1 (V1 VARCHAR(1))");
			//insert local specific chars
			prepSt = conn.prepareStatement("INSERT INTO T1 VALUES(?)");
			for(int i = 0; i < 4; i++) {
				prepSt.setString(1, localisedChar[i].toString());
				prepSt.execute();
			}			
			
			//Create collated index on T1
			st.execute("CREATE INDEX IDX_T1_1 ON T1(V1) COLLATE COLLATED");
			
			//read values from table
			Character[] dbChar = new Character[4];
			st.execute("SELECT V1 FROM T1 ORDER BY V1");
			rs = st.getResultSet();
			if(rs != null){
				if(!rs.first())
					fail("database is empty.");
				int inc = 0;
				do{
					dbChar[inc++] = rs.getString(1).charAt(0);		
				}while(rs.next());
			}
			rs.close();
			
			//compare order with char[]
			assertTrue(Arrays.equals(dbChar, localisedCharExpected));
//			if(localisedChar[0] != dbChar[0])
//				fail("Data remains unsorted");
			                        
			prepSt.close();
			st.close();
			 
		} 
		catch (SQLException e) {
			fail("SQL execution failed");
		}
		finally {
			conn.close();
		}				
	}

}
