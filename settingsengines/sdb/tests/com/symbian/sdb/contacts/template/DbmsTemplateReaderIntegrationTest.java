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

import junit.framework.JUnit4TestAdapter;

import org.junit.BeforeClass;
import org.junit.Test;

import com.symbian.sdb.cmd.CmdLinev2;
import com.symbian.sdb.mode.flow.IFlow;
import com.symbian.sdb.mode.flow.WorkflowFactory;
import com.symbian.sdb.settings.Settings;

public class DbmsTemplateReaderIntegrationTest extends BasicDBMSContactsDBComparisonTest{

	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
		System.setProperty("com.symbian.dbms.lib.path", "lib/");
	}
	
	public static junit.framework.Test suite() {
		return new JUnit4TestAdapter(DbmsTemplateReaderIntegrationTest.class);
	}
	
	@Test
	public void testRead() throws Exception {
		String[] args = {"-m", "dbms.contacts", 
				"-i", "tests/config/templateReaderTests/sdb_94rss.db", 
				"-o", "tests/config/sdb2.db",
				"tests/config/templateReaderTests/vcard2.vcf"
				};
		CmdLinev2 cmd = new CmdLinev2();
		cmd.parseArguments(args);
		new Settings().configure(cmd);	
		
		IFlow flow = workflowFactory.getWorkflow(cmd.getMode());
		
		flow.validateOptions(cmd);
		flow.start(cmd);
	}

    public void setWorkflowFactory(WorkflowFactory workflowFactory) {
        this.workflowFactory = workflowFactory;
    }

}
