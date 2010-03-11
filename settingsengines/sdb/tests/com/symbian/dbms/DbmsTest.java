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

package com.symbian.dbms;


import java.io.File;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

import org.junit.After;
import org.junit.AfterClass;
import org.junit.Assert;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

public class DbmsTest {

	Connection con;
	Statement statement;
	
	String dbms = "dbms:/temp.db";
	String jdbc = "jdbc:sqlite:temp.db";
	
	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
	    System.setProperty("com.symbian.dbms.lib.path", "lib/");
	    System.setProperty("org.sqlite.lib.path", "lib/");
		Class.forName("com.symbian.dbms.jdbc.DbmsDriver");
		Class.forName("org.sqlite.JDBC");
		
		File file = new File("temp.db");
		file.delete();
	}

	@AfterClass
	public static void tearDownAfterClass() throws Exception {
		File file = new File("temp.db");
		if (file.exists()) {
			boolean result = file.delete();
			Assert.assertTrue(result);
		}
	}

	@Before
	public void setUp() throws Exception {
		con = DriverManager.getConnection(dbms);
		statement = con.createStatement();
		Assert.assertNotNull(con);
		Assert.assertNotNull(statement);
	}

	@After
	public void tearDown() throws Exception {
		if (con != null)
			con.close();
	}

	@Test
	public void openCloseTwice() throws Exception {
		Statement st = con.createStatement();
		Assert.assertNotNull(st);
		con.close();

		con = DriverManager.getConnection(dbms);
		Assert.assertNotNull(con);
		
		con.close();
		//con = null;
	}
	
	@Test(expected= SQLException.class)
	public void incorrectStatement0() throws Exception {
		statement.execute("select *");
	}
	
	@Test(expected= SQLException.class)
	public void incorrectStatement1() throws Exception {
		statement.execute("asda asf rubbish statement");
	}
	
	//crashes JVM at this moment
	@Test
	public void closeConnection() throws Exception {
		con.close();
	}
	
	@Test
	public void getSchema() throws Exception {
		Statement stmt = null;
		try {
			stmt = con.createStatement();
			try{
				stmt.execute("DROP TABLE TEST");
			}catch (Exception e) {}
			stmt.execute("CREATE TABLE TEST (T1 INTEGER AUTOINCREMENT, T2 CHAR(10) NOT NULL, T3 DOUBLE)");
			stmt.execute("CREATE INDEX TEST_INDEX ON TEST(T2)");
		} finally {
			if ( stmt != null ) {
				try {stmt.close();} catch (SQLException e) {e.printStackTrace();}
			}
			if ( con != null ) {
				try {con.close();} catch (SQLException e) {e.printStackTrace();}
			}
		}
	
	}
	
	
}






