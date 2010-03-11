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

package com.symbian.sdb.contacts.template;

import java.io.File;
import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import junit.framework.Assert;

import org.apache.commons.cli2.OptionException;
import org.apache.commons.io.FileUtils;
import org.junit.Before;
import org.junit.Test;

import com.symbian.sdb.cmd.CmdLinev2;
import com.symbian.sdb.contacts.BaseIntegrationTestCase;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.mode.DBType;
import com.symbian.sdb.mode.flow.IFlow;
import com.symbian.sdb.mode.flow.WorkflowFactory;
import com.symbian.sdb.mode.flow.ced.SdbFlowException;
import com.symbian.sdb.settings.Settings;
import com.symbian.sdb.util.FileUtil;

/**
 * @author jamesclark
 * 
 */
public class BasicDBMSContactsDBComparisonTest extends BaseIntegrationTestCase  {

    protected WorkflowFactory workflowFactory;
    
    protected static File resources = new File("tests/config/template_itests/");

	protected static String getPathTo(String resource) {
		return FileUtil.concatFilePath(resources.getAbsolutePath(), resource);
	}
	
	/**
	 * Running this file as a Java application will generate dbs for 91->94 for checking on the emulator
	 * 
	 * @param args
	 */
	public static void main(String[] args){
		new BasicDBMSContactsDBComparisonTest().generateDBsForAllOSVersions();
	}
	
	public void generateDBsForAllOSVersions(){
		List<TestConfig> testConfig = new ArrayList<TestConfig>();
		try {
			File vcard = new File("testdata/contacts/vcard/vcard2.vcf");
			testConfig.add(new TestConfig(new File(getPathTo("91ui.rss")), new File(getPathTo("91.cdb")), new File("DBS_100065FF_Contacts91.cdb"), vcard));
			testConfig.add(new TestConfig(new File(getPathTo("92ui.rss")), new File(getPathTo("92.cdb")), new File("DBS_100065FF_Contacts92.cdb"), vcard));
			testConfig.add(new TestConfig(new File(getPathTo("93ui.rss")), new File(getPathTo("93.cdb")), new File("DBS_100065FF_Contacts93.cdb"), vcard));
			testConfig.add(new TestConfig(new File(getPathTo("94ui.rss")), new File(getPathTo("94.cdb")), new File("DBS_100065FF_Contacts94.cdb"), vcard));
		} catch (IOException e) {
			Assert.fail(e.getLocalizedMessage());
		}
		
		for(TestConfig test: testConfig){
			runContactsFlow(test);
			System.out.println("Generated DB: "+test.getGenDBPath());
		}
	}

	@Test
	public void testComparison() throws Exception {

		// copy the DBs to get over the read-only block
		//
		File db1_org = new File(getPathTo("testcheck/big_contact.cdb"));
		File db1_new = File.createTempFile("db1", "db");
		FileUtils.copyFile(db1_org, db1_new);

		File db2_org = new File(getPathTo("testcheck/big_contact2.cdb"));
		File db2_new = File.createTempFile("db2", "db");
		FileUtils.copyFile(db2_org, db2_new);

		TestConfig test = new TestConfig(new File(getPathTo("temp.rss")), db1_new, db2_new);

		Connection valDBCon = getDBMSConnection(test.getValidDBPath(), null);
		Connection genDBCon = getDBMSConnection(test.getGenDBPath(), null);

		compareDBContactTable(valDBCon, genDBCon, -1);
		compareDBIdentityTable(valDBCon, genDBCon, -1);
		compareDBPhoneTable(valDBCon, valDBCon, -1);
		compareDBEmailTable(valDBCon, valDBCon, -1);
		compareDBGroupTable(valDBCon, valDBCon, -1);
		compareDBGroups2Table(valDBCon, valDBCon, -1);
		compareDBSyncTable(valDBCon, valDBCon, -1);
		compareDBPreferencesTable(valDBCon, genDBCon);
	}

	void compareDBContactTable(Connection validDB, Connection generatedDB, int contactID) throws SQLException {
		String query = "select * from CONTACTS";
		if (contactID != -1) {
			query += " where CM_Id = " + contactID;
		}

		PreparedStatement validDBContactsQuery = validDB.prepareStatement(query);
		validDBContactsQuery.execute();
		ResultSet validDBRS = validDBContactsQuery.getResultSet();

		PreparedStatement generatedDBContactsQuery = generatedDB.prepareStatement(query);
		generatedDBContactsQuery.execute();
		ResultSet generatedDBRS = generatedDBContactsQuery.getResultSet();

		while (validDBRS.next()) {
			int id = validDBRS.getInt(1);
			Assert.assertTrue("The number of results returned don't match", generatedDBRS.next());
			Assert.assertEquals("CM_ID not equal [id="+id+"]", validDBRS.getInt(1), generatedDBRS.getInt(1));
			Assert.assertEquals("CM_Type not equal [id="+id+"]", validDBRS.getInt(2), generatedDBRS.getInt(2));
			Assert.assertEquals("CM_PrefTemplateRefId not equal [id="+id+"]", validDBRS.getInt(3), generatedDBRS.getInt(3));
			// These three are not expected to be equal.
			// Assert.assertEquals("CM_UidString not equal",
			// validDBRS.getString(4),generatedDBRS.getString(4));
			// Assert.assertEquals("CM_Last_Modified not equal",
			// validDBRS.getDate(5),generatedDBRS.getDate(5));
			// Assert.assertEquals("CM_ContactCreationDate not equal",
			// validDBRS.getDate(6),generatedDBRS.getDate(6));
			Assert.assertEquals("CM_Attributes not equal [id="+id+"]", validDBRS.getLong(7), generatedDBRS.getLong(7));
			Assert.assertEquals("CM_ReplicationCount not equal [id="+id+"]", validDBRS.getLong(8), generatedDBRS.getLong(8));
			Assert.assertTrue("CM_Header not equal [id="+id+"]", Arrays.equals(validDBRS.getBytes(9), generatedDBRS.getBytes(9)));
			Assert.assertTrue("CM_Textblob not equal [id="+id+"]", Arrays.equals(validDBRS.getBytes(10), generatedDBRS.getBytes(10)));
			// Assert.assertEquals("CM_SearchableText not equal",
			// validDBRS.getString(11),generatedDBRS.getString(11));
		}
	}

	protected void compareDBIdentityTable(Connection validDB, Connection generatedDB, int contactID) throws SQLException {
		String query = "select * from IDENTITYTABLE";
		if (contactID != -1) {
			query += " where Parent_CMID = " + contactID;
		}

		PreparedStatement validDBIdentityQuery = validDB.prepareStatement(query);
		validDBIdentityQuery.execute();
		ResultSet validIdentityDBRS = validDBIdentityQuery.getResultSet();

		PreparedStatement generatedDBIdentityQuery = generatedDB.prepareStatement(query);
		generatedDBIdentityQuery.execute();
		ResultSet generatedIdentityDBRS = generatedDBIdentityQuery.getResultSet();

		while (validIdentityDBRS.next()) {
			Assert.assertTrue("The number of results returned don't match", generatedIdentityDBRS.next());
			Assert.assertEquals("Parent_CMID not equal", validIdentityDBRS.getInt(1), generatedIdentityDBRS.getInt(1));
			Assert.assertEquals("CM_FirstName not equal", validIdentityDBRS.getString(2), generatedIdentityDBRS.getString(2));
			Assert.assertEquals("CM_LastName not equal", validIdentityDBRS.getString(3), generatedIdentityDBRS.getString(3));
			Assert.assertEquals("CM_CompanyName not equal", validIdentityDBRS.getString(4), generatedIdentityDBRS.getString(4));
			Assert.assertTrue("CM_Type not equal", Arrays.equals(validIdentityDBRS.getBytes(5), generatedIdentityDBRS.getBytes(5)));
			Assert.assertEquals("CM_Attributes not equal", validIdentityDBRS.getLong(6), generatedIdentityDBRS.getLong(6));
			Assert.assertEquals("CM_HintField not equal", validIdentityDBRS.getInt(7), generatedIdentityDBRS.getInt(7));
			Assert.assertEquals("CM_ExtHintField not equal", validIdentityDBRS.getLong(8), generatedIdentityDBRS.getLong(8));
			Assert.assertEquals("CM_FirstNmPrn not equal", validIdentityDBRS.getString(9), generatedIdentityDBRS.getString(9));
			Assert.assertEquals("CM_LastNmPrn not equal", validIdentityDBRS.getString(10), generatedIdentityDBRS.getString(10));
			Assert.assertEquals("CM_CompanyNmPrn not equal", validIdentityDBRS.getString(11), generatedIdentityDBRS.getString(11));
		}
	}

	protected void compareDBPhoneTable(Connection validDB, Connection generatedDB, int contactID) throws SQLException {
		String query = "select * from Phone";
		if (contactID != -1) {
			query += " where CM_ID = " + contactID;
		}

		PreparedStatement validDBPhoneQuery = validDB.prepareStatement(query);
		validDBPhoneQuery.execute();
		ResultSet validPhoneDBRS = validDBPhoneQuery.getResultSet();

		PreparedStatement generatedDBPhoneQuery = generatedDB.prepareStatement(query);
		generatedDBPhoneQuery.execute();
		ResultSet generatedPhoneDBRS = generatedDBPhoneQuery.getResultSet();

		while (validPhoneDBRS.next()) {
			Assert.assertTrue("The number of results returned don't match", generatedPhoneDBRS.next());
			Assert.assertEquals("CM_ID not equal", validPhoneDBRS.getInt(1), generatedPhoneDBRS.getInt(1));
			Assert.assertEquals("CM_PhoneMatching not equal", validPhoneDBRS.getInt(2), generatedPhoneDBRS.getInt(2));
			Assert.assertEquals("CM_ExtendedPhoneMatching not equal", validPhoneDBRS.getInt(3), generatedPhoneDBRS.getInt(3));
		}
	}

	protected void compareDBEmailTable(Connection validDB, Connection generatedDB, int contactID) throws SQLException {
		String query = "select * from Emailtable";
		if (contactID != -1) {
			query += " where EmailParent_CMID = " + contactID;
		}

		PreparedStatement validDBEmailQuery = validDB.prepareStatement(query);
		validDBEmailQuery.execute();
		ResultSet validEmailDBRS = validDBEmailQuery.getResultSet();

		PreparedStatement generatedDBEmailQuery = generatedDB.prepareStatement(query);
		generatedDBEmailQuery.execute();
		ResultSet generatedEmailDBRS = generatedDBEmailQuery.getResultSet();

		while (validEmailDBRS.next()) {
			Assert.assertTrue("The number of results returned don't match", generatedEmailDBRS.next());
			Assert.assertEquals("Email_FieldId not equal", validEmailDBRS.getInt(1), generatedEmailDBRS.getInt(1));
			Assert.assertEquals("Email_Parent_CMID not equal", validEmailDBRS.getInt(2), generatedEmailDBRS.getInt(2));
			Assert.assertEquals("EmailAddress not equal", validEmailDBRS.getString(3), generatedEmailDBRS.getString(3));

		}
	}

	protected void compareDBGroupTable(Connection validDB, Connection generatedDB, int contactID) throws SQLException {
		String query = "select * from Groups";
		if (contactID != -1) {
			query += " where CM_Members = " + contactID;
		}

		PreparedStatement validDBGroupQuery = validDB.prepareStatement(query);
		validDBGroupQuery.execute();
		ResultSet validGroupDBRS = validDBGroupQuery.getResultSet();

		PreparedStatement generatedDBGroupQuery = generatedDB.prepareStatement(query);
		generatedDBGroupQuery.execute();
		ResultSet generatedGroupDBRS = generatedDBGroupQuery.getResultSet();

		while (validGroupDBRS.next()) {
			Assert.assertTrue("The number of results returned don't match", generatedGroupDBRS.next());
			Assert.assertEquals("CM_ID not equal", validGroupDBRS.getInt(1), generatedGroupDBRS.getInt(1));
			Assert.assertEquals("CM_Members not equal", validGroupDBRS.getString(2), generatedGroupDBRS.getString(2));
		}
	}

	protected void compareDBGroups2Table(Connection validDB, Connection generatedDB, int groupID) throws SQLException {
		String query = "select * from Groups2";
		if (groupID != -1) {
			query += " where CM_ID = " + groupID;
		}

		PreparedStatement validDBGroupQuery = validDB.prepareStatement(query);
		validDBGroupQuery.execute();
		ResultSet validGroupDBRS = validDBGroupQuery.getResultSet();

		PreparedStatement generatedDBGroupQuery = generatedDB.prepareStatement(query);
		generatedDBGroupQuery.execute();
		ResultSet generatedGroupDBRS = generatedDBGroupQuery.getResultSet();

		while (validGroupDBRS.next()) {
			Assert.assertTrue("The number of results returned don't match", generatedGroupDBRS.next());
			Assert.assertEquals("CM_ID not equal", validGroupDBRS.getInt(1), generatedGroupDBRS.getInt(1));
			Assert.assertTrue("CM_GroupMembers not equal", Arrays.equals(validGroupDBRS.getBytes(2), generatedGroupDBRS.getBytes(2)));
		}
	}

	protected void compareDBSyncTable(Connection validDB, Connection generatedDB, int contactID) throws SQLException {
		String query = "select * from Sync";
		if (contactID != -1) {
			query += " where CM_ID = " + contactID;
		}

		PreparedStatement validDBGroupQuery = validDB.prepareStatement(query);
		validDBGroupQuery.execute();
		ResultSet validGroupDBRS = validDBGroupQuery.getResultSet();

		PreparedStatement generatedDBGroupQuery = generatedDB.prepareStatement(query);
		generatedDBGroupQuery.execute();
		ResultSet generatedGroupDBRS = generatedDBGroupQuery.getResultSet();

		while (validGroupDBRS.next()) {
			Assert.assertTrue("The number of results returned don't match", generatedGroupDBRS.next());
			Assert.assertEquals("CM_ID not equal", validGroupDBRS.getInt(1), generatedGroupDBRS.getInt(1));
			Assert.assertEquals("CM_LastSyncDate not equal", validGroupDBRS.getDate(2), generatedGroupDBRS.getDate(2));
		}
	}

	protected void compareDBPreferencesTable(Connection validDB, Connection generatedDB) throws SQLException {
		String query = "select * from Preferences";

		PreparedStatement validDBQuery = validDB.prepareStatement(query);
		validDBQuery.execute();
		ResultSet validDBRS = validDBQuery.getResultSet();

		PreparedStatement generatedDBQuery = generatedDB.prepareStatement(query);
		generatedDBQuery.execute();
		ResultSet generatedDBRS = generatedDBQuery.getResultSet();

		if (validDBRS.first()) {
			Assert.assertTrue("The number of results returned don't match", generatedDBRS.next());
			Assert.assertEquals("CM_PrefFileId not equal", validDBRS.getInt(1), generatedDBRS.getInt(1));
			Assert.assertTrue("CM_PrefTemplateId not equal", 0==generatedDBRS.getInt(2)||-1==generatedDBRS.getInt(2));
			Assert.assertEquals("CM_PrefOwnCard not equal", validDBRS.getInt(3), generatedDBRS.getInt(3));
			Assert.assertEquals("CM_PrefCardTemplateRefId not equal", validDBRS.getInt(4), generatedDBRS.getInt(4));
			Assert.assertTrue("CM_PrefCardTemplateId not equal", Arrays.equals(validDBRS.getBytes(5), generatedDBRS.getBytes(5)));
			Assert.assertTrue("CM_PrefGroupIdList not equal", Arrays.equals(validDBRS.getBytes(6), generatedDBRS.getBytes(6)));
			Assert.assertEquals("CM_PrefFileVer not equal", validDBRS.getInt(7), generatedDBRS.getInt(7));
			//Assert.assertEquals("CM_CreationDate not equal",validDBRS.getLong(
			// 8),generatedDBRS.getLong(8));
			// Machine UID is just a time stamp can't be compared
			//Assert.assertEquals("CM_MachineUid not equal",validDBRS.getLong(9)
			// ,generatedDBRS.getLong(9));
			Assert.assertTrue("CM_PrefSortOrder not equal", Arrays.equals(validDBRS.getBytes(10), generatedDBRS.getBytes(10)));
		} else {
			Assert.assertTrue("Preferences table empty", false);
		}
	}

	public Connection getDBMSConnection(String filename, String conParameters) throws SDBExecutionException {

		// This compensates for the fact that the JDBC driver cant handle
		// relative
		// paths to directories that dont exist
		File aDbFile = new File(filename);
		if (aDbFile.getParentFile() != null) {
			aDbFile.getParentFile().mkdirs();
		}

		try {
			DBType.DBMS.loadClass();
			String connectionString = DBType.DBMS.getConnectionName() + filename;
			if (conParameters != null) {
				connectionString += "?" + conParameters;
			}
			return DriverManager.getConnection(connectionString);
		} catch (ClassNotFoundException ex) {
			throw new SDBExecutionException("Unable to open Database: " + ex.getMessage(), ex);
		} catch (SQLException ex) {
			throw new SDBExecutionException("Unable to open Database: " + ex.getMessage(), ex);
		}
	}

	/**
	 * @param test
	 */
	protected void runContactsFlow(TestConfig test) {
		try {
			CmdLinev2 cmd = new CmdLinev2();
			cmd.parseArguments(test.getArgs());
			new Settings().configure(cmd);	
			
			IFlow flow = workflowFactory.getWorkflow(cmd.getMode());
			
			flow.validateOptions(cmd);
			flow.start(cmd);
	
		} catch (OptionException ex) {
			Assert.fail("Failed to validate options. "+ex.getLocalizedMessage());
		} catch (SDBValidationException e) {
			Assert.fail("Failed to validate options. "+e.getLocalizedMessage());
		} catch (SDBExecutionException e) {
			Assert.fail("Failed to create DBs. "+e.getLocalizedMessage());
		} catch (SdbFlowException e) {
			Assert.fail("Failed to create DBs. "+e.getLocalizedMessage());
		}
		
	}

	/**
	 * @throws java.lang.Exception
	 */
	@Before
	public void onSetUp() throws Exception {
		System.setProperty("com.symbian.dbms.lib.path", "lib/");
		System.setProperty("sdb.contacts.enabled", "true");
	}

	/**
	 * 
	 * Provides a method of configuring a test.
	 *
	 */
	public class TestConfig {

		protected File template;
		protected File validDB;
		protected File genDB;
		protected File[] vCards;
		protected String group = null;

		/**
		 * 
		 * @param template the rss template that should be used to generate the contact structure.
		 * @param validDB the known good DB that is used to validate against.
		 * @param genDB	the location of the DB to be generated.
		 * @param vCard the vCard to add to the DB - can be null if no vCard is required.
		 * @throws IOException	Thrown if the copy of the validDB (to a temp file) fails.
		 */
		public TestConfig(File template, File validDB, File genDB, File... vCards) throws IOException {
			init(template, validDB, genDB, null, vCards);
		}
			
		/**
		 * 
		 * @param template the rss template that should be used to generate the contact structure.
		* @param validDB the known good DB that is used to validate against.
		 * @param genDB	the location of the DB to be generated.
		 * @param group the group name
		 * @param vCard the vCard to add to the DB - can be null if no vCard is required.
		 * @throws IOException	Thrown if the copy of the validDB (to a temp file) fails.
		 */
		public TestConfig(File template, File validDB, File genDB, String group, File... vCards) throws IOException {
			init(template, validDB, genDB, group, vCards);
		}
		
		private void init(File template, File validDB, File genDB, String group, File... vCards) throws IOException{
			this.template = template;
			this.genDB = genDB;
			if(vCards == null){
				this.vCards = new File[]{};
			} else {
				this.vCards = vCards;
			}

			if(validDB != null){
    			File valid_new = File.createTempFile(validDB.getName(), "db");
    			FileUtils.copyFile(validDB, valid_new);

    			this.validDB = valid_new;
			}
			this.group = group;
		}

		/**
		 * @return
		 */
		public String getGenDBPath() {
			return genDB.getAbsolutePath();
		}

		/**
		 * @return
		 */
		public String getValidDBPath() {
			return validDB.getAbsolutePath();
		}

		/**
		 * @return
		 */
		public String getTemplatePath() {
			return template.getAbsolutePath();
		}
		
		public String[] getArgs(){
			List<String> args = new ArrayList<String>();
			args.add("-t");
			args.add(getTemplatePath());
			args.add("-m");
			args.add("dbms.contacts");
			args.add("-o");
			args.add(getGenDBPath());
			if(group !=null && group.length()>0){
				args.add("-g");
				args.add(group);
			}
			for(File vCard: vCards){
				args.add(vCard.getAbsolutePath());
			};
			return args.toArray(new String[]{});
		}
	}
	

	protected void cleanup(List<TestConfig> tests) {
		cleanup(tests.toArray(new TestConfig[]{}));
	}
	
	protected void cleanup(TestConfig test) {
		cleanup(new TestConfig[]{test});
	}
	
	protected static void cleanup(TestConfig[] tests){
		for(TestConfig test: tests){
			test.genDB.delete();
			test.validDB.delete();
		}
	}

    public void setWorkflowFactory(WorkflowFactory workflowFactory) {
        this.workflowFactory = workflowFactory;
    }
}
