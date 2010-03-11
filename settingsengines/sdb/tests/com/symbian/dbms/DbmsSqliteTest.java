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
import java.sql.SQLException;
import java.sql.Statement;

import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

public class DbmsSqliteTest {

	Connection con;
	Statement statement;
	
	String dbms = "dbms:/temp.db";
	String sqlite = "jdbc:sqlite:temp.db";
	
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
		file.delete();
	}

	@Before
	public void setUp() throws Exception {
		File file = new File("temp.db");
		file.delete();
	}

	@After
	public void tearDown() throws Exception {
		File file = new File("temp.db");
		file.delete();
	}
	
    @Test (expected= SQLException.class)
	public void sqliteToDbms() throws Exception {
		Connection con = DriverManager.getConnection(sqlite);
		con.close();

		Connection con2 = DriverManager.getConnection(dbms);
		con2.getMetaData();
		//Statement st2 = con2.createStatement();
		//st2.execute("select *");
		//con2.close();
	}
	
    @Test (expected= SQLException.class)
	public void dbmsToSqlite() throws Exception {
		//this creates a dbms file
		Connection con = DriverManager.getConnection(dbms);
		con.close();

		//and this opens it as sqlite database
		Connection con2 = DriverManager.getConnection(sqlite);
		con2.getMetaData();
		con2.getCatalog();

		//tries to execute statement which should fail
		Statement st2 = con2.createStatement();
		st2.execute("select * from table1");
		con2.close();

	}
	
	

}
