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

package com.symbian.sdb.mode.flow.ced;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

import java.util.NoSuchElementException;

import junit.framework.JUnit4TestAdapter;

import org.junit.Test;

/**
 * @author jamesclark
 *
 */
public class CedSchemaTest {

	private static final String EXE_NAME_93 = "cedv9_3.exe";
	private static final String EXE_NAME_94 = "cedv9_4.exe";
	private static final String EXE_NAME_95 = "cedv9_5.exe";

	private static final String EXE_NAME_LIN_93 = "cedv9_3";
	private static final String EXE_NAME_LIN_94 = "cedv9_4";
	private static final String EXE_NAME_LIN_95 = "cedv9_5";
	
	private static final String CED_DEPLOY_LOCATION = "here";

	private static final String SCHEMA_LABEL_91 = "91";
	private static final String SCHEMA_LABEL_92 = "92";
	private static final String SCHEMA_LABEL_93 = "93";
	private static final String SCHEMA_LABEL_94 = "94";
	private static final String SCHEMA_LABEL_95 = "95";
	private static final String SCHEMA_LABEL_96 = "96";

	/**
	 * Test method for {@link com.symbian.sdb.mode.flow.ced.CedSchema#getExeName()}.
	 */
	@Test
	public void testGetExeName() {
		String originalValue = System.getProperty("os.name");
		System.setProperty("os.name", "Windows XP");
		
		assertEquals("The ced91 executable name is incorrect.",EXE_NAME_93,CedSchema.ced91.getExeName());
		assertEquals("The ced92 executable name is incorrect.",EXE_NAME_93,CedSchema.ced92.getExeName());
		assertEquals("The ced93 executable name is incorrect.",EXE_NAME_93,CedSchema.ced93.getExeName());
		assertEquals("The ced94 executable name is incorrect.",EXE_NAME_94,CedSchema.ced94.getExeName());
		assertEquals("The ced95 executable name is incorrect.",EXE_NAME_95,CedSchema.ced95.getExeName());
		
		System.setProperty("os.name", originalValue);
	}
	
	/**
	 * Test method for {@link com.symbian.sdb.mode.flow.ced.CedSchema#getExeName()}.
	 */
	@Test
	public void testGetExeName_Linux() {
		String originalValue = System.getProperty("os.name");
		System.setProperty("os.name", "linux");
		
		assertEquals("The ced91 executable name is incorrect.",EXE_NAME_LIN_93,CedSchema.ced91.getExeName());
		assertEquals("The ced92 executable name is incorrect.",EXE_NAME_LIN_93,CedSchema.ced92.getExeName());
		assertEquals("The ced93 executable name is incorrect.",EXE_NAME_LIN_93,CedSchema.ced93.getExeName());
		assertEquals("The ced94 executable name is incorrect.",EXE_NAME_LIN_94,CedSchema.ced94.getExeName());
		assertEquals("The ced95 executable name is incorrect.",EXE_NAME_LIN_95,CedSchema.ced95.getExeName());
		
		System.setProperty("os.name", originalValue);
	}

	/**
	 * Test method for {@link com.symbian.sdb.mode.flow.ced.CedSchema#getExeDirectory()}.
	 */
	@Test
	public void testGetExeDirectory() {
		Boolean isWindows = System.getProperty("os.name").startsWith("Windows");
		String CED_LOCATION;
		if (isWindows) {
			CED_LOCATION = "d:\\ced";
		} else {
			CED_LOCATION = "/home";
		}
		
		System.setProperty("sdb.ced.location", CED_LOCATION);
		
		assertEquals("The ced91 location should be the \"93\" folder in the install location.",CED_LOCATION,CedSchema.ced93.getExeDirectory().getPath());
		assertEquals("The ced92 location should be the \"93\" folder in the install location.",CED_LOCATION,CedSchema.ced93.getExeDirectory().getPath());
		assertEquals("The ced93 location should be the \"93\" folder in the install location.",CED_LOCATION,CedSchema.ced93.getExeDirectory().getPath());
		assertEquals("The ced94 location should be the \"94\" folder in the install location.",CED_LOCATION,CedSchema.ced94.getExeDirectory().getPath());
		assertEquals("The ced95 location should be the \"95\" folder in the install location.",CED_LOCATION,CedSchema.ced95.getExeDirectory().getPath());
	}
	
	/**
	 * Test method for {@link com.symbian.sdb.mode.flow.ced.CedSchema#getSchema(java.lang.String)}.
	 */
	@Test
	public void testGetSchema() {
		assertEquals("The ced91 schema enum should be returned for input str "+SCHEMA_LABEL_91, CedSchema.ced91, CedSchema.getSchema(SCHEMA_LABEL_91));
		assertEquals("The ced92 schema enum should be returned for input str "+SCHEMA_LABEL_92, CedSchema.ced92, CedSchema.getSchema(SCHEMA_LABEL_92));
		assertEquals("The ced93 schema enum should be returned for input str "+SCHEMA_LABEL_93, CedSchema.ced93, CedSchema.getSchema(SCHEMA_LABEL_93));
		assertEquals("The ced94 schema enum should be returned for input str "+SCHEMA_LABEL_94, CedSchema.ced94, CedSchema.getSchema(SCHEMA_LABEL_94));
		assertEquals("The ced95 schema enum should be returned for input str "+SCHEMA_LABEL_95, CedSchema.ced95, CedSchema.getSchema(SCHEMA_LABEL_95));
		
		try {
			CedSchema.getSchema(SCHEMA_LABEL_96);
			fail("The 96 label should not be supported.");
		} catch (Exception e) {
			assertEquals(NoSuchElementException.class, e.getClass());
		}
	}
	
	public static junit.framework.Test suite() { 
        return new JUnit4TestAdapter(CedSchemaTest.class); 
    }

}
