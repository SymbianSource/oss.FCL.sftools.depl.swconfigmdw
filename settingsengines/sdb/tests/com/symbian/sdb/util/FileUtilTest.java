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
//

package com.symbian.sdb.util;

import java.io.File;

import junit.framework.TestCase;

import org.junit.Test;

import com.symbian.sdb.settings.Settings;

public class FileUtilTest  extends TestCase  {

	public void testFileExtension(){
		
		assertEquals(FileUtil.appendToFilename("dir//test.ext", "_NEW"), "dir//test_NEW.ext");
		assertEquals(FileUtil.appendToFilename("dir//test", "_NEW"), "dir//test_NEW");
		assertEquals(FileUtil.appendToFilename("", "_NEW"), "_NEW");
		assertEquals(FileUtil.appendToFilename(null, "_NEW"), null);
	}
	
	/**
	 * Test method for {@link com.symbian.sdb.mode.flow.GenericFlow#determineOutputFile(java.io.File)}.
	 * If a given file is requested it should be set.
	 */
	@Test
	public void testDetermineOutputFile() {
		assertEquals("requestedButExists",FileUtil.determineOutputFile(new File("tests//config//requestedButExists")).getName());
	}
	
	/**
	 * Test method for {@link com.symbian.sdb.mode.flow.GenericFlow#determineOutputFile(java.io.File)}.
	 * If a no file is requested the default should be used 
	 */
	@Test
	public void testDetermineOutputFile_default() {
		System.setProperty(Settings.SDBPROPS.dbname.toString(), "tests//config//requestedDoesntExists");
		assertEquals("requestedDoesntExists",FileUtil.determineOutputFile(null).getName());
	}
	
	/**
	 * Test method for {@link com.symbian.sdb.mode.flow.GenericFlow#determineOutputFile(java.io.File)}.
	 * If a no file is requested the default should be used 
	 */
	@Test
	public void testDetermineOutputFile_existingDefault() {
		System.setProperty(Settings.SDBPROPS.dbname.toString(), "tests//config//requestedButExists");
		assertEquals("requestedButExists_0",FileUtil.determineOutputFile(null).getName());
	}	
}
