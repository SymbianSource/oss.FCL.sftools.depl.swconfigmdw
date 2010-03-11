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
import java.sql.Connection;
import java.util.ArrayList;
import java.util.List;

import junit.framework.Assert;
import junit.framework.JUnit4TestAdapter;

import org.apache.commons.cli2.OptionException;
import org.junit.Test;

import com.symbian.sdb.cmd.CmdLinev2;
import com.symbian.sdb.mode.flow.IFlow;
import com.symbian.sdb.settings.Settings;
import com.symbian.sdb.util.FileUtil;

public class DBMSGroupsIntegrationTest extends BasicDBMSContactsDBComparisonTest {
	List<TestConfig> testConfig = new ArrayList<TestConfig>();
	
	public void onSetUp() throws Exception{
		super.onSetUp();
		try {
			File vcard = new File(getPathTo("vcard2.vcf"));
//			testConfig.add(new GroupsTestConfig(new File(getPathTo("91.rss")), new File(getPathTo("91_group.cdb")), new File(getPathTo("91_gen.cdb")), vcard));
//			testConfig.add(new GroupsTestConfig(new File(getPathTo("92.rss")), new File(getPathTo("92_group.cdb")), new File(getPathTo("92_gen.cdb")), vcard));
			testConfig.add(new TestConfig(new File(getPathTo("93.rss")), new File(getPathTo("93_group.cdb")), new File(getPathTo("93_gen.cdb")), "testgroup", vcard));
//			testConfig.add(new GroupsTestConfig(new File(getPathTo("94.rss")), new File(getPathTo("94_group.cdb")), new File(getPathTo("94_gen.cdb")), vcard));
		} catch (Exception e) {
			Assert.fail(e.getLocalizedMessage());
		}

	}
	protected static File resources = new File("tests/config/group_tests_dbms/");

	protected static String getPathTo(String resource) {
		return FileUtil.concatFilePath(resources.getAbsolutePath(), resource);
	}

	@Test
	public void testAll() throws Exception{
		
		for(TestConfig test: testConfig){
			try {
				CmdLinev2 cmd = new CmdLinev2();
				cmd.parseArguments(test.getArgs());
				new Settings().configure(cmd);	
				
				IFlow flow = workflowFactory.getWorkflow(cmd.getMode());
				
				flow.validateOptions(cmd);
				flow.start(cmd);

			} catch (OptionException ex) {
				Assert.fail("Shouldn't fail here.");
			}
		
			Connection valDBCon = getDBMSConnection(test.getValidDBPath(), null);
			Connection genDBCon = getDBMSConnection(test.getGenDBPath(), null);
			
			compareDBContactTable(valDBCon, genDBCon, 0);
			compareDBIdentityTable(valDBCon, genDBCon, 0);
			compareDBPhoneTable(valDBCon, valDBCon, 0);
			compareDBEmailTable(valDBCon, valDBCon, 0);
			compareDBGroupTable(valDBCon, valDBCon, 0);
			compareDBGroups2Table(valDBCon, valDBCon, 0);
			compareDBSyncTable(valDBCon, valDBCon, 0);
			compareDBPreferencesTable(valDBCon, genDBCon);
		}
	}
	

	
	public static junit.framework.Test suite() {
		return new JUnit4TestAdapter(DBMSGroupsIntegrationTest.class);
	}

	/*
	class GroupsTestConfig extends BasicDBMSContactsDBComparisonTest.TestConfig {

		public GroupsTestConfig(File template, File validDB, File genDB,
				File... cards) throws IOException {
			super(template, validDB, genDB, cards);
			// TODO Auto-generated constructor stub
		}
		
		public String[] getArgs(){
			List<String> args = new ArrayList<String>();
			args.add("-t");
			args.add(getTemplatePath());
			args.add("-m");
			args.add("dbms.contacts");
			args.add("-g");
			args.add("testgroup");
			args.add("-o");
			args.add(getGenDBPath());
			for(File vCard: vCards){
				args.add(vCard.getAbsolutePath());
			};
			return args.toArray(new String[]{});
		}
	}*/
}
