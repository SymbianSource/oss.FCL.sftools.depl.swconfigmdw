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

package com.symbian.sdb.cmd;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.PrintStream;
import java.util.ArrayList;
import java.util.List;

import junit.framework.JUnit4TestAdapter;

import org.apache.commons.cli2.OptionException;
import org.junit.After;
import org.junit.AfterClass;
import org.junit.Assert;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import com.symbian.sdb.mode.DBType;
import com.symbian.sdb.mode.IModeParser;

public class CommandLinev2Test {
	
	CmdLinev2 cmd;
	static ByteArrayOutputStream output;
	static PrintStream copy;
	
	public static junit.framework.Test suite() { 
	    return new JUnit4TestAdapter(CommandLinev2Test.class); 
	}
	
	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
		output = new ByteArrayOutputStream();
		PrintStream out = new PrintStream(output);
		copy = System.out;
		System.setOut(out);
		System.setProperty("sdb.contacts.enabled", "true");
	}
	
	@AfterClass
	public static void tearDownBeforeClass() throws Exception {
		output.close();
		System.setOut(copy);
	}
	
	@Before
	public void setUp() throws Exception {
		cmd = new CmdLinev2();
		output.reset();
	}
	
	@After
	public void tearDown() throws Exception {
		output.reset();
	}

	@Test
	public void testCommandLineHelp() {
		String[] args = {"-h"};
		try {
			boolean result = cmd.parseArguments(args);
			Assert.assertFalse(result);
			String help = output.toString();
			
			Assert.assertNotNull(help);
			Assert.assertTrue(help.contains("Usage"));
			Assert.assertTrue(help.contains("Options"));
 
		} catch (OptionException ex) {
			fail("Shouldn't fail here.");
		} 
	}
	
   @Test
    public void testGroup() {
        String[] args = {"-g", "groupname"};
        try {
            boolean result = cmd.parseArguments(args);
            Assert.assertTrue(result);
            String group = cmd.getGroup();
            Assert.assertEquals("groupname", group);
 
        } catch (OptionException ex) {
            fail("Shouldn't fail here.");
        } 
    }

	@Test
	public void testPrintVersion() {
		String[] args = {"--version"};
		try {
			boolean result = cmd.parseArguments(args);
			Assert.assertFalse(result);
			String version = output.toString().trim();
			
			Assert.assertNotNull(version);
 
		} catch (OptionException ex) {
			fail("Shouldn't fail here.");
		} 
	}

	@Test
	public void testPrintModes() {
		String[] args = {"-l"};
		try {
			boolean result = cmd.parseArguments(args);
			Assert.assertFalse(result);
			String list = output.toString().trim();
			
			Assert.assertNotNull(list);
			
			Assert.assertTrue(list.contains("Available modes"));

			
		} catch (OptionException ex) {
			fail("Shouldn't fail here.");
		} 
	}
	
	@Test
	public void testCommandLineHelpAndListModes() {
		String[] args = {"-l", "-h"};
		try {
			boolean result = cmd.parseArguments(args);
			Assert.assertFalse(result);
			String list = output.toString().trim();
			
			Assert.assertNotNull(list);

			Assert.assertTrue(list.contains("Usage"));
			Assert.assertTrue(list.contains("Options"));
			Assert.assertTrue(list.contains("Available modes"));
		} catch (OptionException ex) {
			fail("Shouldn't fail here.");
		} 
	}
	
	@Test
	public void testModeDefault() {
		String[] args = {"-h"};
		try {
			boolean result = cmd.parseArguments(args);
			Assert.assertFalse(result);
			IModeParser mode = cmd.getMode();
			Assert.assertEquals(DBType.SQLITE, mode.getDbType());
		} catch (OptionException ex) {
			fail("Shouldn't fail here.");
		} 
	}
	
	@Test
	public void testMode() {
		String[] args = {"-m", "dbms"};
		try {
			boolean result = cmd.parseArguments(args);
			Assert.assertTrue(result);
			IModeParser mode = cmd.getMode();
			Assert.assertEquals(DBType.DBMS, mode.getDbType());
		} catch (OptionException ex) {
			fail("Shouldn't fail here.");
		} 
	}
	
	@Test
	public void testModeMissing() throws OptionException {
		String[] args = {"-o", "d:/xx.db"};
		try {
			boolean result = cmd.parseArguments(args);
			Assert.assertTrue(result);
            IModeParser mode = cmd.getMode();
            Assert.assertEquals(DBType.SQLITE, mode.getDbType());;
		} catch (OptionException ex) {
			fail("Shouldn't fail here.");
		} 
	}

	@Test(expected=OptionException.class)
	public void testModeIncorrect() throws OptionException {
		String[] args = {"-m", "xxxx"};
		cmd.parseArguments(args);
	}
	
	@Test(expected=OptionException.class)
	public void testModeMultiple() throws OptionException {
		String[] args = {"-m", "xxxx", "xxxx", "xxxx"};
		cmd.parseArguments(args);
	}
	
	@Test
	public void testGetConfigurationFile() {
		//ExistingXmlFile.xml
		String[] args = {"-c", "./tests/sdb/config/ExistingXmlFile.xml"};
		try {
			boolean result = cmd.parseArguments(args);
			Assert.assertTrue(result);
			File file = cmd.getConfigurationFile();
			Assert.assertNotNull(file);
			Assert.assertTrue(file.exists());
		} catch (OptionException ex) {
			fail("Shouldn't fail here " + ex.getMessage());
		} 
	}
	
	@Test(expected=OptionException.class)
	public void testNonExistingConfigurationFile() throws OptionException {
		//NonExistingXmlFile.xml
		String[] args = {"-c", "./tests/sdb/config/NonExistingXmlFile.xml"};
		cmd.parseArguments(args);
	}
	
	@Test
	public void testGetOutputDb() throws OptionException {
		String[] args = {"-o", "OutputFileName.db"};
		boolean result = cmd.parseArguments(args);
		Assert.assertTrue(result);
		File file = cmd.getOutputDb();
		Assert.assertNotNull(file);
		
		Assert.assertTrue(cmd.failFast());
	}
	
	@Test
	public void testGetInputDb() {
		String[] args = {"-i", "./tests/sdb/config/ExistingInputFile.db"};
		try {
			boolean result = cmd.parseArguments(args);
			Assert.assertTrue(result);
			File file = cmd.getInputDb();
			Assert.assertNotNull(file);
			Assert.assertTrue(file.exists());
		} catch (OptionException ex) {
			fail("Shouldn't fail here " + ex.getMessage());
		} 
	}
	
	@Test
	public void testGetInputFiles() {
		String[] args = {"./tests/config/badSql.sql", "./tests/config/data.sql", "./tests/config/ced.cfg"};
		try {
			boolean result = cmd.parseArguments(args);
			Assert.assertTrue(result);
			List<File> files = new ArrayList<File>();
			files.addAll(cmd.getSQLFiles());
			files.addAll(cmd.getCedFiles());
			Assert.assertNotNull(files);
			Assert.assertTrue(files.size() == 3);
			Assert.assertEquals(new File("./tests/config/badSql.sql"), files.get(0));
			Assert.assertEquals(new File("./tests/config/data.sql"), files.get(1));
			Assert.assertEquals(new File("./tests/config/ced.cfg"), files.get(2));
			
			files = cmd.getSQLFiles();
	        Assert.assertNotNull(files);
	        Assert.assertTrue(files.size() == 2);
	        Assert.assertEquals(new File("./tests/config/badSql.sql"), files.get(0));
	        Assert.assertEquals(new File("./tests/config/data.sql"), files.get(1));
	        
	        files = cmd.getCedFiles();
           Assert.assertNotNull(files);
           Assert.assertTrue(files.size() == 1);
           Assert.assertEquals(new File("./tests/config/ced.cfg"), files.get(0));

		} catch (OptionException ex) {
			fail("Shouldn't fail here " + ex.getMessage());
		} 
	}
	@Test
	public void testPrintHelp() {
		cmd.printHelp();
		
		String help = output.toString();
		
		Assert.assertNotNull(help);
		Assert.assertTrue(help.startsWith("Usage"));
		Assert.assertTrue(help.contains("Options"));
	}

	@Test
	public void testPrintHeader() {
		cmd.printHeader();
		String header = output.toString();
		Assert.assertNotNull(header);
		
	}

	@Test
	public void testPrintFinish() {
		cmd.printFinish();
		String finish = output.toString();
		Assert.assertNotNull(finish);
	}

	@Test
	public void testDefaultPropertyFileGeneration() throws Exception {
		String defaultPropertiesFile =  getDefaultPropertiesFileAbsolutePath(cmd);
		File file = new File(defaultPropertiesFile);
		
		assertEquals("sdb.properties", file.getName());
		assertEquals("config", file.getParentFile().getName());
		Assert.assertTrue(file.getAbsolutePath() + "<>"  + cmd.getInstallationDirectory().getAbsolutePath(), 
		file.getAbsolutePath().toLowerCase().startsWith(cmd.getInstallationDirectory().getAbsolutePath().toLowerCase()));
	}
	
	private String getDefaultPropertiesFileAbsolutePath(CmdLinev2 cmd) {
		return new File(cmd.getDefaultPropertiesFileName()).getAbsolutePath();
	}

	@Test
	public void testKeepGoing() throws OptionException {
		String[] args = {"-k"};
		boolean result = cmd.parseArguments(args);
		Assert.assertFalse(result);
		Assert.assertFalse(cmd.failFast());
	}
	
	@Test
	public void testDebug() throws OptionException {
		String[] args = {"-d"};
		boolean result = cmd.parseArguments(args);
		Assert.assertFalse(result);
		Assert.assertTrue(cmd.isDebugEnabled());
	}

}
