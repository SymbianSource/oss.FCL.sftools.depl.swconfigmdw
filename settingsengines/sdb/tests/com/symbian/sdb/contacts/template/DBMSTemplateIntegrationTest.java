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
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

import junit.framework.Assert;
import junit.framework.JUnit4TestAdapter;

import org.apache.commons.cli2.OptionException;
import org.junit.Test;

import com.symbian.sdb.cmd.CmdLinev2;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.SDBValidationException;
import com.symbian.sdb.mode.flow.IFlow;
import com.symbian.sdb.settings.Settings;

/**
 * @author jamesclark
 *
 */
public class DBMSTemplateIntegrationTest extends BasicDBMSContactsDBComparisonTest {

	List<TestConfig> testConfig = new ArrayList<TestConfig>();
	{
		try {
			File vcard = new File(getPathTo("bigcontact.vcf"));
			testConfig.add(new TestConfig(new File(getPathTo("91.rss")), new File(getPathTo("91.cdb")), new File(getPathTo("91_gen.cdb")), vcard));
			testConfig.add(new TestConfig(new File(getPathTo("92.rss")), new File(getPathTo("92.cdb")), new File(getPathTo("92_gen.cdb")), vcard));
			testConfig.add(new TestConfig(new File(getPathTo("93.rss")), new File(getPathTo("93.cdb")), new File(getPathTo("93_gen.cdb")), vcard));
			testConfig.add(new TestConfig(new File(getPathTo("94.rss")), new File(getPathTo("94.cdb")), new File(getPathTo("94_gen.cdb")), vcard));
		} catch (Exception e) {
			Assert.fail(e.getLocalizedMessage());
		}

	}
	

	// The test currently fails - awaiting implementation
	//@Test
	public void _testTemplatesInDBs() throws Exception{
		
		for(TestConfig test: testConfig){
			runContactsFlow(test);

			Connection valDBCon = getDBMSConnection(test.getValidDBPath(), null);
			Connection genDBCon = getDBMSConnection(test.getGenDBPath(), null);
			
			compareDBContactTable(valDBCon, genDBCon, 0);
			compareDBIdentityTable(valDBCon, genDBCon, 0);
			compareDBPreferencesTable(valDBCon, genDBCon);
		}
	}
	
	// The test currently fails - awaiting implementation
	// @Test
	public void _testDBMSDBs() throws Exception{
		
		for(TestConfig test: testConfig){
			try {
				CmdLinev2 cmd = new CmdLinev2();
				boolean result = cmd.parseArguments(test.getArgs());
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
		return new JUnit4TestAdapter(DBMSTemplateIntegrationTest.class);
	}
	
	
	
	/**
	 * Test baseline database generation for DBMS contacts database 
	 * @throws SDBExecutionException
	 */
	@Test 
	public void testDbmsBaselineDbForBasicFields() throws SDBExecutionException {
		
		TestConfig config = null;
		
		//apply test configuration
		try {
			config = new TestConfig(new File(getPathTo("94ui.rss")), new File(getPathTo("94ui.cdb")), new File(getPathTo("94_gen.cdb")), new File("testdata/contacts/vcard/vcard2.vcf"));
		} catch (IOException e) {
			Assert.fail("Can't apply configuration : " + e.getLocalizedMessage());
		}
			
		//build command from configuration arguments
	
		CmdLinev2 cmd = new CmdLinev2();
		
		try {		
			boolean creatFlow = cmd.parseArguments(config.getArgs());
			if(creatFlow) 
			{
				new Settings().configure(cmd);	
				IFlow flow = workflowFactory.getWorkflow(cmd.getMode());
				flow.validateOptions(cmd);
				flow.start(cmd);
			}
		} catch (SDBValidationException ve) {
			Assert.fail("CLI argument validation failed");  
		} catch (OptionException ex) {
			Assert.fail("Some of the options specified are invalid : " + cmd.toString());
		} catch (Exception e) {
			throw new SDBExecutionException(e);
		}
		
		//get SQL connection to emulator DB
		Connection conDbEmulator = getDBMSConnection(config.getValidDBPath(), null);
		//get SQL connection to baseline DB
		Connection conDbBaseline = getDBMSConnection(config.getGenDBPath(), null);
		
		try {
			
			compareDBContactTable(conDbEmulator, conDbBaseline, 0);
			compareDBIdentityTable(conDbEmulator, conDbBaseline, 0);
			
			/* //No entries made to these tables for basic fields 
			compareDBPhoneTable(conDbEmulator, conDbBaseline, 0);
			compareDBEmailTable(conDbEmulator, conDbBaseline, 0);
			compareDBGroupTable(conDbEmulator, conDbBaseline, 0);
			compareDBGroups2Table(conDbEmulator, conDbBaseline, 0);
			compareDBSyncTable(conDbEmulator, conDbBaseline, 0);
			*/
			compareDBPreferencesTable(conDbEmulator, conDbBaseline);
			
			cleanup(config);
		} catch (SQLException sqle) {
			Assert.fail("Unable to execute SQL statement : " + sqle.getLocalizedMessage());
		}
		
	}
	
	public void testInvaldTemplate() throws Exception {
        File vcard = new File(getPathTo("bigcontact.vcf"));
        TestConfig config = new TestConfig(vcard, null, new File(getPathTo("invalid_template_gen.cdb")), vcard);

        CmdLinev2 cmd = new CmdLinev2();

        boolean createFlow = cmd.parseArguments(config.getArgs());
        try {
            if (createFlow) {
                new Settings().configure(cmd);
                IFlow flow = workflowFactory.getWorkflow(cmd.getMode());
                flow.validateOptions(cmd);
                flow.start(cmd);
                fail("Template generator should throw exception");
            }
        } catch (SDBExecutionException e) {
            //pass
            System.out.println("This stack trace is expected: ");
            e.printStackTrace();
            
        }
    }

}
