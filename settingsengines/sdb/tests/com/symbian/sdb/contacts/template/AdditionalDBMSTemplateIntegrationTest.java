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
// AdditionalDBMSTemplateIntegrationTest.java
//

package com.symbian.sdb.contacts.template;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

import junit.framework.Assert;
import junit.framework.JUnit4TestAdapter;

import org.apache.commons.cli2.OptionException;
import org.junit.BeforeClass;
import org.junit.Test;

import com.symbian.sdb.cmd.CmdLinev2;
import com.symbian.sdb.contacts.dbms.DBMSPreferences;
import com.symbian.sdb.contacts.sqlite.GenericUtils;
import com.symbian.sdb.database.DBManager;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.mode.flow.IFlow;
import com.symbian.sdb.mode.flow.WorkflowFactory;
import com.symbian.sdb.mode.flow.ced.SdbFlowException;
import com.symbian.sdb.settings.Settings;
import com.symbian.sdb.util.LongArray;

public class AdditionalDBMSTemplateIntegrationTest extends BasicDBMSContactsDBComparisonTest {

	protected WorkflowFactory workflowFactory;
	
	private String output_database = "tests/config/template_itests/sdb_temp.db";
	private String input_template_94 = "tests/config/template_itests/94.rss";
	private String input_template_91 = "tests/config/template_itests/91.rss";
	private String modified_flags_template_91 = "tests/config/template_itests/91_different_flags.rss";
	private String vCardFile = "tests/config/templateReaderTests/vcard2.vcf";
	
	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
		System.setProperty("com.symbian.dbms.lib.path", "lib/");
	}

	public static junit.framework.Test suite() {
		return new JUnit4TestAdapter(DbmsTemplateReaderIntegrationTest.class);
	}

	@Test
	public void testAddExistingTemplate() throws Exception {
		executeContactsFlow(input_template_94, null);
		
		executeContactsFlow(input_template_94, output_database);
		check(0, 4, 5, new int[0]);

		executeContactsFlow(input_template_91, output_database);
		int[] x = new int[] {2};
		check(1, 4, 8, x);
		
		executeContactsFlow(input_template_91, output_database);
		x = new int[] {4};
		check(1, 4, 10, x);
		
		executeContactsFlow(modified_flags_template_91, output_database);
		x = new int[] {4, 2};
		check(2, 4, 13, x);
		
	}
	
	private void executeContactsFlow(String template, String inputDatabase) throws OptionException, SDBValidationException, SDBExecutionException, SdbFlowException {
		CmdLinev2 cmd = new CmdLinev2();
		cmd.parseArguments(createArgumentsForContactsFlow(template, inputDatabase));
		new Settings().configure(cmd);	
		
		IFlow flow = workflowFactory.getWorkflow(cmd.getMode());

		flow.validateOptions(cmd);
		flow.start(cmd);
		
	}

	private void checkContactsCount(Connection genDBCon, int contactsCount, String query) throws SQLException {
		Statement stmt = null;
		ResultSet rs = null;
        try{
	        stmt = genDBCon.createStatement();
	        rs = stmt.executeQuery(query);
	        Assert.assertEquals("Checking the number of contacts for query " + query, contactsCount, count(rs));
			GenericUtils.closeQuietly(rs);
		} finally {
			GenericUtils.closeQuietly(rs);
			GenericUtils.closeQuietly(stmt);
        }
	}
	
	private void check(int addTemplateCount, int systemTemplateContacts, int allContacts, 
		int[] additionalTemplateCounts)  throws SDBExecutionException, SQLException {
		Connection genDBCon = getDBMSConnection(output_database, null);
		LongArray addTemplates = checkPreferences(genDBCon, addTemplateCount);
		checkContactsCount(genDBCon, systemTemplateContacts, "select * from contacts where CM_PrefTemplateRefId=0");
		checkContactsCount(genDBCon, allContacts, "select * from contacts");
		
		for (int i = 0; i < addTemplates.size(); i++) {
			checkContactsCount(genDBCon, additionalTemplateCounts[i], 
					"select * from contacts where CM_PrefTemplateRefId=" + addTemplates.get(i));
		}
		
		genDBCon.close();
	}
	
	private LongArray checkPreferences(Connection con, int expected) throws SDBExecutionException {
		DBMSPreferences preferences = new DBMSPreferences(null, null);
		DBManager manager = new DBManager();
		manager.setConnection(con);
		preferences.readFromDb(manager);
		
		LongArray templateIds = preferences.getCardTemplateIds();
		Assert.assertEquals("Checking number of user template ids referenced in the preferences table ",
				expected, templateIds.size());
		
		return templateIds;
	}

	private int count(ResultSet rs) throws SQLException {
        int counter = 0;
        while (rs.next()) {
        	counter++;
        }
		return counter;
	}

	
	private String[] createArgumentsForContactsFlow(String template, String inputDatabase) {
		int size = 7;
		if (inputDatabase != null) {
			size += 2;
		} 
		
		String[] arguments = new String[size];
		
		int index = 0;
		arguments[index] = "-m";
		arguments[++index] = "dbms.contacts";
		
		if (inputDatabase != null) {
			arguments[++index] = "-i";
			arguments[++index] = inputDatabase;
		}
		
		arguments[++index] = "-o";
		arguments[++index] = output_database;
		arguments[++index] = "-t";	
		arguments[++index] = template;
		arguments[++index] = vCardFile;
	
		return arguments;
	}
	
	public void setWorkflowFactory(WorkflowFactory workflowFactory) {
		this.workflowFactory = workflowFactory;
	}
	

}
