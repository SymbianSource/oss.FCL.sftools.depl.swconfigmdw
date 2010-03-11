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

import junit.framework.JUnit4TestAdapter;

import org.apache.commons.cli2.OptionException;
import org.junit.Before;
import org.junit.Test;

import com.symbian.sdb.cmd.CmdLinev2;
import com.symbian.sdb.contacts.speeddial.SpeedDialManagerImpl;
import com.symbian.sdb.exception.SDBValidationException;

public class ContactsFlowTest {
	
    public static junit.framework.Test suite() { 
        return new JUnit4TestAdapter(ContactsFlowTest.class); 
    }
    
	@Before
	public void setUp() {
		System.setProperty("org.sqlite.lib.path", "lib/");
		System.setProperty("com.symbian.dbms.lib.path", "lib/");
		System.setProperty("sdb.contacts.enabled", "true");
	}
	
	@Test
	public void testValidateCreateValidOptions() throws OptionException, SDBValidationException {
		// Create with valid options - Should not throw an exception
		CmdLinev2 cmd = new CmdLinev2();
		cmd.parseArguments(new String[] {"-t", "testdata//vCards//empty.vcf", "-o", "test"});
		
		ContactsFlow contactsFlow = createContactsFlow();
		contactsFlow.validateOptions(cmd);
	}

	@Test
	public void testValidateUpdateValidOptions() throws OptionException, SDBValidationException {
		// Update with valid options - Should not throw an exception
		CmdLinev2 cmd = new CmdLinev2();
		cmd.parseArguments(new String[] {"-i", "testdata//vCards//empty.vcf", "-o", "test", "testdata//vCards//empty.vcf"});

		ContactsFlow contactsFlow = createContactsFlow();
		contactsFlow.validateOptions(cmd);
	}
	
	@Test(expected=SDBValidationException.class)
	public void testValidateFailTemplateFileDoesNotExist() throws OptionException, SDBValidationException {
		// Template file that does not exist/is a dir
		CmdLinev2 cmd = new CmdLinev2();
		cmd.parseArguments(new String[] {"-t", "testdata//vCards//empty", "-o", "test", "testdata//vCards//empty.vcf"});
	
		ContactsFlow contactsFlow = createContactsFlow();
		contactsFlow.validateOptions(cmd);
	}

	@Test(expected=SDBValidationException.class)
	public void testValidateFailTemplateFileNotSpecified() throws OptionException, SDBValidationException {
		// Create and no template file specified
		CmdLinev2 cmd = new CmdLinev2();
		cmd.parseArguments(new String[] {"-o", "test"});

		ContactsFlow contactsFlow = createContactsFlow();
		contactsFlow.validateOptions(cmd);
	}
	
	@Test(expected=SDBValidationException.class)
	public void testValidateFailNovCardSpecified() throws OptionException, SDBValidationException {
		// Update and no vCard file specified
		CmdLinev2 cmd = new CmdLinev2();
		cmd.parseArguments(new String[] {"-i", "testdata//vCards//empty.vcf", "-t", "testdata//vCards//empty.vcf", "-o", "test"});



		ContactsFlow contactsFlow = createContactsFlow();
		contactsFlow.validateOptions(cmd);
	}

	/**
	 * @return
	 */
	private ContactsFlow createContactsFlow() {
		ContactsFlow contactsfFlow = new ContactsFlow();
		contactsfFlow.setSpeedDialManager(new SpeedDialManagerImpl());
		contactsfFlow.setInputDatabaseValidator(new ContactsFlowInputDatabaseValidator());
		return contactsfFlow;
	}
}
