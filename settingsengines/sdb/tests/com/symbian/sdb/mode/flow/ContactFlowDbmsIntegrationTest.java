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

package com.symbian.sdb.mode.flow;


import junit.framework.TestCase;

import org.junit.After;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import com.symbian.sdb.cmd.CmdLinev2;
import com.symbian.sdb.contacts.BaseIntegrationTestCase;
import com.symbian.sdb.database.DBManager;
import com.symbian.sdb.database.SqlExecuter;

public class ContactFlowDbmsIntegrationTest extends BaseIntegrationTestCase    {
	
	private DBManager dbManager = null;
	private ContactsFlow contactsFlow;  

	public void onSetUp() throws Exception {
		super.onSetUp();
		System.setProperty("com.symbian.dbms.lib.path", "lib/");
		System.setProperty("sdb.contacts.configuration", "config/contacts.xml");
		System.setProperty("sdb.contacts.schema.dbms", "schema_data_dbms.sql");
		System.setProperty("sdb.contacts.enabled", "true");
	}
	
	@Test
	public void testContactFlowOnDbms() throws Exception {
		
		//Create and set command-line parameters
		CmdLinev2 cmd = new CmdLinev2();
		cmd.parseArguments(new String[] {"-t", "tests/config/template_itests/93ui.rss", "-m", "dbms.contacts", "-o", "cntflow.cdb", "testdata/contacts/vcard/vcard2.vcf"});
		
		if (null == dbManager)    {
		    dbManager = new DBManager();    
		}

		contactsFlow.validateOptions(cmd);
		contactsFlow.start(cmd);
	}

	@Test
	public void testContactFlowOnDbmsWithNokiaTemplate() throws Exception {
		
		//Create and set command-line parameters
		CmdLinev2 cmd = new CmdLinev2();
		cmd.parseArguments(new String[] {"-t", "tests/config/cntmodel_n.rss", "-m", "dbms.contacts", "-o", "cntflow.cdb", "testdata/contacts/vcard/vcard2.vcf"});
		
		if (null == dbManager)    {
		    dbManager = new DBManager();    
		}

		contactsFlow.validateOptions(cmd);
		contactsFlow.start(cmd);
	}

	public void setContactsFlow(ContactsFlow contactsFlow) {
        this.contactsFlow = contactsFlow;
    }
}
