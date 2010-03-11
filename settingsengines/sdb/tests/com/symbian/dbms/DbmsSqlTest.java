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


public class DbmsSqlTest {
	Connection con;
	Statement statement;
	ResultSet set;
	
	String dbms = "dbms:/temp.db";
	
	private static void deleteDB() {
		File file = new File("temp.db");
		if (file.exists()) {
			boolean deleted = file.delete();
			Assert.assertTrue(deleted);
		}
	}
	
	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
	    System.setProperty("com.symbian.dbms.lib.path", "lib/");
		Class.forName("com.symbian.dbms.jdbc.DbmsDriver");
		deleteDB();
	}

	@AfterClass
	public static void tearDownAfterClass() throws Exception {
		deleteDB();
	}
	
	@Before
	public void setUp() throws Exception {
		deleteDB();
		con = DriverManager.getConnection(dbms);
		statement = con.createStatement();
		Assert.assertNotNull(con);
		Assert.assertNotNull(statement);
	}

	@After
	public void tearDown() throws Exception {
		if (con != null)
			con.close();
		deleteDB();
	}
	
	@Test
	public void createSingleTable() throws Exception {
		Statement st = con.createStatement();
		Assert.assertNotNull(st);
		boolean result = st.execute("create table test (T1 INTEGER, T2 CHAR(10), T3 FLOAT, T4 LONG VARBINARY)");
		Assert.assertFalse(result);
		result = st.execute("insert into TEST (T1, T2, T3, T4) values (17, '1s', 1.1, X'CAFEBABE' )");
		Assert.assertFalse(result);
		st.close();
	//	Assert.assertTrue(st.isClosed());
		
		st = con.createStatement();
		set = st.executeQuery("select * from test");
		Assert.assertNotNull(set);
		Assert.assertEquals(1, set.findColumn("T1"));
		Assert.assertEquals(2, set.findColumn("T2"));
		Assert.assertEquals(3, set.findColumn("T3"));
		Assert.assertEquals(4, set.findColumn("T4"));
		
		Assert.assertTrue(set.first());
		
		Assert.assertEquals(set.getInt(1), 17);
		Assert.assertEquals(set.getInt("T1"), 17);
		
		set.close();
	//	Assert.assertTrue(set.isClosed());
		
		st.close();
		
	}
	
	@Test
	public void testInsert() throws Exception {
		Statement st = con.createStatement();
		Assert.assertNotNull(st);
		st.execute("create table test (T1 INTEGER, T2 CHAR(10), T3 FLOAT, T4 LONG VARBINARY)");
		st.execute("insert into test (T1, T2, T3, T4) values (17, '1s', 1.1, X'CAFEBABE' )");
		st.execute("insert into test (T1, T2, T3, T4) values (20, 'ooo', 5.5, X'CAFEBSAA' )");
		st.execute("insert into test (T1, T2, T3, T4) values (30, 'oo4o', 5.6, X'CAFEBSAA' )");
		st.execute("insert into test (T1, T2, T3, T4) values (40, 'oo2o', 5.7, X'CAFEBSAA' )");
	
		set = st.executeQuery("select * from test");
		Assert.assertNotNull(set);
		//Assert.assertTrue(set.isBeforeFirst());
		Assert.assertTrue(set.next());
		Assert.assertTrue(set.next());
		Assert.assertTrue(set.next());
		Assert.assertTrue(set.next());
		Assert.assertFalse(set.next());
		set.close();
		st.close();
	}
	
	@Test
	public void testSelect() throws Exception {
		Statement st = con.createStatement();
		Assert.assertNotNull(st);
		st.execute("create table test (T1 INTEGER, T2 CHAR(10), T3 FLOAT, T4 LONG VARBINARY)");
		st.execute("insert into test (T1, T2, T3, T4) values (17, '1s', 1.1, X'CAFEBABE' )");
		st.execute("insert into test (T1, T2, T3, T4) values (20, 'ooo', 5.5, X'CAFEBSAA' )");
		st.execute("insert into test (T1, T2, T3, T4) values (30, 'oo4o', 5.6, X'CAFEBSAA' )");
		st.execute("insert into test (T1, T2, T3, T4) values (40, 'oo2o', 5.7, X'CAFEBSAA' )");
		try {
			set = st.executeQuery("select T1 from test where T2='ooo'");
			set.close();
		} catch (SQLException e) {
			Assert.fail("known defect");
		}
		st.close();
//		Assert.assertTrue(st.isClosed());
	}
	
	@Test
	public void testUpdate() throws Exception {
		
		Statement st = con.createStatement();
		Assert.assertNotNull(st);
		
		st.execute("create table test (T1 INTEGER, T2 CHAR(10), T3 FLOAT, T4 LONG VARBINARY)");
		st.execute("insert into test (T1, T2, T3, T4) VALUES (17, '1s', 1.1, X'CAFEBABE' )");
		st.execute("insert into test (T1, T2, T3, T4) values (20, 'ooo', 5.5, X'CAFEBSAA' )");

		st.execute("update test set T1=18 where T3=5.5");
		
		set = st.executeQuery("select * from test where T1=18");
		set.first();
		Assert.assertEquals("ooo", set.getString(2));
		boolean result = set.next();
		Assert.assertFalse(result);
		set.close();
		
		try {
			st.execute("update test set T1=21 where T2='ooo'");
		} catch (SQLException e) {
			Assert.fail("known defect");
		}
		st.close();
	}
	
	
}









