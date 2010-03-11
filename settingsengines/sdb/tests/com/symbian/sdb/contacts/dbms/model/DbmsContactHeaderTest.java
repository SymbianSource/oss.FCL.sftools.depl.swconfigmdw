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

package com.symbian.sdb.contacts.dbms.model;


import java.io.File;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Arrays;
import java.util.List;

import junit.framework.TestCase;

import org.apache.commons.io.FileUtils;
import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

public class DbmsContactHeaderTest extends TestCase {	
	
	Connection con = null;
	Statement statement = null;
	String db = "tests/config/template.cdb";
	String newDb = "template_new";
	File newDBFile;
	byte[] headerBlob = null;

	
	// ~ Attribute flag masks

	@Before
	public void setUp() throws Exception {
		super.setUp();
		newDBFile = File.createTempFile(newDb, "x");
		FileUtils.copyFile(new File(db), newDBFile);
		System.setProperty("com.symbian.dbms.lib.path", "lib/");
		Class.forName("com.symbian.dbms.jdbc.DbmsDriver");
		con = DriverManager.getConnection("dbms:/" + newDBFile.getAbsolutePath());
		statement = con.createStatement();
		Assert.assertNotNull(con);
		Assert.assertNotNull(statement);
	}
	
	private byte[] getHeaderBlobFromDB() throws SQLException {
		
		ResultSet rs = null;
		try {
			rs = statement.executeQuery("SELECT CM_Header FROM contacts WHERE CM_Id = 0");
			rs.first();
			return rs.getBytes(1);
		}
		finally {
			if(rs != null)
				rs.close();
		}
	}
	
	private void persistHeaderToDB(byte[] cmHeader) throws SQLException {
	
		PreparedStatement pst = null; 
		try {
			pst = con.prepareStatement("UPDATE CONTACTS SET CM_Header = ? WHERE CM_Id = 0");
			pst.setBytes(1, cmHeader);
			pst.execute();
		}
		finally {
			pst.close();
		}
	}	
	
	@Test   
	public void testContactFieldHeaderObject() throws Exception {
		
		//Read header blob from DB
		headerBlob = getHeaderBlobFromDB();
		
		//Create contact field header set from DB blob
		AbstractContactHeader header = new ContactHeaderForTemplate(headerBlob);
		
		//create contact header blob from field header
		List<ContactFieldHeader> fields = header.getFieldHeaderList();
		AbstractContactHeader newHeader = new ContactHeaderForTemplate(fields);
		newHeader.persistFieldsToBlob();
		
		byte[] newHeaderBlob = newHeader.getBlob();
		
		
		//compare new header blob with DB blob 
		assertTrue(Arrays.equals(headerBlob, newHeaderBlob));
		
		//Write new header into DB
		persistHeaderToDB(newHeader.getBlob());
		
		//Read blob from database and compare
		assertTrue(Arrays.equals(headerBlob, getHeaderBlobFromDB()));
		
	}
	
	@After
	public void tearDown() throws Exception {
		super.tearDown();
		
		if(statement != null)
			statement.close();
		
		if(con != null)
			con.close();
	}

}
