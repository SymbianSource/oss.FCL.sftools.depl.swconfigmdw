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

import junit.framework.JUnit4TestAdapter;
import mockit.Mockit;

import org.apache.commons.cli2.OptionException;
import org.jmock.Expectations;
import org.jmock.Mockery;
import org.jmock.lib.legacy.ClassImposteriser;

import com.symbian.sdb.cmd.CmdLinev2;
import com.symbian.sdb.contacts.importer.vcard.PropertyData;
import com.symbian.sdb.contacts.sqlite.ContactDaoSQLite;
import com.symbian.sdb.contacts.sqlite.model.SQLiteContactCard;
import com.symbian.sdb.contacts.sqlite.model.SQLiteContactGroup;
import com.symbian.sdb.contacts.sqlite.model.SQLiteEmailAddress;
import com.symbian.sdb.contacts.sqlite.model.SQLitePhoneNumber;
import com.symbian.sdb.contacts.template.ITemplateManager;
import com.symbian.sdb.contacts.template.ITemplateModel;
import com.symbian.sdb.contacts.template.MappingMissingException;
import com.symbian.sdb.contacts.template.TemplateManager;
import com.symbian.sdb.contacts.template.TemplateModel;
import com.symbian.sdb.exception.SDBExecutionException;
import com.symbian.sdb.exception.TemplateParsingException;
import com.symbian.sdb.mode.flow.ContactsFlow;
import com.symbian.sdb.mode.flow.IFlow;
import com.symbian.sdb.settings.Settings;

/**
 * @author krzysztofZielinski
 *
 */
public class SQLiteContactFlowIntegrationTest extends BaseIntegrationTestCase     {

    public static final String databaseFilePath = "testdata/contacts/test_contact.sdb";
    
    private ContactsFlow contactsFlow;
    
    @Override
    protected void onSetUp() throws Exception {
    	super.onSetUp();
    	deleteFile(databaseFilePath);
    }
    
    @Override
    protected void onTearDown() throws Exception {
        // delete existing database
        deleteFile(databaseFilePath);
    }
    
    private void deleteFile(String filePath) {
        File file = new File(filePath);
        if (file.exists())  {
            file.delete();            
        }
    }
    
    public void testCreateRealNewContactDatabase() throws Exception {
        File dbFile = new File(databaseFilePath);
        assertTrue(!dbFile.exists());
		String[] args = {"-m", "sqlite.contacts", 
				"-t", "tests/config/CNTMODEL.RSS", 
				"-o", databaseFilePath,
				"-g", "Group1",
				"testdata/contacts/vcard/vcard2.vcf"};
		try {
			CmdLinev2 cmd = new CmdLinev2();
			cmd.parseArguments(args);
			new Settings().configure(cmd);	
			contactsFlow.setSqliteTemplateManager(createMockRealTemplateManager());
			contactsFlow.validateOptions(cmd);
			contactsFlow.start(cmd);

		} catch (OptionException ex) {
			fail("Shouldn't fail here.");
		} 
        
        //
        //contactFlow.createContacts(vCardFiles, templateModel, groups);
        assertTrue(dbFile.exists());
    }

    /**
     * @return
     */
    private ITemplateModel createMockTemplateModel() throws MappingMissingException {
    	Mockery templateModelMockery = new Mockery();
    	final ITemplateModel templateMock = templateModelMockery.mock(ITemplateModel.class);

    	templateModelMockery.checking(new Expectations() {{ 
    		atLeast(1).of(templateMock).templateContainsMappingForVCardProperty(with(any(PropertyData.class)));will(returnValue(true));
    		allowing (templateMock).setTemplateId(with(any(Integer.class)));
    	}});

    	return templateMock;
    }
    /**
     * @return
     */
    private TemplateManager createMockRealTemplateManager() throws SDBExecutionException, TemplateParsingException {
    	
		System.setProperty("sdb.contacts.configuration", "config/contacts.xml");
		ITemplateManager manager = new TemplateManager();
		final ITemplateModel templateModel = manager.parse("tests/config/CNTMODEL.RSS");
    	
        Mockery templateManagerMockery = new Mockery() {{
            setImposteriser(ClassImposteriser.INSTANCE);
        }};
        final TemplateManager templateManagerMock = templateManagerMockery.mock(TemplateManager.class);
        try {
        	templateManagerMockery.checking(new Expectations() {{ 
                    atLeast(1).of(templateManagerMock).parse(with(any(String.class)));will(returnValue(templateModel));
                    allowing (templateManagerMock).persistTemplate(with(any(TemplateModel.class)));
                    }});
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        return templateManagerMock;
    }
    
    private TemplateManager createMockTemplateManager()  {
        Mockery templateManagerMockery = new Mockery() {{
            setImposteriser(ClassImposteriser.INSTANCE);
        }};
        final TemplateManager templateManagerMock = templateManagerMockery.mock(TemplateManager.class);
        try {
        	templateManagerMockery.checking(new Expectations() {{ 
                    atLeast(1).of(templateManagerMock).parse(with(any(String.class)));will(returnValue(createMockTemplateModel()));
                    allowing (templateManagerMock).persistTemplate(with(any(TemplateModel.class)));
                    }});
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        return templateManagerMock;
    }
    
    public void _testCreateNewContactDatabaseMocked() throws Exception {
        Mockit.redefineMethods(ContactDaoSQLite.class, ContactDaoSQLiteMock.class);
      
        File dbFile = new File(databaseFilePath);
        
        assertTrue(!dbFile.exists());
		String[] args = {"-m", "sqlite.contacts", 
				"-t", "tests/config/cntmodel.rss", 
				"-o", databaseFilePath,
				"-g", "Group1",
				"testdata/contacts/vcard/vcard2.vcf"};
		try {
			CmdLinev2 cmd = new CmdLinev2();
			boolean result = cmd.parseArguments(args);
			new Settings().configure(cmd);	
//			IFlow contactsFlow = new ContactsFlow(new DatabaseManager(), new SqlExecuter(), createMockTemplateManager());
			IFlow flow = new ContactsFlow();

			flow.validateOptions(cmd);
			flow.start(cmd);

		} catch (OptionException ex) {
			fail("Shouldn't fail here.");
		} 
      //  contactFlow.createContacts(vCardFiles, templateModel, groups);
        assertTrue(dbFile.exists());
        
        Mockit.restoreAllOriginalDefinitions();
    }

    public static final class ContactDaoSQLiteMock {
        
        public SQLiteContactCard save(SQLiteContactCard contact) {
            
            assertTrue(contact.getLastName().matches("Rambo[12]"));
            
            if ("Rambo1".equals(contact.getLastName())) {
                assertRambo1(contact);
            }
            else if ("Rambo2".equals(contact.getLastName())) {
                assertRambo2(contact);
            }
            else {
                fail("Unexpected contact found in vCard file!");
            }

            return contact;
        }

        /**
         * @param contact
         */
        private void assertRambo2(SQLiteContactCard contact) {
            assertEquals("John", contact.getFirstName());
            assertEquals("Rambo2", contact.getLastName());
            assertEquals(1, contact.getEmailAddresses().size());
            assertEquals(2, contact.getPhoneNumbers().size());  
            assertEquals(1, contact.getGroups().size());
            assertEquals(99, contact.getTextFields().length());
            assertTrue(contact.getTextFields().matches(".*Rambo2.*"));
            assertTrue(contact.getTextFields().matches(".*John.*"));
            assertTrue(contact.getTextFields().matches(".*Killer.*"));
            assertTrue(contact.getTextFields().matches(".*Software Engineer.*"));
            assertTrue(contact.getTextFields().matches(".*Mr.*"));
            assertTrue(contact.getTextFields().matches(".*Terminator.*"));
            assertTrue(contact.getTextFields().matches(".*07873198717.*"));
            assertTrue(contact.getTextFields().matches(".*12345678901.*"));
            assertTrue(contact.getTextFields().matches(".*John\\.Rambo2@symbian\\.com.*"));

            // verify group 
            SQLiteContactGroup[] groups = new SQLiteContactGroup[contact.getGroups().size()];
            contact.getGroups().toArray(groups);
            // TODO KZ: for now assume textfields is the field where group name is stored
            assertEquals("Group1",groups[0].getTextFields());
            
            // verify email
            SQLiteEmailAddress[] emailAddresses = new SQLiteEmailAddress[contact.getEmailAddresses().size()];
            contact.getEmailAddresses().toArray(emailAddresses);
            
            assertEquals("John.Rambo2@symbian.com", emailAddresses[0].getValue());

            // verify phone numbers
            SQLitePhoneNumber[] phoneNumbers = new SQLitePhoneNumber[contact.getPhoneNumbers().size()];
            contact.getPhoneNumbers().toArray(phoneNumbers);
            
            // 12345678901 or 07873198717
            String valueExpression = "(1098765)|(7178913)";
            String extraValueRegExp = "(4321)|(7870)";
            assertTrue(phoneNumbers[0].getValue().matches(valueExpression));
            assertTrue(phoneNumbers[0].getExtraValue().matches(extraValueRegExp));
            assertTrue(phoneNumbers[1].getValue().matches(valueExpression));
            assertTrue(phoneNumbers[1].getExtraValue().matches(extraValueRegExp));
        }

        /**
         * @param contact
         */
        private void assertRambo1(SQLiteContactCard contact) {
            assertEquals("John", contact.getFirstName());
            assertEquals("Rambo1", contact.getLastName());
            assertEquals(1, contact.getEmailAddresses().size());
            assertEquals(1, contact.getPhoneNumbers().size());
            assertEquals(1, contact.getGroups().size());
            
            // verify email
            SQLiteEmailAddress[] emailAddresses = new SQLiteEmailAddress[contact.getEmailAddresses().size()];
            contact.getEmailAddresses().toArray(emailAddresses);
            
            assertEquals("John.Rambo@war.com", emailAddresses[0].getValue());

            // verify phone numbers
            SQLitePhoneNumber[] phoneNumbers = new SQLitePhoneNumber[contact.getPhoneNumbers().size()];
            contact.getPhoneNumbers().toArray(phoneNumbers);
            
            // 07873198633
            assertEquals("3368913", phoneNumbers[0].getValue());
            assertEquals("7870", phoneNumbers[0].getExtraValue());

        }
    }
    
    public static junit.framework.Test suite() {
		return new JUnit4TestAdapter(SQLiteContactFlowIntegrationTest.class);
	}

    public void setContactsFlow(ContactsFlow contactsFlow) {
        this.contactsFlow = contactsFlow;
    }
}
