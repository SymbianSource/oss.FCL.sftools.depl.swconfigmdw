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

import junit.framework.Assert;
import junit.framework.JUnit4TestAdapter;

import org.junit.Test;

public class ModeParserTest {
	ModeParser parser;
	
	public static junit.framework.Test suite() { 
	    return new JUnit4TestAdapter(ModeParserTest.class); 
	}
	
	@Test
	public void testSqliteContacts() {
		parser = new ModeParser("sqlite.contacts");
		Assert.assertEquals(parser.getDbMode(), DBMode.CONTACTS);
		Assert.assertEquals(parser.getDbType(), DBType.SQLITE);
		Assert.assertNull(parser.getDbSchema());
	}

	@Test
	public void testSqlite() {
		parser = new ModeParser("sqlite");
		Assert.assertEquals(parser.getDbMode(), DBMode.GENERIC);
		Assert.assertEquals(parser.getDbType(), DBType.SQLITE);
		Assert.assertNull(parser.getDbSchema());
	}
	
	@Test
	public void testDbmsContacts() {
		parser = new ModeParser("dbms.contacts");
		Assert.assertEquals(parser.getDbMode(), DBMode.CONTACTS);
		Assert.assertEquals(parser.getDbType(), DBType.DBMS);
		Assert.assertNull(parser.getDbSchema());
	}

	@Test
	public void testDbms() {
		parser = new ModeParser("dbms");
		Assert.assertEquals(parser.getDbMode(), DBMode.GENERIC);
		Assert.assertEquals(parser.getDbType(), DBType.DBMS);
		Assert.assertNull(parser.getDbSchema());
	}
	
	@Test
	public void testCed() {
		parser = new ModeParser("ced");
		Assert.assertEquals(parser.getDbMode(), DBMode.GENERIC);
		Assert.assertEquals(parser.getDbType(), DBType.CED);
		Assert.assertNull(parser.getDbSchema());
	}

	@Test
	public void testGetDbSchema() {
		parser = new ModeParser("ced.9.5");
		Assert.assertEquals(parser.getDbMode(), DBMode.GENERIC);
		Assert.assertEquals(parser.getDbType(), DBType.CED);
		Assert.assertEquals(parser.getDbSchema(), "9.5");
	}

}
