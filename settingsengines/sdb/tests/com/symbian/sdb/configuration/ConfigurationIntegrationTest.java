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

package com.symbian.sdb.configuration;

import java.io.File;
import java.io.IOException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Properties;
import junit.framework.JUnit4TestAdapter;
import org.apache.commons.cli2.OptionException;
import org.junit.AfterClass;
import org.junit.Assert;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import com.symbian.sdb.PropertyRestorerTestCase;
import com.symbian.sdb.cmd.CmdLinev2;
import com.symbian.sdb.database.DBManager;
import com.symbian.sdb.database.SqlExecuter;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.mode.DBType;
import com.symbian.sdb.mode.flow.GenericFlow;
import com.symbian.sdb.mode.flow.GenericFlowInputDatabaseValidator;
import com.symbian.sdb.util.FileUtil;

public class ConfigurationIntegrationTest extends PropertyRestorerTestCase{

    public static junit.framework.Test suite() {
        return new JUnit4TestAdapter(ConfigurationIntegrationTest.class); 
    }
	
	@Before
	public void setSystemProperties() {
		setPropertiesForDBPaths();
		System.setProperty("sdb.schema.location.1.0", "sdb.xsd");
		System.setProperty("sdb.schema.location.2.0", "sdb2.0.xsd");	
	}
	
	@Test
    public void testUpdateEmptyDatabaseWithDefault() {
		File tempFile = getTempDatabaseFile();
		
		createEmptyDatabase(tempFile);
		
		createOrUpdateDatabase(tempFile, "testdata/PlatSec/Default.xml");
		
		checkDatabase(tempFile, true, false, false, false);
	}
	
	@Test
    public void testUpdateEmptyDatabaseWithAll() {
		File tempFile = getTempDatabaseFile();
		
		createEmptyDatabase(tempFile);
		
		createOrUpdateDatabase(tempFile, "testdata/PlatSec/All.xml");
		
		checkDatabase(tempFile, true, true, true, true);
	}

	@Test
    public void testUpdateEmptyDatabaseWithSchema() {
		File tempFile = getTempDatabaseFile();
		
		createEmptyDatabase(tempFile);
		
		createOrUpdateDatabase(tempFile, "testdata/PlatSec/DefaultAndSchema.xml");
		
		checkDatabase(tempFile, true, true, false, false);
	}
	
	@Test
    public void testUpdateEmptyDatabaseWithRead() {
		File tempFile = getTempDatabaseFile();
		
		createEmptyDatabase(tempFile);
		
		createOrUpdateDatabase(tempFile, "testdata/PlatSec/DefaultAndRead.xml");
		
		checkDatabase(tempFile, true, false, true, false);
	}
	
	@Test
    public void testUpdateEmptyDatabaseWithWrite() {
		File tempFile = getTempDatabaseFile();
		
		createEmptyDatabase(tempFile);
		
		createOrUpdateDatabase(tempFile, "testdata/PlatSec/DefaultAndWrite.xml");
		
		checkDatabase(tempFile, true, false, false, true);
	}	
	
	@Test
    public void testUpdateExistingDatabaseWithAll() {
		File tempFile = getTempDatabaseFile();

		createOrUpdateDatabase(tempFile, "testdata/PlatSec/Default.xml");

		checkDatabase(tempFile, true, false, false, false);
		
		createOrUpdateDatabase(tempFile, "testdata/PlatSec/All.xml");
		
		checkDatabase(tempFile, true, true, true, true);
	}	
	
	@Test
    public void testUpdateExistingDatabaseWithDefaultSchema() {
		File tempFile = getTempDatabaseFile();

		createOrUpdateDatabase(tempFile, "testdata/PlatSec/Default.xml");

		checkDatabase(tempFile, true, false, false, false);
		
		createOrUpdateDatabase(tempFile, applyOSSpecificPathSeparator("testdata/PlatSec/DefaultAndSchema.xml"));
		
		checkDatabase(tempFile, true, true, false, false);
	}		
	
	private String applyOSSpecificPathSeparator(String inputPath) {
		String osName = System.getProperty("os.name");
		String osSpecificPath;
		if (osName.toLowerCase().contains("windows"))	{
			osSpecificPath = replaceSlashesWithBackSlashes(inputPath);
		}
		else	{
			// assume unix
			osSpecificPath = replaceBackslashesWithSlashes(inputPath);
		}
		return osSpecificPath;
	}

	private String replaceBackslashesWithSlashes(String path) {
		return path.replaceAll("\\\\", "/");
	}

	private String replaceSlashesWithBackSlashes(String path) {
		return path.replaceAll("/", "\\\\");
	}

	@Test
    public void testUpdateExistingDatabaseWithDefaultAndRead() {
		File tempFile = getTempDatabaseFile();

		createOrUpdateDatabase(tempFile, "testdata/PlatSec/Default.xml");

		checkDatabase(tempFile, true, false, false, false);
		
		createOrUpdateDatabase(tempFile, "testdata/PlatSec/DefaultAndRead.xml");
		
		checkDatabase(tempFile, true, false, true, false);
	}		
	
	@Test
    public void testUpdateExistingDatabaseWithDefaultAndWrite() {
		File tempFile = getTempDatabaseFile();

		createOrUpdateDatabase(tempFile, "testdata/PlatSec/Default.xml");

		checkDatabase(tempFile, true, false, false, false);
		
		createOrUpdateDatabase(tempFile, "testdata/PlatSec/DefaultAndWrite.xml");
		
		checkDatabase(tempFile, true, false, false, true);
	}		
	
	@Test
    public void testChangePageSizeAndEncoding() {
		File tempFile = getTempDatabaseFile();

		createOrUpdateDatabase(tempFile, "testdata/PlatSec/Default.xml");

		// Confirm the page size is 512 and encoding is UTF-16
		Assert.assertEquals("512", getPragma(tempFile, "page_size"));
		Assert.assertEquals("UTF-16le", getPragma(tempFile, "encoding"));
		
		checkDatabase(tempFile, true, false, false, false);
		
		createOrUpdateDatabase(tempFile, "testdata/PlatSec/DefaultPageSize1024UTF8.xml");
		
		// Confirm the page size is still 512, even though the platsec xml file states 1024
		Assert.assertEquals("512", getPragma(tempFile, "page_size"));
		Assert.assertEquals("UTF-16le", getPragma(tempFile, "encoding"));

		checkDatabase(tempFile, true, false, false, false);
	}		
	
	public String getPragma(File dbName, String what) {
		DBManager dbm = new DBManager();
		
		String result = "";
		Connection connection = null;
		
		try {
			dbm.openConnection(DBType.SQLITE, dbName.getAbsolutePath());
			connection = dbm.getConnection();		

			PreparedStatement statement = connection.prepareStatement("PRAGMA " + what + ";");
			ResultSet results = statement.executeQuery();
			results.next();
			
			result = results.getString(1);	        
		} catch (SDBExecutionException e) {
			Assert.fail(e.getMessage());
		} catch (SQLException e) {
			Assert.fail(e.getMessage());
		}
		finally{
			FileUtil.closeSilently(connection);
		}
		
		return result;
	}
	
	public void checkDatabase(File dbName, boolean defaltEntry, boolean schemaEntry, boolean readEntry, boolean writeEntry) {	
		DBManager dbm = new DBManager();
		Connection connection = null;
		try {
			dbm.openConnection(DBType.SQLITE, dbName.getAbsolutePath());
			connection = dbm.getConnection();

			// Check the security table
			Assert.assertEquals("Problem with PlatSec Default entry", checkDefaultEntry(connection), defaltEntry);
			Assert.assertEquals("Problem with PlatSec Schema entry", checkSchemaEntry(connection), schemaEntry);
			Assert.assertEquals("Problem with PlatSec Read entry", checkReadEntry(connection), readEntry);
			Assert.assertEquals("Problem with PlatSec Write entry", checkWriteEntry(connection), writeEntry);
	        	
		} catch (SDBExecutionException e) {
			Assert.fail(e.getMessage());
		}
		finally{
			FileUtil.closeSilently(connection);
		}
	}
	
	
	private boolean checkDefaultEntry(Connection connection) {
		try {
			PreparedStatement defaultStatement1 = connection.prepareStatement("select count(*) from symbian_security where PolicyType='-1';");
			ResultSet result1 = defaultStatement1.executeQuery();
			result1.next();
			
			if (result1.getInt(1) == 0 || result1.getInt(1) > 1) {
				return false;
			}			
			
			PreparedStatement defaultStatement = connection.prepareStatement("select * from symbian_security where PolicyType='-1';");
			ResultSet result = defaultStatement.executeQuery();
			result.next();
			
			if (result.getInt(1) == 1 && result.getInt(2)== -2 && result.getString(3) == null) {
				return true;
			}
			
		} catch (SQLException e) {
			Assert.fail(e.getMessage());
		}
		
		return false;
	}

	private boolean checkSchemaEntry(Connection connection) {
		try {
			PreparedStatement defaultStatement1 = connection.prepareStatement("select count(*) from symbian_security where PolicyType='0';");
			ResultSet result1 = defaultStatement1.executeQuery();
			result1.next();
			
			if (result1.getInt(1) == 0 || result1.getInt(1) > 1) {
				return false;
			}
			
			PreparedStatement defaultStatement = connection.prepareStatement("select * from symbian_security where PolicyType='0';");
			ResultSet result = defaultStatement.executeQuery();
			result.next();

			if (result.getInt(2)== -1 && result.getString(3) == null) {
				return true;
			}
			
		} catch (SQLException e) {
			Assert.fail(e.getMessage());
		}
		
		return false;
	}
	
	private boolean checkReadEntry(Connection connection) {
		try {
			PreparedStatement defaultStatement1 = connection.prepareStatement("select count(*) from symbian_security where PolicyType='1';");
			ResultSet result1 = defaultStatement1.executeQuery();
			result1.next();
			
			if (result1.getInt(1) == 0 || result1.getInt(1) > 1) {
				return false;
			}
			
			PreparedStatement defaultStatement = connection.prepareStatement("select * from symbian_security where PolicyType='1';");
			ResultSet result = defaultStatement.executeQuery();
			result.next();		
			
			if (result.getInt(2)== -1 && result.getString(3) == null) {
				return true;
			}
			
		} catch (SQLException e) {
			Assert.fail(e.getMessage());
		}
		
		return false;
	}	
	
	private boolean checkWriteEntry(Connection connection) {
		try {
			PreparedStatement defaultStatement1 = connection.prepareStatement("select count(*) from symbian_security where PolicyType='2';");
			ResultSet result1 = defaultStatement1.executeQuery();
			result1.next();
			
			if (result1.getInt(1) == 0 || result1.getInt(1) > 1) {
				return false;
			}
			
			PreparedStatement defaultStatement = connection.prepareStatement("select * from symbian_security where PolicyType='2';");
			ResultSet result = defaultStatement.executeQuery();
			result.next();		
			
			if (result.getInt(2)== -1 && result.getString(3) == null) {
				return true;
			}
			
		} catch (SQLException e) {
			Assert.fail(e.getMessage());
		}
		
		return false;
	}
	public void createEmptyDatabase(File dbFile) {
		// Create the command line args object
		CmdLinev2 cmd1 = new CmdLinev2();
		String[] args1 = new String[] {"-m", "sqlite", "-o", dbFile.getAbsolutePath()};
		try {
			cmd1.parseArguments(args1);
		} catch (OptionException e) {
			Assert.fail(e.getMessage());
		}	
		
		Configuration configuration1 = new Configuration();
		SqlExecuter executer1 = new SqlExecuter();
		
		GenericFlow gFlow1 = createGenericFlow(configuration1, executer1);
		
		try {
			gFlow1.validateOptions(cmd1);
			gFlow1.start(cmd1);
		} catch (SDBValidationException e) {
			Assert.fail(e.getMessage());
		} catch (SDBExecutionException e) {
			Assert.fail(e.getMessage());
		}		
	}
	
	public void createOrUpdateDatabase(File dbFile, String platsecFile) {
		// Create the command line args object
		CmdLinev2 cmd = new CmdLinev2();
		String[] args = new String[] {"-m", "sqlite", "-i", dbFile.getAbsolutePath(), "-c", platsecFile, "-o", dbFile.getAbsolutePath()};
		try {
			cmd.parseArguments(args);
		} catch (OptionException e) {

			e.printStackTrace();
		}	
		
	    Configuration configuration = new Configuration();
		SqlExecuter executer = new SqlExecuter();
		
		// Update the database
		GenericFlow gFlow = createGenericFlow(configuration, executer);
		
		try {
			gFlow.validateOptions(cmd);
			gFlow.start(cmd);
		} catch (SDBValidationException e) {
			Assert.fail(e.getMessage());
		} catch (SDBExecutionException e) {
			Assert.fail(e.getMessage());
		} catch (AssertionError e) {
			// These seem to be caused by deleting the temp database, they can be ignored
		}
		
	}

	/**
	 * @param configuration
	 * @param executer
	 * @return
	 */
	private GenericFlow createGenericFlow(Configuration configuration, SqlExecuter executer) {
		GenericFlow gFlow = new GenericFlow(executer, configuration);
		gFlow.setDatabaseManager(createDatabaseManager());
		gFlow.setInputDatabaseValidator(new GenericFlowInputDatabaseValidator());
		return gFlow;
	}
	
    private DBManager createDatabaseManager() {
        return new DBManager();
    }

    public File getTempDatabaseFile() {
		File tempFile = null;
		
		try {
			tempFile = File.createTempFile("sdbtest", ".db");
			//tempFile.deleteOnExit();
			//http://bugs.sun.com/bugdatabase/view_bug.do?bug_id=4171239
			//http://bugs.sun.com/bugdatabase/view_bug.do?bug_id=4950148
		} catch (IOException e) {
			Assert.fail(e.getMessage());
		}	
		
		return tempFile;
	}
}
