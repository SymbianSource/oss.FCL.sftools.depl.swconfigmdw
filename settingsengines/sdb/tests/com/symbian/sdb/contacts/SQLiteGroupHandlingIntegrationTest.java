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

package com.symbian.sdb.contacts;

import java.io.File;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

import junit.framework.Assert;
import junit.framework.JUnit4TestAdapter;

import org.apache.commons.cli2.OptionException;
import org.junit.BeforeClass;
import org.junit.Test;

import com.symbian.sdb.cmd.CmdLinev2;
import com.symbian.sdb.database.DBManager;
import com.symbian.sdb.database.SqlExecuter;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.mode.DBType;
import com.symbian.sdb.mode.flow.ContactsFlow;
import com.symbian.sdb.mode.flow.IFlow;
import com.symbian.sdb.mode.flow.ced.SdbFlowException;
import com.symbian.sdb.settings.Settings;
import com.symbian.sdb.util.FileUtil;


/**
 * @author jamesclark
 *
 */
public class SQLiteGroupHandlingIntegrationTest {

//	/*
//	 * The aim of this test is to exercise SDB and validate whether the group
//	 * handling is correct.
//	 * It consists of three "runs" each with a validation stage.
//	 * 
//	 * Stage 1
//	 * Add a contact with a basic group
//	 * Validate that template, contact and group have been added to contacts table.
//	 * Validate that the groups table contains the group <> contact link
//	 * 
//	 * Stage 2
//	 * Add a second contact to a different group
//	 * Validate that new contact and group have been added to contacts table.
//	 * Validate that the groups table contains the new group <> contact link
//	 * 
//	 * Stage 3
//	 * Add a third contact to the group added in run 1
//	 * Validate that new contact has been added to contacts table (but no additional group).
//	 * Validate that the groups table contains the new group <> contact link
//	 */
//	
//	//TODO run: -m sqlite.contacts -o contacts.db "C:\Documents and Settings\jamesclark\Desktop\Clarke James.vcf" -g fudge -t "C:\Documents and Settings\jamesclark\Desktop\cntmodel.rss"
//	//TODO run: -m sqlite.contacts -i contacts.db -o contactMod.db "C:\Documents and Settings\jamesclark\Desktop\Clarke James1.vcf" -g packer -t "C:\Documents and Settings\jamesclark\Desktop\cntmodel.rss"
//	//TODO run: -m sqlite.contacts -i contactMod.db -o contactMod2.db "C:\Documents and Settings\jamesclark\Desktop\Clarke James.vcf" -g packer -t "C:\Documents and Settings\jamesclark\Desktop\cntmodel.rss"
//	//TODO verify DBs
//	
//	// Stage 1
//	private final File run1ContactsDB = new File("tests//config//groupITests//contacts.db");
//	private final File cntModelTemplate = new File("tests//config//groupITests//cntmodel.rss");
//	private final File vCard1 = new File("tests//config//groupITests//contact1.vcf");
//	private final String group1Label = "group1";
//	
//	// Stage 2
//	private final File run2ContactsDB = new File("tests//config//groupITests//contactsMod.db");
//	private final File vCard2 = new File("tests//config//groupITests//contact2.vcf");
//	private final String group2Label = "group2";
//	
//	// Stage 3
//	private final File run3ContactsDB = new File("tests//config//groupITests//contactsMod2.db");
//	private final File vCard3 = new File("tests//config//groupITests//contact3.vcf");
//	
//	private final File vCard4 = new File("tests//config//groupITests//contact4.vcf");
//	private final File vCard5 = new File("tests//config//groupITests//contact5.vcf");
//	
//	@BeforeClass
//	public static void setSystemProperties() {
//		System.setProperty("org.sqlite.lib.path", "lib/");
//		System.setProperty("sdb.schema.location.1.0", "config//sdb.xsd");
//		System.setProperty("sdb.schema.location.2.0", "config//sdb2.0.xsd");
//		System.setProperty("sdb.contacts.configuration", "config/contacts.xml");
//	}
//	
//	@Test
//	public void testCreateAndUpdateDB(){
//		stage1();
//		stage2();
//		stage3();
//	}
//	
//	@Test
//	public void testCreateAndUpdateDBWithMultipleVCards(){
//		stage1();
//		stage2();
//
//		String[] args = {"-m", "sqlite.contacts", 
//				"-t", cntModelTemplate.getAbsolutePath(), 
//				"-i", run2ContactsDB.getAbsolutePath(),
//				"-o", run3ContactsDB.getAbsolutePath(),
//				"-g", group1Label,
//				vCard3.getAbsolutePath(),
//				vCard4.getAbsolutePath(),
//				vCard5.getAbsolutePath()};
//		try {
//			CmdLinev2 cmd = new CmdLinev2();
//			boolean result = cmd.parseArguments(args);
//			new Settings().configure(cmd);	
//			ContactsFlow flow = new ContactsFlow(new DatabaseManager(), new SqlExecuter());
//			flow.setTemplateManager(SQLiteContactDatabaseCreationIntegrationTest.createMockTemplateManager());
//			flow.validateOptions(cmd);
//			flow.start(cmd);
//		}
//		catch (SdbFlowException e) {
//
//		} catch (OptionException e) {
//			Assert.fail("Exception thrown: "+e.getLocalizedMessage());
//		} catch (SDBValidationException e) {
//			Assert.fail("Exception thrown: "+e.getLocalizedMessage());
//		} catch (SDBExecutionException e) {
//			Assert.fail("Exception thrown: "+e.getLocalizedMessage());
//		}
//		checkDatabase(run3ContactsDB, 8, 5);
//	}
//	
//	@Test
//	public void testAddMultipleToGroup(){
//		String[] args = {"-m", "sqlite.contacts", 
//				"-t", cntModelTemplate.getAbsolutePath(), 
//				"-o", run1ContactsDB.getAbsolutePath(),
//				"-g", group1Label,
//				vCard4.getAbsolutePath(),
//				vCard5.getAbsolutePath()};
//		try {
//			CmdLinev2 cmd = new CmdLinev2();
//			boolean result = cmd.parseArguments(args);
//			new Settings().configure(cmd);	
//			ContactsFlow flow = new ContactsFlow(new DatabaseManager(), new SqlExecuter());
//			flow.setTemplateManager(SQLiteContactDatabaseCreationIntegrationTest.createMockTemplateManager());
//			flow.validateOptions(cmd);
//			flow.start(cmd);
//		}
//		catch (SdbFlowException e) {
//
//		} catch (OptionException e) {
//			Assert.fail("Exception thrown: "+e.getLocalizedMessage());
//		} catch (SDBValidationException e) {
//			Assert.fail("Exception thrown: "+e.getLocalizedMessage());
//		} catch (SDBExecutionException e) {
//			Assert.fail("Exception thrown: "+e.getLocalizedMessage());
//		}
//		checkDatabase(run1ContactsDB, 4, 2);
//		run1ContactsDB.delete();
//	}
//	
//	@Test
//	public void testNoGroupAdded(){
//        
//		String[] args = {"-m", "sqlite.contacts", 
//				"-t", cntModelTemplate.getAbsolutePath(), 
//				"-o", run1ContactsDB.getAbsolutePath(),
//				vCard1.getAbsolutePath()};
//		try {
//			CmdLinev2 cmd = new CmdLinev2();
//			boolean result = cmd.parseArguments(args);
//			new Settings().configure(cmd);	
//			ContactsFlow flow = new ContactsFlow(new DatabaseManager(), new SqlExecuter());
//			flow.setTemplateManager(SQLiteContactDatabaseCreationIntegrationTest.createMockTemplateManager());
//			flow.validateOptions(cmd);
//			flow.start(cmd);
//		}
//		catch (SdbFlowException e) {
//
//		} catch (OptionException e) {
//			Assert.fail("Exception thrown: "+e.getLocalizedMessage());
//		} catch (SDBValidationException e) {
//			Assert.fail("Exception thrown: "+e.getLocalizedMessage());
//		} catch (SDBExecutionException e) {
//			Assert.fail("Exception thrown: "+e.getLocalizedMessage());
//		}
//		checkDatabase(run1ContactsDB, 2, 0);
//		run1ContactsDB.delete();
//	}
//	
//	public void stage1(){
//        
//		String[] args = {"-m", "sqlite.contacts", 
//				"-t", cntModelTemplate.getAbsolutePath(), 
//				"-o", run1ContactsDB.getAbsolutePath(),
//				"-g", group1Label,
//				vCard1.getAbsolutePath()};
//		try {
//			CmdLinev2 cmd = new CmdLinev2();
//			boolean result = cmd.parseArguments(args);
//			new Settings().configure(cmd);	
//			ContactsFlow flow = new ContactsFlow(new DatabaseManager(), new SqlExecuter());
//			flow.setTemplateManager(SQLiteContactDatabaseCreationIntegrationTest.createMockTemplateManager());
//			flow.validateOptions(cmd);
//			flow.start(cmd);
//		}
//		catch (SdbFlowException e) {
//
//		} catch (OptionException e) {
//			Assert.fail("Exception thrown: "+e.getLocalizedMessage());
//		} catch (SDBValidationException e) {
//			Assert.fail("Exception thrown: "+e.getLocalizedMessage());
//		} catch (SDBExecutionException e) {
//			Assert.fail("Exception thrown: "+e.getLocalizedMessage());
//		}
//		checkDatabase(run1ContactsDB, 3, 1);
//	}
//	
//	public void stage2(){
//        
//		String[] args = {"-m", "sqlite.contacts", 
//				"-t", cntModelTemplate.getAbsolutePath(), 
//				"-i", run1ContactsDB.getAbsolutePath(),
//				"-o", run2ContactsDB.getAbsolutePath(),
//				"-g", group2Label,
//				vCard2.getAbsolutePath()};
//		try {
//		    CmdLinev2 cmd = new CmdLinev2();
//			boolean result = cmd.parseArguments(args);
//			new Settings().configure(cmd);	
//			ContactsFlow flow = new ContactsFlow(new DatabaseManager(), new SqlExecuter());
//			flow.setTemplateManager(SQLiteContactDatabaseCreationIntegrationTest.createMockTemplateManager());
//			flow.validateOptions(cmd);
//			flow.start(cmd);
//		}
//		catch (SdbFlowException e) {
//
//		} catch (OptionException e) {
//			Assert.fail("Exception thrown: "+e.getLocalizedMessage());
//		} catch (SDBValidationException e) {
//			Assert.fail("Exception thrown: "+e.getLocalizedMessage());
//		} catch (SDBExecutionException e) {
//			Assert.fail("Exception thrown: "+e.getLocalizedMessage());
//		}
//		checkDatabase(run2ContactsDB, 5, 2);
//	}
//	
//	public void stage3(){
//        
//		String[] args = {"-m", "sqlite.contacts", 
//				"-t", cntModelTemplate.getAbsolutePath(), 
//				"-i", run2ContactsDB.getAbsolutePath(),
//				"-o", run3ContactsDB.getAbsolutePath(),
//				"-g", group1Label,
//				vCard3.getAbsolutePath()};
//		try {
//			CmdLinev2 cmd = new CmdLinev2();
//			boolean result = cmd.parseArguments(args);
//			new Settings().configure(cmd);	
//			ContactsFlow flow = new ContactsFlow(new DatabaseManager(), new SqlExecuter());
//			flow.setTemplateManager(SQLiteContactDatabaseCreationIntegrationTest.createMockTemplateManager());
//			flow.validateOptions(cmd);
//			flow.start(cmd);
//		}
//		catch (SdbFlowException e) {
//
//		} catch (OptionException e) {
//			Assert.fail("Exception thrown: "+e.getLocalizedMessage());
//		} catch (SDBValidationException e) {
//			Assert.fail("Exception thrown: "+e.getLocalizedMessage());
//		} catch (SDBExecutionException e) {
//			Assert.fail("Exception thrown: "+e.getLocalizedMessage());
//		}
//		checkDatabase(run3ContactsDB, 6, 3);
//	}
//
//	public void checkDatabase(File dbName, int contactCount, int groupLinkCount) {	
//		DatabaseManager dbm = new DatabaseManager();
//		Connection connection = null;
//		try {
//			dbm.openConnection(DBType.SQLITE, dbName.getAbsolutePath());
//			connection = dbm.getConnection();
//
//			// Check the security table
//			Assert.assertEquals("Contact table not updated with expected number of contacts.", contactCount, countItemsIn("contact", connection));
//			Assert.assertEquals("Groups table not updated with expected number of contacts.", groupLinkCount, countItemsIn("groups", connection));
//			
//	        	
//		} catch (SDBExecutionException e) {
//			Assert.fail(e.getMessage());
//		}
//		finally{
//			FileUtil.closeSilently(connection);
//		}
//	}
//
//	private int countItemsIn(String table, Connection connection) {
//		try {
//			PreparedStatement defaultStatement1 = connection.prepareStatement("select count(*) from "+table+";");
//			ResultSet result1 = defaultStatement1.executeQuery();
//			result1.next();
//			
//			return result1.getInt(1);
//			
//		} catch (SQLException e) {
//			Assert.fail(e.getMessage());
//		}
//		return -Integer.MIN_VALUE;
//	}
//
	@Test
	public void testname() throws Exception {
		int a;
	}
	public static junit.framework.Test suite() {
        return new JUnit4TestAdapter(SQLiteGroupHandlingIntegrationTest.class); 
    }
    
}
